"""Scan the exact smoke-tested images; no registry writes or suppression files.

The JSON policy rejects every HIGH/CRITICAL, including unfixed findings. Reports
and CycloneDX inventories are retained even on policy failure. Tool/DB failures
are failures, never an empty successful report. Inputs are fixed CI paths.
"""

import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "test-results/images"


def run(*args):
    return subprocess.run(args, cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE).stdout


def assess(report, image_id):
    """Fail closed if the scanner did not analyze the expected Linux image."""
    if report.get("ArtifactType") != "container_image" or report.get("Metadata", {}).get("ImageID") != image_id:
        raise ValueError("Scanner image identity mismatch")
    metadata = report["Metadata"]
    if not metadata.get("OS", {}).get("Family") or metadata["OS"].get("EOSL"):
        raise ValueError("Unknown or end-of-life image OS")
    results = report.get("Results", [])
    if not any(r.get("Class") == "os-pkgs" and r.get("Packages") for r in results):
        raise ValueError("Missing OS package inventory")
    counts = {level: 0 for level in ("UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL")}
    for result in results:
        for finding in result.get("Vulnerabilities") or []:
            level = finding.get("Severity")
            if level not in counts:
                raise ValueError("Malformed vulnerability severity")
            counts[level] += 1
    return counts


def assess_runtime_inventory(report, name):
    """Runtime packaging regression, independent of vulnerability suppressions.

    Keep installer tooling out and verify the exact patched APKs actually landed
    in the final filesystem. This does not replace the full OS/library scan or
    change the project-wide severity/owner-review policy.
    """
    packages = [package for result in report.get("Results", []) for package in result.get("Packages", [])]
    expected = {"zlib": "1.3.2-r1", "musl": "1.2.6-r3", "musl-utils": "1.2.6-r3"}
    if name == "api":
        if any(package.get("Name") == "pip" for package in packages):
            raise ValueError("Runtime API image contains the removed installer")
    elif name == "web":
        expected["libxpm"] = "3.5.20-r0"
    else:
        raise ValueError("Unknown runtime image")
    os_packages = [
        package
        for result in report.get("Results", [])
        if result.get("Class") == "os-pkgs"
        for package in result.get("Packages", [])
    ]
    for package_name, version in expected.items():
        installed = [package.get("Version") for package in os_packages if package.get("Name") == package_name]
        if installed != [version]:
            raise ValueError("Runtime patched package missing/mismatched: " + package_name)


def main():
    smoke = json.loads((ROOT / "test-results/image-smoke.json").read_text())
    source = run("git", "rev-parse", "HEAD").strip()
    assert smoke["status"] == "passed" and smoke["sourceSha"] == source
    assert len(smoke["imageIds"]) == 2 and len(set(smoke["imageIds"])) == 2
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = {
        "sourceSha": source,
        "scanner": {},
        "policy": "all HIGH/CRITICAL block, including unfixed; no ignore file",
        "images": [],
        "published": False,
        "deployed": False,
    }
    for name, image_id in zip(("api", "web"), smoke["imageIds"], strict=True):
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", image_id)
        info = json.loads(run("docker", "image", "inspect", image_id))[0]
        assert info["Config"]["Labels"]["org.opencontainers.image.revision"] == source
        metadata = json.loads((OUT / f"{name}-build.json").read_text())
        assert metadata["containerimage.config.digest"] == image_id
        assert metadata.get("buildx.build.provenance"), "Buildx provenance metadata missing"
        report_path = OUT / f"{name}-scan.json"
        # Scan the daemon ID, not a mutable tag or remote image with the same name.
        run(
            "trivy",
            "image",
            "--image-src",
            "docker",
            "--scanners",
            "vuln",
            "--pkg-types",
            "os,library",
            "--ignorefile",
            "",
            "--ignore-unfixed=false",
            "--list-all-pkgs=true",
            "--format",
            "json",
            "--output",
            str(report_path),
            image_id,
        )
        report = json.loads(report_path.read_text())
        counts = assess(report, image_id)
        run(
            "trivy",
            "convert",
            "--format",
            "cyclonedx",
            "--output",
            str(OUT / f"{name}-sbom.cdx.json"),
            str(report_path),
        )
        evidence["images"].append(
            {
                "name": name,
                "imageId": image_id,
                "counts": counts,
                "reportSha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
                "buildDigest": metadata["containerimage.digest"],
            }
        )
    # Preserve both scan reports and SBOMs before rejecting packaging drift.
    for name in ("api", "web"):
        assess_runtime_inventory(json.loads((OUT / f"{name}-scan.json").read_text()), name)
    evidence["scanner"] = json.loads(run("trivy", "--version", "--format", "json"))
    updated = datetime.fromisoformat(evidence["scanner"]["VulnerabilityDB"]["UpdatedAt"].replace("Z", "+00:00"))
    if not timedelta(0) <= datetime.now(UTC) - updated <= timedelta(hours=24):
        raise ValueError("Scanner database is stale or future-dated")
    evidence["scannedAt"] = datetime.now(UTC).isoformat()
    blocked = any(i["counts"]["HIGH"] or i["counts"]["CRITICAL"] for i in evidence["images"])
    evidence["status"] = "blocked" if blocked else "passed"
    (OUT / "security-summary.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence))
    if blocked:
        raise SystemExit("Container security policy blocked: HIGH/CRITICAL findings; inspect both reports")


if __name__ == "__main__":
    main()
