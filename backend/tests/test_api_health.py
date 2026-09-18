"""API v1 tests for the restricted health contract and typed errors."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from pydantic import SecretStr

from backend.app.core.config import AppEnvironment, Settings
from backend.app.main import create_app


class ApiHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        settings = Settings(environment=AppEnvironment.TEST, readiness_token=SecretStr("test-readiness-token"))
        self.client = TestClient(create_app(settings), raise_server_exceptions=False)

    def test_liveness_is_public_and_minimal(self) -> None:
        response = self.client.get("/api/v1/health/live")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertIn("X-Correlation-ID", response.headers)

    def test_readiness_requires_the_configured_token(self) -> None:
        response = self.client.get("/api/v1/health/ready")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")
        self.assertIn("correlationId", response.json()["error"])
        authorized = self.client.get(
            "/api/v1/health/ready", headers={"X-Shahab-Readiness-Token": "test-readiness-token"}
        )
        self.assertEqual(authorized.status_code, 200)
        self.assertEqual(authorized.json(), {"status": "ready"})

    def test_unknown_route_does_not_expose_internal_data(self) -> None:
        response = self.client.get("/api/v1/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")
        self.assertNotIn("traceback", response.text.casefold())
