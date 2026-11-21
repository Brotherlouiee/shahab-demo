"""Bounded OTP access, with opaque revocable sessions.

This memory adapter is only for local/test without a SQL session. Configured
API requests use the shared PostgreSQL adapter. Live providers require that
persistent adapter; a missing database never permits a memory fallback.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from math import ceil
from threading import Lock
from typing import Protocol
from uuid import UUID


class AccessFailure(Exception):
    """Safe transport-independent failure; never includes phone, code or token."""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__("Account access could not be completed.")


class OtpProvider(Protocol):
    challenge_prefix: str
    requires_persistence: bool

    def send(self, phone: str, challenge_id: str) -> None: ...

    def verify(self, code: str, challenge_id: str) -> bool: ...


class MockOtpProvider:
    """The documented demo code is accepted only by the local/test composition."""

    challenge_prefix = ""
    requires_persistence = False

    def send(self, phone: str, challenge_id: str) -> None:
        """Local/test only: no external side effect."""

    def verify(self, code: str, challenge_id: str = "") -> bool:
        # A later configuration change must never admit an SMS challenge with
        # the public development code.
        if challenge_id.startswith("sms1."):
            return False
        normalized = code.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
        return hmac.compare_digest(normalized.encode(), b"123456")


@dataclass
class Challenge:
    phone: str
    expires_at: float
    attempts: int = 0


@dataclass(frozen=True)
class AccountSession:
    phone: str
    expires_at: float
    account_id: UUID | None = None


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class AccountAccess:
    """Thread-safe, bounded local store; expiry, single use and revocation are server-owned."""

    persistent = False

    def __init__(self, provider: OtpProvider | None, clock: Callable[[], float] = time.monotonic) -> None:
        self.provider = provider
        self.clock = clock
        self.challenges: dict[str, Challenge] = {}
        self.sessions: dict[str, AccountSession] = {}
        self.quota: dict[str, list[float]] = {}
        self.lock = Lock()

    def _enabled(self) -> None:
        if self.provider is None or (self.provider.requires_persistence and not self.persistent):
            raise AccessFailure(503)

    def _prune(self, now: float) -> None:
        self.challenges = {key: item for key, item in self.challenges.items() if item.expires_at > now}
        self.sessions = {key: item for key, item in self.sessions.items() if item.expires_at > now}
        self.quota = {key: [t for t in times if t > now - 120] for key, times in self.quota.items()}
        self.quota = {key: times for key, times in self.quota.items() if times}

    def request_code(self, phone: str, client: str) -> str:
        self._enabled()
        with self.lock:
            now = self.clock()
            self._prune(now)
            keys = ("phone:" + digest(phone), "client:" + digest(client))
            if any(len(self.quota.get(key, [])) >= 5 for key in keys):
                raise AccessFailure(429)
            if len(self.challenges) >= 1024 or len(self.quota) >= 2048:
                raise AccessFailure(429)
            for key in keys:
                self.quota.setdefault(key, []).append(now)
            challenge_id = (self.provider.challenge_prefix if self.provider else "") + secrets.token_urlsafe(32)
            self.challenges[digest(challenge_id)] = Challenge(phone, now + 120)
        # Never hold the access lock over network I/O; reserve quota first.
        try:
            if self.provider is not None:
                self.provider.send(phone, challenge_id)
        except Exception:
            with self.lock:
                self.challenges.pop(digest(challenge_id), None)
            raise AccessFailure(503) from None
        return challenge_id

    def verify_code(self, challenge_id: str, code: str) -> str:
        self._enabled()
        with self.lock:
            now = self.clock()
            self._prune(now)
            key = digest(challenge_id)
            challenge = self.challenges.get(key)
            if challenge is None:
                raise AccessFailure(401)
            challenge.attempts += 1
            if self.provider is None or not self.provider.verify(code, challenge_id):
                if challenge.attempts >= 5:
                    del self.challenges[key]
                raise AccessFailure(401)
            if len(self.sessions) >= 1024:
                raise AccessFailure(429)
            del self.challenges[key]
            token = secrets.token_urlsafe(32)
            self.sessions[digest(token)] = AccountSession(challenge.phone, now + 3600)
            return token

    def verified_phone(self, token: str) -> str:
        self._enabled()
        with self.lock:
            self._prune(self.clock())
            session = self.sessions.get(digest(token))
            if session is None:
                raise AccessFailure(401)
            return session.phone

    def bind_account(self, token: str, account_id: UUID) -> None:
        """Bind only once, before publishing the capability; legacy unbound tokens fail closed."""
        with self.lock:
            self._prune(self.clock())
            key = digest(token)
            session = self.sessions.get(key)
            if session is None or session.account_id is not None:
                raise AccessFailure(401)
            self.sessions[key] = replace(session, account_id=account_id, expires_at=self.clock() + 3600)

    def actor(self, token: str) -> UUID:
        self._enabled()
        with self.lock:
            self._prune(self.clock())
            session = self.sessions.get(digest(token))
            if session is None or session.account_id is None:
                raise AccessFailure(401)
            return session.account_id

    def remaining(self, token: str) -> int:
        """Absolute remaining lifetime, never a fresh one-hour window on restore."""
        self.actor(token)
        with self.lock:
            now = self.clock()
            session = self.sessions.get(digest(token))
            if session is None or session.expires_at <= now:
                raise AccessFailure(401)
            return ceil(session.expires_at - now)

    def revoke(self, token: str) -> None:
        with self.lock:
            self.sessions.pop(digest(token), None)
