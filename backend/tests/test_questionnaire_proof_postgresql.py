"""Real PostgreSQL proof persistence, negative access and additive migration regression."""

import json
import os
import unittest
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
from sqlalchemy.exc import DBAPIError

from backend.app.core.config import Settings
from backend.app.main import create_app
from backend.app.questionnaire.infrastructure.proof import PROOF_COOKIE_PREFIX
from backend.tests import test_account_identity_postgresql as fixture


@unittest.skipUnless(os.environ.get("SHAHAB_TEST_DATABASE_URL"), "requires real PostgreSQL")
class QuestionnaireProofPostgreSqlTests(unittest.TestCase):
    setUp = fixture.AccountIdentityPostgreSqlTests.setUp
    tearDown = fixture.AccountIdentityPostgreSqlTests.tearDown
    alembic = fixture.AccountIdentityPostgreSqlTests.alembic
    legacy_fixture = fixture.AccountIdentityPostgreSqlTests.legacy_fixture
    retained = fixture.AccountIdentityPostgreSqlTests.retained

    def test_legacy_rows_retained_without_fabricated_proof_and_safe_downgrade(self):
        sid, _ = self.legacy_fixture()
        before = self.retained()
        self.alembic("upgrade", "head")
        self.assertEqual(before, self.retained())
        with self.engine.connect() as connection:
            self.assertIsNone(
                connection.scalar(
                    text("SELECT creator_proof_digest FROM questionnaire_sessions WHERE questionnaire_session_id=:sid"),
                    {"sid": sid},
                )
            )
        with TestClient(create_app(Settings(database_url=str(fixture.DATABASE_URL)))) as client:
            client.cookies.set(PROOF_COOKIE_PREFIX + str(sid), "1", path="/api/v1")
            response = client.get(f"/api/v1/questionnaire/sessions/{sid}")
            self.assertEqual(response.status_code, 403)
        self.alembic("downgrade", "aa11b02a2002")
        self.assertNotIn(
            "creator_proof_digest", {c["name"] for c in inspect(self.engine).get_columns("questionnaire_sessions")}
        )
        self.assertEqual(before, self.retained())
        self.alembic("upgrade", "head")
        self.assertEqual(before, self.retained())

    def test_restart_and_two_clients_never_trust_id_or_redis_metadata(self):
        self.alembic("upgrade", "head")
        url = str(fixture.DATABASE_URL)
        with TestClient(create_app(Settings(database_url=url))) as creator:
            started = creator.post("/api/v1/questionnaire/sessions")
            self.assertEqual(started.status_code, 201)
            sid = started.json()["sessionId"]
            proof = creator.cookies.get(PROOF_COOKIE_PREFIX + sid)
            wrote = creator.put(
                f"/api/v1/questionnaire/sessions/{sid}/answers/Q1", json={"answerId": "Q1.incomeInvestment"}
            )
            self.assertEqual(wrote.status_code, 200)
        with TestClient(create_app(Settings(database_url=url))) as restarted:
            self.assertEqual(restarted.get(f"/api/v1/questionnaire/sessions/{sid}").status_code, 403)
            restarted.cookies.set(PROOF_COOKIE_PREFIX + sid, "1", path="/api/v1")
            self.assertEqual(restarted.get(f"/api/v1/questionnaire/sessions/{sid}").status_code, 403)
            restarted.cookies.clear()
            restarted.cookies.set(PROOF_COOKIE_PREFIX + sid, proof, path="/api/v1")
            resumed = restarted.get(f"/api/v1/questionnaire/sessions/{sid}")
            self.assertEqual(resumed.status_code, 200)
            self.assertEqual(resumed.json()["answers"], {"Q1": "Q1.incomeInvestment"})
            self.assertEqual(resumed.json()["expiresAt"], started.json()["expiresAt"])
        with self.assertRaises(DBAPIError), self.engine.begin() as connection:
            connection.execute(
                text("UPDATE questionnaire_sessions SET creator_proof_digest=:d WHERE questionnaire_session_id=:sid"),
                {"d": "a" * 64, "sid": UUID(sid)},
            )
        with self.engine.connect() as connection:
            self.assertEqual(connection.scalar(text("SELECT count(*) FROM questionnaire_answers")), 1)

    def test_two_accounts_cannot_read_write_or_claim_another_bound_questionnaire(self):
        self.legacy_fixture()
        self.alembic("upgrade", "head")
        url = str(fixture.DATABASE_URL)
        with TestClient(create_app(Settings(database_url=url))) as owner:

            def login(client, phone):
                challenge = client.post("/api/v1/account-access/request", json={"phone": phone}).json()
                result = client.post(
                    "/api/v1/account-access/verify", json={"challengeId": challenge["challengeId"], "code": "123456"}
                )
                self.assertEqual(result.status_code, 200)
                return {"Authorization": "Bearer " + result.json()["accessToken"]}

            headers = login(owner, "09000000001")
            sid = owner.post("/api/v1/questionnaire/sessions").json()["sessionId"]
            configuration = json.loads(
                (fixture.ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text()
            )
            for question in configuration["questions"]:
                result = owner.put(
                    f"/api/v1/questionnaire/sessions/{sid}/answers/{question['questionId']}",
                    json={"answerId": question["answerOptions"][0]["answerId"]},
                )
                self.assertEqual(result.status_code, 200)
            self.assertEqual(
                owner.post("/api/v1/recommendations", headers=headers, json={"sessionId": sid}).status_code, 200
            )
            proof = owner.cookies.get(PROOF_COOKIE_PREFIX + sid)
            with TestClient(create_app(Settings(database_url=url))) as attacker:
                other = login(attacker, "09000000002")
                attacker.cookies.set(PROOF_COOKIE_PREFIX + sid, proof, path="/api/v1")
                for method, path, body in (
                    ("GET", f"/api/v1/questionnaire/sessions/{sid}", None),
                    ("PUT", f"/api/v1/questionnaire/sessions/{sid}/answers/Q1", {"answerId": "Q1.incomeInvestment"}),
                    ("POST", "/api/v1/recommendations", {"sessionId": sid}),
                ):
                    result = attacker.request(method, path, headers=other, json=body)
                    self.assertEqual(result.status_code, 403, result.text)
            self.assertEqual(
                owner.post("/api/v1/recommendations", headers=headers, json={"sessionId": sid}).status_code, 200
            )
        with self.engine.connect() as connection:
            self.assertEqual(connection.scalar(text("SELECT count(*) FROM recommendation_history_runs")), 2)
