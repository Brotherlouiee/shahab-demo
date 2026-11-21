"""Classify a GitHub change so documentation-only PRs can skip heavy CI jobs."""

from __future__ import annotations

import os
import subprocess
from pathlib import PurePosixPath


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=False, text=True, capture_output=True)


def is_document(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith("docs/") or PurePosixPath(normalized).suffix.casefold() in {
        ".md",
        ".mdx",
        ".rst",
        ".adoc",
    }


def is_frontend(path: str) -> bool:
    p = path.replace("\\", "/")
    return (
        p.startswith(("src/", "frontend/", "public/", "assets/", "tests/e2e/", "tests/unit/"))
        or p in {"index.html", "package.json", "package-lock.json"}
        or p.startswith(("vite.config.", "playwright.", "tailwind.config.", "postcss.config."))
        or p.startswith("scripts/ci/verify_e2e_partition.")
    )


def main() -> int:
    base = os.environ.get("BASE_SHA", "").strip()
    head = os.environ.get("HEAD_SHA", "").strip()
    force_full = os.environ.get("FORCE_FULL", "").casefold() in {"1", "true", "yes"}

    paths: list[str]
    is_pull_request = os.environ.get("GITHUB_EVENT_NAME", "").casefold() == "pull_request"

    if force_full or not head or set(head) == {"0"}:
        paths = ["<full-run>"]
    else:
        if is_pull_request:
            # Long-lived PR event payloads can carry an old base.sha. Fetch the
            # current target branch instead; GitHub's PR merge commit includes
            # that target snapshot plus this PR's changes.
            base_ref = os.environ.get("GITHUB_BASE_REF", "").strip()
            if base_ref:
                base = f"refs/remotes/origin/{base_ref}"
                fetched = run(
                    "git",
                    "fetch",
                    "--no-tags",
                    "--depth=1",
                    "origin",
                    f"refs/heads/{base_ref}:{base}",
                )
            else:
                fetched = subprocess.CompletedProcess(
                    args=["git", "fetch"],
                    returncode=1,
                    stdout="",
                    stderr="GITHUB_BASE_REF is unavailable",
                )
        elif base:
            fetched = run("git", "fetch", "--no-tags", "--depth=1", "origin", base)
        else:
            fetched = subprocess.CompletedProcess(
                args=["git", "fetch"],
                returncode=1,
                stdout="",
                stderr="BASE_SHA is unavailable",
            )

        compare_ref = base if base else ""
        if fetched.returncode or not compare_ref:
            paths = ["<classification-failed>"]
        else:
            diff = run("git", "diff", "--name-only", "--no-renames", compare_ref, head)
            if diff.returncode:
                print("::warning::Could not classify changed files; running all relevant jobs.")
                paths = ["<classification-failed>"]
            else:
                paths = [line for line in diff.stdout.splitlines() if line]

    docs_only = bool(paths) and all(is_document(path) for path in paths)
    full_product = not docs_only
    frontend = full_product and (
        force_full or "<classification-failed>" in paths or any(is_frontend(path) for path in paths)
    )
    has_docs = any(is_document(path) for path in paths)

    outputs = {
        "docs_only": docs_only,
        "has_docs": has_docs,
        "run_quality": full_product,
        "run_security": full_product,
        "run_images": full_product,
        "run_us13": frontend,
    }
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        raise RuntimeError("GITHUB_OUTPUT is required")
    with open(output_file, "a", encoding="utf-8") as stream:
        for key, value in outputs.items():
            stream.write(f"{key}={'true' if value else 'false'}\n")

    print("Changed paths:")
    for path in paths:
        print(f"  {path}")
    print("CI scope:", ", ".join(f"{key}={str(value).lower()}" for key, value in outputs.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
