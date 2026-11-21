"""Minimal immutable loan-facing domain types shared by future use cases and ports."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoanReference:
    """Stable reference only; display data and persistence fields remain outside this type."""

    loan_id: str


@dataclass(frozen=True, slots=True)
class RecommendationConfigReference:
    """Identifies an approved configuration without embedding mutable source data."""

    config_version: str
