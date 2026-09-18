"""Pure, conservative parsers for approved Persian loan-source scalar formats.

These functions normalize source notation only. They do not assign loan categories,
make a recommendation decision, or infer a value from free-text loan conditions.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from .value_schemas import ParsedScalar, ScalarParseResult, UnknownReason, UnknownScalar

_DIGIT_TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_UNKNOWN_LABELS = {"نامشخص", "unknown"}
_VARIABLE_LABELS = {"متغیر", "variable"}
_MONEY_UNITS = {"میلیون": Decimal("1000000"), "میلیارد": Decimal("1000000000")}


def normalize_source_text(raw: str | None) -> str:
    """Normalize digit glyphs, separators, and whitespace without interpreting value meaning."""
    if raw is None:
        return ""
    text = str(raw).translate(_DIGIT_TRANSLATION)
    text = text.replace("\ufeff", "").replace("٪", "%").replace("٫", ".").replace("٬", ",")
    return " ".join(text.strip().split())


def unknown_scalar(raw: str | None) -> UnknownScalar | None:
    """Return a typed unknown only for explicitly approved unknown source labels."""
    normalized = normalize_source_text(raw).casefold()
    if not normalized:
        return UnknownScalar(UnknownReason.BLANK, "" if raw is None else str(raw))
    if normalized in _UNKNOWN_LABELS:
        return UnknownScalar(UnknownReason.UNKNOWN_LABEL, str(raw))
    if normalized in _VARIABLE_LABELS:
        return UnknownScalar(UnknownReason.VARIABLE_LABEL, str(raw))
    return None


def _parse_decimal_token(token: str) -> Decimal:
    compact = token.replace(" ", "").replace(",", "")
    # In supplied sources, 1/5 میلیارد means 1.5 billion, while 5/000/000 is grouping.
    if re.fullmatch(r"\d+/\d{1,2}", compact):
        compact = compact.replace("/", ".")
    else:
        compact = compact.replace("/", "")
    value = Decimal(compact)
    if value < 0:
        raise ValueError("negative values are outside the approved loan-source scalar contract")
    return value


def _numeric_prefix(text: str) -> str:
    match = re.match(r"^([0-9][0-9,./ ]*)", text)
    if not match:
        raise ValueError("missing numeric prefix")
    return match.group(1)


def _contains_explicit_range(text: str) -> bool:
    """Reject source ranges; choosing an endpoint is a later explicit policy decision."""
    return bool(re.search(r"(?:\sتا\s|\sالی\s|\sبین\s|\s[-–]\s)", text))


def parse_money_tomans(raw: str | None) -> ScalarParseResult:
    """Parse a non-negative scalar money amount into toman; ranges remain unparseable."""
    unknown = unknown_scalar(raw)
    if unknown:
        return unknown
    text = normalize_source_text(raw)
    try:
        if _contains_explicit_range(text):
            raise ValueError("ranges are not scalar values")
        number = _parse_decimal_token(_numeric_prefix(text))
        multiplier = next((factor for label, factor in _MONEY_UNITS.items() if label in text), Decimal("1"))
        if "ریال" in text:
            if multiplier != 1:
                raise ValueError("mixed rial and magnitude units are unsupported")
            number /= Decimal("10")
        return ParsedScalar(number * multiplier, "toman", str(raw))
    except (InvalidOperation, ValueError):
        return UnknownScalar(UnknownReason.UNPARSEABLE, "" if raw is None else str(raw))


def parse_percentage(raw: str | None) -> ScalarParseResult:
    """Parse a non-negative percentage scalar; ranges and prose remain unparseable."""
    unknown = unknown_scalar(raw)
    if unknown:
        return unknown
    text = normalize_source_text(raw)
    try:
        if _contains_explicit_range(text):
            raise ValueError("ranges are not scalar values")
        if "%" not in text and "درصد" not in text:
            raise ValueError("percentage marker is required")
        return ParsedScalar(_parse_decimal_token(_numeric_prefix(text)), "percent", str(raw))
    except (InvalidOperation, ValueError):
        return UnknownScalar(UnknownReason.UNPARSEABLE, "" if raw is None else str(raw))


def parse_months(raw: str | None) -> ScalarParseResult:
    """Parse a non-negative month scalar; interval text is intentionally not inferred."""
    unknown = unknown_scalar(raw)
    if unknown:
        return unknown
    text = normalize_source_text(raw)
    try:
        if _contains_explicit_range(text):
            raise ValueError("ranges are not scalar values")
        if "ماه" not in text:
            raise ValueError("month marker is required")
        value = _parse_decimal_token(_numeric_prefix(text))
        if value != value.to_integral_value():
            raise ValueError("months must be integral")
        return ParsedScalar(value, "months", str(raw))
    except (InvalidOperation, ValueError):
        return UnknownScalar(UnknownReason.UNPARSEABLE, "" if raw is None else str(raw))
