"""Regression tests for US-09.T06U query-scope optimizations."""

from __future__ import annotations

import unittest
from unittest.mock import Mock
from uuid import uuid4

from backend.app.loans.infrastructure.sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository
from backend.app.questionnaire.infrastructure.sqlalchemy_sessions import SqlAlchemyQuestionnaireSessionRepository


class QueryScopeTests(unittest.TestCase):
    def test_detail_lookup_filters_one_opaque_loan_id_without_full_catalogue_scan(self) -> None:
        repository = object.__new__(SqlAlchemyServingLoanCatalogueRepository)
        repository._session = Mock()
        statement = Mock()
        filtered_statement = Mock()
        repository._statement = Mock(return_value=statement)
        repository._to_record = Mock(return_value="approved-detail")
        statement.where.return_value = filtered_statement
        repository._session.execute.return_value.one_or_none.return_value = ("row",)

        result = repository.get_current_serving_loan(str(uuid4()))

        self.assertEqual(result, "approved-detail")
        statement.where.assert_called_once()
        repository._session.execute.assert_called_once_with(filtered_statement)
        repository._to_record.assert_called_once_with(("row",))

    def test_invalid_loan_id_does_not_query_catalogue(self) -> None:
        repository = object.__new__(SqlAlchemyServingLoanCatalogueRepository)
        repository._session = Mock()

        self.assertIsNone(repository.get_current_serving_loan("not-a-uuid"))

        repository._session.execute.assert_not_called()

    def test_prepared_questionnaire_reference_catalogue_skips_per_request_bootstrap(self) -> None:
        reference_catalogue = (
            uuid4(),
            {"Q1": uuid4()},
            {"Q1-A1": uuid4()},
        )
        repository = SqlAlchemyQuestionnaireSessionRepository(
            Mock(),
            Mock(),
            reference_catalogue=reference_catalogue,
        )

        self.assertIs(repository.reference_catalogue, reference_catalogue)


if __name__ == "__main__":
    unittest.main()
