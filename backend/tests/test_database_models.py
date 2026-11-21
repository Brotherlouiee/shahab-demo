"""Metadata-level tests; PostgreSQL execution is intentionally deferred to US-04.T04."""

from __future__ import annotations

import unittest

from backend.app.infrastructure.db.models import Base, LoanTerms, QuestionVariableWeight


class DatabaseModelTests(unittest.TestCase):
    def test_expected_core_tables_are_declared(self) -> None:
        self.assertTrue(
            {"lenders", "loan_products", "loan_product_versions", "loan_terms", "data_import_runs"}.issubset(
                Base.metadata.tables
            )
        )

    def test_numeric_constraints_are_declared(self) -> None:
        self.assertGreaterEqual(len(LoanTerms.__table__.constraints), 3)
        self.assertGreaterEqual(len(QuestionVariableWeight.__table__.constraints), 2)
