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
                for