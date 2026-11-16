#!/usr/bin/env python3
"""Fail-closed structural and trace audit for independent Phase 2 rebuild.

Passing this script NEVER means semantic coverage is complete. Use
--strict-semantic only for the final acceptance gate. Run from checkout:
    python scripts/ci/phase2_rebuild_validate.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

BASELINE = {
    "B": ("docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md",
          "9681c2bf6c3149317c3788516748084cfb6eac7c", 1842),
    "W": ("docs/SHAHAB_DIGITAL_WALLET.md",
          "1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a", 964),
}
REGISTRY = "docs/SHAHAB_PHASE_2_REBUILD_LINE_REGISTER.jsonl"
ATOMS = "docs/SHAHAB_PHASE_2_REBUILD_ATOMIC_REQUIREMENTS.jsonl"
PLAN = "docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN_REBUILD.md"
ALLOWED_REVIEW = {
    "NOT_EXAMINED", "STRUCTURE_CHECKED", "ROLE_CLASSIFIED_NO_ATOM",
    "PARTIAL_ATOMIC_EXTRACTION", "VERIFIED",
}


def read_jsonl(path: Path) -> list[dict]:
    data = []
    for no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            data.append(json.loads(raw))
        except ValueError as exc:
            raise ValueError(f"{path}:{no}: malformed JSON") from exc
    return data


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def verify(repo: Path, strict: bool) -> dict:
    errors: list[str] = []
    sources: dict[str, list[str]] = {}
    expected_lines: set[str] = set()
    for source_id, (path, sha, count) in BASELINE.items():
        data = (repo / path).read_bytes()
        if git_blob_sha(data) != sha:
            fail(errors, f"Source changed: {source_id}")
        lines = data.decode("utf-8").split("\n")
        sources[source_id] = lines
        valid = {f"{source_id}:{i}" for i, x in enumerate(lines, 1) if x.strip()}
        if len(valid) != count:
            fail(errors, f"Line count changed for {source_id}: {len(valid)}")
        expected_lines.update(valid)

    registry = read_jsonl(repo / REGISTRY)
    seen: set[str] = set()
    counts = Counter()
    for row in registry:
        ref = row.get("ref")
        if ref in seen:
            fail(errors, f"Duplicate line ref {ref}")
        seen.add(ref)
        if ref not in expected_lines:
            fail(errors, f"Bad or empty ref {ref}")
        state = row.get("review_status")
        counts[state] += 1
        if state not in ALLOWED_REVIEW:
            fail(errors, f"Invalid review status {ref}: {state}")
        if state == "VERIFIED" and not row.get("review_evidence"):
            fail(errors, f"False VERIFIED without evidence {ref}")
    if seen != expected_lines:
        fail(errors, f"Registry missing {len(expected_lines-seen)}, extra {len(seen-expected_lines)}")
    if len(registry) != 2806:
        fail(errors, f"Registry row count {len(registry)} != 2806")

    atom_rows = read_jsonl(repo / ATOMS)
    plan = (repo / PLAN).read_text(encoding="utf-8")
    if not plan.endswith("\n") or plan.endswith("\n\n"):
        fail(errors, "Plan must end with exactly one newline")
    if re.search(r"\bundefined\b", plan):
        fail(errors, "Undefined text in plan")
    atom_ids: set[str] = set()
    tasks: set[str] = set()
    for row in atom_rows:
        identifier = row["id"]
        if identifier in atom_ids:
            fail(errors, f"Duplicate atom {identifier}")
        atom_ids.add(identifier)
        match = re.fullmatch(r"([BW]):(\d+)", row["source"])
        if not match:
            fail(errors, f"Bad source ref {identifier}")
            continue
        source, lineno = match.group(1), int(match.group(2))
        if row["quote"] not in sources[source][lineno - 1]:
            fail(errors, f"Atom quote not exact: {identifier}")
        task = row["task_id"]
        tasks.add(task)
        if not re.search(r"^\| " + re.escape(task) + r" \|", plan, flags=re.M):
            fail(errors, f"Task missing in plan: {task}")
        if not re.search(r"^\| " + re.escape(identifier) + r" \|", plan, flags=re.M):
            fail(errors, f"Atom missing in plan: {identifier}")
        if not row.get("acceptance") or not row.get("rejects") or not row.get("test_id"):
            fail(errors, f"Unfalsifiable requirement: {identifier}")
        if row.get("test_status") == "PASSED" and not row.get("execution_evidence"):
            fail(errors, f"Test falsely marked PASSED: {identifier}")

    fenced = False
    table_columns: int | None = None
    for n, line in enumerate(plan.split("\n"), 1):
        if line.startswith(chr(96)*3):
            fenced = not fenced
            table_columns = None
            continue
        if fenced:
            continue
        if line.startswith("|"):
            column_count = len(re.split(r"(?<!\\)\|", line)) - 2
            if table_columns is not None and column_count != table_columns:
                fail(errors, f"Markdown table column mismatch at {PLAN}:{n}")
            table_columns = column_count
        else:
            table_columns = None
    if fenced:
        fail(errors, "Unclosed Markdown code fence")

    semantic_complete = (all(x.get("review_status") == "VERIFIED" for x in registry)
                         and all(x.get("coverage") == "COVERED" for x in atom_rows)
                         and all(x.get("test_status") == "PASSED" for x in atom_rows))
    if strict and not semantic_complete:
        fail(errors, "G8 semantic/implementation gate INCOMPLETE")
    result = {
        "status": "FAIL" if errors else "STRUCTURAL_PASS",
        "semantic_complete": semantic_complete,
        "source_lines": len(registry),
        "atoms": len(atom_rows),
        "tasks": len(tasks),
        "review_status": dict(counts),
        "errors": errors,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--strict-semantic", action="store_true")
    args = parser.parse_args()
    result = verify(args.repo, args.strict_semantic)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
