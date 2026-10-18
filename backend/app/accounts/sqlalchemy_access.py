"""Request-scoped PostgreSQL account access: shared challenge/quota and durable revocation.

Only token/challenge digests persist. PostgreSQL's clock is authoritative across
workers. A short advisory transaction lock serializes quota/OTP consumption and
bounded cleanup. No database Session or positive credential cache is shared in
process memory; pending verified phone exists only until this request binds it.
"""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from math import ceil
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.accounts.access import AccessFailure, AccountAccess, OtpProvider, digest
from backend.app.accounts.identity import require_active_account
from backend.app.infrastructure.db.models import AccountAccessSession, AccountOtpChallenge, AccountOtpQuotaEvent


class SqlAlchemyAccountAccess(AccountAccess):
    persistent = True

    def __init__(self, provider: OtpProvider | None, db: Session, clock: Callable[[], datetime] | None = None) -> None:
        super().__init__(provider)
        self.db = db
        self.test_clock = clock
        self.pending: dict[str, str] = {}

    def _now(self) -> datetime:
        if self.test_clock is not None:
            return self.test_clock()
        if self.db.bind is not None and self.db.bind.dialect.name == "postgresql":
            now = self.db.scalar(select(func.clock_timestamp()))
            if not isinstance(now, datetime):
                raise AccessFailure(503)
            return now
        return datetime.now(UTC)  # SQLite is only a local/test contract oracle.

    @contextmanager
    def _write(self) -> Iterator[None]:
        try:
            # Fixed server-owned lock namespace, database-local; callers cannot
            # manufacture dimensions to bypass global bounds or races.
            if self.db.bind is not None and self.db.bind.dialect.name == "postgresql":
                self.db.execute(select(func.pg_advisory_xact_lock(110203)))
            yield
            self.db.commit()
        except AccessFailure:
            try:
                self.db.commit()  # Persist attempts/consumption and bounded expiry cleanup.
            except SQLAlchemyError:
                self.db.rollback()
                raise AccessFailure(503) from None
            raise
        except Exception:
            self.db.rollback()
            raise AccessFailure(503) from None

    def _prune_rows(self, now: datetime) -> None:
        self.db.execute(delete(AccountOtpChallenge).where(AccountOtpChallenge.expires_at <= now))
        self.db.execute(
            delete(AccountOtpQuotaEvent).where(AccountOtpQuotaEvent.occurred_at <= now - timedelta(seconds=120))
        )
        self.db.execute(delete(AccountAccessSession).where(AccountAccessSession.expires_at <= now))

    def request_code(self, phone: str, client: str) -> str:
        self._enabled()
        import secrets

        with self._write():
            now = self._now()
            self._prune_rows(now)
            keys = ("phone:" + digest(phone), "client:" + digest(client))
            counts = self.db.execute(
                select(AccountOtpQuotaEvent.quota_key, func.count())
                .where(AccountOtpQuotaEvent.quota_key.in_(keys))
                .group_by(AccountOtpQuotaEvent.quota_key)
            ).all()
            if any(count >= 5 for _, count in counts):
                raise AccessFailure(429)
            if (self.db.scalar(select(func.count()).select_from(AccountOtpChallenge)) or 0) >= 1024:
                raise AccessFailure(429)
            if (self.db.scalar(select(func.count(func.distinct(AccountOtpQuotaEvent.quota_key)))) or 0) >= 2048:
                raise AccessFailure(429)
            for key in keys:
                self.db.add(AccountOtpQuotaEvent(quota_key=key, occurred_at=now))
            challenge = (self.provider.challenge_prefix if self.provider else "") + secrets.token_urlsafe(32)
            self.db.add(
                AccountOtpChallenge(
                    challenge_digest=digest(challenge),
                    phone=phone,
                    created_at=now,
                    expires_at=now + timedelta(seconds=120),
                    attempts=0,
                )
            )
        # Quota and challenge are committed before I/O, so concurrent workers
        # see the reservation. A timeout is ambiguous: never automatically retry.
        try:
            if self.provider is not None:
                self.provider.send(phone, challenge)
        except Exception:
            with self._write():
                self.db.execute(
                    update(AccountOtpChallenge)
                    .where(AccountOtpChallenge.challenge_digest == digest(challenge))
                    .values(consumed_at=self._now())
                )
            raise AccessFailure(503) from None
        return challenge

    def verify_code(self, challenge_id: str, code: str) -> str:
        self._enabled()
        import secrets

        with self._write():
            now = self._now()
            self._prune_rows(now)
            row = self.db.scalar(
                select(AccountOtpChallenge)
                .where(AccountOtpChallenge.challenge_digest == digest(challenge_id))
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if row is None or row.consumed_at is not None or row.attempts >= 5:
                raise AccessFailure(401)
            row.attempts += 1
            if self.provider is None or not self.provider.verify(code, challenge_id):
                if row.attempts >= 5:
                    row.consumed_at = now
                raise AccessFailure(401)
            row.consumed_at = now
            phone = row.phone
        token = secrets.token_urlsafe(32)
        self.pending[digest(token)] = phone
        return token

    def verified_phone(self, token: str) -> str:
        self._enabled()
        phone = self.pending.get(digest(token))
        if phone is None:
            raise AccessFailure(401)
        return phone

    def bind_account(self, token: str, account_id: UUID) -> None:
        phone = self.verified_phone(token)
        with self._write():
            actor = require_active_account(account_id, self.db)
            if actor.phone != phone:
                raise AccessFailure(401)
            now = self._now()
            self._prune_rows(now)
            if (
                self.db.scalar(
                    select(func.count())
                    .select_from(AccountAccessSession)
                    .where(AccountAccessSession.revoked_at.is_(None))
                )
                or 0
            ) >= 1024:
                raise AccessFailure(429)
            self.db.add(
                AccountAccessSession(
                    token_digest=digest(token),
                    account_id=account_id,
                    issued_at=now,
                    expires_at=now + timedelta(seconds=3600),
                )
            )
        self.pending.pop(digest(token), None)

    def _valid_session(self, token: str) -> AccountAccessSession:
        self._enabled()
        try:
            # Establish immutable ID without holding a session lock, then lock
            # account before credential. Archive G uses the same order, avoiding
            # account/session lock inversion. Neither lookup is a phone resolver.
            account_id = self.db.scalar(
                select(AccountAccessSession.account_id).where(AccountAccessSession.token_digest == digest(token))
            )
            if account_id is None:
                raise AccessFailure(401)
            require_active_account(account_id, self.db)
            row = self.db.scalar(
                select(AccountAccessSession)
                .where(AccountAccessSession.token_digest == digest(token))
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            now = self._now()
            if row is None or row.revoked_at is not None:
                raise AccessFailure(401)
            expires = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)
            if now >= expires:
                raise AccessFailure(401)
            return row
        except SQLAlchemyError:
            self.db.rollback()
            raise AccessFailure(503) from None

    def actor(self, token: str) -> UUID:
        return self._valid_session(token).account_id

    def remaining(self, token: str) -> int:
        row = self._valid_session(token)
        expiry = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)
        try:
            remaining = ceil((expiry - self._now()).total_seconds())
        except SQLAlchemyError:
            self.db.rollback()
            raise AccessFailure(503) from None
        if remaining <= 0:
            raise AccessFailure(401)
        return remaining

    def revoke(self, token: str) -> None:
        self.pending.pop(digest(token), None)
        try:
            now = self._now()
            self.db.execute(
                update(AccountAccessSession)
                .where(AccountAccessSession.token_digest == digest(token), AccountAccessSession.revoked_at.is_(None))
                .values(revoked_at=now)
            )
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise AccessFailure(503) from None

