"""US-06.T02 response-schema tests for allowlisted public loan fields."""

from __future__ import annotations

import unittest
from decimal import Decimal

from backend.app.api.v1.loan_schemas import LoanDetailResponse, LoanSummaryResponse
from backend.app.loans.domain.models import LoanDetail, LoanSummary


class LoanResponseSchemaTests(unittest.TestCase):
    def test_summary_uses_camel_case_and_excludes_internal_logo_reference(self) -> None:
        response = LoanSummaryResponse.from_domain(
            LoanSummary("loan-1", "بانک نمونه", "طرح نمونه", "internal-logo-reference")
        )
        self.assertEqual(
            response.model_dump(by_alias=True),
            {"loanId": "loan-1", "lenderName": "بانک نمونه", "loanName": "طرح نمونه"},
        )

    def test_detail_allowlists_public_terms_but_never_conditions_or_provenance(self) -> None:
        domain = LoanDetail(
            loan_id="loan-1",
            lender_name="بانک نمونه",
            loan_name="طرح نمونه",
            bank_logo_reference="internal-logo-reference",
            max_amount_tomans=Decimal("100000000"),
            monthly_installment_tomans=Decimal("10000000"),
            max_repayment_months=12,
            interest_rate_percent=Decimal("18"),
            deposit_required="دارد",
            deposit_holding_months=3,
            loan_to_deposit_ratio_percent=Decimal("100"),
            guarantee_type="تعهد فردی",
            required_deposit_account="حساب کوتاه مدت",
            conditions_source_text="متن خام شرایط",
        )
        payload = LoanDetailResponse.from_loan_detail(domain).model_dump(by_alias=True)
        self.assertEqual(payload["maxAmountTomans"], Decimal("100000000"))
        self.assertNotIn("conditionsSourceText", payload)
        self.assertNotIn("bankLogoReference", payload)
        self.assertNotIn("servingVersionId", payload)

    def test_extra_or_invalid_public_values_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            LoanSummaryResponse(loanId="loan-1", lenderName="بانک", loanName="طرح", sourceHash="secret")
        with self.assertRaises(ValueError):
            LoanDetailResponse(
                loanId="loan-1",
                lenderName="بانک",
                loanName="طرح",
                maxAmountTomans="-1",
                monthlyInstallmentTomans=None,
                maxRepaymentMonths=None,
                interestRatePercent=None,
                depositRequired=None,
                depositHoldingMonths=None,
                loanToDepositRatioPercent=None,
                guaranteeType=None,
                requiredDepositAccount=None,
            )
