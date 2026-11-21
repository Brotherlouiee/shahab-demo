"""Immutable canonical loan rows produced after staging and normalization.

The type intentionally carries evidence and eligibility separately. It is not a
database model or a recommendation result: later persistence and scoring stages
must retain the same source-row fingerprint and cannot reinterpret ambiguity.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from .normalization import NormalizationState, NormalizedVariable

_REQUIRED_VARIABLE_IDS = frozenset(
    {
        "maxAmount",
        "monthlyInstallment",
        "maxRepaymentMonths",
        "interestRate",
        "depositRequired",
        "depositHoldingMonths",
        "loanToDepositRatio",
        "guaranteeType",
    }
)
_CORE_RANKING_VARIABLE_IDS = frozenset({"maxAmount", "monthlyInstallment", "maxRepaymentMonths", "interestRate"})
_DISPLAY_FIELD_IDS = frozenset({"bankLogo", "requiredDepositAccount", "conditions"})


class RowRejectionCode(StrEnum):
    """Reasons that prevent construction of a canonical row altogether."""

    INVALID_ROW_NUMBER = "invalid_row_number"
    MISSING_LENDER_NAME = "missing_lender_name"
    MISSING_LOAN_NAME = "missing_loan_name"
    VARIABLE_SET_MISMATCH = "variable_set_mismatch"
    VARIABLE_ID_MISMATCH = "variable_id_mismatch"
    UNKNOWN_DISPLAY_FIELD = "unknown_display_field"


class RankingEligibility(StrEnum):
    """A row can be valid canonical data while still needing data-quality review."""

    RANKABLE = "rankable"
    NEEDS_REVIEW = "needs_review"


@dataclass(frozen=True, slots=True)
class CanonicalRowRejection:
    """Non-mutating construction rejection retained as source-row audit evidence."""

    code: RowRejectionCode
    source_row_number: int
    message: str


@dataclass(frozen=True, slots=True)
class CanonicalLoanRow:
    """One immutable normalized loan row with explicit ranking eligibility evidence."""

    source_row_number: int
    source_row_fingerprint: str
    lender_name: str
    loan_name: str
    variables: Mapping[str, NormalizedVariable]
    display_fields: Mapping[str, str]
    ranking_eligibility: RankingEligibility
    ranking_excluded_variable_ids: tuple[str, ...]

    @property
    def identity_key(self) -> tuple[str, str]:
        """Stable catalogue identity; Persian labels never become opaque IDs."""
        return (self.lender_name, self.loan_name)


def build_canonical_loan_row(
    *,
    source_file_sha256: str,
    source_row_number: int,
    lender_name: str | None,
    loan_name: str | None,
    variables: Mapping[str, NormalizedVariable],
    display_fields: Mapping[str, str] | None = None,
) -> CanonicalLoanRow | CanonicalRowRejection:
    """Build a declared variable set and retain ambiguity as eligibility evidence.

    Unknown core data is not a malformed source row. The approved decision puts
    it into needs-review later, so construction preserves the row and its
    explicit exclusion evidence rather than rejecting or coercing its value.
    """
    if source_row_number <= 0:
        return CanonicalRowRejection(
            RowRejectionCode.INVALID_ROW_NUMBER, source_row_number, "Row number must be positive."
        )
    lender = (lender_name or "").strip()
    if not lender:
        return CanonicalRowRejection(
            RowRejectionCode.MISSING_LENDER_NAME, source_row_number, "Lender name is required."
        )
    loan = (loan_name or "").strip()
    if not loan:
        return CanonicalRowRejection(RowRejectionCode.MISSING_LOAN_NAME, source_row_number, "Loan name is required.")
    if frozenset(variables) != _REQUIRED_VARIABLE_IDS:
        return CanonicalRowRejection(
            RowRejectionCode.VARIABLE_SET_MISMATCH,
            source_row_number,
            "Exactly the eight approved loan variables are required.",
        )
    if any(variable_id != value.variable_id for variable_id, value in variables.items()):
        return CanonicalRowRejection(
            RowRejectionCode.VARIABLE_ID_MISMATCH,
            source_row_number,
            "A mapping key must match its normalized variable identifier.",
        )
    fields = dict(display_fields or {})
    if unknown_fields := set(fields).difference(_DISPLAY_FIELD_IDS):
        return CanonicalRowRejection(
            RowRejectionCode.UNKNOWN_DISPLAY_FIELD,
            source_row_number,
            f"Display field is not approved: {sorted(unknown_fields)[0]}",
        )
    exclusions = tuple(
        variable_id
        for variable_id in sorted(_CORE_RANKING_VARIABLE_IDS)
        if variables[variable_id].state is not NormalizationState.CLASSIFIED
    )
    fingerprint_material = f"{source_file_sha256}:{source_row_number}".encode()
    return CanonicalLoanRow(
        source_row_number=source_row_number,
        source_row_fingerprint=hashlib.sha256(fingerprint_material).hexdigest(),
        lender_name=lender,
        loan_name=loan,
        variables=MappingProxyType(dict(variables)),
        display_fields=MappingProxyType(fields),
        ranking_eligibility=RankingEligibility.NEEDS_REVIEW if exclusions else RankingEligibility.RANKABLE,
        ranking_excluded_variable_ids=exclusions,
    )
