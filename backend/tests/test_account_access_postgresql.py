"""Shared PostgreSQL account sessions: worker/restart, races, immutable expiry and migration.

Only CI disposable PostgreSQL may use these downgrade/fixture helpers. They are
not commands for resetting the owner's database.
"""

import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from backend.app.accounts.access import AccessFailure, MockOtpProvider, digest
from backend.app.accounts.profile_repository import ensure_profile
from backend.app.accounts.sqlalchemy_access import SqlAlchemyAccountAccess
from backend.app.core.config import Settings
from backend.app.infrastructure.db.models import AccountAccessSession, AccountOtpChallenge
from backend.app.main import create_app
from backend.tests import test_account_identity_postgresql as fixture


@unittest.skipUnless(os.environ.get("SHAHAB_TEST_DATABASE_URL"), "requires real PostgreSQL")
class AccountAccessPostgreSqlTests(unittest.TestCase):
    setUp = fixture.AccountIdentityPostgreSqlTests.setUp
    tearDown = fixture.AccountIdentityPostgreSqlTests.tearDown
    alembic = fixture.AccountIdentityPostgreSqlTests.alembic
    legacy_fixture = fixture.AccountIdentityPostgreSqlTests.legacy_fixture
    retained = fixture.AccountIdentityPostgreSqlTests.retained

    def test_additive_upgrade_and_downgrade_preserve_all_business_facts(self):
        self.legacy_fixture()
        self.alembic("upgrade", "bb11b02b0001")
        before = self.retained()
        self.alembic("upgrade", "head")
        self.assertEqual(before, self.retained())
        self.alembic("downgrade", "bb11b02b0001")
        self.assertEqual(before, self.retained())
        self.alembic("upgrade", "head")
        self.assertEqual(before, self.retained())

    def test_http_request_verify_restore_and_logout_across_workers_and_restart(self):
        self.alembic("upgrade", "head")
        url = str(fixture.DATABASE_URL)
        with TestClient(create_app(Settings(database_url=url))) as worker_a:
            requested = worker_a.post("/api/v1/account-access/request", json={"phone": "09000000001"})
            self.assertEqual(requested.status_code, 200)
            challenge = requested.json()["challengeId"]
        # A fresh app/process has none of the first worker's Python dictionaries.
        with TestClient(create_app(Settings(database_url=url))) as worker_b:
            verified = worker_b.post("/api/v1/account-access/verify", json={"challengeId": challenge, "code": "123456"})
            self.assertEqual(verified.status_code, 200, verified.text)
            self.assertEqual(verified.json()["expiresIn"], 3600)
            self.assertIn("Max-Age=3600", verified.headers["set-cookie"])
            token = verified.json()["accessToken"]
        with TestClient(create_app(Settings(database_url=url))) as worker_c:
            headers = {"Authorization": "Bearer " + token}
            restored = worker_c.get("/api/v1/account-access/session", headers=headers)
            self.assertEqual(restored.status_code, 200)
            self.assertGreater(restored.json()["expiresIn"], 0)
            self.assertLessEqual(restored.json()["expiresIn"], 3600)
            self.assertNotIn("set-cookie", restored.headers)
            self.assertEqual(worker_c.get("/api/v1/profiles/me", headers=headers).status_code, 200)
            with self.engine.connect() as c:
                row = c.execute(text("SELECT token_digest,issued_at,expires_at FROM account_access_sessions")).one()
                self.assertEqual(row[0], digest(token))
                self.assertNotEqual(row[0], token)
                self.assertEqual((row[2] - row[1]).total_seconds(), 3600)
            self.assertEqual(worker_c.post("/api/v1/account-access/logout", headers=headers).status_code, 204)
        with TestClient(create_app(Settings(database_url=url))) as restarted:
            self.assertEqual(restarted.get("/api/v1/profiles/me", headers=headers).status_code, 401)
            self.assertEqual(restarted.get("/api/v1/account-access/session", headers=headers).status_code, 401)
        with self.engine.connect() as c:
            self.assertIsNotNone(
                c.scalar(
                    text("SELECT revoked_at FROM account_access_sessions WHERE token_digest=:t"), {"t": digest(token)}
                )
            )

    def test_database_expiry_is_absolute_and_cannot_be_renewed_by_sql_or_restore(self):
        self.alembic("upgrade", "head")
        now = datetime.now(UTC)
        with Session(self.engine) as db:
            service = SqlAlchemyAccountAccess(MockOtpProvider(), db, lambda: now)
            challenge = service.request_code("09000000001", "client")
            token = service.verify_code(challenge, "123456")
            actor = ensure_profile(service.verified_phone(token), db)
            service.bind_account(token, actor.account_id)
        with Session(self.engine) as db:
            at_3599 = SqlAlchemyAccountAccess(MockOtpProvider(), db, lambda: now + timedelta(seconds=3599))
            self.assertEqual(at_3599.remaining(token), 1)
            self.assertEqual(at_3599.remaining(token), 1)
        with Session(self.engine) as db:
            at_3600 = SqlAlchemyAccountAccess(MockOtpProvider(), db, lambda: now + timedelta(seconds=3600))
            with self.assertRaises(AccessFailure):
                at_3600.actor(token)
        for sql in (
            "UPDATE account_access_sessions SET expires_at=expires_at+interval '1 hour'",
            "UPDATE account_access_sessions SET account_id=gen_random_uuid()",
        ):
            with self.assertRaises(DBAPIError), self.engine.begin() as c:
                c.execute(text(sql))

    def test_two_connections_consume_a_challenge_exactly_once(self):
        self.alembic("upgrade", "head")
        with Session(self.engine) as db:
            challenge = SqlAlchemyAccountAccess(MockOtpProvider(), db).request_code("09000000001", "client")
        barrier = Barrier(2)

        def consume():
            with Session(self.engine) as db:
                service = SqlAlchemyAccountAccess(MockOtpProvider(), db)
                barrier.wait(timeout=10)
                try:
                    token = service.verify_code(challenge, "123456")
                    actor = ensure_profile(service.verified_phone(token), db)
                    service.bind_account(token, actor.account_id)
                    return 200
                except AccessFailure as error:
                    return error.status

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(lambda _: consume(), range(2)))
        self.assertEqual(statuses, [200, 401])
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(AccountAccessSession)), 1)
            self.assertIsNotNone(db.scalar(select(AccountOtpChallenge)).consumed_at)

    def test_shared_quota_attempts_recovery_and_credential_store_failure(self):
        self.alembic("upgrade", "head")
        now = datetime.now(UTC)
        for _ in range(5):
            with Session(self.engine) as db:
                SqlAlchemyAccountAccess(MockOtpProvider(), db, lambda: now).request_code("09000000001", "client")
        with Session(self.engine) as db, self.assertRaises(AccessFailure) as raised:
            SqlAlchemyAccountAccess(MockOtpProvider(), db, lambda: now).request_code("09000000002", "client")
        self.assertEqual(raised.exception.status, 429)
        now += timedelta(seconds=121)
        with Session(self.engine) as db:
            challenge = SqlAlchemyAccountAccess(MockOtpProvider(), db, lambda: now).request_code(
                "09000000001", "client"
            )
        for _ in range(5):
            with Session(self.engine) as db, self.assertRaises(AccessFailure):
                SqlAlchemyAccountAccess(MockOtpProvider(), db, lambda: now).verify_code(challenge, "000000")
        with Session(self.engine) as db, self.assertRaises(AccessFailure):
            SqlAlchemyAccountAccess(MockOtpProvider(), db, lambda: now).verify_code(challenge, "123456")
        with self.engine.begin() as c:
            c.execute(
                text(
                    "CREATE FUNCTION reject_access_fixture() RETURNS trigger LANGUAGE plpgsql AS $$ "
                    "BEGIN RAISE EXCEPTION 'fixture access store failure'; END $$"
                )
            )
            c.execute(
                text(
                    "CREATE TRIGGER reject_access_fixture BEFORE INSERT ON account_access_sessions "
                    "FOR EACH ROW EXECUTE FUNCTION reject_access_fixture()"
                )
            )
        try:
            with TestClient(create_app(Settings(database_url=str(fixture.DATABASE_URL)))) as client:
                # Distinct dimension prevents this failure proof from testing the earlier quota instead.
                challenge = client.post("/api/v1/account-access/request", json={"phone": "09000000002"})
                self.assertEqual(challenge.status_code, 200)
                result = client.post(
                    "/api/v1/account-access/verify",
                    json={"challengeId": challenge.json()["challengeId"], "code": "123456"},
                )
                self.assertEqual(result.status_code, 503, result.text)
                self.assertNotIn("accessToken", result.text)
                self.assertNotIn("fixture access", result.text)
                self.assertNotIn("set-cookie", result.headers)
            with self.engine.connect() as c:
                self.assertEqual(c.scalar(text("SELECT count(*) FROM account_access_sessions")), 0)
        finally:
            with self.engine.begin() as c:
                c.execute(text("DROP TRIGGER reject_access_fixture ON account_access_sessions"))
                c.execute(text("DROP FUNCTION reject_access_fixture()"))

    def test_lookup_without_sms_verifies_after_restart_and_consumes_once_across_connections(self):
        """Real PostgreSQL locking with a fake external boundary; no paid SMS."""
        from backend.tests.test_kavenegar_otp import accepted, provider

        self.alembic("upgrade", "head")
        sent = []

        def deliver(key, parameters, timeout):
            # A separate connection sees the committed reservation while delivery
            # is in progress. PostgreSQL's advisory quota lock must be released.
            with self.engine.begin() as connection:
                self.assertTrue(connection.scalar(text("SELECT pg_try_advisory_xact_lock(110203)")))
                self.assertEqual(connection.scalar(text("SELECT count(*) FROM account_otp_challenges")), 1)
            sent.append(parameters)
            return accepted()

        with Session(self.engine) as db:
            challenge = SqlAlchemyAccountAccess(provider(deliver), db).request_code("09000000001", "client")
        barrier = Barrier(2)

        def consume():
            with Session(self.engine) as db:
                service = SqlAlchemyAccountAccess(provider(), db)
                barrier.wait(timeout=10)
                try:
                    token = service.verify_code(challenge, sent[0]["token"])
                    actor = ensure_profile(service.verified_phone(token), db)
                    service.bind_account(token, actor.account_id)
                    return 200
                except AccessFailure as error:
                    return error.status

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(lambda _: consume(), range(2))), [200, 401])
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(AccountAccessSession)), 1)
            self.assertIsNotNone(db.scalar(select(AccountOtpChallenge)).consumed_at)

    def test_lookup_failure_keeps_committed_quota_and_denies_every_challenge(self):
        from unittest.mock import Mock

        from backend.app.infrastructure.db.models import Account, AccountOtpQuotaEvent
        from backend.tests.test_kavenegar_otp import provider

        self.alembic("upgrade", "head")
        sender = provider(Mock(side_effect=TimeoutError("synthetic unavailable")))
        for _ in range(5):
            with Session(self.engine) as db, self.assertRaises(AccessFailure) as error:
                SqlAlchemyAccountAccess(sender, db).request_code("09000000001", "client")
            self.assertEqual(error.exception.status, 503)
        with Session(self.engine) as db, self.assertRaises(AccessFailure) as error:
            SqlAlchemyAccountAccess(sender, db).request_code("09000000001", "client")
        self.assertEqual(error.exception.status, 429)
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(AccountOtpQuotaEvent)), 10)
            self.assertEqual(db.scalar(select(func.count()).select_from(Account)), 0)
            self.assertTrue(all(row.consumed_at is not None for row in db.scalars(select(AccountOtpChallenge))))

