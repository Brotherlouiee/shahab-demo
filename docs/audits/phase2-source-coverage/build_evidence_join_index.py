#!/usr/bin/env python3
"""Build a compact reusable join view from pinned Graphify and audit ledgers."""
import json
import hashlib
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from build_and_validate import read_csv

ROOT = Path(__file__).resolve().parents[3]
COVERAGE = ROOT / "docs/audits/phase2-source-coverage"
GRAPH_PATH = ROOT / "knowledge-graph/phase2-reference-docs/semantic/graph.json"
GRAPH_COMMIT = "17622bf4dd56108bee10d880a9dc5eb9617482fd"


# Required join columns. Historical heading labels are optional because
# source-inventory's canonical schema has neither title nor heading_text.
REQUIRED_COLUMNS = {
    "source-inventory.csv": {"source_unit_id"},
    "atomic-obligations.csv": {
        "candidate_id", "document", "source_unit_id", "start_line", "end_line",
        "parent_heading_id", "source_excerpt",
    },
    "execution-trace.csv": {
        "candidate_id", "graph_node_ids", "owner_package_candidates",
        "requirement_candidates", "task_subtask_candidates", "ac_test_candidates",
    },
    "semantic-review-dispositions.csv": {
        "candidate_id", "review_date", "semantic_disposition", "normative_status", "coverage_status",
    },
    "atomic-obligation-dispositions.csv": {
        "atomic_obligation_id", "candidate_id", "normative_status", "coverage_status",
        "normalized_obligation", "related_packages", "requirement_ids", "task_ids",
        "ac_test_ids", "decision_reference", "source_evidence", "plan_evidence",
        "mapping_status", "review_rationale",
    },
    "package-semantic-evidence.csv": {"package_id"},
}


def read_join_rows(name):
    path = COVERAGE / name
    fields, rows = read_csv(path)
    missing = REQUIRED_COLUMNS[name] - set(fields)
    duplicates = [field for field, count in Counter(fields).items() if count > 1]
    if missing:
        raise ValueError(f"{path}: missing required columns: {', '.join(sorted(missing))}")
    if duplicates:
        raise ValueError(f"{path}: duplicate columns: {', '.join(duplicates)}")
    return rows


def unique_ids(rows, field, name):
    counts = Counter(row[field] for row in rows)
    if any(not key.strip() for key in counts):
        raise ValueError(f"{name}: blank {field}")
    for key, count in counts.items():
        if count > 1:
            raise ValueError(f"{name}: duplicate {field} {key}")
    return counts.keys()


def build():
    rows = {name: read_join_rows(name) for name in REQUIRED_COLUMNS}
    candidates = rows["atomic-obligations.csv"]
    atoms = rows["atomic-obligation-dispositions.csv"]
    candidate_ids = unique_ids(candidates, "candidate_id", "atomic-obligations.csv")
    unique_ids(atoms, "atomic_obligation_id", "atomic-obligation-dispositions.csv")
    for atom in atoms:
        if atom["candidate_id"] not in candidate_ids:
            raise ValueError(
                "atomic-obligation-dispositions.csv: "
                f"{atom['atomic_obligation_id']} references unknown candidate_id {atom['candidate_id']}"
            )
    if GRAPH_PATH.exists():
        graph_bytes = GRAPH_PATH.read_bytes()
    else:
        graph_bytes = subprocess.run(
            ["git", "show", f"{GRAPH_COMMIT}:knowledge-graph/phase2-reference-docs/semantic/graph.json"],
            cwd=ROOT, check=True, capture_output=True,
        ).stdout
    if hashlib.sha256(graph_bytes).hexdigest() != "f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93":
        raise SystemExit("Pinned Graphify graph SHA-256 mismatch")
    graph = json.loads(graph_bytes.decode("utf-8"))
    nodes = {node["id"]: node for node in graph["nodes"]}
    adjacency = defaultdict(list)
    for edge in graph["links"]:
        adjacency[edge["source"]].append(edge)
        adjacency[edge["target"]].append(edge)

    inventory = rows["source-inventory.csv"]
    trace = {row["candidate_id"]: row for row in rows["execution-trace.csv"]}
    reviews = {row["candidate_id"]: row for row in rows["semantic-review-dispositions.csv"]}
    atoms_by_candidate = defaultdict(list)
    for atom in atoms:
        atoms_by_candidate[atom["candidate_id"]].append(atom)
    package_evidence = rows["package-semantic-evidence.csv"]
    locators_by_package = Counter(row["package_id"] for row in package_evidence)
    inventory_by_id = {row["source_unit_id"]: row for row in inventory}

    items = []
    for candidate in candidates:
        cid = candidate["candidate_id"]
        mapped = trace.get(cid, {})
        refs = [x for x in mapped.get("graph_node_ids", "").split(";") if x]
        neighboring = {}
        for node_id in refs:
            for edge in adjacency.get(node_id, []):
                other = edge["target"] if edge["source"] == node_id else edge["source"]
                key = (other, edge["relation"], edge["confidence"])
                neighboring[key] = edge
        parent = inventory_by_id.get(candidate.get("parent_heading_id", ""), {})
        items.append({
            "candidate_id": cid,
            "source_document": candidate["document"],
            "source_unit_id": candidate["source_unit_id"],
            "source_lines": f'{candidate["start_line"]}-{candidate["end_line"]}',
            "parent_heading_id": candidate.get("parent_heading_id", ""),
            "section_heading": parent.get("title", parent.get("heading_text", "")),
            "source_excerpt": candidate.get("source_excerpt", ""),
            "graph_nodes": refs,
            "graph_neighbors": [
                {"node_id": edge["target"] if edge["source"] in refs else edge["source"],
                 "relation": edge["relation"], "confidence": edge["confidence"]}
                for edge in sorted(neighboring.values(), key=lambda e: (-e.get("weight", 0), e["relation"]))
            ][:12],
            "review_status": (
                "SEMANTICALLY_REVIEWED"
                if reviews.get(cid, {}).get("review_date") and reviews.get(cid, {}).get("semantic_disposition")
                else reviews.get(cid, {}).get("review_status", "PENDING")
            ),
            "normative_status": reviews.get(cid, {}).get("normative_status", "NEEDS_REVIEW"),
            "coverage_status": reviews.get(cid, {}).get("coverage_status", "PENDING_REVIEW"),
            "atomic_obligation_ids": [a["atomic_obligation_id"] for a in atoms_by_candidate.get(cid, [])],
            "atomic_obligations": [
                {
                    "atomic_obligation_id": atom["atomic_obligation_id"],
                    "normative_status": atom["normative_status"],
                    "coverage_status": atom["coverage_status"],
                    "normalized_obligation": atom["normalized_obligation"],
                    "related_packages": atom["related_packages"],
                    "requirement_ids": atom["requirement_ids"],
                    "task_ids": atom["task_ids"],
                    "ac_test_ids": atom["ac_test_ids"],
                    "decision_reference": atom["decision_reference"],
                    "source_evidence": atom["source_evidence"],
                    "plan_evidence": atom["plan_evidence"],
                    "mapping_status": atom["mapping_status"],
                    "review_rationale": atom["review_rationale"],
                }
                for atom in atoms_by_candidate.get(cid, [])
            ],
            "packages": mapped.get("owner_package_candidates", "").split(";") if mapped.get("owner_package_candidates") else [],
            "requirements": mapped.get("requirement_candidates", "").split(";") if mapped.get("requirement_candidates") else [],
            "tasks": mapped.get("task_subtask_candidates", "").split(";") if mapped.get("task_subtask_candidates") else [],
            "ac_test": mapped.get("ac_test_candidates", "").split(";") if mapped.get("ac_test_candidates") else [],
        })

    bundle = {
        "schema_version": 1,
        "purpose": "Reusable evidence join over the pinned document graph and existing source/plan/audit ledgers; graph relations are retrieval evidence, not proof of semantic coverage.",
        "graph": {
            "path": "knowledge-graph/phase2-reference-docs/semantic/graph.json",
            "commit": GRAPH_COMMIT,
            "built_at_commit": graph.get("built_at_commit"),
            "sha256": hashlib.sha256(graph_bytes).hexdigest(),
            "nodes": len(nodes),
            "edges": len(graph["links"]),
            "edge_confidence_counts": dict(Counter(edge.get("confidence", "UNKNOWN") for edge in graph["links"])),
        },
        "totals": {
            "source_units": len(inventory),
            "candidates": len(candidates),
            "atomic_obligations": len(atoms),
            "candidate_review_status_counts": dict(Counter(item["review_status"] for item in items)),
            "atomic_coverage_status_counts": dict(Counter(atom["coverage_status"] for atom in atoms)),
            "packages": len(locators_by_package),
            "package_evidence_locators": len(package_evidence),
            "package_evidence_locators_by_package": dict(sorted(locators_by_package.items())),
        },
        "candidate_index": items,
    }
    return bundle


def main():
    bundle = build()
    (COVERAGE / "evidence-join-index.json").write_text(
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(bundle["totals"], ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        sys.exit(f"FAIL: {exc}")
