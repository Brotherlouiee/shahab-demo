"""PostgreSQL-backed read adapter for the approved serving loan catalogue."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import (
    Lender,
    LoanConditions,
    LoanProduct,
    LoanProductVersion,
    LoanServingFacts,
    LoanTerms,
    PublicationState,
    ServingCatalogueMember,
    ServingCatalogueVersion,
)
from backend.app.loans.application.ports import ServingLoanCatalogueRepository
from backend.app.loans.domain.models import (
    LoanDetail,
    LoanSummary,
    PublishedLoanRecord,
    ServingCatalogueUnavailableError,
)


class SqlAlchemyServingLoanCatalogueRepository(ServingLoanCatalogueRepository):
    """Expose published catalogue rows only; drafts/raw data cannot cross this boundary."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_current_serving_loans(self) -> tuple[PublishedLoanRecord, ...]:
        return tuple(self._to_record(row) for row in self._rows())

    def get_current_serving_loan(self, loan_id: str) -> PublishedLoanRecord | None:
        try:
            identifier = UUID(loan_id)
        except ValueError:
            return None
        statement = self._statement().where(LoanProductVersion.loan_product_version_id == identifier)
        try:
            row = self._session.execute(statement).one_or_none()
        except SQLAlchemyError as error:
            raise ServingCatalogueUnavailableError("approved loan catalogue is unavailable") from error
        return None if row is None else self._to_record(row)

    def _rows(self):
        try:
            return self._session.execute(self._statement()).all()
        except SQLAlchemyError as error:
            raise ServingCatalogueUnavailableError("approved loan catalogue is unavailable") from error

    def _statement(self):
        return (
            select(LoanProductVersion, LoanProduct, Lender, LoanTerms, LoanConditions, LoanServingFacts)
            .join(
                ServingCatalogueMember,
                ServingCatalogueMember.loan_product_version_id == LoanProductVersion.loan_product_version_id,
            )
            .join(
                ServingCatalogueVersion,
                ServingCatalogueVersion.serving_catalogue_version_id
                == ServingCatalogueMember.serving_catalogue_version_id,
            )
            .join(LoanProduct, LoanProduct.loan_product_id == LoanProductVersion.loan_product_id)
            .join(Lender, Lender.lender_id == LoanProduct.lender_id)
            .outerjoin(LoanTerms, LoanTerms.loan_product_version_id == LoanProductVersion.loan_product_version_id)
            .join(LoanConditions, LoanConditions.loan_product_version_id == LoanProductVersion.loan_product_version_id)
            .join(
                LoanServingFacts, LoanServingFacts.loan_product_version_id == LoanProductVersion.loan_product_version_id
            )
            .where(
                ServingCatalogueVersion.active.is_(True),
                ServingCatalogueVersion.state == "published",
                LoanProductVersion.publication_state == PublicationState.PUBLISHED,
                LoanProductVersion.source_file_id == ServingCatalogueVersion.data_source_file_id,
            )
        )
    @staticmethod
    def _to_record(row) -> PublishedLoanRecord:
        version, product, lender, terms, conditions, facts = row
        loan_id = str(version.loan_product_version_id)
        summary = LoanSummary(loan_id, lender.canonical_name, product.canonical_name, facts.bank_logo_reference)
        detail = LoanDetail(
            loan_id=loan_id,
            lender_name=lender.canonical_name,
            loan_name=product.canonical_name,
            bank_logo_reference=facts.bank_logo_reference,
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
            deposit_required=facts.deposit_required_text,
            deposit_holding_months=facts.deposit_holding_months,
            loan_to_deposit_ratio_percent=None
            if facts.loan_to_deposit_ratio_percent is None
            else Decimal(facts.loan_to_deposit_ratio_percent),
            guarantee_type=facts.guarantee_type_text,
            required_deposit_account=facts.required_deposit_account,
            conditions_source_text=conditions.source_text,
        )
        return PublishedLoanRecord(str(version.loan_product_version_id), summary, detail)
