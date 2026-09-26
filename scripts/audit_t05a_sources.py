"""Read-only audit of the verified loan source before any database backfill.

This report is source evidence, not a publication manifest. An existing database
must be inspected separately; this command never asserts that it is empty.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from backend.app.data_pipeline.domain.normalization import NormalizationState, normalize_variable

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents" / "documents" / "دیتابیس وام های بانکی.unitext"
COLUMNS = {
    "maxAmount": "حداکثر مبلغ",
    "monthlyInstallment": "مبلغ قسط",
    "maxRepaymentMonths": "حداکثر زمان بازپرداخت",
    "interestRate": "نرخ سود وام",
    "depositRequired": "نیاز به سپرده",
    "depositHoldingMonths": "مدت زمان خواب سپرده",
    "loanToDepositRatio": "نسبت مبلغ وام به میزان سپرده",
    "guaranteeType": "نوع ضمانت",
}
CORE = frozenset({"maxAmount", "monthlyInstallment", "maxRepaymentMonths", "interestRate"})


def build_report() -> dict:
    raw = SOURCE.read_bytes()
    with SOURCE.open(encoding="utf-16", newline="") as source:
        records = list(csv.DictReader(source, delimiter="\t"))
    records = [(index, row) for index, row in enumerate(records, 2) if (row.get("نام وام") or "").strip()]
    states: dict[str, Counter] = {key: Counter() for key in COLUMNS}
    unclassified: dict[str, Counter] = {key: Counter() for key in COLUMNS}
    exclusions: list[dict] = []
    identity = Counter()
    conditions = 0
    for row_number, row in records:
        identity[(row["نام بانک"].strip(), row["نام وام"].strip())] += 1
        conditions += bool((row.get("شرایط و مقررات") or "").strip())
        reasons = []
        for variable, column in COLUMNS.items():
            normalized = normalize_variable(variable, row.get(column))
            states[variable][normalized.state.value] += 1
            if normalized.state is not NormalizationState.CLASSIFIED:
                unclassified[variable][(row.get(column) or "").strip() or "<blank>"] += 1
                if variable in CORE:
                    reasons.append(variable)
        if reasons:
            exclusions.append(
                {
                    "row": row_number,
                    "lender": row["نام بانک"].strip(),
                    "loan": row["نام وام"].strip(),
                    "coreVariables": reasons,
                }
            )
    return {
        "source": str(SOURCE.relative_to(ROOT)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "loanCount": len(records),
        "conditionsPresent": conditions,
        "rankableCount": len(records) - len(exclusions),
        "needsReviewCount": len(exclusions),
        "duplicateLenderLoanIdentities": [list(key) for key, count in identity.items() if count > 1],
        "statesByVariable": {key: dict(value) for key, value in states.items()},
        "unclassifiedValues": {key: dict(value) for key, value in unclassified.items() if value},
        "rankingExclusions": exclusions,
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), ensure_ascii=False, indent=2))
