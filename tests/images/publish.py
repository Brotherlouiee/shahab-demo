"""Protected Docker Hub publication; never called by PR/push builds.

No rebuild, implicit latest, tag overwrite, automatic recovery or deployment.
An interrupted/partial publication remains blocked and retains its journal.
"""

import base64
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

from release_policy import api, validate_image_evidence, validate_request
from security_gate import assess

IMMUTABLE_RULE = r"^(v[0-9]+\.[0-9]+\.[0-9]+|sha-[0-9a-f]{40})$"
MEDIA = "application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.manifest.v1+json"
ARTIFACT_TYPE = "application/vnd.shahab.release-evidence.v1+json"


def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def command(*args):
    # Avoid printing tool stderr (may contain authentication/server details).
    result = subprocess.run(args, text=True, capture_output=True, check=False, timeout=180)
    if result.returncode:
        raise ValueError("Publication command failed: " + args[0] + " " + args[1])
    return result.stdout


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward PAT/bearer credentials to another URL.


def request(url, headers=None, data=None, method="GET", missing=False):
    if urllib.parse.urlparse(url).scheme != "https" or urllib.parse.urlparse(url).netloc not in {
        "hub.docker.com",
        "auth.docker.io",
        "registry-1.docker.io",
    }:
        raise ValueError("Unexpected credential destination")
    req = urllib.request.Request(url, headers=headers or {}, data=data, method=method)
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        # Hub may serve blobs through a signed CDN URL. Follow one HTTPS blob
        # redirect without ANY original Authorization header; verify blob hashes.
        location = error.headers.get("Location", "")
        if (
            error.code == 307
            and method == "GET"
            and "/blobs/" in url
            and urllib.parse.urlparse(location).scheme == "https"
        ):
            with urllib.request.build_opener(NoRedirect).open(location, timeout=30) as response:
                return response.read()
        if missing and error.code == 404:
            return None
        raise ValueError("Registry HTTP error " + str(error.code)) from None
    except urllib.error.URLError:
        raise ValueError("Registry transport failure") from None


class Registry:
    def __init__(self, namespace, username, token):
        self.namespace, self.username, self.token = namespace, username, token
        self.bearers = {}
        response = request(
            "https://hub.docker.com/v2/auth/token",
            {"Content-Type": "application/json"},
            json.dumps({"identifier": username, "secret": token}).encode(),
            "POST",
        )
        self.hub_token = json.loads(response)["access_token"]

    def preflight(self, name, tags):
        repo = self.namespace + "/" + name
        info = json.loads(
            request(
                "https://hub.docker.com/v2/namespaces/" + self.namespace + "/repositories/" + name,
                {"Authorization": "Bearer " + self.hub_token},
            )
        )
        policy = info.get("immutable_tags_settings", {})
        if policy.get("enabled") is not True or IMMUTABLE_RULE not in policy.get("rules", []):
            raise ValueError("Configure the documented immutable release-tag rule on both repositories")
        basic = base64.b64encode((self.username + ":" + self.token).encode()).decode()
        query = urllib.parse.urlencode({"service": "registry.docker.io", "scope": "repository:" + repo + ":pull,push"})
        token = json.loads(request("https://auth.docker.io/token?" + query, {"Authorization": "Basic " + basic}))[
            "token"
        ]
        self.bearers[repo] = token
        for tag in tags:
            if self.get(repo, "manifests/" + tag, missing=True) is not None:
                raise ValueError("Release tag already exists; no overwrite or automatic partial-release retry")
        return repo

    def get(self, repo, path, missing=False):
        accept = "application/vnd.oci.image.index.v1+json" if path.startswith("referrers/") else MEDIA
        return request(
            "https://registry-1.docker.io/v2/" + repo + "/" + path,
            {"Authorization": "Bearer " + self.bearers[repo], "Accept": accept},
            missing=missing,
        )

    def verify(self, repo, tag, image_id, sha):
        manifest = self.get(repo, "manifests/" + tag)
        config_digest = json.loads(manifest)["config"]["digest"]
        if config_digest != image_id:
            raise ValueError("Published image differs from the tested image")
        config = self.get(repo, "blobs/" + config_digest)
        if (
            digest(config) != image_id
            or json.loads(config)["config"]["Labels"]["org.opencontainers.image.revision"] != sha
        ):
            raise ValueError("Published config/revision mismatch")
        return digest(manifest)


def validate_environment(info, branches, owner):
    reviewers = [
        reviewer.get("reviewer", {}).get("login", "").lower()
        for rule in info.get("protection_rules", [])
        if rule.get("type") == "required_reviewers"
        for reviewer in rule.get("reviewers", [])
    ]
    policy = info.get("deployment_branch_policy") or {}
    names = [(b.get("name"), b.get("type")) for b in branches.get("branch_policies", [])]
    if (
        reviewers != [owner.lower()]
        or policy.get("custom_branch_policies") is not True
        or names != [("main", "branch")]
    ):
        raise ValueError("Environment must require the repository owner and allow only the main branch")


def validate_review(review, sha, reports, owner, now):
    """Each remaining finding needs its own explicit, time-bounded owner decision."""
    if review.get("sourceSha") != sha or review.get("approvedBy", "").lower() != owner.lower():
        raise ValueError("Missing owner security review for this source SHA")
    actual = set()
    for name, report in reports.items():
        for result in report.get("Results", []):
            for finding in result.get("Vulnerabilities") or []:
                severity = finding.get("Severity")
                if severity not in {"LOW", "MEDIUM"}:
                    raise ValueError("Unacceptable or unknown finding; no security override")
                actual.add(
                    (name, finding["VulnerabilityID"], finding["PkgName"], finding["InstalledVersion"], severity)
                )
    decisions = {}
    for entry in review.get("findings", []):
        key = tuple(entry.get(k) for k in ("image", "id", "package", "version", "severity"))
        if key in decisions or not entry.get("owner") or not entry.get("mitigation"):
            raise ValueError("Duplicate finding or missing risk owner/mitigation")
        deadline = datetime.fromisoformat(entry.get("deadline", "").replace("Z", "+00:00"))
        if deadline.tzinfo is None or deadline <= now or entry.get("decision") != "accepted":
            raise ValueError("Risk decision missing or expired")
        decisions[key] = entry
    if set(decisions) != actual:
        raise ValueError("Security decisions do not exactly cover the current findings")


def candidate(folder, sha, review, owner, now):
    summary = json.loads((folder / "images/security-summary.json").read_text())
    smoke = json.loads((folder / "image-smoke.json").read_text())
    builds = [json.loads((folder / f"images/{name}-build.json").read_text()) for name in ("api", "web")]
    images = validate_image_evidence(sha, summary, smoke, builds)
    for timestamp in (summary["scannedAt"], summary["scanner"]["VulnerabilityDB"]["UpdatedAt"]):
        elapsed = now - datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if not timedelta(0) <= elapsed <= timedelta(hours=24):
            raise ValueError("Publication requires fresh scan and vulnerability database")
    reports = {}
    for image in summary["images"]:
        name = image["name"]
        raw = (folder / f"images/{name}-scan.json").read_bytes()
        reports[name] = json.loads(raw)
        counts = assess(reports[name], image["imageId"])
        if digest(raw) != "sha256:" + image["reportSha256"] or counts != image["counts"]:
            raise ValueError("Scan evidence hash/count mismatch")
        sbom = json.loads((folder / f"images/{name}-sbom.cdx.json").read_text())
        if sbom.get("bomFormat") != "CycloneDX" or not sbom.get("components"):
            raise ValueError("Missing SBOM inventory")
    validate_review(review, sha, reports, owner, now)
    return images, builds


def publish_images(registry, images, builds, sha, tag, folder, journal, save, run=command):
    tags = [tag, "sha-" + sha]
    # All four tags, immutability and both repositories checked before any push.
    repos = [registry.preflight(name, tags) for name in ("shahab-api", "shahab-frontend")]
    for image, build, repo in zip(images, builds, repos, strict=True):
        record = {"repository": repo, "imageId": image["imageId"], "status": "push-started"}
        journal["images"].append(record)
        journal["status"] = "incomplete"
        save()  # Journal before mutation: failure/timeout may have written remote data.
        target = "docker.io/" + repo
        run("docker", "tag", image["imageId"], target + ":" + tag)
        run("docker", "push", target + ":" + tag)
        remote = registry.verify(repo, tag, image["imageId"], sha)
        record.update({"digest": remote, "status": "version-pushed"})
        save()
        run("oras", "tag", target + "@" + remote, tags[1])
        if registry.verify(repo, tags[1], image["imageId"], sha) != remote:
            raise ValueError("Version and SHA tags have different remote digests")
        # Buildx emitted an unsigned SLSA v0.2 predicate. Bind it to the actual
        # pushed subject; retaining metadata is not a cryptographic signature.
        provenance = folder / f"images/{image['name']}-provenance.json"
        provenance.write_text(
            json.dumps(
                {
                    "_type": "https://in-toto.io/Statement/v0.1",
                    "subject": [{"name": target, "digest": {"sha256": remote.removeprefix("sha256:")}}],
                    "predicateType": "https://slsa.dev/provenance/v0.2",
                    "predicate": build["buildx.build.provenance"],
                },
                indent=2,
            )
            + "\n"
        )
        exported = folder / f"images/{image['name']}-attachment.json"
        run(
            "oras",
            "attach",
            "--distribution-spec",
            "v1.1-referrers-api",
            "--artifact-type",
            ARTIFACT_TYPE,
            "--export-manifest",
            str(exported),
            target + "@" + remote,
            str(folder / f"images/{image['name']}-sbom.cdx.json") + ":application/vnd.cyclonedx+json",
            str(provenance) + ":application/vnd.in-toto+json",
        )
        attachment = exported.read_bytes()
        attachment_digest = digest(attachment)
        parsed = json.loads(attachment)
        if parsed.get("subject", {}).get("digest") != remote:
            raise ValueError("Evidence attachment subject mismatch")
        if registry.get(repo, "manifests/" + attachment_digest) != attachment:
            raise ValueError("Remote evidence manifest mismatch")
        # Verify uploaded evidence blobs, not only their local manifests.
        for layer in parsed["layers"]:
            if digest(registry.get(repo, "blobs/" + layer["digest"])) != layer["digest"]:
                raise ValueError("Remote evidence blob mismatch")
        referrers = json.loads(registry.get(repo, "referrers/" + remote))
        if attachment_digest not in [item.get("digest") for item in referrers.get("manifests", [])]:
            raise ValueError("Published evidence is not discoverable by subject digest")
        record.update({"tags": tags, "evidenceDigest": attachment_digest, "status": "verified"})
        save()
    journal["status"] = "complete"
    journal["completedAt"] = datetime.now(UTC).isoformat()
    save()


def main():
    sha, tag = os.environ["APPROVED_SHA"], os.environ["VERSION_TAG"]
    validate_request(os.environ["GITHUB_EVENT_NAME"], os.environ["GITHUB_REF"], tag, sha, sha, "identical")
    namespace = os.environ["DOCKERHUB_NAMESPACE"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,29}", namespace):
        raise ValueError("Docker Hub namespace has not been configured")
    repo, owner = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_REPOSITORY_OWNER"]
    prefix = "repos/" + repo + "/environments/dockerhub-publish"
    validate_environment(api(prefix)[0], api(prefix + "/deployment-branch-policies")[0], owner)
    folder = Path("test-results")
    journal = {
        "sourceSha": sha,
        "versionTag": tag,
        "namespace": namespace,
        "status": "blocked",
        "images": [],
        "deployed": False,
        "runId": os.environ["GITHUB_RUN_ID"],
        "createdAt": datetime.now(UTC).isoformat(),
    }

    def save():
        (folder / "publication.json").write_text(json.dumps(journal, indent=2) + "\n")

    save()
    try:
        images, builds = candidate(folder, sha, json.loads(os.environ["SECURITY_REVIEW"]), owner, datetime.now(UTC))
        for image in images:
            command("docker", "load", "--input", "candidate/" + image["name"] + ".tar")
            info = json.loads(command("docker", "image", "inspect", image["imageId"]))[0]
            if info["Id"] != image["imageId"] or info["Config"]["Labels"]["org.opencontainers.image.revision"] != sha:
                raise ValueError("Loaded image does not match approved evidence")
        registry = Registry(namespace, os.environ["DOCKERHUB_USERNAME"], os.environ["DOCKERHUB_TOKEN"])
        publish_images(registry, images, builds, sha, tag, folder, journal, save)
    except Exception:
        journal["failure"] = (
            "Publication blocked/incomplete; inspect the failed step and retained evidence before recovery"
        )
        save()
        raise


if __name__ == "__main__":
    main()
