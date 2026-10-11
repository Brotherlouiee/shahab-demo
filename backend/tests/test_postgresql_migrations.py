"""Integration verification for the versioned schema; skips only when no real PostgreSQL is supplied."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest

from sqlalchemy import create_engine, inspect, text

DATABASE_URL = os.environ.get("SHAHAB_TEST_DATABASE_URL")
EXPECTED_TABLES = {
    "operations_imports",
    "operations_versions",
    "audit_events",
    "operations_workflow_head",
    "user_profiles",
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
    "loan_serving_facts",
    "answer_option_weights",
    "answer_category_compatibilities",
    "serving_catalogue_versions",
    "serving_catalogue_members",
    "recommendation_history_runs",
    "recommendation_history_items",
    "recommendation_history_item_reasons",
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

    def test_profile_persistence_survives_a_new_connection(self) -> None:
        from sqlalchemy.orm import Session

        from backend.app.accounts.profile_repository import read_profile, upsert_profile
        from backend.app.accounts.profile_schema import ProfilePayload

        self._alembic("upgrade", "head")
        engine = create_engine(str(DATABASE_URL))
        with Session(engine) as session:
            upsert_profile(
                ProfilePayload(phone="09000000001", firstName="آزمون", income="22-to-50", job="manager"), session
            )
        engine.dispose()

        engine = create_engine(str(DATABASE_URL))
        with Session(engine) as session:
            stored = read_profile("09000000001", session)
            self.assertEqual((stored.firstName, stored.income, stored.job), ("آزمون", "22-to-50", "manager"))
        engine.dispose()

    def test_verified_login_creates_profile_and_personal_info_survives_relogin(self) -> None:
        from fastapi.testclient import TestClient
        from sqlalchemy.orm import Session

        from backend.app.core.config import AppEnvironment, Settings
        from backend.app.core.dependencies import get_request_database_session
        from backend.app.infrastructure.db.models import UserProfile
        from backend.app.main import create_app

        self._alembic("upgrade", "head")
        engine = create_engine(str(DATABASE_URL))
        app = create_app(Settings(environment=AppEnvironment.LOCAL))

        def database_session():
            with Session(engine) as session:
                yield session

        app.dependency_overrides[get_request_database_session] = database_session
        client = TestClient(app)

        def login():
            requested = client.post("/api/v1/account-access/request", json={"phone": "۰۹۰۰۰۰۰۰۰۰۱"})
            verified = client.post(
                "/api/v1/account-access/verify",
                json={"challengeId": requested.json()["challengeId"], "code": "123456"},
            )
            self.assertEqual(verified.status_code, 200)
            return {"Authorization": "Bearer " + verified.json()["accessToken"]}

        headers = login()
        with Session(engine) as session:
            record = session.get(UserProfile, "09000000001")
            self.assertIsNotNone(record)
            assert record is not None
            self.assertEqual(record.first_name, "")
        payload = {
            "phone": "09000000001",
            "firstName": "آزمون",
            "lastName": "تست",
            "income": "22-to-50",
            "job": "manager",
        }
        self.assertEqual(client.put("/api/v1/profiles", headers=headers, json=payload).status_code, 200)
        headers = login()
        profile = client.get("/api/v1/profiles/me", headers=headers).json()
        self.assertEqual({key: profile[key] for key in payload}, payload)
        with Session(engine) as session:
            record = session.get(UserProfile, "09000000001")
            assert record is not None
            self.assertEqual(
                (record.first_name, record.last_name, record.income, record.job),
                ("آزمون", "تست", "22-to-50", "manager"),
            )
        engine.dispose()

    def test_official_materialization_has_a_durable_active_version(self) -> None:
        import json
        from decimal import Decimal
        from pathlib import Path

        from sqlalchemy import delete, func, select
        from sqlalchemy.orm import Session

        from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
        from backend.app.infrastructure.db.models import (
            AnswerCategoryCompatibility,
            LoanCategoryAssignment,
            LoanConditions,
            LoanServingFacts,
            ServingCatalogueVersion,
        )
        from backend.app.loans.infrastructure.backfill_serving_facts import backfill_official_serving_facts
        from backend.app.loans.infrastructure.sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository
        from backend.app.recommendation.application.use_cases import RecommendLoans
        from backend.app.recommendation.domain.entities import AnswerPreference, ClassificationState
        from backend.app.recommendation.infrastructure.sqlalchemy_snapshot import (
            SqlAlchemyRecommendationSnapshotRepository,
        )
        from scripts.build_t05a_import_manifest import build_manifest
        from scripts.build_t05a_recommendation_config import build_config
        from scripts.materialize_t05a import audit_database

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
            self.assertEqual(session.scalar(select(func.count()).select_from(LoanServingFacts)), 102)
            database_audit = audit_database(session)
            for key in (
                "missingSourceRows",
                "unexpectedSourceRows",
                "identityMismatchRows",
                "conditionsMismatchRows",
                "incompleteCategoryRows",
                "categoryMismatchCells",
            ):
                self.assertEqual(database_audit[key], [], key)
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
            snapshot = SqlAlchemyRecommendationSnapshotRepository(session).read_approved_snapshot()
            self.assertEqual(len(snapshot.candidates), 102)
            target = next(
                item
                for item in snapshot.candidates
                if all(
                    item.state_for(key) is ClassificationState.CLASSIFIED
                    for key in ("maxAmount", "monthlyInstallment", "maxRepaymentMonths", "interestRate")
                )
            )
            preferences = tuple(
                AnswerPreference(key, target.categories[key] or identifiers["categoryIds"][key][0], Decimal("1"))
                for key in identifiers["loanVariableIds"]
            )
            result = RecommendLoans(SqlAlchemyRecommendationSnapshotRepository(session)).execute(preferences)
            self.assertEqual((len(result.ranked_recommendations), len(result.needs_review)), (88, 14))
            self.assertTrue(all(item.score is not None for item in result.ranked_recommendations))
            self.assertTrue(
                all(trace.raw_score is None for trace in result.traces if trace.decision.value == "needs_review")
            )
            detail = SqlAlchemyServingLoanCatalogueRepository(session).get_current_serving_loan(target.loan_id)
            self.assertTrue(detail.detail.conditions_source_text)
            session.commit()
            with session.begin():
                session.execute(delete(LoanServingFacts))
                self.assertEqual(backfill_official_serving_facts(session, build_manifest()), 102)
            with session.begin():
                self.assertEqual(backfill_official_serving_facts(session, build_manifest()), 0)
        engine.dispose()
