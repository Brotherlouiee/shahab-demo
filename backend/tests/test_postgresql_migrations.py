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
    "loan_category_assignments",
    "loan_conditions",
    "answer_option_weights",
    "answer_category_compatibilities",
    "serving_catalogue_versions",
    "serving_catalogue_members",
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

    def test_official_materialization_has_a_durable_active_version(self) -> None:
        import json
        from pathlib import Path

        from sqlalchemy import func, select
        from sqlalchemy.orm import Session

        from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
        from backend.app.infrastructure.db.models import (
            AnswerCategoryCompatibility,
            LoanCategoryAssignment,
            LoanConditions,
            ServingCatalogueVersion,
        )
        from scripts.build_t05a_import_manifest import build_manifest
        from scripts.build_t05a_recommendation_config import build_config

        self._alembic("upgrade", "head")
        root = Path(__file__).parents[2]
        questionnaire = json.loads((root / "data/contracts/questionnaire-configuration.v1.json").read_text())
        identifiers = json.loads((root / "data/contracts/canonical-identifiers.v1.json").read_text())
        engine = create_engine(str(DATABASE_URL))
        with Session(engine) as session:
            with session.begin():
                first = materialize_official_sources(
                    session,
                    loan_manifest=build_manifest(),
                    config_manifest=build_config(),
                    questionnaire=questionnaire,
                    identifiers=identifiers,
                    actor_reference="ci-fixture",
                    approval_reason="verified source integration test",
                )
            self.assertEqual((first.loan_count, first.rankable_count, first.needs_review_count), (102, 88, 14))
            self.assertEqual(session.scalar(select(func.count()).select_from(LoanCategoryAssignment)), 816)
            self.assertEqual(session.scalar(select(func.count()).select_from(AnswerCategoryCompatibility)), 720)
            self.assertEqual(session.scalar(select(func.count()).select_from(LoanConditions)), 102)
            self.assertEqual(
                session.scalar(
                    select(func.count())
                    .select_from(ServingCatalogueVersion)
                    .where(ServingCatalogueVersion.active.is_(True))
                ),
                1,
            )
            session.commit()
            with session.begin():
                again = materialize_official_sources(
                    session,
                    loan_manifest=build_manifest(),
                    config_manifest=build_config(),
                    questionnaire=questionnaire,
                    identifiers=identifiers,
                    actor_reference="ci-fixture",
                    approval_reason="verified source integration test",
                )
            self.assertTrue(again.reused)
        engine.dispose()
