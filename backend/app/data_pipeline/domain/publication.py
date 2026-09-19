"""Versioned approval and serving-publication value objects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .canonical_row import CanonicalLoanRow


class ServingVersionState(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    PUBLISHED = "published"
    SUPERSEDED = "superseded"


@dataclass(frozen=True, slots=True)
class CatalogueDiff:
    """Auditable identity-level delta against the previous published version."""

    added: tuple[tuple[str, str], ...]
    changed: tuple[tuple[str, str], ...]
    removed: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    """An explicit human decision; absence can never imply approval."""

    actor_reference: str
    reason: str
    decided_at: datetime


@dataclass(frozen=True, slots=True)
class ServingDataVersion:
    """Immutable canonical rows and state transitions for one prepared import."""

    version_id: str
    import_id: str
    source_file_sha256: str
    parser_version: str
    rows: tuple[CanonicalLoanRow, ...]
    diff: CatalogueDiff
    state: ServingVersionState
    approval: ApprovalRecord | None = None


def calculate_catalogue_diff(
    previous_rows: tuple[CanonicalLoanRow, ...], candidate_rows: tuple[CanonicalLoanRow, ...]
) -> CatalogueDiff:
    """Compare immutable rows by business identity without mutating either version."""
    previous = {row.identity_key: row for row in previous_rows}
    candidate = {row.identity_key: row for row in candidate_rows}
    added = tuple(sorted(set(candidate).difference(previous)))
    removed = tuple(sorted(set(previous).difference(candidate)))
    changed = tuple(key for key in sorted(set(candidate).intersection(previous)) if candidate[key] != previous[key])
    return CatalogueDiff(added=added, changed=changed, removed=removed)
