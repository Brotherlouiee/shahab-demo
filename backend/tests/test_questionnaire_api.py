"""US-07.T04 API tests for body-only anonymous questionnaire progress."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import SecretStr

from backend.app.core.config import AppEnvironment, Settings
from backend.app.main import create_app
from backend.app.questionnaire.infrastructure.proof import PROOF_COOKIE_PREFIX

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

    def _complete_entry_steps(self, session_id: str) -> None:
        for step_id, answer_id in (("loan_type", "shahab"), ("entity_type", "person")):
            response = self.client.put(
                f"/api/v1/questionnaire/sessions/{session_id}/flow-answers/{step_id}",
                json={"answerId": answer_id},
            )
            self.assertEqual(response.status_code, 200)

    def test_current_session_is_recovered_only_from_the_matching_http_only_proof_cookie(self) -> None:
        missing = self.client.get("/api/v1/questionnaire/sessions/current")
        self.assertEqual(missing.status_code, 200)
        self.assertIsNone(missing.json())
        self.assertEqual(missing.headers["Cache-Control"], "no-store")

        started = self.client.post("/api/v1/questionnaire/sessions")
        session_id = started.json()["sessionId"]
        self._complete_entry_steps(session_id)
        self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/answers/Q1",
            json={"answerId": "Q1.incomeInvestment"},
        )
        proof_cookie = PROOF_COOKIE_PREFIX + session_id
        with TestClient(self.client.app) as forged:
            forged.cookies.set(proof_cookie, "A" * 43, path="/api/v1")
            self.assertIsNone(forged.get("/api/v1/questionnaire/sessions/current").json())
        resumed = self.client.get("/api/v1/questionnaire/sessions/current")
        self.assertEqual(resumed.status_code, 200)
        self.assertEqual(resumed.json()["sessionId"], session_id)
        self.assertEqual(resumed.json()["answers"], {"Q1": "Q1.incomeInvestment"})
        self.assertEqual(resumed.json()["flowAnswers"], {"loan_type": "shahab", "entity_type": "person"})
        self.assertNotIn("proof", resumed.text)
        self.assertEqual(resumed.headers["Cache-Control"], "no-store")

    def test_entry_answers_are_required_ordered_and_resumed(self) -> None:
        session_id = self.client.post("/api/v1/questionnaire/sessions").json()["sessionId"]
        canonical = self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/answers/Q1",
            json={"answerId": "Q1.incomeInvestment"},
        )
        self.assertEqual(canonical.status_code, 422)
        skipped = self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/flow-answers/entity_type",
            json={"answerId": "person"},
        )
        self.assertEqual(skipped.status_code, 422)
        first = self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/flow-answers/loan_type",
            json={"answerId": "bank"},
        )
        self.assertEqual(first.status_code, 200)
        second = self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/flow-answers/entity_type",
            json={"answerId": "person"},
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            self.client.get(f"/api/v1/questionnaire/sessions/{session_id}").json()["flowAnswers"],
            {"loan_type": "bank", "entity_type": "person"},
        )
        accepted = self.client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/answers/Q1",
            json={"answerId": "Q1.incomeInvestment"},
        )
        self.assertEqual(accepted.status_code, 200)

    def test_session_writes_and_resumes_only_canonical_answers(self) -> None:
        started = self.client.post("/api/v1/questionnaire/sessions")
        self.assertEqual(started.status_code, 201)
        session_id = started.json()["sessionId"]
        self._complete_entry_steps(session_id)
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
        self._complete_entry_steps(session_id)
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
                self._complete_entry_steps(session_id)
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
