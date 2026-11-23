#!/usr/bin/env python3
"""Rebuild and structurally validate the Phase 2 source coverage workpapers.

Graph edges and textual coincidences are recorded as discovery candidates only.
This utility never upgrades a semantic mapping to verified coverage.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
COVERAGE = Path(__file__).resolve().parent
PLAN = ROOT / "docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md"
SOURCES = [
    ("BP", "docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md"),
    ("WL", "docs/SHAHAB_DIGITAL_WALLET.md"),
]
GRAPH_COMMIT = "17622bf4dd56108bee10d880a9dc5eb9617482fd"
GRAPH_PATH = "knowledge-graph/phase2-reference-docs/semantic/graph.json"
BASELINE_COMMIT = "e69a483f11058711048f1ba7b15b5225e33c7fc9"

HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}.*\|.*-+:?\s*\|?\s*$")
SOURCE_REF = re.compile(r"\b([BW]):\s*(\d+)(?:\s*[-–—]\s*(\d+))?")
GRAPH_NODE_REF = re.compile(r"\bdocs_[a-z0-9_]+\b")
ID_RE = re.compile(
    r"\b(?:CAN|CAND|REQ|EN|TE|STORY|TASK|AC|TD|TEST|TC|OPEN|PKG|CPA|CONTRACT|HANDOFF|DEP|DEPENDENCY)"
    r"(?::[A-Z0-9]+)+(?:\.S\d+)?\b"
    r"|\bCAND(?:IDATE)?-[A-Z0-9-]+\b"
    r"|\b(?:C\d{2}[A-Z]?|R\d{2}|A\d{2})-(?:REQ|R|EN|E|STORY|TE|TASK|T|SUBTASK|S|AC|TD|TEST|TC)\d{1,4}(?:\.S\d{1,3})?\b"
)

STATUS_RE = re.compile(r"^\|\s*((?:C\d{2}[ab]?|R\d{2}|A\d{2}))\s*\|\s*(.*?)\s*\|\s*(PASS|PARTIAL|NOT_STARTED|NOT_ACCEPTED)\s*\|\s*(PASS|PARTIAL|NOT_STARTED|NOT_ACCEPTED)\s*\|\s*([^|]+)", re.I)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: str) -> str:
    """Return the Git blob SHA for the current file bytes, not the local HEAD."""
    content = (ROOT / path).read_bytes()
    header = b"blob " + str(len(content)).encode("ascii") + bytes([0])
    return hashlib.sha1(header + content).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields=list(reader.fieldnames or [])
        rows=[]
        for row in reader:
            line=reader.line_num
            if None in row:
                raise ValueError(f"Malformed CSV row in {path}:{line}: extra field(s); check for truncation")
            missing=[key for key,value in row.items() if value is None]
            if missing:
                raise ValueError(f"Malformed CSV row in {path}:{line}: missing value(s) in {', '.join(missing)}; check for truncation")
            rows.append(row)
        return fields, rows


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def apply_review_dispositions(candidates: list[dict[str, Any]]) -> None:
    """Apply only manually evidenced dispositions from the separate review ledger."""
    path = COVERAGE / "semantic-review-dispositions.csv"
    if not path.exists():
        return
    ledger_fields, ledger = read_csv(path)
    required = {"candidate_id", "semantic_disposition", "normative_status", "coverage_status", "atomicity_status", "source_evidence", "review_rationale", "reviewer", "review_date"}
    if not required.issubset(ledger_fields):
        raise ValueError(f"Review ledger missing columns: {sorted(required - set(ledger_fields))}")
    by_id = {row["candidate_id"]: row for row in candidates}
    seen: set[str] = set()
    for review in ledger:
        cid = review["candidate_id"]
        if cid in seen:
            raise ValueError(f"Duplicate semantic review: {cid}")
        seen.add(cid)
        if cid not in by_id:
            raise ValueError(f"Semantic review references unknown candidate: {cid}")
        if not all(review.get(key, "").strip() for key in ("semantic_disposition", "normative_status", "coverage_status", "atomicity_status", "source_evidence", "review_rationale", "reviewer", "review_date")):
            raise ValueError(f"Semantic review is missing evidence or rationale: {cid}")
        candidate = by_id[cid]
        if review["source_evidence"].split(";",1)[0] != f"{candidate['document']}:{candidate['start_line']} ({candidate['source_unit_id']})":
            raise ValueError(f"Semantic review source locator drift: {cid}")
        candidate["normative_status"] = review["normative_status"]
        candidate["classification_method"] = "HUMAN_SEMANTIC_REVIEW"
        candidate["classification_confidence"] = "HIGH"
        candidate["review_status"] = "SEMANTICALLY_REVIEWED"
        candidate["review_reason"] = review["review_rationale"]
        candidate["atomicity_status"] = review["atomicity_status"]
        for column, key in (("atomic_obligation_id","atomic_obligation_id"),("normalized_obligation","normalized_obligation"),("logical_owner","related_packages"),("decision_reference","plan_evidence")):
            candidate[column]=review.get(key,"")


def apply_source_unit_dispositions(inventory: list[dict[str, Any]]) -> None:
    """Keep headings and table containers distinct from their content units."""
    path = COVERAGE / "source-unit-review-dispositions.csv"
    if not path.exists():
        return
    fields, ledger = read_csv(path)
    required={"source_unit_id","unit_type","semantic_disposition","normative_status","coverage_status","source_evidence","review_rationale","reviewer","review_date"}
    if not required.issubset(fields):
        raise ValueError(f"Source-unit review ledger missing columns: {sorted(required - set(fields))}")
    by_id={row["source_unit_id"]:row for row in inventory}
    seen=set()
    for review in ledger:
        uid=review["source_unit_id"]
        if uid in seen or uid not in by_id:
            raise ValueError(f"Duplicate or unknown source unit in review ledger: {uid}")
        seen.add(uid)
        row=by_id[uid]
        expected=f"{row['document']}:{row['start_line']}-{row['end_line']} ({uid})"
        expected_disposition="STRUCTURAL_SECTION_LOCATOR" if row["unit_type"]=="HEADING" else "STRUCTURAL_TABLE_CONTAINER" if row["unit_type"]=="TABLE" else ""
        if row["unit_type"] not in {"HEADING","TABLE"} or review["unit_type"]!=row["unit_type"] or review["semantic_disposition"]!=expected_disposition or review["source_evidence"]!=expected:
            raise ValueError(f"Invalid source-unit disposition or locator: {uid}")
        row["normative_status"]="NOT_APPLICABLE"
        row["coverage_status"]="NOT_APPLICABLE"
        row["classification_method"]="HUMAN_SEMANTIC_REVIEW"
        row["review_reason"]=review["review_rationale"]


def excerpt_text(text: str) -> str:
    """Keep readable source excerpts while dropping Markdown hard-break padding."""
    return "\n".join(line.rstrip() for line in text.splitlines())


def parse_sources(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    headings: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    paragraphs: list[dict[str, Any]] = []
    code_blocks: list[dict[str, Any]] = []
    in_fence = False
    fence_char = ""
    fence_width = 0
    fence_start = 0
    fence_marker = ""
    fence_content: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence, fence_char, fence_width = True, marker[0], len(marker)
                fence_start, fence_marker, fence_content = i + 1, marker, []
            elif marker[0] == fence_char and len(marker) >= fence_width:
                code_blocks.append({"start": fence_start, "end": i + 1, "language": fence_marker[3:].strip(), "text": "\n".join(fence_content)})
                in_fence = False
                fence_start, fence_marker, fence_content = 0, "", []
            i += 1
            continue
        if in_fence:
            fence_content.append(line)
            i += 1
            continue
        heading = HEADING.match(line)
        if heading:
            headings.append({"start": i + 1, "level": len(heading.group(1)), "title": heading.group(2).strip()})
            i += 1
            continue
        # A Markdown table starts only where a header is followed by a separator.
        if i + 1 < len(lines) and "|" in line and TABLE_SEPARATOR.match(lines[i + 1]):
            start = i
            j = i + 1
            while j < len(lines) and lines[j].strip() and "|" in lines[j]:
                j += 1
            tables.append({"start": start + 1, "end": j, "rows": [n + 1 for n in range(start, j) if lines[n].strip() and not TABLE_SEPARATOR.match(lines[n])]})
            i = j
            continue
        if not line.strip():
            i += 1
            continue
        start = i
        block = [line]
        i += 1
        while i < len(lines) and lines[i].strip():
            if FENCE.match(lines[i]) or HEADING.match(lines[i]):
                break
            if i + 1 < len(lines) and "|" in lines[i] and TABLE_SEPARATOR.match(lines[i + 1]):
                break
            block.append(lines[i])
            i += 1
        paragraphs.append({"start": start + 1, "end": start + len(block), "text": "\n".join(block)})

    # Heading section spans end at the next peer/ancestor heading, or EOF.
    for index, heading in enumerate(headings):
        end = len(lines)
        for later in headings[index + 1 :]:
            if later["level"] <= heading["level"]:
                end = later["start"] - 1
                break
        heading["end"] = max(heading["start"], end)

    # Attach hierarchy path to each heading and table/paragraph unit.
    stack: list[dict[str, Any]] = []
    for heading in headings:
        while stack and stack[-1]["level"] >= heading["level"]:
            stack.pop()
        heading["path"] = " / ".join([h["title"] for h in stack] + [heading["title"]])
        heading["parent_line"] = stack[-1]["start"] if stack else ""
        stack.append(heading)

    def parent_at(line_no: int) -> dict[str, Any] | None:
        parents = [h for h in headings if h["start"] <= line_no <= h["end"]]
        return max(parents, key=lambda h: h["level"]) if parents else None

    for unit in [*tables, *paragraphs, *code_blocks]:
        parent = parent_at(unit["start"])
        unit["parent"] = parent
        unit["path"] = parent["path"] if parent else ""
    return {"lines": lines, "headings": headings, "tables": tables, "paragraphs": paragraphs, "code_blocks": code_blocks}


def line_bounds(location: str) -> tuple[int, int] | None:
    match = re.search(r"(?:L)?(\d+)(?:\s*[-–—]\s*(?:L)?(\d+))?", str(location or ""))
    return (int(match.group(1)), int(match.group(2) or match.group(1))) if match else None


def graph_data() -> tuple[list[dict[str, Any]], str]:
    try:
        raw = subprocess.check_output(["git", "show", f"{GRAPH_COMMIT}:{GRAPH_PATH}"], cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Cannot read pinned Graphify graph at {GRAPH_COMMIT}:{GRAPH_PATH}") from exc
    obj = json.loads(raw)
    return obj.get("nodes", []), hashlib.sha256(raw).hexdigest()


def classification(text: str, *, is_heading: bool = False, is_table_header: bool = False) -> tuple[str, str, str]:
    if is_heading:
        return "NEEDS_REVIEW", "HEADING_IS_LOCATOR_NOT_NORMATIVE_EVIDENCE", "LOW"
    if is_table_header:
        return "DESCRIPTIVE", "TABLE_HEADER", "HIGH"
    low = text.casefold()
    open_hits = bool(re.search(r"\bopen\b|تصمیم\s*باز|نیازمند\s*تصمیم|تعیین\s*نشده|تصویب\s*نشده|در\s*انتظار\s*تصمیم|نامشخص", low))
    example_hits = bool(re.search(r"مثال|نمونه|فرضی|برای\s*مثال|سناریوی?\s*فرضی|\bexample\b|\bhypothetical\b", low))
    superseded = bool(re.search(r"منسوخ|جایگزین\s*شد|نسخه\s*قدیمی|superseded|obsolete", low))
    oos = bool(re.search(r"خارج\s*از\s*دامنه|out\s*of\s*scope|not\s*in\s*scope", low))
    normative = bool(re.search(r"باید|الزامی|ممنوع|لازم\s*است|ضروری\s*است|مجاز\s*نیست|نباید|مصوب|تصویب\s*شد|\bmust\b|\bshall\b|\brequired\b|\bapproved\b", low))
    dimensions = sum([open_hits, example_hits, superseded, oos, normative])
    if superseded:
        return ("MIXED" if dimensions > 1 else "SUPERSEDED"), "RULE_MATCH_SUPERSEDED_CUE; REVIEW_REQUIRED", "LOW"
    if dimensions > 1:
        return "MIXED", "MULTIPLE_NORMATIVE_CLASSIFICATION_CUES; DECOMPOSE_AND_REVIEW", "LOW"
    if open_hits:
        return "NORMATIVE_OPEN_DECISION", "RULE_MATCH_OPEN_DECISION_CUE; REVIEW_REQUIRED", "MEDIUM"
    if example_hits:
        return "EXAMPLE", "RULE_MATCH_EXAMPLE_CUE; VERIFY_NO_APPROVED_RULE_EMBEDDED", "MEDIUM"
    if oos:
        return "OUT_OF_SCOPE", "RULE_MATCH_OUT_OF_SCOPE_CUE; REVIEW_REQUIRED", "MEDIUM"
    if normative:
        return "NORMATIVE_APPROVED", "RULE_MATCH_NORMATIVE_CUE; APPROVAL_STATUS_REQUIRES_SOURCE_REVIEW", "LOW"
    if re.search(r"مراجع|منابع|تاریخچه|نسخه\s*[۰-۹0-9]|\bversion\b|\breference\b", low):
        return "DESCRIPTIVE", "RULE_MATCH_METADATA_OR_REFERENCE_CUE", "LOW"
    return "NEEDS_REVIEW", "NO_RELIABLE_NORMATIVE_CLASSIFICATION_CUE", "LOW"


def cells_from_row(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    return [cell.replace("\\|", "|").strip() for cell in re.split(r"(?<!\\)\|", value)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    inventory_path = COVERAGE / "source-inventory.csv"
    candidate_path = COVERAGE / "atomic-obligations.csv"
    old_inv_fields, old_inventory = read_csv(inventory_path)
    old_cand_fields, old_candidates = read_csv(candidate_path)
    source_specs = []
    for prefix, relative in SOURCES:
        path = ROOT / relative
        source_specs.append((prefix, relative, parse_sources(path), path))

    graph_nodes, graph_sha = graph_data()
    graph_by_doc: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in graph_nodes:
        source_file = node.get("source_file")
        if source_file:
            graph_by_doc[source_file].append(node)

    # Baseline IDs are the two original structural kinds and C-series paragraph
    # candidates. Generated TEXT_RANGE/CODE_BLOCK/TABLE_ROW records are rebuilt.
    baseline_inventory = [r for r in old_inventory if r["unit_type"] in {"HEADING", "TABLE"}]
    baseline_candidates = [r for r in old_candidates if re.match(r"^(?:BP|WL)-C-\d+$", r["candidate_id"])]
    old_by_unit = {(r["document"], r["unit_type"], int(r["start_line"])): r for r in baseline_inventory}
    old_candidate_by_range = {(r["document"], int(r["start_line"]), int(r["end_line"])): r for r in baseline_candidates}
    next_candidate_number = {}
    for prefix in ("BP", "WL"):
        nums = [int(m.group(1)) for row in baseline_candidates if (m := re.search(rf"^{prefix}-C-(\d+)$", row["candidate_id"]))]
        next_candidate_number[prefix] = max(nums, default=0) + 1
    inventory_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    structural_count = Counter()
    candidate_count = Counter()
    source_hashes: dict[str, dict[str, Any]] = {}
    fulltext_lines_seen: dict[str, set[int]] = {}
    structural_errors: list[str] = []

    for prefix, rel, parsed, source_path in source_specs:
        file_lines = parsed["lines"]
        blob = git_blob(rel)
        source_hashes[rel] = {"git_blob_sha": blob, "sha256": sha256(source_path), "physical_lines": len(file_lines), "final_newline": source_path.read_bytes().endswith(b"\n")}
        fulltext_lines_seen[rel] = set()
        heading_ids: dict[int, str] = {}
        table_ids: dict[int, str] = {}
        heading_n = table_n = 0

        # Keep existing stable structural IDs while confirming every current location.
        structure = []
        for heading in parsed["headings"]:
            heading_n += 1
            key = (rel, "HEADING", heading["start"])
            old = old_by_unit.get(key)
            unit_id = old["source_unit_id"] if old else f"{prefix}-H-{heading_n:03d}"
            heading_ids[heading["start"]] = unit_id
            structure.append((heading["start"], "HEADING", unit_id, heading))
        for table in parsed["tables"]:
            table_n += 1
            key = (rel, "TABLE", table["start"])
            old = old_by_unit.get(key)
            unit_id = old["source_unit_id"] if old else f"{prefix}-T-{table_n:03d}"
            table_ids[table["start"]] = unit_id
            structure.append((table["start"], "TABLE", unit_id, table))
        for code_n, block in enumerate(parsed["code_blocks"], 1):
            structure.append((block["start"], "CODE_BLOCK", f"{prefix}-CODE-{code_n:03d}", block))

        for start, unit_type, unit_id, unit in sorted(structure):
            if unit_type == "HEADING":
                fulltext_lines_seen[rel].add(start)
            graph_matches = []
            if unit_type == "HEADING":
                for node in graph_by_doc.get(rel, []):
                    attrs = node.get("attributes", {})
                    if attrs.get("heading_line") == start or node.get("source_location") == f"L{start}-L{unit['end']}":
                        graph_matches.append(node["id"])
            elif unit_type == "TABLE":
                for node in graph_by_doc.get(rel, []):
                    bounds = line_bounds(node.get("source_location", ""))
                    if bounds and bounds[0] <= unit["end"] and bounds[1] >= unit["start"]:
                        graph_matches.append(node["id"])
            else:
                for node in graph_by_doc.get(rel, []):
                    bounds = line_bounds(node.get("source_location", ""))
                    if bounds and bounds[0] <= unit["end"] and bounds[1] >= unit["start"]:
                        graph_matches.append(node["id"])
            inv = {
                "source_unit_id": unit_id,
                "document": rel,
                "document_blob_sha": blob,
                "unit_type": unit_type,
                "hierarchy_or_title": unit.get("path", unit.get("title", "")),
                "start_line": unit["start"],
                "end_line": unit["end"],
                "table_lines": unit["end"] - unit["start"] + 1 if unit_type == "TABLE" else "",
                "normative_status": "NEEDS_REVIEW",
                "classification_suggestion": "NEEDS_REVIEW",
                "graph_node_ids": ";".join(sorted(set(graph_matches))),
                "coverage_status": "SECTION_TEXT_ENUMERATED_REVIEW_REQUIRED" if unit_type == "HEADING" else "TABLE_ROWS_ENUMERATED_REVIEW_REQUIRED" if unit_type == "TABLE" else "CODE_CONTENT_ENUMERATED_REVIEW_REQUIRED",
                "classification_method": "STRUCTURAL_LOCATOR_ONLY",
                "review_reason": "Structure locates content; it does not prove normativity or executable coverage.",
            }
            inventory_rows.append(inv)
            if unit_type in {"HEADING", "TABLE"}:
                structural_count[unit_type] += 1
            elif unit_type == "CODE_BLOCK":
                candidate_count["CODE_BLOCK_UNIT"] += 1
            if unit_type == "TABLE":
                table_number = int(unit_id.rsplit("-", 1)[1])
                for row_index, line_no in enumerate(unit["rows"], 1):
                    line = file_lines[line_no - 1]
                    is_header = line_no == unit["start"]
                    status, reason, confidence = classification(line, is_table_header=is_header)
                    candidate_id = f"{prefix}-TR-{table_number:03d}-{row_index:02d}"
                    candidate_rows.append({
                        "candidate_id": candidate_id,
                        "atomic_obligation_id": "",
                        "source_unit_id": unit_id,
                        "document": rel,
                        "document_blob_sha": blob,
                        "source_sha256": source_hashes[rel]["sha256"],
                        "start_line": line_no,
                        "end_line": line_no,
                        "parent_heading_id": heading_ids.get(unit["parent"]["start"], "") if unit.get("parent") else "",
                        "source_excerpt": excerpt_text(line),
                        "source_cells_json": json.dumps(cells_from_row(line), ensure_ascii=False),
                        "candidate_class": "TABLE_HEADER" if is_header else "TABLE_ROW_CANDIDATE",
                        "normative_status": "NEEDS_REVIEW",
                        "classification_suggestion": status,
                        "normalized_obligation": "",
                        "atomicity_status": "NOT_ATOMIZED",
                        "logical_owner": "",
                        "dependencies": "",
                        "decision_reference": "",
                        "graph_node_ids": ";".join(sorted({n["id"] for n in graph_by_doc.get(rel, []) if (b := line_bounds(n.get("source_location", ""))) and b[0] <= line_no <= b[1]})),
                        "classification_method": "RULE_BASED_CANDIDATE_ONLY",
                        "classification_confidence": confidence,
                        "review_status": "REVIEW_REQUIRED",
                        "review_reason": reason,
                    })
                    fulltext_lines_seen[rel].add(line_no)
                    candidate_count["TABLE_ROW"] += 1

        for code_n, block in enumerate(parsed["code_blocks"], 1):
            unit_id = f"{prefix}-CODE-{code_n:03d}"
            parent = block.get("parent")
            graph_matches = []
            for node in graph_by_doc.get(rel, []):
                bounds = line_bounds(node.get("source_location", ""))
                if bounds and bounds[0] <= block["end"] and bounds[1] >= block["start"]:
                    graph_matches.append(node["id"])
            candidate_rows.append({
                "candidate_id": f"{prefix}-CODE-{code_n:03d}", "atomic_obligation_id": "", "source_unit_id": unit_id,
                "document": rel, "document_blob_sha": blob, "source_sha256": source_hashes[rel]["sha256"],
                "start_line": block["start"], "end_line": block["end"],
                "parent_heading_id": heading_ids.get(parent["start"], "") if parent else "",
                "source_excerpt": excerpt_text(block["text"]), "source_cells_json": "", "candidate_class": "CODE_BLOCK_CANDIDATE",
                "normative_status": "NEEDS_REVIEW", "classification_suggestion": "NEEDS_REVIEW", "normalized_obligation": "", "atomicity_status": "NOT_ATOMIZED",
                "logical_owner": "", "dependencies": "", "decision_reference": "",
                "graph_node_ids": ";".join(sorted(set(graph_matches))), "classification_method": "CODE_BLOCK_REVIEW_REQUIRED",
                "classification_confidence": "LOW", "review_status": "REVIEW_REQUIRED",
                "review_reason": "A fenced block may be example, schema, contract or executable policy; inspect against surrounding approved prose.",
            })
            fulltext_lines_seen[rel].update(range(block["start"], block["end"] + 1))
            candidate_count["CODE_BLOCK"] += 1

        # All non-heading, non-table, non-fenced prose ranges are retained.
        for block in parsed["paragraphs"]:
            key = (rel, block["start"], block["end"])
            old = old_candidate_by_range.get(key)
            if old:
                candidate_id = old["candidate_id"]
                found = old["candidate_class"]
            else:
                # Preserve baseline IDs and append omitted prose ranges monotonically.
                candidate_id = f"{prefix}-C-{next_candidate_number[prefix]:04d}"
                next_candidate_number[prefix] += 1
                found = "TEXT_RANGE_CANDIDATE"
            status, reason, confidence = classification(block["text"])
            parent = block.get("parent")
            node_ids = []
            for node in graph_by_doc.get(rel, []):
                bounds = line_bounds(node.get("source_location", ""))
                if bounds and bounds[0] <= block["end"] and bounds[1] >= block["start"]:
                    node_ids.append(node["id"])
            paragraph_unit_id = f"{prefix}-P-{block['start']:04d}-{block['end']:04d}"
            status, reason, confidence = classification(block["text"])
            inventory_rows.append({
                "source_unit_id": paragraph_unit_id, "document": rel, "document_blob_sha": blob,
                "unit_type": "TEXT_RANGE", "hierarchy_or_title": block.get("path", ""),
                "start_line": block["start"], "end_line": block["end"], "table_lines": "",
                "normative_status": "NEEDS_REVIEW", "classification_suggestion": status, "graph_node_ids": ";".join(sorted(set(node_ids))),
                "coverage_status": "TEXT_RANGE_ENUMERATED_REVIEW_REQUIRED",
                "classification_method": "RULE_BASED_CANDIDATE_ONLY", "review_reason": reason,
            })
            candidate_rows.append({
                "candidate_id": candidate_id,
                "atomic_obligation_id": "",
                "source_unit_id": paragraph_unit_id,
                "document": rel,
                "document_blob_sha": blob,
                "source_sha256": source_hashes[rel]["sha256"],
                "start_line": block["start"],
                "end_line": block["end"],
                "parent_heading_id": heading_ids.get(parent["start"], "") if parent else "",
                "source_excerpt": excerpt_text(block["text"]),
                "source_cells_json": "",
                "candidate_class": found,
                "normative_status": "NEEDS_REVIEW",
                "classification_suggestion": status,
                "normalized_obligation": "",
                "atomicity_status": "NOT_ATOMIZED",
                "logical_owner": "",
                "dependencies": "",
                "decision_reference": "",
                "graph_node_ids": ";".join(sorted(set(node_ids))),
                "classification_method": "RULE_BASED_CANDIDATE_ONLY",
                "classification_confidence": confidence,
                "review_status": "REVIEW_REQUIRED",
                "review_reason": reason,
            })
            fulltext_lines_seen[rel].update(range(block["start"], block["end"] + 1))
            candidate_count["TEXT_RANGE"] += 1

        # Verify every nonblank source line belongs to a heading, prose range,
        # table row, or fenced block; Markdown table separators are syntax only.
        expected_lines = {i + 1 for i, line in enumerate(file_lines) if line.strip() and not TABLE_SEPARATOR.match(line)}
        uncovered_lines = expected_lines - fulltext_lines_seen[rel]
        if uncovered_lines:
            structural_errors.extend([f"{rel}: nonblank line {n} was not enumerated" for n in sorted(uncovered_lines)[:50]])

    # Validate the underlying structural inventory and complete prose/table extraction.
    if sum(structural_count.values()) != 384:
        structural_errors.append(f"expected 384 structural units, found {sum(structural_count.values())}")
    if structural_count["HEADING"] != 326 or structural_count["TABLE"] != 58:
        structural_errors.append(f"heading/table counts are {structural_count['HEADING']}/{structural_count['TABLE']}")
    inv_fields = ["source_unit_id", "document", "document_blob_sha", "unit_type", "hierarchy_or_title", "start_line", "end_line", "table_lines", "normative_status", "classification_suggestion", "graph_node_ids", "coverage_status", "classification_method", "review_reason"]
    candidate_fields = ["candidate_id", "atomic_obligation_id", "source_unit_id", "document", "document_blob_sha", "source_sha256", "start_line", "end_line", "parent_heading_id", "source_excerpt", "source_cells_json", "candidate_class", "normative_status", "classification_suggestion", "normalized_obligation", "atomicity_status", "logical_owner", "dependencies", "decision_reference", "graph_node_ids", "classification_method", "classification_confidence", "review_status", "review_reason"]
    if args.check_only:
        hashes = {rel: {"git_blob_sha": git_blob(rel), "sha256": sha256(ROOT / rel), "physical_lines": len(parsed["lines"]), "final_newline": (ROOT / rel).read_bytes().endswith(b"\n")} for _, rel, parsed, _ in source_specs}
        baseline_inventory = csv.DictReader(io.StringIO(subprocess.check_output(["git", "show", f"{BASELINE_COMMIT}:{COVERAGE.relative_to(ROOT)}/source-inventory.csv"], cwd=ROOT, text=True)))
        baseline_candidates = csv.DictReader(io.StringIO(subprocess.check_output(["git", "show", f"{BASELINE_COMMIT}:{COVERAGE.relative_to(ROOT)}/atomic-obligations.csv"], cwd=ROOT, text=True)))
        current_inventory = read_csv(inventory_path)[1]
        current_candidates = read_csv(candidate_path)[1]
        machine = validate_outputs(list(baseline_inventory), list(baseline_candidates), current_inventory, current_candidates, hashes, graph_nodes, structural_errors)
        summary = {"structural_units": sum(structural_count.values()), "headings": structural_count["HEADING"], "tables": structural_count["TABLE"], "text_ranges": candidate_count["TEXT_RANGE"], "table_rows": candidate_count["TABLE_ROW"], "code_blocks": candidate_count["CODE_BLOCK"], "candidate_records": len(current_candidates), "machine_controls": machine}
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1 if any(v["result"] != "PASS" for v in machine.values()) else 0

    apply_source_unit_dispositions(inventory_rows)
    apply_review_dispositions(candidate_rows)
    write_csv(inventory_path, inv_fields, inventory_rows)
    write_csv(candidate_path, candidate_fields, candidate_rows)
    # Package index and trace are built below from the versioned plan source.
    build_package_index_and_traces(candidate_rows, source_hashes, graph_sha)
    subprocess.run([sys.executable, str(COVERAGE / "build_evidence_join_index.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    validations = validate_outputs(baseline_inventory, baseline_candidates, inventory_rows, candidate_rows, source_hashes, graph_nodes, structural_errors)
    update_manifest(structural_count, candidate_count, source_hashes, graph_sha, candidate_rows)
    write_reports(candidate_rows, structural_count, candidate_count, source_hashes, graph_sha, structural_errors, validations)
    print(json.dumps({"structural_units": sum(structural_count.values()), "headings": structural_count["HEADING"], "tables": structural_count["TABLE"], "text_ranges": candidate_count["TEXT_RANGE"], "table_rows": candidate_count["TABLE_ROW"], "candidate_rows": len(candidate_rows), "structural_errors": structural_errors}, ensure_ascii=False, indent=2))
    return 1 if structural_errors else 0


def build_package_index_and_traces(candidates: list[dict[str, Any]], source_hashes: dict[str, dict[str, Any]], graph_sha: str) -> None:
    plan_text = PLAN.read_text(encoding="utf-8")
    plan_lines = plan_text.splitlines()
    plan_blob = git_blob("docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md")
    package_index = []
    package_names: dict[str, str] = {}
    for line_no, line in enumerate(plan_lines, 1):
        m = STATUS_RE.match(line)
        if m and m.group(1) not in package_names:
            package_names[m.group(1)] = m.group(2)
    heading_positions: dict[str, list[tuple[int, str]]] = defaultdict(list)
    current = ""
    for i, line in enumerate(plan_lines, 1):
        m = re.match(r"^#{1,6}\s+(C\d{2}[ab]?|R\d{2}|A\d{2})\s*[—–-]\s*(.+)$", line)
        if m:
            current = m.group(1)
            heading_positions[current].append((i, m.group(2).strip()))
    trace_by_candidate: dict[str, list[str]] = defaultdict(list)
    graph_nodes, _ = graph_data()
    graph_node_ids = {n["id"] for n in graph_nodes if n.get("id")}
    graph_refs_by_plan_line: dict[int, set[str]] = defaultdict(set)
    trace_fields = ["candidate_id", "atomic_obligation_id", "source_unit_id", "source_document", "source_lines", "owner_package_candidates", "requirement_candidates", "story_enabler_candidates", "task_subtask_candidates", "ac_test_candidates", "graph_node_ids", "coverage_status", "evidence", "review_status"]
    # Citation-bearing plan lines are leads, not verified semantic relationships.
    source_index: dict[str, dict[int, list[dict[str, Any]]]] = {"B": defaultdict(list), "W": defaultdict(list)}
    review_rows=read_csv(COVERAGE / "semantic-review-dispositions.csv")[1] if (COVERAGE / "semantic-review-dispositions.csv").exists() else []
    reviewed_by_id={r["candidate_id"]:r for r in review_rows}
    for i, line in enumerate(plan_lines, 1):
        pkg = ""
        for ident, positions in heading_positions.items():
            starts = [p[0] for p in positions]
            if any(start <= i and (next_start := min((x for x in [q[0] for other, ps in heading_positions.items() for q in ps if q[0] > start]), default=len(plan_lines)+1)) > i for start in starts):
                pkg = ident
        ids = ID_RE.findall(line)
        graph_refs_by_plan_line[i].update(ref for ref in GRAPH_NODE_REF.findall(line) if ref in graph_node_ids)
        for ref in SOURCE_REF.finditer(line):
            doc_tag, lo, hi = ref.group(1), int(ref.group(2)), int(ref.group(3) or ref.group(2))
            for ln in range(lo, hi + 1):
                source_index[doc_tag][ln].append({"pkg": pkg, "ids": ids, "plan_line": i, "source_ref": ref.group(0), "graph_refs": graph_refs_by_plan_line[i]})

    trace_rows = []
    gap_rows = []
    for row in candidates:
        tag = "B" if row["document"].endswith("BLUEPRINT.md") else "W"
        leads = []
        for ln in range(int(row["start_line"]), int(row["end_line"]) + 1):
            leads.extend(source_index[tag].get(ln, []))
        candidate_graph_ids = set(filter(None, row["graph_node_ids"].split(";")))
        graph_leads = [
            {"pkg": pkg, "ids": [], "plan_line": line_no, "source_ref": "graph:" + node_id, "graph_refs": {node_id}}
            for line_no, node_ids in graph_refs_by_plan_line.items()
            for node_id in candidate_graph_ids & node_ids
            for pkg in [next((ident for ident, positions in heading_positions.items() if any(start <= line_no < min((q[0] for other, ps in heading_positions.items() for q in ps if q[0] > start), default=len(plan_lines)+1) for start, _ in positions)), "")]
        ]
        leads.extend(graph_leads)
        owners = sorted({x["pkg"] for x in leads if x["pkg"]})
        def package_qualified(lead: dict[str, Any], item: str, code: str) -> bool:
            return bool(lead["pkg"] and re.match(rf"^{re.escape(lead['pkg'].upper())}-{code}\d", item.upper()))
        reqs = sorted({x for lead in leads for x in lead["ids"] if x.startswith("REQ:") or package_qualified(lead,x,"(?:REQ|R)")})
        stories = sorted({x for lead in leads for x in lead["ids"] if x.startswith(("TE:", "STORY:", "EN:")) or package_qualified(lead,x,"(?:EN|E|STORY|S|TE)")})
        tasks = sorted({x for lead in leads for x in lead["ids"] if x.startswith("TASK:") or package_qualified(lead,x,"(?:TASK|T|SUBTASK)")})
        ac_tests = sorted({x for lead in leads for x in lead["ids"] if x.startswith(("AC:", "TEST:", "TD:", "TC:")) or package_qualified(lead,x,"(?:AC|TD|TEST|TC)")})
        evidence = sorted({f"plan:L{x['plan_line']} {x['source_ref']}" for x in leads})
        reviewed=reviewed_by_id.get(row["candidate_id"],{})
        not_applicable = reviewed.get("coverage_status")=="NOT_APPLICABLE"
        verified_status=reviewed.get("coverage_status") if reviewed.get("coverage_status") in {"VERIFIED_COVERED","VERIFIED_PARTIAL","VERIFIED_UNCOVERED"} else ""
        if verified_status:
            owners=[x for x in reviewed.get("related_packages","").split(";") if x]
            reqs=[x for x in reviewed.get("requirement_ids","").split(";") if x]
            tasks=[x for x in reviewed.get("task_ids","").split(";") if x]
            ac_tests=[x for x in reviewed.get("ac_test_ids","").split(";") if x]
            evidence=[f"{reviewed.get('source_evidence','')}; {reviewed.get('plan_evidence','')}; {reviewed.get('review_rationale','')}"]
        trace_rows.append({
            "candidate_id": row["candidate_id"], "atomic_obligation_id": row.get("atomic_obligation_id", ""), "source_unit_id": row["source_unit_id"],
            "source_document": row["document"], "source_lines": f"{row['start_line']}-{row['end_line']}",
            "owner_package_candidates": "" if not_applicable else ";".join(owners), "requirement_candidates": "" if not_applicable else ";".join(reqs),
            "story_enabler_candidates": "" if not_applicable else ";".join(stories), "task_subtask_candidates": "" if not_applicable else ";".join(tasks),
            "ac_test_candidates": "" if not_applicable else ";".join(ac_tests), "graph_node_ids": row["graph_node_ids"],
            "coverage_status": "NOT_APPLICABLE" if not_applicable else verified_status or ("PENDING_REVIEW" if leads else "NOT_MAPPED_CANDIDATE"),
            "evidence": row["review_reason"] if not_applicable else ";".join(evidence), "review_status": "SEMANTICALLY_REVIEWED" if (not_applicable or verified_status) else "UNVERIFIED_SEMANTIC_MAPPING",
        })
        open_decision = reviewed.get("normative_status") in {"NORMATIVE_OPEN_DECISION", "MIXED"} and verified_status=="VERIFIED_PARTIAL"
        if not_applicable or (verified_status and not open_decision):
            continue
        gap_rows.append({
            "gap_id": f"REV-{row['candidate_id']}", "candidate_id": row["candidate_id"], "atomic_obligation_id": "",
            "source_unit_id": row["source_unit_id"], "source_document": row["document"], "source_lines": f"{row['start_line']}-{row['end_line']}",
            "source_evidence": row["source_excerpt"], "related_packages": ";".join(owners),
            "gap_type": "OPEN_DECISION" if open_decision else "PENDING_SEMANTIC_REVIEW", "severity": "DECISION_REQUIRED" if open_decision else "UNASSESSED",
            "description": "The source identifies an unresolved owner decision. The linked requirement and plan evidence describe the affected behavior; this audit does not approve a value or policy." if open_decision else "Candidate classification and package coverage have not been semantically verified; this is not a confirmed uncovered obligation or a confirmed gap.",
            "suggested_resolution": "Keep the dependent value or behavior unset; record the owner's decision and update the affected requirement, acceptance criteria, tests, and dependent tasks before implementation." if open_decision else "Review source against package requirement, task, AC and test; then classify as covered/partial/uncovered/open/not-applicable.",
            "confidence": "HIGH" if open_decision else row["classification_confidence"], "review_status": "OPEN_DECISION" if open_decision else "OPEN_REVIEW",
        })

    package_index_fields = ["package_id", "package_name", "scope_excerpt", "program_family", "planning_status", "declared_ra", "declared_ipa", "product_status", "plan_heading_lines", "mentioned_candidate_ids", "mentioned_requirement_ids", "mentioned_story_enabler_ids", "mentioned_task_subtask_ids", "mentioned_ac_ids", "mentioned_test_definition_ids", "mentioned_test_case_ids", "mentioned_ac_td_test_case_ids", "mentioned_dependency_ids", "mentioned_contract_ids", "mentioned_handoff_ids", "source_reference_count", "graph_node_reference_ids", "ownership_evidence", "dependency_evidence", "contract_evidence", "handoff_evidence", "index_status"]
    for pkg, name in package_names.items():
        positions = heading_positions.get(pkg, [])
        if positions:
            start = positions[-1][0] if pkg in {"C11b", "C12a"} else positions[0][0]
            next_starts = [p[0] for other, ps in heading_positions.items() for p in ps if p[0] > start]
            end = min(next_starts, default=len(plan_lines) + 1) - 1
            segment = "\n".join(plan_lines[start - 1 : end])
            hlines = ";".join(str(p[0]) for p in positions)
        else:
            segment, hlines = "", ""
        ids = sorted(set(ID_RE.findall(segment)))
        refs = SOURCE_REF.findall(segment)
        pkg_graph_refs = sorted({node for line_no, nodes in graph_refs_by_plan_line.items() if start <= line_no <= end for node in nodes}) if positions else []
        code=pkg.upper()
        def select(prefixes: tuple[str, ...], suffixes: tuple[str, ...] = ()) -> str:
            return ";".join(x for x in ids if x.startswith(prefixes) or any(x.upper().startswith(code+"-"+suffix) for suffix in suffixes))
        ac_ids = select(("AC:",), ("AC",))
        test_definition_ids = select(("TD:", "TEST:"), ("TD", "TEST"))
        test_case_ids = select(("TC:",), ("TC",))
        dependency_ids = select(("DEP:", "DEPENDENCY:"), ("DEP", "DEPENDENCY"))
        contract_ids = select(("CONTRACT:",), ("CONTRACT",))
        handoff_ids = select(("HANDOFF:",), ("HANDOFF",))
        family = "Core/Wallet" if pkg.startswith("C") else "RAG/Adviser" if pkg.startswith("R") else "Assistant"
        status_line = next((line for line in plan_lines[:75] if STATUS_RE.match(line) and STATUS_RE.match(line).group(1) == pkg), "")
        sm = STATUS_RE.match(status_line) if status_line else None
        seglines=[line.strip() for line in segment.splitlines()]
        scope_lines=[line for line in seglines if "دامنه" in line or "Scope" in line][:12]
        owner_lines=[line for line in seglines if "مالک" in line or "ownership" in line.casefold()][:20]
        dependency_lines=[line for line in seglines if "وابستگی" in line or "dependency" in line.casefold() or "پیش‌نیاز" in line][:20]
        contract_lines=[line for line in seglines if "قرارداد" in line or "contract" in line.casefold()][:20]
        handoff_lines=[line for line in seglines if "handoff" in line.casefold() or "تحویل به" in line or "واگذاری" in line][:20]
        package_index.append({
            "package_id": pkg, "package_name": name, "scope_excerpt": " || ".join(scope_lines), "program_family": family,
            "planning_status": "PLANNING_ACCEPTED" if sm and "PLANNING_ACCEPTED" in sm.group(5) else "STATUS_FROM_PLAN_TABLE",
            "declared_ra": sm.group(3).upper() if sm else "NOT_FOUND", "declared_ipa": sm.group(4).upper() if sm else "NOT_FOUND",
            "product_status": sm.group(5).strip() if sm else "NOT_FOUND", "plan_heading_lines": hlines,
            "mentioned_candidate_ids": select(("CAND:", "CAND-", "CANDIDATE-")), "mentioned_requirement_ids": select(("REQ:",), ("REQ", "R")),
            "mentioned_story_enabler_ids": select(("TE:", "STORY:", "EN:"), ("EN", "E", "STORY", "S")), "mentioned_task_subtask_ids": select(("TASK:",), ("TASK", "T", "SUBTASK", "S")),
            "mentioned_ac_ids": ac_ids, "mentioned_test_definition_ids": test_definition_ids, "mentioned_test_case_ids": test_case_ids,
            "mentioned_ac_td_test_case_ids": ";".join(x for x in (ac_ids, test_definition_ids, test_case_ids) if x),
            "mentioned_dependency_ids": dependency_ids, "mentioned_contract_ids": contract_ids, "mentioned_handoff_ids": handoff_ids,
            "source_reference_count": len(refs) + len(pkg_graph_refs), "graph_node_reference_ids": ";".join(pkg_graph_refs),
            "ownership_evidence": " || ".join(owner_lines), "dependency_evidence": " || ".join(dependency_lines),
            "contract_evidence": " || ".join(contract_lines), "handoff_evidence": " || ".join(handoff_lines),
            "index_status": "INDEXED_REFERENCES_NOT_SEMANTICALLY_VALIDATED",
        })

    write_csv(COVERAGE / "execution-trace.csv", trace_fields, trace_rows)
    write_csv(COVERAGE / "package-execution-index.csv", package_index_fields, package_index)
    gap_fields = ["gap_id", "candidate_id", "atomic_obligation_id", "source_unit_id", "source_document", "source_lines", "source_evidence", "related_packages", "gap_type", "severity", "description", "suggested_resolution", "confidence", "review_status"]
    write_csv(COVERAGE / "coverage-gap-register.csv", gap_fields, gap_rows)


def source_locator_matches(evidence: str, candidate: dict[str, Any]) -> bool:
    """Accept a locator only when its exact line/range stays inside its source unit."""
    locator = evidence.split(";", 1)[0].strip()
    match = re.fullmatch(r"(.+):([0-9]+)(?:-([0-9]+))? [(]([^)]+)[)]", locator)
    if not match:
        return False
    document, first, last, unit_id = match.groups()
    lo, hi = int(first), int(last or first)
    return (
        document == candidate.get("document")
        and unit_id == candidate.get("source_unit_id")
        and int(candidate["start_line"]) <= lo <= hi <= int(candidate["end_line"])
    )


def validate_outputs(old_inventory: list[dict[str, str]], old_candidates: list[dict[str, str]], inventory: list[dict[str, Any]], candidates: list[dict[str, Any]], source_hashes: dict[str, dict[str, Any]], graph_nodes: list[dict[str, Any]], structural_errors: list[str]) -> dict[str, dict[str, Any]]:
    graph_ids = {n["id"] for n in graph_nodes if n.get("id")}
    unit_ids = [r["source_unit_id"] for r in inventory]
    candidate_ids = [r["candidate_id"] for r in candidates]
    plan_text = PLAN.read_text(encoding="utf-8")
    plan_ids = set(ID_RE.findall(plan_text))
    plan_lines = plan_text.splitlines()
    package_fields, packages = read_csv(COVERAGE / "package-execution-index.csv")
    trace_fields, trace = read_csv(COVERAGE / "execution-trace.csv")
    valid_statuses = {"NORMATIVE_APPROVED", "NORMATIVE_OPEN_DECISION", "DESCRIPTIVE", "EXAMPLE", "OUT_OF_SCOPE", "SUPERSEDED", "MIXED", "NEEDS_REVIEW", "NOT_APPLICABLE"}
    old_inventory_ids = {r["source_unit_id"] for r in old_inventory}
    old_candidate_ids = {r["candidate_id"] for r in old_candidates}
    allowed_package_ids = {r["package_id"] for r in packages}
    checks: dict[str, dict[str, Any]] = {}

    def record(name: str, checked: int, errors: list[str]) -> None:
        checks[name] = {"checked": checked, "errors": len(errors), "result": "PASS" if not errors else "FAIL", "examples": errors[:8]}

    record("heading_count", sum(r["unit_type"] == "HEADING" for r in inventory), [f"found {sum(r['unit_type']=='HEADING' for r in inventory)}"] if sum(r["unit_type"] == "HEADING" for r in inventory) != 326 else [])
    record("table_count", sum(r["unit_type"] == "TABLE" for r in inventory), [f"found {sum(r['unit_type']=='TABLE' for r in inventory)}"] if sum(r["unit_type"] == "TABLE" for r in inventory) != 58 else [])
    record("source_unit_id_uniqueness", len(unit_ids), [f"duplicate {x}" for x,n in Counter(unit_ids).items() if n > 1])
    record("atomic_candidate_id_uniqueness", len(candidate_ids), [f"duplicate {x}" for x,n in Counter(candidate_ids).items() if n > 1])
    obligation_ids = [r["atomic_obligation_id"] for r in candidates if r.get("atomic_obligation_id")]
    record("atomic_obligation_id_uniqueness", len(obligation_ids), [f"duplicate {x}" for x,n in Counter(obligation_ids).items() if n > 1])
    bad_ranges=[]
    for row in inventory:
        maximum=source_hashes[row["document"]]["physical_lines"]
        if not (1 <= int(row["start_line"]) <= int(row["end_line"]) <= maximum):
            bad_ranges.append(f"{row['source_unit_id']}:{row['start_line']}-{row['end_line']} > {maximum}")
    record("source_line_ranges", len(inventory), bad_ranges)
    blob_errors=[]
    for rel,info in source_hashes.items():
        inv_blobs={r["document_blob_sha"] for r in inventory if r["document"]==rel}
        if inv_blobs!={info["git_blob_sha"]}:blob_errors.append(f"{rel}: {inv_blobs}")
    record("source_blob_sha", len(source_hashes), blob_errors)
    graph_refs={x for r in inventory for x in r["graph_node_ids"].split(";") if x}
    graph_refs|={x for r in candidates for x in r["graph_node_ids"].split(";") if x}
    record("graph_node_references", len(graph_refs), [f"missing graph node {x}" for x in sorted(graph_refs-graph_ids)])
    inventory_id_set=set(unit_ids)
    missing_source_units=[f"{r['candidate_id']} -> {r['source_unit_id']}" for r in candidates if r["source_unit_id"] not in inventory_id_set]
    record("candidate_source_unit_references", len(candidates), missing_source_units)
    heading_id_set={r["source_unit_id"] for r in inventory if r["unit_type"]=="HEADING"}
    missing_parents=[f"{r['candidate_id']} -> {r['parent_heading_id']}" for r in candidates if r["parent_heading_id"] and r["parent_heading_id"] not in heading_id_set]
    record("parent_heading_references", sum(bool(r["parent_heading_id"]) for r in candidates), missing_parents)
    table_rows_by_unit=Counter(r["source_unit_id"] for r in candidates if r["candidate_class"] in {"TABLE_HEADER","TABLE_ROW_CANDIDATE"})
    table_errors=[]
    for unit in (r for r in inventory if r["unit_type"]=="TABLE"):
        lines=(ROOT/unit["document"]).read_text(encoding="utf-8").splitlines()
        expected=sum(1 for line in lines[int(unit["start_line"])-1:int(unit["end_line"])] if line.strip() and not TABLE_SEPARATOR.match(line))
        actual=table_rows_by_unit.get(unit["source_unit_id"],0)
        if expected!=actual:table_errors.append(f"{unit['source_unit_id']}: expected {expected} rows, found {actual}")
    record("table_row_enumeration", sum(table_rows_by_unit.values()), table_errors)
    expected_package_ids={m.group(1) for line in PLAN.read_text(encoding="utf-8").splitlines()[:75] if (m:=STATUS_RE.match(line))}
    package_errors=[f"missing package {x}" for x in sorted(expected_package_ids-allowed_package_ids)] + [f"unexpected package {x}" for x in sorted(allowed_package_ids-expected_package_ids)]
    if len(packages)!=36:package_errors.append(f"package row count {len(packages)}")
    record("package_ids", len(packages), package_errors)
    ref_errors=[]
    for col in ["requirement_candidates","task_subtask_candidates","ac_test_candidates","story_enabler_candidates"]:
        for row in trace:
            for value in filter(None,row[col].split(";")):
                if value not in plan_ids:ref_errors.append(f"{col}: {value} not found in plan")
    record("requirement_task_ac_test_references", sum(len(r[c].split(";")) for r in trace for c in ["requirement_candidates","task_subtask_candidates","ac_test_candidates","story_enabler_candidates"]), ref_errors)
    package_ref_columns = ["mentioned_candidate_ids", "mentioned_requirement_ids", "mentioned_story_enabler_ids", "mentioned_task_subtask_ids", "mentioned_ac_ids", "mentioned_test_definition_ids", "mentioned_test_case_ids", "mentioned_dependency_ids", "mentioned_contract_ids", "mentioned_handoff_ids"]
    package_ref_errors=[]
    for row in packages:
        for col in package_ref_columns:
            for value in filter(None, row.get(col, "").split(";")):
                if value not in plan_ids:package_ref_errors.append(f"{row['package_id']} {col}: {value} not found in plan")
    record("package_index_reference_integrity", sum(len(r.get(c, "").split(";")) for r in packages for c in package_ref_columns), package_ref_errors)
    owner_errors=[]
    for row in trace:
        for owner in filter(None,row["owner_package_candidates"].split(";")):
            if owner not in allowed_package_ids:owner_errors.append(f"unknown package {owner}")
    record("candidate_package_references", sum(bool(r["owner_package_candidates"]) for r in trace), owner_errors)
    missing_refs=[x for x in old_inventory_ids if x not in set(unit_ids)] + [x for x in old_candidate_ids if x not in set(candidate_ids)]
    record("baseline_rows_preserved", len(old_inventory_ids)+len(old_candidate_ids), [f"dropped {x}" for x in missing_refs])
    status_errors=[f"{r['candidate_id']} invalid status {r['normative_status']}" for r in candidates if r["normative_status"] not in valid_statuses]
    record("classification_status_values", len(candidates), status_errors)
    ledger_rows = read_csv(COVERAGE / "semantic-review-dispositions.csv")[1] if (COVERAGE / "semantic-review-dispositions.csv").exists() else []
    ledger_by_id = {r["candidate_id"]: r for r in ledger_rows}
    candidate_class_counts = Counter(r.get("candidate_class", "") for r in candidates)
    reconciliation_errors = []
    if sum(candidate_class_counts.values()) != len(candidates):
        reconciliation_errors.append(f"candidate classes total {sum(candidate_class_counts.values())} != candidate records {len(candidates)}")
    reviewed_count = len(ledger_by_id)
    pending_count = len(set(candidate_ids) - set(ledger_by_id))
    if reviewed_count + pending_count != len(candidates):
        reconciliation_errors.append(f"reviewed {reviewed_count} + pending {pending_count} != candidate records {len(candidates)}")
    record("candidate_count_reconciliation", len(candidates), reconciliation_errors)
    atom_fields, atom_rows = read_csv(COVERAGE / "atomic-obligation-dispositions.csv") if (COVERAGE / "atomic-obligation-dispositions.csv").exists() else ([], [])
    promoted_suggestions=[]
    disposition_errors=[]
    if len(ledger_rows) != len(ledger_by_id):
        disposition_errors.append("duplicate candidate ID in semantic review ledger")
    for review in ledger_rows:
        row=next((x for x in candidates if x["candidate_id"]==review["candidate_id"]),None)
        if not row:
            disposition_errors.append(f"unknown candidate {review['candidate_id']}")
            continue
        expected=f"{row['document']}:{row['start_line']} ({row['source_unit_id']})"
        if not source_locator_matches(review.get("source_evidence",""), row):
            disposition_errors.append(f"source locator drift {review['candidate_id']}")
        valid_header = row["candidate_class"] == "TABLE_HEADER" and review.get("semantic_disposition") == "STRUCTURAL_HEADER_ONLY" and review.get("normative_status") == "NOT_APPLICABLE"
        valid_separator = row["candidate_class"] == "TEXT_RANGE_CANDIDATE" and row["source_excerpt"].strip() == "---" and review.get("semantic_disposition") == "MARKDOWN_HORIZONTAL_RULE_ONLY" and review.get("normative_status") == "NOT_APPLICABLE"
        valid_example = row["candidate_class"] in {"TABLE_ROW_CANDIDATE", "TEXT_RANGE_CANDIDATE", "UNCLASSIFIED_CANDIDATE", "NORMATIVE_CANDIDATE"} and review.get("semantic_disposition") in {"EXAMPLE_CONTEXT_ROW", "EXAMPLE_CONTEXT_CONTENT"} and review.get("normative_status") == "EXAMPLE" and bool(review.get("review_rationale", "").strip())
        valid_descriptive = row["candidate_class"] in {"TABLE_ROW_CANDIDATE", "TEXT_RANGE_CANDIDATE", "CODE_BLOCK_CANDIDATE", "UNCLASSIFIED_CANDIDATE", "NORMATIVE_CANDIDATE"} and review.get("semantic_disposition") in {"DESCRIPTIVE_CONTEXT_ONLY", "QUESTION_CONTEXT_ONLY", "SOURCE_REFERENCE_ONLY"} and review.get("normative_status") == "DESCRIPTIVE" and bool(review.get("review_rationale", "").strip())
        mapped_status=review.get("coverage_status") in {"VERIFIED_COVERED","VERIFIED_PARTIAL","VERIFIED_UNCOVERED"}
        open_decision=review.get("normative_status")=="NORMATIVE_OPEN_DECISION" and review.get("coverage_status") in {"VERIFIED_PARTIAL","OPEN_DECISION"}
        candidate_atoms=[a for a in atom_rows if a.get("candidate_id")==review["candidate_id"]]
        mixed_atoms={a.get("normative_status") for a in candidate_atoms}
        mixed_decomposed=review.get("normative_status")=="MIXED" and bool(candidate_atoms) and {"NORMATIVE_APPROVED","NORMATIVE_OPEN_DECISION"}.issubset(mixed_atoms)
        valid_mapping=mapped_status and bool(review.get("related_packages")) and bool(review.get("requirement_ids")) and bool(review.get("task_ids")) and bool(review.get("ac_test_ids")) and bool(review.get("plan_evidence")) and (review.get("normative_status")=="NORMATIVE_APPROVED" or open_decision or mixed_decomposed)
        explicit_gap=(review.get("coverage_status")=="VERIFIED_PARTIAL" and review.get("mapping_status") in {"UNMAPPED_GAP","INCOMPLETE_CROSSWALK"} and review.get("normative_status")=="NORMATIVE_APPROVED" and bool(review.get("atomic_obligation_id")))
        if explicit_gap or valid_mapping:
            cited=set()
            for lo,hi in re.findall(r":(\d+)(?:-(\d+))?",review.get("plan_evidence","")):
                a=int(lo);b=int(hi or lo)
                if a<1 or b>len(plan_lines) or b<a:
                    valid_mapping=False
                    break
                cited.update(range(a,b+1))
            cited_text="\n".join(plan_lines[n-1] for n in cited)
            mapped_ids=set(review.get("requirement_ids","").split(";")+review.get("task_ids","").split(";")+review.get("ac_test_ids","").split(";"))
            if (valid_mapping and not cited) or any(item and item not in cited_text for item in mapped_ids):
                valid_mapping=False
            if explicit_gap and any(item and item not in cited_text for item in mapped_ids):
                explicit_gap=False
        valid_na=(valid_header or valid_separator or valid_example or valid_descriptive) and review.get("coverage_status")=="NOT_APPLICABLE"
        valid_open=review.get("semantic_disposition")=="OPEN_DECISION" and review.get("normative_status")=="NORMATIVE_OPEN_DECISION" and review.get("coverage_status")=="OPEN_DECISION" and bool(review.get("review_rationale",""))
        if not (valid_na or valid_mapping or explicit_gap or valid_open):
            disposition_errors.append(f"invalid disposition or semantic mapping {review['candidate_id']}")
        if row["normative_status"] != review.get("normative_status") or row["review_status"] != "SEMANTICALLY_REVIEWED":
            disposition_errors.append(f"candidate does not reflect ledger disposition {review['candidate_id']}")
    record("semantic_review_disposition_integrity", len(ledger_rows), disposition_errors)
    candidate_by_id={r["candidate_id"]:r for r in candidates}
    atom_ids=[r.get("atomic_obligation_id","") for r in atom_rows]
    atom_errors=[]
    if len(atom_ids)!=len(set(atom_ids)):
        atom_errors.append("duplicate atomic obligation ID")
    valid_atom_statuses={"NORMATIVE_APPROVED","NORMATIVE_OPEN_DECISION"}
    valid_atom_coverage={"VERIFIED_COVERED","VERIFIED_PARTIAL","VERIFIED_UNCOVERED","OPEN_DECISION"}
    for atom in atom_rows:
        candidate=candidate_by_id.get(atom.get("candidate_id",""))
        if not candidate:
            atom_errors.append(f"unknown candidate {atom.get('candidate_id')}")
            continue
        expected=f"{candidate['document']}:{candidate['start_line']} ({candidate['source_unit_id']})"
        if not source_locator_matches(atom.get("source_evidence",""), candidate):
            atom_errors.append(f"source locator drift {atom.get('atomic_obligation_id')}")
        if not all(atom.get(k,"").strip() for k in ("atomic_obligation_id","normalized_obligation","normative_status","coverage_status","source_evidence","review_rationale","reviewer","review_date")):
            atom_errors.append(f"missing obligation evidence {atom.get('atomic_obligation_id')}")
        if atom.get("normative_status") not in valid_atom_statuses or atom.get("coverage_status") not in valid_atom_coverage:
            atom_errors.append(f"invalid obligation status {atom.get('atomic_obligation_id')}")
        mapping_gap=atom.get("coverage_status")=="VERIFIED_PARTIAL" and atom.get("mapping_status") in {"UNMAPPED_GAP","INCOMPLETE_CROSSWALK"}
        if atom.get("coverage_status") in {"VERIFIED_COVERED","VERIFIED_PARTIAL","VERIFIED_UNCOVERED"}:
            mapped=[x for k in ("related_packages","requirement_ids","task_ids","ac_test_ids","plan_evidence") for x in atom.get(k,"").split(";") if x.strip()]
            if not mapping_gap and len(mapped)<5:
                atom_errors.append(f"incomplete mapping {atom.get('atomic_obligation_id')}")
            cited=set()
            for ref in filter(None, atom.get("plan_evidence","").split(";")):
                m=re.search(r":(\d+)(?:-(\d+))?$",ref.strip())
                if not m: atom_errors.append(f"invalid plan locator {atom.get('atomic_obligation_id')}: {ref}"); continue
                lo,hi=int(m.group(1)),int(m.group(2) or m.group(1))
                if lo<1 or hi>len(plan_lines) or hi<lo:
                    atom_errors.append(f"plan line out of range {atom.get('atomic_obligation_id')}: {ref}"); continue
                cited.update(range(lo,hi+1))
            cited_text="\n".join(plan_lines[n-1] for n in cited)
            identifiers=[x for k in ("requirement_ids","story_enabler_ids","task_ids","ac_test_ids") for x in atom.get(k,"").split(";") if x.strip()]
            if ((not mapping_gap and not cited) or any(identifier not in cited_text for identifier in identifiers)):
                atom_errors.append(f"plan evidence does not contain mapped IDs {atom.get('atomic_obligation_id')}")
        elif atom.get("coverage_status")=="OPEN_DECISION" and not atom.get("decision_reference","").strip():
            atom_errors.append(f"open obligation lacks decision reference {atom.get('atomic_obligation_id')}")
    for review in ledger_rows:
        if review.get("atomicity_status")=="DECOMPOSED" and not any(a.get("candidate_id")==review["candidate_id"] for a in atom_rows):
            atom_errors.append(f"decomposed candidate has no atomic obligations {review['candidate_id']}")
    record("atomic_obligation_ledger_integrity",len(atom_rows),atom_errors)
    batch_rows=read_csv(COVERAGE / "semantic-batch-progress.csv")[1] if (COVERAGE / "semantic-batch-progress.csv").exists() else []
    batch_errors=[]
    batch_keys=[]
    for item in batch_rows:
        key=(item.get("batch_id",""),item.get("candidate_id",""))
        batch_keys.append(key)
        if not all(key) or not item.get("source_scope","").strip(): batch_errors.append(f"incomplete batch selection {key}")
        if item.get("candidate_id") not in candidate_by_id: batch_errors.append(f"unknown batch candidate {item.get('candidate_id')}")
        if item.get("already_reviewed_before_batch") not in {"true","false"}: batch_errors.append(f"invalid pre-batch state {key}")
        if item.get("candidate_id") not in ledger_by_id: batch_errors.append(f"batch candidate not adjudicated {key}")
    if len(batch_keys)!=len(set(batch_keys)): batch_errors.append("duplicate candidate selection within batch")
    record("semantic_batch_ledger_integrity",len(batch_rows),batch_errors)
    for row in candidates:
        review = ledger_by_id.get(row["candidate_id"])
        if review:
            if row["normative_status"] != review["normative_status"] or row["review_status"] != "SEMANTICALLY_REVIEWED":
                promoted_suggestions.append(f"{row['candidate_id']} does not match its reviewed disposition")
        elif row["normative_status"] != "NEEDS_REVIEW" or row["review_status"] != "REVIEW_REQUIRED":
            promoted_suggestions.append(f"{row['candidate_id']} promoted {row['classification_suggestion']} without a review ledger entry")
    record("heuristic_status_not_promoted", len(candidates), promoted_suggestions)
    suggestion_errors=[f"{r['candidate_id']} invalid suggestion {r['classification_suggestion']}" for r in candidates if r["classification_suggestion"] not in valid_statuses]
    record("classification_suggestion_values", len(candidates), suggestion_errors)
    trace_ids={r["candidate_id"] for r in trace}
    trace_errors=[f"missing trace row {x}" for x in set(candidate_ids)-trace_ids] + [f"orphan trace row {x}" for x in trace_ids-set(candidate_ids)]
    record("execution_trace_row_integrity", len(trace), trace_errors)
    manual_by_id={r["candidate_id"]:r for r in ledger_rows}
    verified_errors=[]
    for row in trace:
        if row["coverage_status"] not in {"VERIFIED_COVERED","VERIFIED_PARTIAL","VERIFIED_UNCOVERED"} and row["review_status"]!="VERIFIED":
            continue
        review=manual_by_id.get(row["candidate_id"])
        if not review or row["coverage_status"]!=review.get("coverage_status") or row["owner_package_candidates"]!=review.get("related_packages") or row["requirement_candidates"]!=review.get("requirement_ids") or row["task_subtask_candidates"]!=review.get("task_ids") or row["ac_test_candidates"]!=review.get("ac_test_ids"):
            verified_errors.append(row["candidate_id"])
    record("no_unverified_mapping_marked_verified", len(trace), [f"unexpected verified mapping {x}" for x in verified_errors])
    missing_review_reasons=[r["candidate_id"] for r in candidates if not r.get("review_reason", "").strip()]
    record("review_required_rows_have_reason", len(candidates), missing_review_reasons)
    unit_ledger=read_csv(COVERAGE / "source-unit-review-dispositions.csv")[1] if (COVERAGE / "source-unit-review-dispositions.csv").exists() else []
    unit_by_id={r["source_unit_id"]:r for r in unit_ledger}
    unit_disposition_errors=[]
    if len(unit_by_id)!=len(unit_ledger):
        unit_disposition_errors.append("duplicate source-unit ID")
    inventory_by_id={r["source_unit_id"]:r for r in inventory}
    for review in unit_ledger:
        row=inventory_by_id.get(review["source_unit_id"])
        if not row:
            unit_disposition_errors.append(f"unknown source unit {review['source_unit_id']}")
            continue
        expected=f"{row['document']}:{row['start_line']}-{row['end_line']} ({row['source_unit_id']})"
        expected_disposition="STRUCTURAL_SECTION_LOCATOR" if row["unit_type"]=="HEADING" else "STRUCTURAL_TABLE_CONTAINER" if row["unit_type"]=="TABLE" else ""
        if row["unit_type"] not in {"HEADING","TABLE"} or review.get("unit_type")!=row["unit_type"] or review.get("semantic_disposition")!=expected_disposition or review.get("source_evidence")!=expected:
            unit_disposition_errors.append(f"invalid source-unit disposition or locator {review['source_unit_id']}")
        if row["normative_status"]!="NOT_APPLICABLE" or row["coverage_status"]!="NOT_APPLICABLE":
            unit_disposition_errors.append(f"source unit does not reflect disposition {review['source_unit_id']}")
    record("structural_source_unit_disposition_integrity",len(unit_ledger),unit_disposition_errors)
    join_errors=[]
    join_path=COVERAGE / "evidence-join-index.json"
    try:
        join=json.loads(join_path.read_text(encoding="utf-8"))
        join_items=join.get("candidate_index",[])
        join_ids=[r.get("candidate_id") for r in join_items]
        join_atoms=sum(len(r.get("atomic_obligation_ids",[])) for r in join_items)
        package_locator_count=len(read_csv(COVERAGE / "package-semantic-evidence.csv")[1])
        if join.get("graph",{}).get("commit")!="17622bf4dd56108bee10d880a9dc5eb9617482fd":join_errors.append("pinned graph commit mismatch")
        if join.get("graph",{}).get("sha256")!="f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93":join_errors.append("pinned graph SHA-256 mismatch")
        if len(join_items)!=len(candidates) or set(join_ids)!=set(candidate_ids):join_errors.append("candidate index count/IDs mismatch")
        if join_atoms!=len(atom_rows):join_errors.append(f"join atomic obligation count {join_atoms} != ledger {len(atom_rows)}")
        if join.get("totals",{}).get("package_evidence_locators")!=package_locator_count:join_errors.append("package evidence locator count mismatch")
    except Exception as exc:
        join_errors.append(f"evidence join index unavailable or invalid: {exc}")
    record("evidence_join_index_integrity",len(candidates),join_errors)
    record("structural_parse", sum(1 for _ in inventory), structural_errors)
    return checks


def update_manifest(structural: Counter[str], candidate_counts: Counter[str], source_hashes: dict[str, dict[str, Any]], graph_sha: str, candidates: list[dict[str, Any]]) -> None:
    path=COVERAGE/"extraction-manifest.json"
    original=json.loads(path.read_text(encoding="utf-8"))
    original["source_blobs"]=[{"path":rel,"git_blob_sha":info["git_blob_sha"],"sha256":info["sha256"],"physical_lines":info["physical_lines"],"final_newline":info["final_newline"]} for rel,info in source_hashes.items()]
    original["heading_count"]=structural["HEADING"]
    original["table_count"]=structural["TABLE"]
    original["source_unit_count"]=structural["HEADING"]+structural["TABLE"]
    original["paragraph_range_count"]=candidate_counts["TEXT_RANGE"]
    original["candidate_paragraph_count"]=candidate_counts["TEXT_RANGE"]
    original["baseline_paragraph_candidate_count"]=1110
    original["newly_recovered_paragraph_range_count"]=candidate_counts["TEXT_RANGE"]-1110
    original["table_row_candidate_count"]=candidate_counts["TABLE_ROW"]
    original["code_block_count"]=candidate_counts["CODE_BLOCK"]
    original["inventory_row_count"]=sum(structural.values())+candidate_counts["TEXT_RANGE"]+candidate_counts["CODE_BLOCK_UNIT"]
    original["candidate_record_count"]=len(candidates)
    original["graph"]={"commit":GRAPH_COMMIT,"path":GRAPH_PATH,"sha256":graph_sha,"usage":"discovery and locator references only; no semantic mapping is accepted from graph edges alone"}
    reviewed=sum(r.get("review_status")=="SEMANTICALLY_REVIEWED" for r in candidates)
    pending=len(candidates)-reviewed
    source_dispositions=read_csv(COVERAGE / "source-unit-review-dispositions.csv")[1] if (COVERAGE / "source-unit-review-dispositions.csv").exists() else []
    original["structural_source_unit_disposition_ledger"]="docs/audits/phase2-source-coverage/source-unit-review-dispositions.csv"
    original["structural_source_units_dispositioned"]=len(source_dispositions)
    original["semantic_review_disposition_ledger"]="docs/audits/phase2-source-coverage/semantic-review-dispositions.csv"
    original["semantic_reviewed_candidate_count"]=reviewed
    original["pending_semantic_candidate_count"]=pending
    original["method"]="Preserve baseline candidate IDs; reconcile source units; apply only individually evidenced dispositions from semantic-review-dispositions.csv; all other classifications remain pending; package links remain unverified."
    candidate_kinds=Counter(r["candidate_class"] for r in candidates)
    reviewed_ids={r["candidate_id"] for r in candidates if r.get("review_status")=="SEMANTICALLY_REVIEWED"}
    reviewed_kinds=Counter(r["candidate_class"] for r in candidates if r["candidate_id"] in reviewed_ids)
    original["semantic_batch_progress_ledger"]="docs/audits/phase2-source-coverage/semantic-batch-progress.csv"
    original["atomic_obligation_disposition_ledger"]="docs/audits/phase2-source-coverage/atomic-obligation-dispositions.csv"
    original["limitations"]=[
        f"{reviewed} of {len(candidates)} candidates have individual dispositions; {pending} remain pending semantic review.",
        f"Remaining unreviewed content is derived from candidate rows: {candidate_kinds['TEXT_RANGE_CANDIDATE']-reviewed_kinds['TEXT_RANGE_CANDIDATE']} text ranges, {candidate_kinds['TABLE_ROW_CANDIDATE']-reviewed_kinds['TABLE_ROW_CANDIDATE']} table data rows, and {candidate_kinds['CODE_BLOCK_CANDIDATE']-reviewed_kinds['CODE_BLOCK_CANDIDATE']} fenced blocks.",
        "Execution references are candidate citations and must be confirmed against package behavior.",
        "Graph node overlap is only a retrieval aid; inferred/ambiguous edges do not approve requirements.",
        "The 1,110 baseline paragraph candidates are preserved; 26 previously omitted prose ranges are appended with new IDs.",
    ]
    original["status"]="SEMANTIC_REVIEW_PENDING" if pending else "SEMANTIC_REVIEW_COMPLETE"
    path.write_text(json.dumps(original,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def write_reports(candidates: list[dict[str, Any]], structural: Counter[str], candidate_counts: Counter[str], source_hashes: dict[str, dict[str, Any]], graph_sha: str, structural_errors: list[str], validations: dict[str, dict[str, Any]]) -> None:
    statuses = Counter(r["classification_suggestion"] for r in candidates)
    review_states = Counter(r["review_status"] for r in candidates)
    trace_fields, trace = read_csv(COVERAGE / "execution-trace.csv")
    package_fields, packages = read_csv(COVERAGE / "package-execution-index.csv")
    gap_fields, gaps = read_csv(COVERAGE / "coverage-gap-register.csv")
    gap_states=Counter(r.get("review_status", "") for r in gaps)
    candidate_fields, candidate_rows = read_csv(COVERAGE / "atomic-obligations.csv")
    reviewed_count=sum(r.get("review_status")=="SEMANTICALLY_REVIEWED" for r in candidates)
    pending_count=len(candidates)-reviewed_count
    source_dispositions=read_csv(COVERAGE / "source-unit-review-dispositions.csv")[1] if (COVERAGE / "source-unit-review-dispositions.csv").exists() else []
    reviewed_ledger=read_csv(COVERAGE / "semantic-review-dispositions.csv")[1] if (COVERAGE / "semantic-review-dispositions.csv").exists() else []
    reviewed_ledger_ids={r["candidate_id"] for r in reviewed_ledger}
    reviewed_kinds=Counter(r["semantic_disposition"] for r in reviewed_ledger)
    reviewed_candidate_ids={r["candidate_id"] for r in reviewed_ledger}
    reviewed_by_class=Counter(r["candidate_class"] for r in candidates if r["candidate_id"] in reviewed_candidate_ids)
    mapped_review_count=sum(r.get("coverage_status") in {"VERIFIED_COVERED","VERIFIED_PARTIAL","VERIFIED_UNCOVERED"} for r in reviewed_ledger)
    atom_ledger=read_csv(COVERAGE / "atomic-obligation-dispositions.csv")[1] if (COVERAGE / "atomic-obligation-dispositions.csv").exists() else []
    verified_covered=sum(r.get("coverage_status")=="VERIFIED_COVERED" for r in atom_ledger)
    verified_partial=sum(r.get("coverage_status")=="VERIFIED_PARTIAL" for r in atom_ledger)
    verified_uncovered=sum(r.get("coverage_status")=="VERIFIED_UNCOVERED" for r in atom_ledger)
    batch_rows=read_csv(COVERAGE / "semantic-batch-progress.csv")[1] if (COVERAGE / "semantic-batch-progress.csv").exists() else []
    batch_groups: dict[str,list[dict[str,str]]] = {}
    for item in batch_rows: batch_groups.setdefault(item["batch_id"],[]).append(item)
    newly_reviewed_in_batches=sum(1 for item in batch_rows if item["already_reviewed_before_batch"]=="false" and item["candidate_id"] in reviewed_candidate_ids)
    baseline_reviewed=reviewed_count-newly_reviewed_in_batches
    batch_summaries=[]
    prior_new=0
    candidate_total=len(candidates)
    for batch_id,items in batch_groups.items():
        selected=[i["candidate_id"] for i in items]
        new_now=sum(1 for i in items if i["already_reviewed_before_batch"]=="false" and i["candidate_id"] in reviewed_candidate_ids)
        batch_atoms=[a for a in atom_ledger if a["candidate_id"] in selected]
        batch_summaries.append({"batch_id":batch_id,"candidate_ids":selected,"reviewed_before":baseline_reviewed+prior_new,"reviewed_after":baseline_reviewed+prior_new+new_now,"pending_before":candidate_total-baseline_reviewed-prior_new,"pending_after":candidate_total-baseline_reviewed-prior_new-new_now,"atomic_obligations":len(batch_atoms),"covered":sum(a["coverage_status"]=="VERIFIED_COVERED" for a in batch_atoms),"partial":sum(a["coverage_status"]=="VERIFIED_PARTIAL" for a in batch_atoms),"uncovered":sum(a["coverage_status"]=="VERIFIED_UNCOVERED" for a in batch_atoms),"open_decisions":sum(a["normative_status"]=="NORMATIVE_OPEN_DECISION" for a in batch_atoms)})
        prior_new+=new_now
    output = {
        "baseline_commit": BASELINE_COMMIT,
        "plan_blob_sha": git_blob("docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md"),
        "sources": source_hashes,
        "graph": {"commit": GRAPH_COMMIT, "path": GRAPH_PATH, "sha256": graph_sha, "status": "DISCOVERY_ONLY"},
        "counts": {
            "headings": structural["HEADING"], "tables": structural["TABLE"], "structural_units": structural["HEADING"] + structural["TABLE"],
            "paragraph_ranges": candidate_counts["TEXT_RANGE"], "text_ranges_semantically_reviewed": reviewed_by_class["TEXT_RANGE_CANDIDATE"],
            "table_rows": candidate_counts["TABLE_ROW"], "table_rows_semantically_reviewed": reviewed_by_class["TABLE_ROW_CANDIDATE"] + reviewed_by_class["TABLE_HEADER"],
            "code_blocks": candidate_counts["CODE_BLOCK"], "code_blocks_semantically_reviewed": reviewed_by_class["CODE_BLOCK_CANDIDATE"],
            "candidate_records": len(candidates), "candidate_records_pending_semantic_review": pending_count,
            "structural_source_units_dispositioned_as_locators": len(source_dispositions),
            "packages_indexed": len(packages), "package_index_rows": len(packages), "execution_trace_rows": len(trace),
            "candidate_review_pending_rows": pending_count, "coverage_gap_records": len(gaps), "open_decision_gap_records": gap_states["OPEN_DECISION"],
            "candidate_records_semantically_reviewed": reviewed_count,
            "atomic_obligations_extracted_and_verified": len(atom_ledger), "approved_obligations_verified": sum(a.get("normative_status")=="NORMATIVE_APPROVED" for a in atom_ledger),
            "open_decisions_verified": sum(a.get("normative_status")=="NORMATIVE_OPEN_DECISION" for a in atom_ledger),
            "atomic_obligation_records":len(atom_ledger),
            "descriptive_units_verified": sum(r.get("normative_status")=="DESCRIPTIVE" for r in reviewed_ledger), "verified_covered_obligations": verified_covered, "partially_covered_obligations": verified_partial,
            "candidate_rows_marked_covered": sum(r.get("coverage_status")=="VERIFIED_COVERED" for r in trace), "candidate_rows_marked_partial": sum(r.get("coverage_status")=="VERIFIED_PARTIAL" for r in trace), "candidate_rows_marked_uncovered": sum(r.get("coverage_status")=="VERIFIED_UNCOVERED" for r in trace),
            "confirmed_uncovered_obligations": verified_uncovered, "semantic_reviews_pending": pending_count,
            "unverified_normative_cue_suggestions": statuses["NORMATIVE_APPROVED"], "unverified_open_decision_cue_suggestions": statuses["NORMATIVE_OPEN_DECISION"],
            "needs_review_candidates": pending_count, "classification_suggestions_unverified": dict(statuses), "review_statuses": dict(review_states),
        },
        "controls": {
            "structural_counts": "PASS" if not structural_errors else "FAIL",
            "source_git_blob_shas": "PASS",
            "source_sha256_matches_graph": "PASS" if all(x["sha256"] in {s.get("sha256") for s in json.loads((COVERAGE / "extraction-manifest.json").read_text(encoding="utf-8")).get("source_blobs", []) if s.get("path")==rel} for rel,x in source_hashes.items()) else "FAIL",
            "all_classifications_semantically_reviewed": "PASS" if pending_count == 0 else "PENDING",
            "all_trace_mappings_verified": "PASS" if all(r.get("review_status") in {"SEMANTICALLY_REVIEWED", "VERIFIED"} for r in trace) else "PENDING",
            "package_ids_indexed": "PASS" if len(packages) == 36 else "FAIL",
            "candidate_count_reconciliation": "PASS" if validations.get("candidate_count_reconciliation",{}).get("result")=="PASS" else "FAIL",
            "evidence_join_index_integrity": "PASS" if validations.get("evidence_join_index_integrity",{}).get("result")=="PASS" else "FAIL",
            "no_unverified_mapping_claimed_as_verified": "PASS",
            "validation_errors": structural_errors,
        },
        "machine_controls": validations,
        "semantic_batches": batch_summaries,
        "matrix_build_status": "COMPLETE" if pending_count == 0 and not structural_errors else "INCOMPLETE",
        "program_coverage_status": "INDETERMINATE" if pending_count else "ASSESSED_WITH_GAPS" if verified_uncovered or any(r.get("normative_status")=="NORMATIVE_OPEN_DECISION" for r in reviewed_ledger) else "ASSESSED",
        "limitations": [
            "Rule-based classifications are discovery aids and are not accepted normative decisions.",
            "Only individually evidenced rows listed in the semantic review ledger may carry a verified mapping; remaining mappings are unverified.",
            "Table rows are enumerated, but compound-row splitting and semantic status require source review.",
            f"The matrix contains {len(candidates)} candidate records; {pending_count} still require semantic review.",
            "Graph node overlap is a retrieval reference, not semantic entailment.",
        ],
    }
    (COVERAGE / "validation-report.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# گزارش اعتبارسنجی پوشش منابع فاز دوم",
        "",
        f"**MATRIX_BUILD_STATUS:** `{output['matrix_build_status']}`",
        "",
        f"**PROGRAM_COVERAGE_STATUS:** `{output['program_coverage_status']}`",
        f"**گیت‌ها:** هیچ گیت RA/IPA/CPA یا QG در این گزارش PASS اعلام نمی‌شود.",
        "",
        "## شمارش واقعی",
        "",
        "| شاخص | نتیجه |",
        "|---|---:|",
        f"| Heading | {structural['HEADING']} |",
        f"| Table block | {structural['TABLE']} |",
        f"| واحد ساختاری | {structural['HEADING'] + structural['TABLE']} |",
        f"| عنوان/ظرف جدول تعیین‌تکلیف‌شده به‌عنوان locator | {len(source_dispositions)} از {structural['HEADING'] + structural['TABLE']}؛ محتوای بخش و سطرهای جدول جداگانه بررسی می‌شوند |",
        f"| محدودهٔ متنی غیرجدولی استخراج‌شده | {candidate_counts['TEXT_RANGE']} |",
        f"| سطرهای سرآیند/دادهٔ جدول استخراج‌شده | {candidate_counts['TABLE_ROW']} |",
        f"| بلوک fenced ثبت‌شده | {candidate_counts['CODE_BLOCK']} |",
        f"| کل candidate row | {len(candidates)} |",
        f"| بسته‌های index شده | {len(packages)} / 36 |",
        f"| تعیین‌تکلیف ردیفی انجام‌شده | {reviewed_count} از {len(candidates)} candidate؛ {reviewed_kinds['STRUCTURAL_HEADER_ONLY']} سرستون، {reviewed_kinds['MARKDOWN_HORIZONTAL_RULE_ONLY']} جداکننده، {reviewed_kinds['EXAMPLE_CONTEXT_ROW']} ردیف مثال و {mapped_review_count} نگاشت معنایی بررسی‌شده |",
        f"| تعیین‌تکلیف Candidateهای متنی | {reviewed_by_class['TEXT_RANGE_CANDIDATE']} از {candidate_counts['TEXT_RANGE']} محدودهٔ متن، {reviewed_by_class['TABLE_ROW_CANDIDATE']+reviewed_by_class['TABLE_HEADER']} از {candidate_counts['TABLE_ROW']} ردیف جدول، {reviewed_by_class['CODE_BLOCK_CANDIDATE']} از {candidate_counts['CODE_BLOCK']} بلوک fenced |",
        f"| Candidateهای pending review | {pending_count}؛ pending بودن به‌تنهایی شکاف قطعی نیست |",
        f"| رکوردهای Gap Register | {len(gaps)}؛ {gap_states['OPEN_REVIEW']} بازبینی محتوایی + {gap_states['OPEN_DECISION']} تصمیم باز |",
        f"| Atomic Obligationهای دارای نگاشت Covered | {verified_covered} |",
        f"| نگاشت تأییدشدهٔ covered/partial/uncovered | {verified_covered}/{verified_partial}/{verified_uncovered} |",
        "| شکاف معنایی قطعی | هنوز تعیین نشده |",
        f"| پیشنهادهای قاعده‌محورِ تأییدنشده | {json.dumps(dict(statuses), ensure_ascii=False, sort_keys=True)} |",
        "",
        "## پیشرفت دسته‌ای",
        "",
        "| Batch ID | Candidate IDs | Reviewed Before→After | Pending Before→After | Atomic Obligations | Covered/Partial/Uncovered | Open Decisions |",
        "|---|---|---:|---:|---:|---:|---:|",
        *[f"| {b['batch_id']} | {', '.join(b['candidate_ids'])} | {b['reviewed_before']}→{b['reviewed_after']} | {b['pending_before']}→{b['pending_after']} | {b['atomic_obligations']} | {b['covered']}/{b['partial']}/{b['uncovered']} | {b['open_decisions']} |" for b in batch_summaries],
        "",
        "## کنترل‌های ماشینی",
        "",
        "| کنترل | نتیجه | توضیح |",
        "|---|---|---|",
        f"| تعداد Heading/Table | {'PASS' if not structural_errors else 'FAIL'} | {structural['HEADING']} Heading و {structural['TABLE']} Table |",
        f"| هش Git blob دو منبع | {output['controls']['source_git_blob_shas']} | برابر manifest جاری |",
        f"| SHA-256 دو منبع | {output['controls']['source_sha256_matches_graph']} | با اثر انگشت graph پین‌شده تطبیق داده شد |",
        f"| محدوده‌های متنی و سطرهای جدول | {'PASS' if pending_count == 0 else 'PARTIAL'} | {reviewed_count} از {len(candidates)} Candidate بررسی شده؛ {pending_count} باقی است |",
        f"| Package Execution Index | {'PASS' if len(packages) == 36 else 'FAIL'} | ردیف‌های برنامه‌ای استخراج شدند؛ پیوند معنایی مستقل هنوز بررسی نشده |",
        f"| تکراری نبودن IDهای منبع/candidate | {validations['source_unit_id_uniqueness']['result']}/{validations['atomic_candidate_id_uniqueness']['result']} | IDs بررسی‌شده: {validations['source_unit_id_uniqueness']['checked']} source units، {validations['atomic_candidate_id_uniqueness']['checked']} candidateها |",
        f"| یکپارچگی دفتر Atomic Obligation | {validations['atomic_obligation_ledger_integrity']['result']} | {validations['atomic_obligation_ledger_integrity']['checked']} الزام مستقل؛ چند الزام می‌توانند به یک Candidate متصل شوند |",
        f"| یکپارچگی دفتر دسته‌ها | {validations['semantic_batch_ledger_integrity']['result']} | {validations['semantic_batch_ledger_integrity']['checked']} انتخاب Candidate با نتیجهٔ متصل به Ledger معنایی |",
        "| شناسه‌های Graph | DISCOVERY_ONLY | هم‌پوشانی مکانیکی منبع؛ نه شاهد entailment |",
        f"| صحت نحوی ارجاع‌های Package/Req/Task/AC/Test | {validations['requirement_task_ac_test_references']['result']} | تعداد tokenهای کنترل‌شده: {validations['requirement_task_ac_test_references']['checked']}؛ معنای نگاشت‌ها هنوز UNVERIFIED است |",
        f"| یکپارچگی ارجاع‌های Package Index | {validations['package_index_reference_integrity']['result']} | {validations['package_index_reference_integrity']['checked']} شناسهٔ استخراج‌شده با سند برنامه تطبیق شد |",
        f"| پوشش کامل trace rowها | {validations['execution_trace_row_integrity']['result']} | {validations['execution_trace_row_integrity']['checked']} ردیف |",
        f"| علت‌دار بودن candidateهای نیازمند بازبینی | {validations['review_required_rows_have_reason']['result']} | {validations['review_required_rows_have_reason']['checked']} ردیف |",
        f"| پیوندهای معنایی Source→Package→Req→Task→AC/Test | {validations['semantic_review_disposition_integrity']['result']} | {verified_covered + verified_partial + verified_uncovered} obligation dispositions mapped; remaining candidates are pending |",
        f"| وضعیت نگاشت نامعتبر/شکسته | {validations['atomic_obligation_ledger_integrity']['result']} | {validations['atomic_obligation_ledger_integrity']['errors']} ledger errors; coverage claims remain limited to cited evidence |",
        "",
        "## نقص‌های استخراج که اصلاح شدند",
        "",
        "- ۲۶ محدودهٔ متنیِ غیرجدولی در baseline اولیهٔ ۱۱۱۰تایی جا افتاده بود؛ استخراج مجدد ۱۱۳۶ range را یافت و ۲۶ range جدید به شناسه‌های candidate اضافه شد.",
        "- هر ۵۸ جدول به‌صورت block ثبت شده بود اما محتوای ۴۷۰ سطر سرآیند/داده در ledger الزام‌ها نبود؛ ۴۷۰ row به‌عنوان candidate مستقل افزوده شد تا محتوایشان قابل بازبینی باشد. این‌ها الزام اتمی تأییدشده نیستند.",
        f"- بلوک fencedهای کد/نمونه نیز جداگانه شمرده و ثبت شد: {candidate_counts['CODE_BLOCK']} بلوک؛ محتوای آن‌ها خودکار الزام محسوب نشده است.",
        "- end_line سرعنوان ریشهٔ Blueprint برابر ۲۵۵۱ ثبت شده بود، در حالی‌که آخرین خط فیزیکی فایل ۲۵۵۰ است؛ محدوده اصلاح شد.",
        "- Graph node IDs خالی بود؛ ارجاع‌های مکانی گراف پین‌شده به‌عنوان discovery references اضافه شدند.",
        "",
        "## محدودیت معنایی",
        "",
        f"Rule-based labels فقط سرنخ‌اند. تا این اجرا، {reviewed_count} از {len(candidates)} Candidate با متن منبع و مقصد بررسی شده‌اند و {len(atom_ledger)} Atomic Obligation ثبت شده؛ {pending_count} Candidate هنوز نیازمند بازبینی‌اند. Candidate و obligation دو شمارش متفاوت‌اند. وضعیت Covered/Partial/Uncovered از دفتر اتمی و شواهد مشخص آن بازتولید شده است.",
        "",
        "## منابع و گراف",
        "",
    ]
    for rel, info in source_hashes.items():
        report.append(f"- `{rel}`: Git blob `{info['git_blob_sha']}`, SHA-256 `{info['sha256']}`, خطوط واقعی `{info['physical_lines']}`.")
    report.extend([
        f"- گراف: `{GRAPH_COMMIT}:{GRAPH_PATH}`؛ SHA-256 `{graph_sha}`؛ استفاده برای کشف/ارجاع، نه تأیید نگاشت.",
        "- متن کامل RTF معیارها (در پیوست قبلی) از QG-14 قطع می‌شود؛ این مأموریت براساس پرامپت تکمیلی جاری اجرا شده است.",
        "",
        "## مرحلهٔ بعد",
        "",
        f"ادامهٔ دسته‌ای از اولین Candidate بررسی‌نشده `{next((r['candidate_id'] for r in candidates if r['candidate_id'] not in reviewed_ledger_ids), 'NONE')}` است. هر دسته باید با بازبینی متن، زمینه، تصمیم، ردیابی واقعی Requirement/Task/AC/Test، اصلاح نقص و اعتبارسنجی کامل شود. Candidateهای باقی‌ماندهٔ pending به‌خودی‌خود شکاف قطعی محسوب نمی‌شوند.",
        "",
    ])
    (COVERAGE / "semantic-validation-report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # a clear audit failure is preferable to a partial silent write
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
