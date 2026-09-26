"""Compare question-to-variable weights across the two verified official matrices.

This read-only audit reports source coordinates. It never selects a preferred
weight or changes the approval status of a recommendation configuration.
"""

from __future__ import annotations

import csv
import json
import re
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / ".agents" / "documents"
MAPPING = SOURCE_DIR / "ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام.unitext"
ANSWER_WEIGHTS = SOURCE_DIR / "تبدیل پاسخ‌ها به وزن‌های عددی.unitext"
VARIABLES = {
    "حداکثر مبلغ": "maxAmount",
    "مبلغ قسط": "monthlyInstallment",
    "حداکثر زمان بازپرداخت": "maxRepaymentMonths",
    "نرخ سود وام": "interestRate",
    "نرخ سود": "interestRate",
    "نیاز به سپرده": "depositRequired",
    "مدت زمان خواب سپرده": "depositHoldingMonths",
    "نسبت مبلغ وام به میزان سپرده": "loanToDepositRatio",
    "نوع ضمانت": "guaranteeType",
}
TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def rows(path: Path):
    with path.open(encoding="utf-16", newline="") as source:
        yield from enumerate(csv.reader(source, delimiter="\t"), 1)


def decimal(value: str) -> Decimal:
    return Decimal(value.translate(TRANSLATION).replace("/", ".").strip())


def question(value: str) -> str | None:
    match = re.search(r"(?:پرسش|سناریو)\s*(\d+)", value.translate(TRANSLATION))
    if not match:
        return None
    number = int(match.group(1))
    return ("S" if "سناریو" in value else "Q") + str(number)


def weights(path: Path, *, mapping: bool) -> dict[tuple[str, str], tuple[Decimal, int]]:
    result = {}
    variable = None
    for row_number, row in rows(path):
        cells = row + [""] * (4 - len(row))
        variable = VARIABLES.get(cells[0].strip(), variable)
        if not variable:
            continue
        q = question(cells[1 if mapping else 2])
        if not q:
            continue
        value = cells[2 if mapping else 1].strip()
        if not value:
            continue
        key = (variable, q)
        if key in result:
            raise ValueError(f"duplicate {key} in {path}:{row_number}")
        result[key] = (decimal(value), row_number)
    return result


def build_report() -> dict:
    left = weights(MAPPING, mapping=True)
    right = weights(ANSWER_WEIGHTS, mapping=False)
    conflicts = []
    for variable, q in sorted(left.keys() | right.keys()):
        a, b = left.get((variable, q)), right.get((variable, q))
        if a is None or b is None or a[0] != b[0]:
            conflicts.append(
                {
                    "variableId": variable,
                    "questionId": q,
                    "mapping": None if a is None else {"weight": str(a[0]), "row": a[1]},
                    "answerWeights": None if b is None else {"weight": str(b[0]), "row": b[1]},
                }
            )
    return {
        "sourcePaths": [str(MAPPING.relative_to(ROOT)), str(ANSWER_WEIGHTS.relative_to(ROOT))],
        "authoritativeWeightSource": str(ANSWER_WEIGHTS.relative_to(ROOT)),
        "ignoredNumericSource": str(MAPPING.relative_to(ROOT)),
        "comparedPairs": len(left.keys() | right.keys()),
        "nonAuthoritativeDifferences": conflicts,
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), ensure_ascii=False, indent=2))
