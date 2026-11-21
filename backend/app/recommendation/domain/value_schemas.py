"""Framework-independent value contracts for canonical loan-source parsing."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class UnknownReason(StrEnum):
    BLANK = "blank"
    UNKNOWN_LABEL = "unknown_label"
    VARIABLE_LABEL = "variable_label"
    UNPARSEABLE = "unparseable"


@dataclass(frozen=True)
class ParsedScalar:
    """A parsed source scalar; all numeric values retain their normalized unit."""

    value: Decimal
    unit: str
    raw: str


@dataclass(frozen=True)
class UnknownScalar:
    """A source value intentionally not interpreted as a numeric/category value."""

    reason: UnknownReason
    raw: str


ScalarParseResult = ParsedScalar | UnknownScalar
