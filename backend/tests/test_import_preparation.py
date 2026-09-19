"""Tests for the non-publishing manifest preparation boundary."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from backend.app.data_pipeline.application.prepare_import import (
    ImportManifestRow,
    ImportPlanIssueCode,
    prepare_import_manifest,
)
from backend.app.data_pipeline.domain.canonical_row import RowRejectionCode


class ImportPreparationTests(unittest.TestCase):
    def test_clean_manifest_is_reviewable_but_not_published(self) -> None:
        plan = prepare_import_manifest(
            source_file_sha256="a" * 64,
            parser_version="normalizer-v1",
            rows=(_manifest_row(),),
        )
        self.assertTrue(plan.is_publishable_candidate)
        self.assertEqual(len(plan.accepted_rows), 1)
        self.assertEqual(plan.accepted_rows[0].ranking_excluded_variable_ids, ())

    def test_every_invalid_item_is_retained_as_rejection_or_issue(self) -> None:
        plan = prepare_import_manifest(
            source_file_sha256="not-a-hash",
            parser_version="normalizer-v1",
            rows=(
                _manifest_row(source_row_number=3, loan_name="طرح اول"),
                _manifest_row(source_row_number=3, loan_name="طرح دوم"),
                _manifest_row(source_row_number=4, lender_name=""),
                _manifest_row(source_row_number=5, loan_name="طرح اول"),
            ),
        )
        self.assertFalse(plan.is_publishable_candidate)
        self.assertEqual(len(plan.accepted_rows), 1)
        self.assertEqual(plan.rejected_rows[0].code, RowRejectionCode.MISSING_LENDER_NAME)
        self.assertEqual(
            {item.code for item in plan.issues},
            {
                ImportPlanIssueCode.INVALID_SOURCE_HASH,
                ImportPlanIssueCode.DUPLICATE_SOURCE_ROW,
                ImportPlanIssueCode.DUPLICATE_CATALOGUE_IDENTITY,
            },
        )

    def test_unknown_core_value_is_not_a_manifest_rejection(self) -> None:
        values = dict(_manifest_row().variable_values)
        values["interestRate"] = "نامشخص"
        plan = prepare_import_manifest(
            source_file_sha256="a" * 64,
            parser_version="normalizer-v1",
            rows=(
                ImportManifestRow(
                    source_row_number=7,
                    lender_name="بانک نمونه",
                    loan_name="طرح نمونه",
                    variable_values=values,
                ),
            ),
        )
        self.assertTrue(plan.is_publishable_candidate)
        self.assertEqual(plan.accepted_rows[0].ranking_excluded_variable_ids, ("interestRate",))

    def test_cli_emits_non_publishing_plan_and_failure_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "sourceFileSha256": "a" * 64,
                        "parserVersion": "normalizer-v1",
                        "rows": [
                            {
                                "sourceRowNumber": 2,
                                "lenderName": "بانک نمونه",
                                "loanName": "طرح نمونه",
                                "variableValues": _manifest_row().variable_values,
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "scripts/prepare_canonical_import.py", "--manifest", str(manifest)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["publishableCandidate"])


def _manifest_row(
    *,
    source_row_number: int = 2,
    lender_name: str | None = "بانک نمونه",
    loan_name: str | None = "طرح نمونه",
) -> ImportManifestRow:
    return ImportManifestRow(
        source_row_number=source_row_number,
        lender_name=lender_name,
        loan_name=loan_name,
        variable_values={
            "maxAmount": "100 میلیون تومان",
            "monthlyInstallment": "10 میلیون تومان",
            "maxRepaymentMonths": "12 ماه",
            "interestRate": "18 درصد",
            "depositRequired": "دارد",
            "depositHoldingMonths": "3 ماه",
            "loanToDepositRatio": "100 درصد",
            "guaranteeType": "تعهد فردی",
        },
        display_fields={"conditions": "شرط نمونه"},
    )
