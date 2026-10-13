"""US-11.T04: PII-safe metrics, alert thresholds, and strict log schema."""

from __future__ import annotations

import logging
import unittest

from fastapi.testclient import TestClient

from backend.app.api.observability import OperationalMetrics
from backend.app.core.config import AppEnvironment, Settings
from backend.app.core.logging import RedactingFilter, is_sensitive_field
from backend.app.main import create_app


class RecordingLogger(logging.Logger):
    def __init__(self) -> None:
        super().__init__("observability-test")
        self.records: list[tuple[str, tuple[object, ...]]] = []

    def warning(self, msg: object, *args: object, **kwargs: object) -> None:
        self.records.append((str(msg), args))


class SafeObservabilityTests(unittest.TestCase):
    def test_invalid_and_sensitive_log_values_are_never_formatted(self) -> None:
        privacy_canaries = ("09123456789", "very-private-answer", "Bearer secret", "income=123456")
        for name in ("phone", "answers", "income", "firstName", "sessionId", "authorization"):
            self.assertTrue(is_sensitive_field(name))
        redactor = RedactingFilter()
        for secret in privacy_canaries:
            record = logging.LogRecord(
                "shahab", logging.INFO, __file__, 1, "unsafe: %s", (secret,), None
            )
            self.assertTrue(redactor.filter(record))
            self.assertNotIn(secret, record.getMessage())
            self.assertEqual(record.getMessage(), "unstructured_log_redacted")
        for secret in privacy_canaries:
            record = logging.LogRecord(
                "shahab", logging.INFO, __file__, 1,
                "development_api_timing endpoint=%s status_code=%s duration_ms=%.1f",
                (secret, 401, 2.0), None
            )
            redactor.filter(record)
            self.assertEqual(record.getMessage(), "unstructured_log_redacted")

    def test_process_local_metrics_do_not_hold_identifiers(self) -> None:
        logger = RecordingLogger()
        metrics = OperationalMetrics(logger)
        for i in range(10):
            metrics.record("GET", 403, 20.0, login_failure=True)
        snapshot = metrics.snapshot()
        self.assertEqual(snapshot["signals"]["forbidden"], 10)
        self.assertEqual(snapshot["signals"]["login_failure"], 10)
        self.assertEqual(snapshot["request_counts"]["GET_4xx"], 10)
        self.assertEqual(len(logger.records), 2)
        for name in ("login_failure", "forbidden"):
            self.assertTrue(any(args[0] == name for _, args in logger.records))
        metrics.record("POST", 503, 700.0)
        self.assertEqual(metrics.snapshot()["latency_buckets_ms"]["1000"], 1)
        self.assertNotIn("09123456789", str(snapshot))
        metrics.record("PUT", 401, 5.0, login_failure=False)
        self.assertEqual(metrics.snapshot()["signals"]["login_failure"], 10)

    def test_bounded_alerts_do_not_repeat_in_same_window(self) -> None:
        logger = RecordingLogger()
        metrics = OperationalMetrics(logger)
        for _ in range(21):
            metrics.record("POST", 429, 1.0)
        self.assertEqual(len(logger.records), 1)
        self.assertEqual(logger.records[0][1][0], "rate_limited")

    def test_api_outcomes_recorded_without_sensitive_path_or_body(self) -> None:
        app = create_app(Settings(environment=AppEnvironment.TEST))
        with TestClient(app, raise_server_exceptions=False) as client:
            client.get("/api/v1/profiles/me", headers={"Authorization": "Bearer very-private-token"})
            client.get("/api/v1/missing-09123456789")
            client.post("/api/v1/account-access/request", json={"phone": "09123456789"})
        snapshot = app.state.operational_metrics.snapshot()
        self.assertGreaterEqual(sum(snapshot["request_counts"].values()), 3)
        self.assertNotIn("09123456789", str(snapshot))
        self.assertNotIn("very-private-token", str(snapshot))
        self.assertNotIn("/profiles/me", str(snapshot))
