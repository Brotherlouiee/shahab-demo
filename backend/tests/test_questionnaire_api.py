"""US-07.T04 API tests for body-only anonymous questionnaire progress."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from pydantic import SecretStr

from backend.app.core.config import AppEnvironment, Settings
from backend.app.main import create_app


class QuestionnaireApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(
            create_app(Settings(environment=AppEnvironment.TEST, readiness_token=SecretStr("test-readiness-token"))),
            raise_server_exceptions=False,
        )

    def test_session_writes_and_resumes_only_canonical_answers(self) -> None:
        started = self.client.post("/api/v1/questionnaire/sessions")
        self.assertEqual(started.status_code, 201)
        session_id = started.json()["sessionId"]
        self.assertNotIn("answer", started.request.url.path)

        saved = self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/answers/Q1",
            json={"answerId": "Q1.incomeInvestment"},
        )
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json()["answers"], {"Q1": "Q1.incomeInvestment"})

        resumed = self.client.get(f"/api/v1/questionnaire/sessions/{session_id}")
        self.assertEqual(resumed.status_code, 200)
        self.assertEqual(resumed.json()["answers"], {"Q1": "Q1.incomeInvestment"})

    def test_rejects_an_answer_owned_by_another_question(self) -> None:
        session_id = self.client.post("/api/v1/questionnaire/sessions").json()["sessionId"]
        response = self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/answers/Q1",
            json={"answerId": "Q2.short_term"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "invalid_request")


    def test_rejects_unknown_sessions_with_a_safe_typed_not_found_error(self) -> None:
        response = self.client.get("/api/v1/questionnaire/sessions/unknown-session")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "questionnaire_session_not_found")
        self.assertNotIn("unknown-session", response.json()["error"]["message"])

    def test_rejects_answer_transport_outside_the_json_body(self) -> None:
        session_id = self.client.post("/api/v1/questionnaire/sessions").json()["sessionId"]
        response = self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/answers/Q1?answerId=Q1.incomeInvestment",
            json={},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "invalid_request")
