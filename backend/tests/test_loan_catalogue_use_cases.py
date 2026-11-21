"""US-06.T01 tests: serving-only loan list and detail use cases."""

from __future__ import annotations

import unittest
from decimal import Decimal

from backend.app.loans.application.use_cases import GetLoanDetails, ListLoans
from backend.app.loans.domain.models import LoanDetail, LoanSummary, PublishedLoanRecord
from backend.app.loans.infrastructure.in_memory_catalogue import InMemoryServingLoanCatalogueRepository


class LoanCatalogueUseCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current_record = _record(
            loan_id="loan-b",
            lender_name="بانک ب",
            loan_name="طرح ب",
            serving_version_id="serving-v2",
        )
        self.first_record = _record(
            loan_id="loan-a",
            lender_name="بانک الف",
            loan_name="طرح الف",
            serving_version_id="serving-v2",
        )
        self.superseded_record = _record(
            loan_id="loan-old",
            lender_name="بانک قدیمی",
            loan_name="طرح قدیمی",
            serving_version_id="serving-v1",
        )
        repository = InMemoryServingLoanCatalogueRepository(
            active_serving_version_id="serving-v2",
            records=(self.current_record, self.superseded_record, self.first_record),
        )
        self.list_loans = ListLoans(repository)
        self.get_loan_details = GetLoanDetails(repository)

    def test_list_is_deterministic_and_excludes_superseded_catalogue(self) -> None:
        result = self.list_loans.execute()
        self.assertEqual([loan.loan_id for loan in result], ["loan-a", "loan-b"])
        self.assertNotIn("loan-old", [loan.loan_id for loan in result])
        self.assertFalse(hasattr(result[0], "serving_version_id"))

    def test_detail_returns_only_current_approved_serving_record(self) -> None:
        detail = self.get_loan_details.execute("loan-b")
        assert detail is not None
        self.assertEqual(detail.loan_name, "طرح ب")
        self.assertEqual(detail.conditions_source_text, "شرایط متن خام تأییدشده")
        self.assertIsNone(self.get_loan_details.execute("loan-old"))

    def test_detail_rejects_blank_id_without_repository_lookup(self) -> None:
        with self.assertRaisesRegex(ValueError, "loan id is required"):
            self.get_loan_details.execute("  ")


def _record(*, loan_id: str, lender_name: str, loan_name: str, serving_version_id: str) -> PublishedLoanRecord:
    summary = LoanSummary(
        loan_id=loan_id,
        lender_name=lender_name,
        loan_name=loan_name,
        bank_logo_reference="bank-logo-safe-ref",
    )
    return PublishedLoanRecord(
        serving_version_id=serving_version_id,
        summary=summary,
        detail=LoanDetail(
            loan_id=loan_id,
            lender_name=lender_name,
            loan_name=loan_name,
            bank_logo_reference="bank-logo-safe-ref",
            max_amount_tomans=Decimal("100000000"),
            monthly_installment_tomans=Decimal("10000000"),
            max_repayment_months=12,
            interest_rate_percent=Decimal("18"),
            deposit_required="دارد",
            deposit_holding_months=3,
            loan_to_deposit_ratio_percent=Decimal("100"),
            guarantee_type="تعهد فردی",
            required_deposit_account="حساب کوتاه مدت",
            conditions_source_text="شرایط متن خام تأییدشده",
        ),
    )
