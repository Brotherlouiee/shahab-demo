"""Structured logging helpers that redact sensitive values before emission."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

SENSITIVE_FIELD_MARKERS = ("password", "secret", "token", "authorization", "cookie", "otp", "api_key")
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
        if isinstance(record.msg, Mapping):
            record.msg = redact_value(record.msg)
        if isinstance(record.args, Mapping):
            record.args = redact_value(record.args)
        elif isinstance(record.args, tuple):
            record.args = tuple(redact_value(item) for item in record.args)
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
