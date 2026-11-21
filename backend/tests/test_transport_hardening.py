"""US-11.T02H: transport, CSRF, CORS and private-response negative matrix."""

import unittest

from fastapi.testclient import TestClient

from backend.app.core.config import AppEnvironment, Settings
from backend.app.main import create_app


class TransportHardeningTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            Settings(
                environment=AppEnvironment.TEST,
                cors_allowed_origins=("https://trusted.example",),
            )
        )
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_private_errors_and_success_are_never_cacheable(self):
        for response in (
            self.client.get("/api/v1/profiles/me"),
            self.client.get("/api/v1/bookmarks"),
            self.client.post("/api/v1/questionnaire/sessions"),
            self.client.get("/api/v1/not-found"),
        ):
            self.assertEqual(response.headers["cache-control"], "no-store")
            self.assertEqual(response.headers["pragma"], "no-cache")
            self.assertEqual(response.headers["x-content-type-options"], "nosniff")
            self.assertEqual(response.headers["referrer-policy"], "no-referrer")
            self.assertEqual(response.headers["x-frame-options"], "DENY")

    def test_cookie_mutations_reject_cross_origin_even_if_cors_allowlisted(self):
        for origin in ("https://evil.example", "https://trusted.example", "null"):
            response = self.client.post(
                "/api/v1/account-access/logout",
                headers={"Origin": origin, "Cookie": "shahab_account_access=synthetic"},
            )
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.headers["cache-control"], "no-store")
            self.assertEqual(response.json()["error"]["code"], "forbidden")

    def test_cross_site_fetch_metadata_without_origin_is_denied(self):
        response = self.client.post("/api/v1/account-access/logout", headers={"Sec-Fetch-Site": "cross-site"})
        self.assertEqual(response.status_code, 403)

    def test_invalid_cors_configuration_is_rejected(self):
        for origin in ("*", "null", "https://allowed.example/path", "https://user@allowed.example"):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                Settings(cors_allowed_origins=(origin,))

    def test_cors_preflight_denies_unknown_and_limits_methods(self):
        denied = self.client.options(
            "/api/v1/account-access/request",
            headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
        )
        self.assertNotEqual(denied.headers.get("access-control-allow-origin"), "https://evil.example")
        permitted = self.client.options(
            "/api/v1/account-access/request",
            headers={"Origin": "https://trusted.example", "Access-Control-Request-Method": "POST"},
        )
        self.assertEqual(permitted.headers.get("access-control-allow-origin"), "https://trusted.example")
        forbidden_method = self.client.options(
            "/api/v1/account-access/request",
            headers={"Origin": "https://trusted.example", "Access-Control-Request-Method": "TRACE"},
        )
        self.assertNotEqual(forbidden_method.status_code, 200)

    def test_body_limits_and_malformed_length_have_safe_errors(self):
        huge = self.client.post(
            "/api/v1/account-access/request",
            headers={"Content-Type": "application/json"},
            content=b"x" * (1024 * 1024 + 1),
        )
        self.assertEqual(huge.status_code, 413)
        self.assertEqual(huge.headers["cache-control"], "no-store")
        malformed = self.client.post(
            "/api/v1/account-access/request",
            headers={"Content-Length": "invalid"},
            content=b"{}",
        )
        self.assertIn(malformed.status_code, (400, 422))

    def test_streamed_body_is_rejected_before_unbounded_allocation(self):
        def pieces():
            yield b"x" * (600 * 1024)
            yield b"y" * (600 * 1024)

        response = self.client.post(
            "/api/v1/account-access/request",
            headers={"Content-Type": "application/json"},
            content=pieces(),
        )
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["error"]["code"], "invalid_request")

    def test_bearer_allowed_origin_does_not_bypass_account_checks(self):
        response = self.client.post(
            "/api/v1/account-access/logout",
            headers={"Origin": "https://trusted.example", "Authorization": "Bearer synthetic"},
        )
        self.assertIn(response.status_code, (204, 401))
        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_secure_transport_emits_hsts_only_for_https(self):
        secure = TestClient(self.app, base_url="https://testserver")
        self.assertEqual(
            secure.get("/api/v1/profiles/me").headers["strict-transport-security"],
            "max-age=31536000",
        )
        self.assertNotIn("strict-transport-security", self.client.get("/api/v1/profiles/me").headers)
