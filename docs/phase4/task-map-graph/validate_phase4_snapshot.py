#!/usr/bin/env python3
"""Fail-closed validation of the certified Phase 4 Git snapshot.

This verifies file identity and repository provenance. It is not a semantic
graph validator and never invokes a builder or modifies project artifacts.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

MANIFEST_RELATIVE = "docs/phase4/task-map-graph/phase4-certified-snapshot.json"
REPOSITORY = "Brotherlouiee/shahab-demo"
APPROVED_SOURCE_COMMIT = "8ce742b640bbcbb87be5fc29f3a5a28d92593dec"
APPROVED_SNAPSHOT_ID = "phase4-45ed4ec10d34216cf935"
REQUIRED_GROUPS = ("primary_inputs", "reference_inputs")
OPTIONAL_GROUPS = ("optional_human_review_artifacts", "audit_evidence_only")
PRIMARY_PATHS = {
    "docs/phase4/task-map-graph/task-map-graph.json",
    "docs/phase4/task-map-graph/task-map-mapping.json",
}
REFERENCE_PATHS = {
    "docs/phase4/task-map-graph/current-project-code-graph.json",
    "docs/phase4/task-map-graph/new-project-task-graph.json",
    "knowledge-graph/phase2-reference-docs/semantic/graph.json",
    "docs/audits/phase2-source-coverage/evidence-join-index.json",
    "docs/audits/phase2-source-coverage/source-inventory.csv",
    "docs/audits/phase2-source-coverage/atomic-obligations.csv",
    "docs/audits/phase2-source-coverage/execution-trace.csv",
    "docs/audits/phase2-source-coverage/semantic-review-dispositions.csv",
    "docs/audits/phase2-source-coverage/atomic-obligation-dispositions.csv",
    "docs/audits/phase2-source-coverage/package-semantic-evidence.csv",
    "docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md",
    "docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md",
    "docs/SHAHAB_DIGITAL_WALLET.md",
    "docs/TASK_EXECUTION_PROTOCOL.md",
    "docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md",
}
REQUIRED_PATHS = PRIMARY_PATHS | REFERENCE_PATHS
IMMUTABLE_SHA256 = {
    "knowledge-graph/phase2-reference-docs/semantic/graph.json": "f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93",
    "docs/phase4/task-map-graph/current-project-code-graph.json": "0a496833d1a58a6d07e58f3d5d2b59f2c0306a924d8573a687fc4067c549c982",
    "docs/phase4/task-map-graph/new-project-task-graph.json": "deb940949583007628dccb89de538c8f3b278aef1c6f99d1386f613f107fa0f7",
}


class SnapshotValidationError(ValueError):
    """Raised when a snapshot cannot be safely consumed."""


def git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.run(
            ["git", *args], cwd=root, check=True, capture_output=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SnapshotValidationError(f"git {' '.join(args)} failed: {exc}") from exc


def safe_relative_path(value: Any, root: Path) -> tuple[str, Path]:
    if not isinstance(value, str) or not value:
        raise SnapshotValidationError("artifact path must be a non-empty string")
    posix = PurePosixPath(value)
    if posix.is_absolute() or ".." in posix.parts or "\\" in value:
        raise SnapshotValidationError(f"artifact path escapes repository: {value!r}")
    target = root.joinpath(*posix.parts)
    resolved_root = root.resolve()
    resolved_target = target.resolve(strict=False)
    if not resolved_target.is_relative_to(resolved_root):
        raise SnapshotValidationError(f"artifact path escapes repository: {value}")
    current = root
    for part in posix.parts:
        current = current / part
        if current.is_symlink():
            raise SnapshotValidationError(f"artifact path traverses a symbolic link: {value}")
    return posix.as_posix(), target


def _read_committed_blob(root: Path, commit: str, relative: str) -> tuple[bytes, str]:
    entry = git(root, "ls-tree", commit, "--", relative).decode("utf-8").strip()
    if not entry:
        raise SnapshotValidationError(f"{relative}: absent from certified commit {commit}")
    try:
        mode, kind, blob, _path = entry.split("\t", 1)[0].split() + [entry.split("\t", 1)[1]]
    except (ValueError, IndexError) as exc:
        raise SnapshotValidationError(f"{relative}: malformed Git tree entry") from exc
    if kind != "blob" or mode not in {"100644", "100755"}:
        raise SnapshotValidationError(f"{relative}: expected regular Git blob, found {mode} {kind}")
    contents = git(root, "cat-file", "blob", f"{commit}:{relative}")
    return contents, blob


def artifact_records(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for group in (*REQUIRED_GROUPS, *OPTIONAL_GROUPS):
        items = manifest.get(group)
        if not isinstance(items, list):
            raise SnapshotValidationError(f"manifest.{group} must be a list")
        records.extend(items)
    return records


def validate(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    try:
        manifest_relative = manifest_path.resolve().relative_to(root).as_posix()
    except ValueError as exc:
        raise SnapshotValidationError("manifest must be inside the repository") from exc
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SnapshotValidationError(f"manifest unreadable: {manifest_path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise SnapshotValidationError("manifest root must be an object")
    manifest_in_head, _ = _read_committed_blob(root, "HEAD", manifest_relative)
    try:
        manifest_working_bytes = manifest_path.read_bytes()
    except OSError as exc:
        raise SnapshotValidationError(f"manifest became unavailable during validation: {exc}") from exc
    if manifest_in_head != manifest_working_bytes:
        raise SnapshotValidationError("manifest working file differs from current Git HEAD")
    if manifest.get("manifest_schema_version") != "1.0":
        raise SnapshotValidationError("unsupported manifest_schema_version")
    if manifest.get("repository") != REPOSITORY:
        raise SnapshotValidationError("manifest repository does not match this validator")
    if manifest.get("source_pr") != 257:
        raise SnapshotValidationError("manifest source_pr is not the approved Phase 4 handoff PR")
    try:
        remote = git(root, "remote", "get-url", "origin").decode().strip().lower()
    except SnapshotValidationError as exc:
        raise SnapshotValidationError("repository origin is missing or unreadable") from exc
    if remote not in {"https://github.com/brotherlouiee/shahab-demo.git", "https://github.com/brotherlouiee/shahab-demo", "git@github.com:brotherlouiee/shahab-demo.git"}:
        raise SnapshotValidationError("Git origin does not identify the approved repository")
    commit = manifest.get("certified_source_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise SnapshotValidationError("certified_source_commit must be a full Git SHA")
    if commit != APPROVED_SOURCE_COMMIT:
        raise SnapshotValidationError("certified_source_commit is not the project-approved snapshot source")
    if manifest.get("snapshot_id") != APPROVED_SNAPSHOT_ID:
        raise SnapshotValidationError("snapshot_id is not the approved deterministic snapshot ID")
    if manifest.get("certification_status") != "TECHNICALLY_VALID_FOR_PHASE5; FORMAL_PHASE4_ACCEPTANCE_CONDITIONAL":
        raise SnapshotValidationError("manifest certification_status is not the approved technical-only status")
    if manifest.get("formal_phase4_acceptance") != "CONDITIONAL":
        raise SnapshotValidationError("manifest must preserve conditional formal acceptance")
    resolved = git(root, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    if resolved != commit:
        raise SnapshotValidationError("certified_source_commit did not resolve exactly")
    head = git(root, "rev-parse", "--verify", "HEAD").decode().strip()
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=root).returncode != 0:
        raise SnapshotValidationError("current HEAD does not contain the certified source commit")

    records = artifact_records(manifest)
    expected_group_roles = {
        "primary_inputs": "REQUIRED_PRIMARY_INPUT",
        "reference_inputs": "REQUIRED_REFERENCE_INPUT",
        "optional_human_review_artifacts": "OPTIONAL_HUMAN_REVIEW",
        "audit_evidence_only": "AUDIT_EVIDENCE_ONLY",
    }
    for group, role in expected_group_roles.items():
        for item in manifest[group]:
            if item.get("role") != role:
                raise SnapshotValidationError(f"{item.get('path')}: role does not match manifest.{group}")
    by_path: dict[str, dict[str, Any]] = {}
    committed_files: dict[str, bytes] = {}
    for record in records:
        if not isinstance(record, dict):
            raise SnapshotValidationError("artifact entries must be objects")
        relative, _ = safe_relative_path(record.get("path"), root)
        if relative in by_path:
            raise SnapshotValidationError(f"duplicate or ambiguous artifact path: {relative}")
        by_path[relative] = record
        digest = record.get("sha256")
        size = record.get("size_bytes")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise SnapshotValidationError(f"{relative}: invalid SHA-256 in manifest")
        if not isinstance(size, int) or size < 0:
            raise SnapshotValidationError(f"{relative}: invalid size_bytes in manifest")
        if not isinstance(record.get("role"), str) or not record["role"]:
            raise SnapshotValidationError(f"{relative}: missing artifact role")
        committed, blob_sha = _read_committed_blob(root, commit, relative)
        committed_hash = hashlib.sha256(committed).hexdigest()
        if committed_hash != digest or len(committed) != size:
            raise SnapshotValidationError(f"{relative}: certified commit does not match manifest hash/size")
        if record.get("git_blob_sha") and record["git_blob_sha"] != blob_sha:
            raise SnapshotValidationError(f"{relative}: Git blob SHA mismatch")
        _, working_path = safe_relative_path(relative, root)
        if working_path.is_symlink():
            raise SnapshotValidationError(f"{relative}: symbolic links are not accepted as snapshot files")
        try:
            working = working_path.read_bytes()
        except OSError as exc:
            raise SnapshotValidationError(f"{relative}: required snapshot file is unavailable: {exc}") from exc
        if working != committed:
            raise SnapshotValidationError(f"{relative}: working file differs from certified commit")
        committed_files[relative] = committed

    missing = REQUIRED_PATHS - set(by_path)
    if missing:
        raise SnapshotValidationError("manifest missing required artifacts: " + ", ".join(sorted(missing)))
    if {r["path"] for r in manifest["primary_inputs"]} != PRIMARY_PATHS:
        raise SnapshotValidationError("primary input set does not match the approved minimum contract")
    if not REFERENCE_PATHS.issubset({r["path"] for r in manifest["reference_inputs"]}):
        raise SnapshotValidationError("reference input set does not match the approved minimum contract")
    for group in REQUIRED_GROUPS:
        for item in manifest[group]:
            if item.get("required_for_phase5") is not True:
                raise SnapshotValidationError(f"{item['path']}: required input marked optional")
    for group in OPTIONAL_GROUPS:
        for item in manifest[group]:
            if item.get("required_for_phase5") is not False:
                raise SnapshotValidationError(f"{item['path']}: optional/audit artifact marked required")
    hash_map = manifest.get("artifact_hashes")
    size_map = manifest.get("artifact_sizes")
    role_map = manifest.get("artifact_roles")
    for name, value in (("artifact_hashes", hash_map), ("artifact_sizes", size_map), ("artifact_roles", role_map)):
        if not isinstance(value, dict):
            raise SnapshotValidationError(f"manifest.{name} must be an object")
        if set(value) != set(by_path):
            raise SnapshotValidationError(f"manifest.{name} path set does not match artifact records")
    for path, item in by_path.items():
        if hash_map.get(path) != item["sha256"] or size_map.get(path) != item["size_bytes"] or role_map.get(path) != item["role"]:
            raise SnapshotValidationError(f"{path}: artifact summary maps disagree with records")
    for path, expected in IMMUTABLE_SHA256.items():
        if hashlib.sha256(committed_files[path]).hexdigest() != expected:
            raise SnapshotValidationError(f"{path}: immutable graph SHA-256 differs from approved value")

    try:
        graph = json.loads(committed_files["docs/phase4/task-map-graph/task-map-graph.json"])
        mapping = json.loads(committed_files["docs/phase4/task-map-graph/task-map-mapping.json"])
        task_graph = json.loads(committed_files["docs/phase4/task-map-graph/new-project-task-graph.json"])
        code_graph = json.loads(committed_files["docs/phase4/task-map-graph/current-project-code-graph.json"])
        evidence = json.loads(committed_files["docs/audits/phase2-source-coverage/evidence-join-index.json"])
    except (KeyError, json.JSONDecodeError) as exc:
        raise SnapshotValidationError(f"required JSON artifact is invalid: {exc}") from exc
    graph_validation = graph.get("validation", {})
    validation_flags = {"unique_node_ids", "all_edge_endpoints_valid", "all_task_graph_nodes_preserved",
                        "all_code_graph_nodes_preserved", "all_source_edges_preserved",
                        "lossless_source_snapshots_present", "open_decisions_preserved",
                        "mapping_coverage", "immutable_graphs_unchanged",
                        "all_source_data_references_valid", "lossless_source_payload_round_trip"}
    if graph_validation.get("result") != "PASS" or not validation_flags.issubset(graph_validation) or any(
        value is not True for key, value in graph_validation.items()
        if key in validation_flags
    ):
        raise SnapshotValidationError("combined graph's recorded validation is not PASS")
    graph_stats = manifest.get("graph_statistics", {})
    actual_graph_stats = {
        "combined_graph_nodes": graph.get("counts", {}).get("node_total"),
        "combined_graph_edges": graph.get("counts", {}).get("edge_total"),
        "communities": graph.get("counts", {}).get("communities"),
        "current_code_nodes": graph.get("source_inputs", {}).get("current_project_code_graph", {}).get("node_count"),
        "task_graph_nodes": graph.get("source_inputs", {}).get("new_project_task_graph", {}).get("node_count"),
    }
    task_counts: dict[str, int] = {}
    for node in task_graph.get("nodes", []):
        kind = node.get("node_type")
        task_counts[kind] = task_counts.get(kind, 0) + 1
    actual_graph_stats.update({"packages": task_counts.get("PACKAGE", 0), "tasks": task_counts.get("TASK", 0),
                               "subtasks": task_counts.get("SUBTASK", 0)})
    if graph_stats != actual_graph_stats:
        raise SnapshotValidationError("graph_statistics do not reconcile with committed graph inputs")
    status_counts: dict[str, int] = {}
    for item in mapping.get("mappings", []):
        status = item.get("mapping_status")
        status_counts[status] = status_counts.get(status, 0) + 1
    mapping_stats = manifest.get("mapping_statistics", {})
    actual_mapping_stats = {"records": len(mapping.get("mappings", [])), **status_counts,
                            "relation_overlay": len(mapping.get("stage4_relation_overlay", {}).get("relations", []))}
    if mapping_stats != actual_mapping_stats:
        raise SnapshotValidationError("mapping_statistics do not reconcile with committed mapping")
    decisions = mapping.get("open_decision_references", [])
    if len(decisions) != 134 or any(
        d.get("decision_status", d.get("confidence")) != "OPEN" or d.get("mapping_status") != "BLOCKED"
        for d in decisions
    ):
        raise SnapshotValidationError("open decisions are not all preserved as OPEN/BLOCKED")
    decision_stats = manifest.get("decision_statistics", {})
    if decision_stats.get("open_decisions") != len(decisions) or decision_stats.get("blocked_mappings") != len(decisions):
        raise SnapshotValidationError("decision_statistics do not reconcile with committed mapping")
    if len(mapping.get("stage4_code_search_audit", {}).get("records", [])) != decision_stats.get("stage4_replay_records"):
        raise SnapshotValidationError("Stage 4 replay record count does not reconcile")
    coverage = evidence.get("totals", {})
    expected_coverage = {"candidates": coverage.get("candidates"),
                         "pending_candidates": coverage.get("candidate_review_status_counts", {}).get("PENDING", 0),
                         "atomic_obligations": coverage.get("atomic_obligations"),
                         "covered": coverage.get("atomic_coverage_status_counts", {}).get("VERIFIED_COVERED", 0),
                         "partial": coverage.get("atomic_coverage_status_counts", {}).get("PARTIALLY_COVERED", 0),
                         "open_decision": coverage.get("atomic_coverage_status_counts", {}).get("OPEN_DECISION", 0),
                         "uncovered": coverage.get("atomic_coverage_status_counts", {}).get("VERIFIED_UNCOVERED", 0)}
    if manifest.get("source_coverage_statistics") != expected_coverage:
        raise SnapshotValidationError("source_coverage_statistics do not reconcile with committed Evidence Join Index")
    for payload_name, path in (("current_project_code_graph", "docs/phase4/task-map-graph/current-project-code-graph.json"),
                               ("new_project_task_graph", "docs/phase4/task-map-graph/new-project-task-graph.json"),
                               ("task_map_mapping", "docs/phase4/task-map-graph/task-map-mapping.json")):
        try:
            payload = graph["source_payloads"][payload_name]
            raw = gzip.decompress(base64.b64decode(payload["data"], validate=True))
        except (KeyError, ValueError, OSError) as exc:
            raise SnapshotValidationError(f"combined graph source payload {payload_name} is invalid: {exc}") from exc
        if raw != committed_files[path] or hashlib.sha256(raw).hexdigest() != payload.get("sha256_uncompressed"):
            raise SnapshotValidationError(f"combined graph embedded snapshot does not match {path}")
    # Detect files changed while the manifest was being checked.
    for path in by_path:
        _, working_path = safe_relative_path(path, root)
        if working_path.read_bytes() != _read_committed_blob(root, commit, path)[0]:
            raise SnapshotValidationError(f"{path}: changed during snapshot validation")
    return {"result": "CERTIFIED_SNAPSHOT_VALID", "snapshot_id": manifest.get("snapshot_id"),
            "certified_source_commit": commit, "checked_artifacts": len(by_path), "head": head}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=MANIFEST_RELATIVE)
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[3]
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    try:
        result = validate(manifest_path, root)
    except SnapshotValidationError as exc:
        print(f"STOP_CONSUMPTION: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
