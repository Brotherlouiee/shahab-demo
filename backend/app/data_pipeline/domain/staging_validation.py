"""Typed, non-destructive staging validation findings for raw delimited source evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StagingIssueCode(StrEnum):
    UNSUPPORTED_ENCODING = "unsupported_encoding"
    EMPTY_SOURCE = "empty_source"
    INVALID_HEADER = "invalid_header"
    DUPLICATE_HEADER = "duplicate_header"
    ROW_WIDTH_MISMATCH = "row_width_mismatch"
    DUPLICATE_SOURCE_EVIDENCE = "duplicate_source_evidence"


@dataclass(frozen=True, slots=True)
class StagingIssue:
    """A precise non-mutating issue; row 1 is the header and source bytes remain untouched."""

    code: StagingIssueCode
    message: str
    row_number: int | None = None


@dataclass(frozen=True, slots=True)
class StagingValidationResult:
    """Validated table shape plus findings; downstream stages must refuse results with issues."""

    headers: tuple[str, ...]
    row_count: int
    issues: tuple[StagingIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues
