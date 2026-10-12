"""Clock-controlled contract tests: absolute hour, no restore renewal and shared SQL semantics."""

import unittest
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app.accounts.access import AccessFailure, AccountAccess, MockOtpProvider, digest
from backend.app.accounts.profile_repository import ensure_profile
from backend.app.accounts.sqlalchemy_access import SqlAlchemyAccountAccess
from backend.app.infrastructure.db.models import AccountAccessSession, Base


class MemorySessionClockTests(unittest.TestCase):
    def test_3599_3600_and_restore_never_renew(self):
        now = 0.0
        service = AccountAccess(MockOtpProvider(), lambda: now)
        challenge = service.request_code("09000000001", "client")
        token = service.verify_code(challenge, "123456")
        service.bind_account(token, uuid4())
        self.assertEqual(service.remaining(token), 3600)
        now = 3599
        self.assertEqual(service.remaining(token), 1)
        self.assertEqual(service.remaining(token), 1)
        now = 3600
        with self.assertRaises(AccessFailure):
            service.actor(token)


class SqlSessionClockTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.now = datetime(2026, 10, 12, tzinfo=UTC)
        self.service = SqlAlchemyAccountAccess(MockOtpProvider(), self.db, lambda: self.now)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def login(self):
        challenge = self.service.request_code("09000000001", "client")
        token = self.service.verify_code(challenge, "123456")
        actor = ensure_profile(self.service.verified_phone(token), self.db)
        self.service.bind_account(token, actor.account_id)
        return token, actor

    def test_absolute_expiry_and_digest_only_row(self):
        token, actor = self.login()
        row = self.db.scalar(select(AccountAccessSession))
        self.assertEqual(row.token_digest, digest(token))
        self.assertNotEqual(row.token_digest, token)
        self.assertEqual(row.account_id, actor.account_id)
        expires = row.expires_at
        self.now += timedelta(seconds=3599)
        self.assertEqual(self.service.remaining(token), 1)
        self.assertEqual(self.service.remaining(token), 1)
        self.assertEqual(self.db.scalar(select(AccountAccessSession)).expires_at, expires)
        self.now += timedelta(seconds=1)
        with self.assertRaises(AccessFailure):
            self.service.actor(token)

    def test_logout_revocation_is_visible_to_another_store(self):
        token, actor = self.login()
        another = SqlAlchemyAccountAccess(MockOtpProvider(), self.db, lambda: self.now)
        self.assertEqual(another.actor(token), actor.account_id)
        self.service.revoke(token)
        with self.assertRaises(AccessFailure):
            another.actor(token)
        self.service.revoke(token)  # Repeated logout cannot restore a credential.
        row = self.db.scalar(select(AccountAccessSession))
        self.assertIsNotNone(row.revoked_at)

    def test_shared_challenge_attempts_single_use_and_quota(self):
        challenge = self.service.request_code("09000000001", "client")
        other = SqlAlchemyAccountAccess(MockOtpProvider(), self.db, lambda: self.now)
        for _ in range(5):
            with self.assertRaises(AccessFailure):
                other.verify_code(challenge, "000000")
        with self.assertRaises(AccessFailure):
            self.service.verify_code(challenge, "123456")
        for _ in range(4):
            other.request_code("09000000001", "client")
        with self.assertRaises(AccessFailure) as raised:
            self.service.request_code("09000000002", "client")
        self.assertEqual(raised.exception.status, 429)
        self.now += timedelta(seconds=121)
        challenge = self.service.request_code("09000000001", "client")
        token = other.verify_code(challenge, "123456")
        self.assertEqual(other.verified_phone(token), "09000000001")
        with self.assertRaises(AccessFailure):
            self.service.verify_code(challenge, "123456")
