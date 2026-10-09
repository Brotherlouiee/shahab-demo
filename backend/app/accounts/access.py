"""Bounded development OTP access, with opaque revocable sessions.

This is deliberately a local/test adapter, not proof of real phone ownership.
No state is persisted across API restarts. A real provider and shared session
store require their own reviewed production task; disabled environments fail closed.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock
from typing import Protocol


class AccessFailure(Exception):
    """Safe transport-independent failure; never includes phone, code or token."""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__("Account access could not be completed.")


class OtpProvider(Protocol):
    def verify(self, code: str) -> bool: ...


class MockOtpProvider:
    """The documented demo code is accepted only by the local/test composition."""

    def verify(self, code: str) -> bool:
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


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class AccountAccess:
    """Thread-safe, bounded local store; expiry, single use and revocation are server-owned."""

    def __init__(self, provider: OtpProvider | None, clock: Callable[[], float] = time.monotonic) -> None:
        self.provider = provider
        self.clock = clock
        self.challenges: dict[str, Challenge] = {}
        self.sessions: dict[str, AccountSession] = {}
        self.quota: dict[str, list[float]] = {}
        self.lock = Lock()

    def _enabled(self) -> None:
        if self.provider is None:
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
            challenge_id = secrets.token_urlsafe(32)
            self.challenges[digest(challenge_id)] = Challenge(phone, now + 120)
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
            if self.provider is None or not self.provider.verify(code):
                if challenge.attempts >= 5:
                    del self.challenges[key]
                raise AccessFailure(401)
            if len(self.sessions) >= 1024:
                raise AccessFailure(429)
            del self.challenges[key]
            token = secrets.token_urlsafe(32)
            self.sessions[digest(token)] = AccountSession(challenge.phone, now + 1800)
            return token

    def actor(self, token: str) -> str:
        self._enabled()
        with self.lock:
            self._prune(self.clock())
            session = self.sessions.get(digest(token))
            if session is None:
                raise AccessFailure(401)
            return session.phone

    def revoke(self, token: str) -> None:
        with self.lock:
            self.sessions.pop(digest(token), None)
