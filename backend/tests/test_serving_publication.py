"""Approval/publish tests for US-05.T04; no API or production database is involved."""

from __future__ import annotations

import unittest
from datetime import UTC, datetime

from backend.app.data_pipeline.application.publish_serving_version import ServingPublicationService
from backend.app.data_pipeline.domain.canonical_row import (
    CanonicalLoanRow,
    CanonicalRowRejection,
    RankingEligibility,
    RowRejectionCode,
    build_canonical_loan_row,
)
from backend.app.data_pipeline.domain.normalization import normalize_variable
from backend.app.data_pipeline.domain.publication import ServingVersionState
from backend.app.data_pipeline.infrastructure.in_memory_serving_versions import InMemoryServingVersionRepository

_SOURCE_HASH = "a" * 64


class CanonicalRowTests(unittest.TestCase):
    def test_core_unknown_needs_review_but_deposit_unknown_remains_rankable(self) -> None:
        core_unknown = _row(interest_rate="نامشخص")
        deposit_unknown = _row(deposit_required="نامشخص")
        self.assertEqual(core_unknown.ranking_eligibility, RankingEligibility.NEEDS_REVIEW)
        self.assertEqual(core_unknown.ranking_excluded_variable_ids, ("interestRate",))
        self.assertEqual(deposit_unknown.ranking_eligibility, RankingEligibility.RANKABLE)
        self.assertEqual(deposit_unknown.ranking_excluded_variable_ids, ())

    def test_missing_display_identity_is_rejection_evidence(self) -> None:
        result = build_canonical_loan_row(
            source_file_sha256=_SOURCE_HASH,
            source_row_number=7,
            lender_name="",
            loan_name="طرح نمونه",
            variables=_variables(),
        )
        self.assertIsInstance(result, CanonicalRowRejection)
        assert isinstance(result, CanonicalRowRejection)
        self.assertEqual(result.code, RowRejectionCode.MISSING_LENDER_NAME)

    def test_variable_set_mismatch_cannot_reach_core(self) -> None:
        values = _variables()
        values.pop("guaranteeType")
        result = build_canonical_loan_row(
            source_file_sha256=_SOURCE_HASH,
            source_row_number=7,
            lender_name="بانک نمونه",
            loan_name="طرح نمونه",
            variables=values,
        )
        self.assertIsInstance(result, CanonicalRowRejection)
        assert isinstance(result, CanonicalRowRejection)
        self.assertEqual(result.code, RowRejectionCode.VARIABLE_SET_MISMATCH)


class ServingPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryServingVersionRepository()
        self.service = ServingPublicationService(self.repository)
        self.now = datetime(2026, 9, 19, tzinfo=UTC)

    def test_approval_is_required_before_atomic_publish_and_diff_is_retained(self) -> None:
        first = self.service.prepare(
            version_id="catalogue-v1",
            import_id="import-1",
            source_file_sha256=_SOURCE_HASH,
            parser_version="normalizer-v1",
            rows=(_row(),),
        )
        self.assertEqual(first.diff.added, (("بانک نمونه", "طرح نمونه"),))
        with self.assertRaisesRegex(ValueError, "only an approved"):
            self.service.publish(version_id="catalogue-v1")

        self.service.approve(
            version_id="catalogue-v1",
            actor_reference="data-owner",
            reason="Audit reviewed",
            decided_at=self.now,
        )
        published = self.service.publish(version_id="catalogue-v1")
        self.assertEqual(published.state, ServingVersionState.PUBLISHED)
        self.assertEqual(self.repository.get_current_published(), published)

        second = self.service.prepare(
            version_id="catalogue-v2",
            import_id="import-2",
            source_file_sha256="b" * 64,
            parser_version="normalizer-v1",
            rows=(_row(loan_name="طرح اصلاح‌شده"),),
        )
        self.assertEqual(second.diff.added, (("بانک نمونه", "طرح اصلاح‌شده"),))
        self.assertEqual(second.diff.removed, (("بانک نمونه", "طرح نمونه"),))

    def test_publish_failure_does_not_move_active_pointer(self) -> None:
        baseline = self._publish_baseline()
        candidate = self.service.prepare(
            version_id="catalogue-v2",
            import_id="import-2",
            source_file_sha256="b" * 64,
            parser_version="normalizer-v1",
            rows=(_row(loan_name="طرح دیگر"),),
        )
        self.service.approve(
            version_id=candidate.version_id,
            actor_reference="data-owner",
            reason="Audit reviewed",
            decided_at=self.now,
        )
        self.repository.fail_next_publish_for_test()
        with self.assertRaisesRegex(RuntimeError, "simulated publication failure"):
            self.service.publish(version_id=candidate.version_id)
        self.assertEqual(self.repository.get_current_published(), baseline)
        self.assertEqual(self.repository.get_by_id(candidate.version_id).state, ServingVersionState.APPROVED)

    def _publish_baseline(self):
        candidate = self.service.prepare(
            version_id="catalogue-v1",
            import_id="import-1",
            source_file_sha256=_SOURCE_HASH,
            parser_version="normalizer-v1",
            rows=(_row(),),
        )
        self.service.approve(
            version_id=candidate.version_id,
            actor_reference="data-owner",
            reason="Audit reviewed",
            decided_at=self.now,
        )
        return self.service.publish(version_id=candidate.version_id)


def _variables(*, interest_rate: str = "18 درصد", deposit_required: str = "دارد"):
    return {
        "maxAmount": normalize_variable("maxAmount", "100 میلیون تومان"),
        "monthlyInstallment": normalize_variable("monthlyInstallment", "10 میلیون تومان"),
        "maxRepaymentMonths": normalize_variable("maxRepaymentMonths", "12 ماه"),
        "interestRate": normalize_variable("interestRate", interest_rate),
        "depositRequired": normalize_variable("depositRequired", deposit_required),
        "depositHoldingMonths": normalize_variable("depositHoldingMonths", "3 ماه"),
        "loanToDepositRatio": normalize_variable("loanToDepositRatio", "100 درصد"),
        "guaranteeType": normalize_variable("guaranteeType", "تعهد فردی"),
    }


def _row(
    *,
    loan_name: str = "طرح نمونه",
    interest_rate: str = "18 درصد",
    deposit_required: str = "دارد",
) -> CanonicalLoanRow:
    result = build_canonical_loan_row(
        source_file_sha256=_SOURCE_HASH,
        source_row_number=7,
        lender_name="بانک نمونه",
        loan_name=loan_name,
        variables=_variables(interest_rate=interest_rate, deposit_required=deposit_required),
        display_fields={"conditions": "شرط نمونه"},
    )
    assert isinstance(result, CanonicalLoanRow)
    return result
