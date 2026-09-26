"""Generate a deterministic, non-publishing import manifest from the verified loan source.

The source stays byte-for-byte unchanged. This command has no database connection;
approval and serving publication require a separate, explicit transaction.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from backend.app.data_pipeline.application.prepare_import import ImportManifestRow, prepare_import_manifest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents" / "documents" / "دیتابیس وام های بانکی.unitext"
EXPECTED_SHA256 = "598052635954071b192bb43505e572f30ee88efd99b4d5ae757f6d555bfaae45"
PARSER_VERSION = "loan-source.v1"
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
DISPLAY = {"bankLogo": "لوگو بانک", "requiredDepositAccount": "حساب سپرده لازم", "conditions": "شرایط و مقررات"}


def build_manifest(path: Path = SOURCE) -> dict:
    raw = path.read_bytes()
    source_hash = hashlib.sha256(raw).hexdigest()
    if source_hash != EXPECTED_SHA256:
        raise ValueError("loan source bytes differ from the verified canonical source")
    with path.open(encoding="utf-16", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if not set(COLUMNS.values()).issubset(reader.fieldnames or ()) or not set(DISPLAY.values()).issubset(
            reader.fieldnames or ()
        ):
            raise ValueError("loan source headers do not cover the canonical manifest")
        rows = [
            {
                "sourceRowNumber": source_row_number,
                "lenderName": row["نام بانک"].strip(),
                "loanName": row["نام وام"].strip(),
                "variableValues": {key: row.get(column) for key, column in COLUMNS.items()},
                "displayFields": {key: row[column] for key, column in DISPLAY.items() if row.get(column)},
            }
            for source_row_number, row in enumerate(reader, 2)
            if (row.get("نام وام") or "").strip()
        ]
    plan = prepare_import_manifest(
        source_file_sha256=source_hash,
        parser_version=PARSER_VERSION,
        rows=tuple(
            ImportManifestRow(
                source_row_number=item["sourceRowNumber"],
                lender_name=item["lenderName"],
                loan_name=item["loanName"],
                variable_values=item["variableValues"],
                display_fields=item["displayFields"],
            )
            for item in rows
        ),
    )
    if not plan.is_publishable_candidate:
        raise ValueError(
            f"canonical import plan has {len(plan.rejected_rows)} rejected rows and {len(plan.issues)} issues"
        )
    return {"schemaVersion": "1.0.0", "sourceFileSha256": source_hash, "parserVersion": PARSER_VERSION, "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_manifest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(manifest["rows"]), "sourceSha256": manifest["sourceFileSha256"]}))


if __name__ == "__main__":
    main()
