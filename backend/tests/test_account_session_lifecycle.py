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


class ArchiveAccountSqliteContractTests(unittest.TestCase):
    """SQLite contract checks; concurrency and transactional locking require PostgreSQL."""

    def setUp(self):
        from backend.app.infrastructure.db.models import Base

        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_archive_revokes_all_credentials_and_new_generation_is_empty(self):
        from sqlalchemy import select
        from backend.app.accounts.identity import archive_account
        from backend.app.infrastructure.db.models import Account, AccountAccessSession, UserProfile

        with Session(self.engine) as db:
            provider = MockOtpProvider()
            service = SqlAlchemyAccountAccess(provider, db)
            tokens = []
            for index in range(2):
                challenge = service.request_code("09000000001", f"client{index}")
                token = service.verify_code(challenge, "123456")
                actor = ensure_profile(service.verified_phone(token), db)
                service.bind_account(token, actor.account_id)
                tokens.append(token)
            old_id = actor.account_id
            db.rollback()
            archive_account(old_id, db)
            db.expire_all()
            old = db.get(Account, old_id)
            self.assertEqual(old.status, "archived")
            self.assertIsNotNone(old.archived_at)
            self.assertEqual(db.get(UserProfile, old_id).first_name, "")
            self.assertEqual(
                len(db.scalars(select(AccountAccessSession).where(AccountAccessSession.account_id == old_id)).all()), 2
            )
            for token in tokens:
                with self.assertRaises(AccessFailure):
                    service.actor(token)
            new_actor = ensure_profile("09000000001", db)
            self.assertNotEqual(new_actor.account_id, old_id)
            self.assertEqual(db.get(UserProfile, new_actor.account_id).first_name, "")
            self.assertEqual(db.get(Account, old_id).status, "archived")
            from backend.app.api.errors import ApiError

            with self.assertRaises(ApiError) as failure:
                archive_account(old_id, db)
            self.assertEqual(failure.exception.status_code, 404)
