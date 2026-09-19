"""Structural staging tests; parsing/normalization intentionally remain outside US-05.T02."""

from __future__ import annotations

import unittest

from backend.app.data_pipeline.application.validate_staging import DelimitedStagingValidator
from backend.app.data_pipeline.domain.staging_validation import StagingIssueCode


class StagingValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = DelimitedStagingValidator(expected_headers=("نام بانک", "نام وام"), encoding="utf-16-le")

    def test_valid_utf16_source_has_no_findings(self) -> None:
        result = self.validator.validate(
            "نام بانک\tنام وام\nبانک الف\tطرح الف\n".encode("utf-16-le"),
            source_sha256="a" * 64,
            known_source_hashes=frozenset(),
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(result.row_count, 1)

    def test_header_and_row_shape_are_reported_without_repair(self) -> None:
        result = self.validator.validate(
            "نام بانک\tنام بانک\nبانک الف\n".encode("utf-16-le"),
            source_sha256="b" * 64,
            known_source_hashes=frozenset(),
        )
        self.assertEqual(
            {issue.code for issue in result.issues},
            {StagingIssueCode.DUPLICATE_HEADER, StagingIssueCode.INVALID_HEADER, StagingIssueCode.ROW_WIDTH_MISMATCH},
        )

    def test_encoding_and_duplicate_source_evidence_are_both_visible(self) -> None:
        result = self.validator.validate(b"\xff", source_sha256="c" * 64, known_source_hashes=frozenset({"c" * 64}))
        self.assertEqual(
            {issue.code for issue in result.issues},
            {StagingIssueCode.DUPLICATE_SOURCE_EVIDENCE, StagingIssueCode.UNSUPPORTED_ENCODING},
        )
