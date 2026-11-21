"""Fail-closed consumption: identity, publication origin and rollback boundaries."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from consume import (
    JOURNAL_KEYS,
    REPOSITORY,
    ROOT,
    inspect_image,
    load_manifest,
    smoke,
    validate_manifest,
    validate_publication,
    validate_rollback,
)


def release():
    return json.loads((ROOT / "docs/release/images/v0.1.0.json").read_text())


def source_run(value):
    return {
        "id": int(value["runId"]),
        "repository": {"full_name": REPOSITORY},
        "path": ".github/workflows/image-publish.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": value["sourceSha"],
        "status": "completed",
        "conclusion": "success",
    }


def journal(value):
    raw = (json.dumps({k: value[k] for k in JOURNAL_KEYS}) + "\n").encode()
    value["publicationEvidence"]["journalSha256"] = hashlib.sha256(raw).hexdigest()
    return raw


def info(item, sha):
    return {
        "Id": item["imageId"],
        "RepoDigests": [item["repository"] + "@" + item["digest"]],
        "Config": {"User": "10001", "Labels": {"org.opencontainers.image.revision": sha}},
    }


class ConsumeTests(unittest.TestCase):
    def test_real_manifest_has_two_distinct_images_and_no_fake_previous(self):
        value = validate_manifest(release())
        self.assertEqual(value["runId"], "39224423986")
        self.assertIsNone(value["previousRelease"])
        self.assertFalse(value["compatibility"]["deploymentEligible"])
        self.assertIsNone(value["compatibility"]["dataSnapshot"])

    def test_reject_partial_wrong_namespace_tag_sha_and_timestamp(self):
        for path, bad in [
            (("status",), "incomplete"),
            (("images",), release()["images"][:1]),
            (("namespace",), "another"),
            (("sourceSha",), "short"),
            (("versionTag",), "latest"),
            (("completedAt",), "2000-01-01T00:00:00+00:00"),
            (("deployed",), True),
            (("images", 0, "tags"), ["v0.1.0", "sha-other"]),
            (("images", 1, "repository"), "shahab2026/shahab-backend"),
            (("images", 0, "digest"), "sha256:bad"),
        ]:
            value = release()
            target = value
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = bad
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_manifest(value)

    def test_version_cannot_escape_manifest_directory(self):
        for version in ("../../main", "v01.0.0", "v0.1.0\n", "v0.1.0-rc", "{}"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                load_manifest(version)

    def test_exact_journal_and_main_run_pass(self):
        value = release()
        raw = journal(value)
        validate_publication(value, source_run(value), raw)

    def test_failed_pr_wrong_source_repo_and_workflow_never_authorize_pull(self):
        value = release()
        raw = journal(value)
        for key, bad in [
            ("conclusion", "failure"),
            ("status", "in_progress"),
            ("head_branch", "other"),
            ("head_sha", "a" * 40),
            ("event", "pull_request"),
            ("repository", {"full_name": "other/repo"}),
            ("path", "another.yml"),
            ("id", 42),
        ]:
            run = source_run(value)
            run[key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_publication(value, run, raw)

    def test_tampered_journal_even_with_new_hash_is_rejected(self):
        value = release()
        altered = copy.deepcopy(value)
        altered["images"][0]["digest"] = "sha256:" + "a" * 64
        raw = journal(altered)
        value["publicationEvidence"]["journalSha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaises(ValueError):
            validate_publication(value, source_run(value), raw)
        with self.assertRaises(ValueError):
            validate_publication(value, source_run(value), b"{}")

    def test_pull_identity_checks_digest_id_revision_and_non_root(self):
        value = release()
        item = value["images"][0]
        valid = info(item, value["sourceSha"])
        inspect_image(item, value["sourceSha"], valid)
        for key, bad in [("Id", "sha256:" + "a" * 64), ("RepoDigests", [])]:
            altered = copy.deepcopy(valid)
            altered[key] = bad
            with self.assertRaises(ValueError):
                inspect_image(item, value["sourceSha"], altered)
        for user in ("", "root", "0:10001"):
            altered = copy.deepcopy(valid)
            altered["Config"]["User"] = user
            with self.assertRaises(ValueError):
                inspect_image(item, value["sourceSha"], altered)
        valid["Config"]["Labels"]["org.opencontainers.image.revision"] = "a" * 40
        with self.assertRaises(ValueError):
            inspect_image(item, value["sourceSha"], valid)

    def test_smoke_pulls_both_remote_digests_without_build_push_or_tag(self):
        value = release()
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "test-results").mkdir()
            proof = {
                "status": "passed",
                "sourceSha": value["sourceSha"],
                "imageIds": [i["imageId"] for i in value["images"]],
            }
            (source / "test-results/image-smoke.json").write_text(json.dumps(proof))

            def run(*args, **kwargs):
                calls.append(args)
                if args[:3] == ("git", "rev-parse", "HEAD"):
                    return value["sourceSha"]
                if args[:3] == ("docker", "image", "inspect"):
                    item = next(i for i in value["images"] if args[3].endswith(i["digest"]))
                    return json.dumps([info(item, value["sourceSha"])])
                return ""

            result = smoke(value, source, run)
            self.assertEqual(result["smoke"], proof)
        self.assertEqual(len([c for c in calls if c[:2] == ("docker", "pull")]), 2)
        self.assertFalse(any(c[:2] in [("docker", "build"), ("docker", "push"), ("docker", "tag")] for c in calls))

    def test_wrong_source_stops_before_registry_access(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                smoke(release(), Path(directory), lambda *a, **kw: "wrong-source")

    def test_first_release_does_not_claim_same_pair_as_rollback(self):
        with self.assertRaises(ValueError):
            validate_rollback(release(), release())

    def test_distinct_prior_pair_requires_recorded_compatible_versions(self):
        previous = release()
        current = release()
        current.update(
            {
                "sourceSha": "a" * 40,
                "versionTag": "v0.2.0",
                "previousRelease": "v0.1.0",
                "createdAt": "2026-10-20T00:00:00+00:00",
            }
        )
        for index, image in enumerate(current["images"]):
            image["digest"] = "sha256:" + str(index + 1) * 64
        validate_rollback(current, previous)
        current["compatibility"]["databaseRevision"] = "changed-schema"
        with self.assertRaises(ValueError):
            validate_rollback(current, previous)
        current["compatibility"] = copy.deepcopy(previous["compatibility"])
        current["previousRelease"] = None
        with self.assertRaises(ValueError):
            validate_rollback(current, previous)

    def test_pr_event_cannot_use_consumer(self):
        with patch.dict("os.environ", {"GITHUB_EVENT_NAME": "pull_request", "GITHUB_REF": "refs/heads/main"}):
            with patch("sys.argv", ["consume.py", "prepare"]), self.assertRaises(ValueError):
                from consume import main

                main()


if __name__ == "__main__":
    unittest.main()
