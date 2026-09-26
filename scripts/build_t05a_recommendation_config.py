"""Materialize approved source weights and one-to-one coefficients without UI inference.

The numerical column in the question-variable mapping source is deliberately not
read. D-005 makes the answer-conversion table authoritative for weights. The
separate one-to-one matrix supplies category compatibility coefficients.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = ROOT / ".agents" / "documents"
WEIGHTS = DOCUMENTS / "تبدیل پاسخ‌ها به وزن‌های عددی.unitext"
COEFFICIENTS = (
    DOCUMENTS / "ضرایب تناسب یک به یک گزینه‌های هر یک از سئوالاتسناریوها با هریک از دسته بندی‌ها متغیرهای وام.unitext"
)
WEIGHTS_SHA = "f786ff278f58a5abb998dafca46625cbf3da5922db1e5c68d505487b57133749"
COEFFICIENTS_SHA = "65859d3de5addef6c164c263100e0fc672897e1518a7b05091ec7b91dbfdcf56"
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
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def _rows(path: Path) -> list[list[str]]:
    with path.open(encoding="utf-16", newline="") as source:
        return list(csv.reader(source, delimiter="\t"))


def _number(text: str) -> Decimal:
    result = Decimal(text.translate(DIGITS).replace("/", ".").strip())
    if not Decimal("0") <= result <= Decimal("1"):
        raise ValueError("coefficient outside [0,1]")
    return result


def _question(text: str) -> str | None:
    normalized = text.translate(DIGITS)
    match = re.search(r"(?:پرسش|سناریو)\s*(\d+)", normalized)
    if not match:
        return None
    return ("S" if "سناریو" in normalized else "Q") + str(int(match.group(1)))


def _verify_source(path: Path, expected: str) -> None:
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"verified source changed: {path.name}")


def build_config() -> dict:
    _verify_source(WEIGHTS, WEIGHTS_SHA)
    _verify_source(COEFFICIENTS, COEFFICIENTS_SHA)
    decision = json.loads((ROOT / "data/contracts/recommendation-data-decisions.v1.json").read_text(encoding="utf-8"))
    if not decision["approved"] or decision["weightSourcePolicy"]["authoritativeSha256"] != WEIGHTS_SHA:
        raise ValueError("D-005 approved source is unavailable")
    identifiers = json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text(encoding="utf-8"))
    questions = json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text(encoding="utf-8"))
    answers = {q["questionId"]: [a["answerId"] for a in q["answerOptions"]] for q in questions["questions"]}
    category_ids = identifiers["categoryIds"]
    weights: dict[tuple[str, str], dict] = {}
    active_variable = None
    active_key = None
    for line, row in enumerate(_rows(WEIGHTS), 1):
        cells = row + [""] * max(0, 5 - len(row))
        active_variable = VARIABLES.get(cells[0].strip(), active_variable)
        q = _question(cells[2])
        if q:
            if active_variable not in category_ids or q not in answers:
                raise ValueError(f"unknown variable/question at weight source row {line}")
            active_key = (active_variable, q)
            if active_key in weights:
                raise ValueError(f"duplicate weight group at source row {line}")
            weights[active_key] = {
                "variableId": active_variable,
                "questionId": q,
                "questionWeight": str(_number(cells[1])),
                "sourceRow": line,
                "answers": [],
            }
        if active_key and cells[3].strip():
            group = weights[active_key]
            ordinal = len(group["answers"])
            if ordinal >= len(answers[active_key[1]]):
                raise ValueError(f"too many answer weights at source row {line}")
            group["answers"].append(
                {
                    "answerId": answers[active_key[1]][ordinal],
                    "sourceWeightedValue": str(_number(cells[4])),
                    "sourceRow": line,
                }
            )
    if len(weights) != 30 or any(len(group["answers"]) != 5 for group in weights.values()):
        raise ValueError("answer conversion does not cover exactly 30 five-answer groups")
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for group in weights.values():
        totals[group["variableId"]] += Decimal(group["questionWeight"])
    if set(totals) != set(category_ids) or any(total != 1 for total in totals.values()):
        raise ValueError("authoritative question weights do not sum to one for every variable")

    matrix = _rows(COEFFICIENTS)
    compatibilities = []
    active_variable = None
    category_ordinal = 0
    header: list[tuple[int, str]] = []
    for line, row in enumerate(matrix, 1):
        cells = row + [""] * max(0, 2 - len(row))
        if cells[0].strip():
            active_variable = VARIABLES.get(cells[0].strip())
            if active_variable is None:
                raise ValueError(f"unknown category variable at source row {line}")
            category_ordinal = 0
        if cells[1].strip() and active_variable:
            categories = category_ids[active_variable]
            if category_ordinal >= len(categories):
                raise ValueError(f"too many categories for {active_variable}")
            category_id = categories[category_ordinal]
            category_ordinal += 1
            expected_groups = {q for variable, q in weights if variable == active_variable}
            if {q for _, q in header} != expected_groups:
                raise ValueError(f"matrix question set disagrees with D-005 groups at row {line}")
            for start, q in header:
                for ordinal, answer_id in enumerate(answers[q]):
                    if start + ordinal >= len(row):
                        raise ValueError(f"missing compatibility cell at row {line}")
                    compatibilities.append(
                        {
                            "variableId": active_variable,
                            "categoryId": category_id,
                            "questionId": q,
                            "answerId": answer_id,
                            "coefficient": str(_number(row[start + ordinal])),
                            "sourceRow": line,
                            "sourceColumn": start + ordinal + 1,
                        }
                    )
        elif not cells[0].strip() and not cells[1].strip():
            proposed = [(index, q) for index, cell in enumerate(row) if index >= 2 and (q := _question(cell))]
            if proposed:
                header = proposed
    expected_count = sum(
        len(ids) * sum(variable == name for variable, _ in weights) * 5 for name, ids in category_ids.items()
    )
    if (
        len(compatibilities) != expected_count
        or len({(x["categoryId"], x["answerId"]) for x in compatibilities}) != expected_count
    ):
        raise ValueError("one-to-one coefficients have missing or duplicate cells")
    return {
        "schemaVersion": "1.0.0",
        "configVersion": decision["configVersion"],
        "approved": True,
        "decisionIds": ["D-001", "D-002", "D-003", "D-004", "D-005"],
        "sources": {"answerWeightsSha256": WEIGHTS_SHA, "compatibilitySha256": COEFFICIENTS_SHA},
        "questionWeights": sorted(weights.values(), key=lambda x: (x["variableId"], x["questionId"])),
        "compatibilities": compatibilities,
    }


if __name__ == "__main__":
    print(json.dumps(build_config(), ensure_ascii=False, indent=2))
