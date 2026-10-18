"""Read-only eligibility check for A.3; never publish, create a tag or deploy.

Only an explicit workflow_dispatch on main, naming a strict version tag and its
approved commit, can qualify. The tag must resolve to that commit, be ancestral
to main and have all seven successful jobs in the latest main-push gate runs.
GitHub/API errors and incomplete evidence fail closed. No owner secret is used.
"""

import json
import os
import re
import subprocess
import tempfile
import urllib.parse
from pathlib import Path

REQUIRED = {
    ".github/workflows/quality.yml": {
        "Quality gates",
        "PostgreSQL migration verification",
        "Loan details browser verification",
        "Profile OTP real API browser verification",
    },
    ".github/workflows/security.yml": {"Python SAST and Python/Node dependency audit"},
    ".github/workflows/us13-baseline.yml": {"Independent original-vs-candidate route evidence"},
    ".github/workflows/image-smoke.yml": {"Build and run two isolated images"},
}


def validate_request(event, ref, tag, approved, resolved, comparison):
    if event != "workflow_dispatch" or ref != "refs/heads/main":
        raise ValueError("Only explicit dispatch from main is eligible")
    if not re.fullmatch(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", tag):
        raise ValueError("Version must be vX.Y.Z without suffix or leading zero")
    if not re.fullmatch(r"[0-9a-f]{40}", approved) or resolved != approved:
        raise ValueError("Tag does not identify the explicitly approved SHA")
    if comparison not in {"ahead", "identical"}:
        raise ValueError("Approved commit is not in main history")


def validate_gates(sha, runs, jobs_by_run):
    """Use latest run, not an older green run hiding a newer failure."""
    selected = []
    for path, names in REQUIRED.items():
        candidates = [
            r
            for r in runs
            if r.get("path") == path
            and r.get("head_sha") == sha
            and r.get("head_branch") == "main"
            and r.get("event") == "push"
        ]
        if not candidates:
            raise ValueError("Missing main-push workflow: " + path)
        run = max(candidates, key=lambda r: r["id"])
        if run.get("status") != "completed" or run.get("conclusion") != "success":
            raise ValueError("Latest workflow not successful: " + path)
        jobs = jobs_by_run.get(run["id"], [])
        for name in names:
            matching = [j for j in jobs if j.get("name") == name]
            if len(matching) != 1 or matching[0].get("conclusion") != "success":
                raise ValueError("Required job missing/skipped/failed: " + name)
            if matching[0].get("head_sha") != sha or matching[0].get("status") != "completed":
                raise ValueError("Job belongs to a different SHA or is incomplete")
        selected.append({"path": path, "id": run["id"], "attempt": run["run_attempt"]})
    return selected


def validate_image_evidence(sha, summary, smoke, builds):
    """A green A.1-era job without A.2 scan/provenance must never qualify."""
    if summary.get("sourceSha") != sha or summary.get("status") != "passed":
        raise ValueError("Missing successful scan at approved SHA")
    if smoke.get("sourceSha") != sha or smoke.get("status") != "passed":
        raise ValueError("Missing successful smoke at approved SHA")
    images = summary.get("images", [])
    if [i.get("name") for i in images] != ["api", "web"]:
        raise ValueError("Both images required")
    ids = [i.get("imageId") for i in images]
    if ids != smoke.get("imageIds") or len(set(ids)) != 2:
        raise ValueError("Scan/smoke images differ")
    for image, build in zip(images, builds, strict=True):
        if image.get("counts", {}).get("HIGH") != 0 or image.get("counts", {}).get("CRITICAL") != 0:
            raise ValueError("High/critical image findings")
        if build.get("containerimage.config.digest") != image["imageId"] or not build.get("buildx.build.provenance"):
            raise ValueError("Missing matching build provenance")
    return [{"name": i["name"], "imageId": i["imageId"], "buildDigest": i["buildDigest"]} for i in images]


def api(endpoint):
    # gh handles credentials without placing them in arguments or output. Read
    # pages explicitly; failures raise, and no response body is logged.
    response = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", endpoint], check=True, text=True, stdout=subprocess.PIPE
    ).stdout
    return json.loads(response)


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid repository")
    tag, approved = os.environ["VERSION_TAG"], os.environ["APPROVED_SHA"]
    # Validate untrusted inputs before using either in an API path.
    validate_request(os.environ["GITHUB_EVENT_NAME"], os.environ["GITHUB_REF"], tag, approved, approved, "identical")
    prefix = "repos/" + repo
    obj = api(prefix + "/git/ref/tags/" + urllib.parse.quote(tag, safe=""))[0]["object"]
    for _ in range(5):
        if obj["type"] == "commit":
            break
        if obj["type"] != "tag" or not re.fullmatch(r"[0-9a-f]{40}", obj["sha"]):
            raise ValueError("Invalid annotated tag")
        obj = api(prefix + "/git/tags/" + obj["sha"])[0]["object"]
    if obj["type"] != "commit":
        raise ValueError("Tag does not resolve to a commit")
    comparison = api(prefix + "/compare/" + approved + "...main")[0]["status"]
    validate_request(os.environ["GITHUB_EVENT_NAME"], os.environ["GITHUB_REF"], tag, approved, obj["sha"], comparison)
    runs = [
        r
        for page in api(prefix + "/actions/runs?event=push&branch=main&head_sha=" + approved + "&per_page=100")
        for r in page["workflow_runs"]
    ]
    relevant = [r for r in runs if r.get("path") in REQUIRED]
    latest = {p: max((r for r in relevant if r["path"] == p), key=lambda r: r["id"], default=None) for p in REQUIRED}
    jobs = {
        r["id"]: [
            j
            for page in api(prefix + "/actions/runs/" + str(r["id"]) + "/jobs?filter=latest&per_page=100")
            for j in page["jobs"]
        ]
        for r in latest.values()
        if r
    }
    gates = validate_gates(approved, runs, jobs)
    image_run = next(g["id"] for g in gates if g["path"] == ".github/workflows/image-smoke.yml")
    with tempfile.TemporaryDirectory(prefix="shahab-release-evidence-") as temporary:
        subprocess.run(
            [
                "gh",
                "run",
                "download",
                str(image_run),
                "--repo",
                repo,
                "--name",
                "container-build-contract-evidence",
                "--dir",
                temporary,
            ],
            check=True,
            capture_output=True,
        )
        folder = Path(temporary)
        summary = json.loads((folder / "images/security-summary.json").read_text())
        smoke = json.loads((folder / "image-smoke.json").read_text())
        builds = [json.loads((folder / f"images/{name}-build.json").read_text()) for name in ("api", "web")]
        images = validate_image_evidence(approved, summary, smoke, builds)
        for name in ("api", "web"):
            sbom = json.loads((folder / f"images/{name}-sbom.cdx.json").read_text())
            if sbom.get("bomFormat") != "CycloneDX" or not sbom.get("components"):
                raise ValueError("Missing SBOM inventory")
    output = {
        "sourceSha": approved,
        "versionTag": tag,
        "gateRuns": gates,
        "images": images,
        "eligibleForA3": True,
        "approvalRun": os.environ["GITHUB_RUN_ID"],
        "published": False,
        "deployed": False,
        "remaining": "A.3 namespace, restricted credentials, protected approval and actual publish/digest proof",
    }
    folder = Path("test-results")
    folder.mkdir(exist_ok=True)
    (folder / "release-eligibility.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output))


if __name__ == "__main__":
    main()
