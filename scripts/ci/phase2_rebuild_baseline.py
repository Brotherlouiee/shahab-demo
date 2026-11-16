#!/usr/bin/env python3
"""Reproducible, non-semantic SHA/line/table/diagram baseline for SHAHAB Phase 2.

This script DOES NOT approve requirements.  Every row remains NOT_EXAMINED
until a reviewer verifies its atomic obligations against the source.
Usage:
    python scripts/ci/phase2_rebuild_baseline.py --out /tmp/shahab-phase2-audit
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SOURCES = {
    "B": {
        "path": "docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md",
        "blob": "9681c2bf6c3149317c3788516748084cfb6eac7c",
        "nonempty": 1842,
        "lines": 2551,
    },
    "W": {
        "path": "docs/SHAHAB_DIGITAL_WALLET.md",
        "blob": "1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a",
        "nonempty": 964,
        "lines": 1780,
    },
}


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def provisional_role(text: str, fence: str | None, historical: bool) -> str:
    line = text.strip()
    if line.startswith("#"):
        return "STRUCTURAL_CANDIDATE"
    if line.startswith(chr(96) * 3):
        return "CODE_FENCE"
    if fence == "mermaid":
        return "DIAGRAM_CANDIDATE"
    if fence:
        return "CODE_OR_DIAGRAM_CANDIDATE"
    if line.startswith("|"):
        if re.match(r"^\|[\s:|\-]+\|?$", line):
            return "TABLE_SEPARATOR"
        return "TABLE_CELL_GROUP_CANDIDATE"
    if historical:
        return "HISTORICAL_CANDIDATE"
    if re.search(r"^(?:[-*]\s+)?(?:\*\*)?(?:مثال|منبع|پیوست|یادداشت)", line):
        return "EXAMPLE_OR_REFERENCE_CANDIDATE"
    if re.search(r"تصمیم[‌ ]باز|غیرمصوب|در انتظار تصویب|پیشنهادی", line):
        return "OPEN_OR_PROPOSAL_CANDIDATE"
    if re.search(r"پاسخ مصوب|تصمیم تأییدشده|الزام|باید|ممنوع|مجاز|فقط|قاعده", line):
        return "NORMATIVE_CANDIDATE"
    return "UNCLASSIFIED_REVIEW_REQUIRED"


def collect(repo: Path) -> tuple[dict, list[dict]]:
    summaries: dict = {}
    registry: list[dict] = []
    for key, spec in SOURCES.items():
        data = (repo / spec["path"]).read_bytes()
        sha = blob_sha(data)
        if sha != spec["blob"]:
            raise ValueError(f"Canonical source {key} changed: {sha} != {spec['blob']}")
        lines = data.decode("utf-8").split("\n")
        count = sum(bool(line.strip()) for line in lines)
        if count != spec["nonempty"] or len(lines) != spec["lines"]:
            raise ValueError(f"Baseline dimensions changed for {key}: {len(lines)}/{count}")
        headers = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0}
        table_groups = 0
        mermaid = 0
        fence: str | None = None
        table_active = False
        historical = False
        section = ""
        for n, text in enumerate(lines, 1):
            stripped = text.strip()
            heading = re.match(r"^(#{1,6})\s+(.+)$", text)
            if heading:
                headers[str(len(heading.group(1)))] += 1
                section = heading.group(2)
                if any(token in section for token in ("تاریخچه تغییر", "یادداشت تغییر", "تاریخچه اصلاح")):
                    historical = True
                elif heading.group(1) == "##":
                    historical = False
            is_table = stripped.startswith("|")
            if is_table and not table_active:
                table_groups += 1
            table_active = is_table
            if stripped.startswith(chr(96) * 3):
                if fence is None:
                    fence = stripped[3:].strip() or "plain"
                    if fence == "mermaid":
                        mermaid += 1
                    role = "CODE_FENCE"
                else:
                    role = "CODE_FENCE"
                    fence = None
            else:
                role = provisional_role(text, fence, historical)
            if not stripped:
                continue
            registry.append({
                "ref": f"{key}:{n}",
                "text": text,
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "section": section,
                "provisional_role": role,
                "semantic_class": None,
                "review_status": "NOT_EXAMINED",
                "atoms": [],
                "review_evidence": None,
            })
        summaries[key] = {
            "path": spec["path"], "git_blob_sha": sha,
            "physical_lines_split_newline": len(lines),
            "nonempty_line_units": count, "headings_by_level": headers,
            "table_groups": table_groups,
            "mermaid_diagrams": mermaid,
        }
    return summaries, registry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary, rows = collect(args.repo)
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "SHAHAB-PHASE2-REBUILD-G1-v1",
        "method": "UTF-8 split on newline; every nonempty line retained including tables/code/diagrams",
        "sources": summary,
        "total_line_units": len(rows),
        "semantic_status": "NOT_VERIFIED",
        "atomic_count": None,
        "historical_claim_5258": "UNREPRODUCED",
    }
    if len(rows) != 2806:
        raise ValueError(f"Expected 2806 source lines, got {len(rows)}")
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.out / "source_lines.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows),
        encoding="utf-8",
    )
    print(json.dumps({"line_units": len(rows), "sources": summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
