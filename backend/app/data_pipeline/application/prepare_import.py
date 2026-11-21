"""Prepare an auditable import plan without publishing a serving version.

The CLI boundary supplies only a reviewed manifest shape. This use case keeps
normalization and rejection evidence in domain objects so a future PostgreSQL
adapter can persist them without re-parsing a user-controlled file.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from backend.app.data_pipeline.domain.canonical_row import (
    CanonicalLoanRow,
    CanonicalRowRejection,
    build_canonical_loan_row,
)
from backend.app.data_pipeline.domain.normalization import normalize_variable


class ImportPlanIssueCode(StrEnum):
    INVALID_SOURCE_HASH = "invalid_source_hash"
    DUPLICATE_SOURCE_ROW = "duplicate_source_row"
    DUPLICATE_CATALOGUE_IDENTITY = "duplicate_catalogue_identity"


@dataclass(frozen=True, slots=True)
class ImportPlanIssue:
    """A non-mutating manifest issue retained for operational review."""

    code: ImportPlanIssueCode
    message: str
    source_row_number: int | None = None


@dataclass(frozen=True, slots=True)
class ImportManifestRow:
    """Narrow, JSON-decoded input shape; all eight values remain raw source text."""

    source_row_number: int
    lender_name: str | None
    loan_name: str | None
    variable_values: Mapping[str, str | None]
    display_fields: Mapping[str, str] | None = None


@dataclass(frozen=True, slots=True)
class ImportPreparation:
    """Immutable plan passed to review, never directly to public serving."""

    source_file_sha256: str
    parser_version: str
    accepted_rows: tuple[CanonicalLoanRow, ...]
    rejected_rows: tuple[CanonicalRowRejection, ...]
    issues: tuple[ImportPlanIssue, ...]

    @property
    def is_publishable_candidate(self) -> bool:
        """A plan with any rejection/issue needs correction before approval."""
        return bool(self.accepted_rows) and not self.rejected_rows and not self.issues


def prepare_import_manifest(
    *,
    source_file_sha256: str,
    parser_version: str,
    rows: Sequence[ImportManifestRow],
) -> ImportPreparation:
    """Normalize a reviewed manifest deterministically and collect all evidence.

    No item is silently dropped: invalid source identity, duplicate row number,
    duplicate catalogue identity and canonical-row rejection each appear in the
    returned plan. The caller is responsible for recording the plan/diff and
    obtaining approval before the separate serving publication use case runs.
    """
    issues: list[ImportPlanIssue] = []
    if len(source_file_sha256) != 64 or any(char not in "0123456789abcdef" for char in source_file_sha256.lower()):
        issues.append(
            ImportPlanIssue(
                ImportPlanIssueCode.INVALID_SOURCE_HASH, "Source SHA-256 must be 64 hexadecimal characters."
            )
        )
    if not parser_version.strip():
        raise ValueError("parser version is required")
    accepted: list[CanonicalLoanRow] = []
    rejected: list[CanonicalRowRejection] = []
    row_numbers: set[int] = set()
    identities: set[tuple[str, str]] = set()
    for raw_row in rows:
        if raw_row.source_row_number in row_numbers:
            issues.append(
                ImportPlanIssue(
                    ImportPlanIssueCode.DUPLICATE_SOURCE_ROW,
                    "Source row number appears more than once.",
                    raw_row.source_row_number,
                )
            )
            continue
        row_numbers.add(raw_row.source_row_number)
        variables = {
            variable_id: normalize_variable(variable_id, value)
            for variable_id, value in raw_row.variable_values.items()
        }
        result = build_canonical_loan_row(
            source_file_sha256=source_file_sha256,
            source_row_number=raw_row.source_row_number,
            lender_name=raw_row.lender_name,
            loan_name=raw_row.loan_name,
            variables=variables,
            display_fields=raw_row.display_fields,
        )
        if isinstance(result, CanonicalRowRejection):
            rejected.append(result)
            continue
        if result.identity_key in identities:
            issues.append(
                ImportPlanIssue(
                    ImportPlanIssueCode.DUPLICATE_CATALOGUE_IDENTITY,
                    "Lender and loan name must be unique within one import plan.",
                    raw_row.source_row_number,
                )
            )
            continue
        identities.add(result.identity_key)
        accepted.append(result)
    return ImportPreparation(
        source_file_sha256=source_file_sha256,
        parser_version=parser_version,
        accepted_rows=tuple(accepted),
        rejected_rows=tuple(rejected),
        issues=tuple(issues),
    )
