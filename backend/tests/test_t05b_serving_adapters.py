"""Read-only serving adapters against the verified official source fixture."""

from __future__ import annotations

import json
import unittest
import uuid
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.core.config import AppEnvironment, Settings
from backend.app.core.dependencies import get_loan_details_use_case
from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from backend.app.infrastructure.db.models import (
    Base,
    LoanCategoryAssignment,
    LoanConditions,
    LoanProductVersion,
    LoanServingFacts,
    PublicationState,
    RecommendationConfigVersion,
    ServingCatalogueMember,
    ServingCatalogueVersion,
)
from backend.app.loans.application.use_cases import GetLoanDetails
from backend.app.loans.domain.models import ServingCatalogueUnavailableError
from backend.app.loans.infrastructure.backfill_serving_facts import backfill_official_serving_facts
from backend.app.loans.infrastructure.sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository
from backend.app.main import create_app
from backend.app.recommendation.application.use_cases import RecommendLoans
from backend.app.recommendation.domain.entities import AnswerPreference, ClassificationState
from backend.app.recommendation.infrastructure.sqlalchemy_snapshot import (
    SnapshotIntegrityError,
    SnapshotUnavailableError,
    SqlAlchemyRecommendationSnapshotRepository,
)
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config

ROOT = Path(__file__).parents[2]


class OfficialServingAdaptersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_manifest()
        cls.config = build_config()
        cls.questionnaire = json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text())
        cls.identifiers = json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text())

    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as session, session.begin():
            materialize_official_sources(
                session,
                loan_manifest=self.manifest,
                config_manifest=self.config,
                questionnaire=self.questionnaire,
                identifiers=self.identifiers,
                actor_reference="reviewed-operator",
                approval_reason="official source verification",
            )

    def tearDown(self):
        self.engine.dispose()

    def test_real_snapshot_runs_engine_and_details_are_same_published_versions(self):
        with Session(self.engine) as session:
            snapshot = SqlAlchemyRecommendationSnapshotRepository(session).read_approved_snapshot()
            self.assertEqual((len(snapshot.candidates), snapshot.config_version), (102, "1.1.0"))
            target = next(
                candidate
                for candidate in snapshot.candidates
                if all(
                    candidate.state_for(variable) is ClassificationState.CLASSIFIED
                    for variable in ("maxAmount", "monthlyInstallment", "maxRepaymentMonths", "interestRate")
                )
            )
            preferences = tuple(
                AnswerPreference(
                    variable_id,
                    target.categories[variable_id] or self.identifiers["categoryIds"][variable_id][0],
                    Decimal("1"),
                )
                for variable_id in self.identifiers["loanVariableIds"]
            )
            run = RecommendLoans(SqlAlchemyRecommendationSnapshotRepository(session)).execute(preferences)
            self.assertEqual((len(run.ranked_recommendations), len(run.needs_review), len(run.traces)), (88, 14, 102))
            self.assertEqual(
                next(item.score for item in run.ranked_recommendations if item.loan_id == target.loan_id),
                Decimal("1.000000"),
            )
            self.assertTrue(
                all(trace.raw_score is None for trace in run.traces if trace.decision.value == "needs_review")
            )
            repository = SqlAlchemyServingLoanCatalogueRepository(session)
            detail = repository.get_current_serving_loan(target.loan_id)
            self.assertIsNotNone(detail)
            source_row = session.get(LoanProductVersion, uuid.UUID(target.loan_id)).source_row_number
            expected = next(item for item in self.manifest["rows"] if item["sourceRowNumber"] == source_row)
            self.assertEqual(detail.detail.conditions_source_text, expected["displayFields"]["conditions"])
            self.assertEqual(detail.detail.guarantee_type, expected["variableValues"]["guaranteeType"])
            self.assertEqual(
                detail.detail.required_deposit_account, expected["displayFields"]["requiredDepositAccount"]
            )
            self.assertEqual(len(repository.list_current_serving_loans()), 102)

    def test_fail_closed_on_missing_active_config_or_category(self):
        with Session(self.engine) as session:
            active = session.scalar(select(ServingCatalogueVersion).where(ServingCatalogueVersion.active.is_(True)))
            active.active = False
            active.state = "superseded"
            session.commit()
            with self.assertRaises(SnapshotUnavailableError):
                SqlAlchemyRecommendationSnapshotRepository(session).read_approved_snapshot()
            self.assertEqual(SqlAlchemyServingLoanCatalogueRepository(session).list_current_serving_loans(), ())
            active.active = True
            active.state = "published"
            config = session.get(RecommendationConfigVersion, active.config_version_id)
            config.approved = False
            session.commit()
            with self.assertRaises(SnapshotIntegrityError):
                SqlAlchemyRecommendationSnapshotRepository(session).read_approved_snapshot()
            config.approved = True
            assignment = session.scalar(select(LoanCategoryAssignment))
            session.delete(assignment)
            session.commit()
            with self.assertRaises(SnapshotIntegrityError):
                SqlAlchemyRecommendationSnapshotRepository(session).read_approved_snapshot()

    def test_draft_and_nonmember_are_invisible_and_empty_active_is_no_candidate(self):
        with Session(self.engine) as session:
            published = session.scalar(select(LoanProductVersion))
            published.publication_state = PublicationState.DRAFT
            session.commit()
            with self.assertRaises(SnapshotIntegrityError):
                SqlAlchemyRecommendationSnapshotRepository(session).read_approved_snapshot()
            self.assertIsNone(
                SqlAlchemyServingLoanCatalogueRepository(session).get_current_serving_loan(
                    str(published.loan_product_version_id)
                )
            )
            published.publication_state = PublicationState.PUBLISHED
            active = session.scalar(select(ServingCatalogueVersion).where(ServingCatalogueVersion.active.is_(True)))
            session.execute(
                delete(ServingCatalogueMember).where(
                    ServingCatalogueMember.serving_catalogue_version_id == active.serving_catalogue_version_id
                )
            )
            session.commit()
            snapshot = SqlAlchemyRecommendationSnapshotRepository(session).read_approved_snapshot()
            self.assertEqual(snapshot.candidates, ())
            self.assertEqual(SqlAlchemyServingLoanCatalogueRepository(session).list_current_serving_loans(), ())

    def test_empty_conditions_are_distinct_from_absent_loan(self):
        with Session(self.engine) as session:
            condition = session.scalar(select(LoanConditions))
            condition.source_text = ""
            session.commit()
            repository = SqlAlchemyServingLoanCatalogueRepository(session)
            self.assertEqual(
                repository.get_current_serving_loan(
                    str(condition.loan_product_version_id)
                ).detail.conditions_source_text,
                "",
            )
            self.assertIsNone(repository.get_current_serving_loan("missing"))

    def test_public_detail_response_uses_real_conditions_without_internal_data(self):
        with Session(self.engine) as session:
            version = session.scalar(select(LoanProductVersion))
            app = create_app(Settings(environment=AppEnvironment.TEST))
            app.dependency_overrides[get_loan_details_use_case] = lambda: GetLoanDetails(
                SqlAlchemyServingLoanCatalogueRepository(session)
            )
            response = TestClient(app, raise_server_exceptions=False).get(
                f"/api/v1/loans/{version.loan_product_version_id}"
            )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertTrue(payload["conditions"])
            for internal in (
                "sourceRowNumber",
                "servingVersionId",
                "configVersion",
                "trace",
                "rawAnswers",
                "sessionId",
            ):
                self.assertNotIn(internal, payload)

    def test_backfill_is_idempotent_and_failure_rolls_back(self):
        with Session(self.engine) as session:
            session.execute(delete(LoanServingFacts))
            session.commit()
            with session.begin():
                self.assertEqual(backfill_official_serving_facts(session, self.manifest), 102)
            with session.begin():
                self.assertEqual(backfill_official_serving_facts(session, self.manifest), 0)
            facts = session.scalar(select(LoanServingFacts))
            facts.guarantee_type_text = "tampered"
            session.commit()
            with self.assertRaises(ValueError), session.begin():
                backfill_official_serving_facts(session, self.manifest)
            self.assertEqual(session.scalar(select(func.count()).select_from(LoanServingFacts)), 102)

    def test_unavailable_storage_has_typed_failures(self):
        empty_engine = create_engine("sqlite+pysqlite:///:memory:")
        try:
            with Session(empty_engine) as session:
                with self.assertRaises(SnapshotUnavailableError):
                    SqlAlchemyRecommendationSnapshotRepository(session).read_approved_snapshot()
                with self.assertRaises(ServingCatalogueUnavailableError):
                    SqlAlchemyServingLoanCatalogueRepository(session).list_current_serving_loans()
        finally:
            empty_engine.dispose()
