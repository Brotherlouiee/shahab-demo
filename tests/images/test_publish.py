"""Negative publication contracts; mock transport never proves a real push."""

import json
import tempfile
import unittest
import urllib.error
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from publish import (
    IMMUTABLE_RULE,
    Registry,
    candidate,
    digest,
    publish_images,
    request,
    validate_environment,
    validate_review,
)

SHA = "a" * 40
NOW = datetime.now(UTC)


class PublicationTests(unittest.TestCase):
    def test_environment_requires_owner_and_only_main(self):
        environment = {
            "protection_rules": [{"type": "required_reviewers", "reviewers": [{"reviewer": {"login": "Owner"}}]}],
            "deployment_branch_policy": {"custom_branch_policies": True},
        }
        branches = {"branch_policies": [{"name": "main", "type": "branch"}]}
        validate_environment(environment, branches, "owner")
        with self.assertRaises(ValueError):
            validate_environment(environment, {"branch_policies": [{"name": "*", "type": "branch"}]}, "owner")
        with self.assertRaises(ValueError):
            validate_environment(environment, branches, "someone-else")

    def test_risk_acceptance_is_exact_explicit_and_time_bounded(self):
        report = {
            "api": {
                "Results": [
                    {
                        "Vulnerabilities": [
                            {
                                "VulnerabilityID": "CVE-test",
                                "PkgName": "pkg",
                                "InstalledVersion": "1",
                                "Severity": "MEDIUM",
                            }
                        ]
                    }
                ]
            }
        }
        entry = {
            "image": "api",
            "id": "CVE-test",
            "package": "pkg",
            "version": "1",
            "severity": "MEDIUM",
            "owner": "owner",
            "mitigation": "Track patched release",
            "deadline": (NOW + timedelta(days=1)).isoformat(),
            "decision": "accepted",
        }
        review = {"sourceSha": SHA, "approvedBy": "owner", "findings": [entry]}
        validate_review(review, SHA, report, "owner", NOW)
        for field, wrong in [
            ("owner", ""),
            ("mitigation", ""),
            ("decision", "pending"),
            ("deadline", (NOW - timedelta(seconds=1)).isoformat()),
            ("version", "2"),
        ]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_review({**review, "findings": [{**entry, field: wrong}]}, SHA, report, "owner", NOW)
        for wrong in (
            {},
            {**review, "sourceSha": "b" * 40},
            {**review, "findings": []},
            {**review, "findings": [entry, entry]},
        ):
            with self.assertRaises(ValueError):
                validate_review(wrong, SHA, report, "owner", NOW)
        report["api"]["Results"][0]["Vulnerabilities"][0]["Severity"] = "HIGH"
        with self.assertRaises(ValueError):
            validate_review(review, SHA, report, "owner", NOW)

    def test_only_404_is_missing_and_redirects_are_not_credentials_destinations(self):
        for status in (401, 403, 429, 500, 404):
            with patch(
                "urllib.request.OpenerDirector.open",
                side_effect=urllib.error.HTTPError("https://registry-1.docker.io/test", status, "", {}, None),
            ):
                if status == 404:
                    self.assertIsNone(request("https://registry-1.docker.io/test", missing=True))
                else:
                    with self.assertRaises(ValueError):
                        request("https://registry-1.docker.io/test", missing=True)
        with self.assertRaises(ValueError):
            request("https://attacker.invalid", {"Authorization": "secret"})

    def test_cdn_blob_redirect_does_not_forward_bearer_credentials(self):
        cdn = "https://cdn.example.invalid/signed-blob"
        error = urllib.error.HTTPError(
            "https://registry-1.docker.io/v2/owner/api/blobs/sha256:abc", 307, "", {"Location": cdn}, None
        )
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b"blob"
        with patch("urllib.request.OpenerDirector.open", side_effect=[error, response]) as opened:
            self.assertEqual(
                request(
                    "https://registry-1.docker.io/v2/owner/api/blobs/sha256:abc", {"Authorization": "Bearer synthetic"}
                ),
                b"blob",
            )
            self.assertEqual(opened.call_args.args, (cdn,))
        with self.assertRaises(ValueError):
            request("http://registry-1.docker.io/test", {"Authorization": "synthetic"})

    def test_registry_requires_server_immutability_and_absent_tags(self):
        registry = Registry.__new__(Registry)
        registry.namespace, registry.username, registry.token = "owner", "owner", "synthetic"
        registry.hub_token, registry.bearers = "synthetic", {}
        for policy, exists, allowed in [
            ({}, False, False),
            ({"enabled": True, "rules": [IMMUTABLE_RULE]}, True, False),
            ({"enabled": True, "rules": [IMMUTABLE_RULE]}, False, True),
        ]:
            with (
                patch(
                    "publish.request",
                    side_effect=[json.dumps({"immutable_tags_settings": policy}).encode(), b'{"token":"synthetic"}'],
                ),
                patch.object(registry, "get", return_value=b"{}" if exists else None),
            ):
                if allowed:
                    self.assertEqual(registry.preflight("shahab-api", ["v1.0.0", "sha-" + SHA]), "owner/shahab-api")
                else:
                    with self.assertRaises(ValueError):
                        registry.preflight("shahab-api", ["v1.0.0", "sha-" + SHA])

    def test_remote_digest_and_revision_are_actually_checked(self):
        registry = Registry.__new__(Registry)
        config = json.dumps({"config": {"Labels": {"org.opencontainers.image.revision": SHA}}}).encode()
        image_id = digest(config)
        manifest = json.dumps({"config": {"digest": image_id}}).encode()
        with patch.object(registry, "get", side_effect=[manifest, config]):
            self.assertEqual(registry.verify("owner/api", "v1.0.0", image_id, SHA), digest(manifest))
        with patch.object(registry, "get", side_effect=[manifest, config]), self.assertRaises(ValueError):
            registry.verify("owner/api", "v1.0.0", image_id, "b" * 40)
        with patch.object(registry, "get", return_value=manifest), self.assertRaises(ValueError):
            registry.verify("owner/api", "v1.0.0", "sha256:" + "0" * 64, SHA)

    def test_candidate_requires_fresh_matching_scan_and_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "images").mkdir()
            ids = ["sha256:" + c * 64 for c in ("1", "2")]
            images = []
            for name, image_id in zip(("api", "web"), ids, strict=True):
                report = {
                    "ArtifactType": "container_image",
                    "Metadata": {"ImageID": image_id, "OS": {"Family": "alpine"}},
                    "Results": [{"Class": "os-pkgs", "Packages": [{"Name": "test"}], "Vulnerabilities": []}],
                }
                raw = json.dumps(report).encode()
                (folder / f"images/{name}-scan.json").write_bytes(raw)
                images.append(
                    {
                        "name": name,
                        "imageId": image_id,
                        "counts": {"UNKNOWN": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
                        "reportSha256": digest(raw).removeprefix("sha256:"),
                        "buildDigest": image_id,
                    }
                )
                (folder / f"images/{name}-build.json").write_text(
                    json.dumps({"containerimage.config.digest": image_id, "buildx.build.provenance": {"materials": []}})
                )
                (folder / f"images/{name}-sbom.cdx.json").write_text(
                    json.dumps({"bomFormat": "CycloneDX", "components": [{"name": "test"}]})
                )
            summary = {
                "sourceSha": SHA,
                "status": "passed",
                "images": images,
                "scannedAt": NOW.isoformat(),
                "scanner": {"VulnerabilityDB": {"UpdatedAt": NOW.isoformat()}},
            }
            summary_path = folder / "images/security-summary.json"
            summary_path.write_text(json.dumps(summary))
            (folder / "image-smoke.json").write_text(
                json.dumps({"sourceSha": SHA, "status": "passed", "imageIds": ids})
            )
            review = {"sourceSha": SHA, "approvedBy": "owner", "findings": []}
            self.assertEqual(len(candidate(folder, SHA, review, "owner", NOW)[0]), 2)
            with self.assertRaises(ValueError):
                candidate(folder, SHA, review, "owner", NOW + timedelta(hours=25))
            (folder / "images/api-scan.json").write_text("{}")
            with self.assertRaises(ValueError):
                candidate(folder, SHA, review, "owner", NOW)

    def test_complete_requires_both_images_and_remote_evidence(self):
        class FakeRegistry:
            blobs = {}
            fail_second = False

            def preflight(self, name, tags):
                return "owner/" + name

            def verify(self, repo, *args):
                if self.fail_second and repo.endswith("frontend"):
                    raise ValueError("Second publication failed")
                return "sha256:" + "3" * 64

            def get(self, repo, path):
                return self.blobs[path]

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "images").mkdir()
            registry = FakeRegistry()
            journal = {"images": [], "status": "blocked"}

            def run(*args):
                if args[:2] != ("oras", "attach"):
                    return ""
                export = Path(args[args.index("--export-manifest") + 1])
                attachment = json.dumps({"subject": {"digest": "sha256:" + "3" * 64}, "layers": []}).encode()
                export.write_bytes(attachment)
                registry.blobs["manifests/" + digest(attachment)] = attachment
                registry.blobs["referrers/sha256:" + "3" * 64] = json.dumps(
                    {"manifests": [{"digest": digest(attachment)}]}
                ).encode()
                return ""

            images = [{"imageId": "sha256:" + c * 64, "name": n} for n, c in (("api", "1"), ("web", "2"))]
            builds = [{"buildx.build.provenance": {"materials": []}}] * 2
            publish_images(registry, images, builds, SHA, "v1.0.0", folder, journal, lambda: None, run)
            self.assertEqual(journal["status"], "complete")
            self.assertEqual([i["status"] for i in journal["images"]], ["verified", "verified"])
            registry.fail_second = True
            journal = {"images": [], "status": "blocked"}
            with self.assertRaises(ValueError):
                publish_images(registry, images, builds, SHA, "v1.0.0", folder, journal, lambda: None, run)
            self.assertEqual(journal["status"], "incomplete")
            self.assertEqual(journal["images"][0]["status"], "verified")
            self.assertEqual(journal["images"][1]["status"], "push-started")

    def test_all_preflights_precede_writes_and_failure_keeps_incomplete_journal(self):
        class FakeRegistry:
            calls = []

            def preflight(self, name, tags):
                self.calls.append(("preflight", name))
                return "owner/" + name

            def verify(self, *args):
                return "sha256:" + "1" * 64

        registry = FakeRegistry()
        journal = {"status": "blocked", "images": []}
        snapshots = []

        def run(*args):
            registry.calls.append(args)
            if args[:2] == ("docker", "push"):
                raise ValueError("Synthetic network failure after a possible registry write")

        images = [{"imageId": "sha256:" + "2" * 64, "name": n} for n in ("api", "web")]
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(ValueError):
            publish_images(
                registry,
                images,
                [{}, {}],
                SHA,
                "v1.0.0",
                Path(temp),
                journal,
                lambda: snapshots.append(json.loads(json.dumps(journal))),
                run,
            )
        self.assertEqual([c[0] for c in registry.calls[:2]], ["preflight", "preflight"])
        self.assertEqual(journal["status"], "incomplete")
        self.assertEqual(journal["images"][0]["status"], "push-started")
        self.assertEqual(len(journal["images"]), 1)
        self.assertTrue(snapshots)


if __name__ == "__main__":
    unittest.main()
