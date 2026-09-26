"""Pure, conservative conversion of approved source fields to canonical categories.

This module deliberately does not score or approve loans. A value is classified
only when a scalar/text label fits an explicitly versioned category rule. Values
in a source-matrix gap or outside its stated maximum remain observable but cannot
silently affect a future recommendation.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from backend.app.recommendation.domain.persian_value_parser import (
    normalize_source_text,
    parse_money_tomans,
    parse_months,
    parse_percentage,
)
from backend.app.recommendation.domain.value_schemas import ParsedScalar, UnknownScalar


class NormalizationState(StrEnum):
    """Outcome state retained for review before any scoring policy is applied."""

    CLASSIFIED = "classified"
    UNKNOWN = "unknown"
    VARIABLE = "variable"
    UNPARSEABLE = "unparseable"
    UNMAPPED = "unmapped"


@dataclass(frozen=True, slots=True)
class NormalizedVariable:
    """Canonical category evidence for one source value, never a scoring result."""

    variable_id: str
    category_id: str | None
    numeric_value: Decimal | None
    state: NormalizationState
    raw: str


@dataclass(frozen=True, slots=True)
class CategoryBand:
    """An explicit lower/upper category boundary from the approved source matrix."""

    category_id: str
    minimum: Decimal | None = None
    maximum: Decimal | None = None
    minimum_inclusive: bool = True
    maximum_inclusive: bool = True

    def contains(self, value: Decimal) -> bool:
        """Return whether the value belongs to this exact declared band."""
        if self.minimum is not None and (
            value < self.minimum or (value == self.minimum and not self.minimum_inclusive)
        ):
            return False
        return not (
            self.maximum is not None
            and (value > self.maximum or (value == self.maximum and not self.maximum_inclusive))
        )


# Source: .agents/documents/ماتریس گزینه های متغیرهای وام.unitext, mirrored as
# the reviewable Markdown matrix. Adjacent displayed ranges share a boundary; the
# earlier row owns that boundary. Explicit source gaps (e.g. 5 months) and values
# above the stated 35-billion-toman cap stay UNMAPPED rather than guessed.
_BANDS: dict[str, tuple[CategoryBand, ...]] = {
    "maxAmount": (
        CategoryBand("amount_0_50m", Decimal("0"), Decimal("50000000")),
        CategoryBand("amount_50_150m", Decimal("50000000"), Decimal("150000000"), minimum_inclusive=False),
        CategoryBand("amount_150_300m", Decimal("150000000"), Decimal("300000000"), minimum_inclusive=False),
        CategoryBand("amount_300_600m", Decimal("300000000"), Decimal("600000000"), minimum_inclusive=False),
        CategoryBand("amount_600m_1_5b", Decimal("600000000"), Decimal("1500000000"), minimum_inclusive=False),
        CategoryBand("amount_1_5b_5b", Decimal("1500000000"), Decimal("5000000000"), minimum_inclusive=False),
        CategoryBand("amount_5b_15b", Decimal("5000000000"), Decimal("15000000000"), minimum_inclusive=False),
        CategoryBand("amount_15b_35b", Decimal("15000000000"), Decimal("35000000000"), minimum_inclusive=False),
    ),
    "monthlyInstallment": (
        CategoryBand("installment_lt_5m", maximum=Decimal("5000000"), maximum_inclusive=False),
        CategoryBand("installment_5_15m", Decimal("5000000"), Decimal("15000000")),
        CategoryBand("installment_15_50m", Decimal("15000000"), Decimal("50000000"), minimum_inclusive=False),
        CategoryBand("installment_50_200m", Decimal("50000000"), Decimal("200000000"), minimum_inclusive=False),
        CategoryBand("installment_200m_1b", Decimal("200000000"), Decimal("1000000000"), minimum_inclusive=False),
        CategoryBand("installment_gt_1b", Decimal("1000000000"), minimum_inclusive=False),
    ),
    "maxRepaymentMonths": (
        CategoryBand("term_lt_5m", maximum=Decimal("5"), maximum_inclusive=False),
        CategoryBand("term_6_12m", Decimal("6"), Decimal("12")),
        CategoryBand("term_13_24m", Decimal("13"), Decimal("24")),
        CategoryBand("term_25_48m", Decimal("25"), Decimal("48")),
        CategoryBand("term_49_60m", Decimal("49"), Decimal("60")),
        CategoryBand("term_gt_60m", Decimal("60"), minimum_inclusive=False),
    ),
    "interestRate": (
        CategoryBand("rate_0_4", Decimal("0"), Decimal("4")),
        CategoryBand("rate_5_14", Decimal("5"), Decimal("14")),
        CategoryBand("rate_15_20", Decimal("15"), Decimal("20")),
        CategoryBand("rate_21_23", Decimal("21"), Decimal("23")),
        CategoryBand("rate_gt_23", Decimal("23"), minimum_inclusive=False),
    ),
    "depositHoldingMonths": (
        CategoryBand("holding_up_to_1m", Decimal("0"), Decimal("1")),
        CategoryBand("holding_1_3m", Decimal("1"), Decimal("3"), minimum_inclusive=False),
        CategoryBand("holding_3_6m", Decimal("3"), Decimal("6"), minimum_inclusive=False),
        CategoryBand("holding_6_12m", Decimal("6"), Decimal("12"), minimum_inclusive=False),
        CategoryBand("holding_gt_12m", Decimal("12"), minimum_inclusive=False),
    ),
    "loanToDepositRatio": (
        CategoryBand("ratio_lt_100", maximum=Decimal("100"), maximum_inclusive=False),
        CategoryBand("ratio_100_200", Decimal("100"), Decimal("200")),
        CategoryBand("ratio_200_400", Decimal("200"), Decimal("400"), minimum_inclusive=False),
        CategoryBand("ratio_gt_400", Decimal("400"), minimum_inclusive=False),
    ),
}
_PARSERS: dict[str, Callable[[str | None], ParsedScalar | UnknownScalar]] = {
    "maxAmount": parse_money_tomans,
    "monthlyInstallment": parse_money_tomans,
    "maxRepaymentMonths": parse_months,
    "interestRate": parse_percentage,
    "depositHoldingMonths": parse_months,
    "loanToDepositRatio": parse_percentage,
}
_GUARANTEE_CATEGORIES = {
    "وثایق سخت": "hardCollateral",
    "تعهد شخص ثالث": "thirdPartyUndertaking",
    # The loan catalogue uses the plural of the exact same approved label.
    "تعهدات شخص ثالث": "thirdPartyUndertaking",
    "تعهد فردی": "personalUndertaking",
    "تعهدات فردی": "personalUndertaking",
}


def _unknown_result(variable_id: str, parsed: UnknownScalar) -> NormalizedVariable:
    state = {
        "blank": NormalizationState.UNKNOWN,
        "unknown_label": NormalizationState.UNKNOWN,
        "variable_label": NormalizationState.VARIABLE,
    }.get(parsed.reason.value, NormalizationState.UNPARSEABLE)
    return NormalizedVariable(variable_id, None, None, state, parsed.raw)


def _text_state(text: str) -> NormalizationState:
    if text in {"", "نامشخص"}:
        return NormalizationState.UNKNOWN
    if text == "متغیر":
        return NormalizationState.VARIABLE
    return NormalizationState.UNMAPPED


def normalize_numeric_variable(variable_id: str, raw: str | None) -> NormalizedVariable:
    """Parse one approved scalar field and categorise it without filling source gaps."""
    parser = _PARSERS.get(variable_id)
    if parser is None:
        raise ValueError(f"unsupported numeric variable: {variable_id}")
    parsed = parser(raw)
    if isinstance(parsed, UnknownScalar):
        return _unknown_result(variable_id, parsed)
    for band in _BANDS[variable_id]:
        if band.contains(parsed.value):
            return NormalizedVariable(
                variable_id, band.category_id, parsed.value, NormalizationState.CLASSIFIED, parsed.raw
            )
    return NormalizedVariable(variable_id, None, parsed.value, NormalizationState.UNMAPPED, parsed.raw)


def normalize_deposit_required(raw: str | None) -> NormalizedVariable:
    """Map only explicit yes/no labels; every other source form is non-scoring evidence."""
    text = normalize_source_text(raw)
    category = {
        "دارد": "deposit_required",
        "بله": "deposit_required",
        "ندارد": "deposit_not_required",
        "خیر": "deposit_not_required",
    }.get(text)
    if category is not None:
        return NormalizedVariable(
            "depositRequired", category, None, NormalizationState.CLASSIFIED, "" if raw is None else str(raw)
        )
    return NormalizedVariable("depositRequired", None, None, _text_state(text), "" if raw is None else str(raw))


def normalize_guarantee_type(raw: str | None) -> NormalizedVariable:
    """Map only the three exact approved guarantee labels from the source matrix."""
    text = normalize_source_text(raw)
    category = _GUARANTEE_CATEGORIES.get(text)
    if category is not None:
        return NormalizedVariable(
            "guaranteeType", category, None, NormalizationState.CLASSIFIED, "" if raw is None else str(raw)
        )
    return NormalizedVariable("guaranteeType", None, None, _text_state(text), "" if raw is None else str(raw))


def normalize_variable(variable_id: str, raw: str | None) -> NormalizedVariable:
    """Normalise any approved loan variable through its narrow, explicit rule."""
    if variable_id == "depositRequired":
        return normalize_deposit_required(raw)
    if variable_id == "guaranteeType":
        return normalize_guarantee_type(raw)
    return normalize_numeric_variable(variable_id, raw)
