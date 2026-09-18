"""Focused tests for the US-03.T02 FastAPI core boundary."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from backend.app.core.config import AppEnvironment, Settings
from backend.app.core.logging import REDACTED_VALUE, redact_value
from backend.app.main import create_app


class CoreBootstrapTests(unittest.TestCase):
    def test_settings_validate_log_level(self) -> None:
        with self.assertRaises(ValueError):
            Settings(log_level="verbose")

    def test_production_hides_interactive_documentation(self) -> None:
        settings = Settings(environment=AppEnvironment.PRODUCTION)
        app = create_app(settings)
        self.assertIsNone(app.docs_url)
        self.assertIsNone(app.openapi_url)

    def test_comma_separated_cors_origins_are_read_from_environment(self) -> None:
        with patch.dict(
            os.environ,
            {"SHAHAB_CORS_ALLOWED_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173"},
            clear=False,
        ):
            self.assertEqual(
                Settings().cors_allowed_origins,
                ("http://localhost:5173", "http://127.0.0.1:5173"),
            )

    def test_app_is_composed_from_explicit_settings(self) -> None:
        settings = Settings(app_name="Test Shahab", environment=AppEnvironment.TEST)
        app = create_app(settings)
        self.assertEqual(app.title, "Test Shahab")
        self.assertIs(app.state.settings, settings)

    def test_nested_sensitive_values_are_redacted(self) -> None:
        value = {"otp": "123456", "nested": {"access_token": "abc"}, "safe": "visible"}
        self.assertEqual(
            redact_value(value),
            {"otp": REDACTED_VALUE, "nested": {"access_token": REDACTED_VALUE}, "safe": "visible"},
        )
