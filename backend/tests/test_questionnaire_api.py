"""US-07.T04 API tests for body-only anonymous questionnaire progress."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import SecretStr

from backend.app.core.config import AppEnvironment, Settings
from backend.app.main import create_app

_QUESTIONNAIRE_CONFIGURATION = json.loads(
    (Path(__file__).resolve().parents[2] / "data/contracts/questionnaire-configuration.v1.json").read_text(
        encoding="utf-8"
    )
)
_CANONICAL_QUESTIONS = _QUESTIONNAIRE_CONFIGURATION["questions"]


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

    def test_rejects_skipping_required_questions_without_persisting_the_answer(self) -> None:
        for answered_count in range(len(_CANONICAL_QUESTIONS)):
            with self.subTest(answered_count=answered_count):
                session_id = self.client.post("/api/v1/questionnaire/sessions").json()["sessionId"]
                expected_answers: dict[str, str] = {}

                for question in _CANONICAL_QUESTIONS[:answered_count]:
                    question_id = question["questionId"]
                    answer_id = question["answerOptions"][0]["answerId"]
                    accepted = self.client.put(
                        f"/api/v1/questionnaire/sessions/{session_id}/answers/{question_id}",
                        json={"answerId": answer_id},
                    )
                    self.assertEqual(accepted.status_code, 200)
                    expected_answers[question_id] = answer_id

                for skipped_question in _CANONICAL_QUESTIONS[answered_count + 1 :]:
                    question_id = skipped_question["questionId"]
                    answer_id = skipped_question["answerOptions"][0]["answerId"]
                    skipped = self.client.put(
                        f"/api/v1/questionnaire/sessions/{session_id}/answers/{question_id}",
                        json={"answerId": answer_id},
                    )
                    self.assertEqual(skipped.status_code, 422, question_id)
                    self.assertEqual(skipped.json()["error"]["code"], "invalid_request")
                    self.assertEqual(
                        self.client.get(f"/api/v1/questionnaire/sessions/{session_id}").json()["answers"],
                        expected_answers,
                    )

    def test_rejects_unproved_sessions_without_disclosing_existence(
        self,
    ) -> None:
        response = self.client.get("/api/v1/questionnaire/sessions/unknown-session")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "forbidden")
        self.assertNotIn("unknown-session", response.json()["error"]["message"])

    def test_rejects_answer_transport_outside_the_json_body(self) -> None:
        session_id = self.client.post("/api/v1/questionnaire/sessions").json()["sessionId"]
        response = self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/answers/Q1?answerId=Q1.incomeInvestment",
            json={},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "invalid_request")
