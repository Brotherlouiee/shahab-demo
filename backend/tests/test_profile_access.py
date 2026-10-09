"""Regression tests for anonymous access, ownership, expiry and failed persistence."""

import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.app.accounts.access import AccessFailure, AccountAccess, MockOtpProvider
from backend.app.accounts.phone import normalize_phone
from backend.app.core.config import AppEnvironment, Settings
from backend.app.core.dependencies import get_request_database_session
from backend.app.infrastructure.db.models import UserProfile
from backend.app.main import create_app


class ProfileAccessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(Settings(environment=AppEnvironment.TEST, profile_mock_otp_enabled=True))
        self.database = MagicMock()
        self.record = UserProfile(
            phone="09000000001",
            first_name="آزمون",
            last_name="تست",
            income="up-to-22",
            job="employee",
            gender="",
            avatar_data_url=None,
        )
        self.database.get.return_value = self.record
        self.app.dependency_overrides[get_request_database_session] = lambda: self.database
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def login(self, phone: str = "09000000001") -> dict[str, str]:
        challenge = self.client.post("/api/v1/account-access/request", json={"phone": phone})
        self.assertEqual(challenge.status_code, 200)
        verified = self.client.post(
            "/api/v1/account-access/verify",
            json={
                "challengeId": challenge.json()["challengeId"],
                "code": "۱۲۳۴۵۶",
            },
        )
        self.assertEqual(verified.status_code, 200)
        return {"Authorization": "Bearer " + verified.json()["accessToken"]}

    def test_anonymous_and_forged_access_do_not_read_storage(self) -> None:
        for headers in ({}, {"Authorization": "Bearer forged"}):
            self.assertEqual(self.client.get("/api/v1/profiles/me", headers=headers).status_code, 401)
            self.assertEqual(
                self.client.put("/api/v1/profiles", headers=headers, json={"phone": "09000000001"}).status_code, 401
            )
        self.database.get.assert_not_called()
        self.assertEqual(self.client.get("/api/v1/profiles/09000000001").status_code, 404)

    def test_read_is_owned_and_other_phone_cannot_be_written(self) -> None:
        headers = self.login()
        response = self.client.get("/api/v1/profiles/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.database.get.assert_called_with(UserProfile, "09000000001")
        response = self.client.put("/api/v1/profiles", headers=headers, json={"phone": "09000000002"})
        self.assertEqual(response.status_code, 403)
        self.database.commit.assert_not_called()
        self.assertEqual(self.record.phone, "09000000001")

    def test_profile_write_and_storage_failure_are_distinct(self) -> None:
        headers = self.login()
        response = self.client.put(
            "/api/v1/profiles",
            headers=headers,
            json={
                "phone": "۰۹۰۰۰۰۰۰۰۰۱",
                "firstName": "آزمون",
                "income": "22-to-50",
                "job": "manager",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["income"], "22-to-50")
        self.database.commit.side_effect = RuntimeError("private database failure")
        response = self.client.put("/api/v1/profiles", headers=headers, json={"phone": "09000000001"})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private database", response.text)
        self.database.rollback.assert_called_once()

    def test_extra_fields_invalid_job_and_avatar_are_rejected(self) -> None:
        headers = self.login()
        for extra in ({"admin": True}, {"job": "invalid"}, {"avatar": "data:image/svg+xml;base64,PHN2Zz4="}):
            response = self.client.put("/api/v1/profiles", headers=headers, json={"phone": "09000000001", **extra})
            self.assertEqual(response.status_code, 422)
        self.database.commit.assert_not_called()

    def test_logout_revokes_the_capability(self) -> None:
        headers = self.login()
        self.assertEqual(self.client.post("/api/v1/account-access/logout", headers=headers).status_code, 204)
        self.assertEqual(self.client.get("/api/v1/profiles/me", headers=headers).status_code, 401)

    def test_verification_creates_a_profile_only_after_valid_code(self) -> None:
        self.database.get.return_value = None
        challenge = self.client.post("/api/v1/account-access/request", json={"phone": "09000000001"}).json()
        self.database.add.assert_not_called()
        response = self.client.post(
            "/api/v1/account-access/verify", json={"challengeId": challenge["challengeId"], "code": "000000"}
        )
        self.assertEqual(response.status_code, 401)
        self.database.add.assert_not_called()
        response = self.client.post(
            "/api/v1/account-access/verify", json={"challengeId": challenge["challengeId"], "code": "123456"}
        )
        self.assertEqual(response.status_code, 200)
        created = self.database.add.call_args.args[0]
        self.assertEqual((created.phone, created.first_name, created.last_name), ("09000000001", "", ""))
        self.database.commit.assert_called_once()

    def test_repeat_login_preserves_existing_profile(self) -> None:
        self.login()
        self.login()
        self.database.add.assert_not_called()
        self.database.commit.assert_not_called()
        self.assertEqual((self.record.first_name, self.record.income), ("آزمون", "up-to-22"))

    def test_failed_profile_creation_does_not_issue_access(self) -> None:
        self.database.get.return_value = None
        self.database.commit.side_effect = RuntimeError("private database failure")
        challenge = self.client.post("/api/v1/account-access/request", json={"phone": "09000000001"}).json()
        response = self.client.post(
            "/api/v1/account-access/verify", json={"challengeId": challenge["challengeId"], "code": "123456"}
        )
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("accessToken", response.text)
        self.assertNotIn("private database", response.text)
        self.database.rollback.assert_called_once()

    def test_existing_local_container_without_new_flag_can_request_mock_otp(self) -> None:
        from unittest.mock import patch

        with patch.dict("os.environ", {}, clear=True):
            app = create_app(Settings(environment=AppEnvironment.LOCAL))
        client = TestClient(app)
        response = client.post("/api/v1/account-access/request", json={"phone": "09000000001"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("challengeId", response.json())

    def test_mock_is_explicit_and_never_available_in_staging_or_production(self) -> None:
        for environment, enabled in (
            (AppEnvironment.LOCAL, False),
            (AppEnvironment.STAGING, True),
            (AppEnvironment.PRODUCTION, True),
        ):
            client = TestClient(create_app(Settings(environment=environment, profile_mock_otp_enabled=enabled)))
            self.assertEqual(
                client.post("/api/v1/account-access/request", json={"phone": "09000000001"}).status_code, 503
            )
            self.assertEqual(
                client.get("/api/v1/profiles/me", headers={"Authorization": "Bearer forged"}).status_code, 503
            )


class AccountSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = 0.0
        self.access = AccountAccess(MockOtpProvider(), lambda: self.now)

    def test_attempt_limit_expiry_and_single_use(self) -> None:
        challenge = self.access.request_code("09000000001", "test-client")
        for _ in range(5):
            with self.assertRaises(AccessFailure):
                self.access.verify_code(challenge, "000000")
        with self.assertRaises(AccessFailure):
            self.access.verify_code(challenge, "123456")
        challenge = self.access.request_code("09000000001", "test-client")
        self.now = 121
        with self.assertRaises(AccessFailure):
            self.access.verify_code(challenge, "123456")
        challenge = self.access.request_code("09000000001", "test-client")
        token = self.access.verify_code(challenge, "123456")
        self.assertEqual(self.access.actor(token), "09000000001")
        with self.assertRaises(AccessFailure):
            self.access.verify_code(challenge, "123456")
        self.now += 1801
        with self.assertRaises(AccessFailure):
            self.access.actor(token)

    def test_request_quota_and_its_recovery(self) -> None:
        for _ in range(5):
            self.access.request_code("09000000001", "test-client")
        with self.assertRaises(AccessFailure) as raised:
            self.access.request_code("09000000002", "test-client")
        self.assertEqual(raised.exception.status, 429)
        self.now += 121
        self.access.request_code("09000000001", "test-client")

    def test_full_persian_arabic_and_suffix_numbers_preserve_identity(self) -> None:
        for value in ("09000000001", "۰۹۰۰۰۰۰۰۰۰۱", "٠٩٠٠٠٠٠٠٠٠١", "000000001"):
            self.assertEqual(normalize_phone(value), "09000000001")
        with self.assertRaises(ValueError):
            normalize_phone("0900000000")
