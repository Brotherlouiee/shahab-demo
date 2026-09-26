"""Serving-catalogue adapter rejects orphan published and draft versions."""

from __future__ import annotations

import unittest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import Base, Lender, LoanProduct, LoanProductVersion, PublicationState
from backend.app.loans.infrastructure.sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository


class SqlAlchemyCatalogueAdapterTests(unittest.TestCase):
    def test_no_version_without_active_membership_is_visible(self) -> None:
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            lender = Lender(lender_id=uuid.uuid4(), canonical_name="بانک نمونه")
            product = LoanProduct(loan_product_id=uuid.uuid4(), lender_id=lender.lender_id, canonical_name="طرح نمونه")
            published = LoanProductVersion(
                loan_product_version_id=uuid.uuid4(),
                loan_product_id=product.loan_product_id,
                version_number=1,
                publication_state=PublicationState.PUBLISHED,
            )
            draft = LoanProductVersion(
                loan_product_version_id=uuid.uuid4(),
                loan_product_id=product.loan_product_id,
                version_number=2,
                publication_state=PublicationState.DRAFT,
            )
            session.add_all((lender, product, published, draft))
            session.commit()
            repository = SqlAlchemyServingLoanCatalogueRepository(session)
            self.assertEqual(repository.list_current_serving_loans(), ())
            self.assertIsNone(repository.get_current_serving_loan(str(published.loan_product_version_id)))
            self.assertIsNone(repository.get_current_serving_loan(str(draft.loan_product_version_id)))
