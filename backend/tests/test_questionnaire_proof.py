"""F01 regression: two clients/accounts, no answer disclosure or unauthorized persistence."""

import hashlib
import unittest
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import QuestionnaireAnswer, QuestionnaireSession, RecommendationHistoryRun
from backend.app.questionnaire.infrastructure.proof import PROOF_COOKIE_PREFIX
from backend.tests import test_recommendation_history_api as fixture


class QuestionnaireProofTests(unittest.TestCase):
    setUpClass = classmethod(fixture.RecommendationHistoryApiTests.setUpClass.__func__)
    setUp = fixture.RecommendationHistoryApiTests.setUp
    tearDown = fixture.RecommendationHistoryApiTests.tearDown
    login = fixture.RecommendationHistoryApiTests.login
    completed_session = fixture.RecommendationHistoryApiTests.completed_session

    def paths(self, sid):
        return (
            ("GET", f"/api/v1/questionnaire/sessions/{sid}", None),
            ("PUT", f"/api/v1/questionnaire/sessions/{sid}/answers/Q1", {"answerId": "Q1.incomeInvestment"}),
            ("POST", "/api/v1/recommendations", {"sessionId": sid}),
        )

    def denied(self, client, sid, headers=None, status=403):
        for method, path, body in self.paths(sid):
            response = client.request(method, path, json=body, headers=headers or {})
            self.assertEqual(response.status_code, status, response.text)
            self.assertNotIn("answers", response.json())
            self.assertNotIn("rankedRecommendations", response.json())

    def test_id_constant_forged_and_other_session_proof_never_read_write_or_claim(self):
        sid = self.completed_session()
        proof = self.client.cookies.get(PROOF_COOKIE_PREFIX + sid)
        other_sid = self.client.post("/api/v1/questionnaire/sessions").json()["sessionId"]
        other_proof = self.client.cookies.get(PROOF_COOKIE_PREFIX + other_sid)
        self.assertEqual(len(proof), 43)
        self.assertNotEqual(proof, other_proof)
        with Session(self.client.app.state.database_engine) as db:
            before = db.scalar(select(func.count()).select_from(QuestionnaireAnswer))
            stored = db.get(QuestionnaireSession, UUID(sid))
            self.assertEqual(stored.creator_proof_digest, hashlib.sha256(proof.encode()).hexdigest())
            self.assertNotEqual(stored.creator_proof_digest, proof)
        with TestClient(self.client.app) as attacker:
            for value in (None, "1", "A" * 43, other_proof):
                attacker.cookies.clear()
                if value is not None:
                    attacker.cookies.set(PROOF_COOKIE_PREFIX + sid, value, path="/api/v1")
                self.denied(attacker, sid)
        with Session(self.client.app.state.database_engine) as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(QuestionnaireAnswer)), before)
            self.assertIsNone(db.get(QuestionnaireSession, UUID(sid)).owner_account_id)
            self.assertEqual(db.scalar(select(func.count()).select_from(RecommendationHistoryRun)), 0)
        self.assertEqual(self.client.get(f"/api/v1/questionnaire/sessions/{sid}").status_code, 200)

    def test_bound_account_requires_both_creator_proof_and_exact_account_generation(self):
        owner = self.login("09000000001")
        sid = self.completed_session()
        proof = self.client.cookies.get(PROOF_COOKIE_PREFIX + sid)
        self.assertEqual(
            self.client.post("/api/v1/recommendations", headers=owner, json={"sessionId": sid}).status_code, 200
        )
        with TestClient(self.client.app) as other:
            challenge = other.post("/api/v1/account-access/request", json={"phone": "09000000002"}).json()
            result = other.post(
                "/api/v1/account-access/verify", json={"challengeId": challenge["challengeId"], "code": "123456"}
            )
            other.cookies.set(PROOF_COOKIE_PREFIX + sid, proof, path="/api/v1")
            self.denied(other, sid, {"Authorization": "Bearer " + result.json()["accessToken"]})
            other.cookies.clear()
            other.cookies.set(PROOF_COOKIE_PREFIX + sid, proof, path="/api/v1")
            self.denied(other, sid)  # Owner proof alone cannot read a bound account after logout.
        self.assertEqual(self.client.get(f"/api/v1/questionnaire/sessions/{sid}", headers=owner).status_code, 200)
        self.assertEqual(
            self.client.post("/api/v1/recommendations", headers=owner, json={"sessionId": sid}).status_code, 200
        )
        with Session(self.client.app.state.database_engine) as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(RecommendationHistoryRun)), 1)

    def test_valid_expired_proof_is_410_and_refresh_never_renews_it(self):
        sid = self.completed_session()
        engine = self.client.app.state.database_engine
        with Session(engine) as db:
            original = db.get(QuestionnaireSession, UUID(sid)).expires_at
        resumed = self.client.get(f"/api/v1/questionnaire/sessions/{sid}")
        self.assertEqual(resumed.status_code, 200)
        self.assertNotIn("set-cookie", resumed.headers)
        with Session(engine) as db:
            row = db.get(QuestionnaireSession, UUID(sid))
            self.assertEqual(row.expires_at, original)
            row.created_at = datetime.now(UTC) - timedelta(minutes=40)
            row.expires_at = datetime.now(UTC) - timedelta(minutes=10)
            db.commit()
        self.denied(self.client, sid, status=410)

    def test_secret_not_in_response_and_cookie_flags_are_preserved(self):
        response = self.client.post("/api/v1/questionnaire/sessions")
        sid = response.json()["sessionId"]
        secret = self.client.cookies.get(PROOF_COOKIE_PREFIX + sid)
        self.assertNotIn(secret, response.text)
        self.assertNotIn("proof", response.text)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        for flag in ("HttpOnly", "SameSite=lax", "Path=/api/v1", "Max-Age=1800"):
            self.assertIn(flag, response.headers["set-cookie"])
