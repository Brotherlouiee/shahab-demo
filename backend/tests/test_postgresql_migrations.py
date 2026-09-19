"""Integration verification for the versioned schema; skips only when no real PostgreSQL is supplied."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest

from sqlalchemy import create_engine, inspect, text

DATABASE_URL = os.environ.get("SHAHAB_TEST_DATABASE_URL")
EXPECTED_TABLES = {
    "answer_options",
    "data_import_runs",
    "data_source_files",
    "lenders",
    "loan_product_versions",
    "loan_products",
    "loan_terms",
    "loan_variables",
    "question_variable_weights",
    "questionnaire_versions",
    "questions",
    "recommendation_config_versions",
    "variable_categories",
}
EXPECTED_INDEX = "ix_loan_products_lender_id"


@unittest.skipUnless(DATABASE_URL, "requires SHAHAB_TEST_DATABASE_URL for real PostgreSQL verification")
class PostgreSqlMigrationTests(unittest.TestCase):
    """Exercise empty-db upgrade, a representative fixture write and a complete downgrade."""

    def setUp(self) -> None:
        self.environment = {**os.environ, "SHAHAB_DATABASE_URL": str(DATABASE_URL)}
        self._alembic("downgrade", "base", check=False)

    def tearDown(self) -> None:
        self._alembic("downgrade", "base", check=False)

    def _alembic(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-c", "from alembic.config import main; main()", *arguments],
            check=check,
            cwd=os.getcwd(),
            env=self.environment,
            text=True,
            capture_output=True,
        )

    def test_upgrade_fixture_and_downgrade(self) -> None:
        self._alembic("upgrade", "head")
        engine = create_engine(str(DATABASE_URL))
        self.assertTrue(EXPECTED_TABLES.issubset(set(inspect(engine).get_table_names())))
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO lenders (lender_id, canonical_name) "
                    "VALUES ('00000000-0000-0000-0000-000000000001', 'fixture-lender')"
                )
            )
            self.assertEqual(connection.execute(text("SELECT COUNT(*) FROM lenders")).scalar_one(), 1)
        engine.dispose()

        self._alembic("downgrade", "base")
        engine = create_engine(str(DATABASE_URL))
        # Alembic deliberately retains its own version ledger at base; only application tables must be gone.
        self.assertFalse(EXPECTED_TABLES & set(inspect(engine).get_table_names()))
        engine.dispose()

    def test_selective_catalogue_lookup_uses_index(self) -> None:
        """Record the V1 list-query plan on PostgreSQL; cost values are deliberately not asserted."""
        self._alembic("upgrade", "head")
        engine = create_engine(str(DATABASE_URL))
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO lenders (lender_id, canonical_name) "
                    "SELECT md5(series::text)::uuid, 'explain-lender-' || series "
                    "FROM generate_series(1, 1000) AS series"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO loan_products (loan_product_id, lender_id, canonical_name) "
                    "SELECT md5(('product-' || series)::text)::uuid, md5(series::text)::uuid, "
                    "'explain-product-' || series FROM generate_series(1, 1000) AS series"
                )
            )
            plan = connection.execute(
                text(
                    "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
                    "SELECT loan_product_id, canonical_name FROM loan_products "
                    "WHERE lender_id = md5('500')::uuid"
                )
            ).scalar_one()[0]["Plan"]
        engine.dispose()

        self.assertIn(EXPECTED_INDEX, str(plan))
        self.assertNotEqual(plan["Node Type"], "Seq Scan")
