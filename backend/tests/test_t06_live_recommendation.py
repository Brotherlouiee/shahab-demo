"""Full session-to-approved-source recommendation and safe details regression."""

from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.core.config import Settings
from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from backend.app.infrastructure.db.models import Base
from backend.app.main import create_app
from backend.app.recommendation.domain.entities import ClassificationState, LoanCandidate
from backend.app.recommendation.engine.canonical_scoring import CategoryImpact, score_official_categories
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config

ROOT = Path(__file__).resolve().parents[2]


class LiveRecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loan_manifest = build_manifest()
        cls.config_manifest = build_config()
        cls.questionnaire = json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text())
        cls.identifiers = json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text())

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.database_url = f"sqlite+pysqlite:///{self.directory.name}/serving.sqlite"
        engine = create_engine(self.database_url)
        Base.metadata.create_all(engine)
        with Session(engine) as session, session.begin():
            materialize_official_sources(
                session,
                loan_manifest=self.loan_manifest,
                config_manifest=self.config_manifest,
                questionnaire=self.questionnaire,
                identifiers=self.identifiers,
                actor_reference="verified-test",
                approval_reason="official source regression",
            )
        engine.dispose()
        self.patches = [
            patch(
                "backend.app.core.dependencies.create_database_engine",
                side_effect=lambda _: create_engine(self.database_url),
            ),
            patch(
                "backend.app.api.v1.recommendations.create_database_engine",
                side_effect=lambda _: create_engine(self.database_url),
            ),
        ]
        for item in self.patches:
            item.start()
        self.client = TestClient(create_app(Settings(database_url=self.database_url)))

    def tearDown(self):
        self.client.close()
        for item in reversed(self.patches):
            item.stop()
        self.directory.cleanup()

    def test_complete_session_returns_only_published_loans_and_safe_details(self):
        missing = self.client.post("/api/v1/recommendations", json={"sessionId": "missing"})
        self.assertEqual(missing.status_code, 404)
        started = self.client.post("/api/v1/questionnaire/sessions")
        self.assertEqual(started.status_code, 201)
        session_id = started.json()["sessionId"]
        incomplete = self.client.post("/api/v1/recommendations", json={"sessionId": session_id})
        self.assertEqual(incomplete.status_code, 422)
        for question in self.questionnaire["questions"]:
            written = self.client.put(
                f"/api/v1/questionnaire/sessions/{session_id}/answers/{question['questionId']}",
                json={"answerId": question["answerOptions"][0]["answerId"]},
            )
            self.assertEqual(written.status_code, 200)
        result = self.client.post("/api/v1/recommendations", json={"sessionId": session_id})
        self.assertEqual(result.status_code, 200, result.text)
        body = result.json()
        self.assertEqual(body["configVersion"], "1.1.0")
        self.assertEqual(len(body["needsReview"]), 14)
        self.assertLessEqual(len(body["rankedRecommendations"]), 88)
        self.assertEqual(
            len(body["rankedRecommendations"]) + len(body["needsReview"]) + (88 - len(body["rankedRecommendations"])),
            102,
        )
        self.assertTrue(all(0.5 <= item["compatibilityScore"] <= 1 for item in body["rankedRecommendations"]))
        self.assertTrue(all("compatibilityScore" not in item for item in body["needsReview"]))
        self.assertNotIn(session_id, result.text)
        loan_id = body["rankedRecommendations"][0]["loanId"]
        detail = self.client.get(f"/api/v1/loans/{loan_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertTrue(detail.json()["conditions"])
        self.assertEqual(
            self.client.post("/api/v1/recommendations", json={"sessionId": session_id, "score": 1}).status_code, 422
        )

    def test_source_cell_weights_and_neutral_rule(self):
        impacts = (
            CategoryImpact("maxAmount", "high", "Q1.first", Decimal("0.4"), Decimal("0.5"), 4, 3),
            CategoryImpact("depositRequired", "yes", "Q2.first", Decimal("0.6"), Decimal("0.5"), 5, 3),
            *(
                CategoryImpact(variable, "good", "Q3.first", Decimal("1"), Decimal("1"), 6, 3)
                for variable in ("monthlyInstallment", "maxRepaymentMonths", "interestRate")
            ),
        )
        core = {variable: "good" for variable in ("monthlyInstallment", "maxRepaymentMonths", "interestRate")}
        candidates = (
            LoanCandidate("b", {**core, "maxAmount": "high", "depositRequired": "yes"}),
            LoanCandidate(
                "a",
                {**core, "maxAmount": "high", "depositRequired": None},
                {"depositRequired": ClassificationState.UNKNOWN},
            ),
            LoanCandidate("review", {**core, "maxAmount": None, "depositRequired": "yes"}),
        )
        partition = score_official_categories(candidates, impacts)
        self.assertEqual([item.loan_id for item in partition.ranked], ["a"])
        self.assertEqual(partition.below_threshold, ("b",))
        self.assertEqual(partition.evidence["a"][2], ("depositRequired",))
        self.assertEqual(partition.needs_review[0].loan_id, "review")
