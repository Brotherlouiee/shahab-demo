"""Structured logging helpers that redact sensitive values before emission."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

SENSITIVE_FIELD_MARKERS = (
    "password", "secret", "token", "authorization", "cookie", "otp", "api_key",
    "phone", "mobile", "name", "income", "salary", "answer", "questionnaire",
    "gender", "job", "avatar", "session", "address", "email", "reason", "payload",
    "body", "query", "url", "header", "trace", "financial", "identity", "actor",
)
REDACTED_VALUE = "[REDACTED]"


def is_sensitive_field(name: str) -> bool:
    """Detect common credential/PII-bearing field names case-insensitively."""
    normalized = name.casefold().replace("-", "_")
    return any(marker in normalized for marker in SENSITIVE_FIELD_MARKERS)


def redact_value(value: Any, *, field_name: str | None = None) -> Any:
    """Recursively remove secret-bearing values while preserving safe diagnostics."""
    if field_name and is_sensitive_field(field_name):
        return REDACTED_VALUE
    if isinstance(value, Mapping):
        return {str(key): redact_value(item, field_name=str(key)) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    return value


class RedactingFilter(logging.Filter):
    """Ensure mapping messages and mapping arguments never leak sensitive fields."""

    def filter(self, record: logging.LogRecord) -> bool:
        allowed = {
            "development_api_timing endpoint=%s status_code=%s duration_ms=%.1f",
            "operational_alert signal=%s window_seconds=60 threshold=%d",
        }
        if not isinstance(record.msg, str) or record.msg not in allowed:
            record.msg = "unstructured_log_redacted"
            record.args = ()
            return True
        if not isinstance(record.args, tuple) or len(record.args) != 3:
            record.msg = "unstructured_log_redacted"
            record.args = ()
            return True
        first, second, third = record.args
        if record.msg.startswith("development_api_timing"):
            valid = (
                isinstance(first, str) and first in {"questionnaire_session_create", "questionnaire_answer_write", "recommendation"}
                and isinstance(second, int)
                and isinstance(third, (int, float))
            )
        else:
            valid = (
                isinstance(first, str) and first in {"login_failure", "forbidden", "rate_limited", "server_error"}
                and isinstance(second, int)
                and isinstance(third, int)
            )
        if not valid:
            record.msg = "unstructured_log_redacted"
            record.args = ()
        return True


def configure_logging(log_level: str) -> logging.Logger:
    """Configure one application logger; handlers are not duplicated on re-entry."""
    logger = logging.getLogger("shahab")
    logger.setLevel(log_level)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        handler.addFilter(RedactingFilter())
        logger.addHandler(handler)
    return logger
