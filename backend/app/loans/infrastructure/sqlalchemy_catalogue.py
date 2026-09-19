"""PostgreSQL-backed read adapter for the approved serving loan catalogue."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import Lender, LoanProduct, LoanProductVersion, LoanTerms, PublicationState
from backend.app.loans.application.ports import ServingLoanCatalogueRepository
from backend.app.loans.domain.models import LoanDetail, LoanSummary, PublishedLoanRecord


class SqlAlchemyServingLoanCatalogueRepository(ServingLoanCatalogueRepository):
    """Expose published catalogue rows only; drafts/raw data cannot cross this boundary."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_current_serving_loans(self) -> tuple[PublishedLoanRecord, ...]:
        return tuple(self._to_record(row) for row in self._rows())

    def get_current_serving_loan(self, loan_id: str) -> PublishedLoanRecord | None:
        for row in self._rows():
            if str(row[0].loan_product_version_id) == loan_id:
                return self._to_record(row)
        return None

    def _rows(self):
        statement = (
            select(LoanProductVersion, LoanProduct, Lender, LoanTerms)
            .join(LoanProduct, LoanProduct.loan_product_id == LoanProductVersion.loan_product_id)
            .join(Lender, Lender.lender_id == LoanProduct.lender_id)
            .outerjoin(LoanTerms, LoanTerms.loan_product_version_id == LoanProductVersion.loan_product_version_id)
            .where(LoanProductVersion.publication_state == PublicationState.PUBLISHED)
        )
        return self._session.execute(statement).all()

    @staticmethod
    def _to_record(row) -> PublishedLoanRecord:
        version, product, lender, terms = row
        loan_id = str(version.loan_product_version_id)
        summary = LoanSummary(loan_id, lender.canonical_name, product.canonical_name, None)
        detail = LoanDetail(
            loan_id=loan_id,
            lender_name=lender.canonical_name,
            loan_name=product.canonical_name,
            bank_logo_reference=None,
            max_amount_tomans=None
            if terms is None
            else Decimal(terms.max_amount)
            if terms.max_amount is not None
            else None,
            monthly_installment_tomans=None
            if terms is None
            else Decimal(terms.monthly_installment)
            if terms.monthly_installment is not None
            else None,
            max_repayment_months=None if terms is None else terms.max_repayment_months,
            interest_rate_percent=None
            if terms is None
            else Decimal(terms.interest_rate)
            if terms.interest_rate is not None
            else None,
            deposit_required=None,
            deposit_holding_months=None,
            loan_to_deposit_ratio_percent=None,
            guarantee_type=None,
            required_deposit_account=None,
            conditions_source_text=None,
        )
        return PublishedLoanRecord(str(version.loan_product_version_id), summary, detail)
