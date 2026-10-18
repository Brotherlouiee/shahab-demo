"""No SMS, credentials or provider network: contract and existing access-path tests."""

import json
import os
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from urllib.parse import parse_qs

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.accounts.access import AccessFailure, AccountAccess, MockOtpProvider, digest
from backend.app.accounts.kavenegar import MAX_RESPONSE_BYTES, KavenegarOtpProvider, _NoRedirect, post_lookup
from backend.app.accounts.profile_repository import ensure_profile
from backend.app.accounts.sqlalchemy_access import SqlAlchemyAccountAccess
from backend.app.core.config import AppEnvironment, Settings
from backend.app.core.dependencies import get_request_database_session
from backend.app.infrastructure.db.models import (
    Account,
    AccountAccessSession,
    AccountOtpChallenge,
    AccountOtpQuotaEvent,
    Base,
)
from backend.app.main import create_app

PHONE = "09000000001"
CHALLENGE = "sms1." + "a" * 43
KEY = "test" * 8
SECRET = "synthetic-only-" * 4


def accepted():
    return {"return": {"status": 200}, "entries": [{"messageid": 42, "status": 5}]}


def provider(transport=None):
    return KavenegarOtpProvider(KEY, "SyntheticTemplate", SECRET, transport=transport or Mock(return_value=accepted()))


class LookupContractTests(unittest.TestCase):
    def test_post_form_has_fixed_https_endpoint_timeout_no_sender_and_no_retries(self):
        response = Mock(status=200)
        response.read.return_value = json.dumps(accepted()).encode()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        opener = Mock()
        opener.open.return_value = response
        with patch("backend.app.accounts.kavenegar.build_opener", return_value=opener) as factory:
            provider(post_lookup).send(PHONE, CHALLENGE)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, f"https://api.kavenegar.com/v1/{KEY}/verify/lookup.json")
        self.assertEqual(request.method, "POST")
        self.assertEqual(opener.open.call_args.kwargs, {"timeout": 5.0})
        self.assertEqual(opener.open.call_count, 1)
        parameters = parse_qs(request.data.decode())
        self.assertEqual(set(parameters), {"receptor", "token", "template", "type"})
        self.assertEqual(parameters["receptor"], [PHONE])
        self.assertEqual(parameters["template"], ["SyntheticTemplate"])
        self.assertEqual(parameters["type"], ["sms"])
        self.assertRegex(parameters["token"][0], r"^[0-9]{6}$")
        self.assertEqual(factory.call_args.args[0].proxies, {})
        response.read.assert_called_once_with(MAX_RESPONSE_BYTES + 1)

    def test_fresh_provider_can_verify_sent_code_and_other_challenge_cannot(self):
        transport = Mock(return_value=accepted())
        first = provider(transport)
        first.send(PHONE, CHALLENGE)
        code = transport.call_args.args[1]["token"]
        self.assertTrue(provider().verify(code, CHALLENGE))
        self.assertTrue(provider().verify(code.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")), CHALLENGE))
        self.assertFalse(provider().verify(code, "legacy-mock-challenge"))
        self.assertFalse(MockOtpProvider().verify("123456", CHALLENGE))
        other = "sms1." + "b" * 43
        # This fixed synthetic pair has distinct codes; no statistical uniqueness assertion.
        self.assertFalse(provider().verify(code, other))
        self.assertFalse(KavenegarOtpProvider(KEY, "SyntheticTemplate", "other-secret-" * 4).verify(code, CHALLENGE))

    def test_provider_rejection_invalid_payload_and_network_errors_are_safe_and_single_attempt(self):
        cases = [
            None,
            [],
            {},
            {"return": {"status": 200}, "entries": []},
            {"return": {"status": "200"}, "entries": [{"messageid": 42, "status": 5}]},
            {"return": {"status": 200}, "entries": [{"messageid": True, "status": 5}]},
        ]
        cases += [
            {"return": {"status": status, "message": KEY + PHONE}, "entries": None}
            for status in (401, 418, 424, 426, 431, 432, 500)
        ]
        cases += [
            {"return": {"status": 200}, "entries": [{"messageid": 42, "status": status}]}
            for status in (11, 13, 14, 100, "5", True)
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                transport = Mock(return_value=payload)
                with self.assertRaises(AccessFailure) as error:
                    provider(transport).send(PHONE, CHALLENGE)
                self.assertEqual(error.exception.status, 503)
                self.assertNotIn(KEY, str(error.exception))
                self.assertEqual(transport.call_count, 1)
        for exception in (TimeoutError(KEY + PHONE), HTTPError("https://invalid/" + KEY, 424, PHONE, {}, None)):
            transport = Mock(side_effect=exception)
            with self.assertRaises(AccessFailure) as error:
                provider(transport).send(PHONE, CHALLENGE)
            self.assertEqual(str(error.exception), "Account access could not be completed.")
            self.assertTrue(error.exception.__suppress_context__)
            self.assertEqual(transport.call_count, 1)

    def test_redirect_oversized_invalid_json_and_non_200_are_rejected(self):
        with self.assertRaises(AccessFailure):
            _NoRedirect().redirect_request(None, None, 302, "", {}, "https://elsewhere.invalid")
        for status, body in ((200, b"x" * (MAX_RESPONSE_BYTES + 1)), (200, b"invalid"), (302, b"{}")):
            response = Mock(status=status)
            response.read.return_value = body
            response.__enter__ = Mock(return_value=response)
            response.__exit__ = Mock(return_value=False)
            opener = Mock()
            opener.open.return_value = response
            with patch("backend.app.accounts.kavenegar.build_opener", return_value=opener):
                with self.assertRaises((AccessFailure, ValueError)):
                    post_lookup(KEY, {}, 5.0)

    def test_memory_fallback_and_incomplete_configuration_are_rejected(self):
        transport = Mock(return_value=accepted())
        with self.assertRaises(AccessFailure) as error:
            AccountAccess(provider(transport)).request_code(PHONE, "client")
        self.assertEqual(error.exception.status, 503)
        transport.assert_not_called()
        for environment in (
            AppEnvironment.LOCAL,
            AppEnvironment.TEST,
            AppEnvironment.STAGING,
            AppEnvironment.PRODUCTION,
        ):
            with self.assertRaises(ValueError):
                create_app(Settings(environment=environment, kavenegar_otp_enabled=True))
        for changes in (
            {"api_key": "../malformed"},
            {"template": "../invalid"},
            {"code_secret": "short"},
            {"timeout": 0},
            {"timeout": 11},
        ):
            arguments = {"api_key": KEY, "template": "SyntheticTemplate", "code_secret": SECRET, **changes}
            with self.assertRaises(ValueError):
                KavenegarOtpProvider(**arguments)

    def test_live_activation_is_explicit_and_never_available_in_ci_or_test(self):
        values = dict(
            kavenegar_otp_enabled=True,
            kavenegar_template_approved=True,
            database_url="postgresql+psycopg://unused.invalid/test",
            kavenegar_api_key=KEY,
            kavenegar_template="SyntheticTemplate",
            otp_code_secret=SECRET,
        )
        with patch.dict(os.environ, {}, clear=True):
            app = create_app(Settings(environment=AppEnvironment.PRODUCTION, **values))
            self.assertIsInstance(app.state.account_access.provider, KavenegarOtpProvider)
            with self.assertRaises(AccessFailure):
                # No lifespan/connection: real provider cannot use the memory store.
                app.state.account_access.request_code(PHONE, "client")
            with self.assertRaises(ValueError):
                create_app(Settings(environment=AppEnvironment.TEST, **values))
            with self.assertRaises(ValueError):
                create_app(Settings(environment=AppEnvironment.PRODUCTION, **{**values, "database_url": "sqlite://"}))
        for flag in ("CI", "GITHUB_ACTIONS"):
            with patch.dict(os.environ, {flag: "true"}), self.assertRaises(ValueError):
                create_app(Settings(environment=AppEnvironment.PRODUCTION, **values))


class LookupAccessTests(unittest.TestCase):
    """SQLite proves the contract; PostgreSQL race/locking is a separate suite."""

    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.now = datetime(2026, 10, 18, tzinfo=UTC)
        self.sent = []

        def send(key, parameters, timeout):
            self.assertFalse(self.db.in_transaction(), "network must run after quota transaction commits")
            self.sent.append(parameters)
            return accepted()

        self.sender = provider(send)
        self.service = SqlAlchemyAccountAccess(self.sender, self.db, lambda: self.now)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_challenge_digest_only_fresh_worker_single_use_and_absolute_session(self):
        challenge = self.service.request_code(PHONE, "client")
        code = self.sent[-1]["token"]
        row = self.db.scalar(select(AccountOtpChallenge))
        self.assertEqual(row.challenge_digest, digest(challenge))
        self.assertNotEqual(row.challenge_digest, challenge)
        self.assertNotEqual(row.challenge_digest, digest(code))
        # SQLite drops tzinfo on a reloaded row. A fresh worker has no such
        # identity-map object for SQLAlchemy's DELETE synchronization to compare.
        self.db.expunge_all()
        other = SqlAlchemyAccountAccess(provider(), self.db, lambda: self.now)
        token = other.verify_code(challenge, code)
        actor = ensure_profile(other.verified_phone(token), self.db)
        other.bind_account(token, actor.account_id)
        self.assertEqual(other.remaining(token), 3600)
        with self.assertRaises(AccessFailure):
            self.service.verify_code(challenge, code)
        self.now += timedelta(seconds=3599)
        self.assertEqual(other.remaining(token), 1)
        self.now += timedelta(seconds=1)
        with self.assertRaises(AccessFailure):
            other.actor(token)

    def test_wrong_code_limits_expiry_and_quota_remain_shared(self):
        challenge = self.service.request_code(PHONE, "client")
        code = self.sent[-1]["token"]
        wrong = "000000" if code != "000000" else "111111"
        other = SqlAlchemyAccountAccess(provider(), self.db, lambda: self.now)
        for _ in range(5):
            with self.assertRaises(AccessFailure):
                other.verify_code(challenge, wrong)
        with self.assertRaises(AccessFailure):
            self.service.verify_code(challenge, code)
        for _ in range(4):
            self.service.request_code(PHONE, "client")
        with self.assertRaises(AccessFailure) as error:
            other.request_code(PHONE, "client")
        self.assertEqual(error.exception.status, 429)
        self.assertEqual(len(self.sent), 5)
        self.now += timedelta(seconds=121)
        challenge = self.service.request_code(PHONE, "client")
        code = self.sent[-1]["token"]
        self.now += timedelta(seconds=120)
        with self.assertRaises(AccessFailure):
            other.verify_code(challenge, code)

    def test_send_failure_consumes_challenge_keeps_quota_and_never_creates_account(self):
        self.sender._transport = Mock(side_effect=TimeoutError(KEY + PHONE))
        with self.assertRaises(AccessFailure) as error:
            self.service.request_code(PHONE, "client")
        self.assertEqual(error.exception.status, 503)
        self.assertIsNotNone(self.db.scalar(select(AccountOtpChallenge)).consumed_at)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(AccountOtpQuotaEvent)), 2)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Account)), 0)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(AccountAccessSession)), 0)

    def test_api_request_verify_cookie_profile_restore_logout_and_safe_failure(self):
        app = create_app(Settings(environment=AppEnvironment.TEST))
        app.state.account_access = AccountAccess(self.sender)
        app.dependency_overrides[get_request_database_session] = lambda: self.db
        client = TestClient(app, raise_server_exceptions=False)
        requested = client.post("/api/v1/account-access/request", json={"phone": PHONE})
        self.assertEqual(requested.status_code, 200, requested.text)
        challenge = requested.json()["challengeId"]
        code = self.sent[-1]["token"]
        self.assertEqual(set(requested.json()), {"challengeId", "expiresIn"})
        self.assertEqual(requested.headers["cache-control"], "no-store")
        verified = client.post("/api/v1/account-access/verify", json={"challengeId": challenge, "code": code})
        self.assertEqual(verified.status_code, 200, verified.text)
        self.assertIn("HttpOnly", verified.headers["set-cookie"])
        self.assertEqual(client.get("/api/v1/profiles/me").status_code, 200)
        self.assertEqual(client.get("/api/v1/account-access/session").status_code, 200)
        self.assertEqual(client.post("/api/v1/account-access/logout").status_code, 204)
        self.assertEqual(client.get("/api/v1/profiles/me").status_code, 401)
        self.sender._transport = Mock(side_effect=TimeoutError(KEY + PHONE))
        failed = client.post("/api/v1/account-access/request", json={"phone": PHONE})
        self.assertEqual(failed.status_code, 503)
        self.assertNotIn(KEY, failed.text)
        self.assertNotIn(PHONE, failed.text)
        self.assertNotIn("set-cookie", failed.headers)
        self.assertEqual(failed.headers["cache-control"], "no-store")
