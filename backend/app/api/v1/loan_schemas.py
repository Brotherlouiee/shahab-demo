"""Safe response schemas for approved serving-loan use cases.

These are transport contracts only. They intentionally omit provenance, serving
version IDs, approval metadata, raw conditions text and internal asset references.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from backend.app.loans.domain.models import LoanDetail, LoanSummary

MoneyAmount = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=2)]
Percentage = Annotated[Decimal, Field(ge=0, max_digits=8, decimal_places=4)]
LoanIdentifier = Annotated[str, Field(min_length=1, max_length=128)]
DisplayText = Annotated[str, Field(min_length=1, max_length=255)]


class LoanSummaryResponse(BaseModel):
    """Public list item; no data-pipeline or approval implementation detail."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    loan_id: LoanIdentifier = Field(alias="loanId")
    lender_name: DisplayText = Field(alias="lenderName")
    loan_name: DisplayText = Field(alias="loanName")

    @classmethod
    def from_domain(cls, loan: LoanSummary) -> LoanSummaryResponse:
        """Map the explicit public subset instead of serializing a domain object."""
        return cls(loanId=loan.loan_id, lenderName=loan.lender_name, loanName=loan.loan_name)


class LoanDetailResponse(LoanSummaryResponse):
    """Public approved facts; conditions text remains unavailable until US-06.T03."""

    max_amount_tomans: MoneyAmount | None = Field(alias="maxAmountTomans")
    monthly_installment_tomans: MoneyAmount | None = Field(alias="monthlyInstallmentTomans")
    max_repayment_months: Annotated[int, Field(ge=0)] | None = Field(alias="maxRepaymentMonths")
    interest_rate_percent: Percentage | None = Field(alias="interestRatePercent")
    deposit_required: Annotated[str, Field(max_length=100)] | None = Field(alias="depositRequired")
    deposit_holding_months: Annotated[int, Field(ge=0)] | None = Field(alias="depositHoldingMonths")
    loan_to_deposit_ratio_percent: Percentage | None = Field(alias="loanToDepositRatioPercent")
    guarantee_type: Annotated[str, Field(max_length=100)] | None = Field(alias="guaranteeType")
    required_deposit_account: Annotated[str, Field(max_length=255)] | None = Field(alias="requiredDepositAccount")

    @classmethod
    def from_loan_detail(cls, loan: LoanDetail) -> LoanDetailResponse:
        """Map the vetted public fields one by one; source/provenance stays server-side."""
        return cls(
            loanId=loan.loan_id,
            lenderName=loan.lender_name,
            loanName=loan.loan_name,
            maxAmountTomans=loan.max_amount_tomans,
            monthlyInstallmentTomans=loan.monthly_installment_tomans,
            maxRepaymentMonths=loan.max_repayment_months,
            interestRatePercent=loan.interest_rate_percent,
            depositRequired=loan.deposit_required,
            depositHoldingMonths=loan.deposit_holding_months,
            loanToDepositRatioPercent=loan.loan_to_deposit_ratio_percent,
            guaranteeType=loan.guarantee_type,
            requiredDepositAccount=loan.required_deposit_account,
        )
