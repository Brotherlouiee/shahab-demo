"""Exercise the live recommendation path on CI's disposable PostgreSQL service."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.core.config import Settings
from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from backend.app.main import create_app
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config

DATABASE_URL = os.environ.get("SHAHAB_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(DATABASE_URL, "requires disposable PostgreSQL service")
class LivePostgresqlRecommendationTests(unittest.TestCase):
    def _migrate(self, direction: str) -> None:
        subprocess.run(
            [
                sys.executable,
                "-c",
                "from alembic.config import main; main()",
                direction,
                "head" if direction == "upgrade" else "base",
            ],
            cwd=ROOT,
            env={**os.environ, "SHAHAB_DATABASE_URL": str(DATABASE_URL)},
            check=True,
            capture_output=True,
            text=True,
        )

    def test_real_postgresql_session_approved_score_and_conditions(self) -> None:
        self._migrate("upgrade")
        try:
            questionnaire = json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text())
            identifiers = json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text())
            engine = create_engine(str(DATABASE_URL))
            try:
                with Session(engine) as session, session.begin():
                    materialize_official_sources(
                        session,
                        loan_manifest=build_manifest(),
                        config_manifest=build_config(),
                        questionnaire=questionnaire,
                        identifiers=identifiers,
                        actor_reference="CI-reviewed-fixture",
                        approval_reason="source-backed integration regression",
                    )
            finally:
                engine.dispose()
            with TestClient(create_app(Settings(database_url=str(DATABASE_URL)))) as client:
                requested = client.post("/api/v1/account-access/request", json={"phone": "09000000001"})
                self.assertEqual(requested.status_code, 200, requested.text)
                verified = client.post(
                    "/api/v1/account-access/verify",
                    json={"challengeId": requested.json()["challengeId"], "code": "123456"},
                )
                self.assertEqual(verified.status_code, 200, verified.text)
                headers = {"Authorization": f"Bearer {verified.json()['accessToken']}"}
                session_id = client.post("/api/v1/questionnaire/sessions").json()["sessionId"]
                for question in questionnaire["questions"]:
                    response = client.put(
                        f"/api/v1/questionnaire/sessions/{session_id}/answers/{question['questionId']}",
                        json={"answerId": question["answerOptions"][0]["answerId"]},
                    )
                    self.assertEqual(response.status_code, 200)
                result = client.post("/api/v1/recommendations", headers=headers, json={"sessionId": session_id})
                self.assertEqual(result.status_code, 200, result.text)
                body = result.json()
                self.assertEqual(len(body["needsReview"]), 14)
                self.assertTrue(body["rankedRecommendations"])
                self.assertEqual(
                    len(body["rankedRecommendations"])
                    + len(body["lowCompatibilityRecommendations"])
                    + len(body["needsReview"]),
                    102,
                )
                self.assertTrue(
                    all(item["compatibilityScore"] < 0.5 for item in body["lowCompatibilityRecommendations"])
                )
                history = client.get("/api/v1/recommendation-history", headers=headers)
                self.assertEqual(history.status_code, 200, history.text)
                self.assertEqual(len(history.json()["items"]), 1)
                stored = client.get(
                    f"/api/v1/recommendation-history/{history.json()['items'][0]['historyId']}",
                    headers=headers,
                )
                self.assertEqual(stored.status_code, 200, stored.text)
                self.assertEqual(stored.json(), body)
                loan_id = body["rankedRecommendations"][0]["loanId"]
                detail = client.get(f"/api/v1/loans/{loan_id}")
                self.assertEqual(detail.status_code, 200)
                self.assertTrue(detail.json()["conditions"])
        finally:
            self._migrate("downgrade")
