"""Recommendation-history ownership, persistence and immutable-read regression."""

from __future__ import annotations

import json
import tempfile
import unittest
from uuid import UUID
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.app.core.config import Settings
from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from backend.app.infrastructure.db.models import Base, RecommendationHistoryRun
from backend.app.main import create_app
from backend.app.recommendation.infrastructure.history import RecommendationHistoryRepository
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config

ROOT = Path(__file__).resolve().parents[2]


class RecommendationHistoryApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loan_manifest = build_manifest()
        cls.config_manifest = build_config()
        cls.questionnaire = json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text())
        cls.identifiers = json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text())

    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.database_url = f"sqlite+pysqlite:///{self.directory.name}/history.sqlite"
        engine = create_engine(self.database_url)
        Base.metadata.create_all(engine)
        with Session(engine) as session, session.begin():
            materialize_official_sources(
                session,
                loan_manifest=self.loan_manifest,
                config_manifest=self.config_manifest,
                questionnaire=self.questionnaire,
                identifiers=self.identifiers,
                actor_reference="history-test",
                approval_reason="history integration fixture",
            )
        engine.dispose()
        self.client = TestClient(create_app(Settings(database_url=self.database_url)), raise_server_exceptions=False)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        self.directory.cleanup()

    def login(self, phone: str) -> dict[str, str]:
        requested = self.client.post("/api/v1/account-access/request", json={"phone": phone})
        self.assertEqual(requested.status_code, 200, requested.text)
        verified = self.client.post(
            "/api/v1/account-access/verify",
            json={"challengeId": requested.json()["challengeId"], "code": "123456"},
        )
        self.assertEqual(verified.status_code, 200, verified.text)
        return {"Authorization": f"Bearer {verified.json()['accessToken']}"}

    def completed_session(self) -> str:
        started = self.client.post("/api/v1/questionnaire/sessions")
        self.assertEqual(started.status_code, 201)
        session_id = started.json()["sessionId"]
        for question in self.questionnaire["questions"]:
            response = self.client.put(
                f"/api/v1/questionnaire/sessions/{session_id}/answers/{question['questionId']}",
                json={"answerId": question["answerOptions"][0]["answerId"]},
            )
            self.assertEqual(response.status_code, 200, response.text)
        return session_id

    def test_authenticated_result_persists_once_and_is_owner_scoped(self) -> None:
        owner = self.login("09000000001")
        session_id = self.completed_session()
        first = self.client.post("/api/v1/recommendations", headers=owner, json={"sessionId": session_id})
        self.assertEqual(first.status_code, 200, first.text)
        repeated = self.client.post("/api/v1/recommendations", headers=owner, json={"sessionId": session_id})
        self.assertEqual(repeated.status_code, 200, repeated.text)
        self.assertEqual(repeated.json(), first.json())

        page = self.client.get("/api/v1/recommendation-history", headers=owner)
        self.assertEqual(page.status_code, 200, page.text)
        self.assertEqual(len(page.json()["items"]), 1)
        self.assertEqual(page.json()["items"][0]["rankedCount"], len(first.json()["rankedRecommendations"]))
        history_id = page.json()["items"][0]["historyId"]
        detail = self.client.get(f"/api/v1/recommendation-history/{history_id}", headers=owner)
        self.assertEqual(detail.status_code, 200, detail.text)
        self.assertEqual(detail.json()["dataVersion"], first.json()["dataVersion"])
        self.assertEqual(detail.json()["configVersion"], first.json()["configVersion"])
        for key in ("rankedRecommendations", "lowCompatibilityRecommendations", "needsReview"):
            self.assertEqual(
                detail.json()[key],
                first.json()[key],
                f"historical {key} must preserve the original server result",
            )

        attacker = TestClient(self.client.app, raise_server_exceptions=False)
        attacker.__enter__()
        try:
            original_client = self.client
            self.client = attacker
            other = self.login("09000000002")
            self.client = original_client
            self.assertEqual(attacker.get("/api/v1/recommendation-history", headers=other).json()["items"], [])
            self.assertEqual(
                attacker.get(f"/api/v1/recommendation-history/{history_id}", headers=other).status_code,
                404,
            )
            self.assertEqual(
                attacker.post("/api/v1/recommendations", headers=other, json={"sessionId": session_id}).status_code,
                403,
            )
        finally:
            self.client = original_client
            attacker.__exit__(None, None, None)
        verification_engine = create_engine(self.database_url)
        with Session(verification_engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(RecommendationHistoryRun)), 1)
        verification_engine.dispose()

    def test_verified_cookie_restores_history_access_without_bearer_header(self) -> None:
        self.login("09000000001")
        session = self.client.get("/api/v1/account-access/session")
        self.assertEqual(session.status_code, 200, session.text)
        self.assertEqual(session.json()["phone"], "09000000001")

    def test_owner_can_hide_a_history_card_without_deleting_its_audit_snapshot(self) -> None:
        owner = self.login("09000000001")
        session_id = self.completed_session()
        self.assertEqual(
            self.client.post("/api/v1/recommendations", headers=owner, json={"sessionId": session_id}).status_code,
            200,
        )
        history_id = self.client.get("/api/v1/recommendation-history", headers=owner).json()["items"][0]["historyId"]

        hidden = self.client.delete(f"/api/v1/recommendation-history/{history_id}", headers=owner)
        self.assertEqual(hidden.status_code, 204, hidden.text)
        self.assertEqual(self.client.get("/api/v1/recommendation-history", headers=owner).json()["items"], [])
        self.assertEqual(
            self.client.get(f"/api/v1/recommendation-history/{history_id}", headers=owner).status_code, 404
        )

        verification_engine = create_engine(self.database_url)
        with Session(verification_engine) as session:
            retained = session.get(RecommendationHistoryRun, UUID(history_id))
            self.assertIsNotNone(retained)
            self.assertIsNotNone(retained.hidden_at)
        verification_engine.dispose()

    def test_failed_snapshot_write_leaves_no_partial_history(self) -> None:
        owner = self.login("09000000001")
        session_id = self.completed_session()
        with patch.object(RecommendationHistoryRepository, "_add_items", side_effect=RuntimeError("fixture failure")):
            response = self.client.post("/api/v1/recommendations", headers=owner, json={"sessionId": session_id})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.client.get("/api/v1/recommendation-history", headers=owner).json()["items"], [])
