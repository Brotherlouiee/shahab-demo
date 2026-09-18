"""Audit byte-verified UTF-16 canonical sources without transforming business data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


@dataclass(frozen=True)
class SourceSpec:
    raw_name: str
    repository_path: str
    role: str


SOURCES = (
    SourceSpec("پرسشنامه سنجش متغیرهای رفتاری.txt", ".agents/documents/پرسشنامه سنجش متغیرهای رفتاری.unitext", "questionnaire"),
    SourceSpec("ماتریس گزینه های متغیرهای وام.txt", ".agents/documents/ماتریس گزینه های متغیرهای وام.unitext", "loan_categories"),
    SourceSpec("ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام.txt", ".agents/documents/ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام.unitext", "question_variable_weights"),
    SourceSpec("تبدیل پاسخ‌ها به وزن‌های عددی.txt", ".agents/documents/تبدیل پاسخ‌ها به وزن‌های عددی.unitext", "answer_weights"),
    SourceSpec("ضرایب تناسب یک به یک گزینه‌های هر یک از سئوالاتسناریوها با هریک از دسته بندی‌ها متغیرهای وام.txt", ".agents/documents/ضرایب تناسب یک به یک گزینه‌های هر یک از سئوالاتسناریوها با هریک از دسته بندی‌ها متغیرهای وام.unitext", "compatibility_coefficients"),
    SourceSpec("دیتابیس وام های بانکی.txt", ".agents/documents/دیتابیس وام های بانکی.unitext", "loan_database"),
)

PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
EXPECTED_QUESTION_ROWS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13]
EXPECTED_CATEGORY_COUNTS = {
    "حداکثر مبلغ": 8, "مبلغ قسط": 6, "حداکثر زمان بازپرداخت": 6, "نرخ سود": 5,
    "نیاز به سپرده": 2, "مدت زمان خواب سپرده": 5, "نسبت مبلغ وام به میزان سپرده": 4, "نوع ضمانت": 3,
}
VARIABLE_ALIASES = {"نرخ سود وام": "نرخ سود"}
CORE_LOAN_COLUMNS = ("نرخ سود وام", "حداکثر مبلغ", "مبلغ قسط", "حداکثر زمان بازپرداخت")
NEUTRAL_LOAN_COLUMNS = ("نیاز به سپرده", "مدت زمان خواب سپرده", "نسبت مبلغ وام به میزان سپرده")


def read_source(path: Path) -> tuple[bytes, str, list[list[str]]]:
    raw = path.read_bytes()
    text = raw.decode("utf-16")
    rows = list(csv.reader(text.lstrip("\ufeff").splitlines(), delimiter="\t"))
    return raw, text, rows


def decimal_token(value: str) -> Decimal | None:
    token = value.strip().translate(PERSIAN_DIGITS).replace("٫", ".")
    if not token:
        return None
    if re.fullmatch(r"\d+/\d{1,2}", token):
        token = token.replace("/", ".")
    try:
        return Decimal(token)
    except InvalidOperation:
        return None


def cells(row: list[str], size: int = 3) -> list[str]:
    return (row + [""] * max(0, size - len(row)))[:size]


def audit_questionnaire(rows: list[list[str]]) -> dict:
    active = None
    options: dict[int, int] = defaultdict(int)
    duplicates: list[int] = []
    seen: set[int] = set()
    for row in rows[1:]:
        number, _, option = cells(row)
        if number.strip().isdigit():
            active = int(number.strip())
            if active in seen:
                duplicates.append(active)
            seen.add(active)
        if active is not None and option.strip():
            options[active] += 1
    return {"questionRows": sorted(options), "optionCounts": dict(options), "duplicates": duplicates,
            "missingExpectedRows": [item for item in EXPECTED_QUESTION_ROWS if item not in options],
            "wrongOptionCounts": {str(k): v for k, v in options.items() if v != 5}}


def audit_categories(rows: list[list[str]]) -> dict:
    active = None
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        variable, category, _ = cells(row)
        if variable.strip():
            active = variable.strip()
        if active and category.strip():
            counts[active] += 1
    return {"categoryCounts": dict(counts), "missingVariables": [name for name in EXPECTED_CATEGORY_COUNTS if name not in counts],
            "wrongCounts": {name: counts.get(name, 0) for name, expected in EXPECTED_CATEGORY_COUNTS.items() if counts.get(name, 0) != expected}}


def audit_mapping(rows: list[list[str]]) -> dict:
    active = None
    totals: dict[str, Decimal] = defaultdict(Decimal)
    invalid: list[dict] = []
    coverage: dict[str, int] = defaultdict(int)
    for row_number, row in enumerate(rows[1:], start=2):
        variable, question, weight = cells(row)
        if variable.strip():
            active = VARIABLE_ALIASES.get(variable.strip(), variable.strip())
        if not active or not question.strip():
            continue
        parsed = decimal_token(weight)
        if parsed is None or not Decimal("0") <= parsed <= Decimal("1"):
            invalid.append({"row": row_number, "variable": active, "rawWeight": weight})
            continue
        totals[active] += parsed
        coverage[active] += 1
    return {"weightTotals": {key: str(value) for key, value in totals.items()}, "mappingRows": dict(coverage),
            "invalidWeights": invalid, "missingVariables": [name for name in EXPECTED_CATEGORY_COUNTS if name not in totals],
            "nonUnitTotals": {key: str(value) for key, value in totals.items() if value != Decimal("1")}}


def audit_numeric_cells(rows: list[list[str]]) -> dict:
    values: list[Decimal] = []
    invalid: list[dict] = []
    for row_number, row in enumerate(rows, start=1):
        for column, cell in enumerate(row, start=1):
            token = cell.strip()
            if not token:
                continue
            parsed = decimal_token(token)
            if parsed is not None:
                values.append(parsed)
                if not Decimal("0") <= parsed <= Decimal("1"):
                    invalid.append({"row": row_number, "column": column, "value": token})
    return {"numericCellCount": len(values), "minimum": str(min(values)) if values else None,
            "maximum": str(max(values)) if values else None, "outOfRange": invalid}


def audit_loan_database(rows: list[list[str]]) -> dict:
    header = rows[0]
    header_positions = {value.strip(): index for index, value in enumerate(header) if value.strip()}
    loan_rows = [row for row in rows[1:] if row and row[0].strip()]
    unknown = {column: Counter() for column in (*CORE_LOAN_COLUMNS, *NEUTRAL_LOAN_COLUMNS)}
    for row in loan_rows:
        for column in unknown:
            index = header_positions.get(column)
            value = row[index].strip() if index is not None and index < len(row) else ""
            if value in {"نامشخص", "متغیر", ""}:
                unknown[column][value or "blank"] += 1
    duplicate_names = [name for name, count in Counter(row[0].strip() for row in loan_rows).items() if count > 1]
    return {"headerCount": len(header), "nonEmptyHeaderCount": len(header_positions), "emptyHeaderCount": len(header) - len(header_positions),
            "loanRowCount": len(loan_rows), "duplicateLoanNames": duplicate_names,
            "unknownCounts": {column: dict(counter) for column, counter in unknown.items()}}


def build_report(source_dir: Path) -> dict:
    source_data: dict[str, list[list[str]]] = {}
    provenance = []
    for spec in SOURCES:
        path = source_dir / spec.raw_name
        raw, _, rows = read_source(path)
        source_data[spec.role] = rows
        provenance.append({"role": spec.role, "repositoryPath": spec.repository_path, "inputPath": str(path),
                           "encoding": "UTF-16LE", "sha256": hashlib.sha256(raw).hexdigest(), "byteCount": len(raw), "rowCount": len(rows)})
    mapping = audit_mapping(source_data["question_variable_weights"])
    report = {
        "auditVersion": "1.0.0", "mode": "read_only", "provenance": provenance,
        "questionnaire": audit_questionnaire(source_data["questionnaire"]),
        "loanCategories": audit_categories(source_data["loan_categories"]),
        "questionVariableMapping": mapping,
        "answerWeightCells": audit_numeric_cells(source_data["answer_weights"]),
        "compatibilityCoefficientCells": audit_numeric_cells(source_data["compatibility_coefficients"]),
        "loanDatabase": audit_loan_database(source_data["loan_database"]),
        "issues": [],
    }
    if report["loanDatabase"]["emptyHeaderCount"]:
        report["issues"].append({"severity": "info", "code": "LOAN_DB_EMPTY_HEADERS", "message": "Trailing loan database headers are empty; importer must ignore only proven-empty columns."})
    for column in CORE_LOAN_COLUMNS:
        if report["loanDatabase"]["unknownCounts"][column]:
            report["issues"].append({"severity": "blocking", "code": "CORE_LOAN_VALUE_UNKNOWN", "column": column,
                                      "message": "Core values need the versioned extraction/exclusion decision required by the canonical guide."})
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(args.source_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"loanRows": report["loanDatabase"]["loanRowCount"], "issues": len(report["issues"]), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
