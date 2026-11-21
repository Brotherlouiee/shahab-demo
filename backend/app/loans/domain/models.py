"""Stable, framework-free views of an approved serving loan catalogue."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


class ServingCatalogueUnavailableError(RuntimeError):
    """Approved loan details are unavailable from the serving store."""


@dataclass(frozen=True, slots=True)
class LoanSummary:
    """Minimal safe catalogue item; it deliberately omits source/provenance internals."""

    loan_id: str
    lender_name: str
    loan_name: str
    bank_logo_reference: str | None


@dataclass(frozen=True, slots=True)
class LoanDetail:
    """Approved loan facts for later presentation; conditions remain plain source text."""

    loan_id: str
    lender_name: str
    loan_name: str
    bank_logo_reference: str | None
    max_amount_tomans: Decimal | None
    monthly_installment_tomans: Decimal | None
    max_repayment_months: int | None
    interest_rate_percent: Decimal | None
    deposit_required: str | None
    deposit_holding_months: int | None
    loan_to_deposit_ratio_percent: Decimal | None
    guarantee_type: str | None
    required_deposit_account: str | None
    conditions_source_text: str | None


@dataclass(frozen=True, slots=True)
class PublishedLoanRecord:
    """Repository-only projection from one current approved serving version.

    The current serving-version identifier is retained for consistency checks,
    but never copied into LoanSummary or LoanDetail. That prevents public
    consumers from coupling to import/provenance implementation details.
    """

    serving_version_id: str
    summary: LoanSummary
    detail: LoanDetail

    def __post_init__(self) -> None:
        """Require repository projections to have one stable loan identity."""
        if self.summary.loan_id != self.detail.loan_id:
            raise ValueError("summary and detail must identify the same loan")
