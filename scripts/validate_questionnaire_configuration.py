"""Validate that questionnaire configuration remains exact to its verified source.

This is a build-time integrity gate. It never modifies a source or config file;
changing wording/options requires an intentional versioned artifact update after
the source-hash review described in the canonical development guide.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from backend.app.questionnaire.domain.configuration import load_questionnaire_configuration

ROOT = Path(__file__).parents[1]
CONFIG_PATH = ROOT / "data/contracts/questionnaire-configuration.v1.json"
IDENTIFIERS_PATH = ROOT / "data/contracts/canonical-identifiers.v1.json"
SOURCE_PATH = ROOT / ".agents/documents/پرسشنامه سنجش متغیرهای رفتاری.unitext"
SOURCE_SHA256 = "8db132f2147b79f659f51b61754f0d97f0c4ba90c312ae4cca2948770a83accd"


def source_questions() -> list[tuple[int, str, list[str]]]:
    """Read the trusted UTF-16LE source without inventing or reordering wording."""

    rows = csv.reader(SOURCE_PATH.open(encoding="utf-16"), delimiter="\t")
    extracted: list[tuple[int, str, list[str]]] = []
    current: tuple[int, str, list[str]] | None = None
    for row in rows:
        if len(row) < 3:
            continue
        source_number, prompt, option = (value.strip() for value in row[:3])
        if source_number.isdecimal():
            current = (int(source_number), prompt, [])
            extracted.append(current)
        if current is None or not option:
            continue
        current[2].append(option)
    return extracted


def main() -> None:
    identifiers = json.loads(IDENTIFIERS_PATH.read_text(encoding="utf-8"))
    configuration = load_questionnaire_configuration(CONFIG_PATH, identifiers)
    if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise SystemExit("questionnaire source hash differs from the verified artifact")

    expected = source_questions()
    actual = list(configuration.questions)
    if len(actual) != len(expected):
        raise SystemExit("questionnaire configuration does not cover every source question")
    for configured, (source_number, prompt, options) in zip(actual, expected, strict=True):
        if configured.source_question_number != source_number or configured.prompt != prompt:
            raise SystemExit(f"source wording differs for {configured.question_id}")
        if [option.label for option in configured.answer_options] != options:
            raise SystemExit(f"source options differ for {configured.question_id}")
    print("questionnaire configuration validation passed")


if __name__ == "__main__":
    main()
