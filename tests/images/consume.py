"""Pull a published pair by digest and exercise it without building or deploying.

The committed manifest is matched to a successful main publication and its journal.
Credentials are handled by docker/login-action, never by this script. Runtime
probes reuse the smoke harness from each approved source checkout. A first release
has no rollback target: its result must explicitly retain that blocker.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from release_policy import api

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = "Brotherlouiee/shahab-demo"
VERSION = r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
DIGEST = r"sha256:[a-f0-9]{64}"
JOURNAL_KEYS = (
    "sourceSha",
    "versionTag",
    "namespace",
    "status",
    "images",
    "deployed",
    "runId",
    "createdAt",
    "completedAt",
)


def command(*args, cwd=ROOT):
    # Never propagate credential-bearing stderr or arbitrary runtime output.
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=300, check=False)
    if result.returncode:
        raise ValueError("Consumption command failed: " + args[0] + " " + args[1])
    return result.stdout


def validate_manifest(value):
    """Only the approved namespace and an exact complete, non-deployed pair pass."""
    sha = value.get("sourceSha", "")
    version = value.get("versionTag", "")
    if (
        value.get("schemaVersion") != 1
        or value.get("status") != "complete"
        or value.get("deployed") is not False
        or value.get("namespace") != "shahab2026"
        or not re.fullmatch(r"[a-f0-9]{40}", sha)
        or not re.fullmatch(VERSION, version)
        or not re.fullmatch(r"[1-9][0-9]*", str(value.get("runId", "")))
    ):
        raise ValueError("Invalid or incomplete publication manifest")
    images = value.get("images", [])
    if len(images) != 2:
        raise ValueError("Both published images are required")
    for item, name in zip(images, ("shahab-backend", "shahab-frontend"), strict=True):
        if (
            item.get("repository") != "shahab2026/" + name
            or item.get("status") != "verified"
            or item.get("tags") != [version, "sha-" + sha]
            or any(not re.fullmatch(DIGEST, item.get(key, "")) for key in ("digest", "imageId", "evidenceDigest"))
        ):
            raise ValueError("Invalid image identity, order or tags")
    if len({i["digest"] for i in images}) != 2 or len({i["imageId"] for i in images}) != 2:
        raise ValueError("API and frontend must be distinct images")
    created, completed = [datetime.fromisoformat(value[k]) for k in ("createdAt", "completedAt")]
    if not created.tzinfo or not completed.tzinfo or completed < created:
        raise ValueError("Invalid publication timestamps")
    evidence = value.get("publicationEvidence", {})
    if (
        not re.fullmatch(r"[a-f0-9]{64}", evidence.get("journalSha256", ""))
        or not isinstance(evidence.get("artifactId"), int)
        or evidence["artifactId"] <= 0
        or evidence.get("runUrl") != f"https://github.com/{REPOSITORY}/actions/runs/{value['runId']}"
    ):
        raise ValueError("Missing publication trace")
    compatibility = value.get("compatibility", {})
    if (
        compatibility.get("sourceBundleSha") != sha
        or compatibility.get("apiVersion") != "/api/v1"
        or compatibility.get("deploymentEligible") is not False
        or not compatibility.get("databaseRevision")
        or "dataSnapshot" not in compatibility
        or "configSnapshot" not in compatibility
    ):
        raise ValueError("Missing compatibility boundary")
    return value


def load_manifest(version):
    if not re.fullmatch(VERSION, version):
        raise ValueError("Version must be vX.Y.Z; paths and suffixes are not allowed")
    return validate_manifest(json.loads((ROOT / f"docs/release/images/{version}.json").read_text()))


def validate_publication(value, run, raw):
    if (
        run.get("repository", {}).get("full_name") != REPOSITORY
        or str(run.get("id")) != value["runId"]
        or run.get("path") != ".github/workflows/image-publish.yml"
        or run.get("event") != "workflow_dispatch"
        or run.get("head_branch") != "main"
        or run.get("head_sha") != value["sourceSha"]
        or run.get("status") != "completed"
        or run.get("conclusion") != "success"
        or hashlib.sha256(raw).hexdigest() != value["publicationEvidence"]["journalSha256"]
        or json.loads(raw) != {k: value[k] for k in JOURNAL_KEYS}
    ):
        raise ValueError("Manifest does not match the successful publication journal")


def verify_publication(value):
    """Download evidence by run/name; artifact ID and journal hash must both agree."""
    import tempfile

    prefix = f"repos/{REPOSITORY}/actions/runs/{value['runId']}"
    run = api(prefix)[0]
    artifacts = [a for p in api(prefix + "/artifacts?per_page=100") for a in p["artifacts"]]
    matches = [a for a in artifacts if a["name"] == "dockerhub-publication-evidence" and not a["expired"]]
    if len(matches) != 1 or matches[0]["id"] != value["publicationEvidence"]["artifactId"]:
        raise ValueError("Exact publication artifact unavailable; do not substitute another run")
    with tempfile.TemporaryDirectory(prefix="shahab-publication-") as folder:
        command(
            "gh",
            "run",
            "download",
            value["runId"],
            "--repo",
            REPOSITORY,
            "--name",
            "dockerhub-publication-evidence",
            "--dir",
            folder,
        )
        validate_publication(value, run, (Path(folder) / "publication.json").read_bytes())


def validate_rollback(current, previous):
    """No same-version rehearsal or unapproved compatibility assumption."""
    if (
        current["sourceSha"] == previous["sourceSha"]
        or current["versionTag"] == previous["versionTag"]
        or any(a["digest"] == b["digest"] for a, b in zip(current["images"], previous["images"], strict=True))
        or datetime.fromisoformat(previous["completedAt"]) >= datetime.fromisoformat(current["createdAt"])
        or current.get("previousRelease") != previous["versionTag"]
    ):
        raise ValueError("No distinct, earlier, explicitly recorded rollback pair")
    for key in ("apiVersion", "databaseRevision", "dataSnapshot", "configSnapshot"):
        if current["compatibility"][key] != previous["compatibility"][key]:
            raise ValueError("Rollback compatibility differs; independent review is required")


def inspect_image(item, sha, info):
    reference = item["repository"] + "@" + item["digest"]
    refs = {s.removeprefix("docker.io/") for s in info.get("RepoDigests", [])}
    user = info.get("Config", {}).get("User", "")
    if (
        info.get("Id") != item["imageId"]
        or reference not in refs
        or info.get("Config", {}).get("Labels", {}).get("org.opencontainers.image.revision") != sha
        or not user
        or user.split(":")[0] in {"root", "0"}
    ):
        raise ValueError("Pulled digest/config/revision/non-root identity mismatch")


def smoke(value, source, run=command):
    if run("git", "rev-parse", "HEAD", cwd=source).strip() != value["sourceSha"]:
        raise ValueError("Reference checkout is not the published source")
    refs = []
    for item in value["images"]:
        ref = "docker.io/" + item["repository"] + "@" + item["digest"]
        run("docker", "pull", "--platform", "linux/amd64", ref)
        inspect_image(item, value["sourceSha"], json.loads(run("docker", "image", "inspect", ref))[0])
        refs.append(ref)
    # The source harness uses disposable names/loopback ports and removes only
    # its containers/network in finally. It has no database or owner volumes.
    run(sys.executable, "tests/images/smoke.py", "--api-image", refs[0], "--web-image", refs[1], cwd=source)
    proof = json.loads((source / "test-results/image-smoke.json").read_text())
    if (
        proof.get("status") != "passed"
        or proof.get("sourceSha") != value["sourceSha"]
        or proof.get("imageIds") != [i["imageId"] for i in value["images"]]
    ):
        raise ValueError("Remote-image smoke proof mismatch")
    return {"version": value["versionTag"], "sourceSha": value["sourceSha"], "pullReferences": refs, "smoke": proof}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run"))
    parser.add_argument("--version", default="v0.1.0")
    parser.add_argument("--previous-version", default="")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--previous-source", type=Path)
    args = parser.parse_args()
    if os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch" or os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise ValueError("Consumption requires manual main execution")
    current = load_manifest(args.version)
    previous = load_manifest(args.previous_version) if args.previous_version else None
    if current.get("previousRelease") and not previous:
        raise ValueError("Supply the recorded previous release; do not skip rollback")
    if previous:
        validate_rollback(current, previous)
    if args.mode == "prepare":
        for value in (current, previous):
            if value:
                verify_publication(value)
        with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
            output.write(f"source_sha={current['sourceSha']}\n")
            output.write(f"previous_sha={previous['sourceSha'] if previous else ''}\n")
        return
    folder = ROOT / "test-results"
    folder.mkdir(exist_ok=True)
    result = {
        "taskId": "US-12.T04A.4",
        "status": "incomplete",
        "deployed": False,
        "runId": os.environ["GITHUB_RUN_ID"],
        "startedAt": datetime.now(UTC).isoformat(),
        "checks": [],
    }
    try:
        if not args.source or (previous and not args.previous_source):
            raise ValueError("Supply independent source references")
        result["checks"].append(smoke(current, args.source.resolve()))
        result["consumptionStatus"] = "passed"
        if previous:
            result["checks"].append(smoke(previous, args.previous_source.resolve()))
            result["checks"].append(smoke(current, args.source.resolve()))
            result["rollbackStatus"] = "isolated-pair-restart-passed"
            result["status"] = "isolated-checks-passed"
        else:
            result["rollbackStatus"] = "blocked-no-previous-release"
            result["status"] = "consumption-passed-rollback-blocked"
        result["completedAt"] = datetime.now(UTC).isoformat()
    finally:
        (folder / "image-consumption.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result))


if __name__ == "__main__":
    main()
