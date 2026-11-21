"""Strict structural validation of raw delimited evidence before any normalization is permitted."""

from __future__ import annotations

from backend.app.data_pipeline.domain.staging_validation import (
    StagingIssue,
    StagingIssueCode,
    StagingValidationResult,
)


class DelimitedStagingValidator:
    """Validate a declared source contract without coercing, repairing or silently dropping data.

    Canonical `.unitext` sources are UTF-16 LE today; encoding is an explicit constructor
    contract so a future approved source can use another codec without guessing. Duplicate
    source evidence is a review signal, not a reason to mutate immutable raw storage.
    """

    def __init__(self, *, expected_headers: tuple[str, ...], encoding: str, delimiter: str = "\t") -> None:
        if not expected_headers or not encoding or len(delimiter) != 1:
            raise ValueError("expected_headers, encoding and a one-character delimiter are required")
        self._expected_headers = expected_headers
        self._encoding = encoding
        self._delimiter = delimiter

    def validate(
        self, content: bytes, *, source_sha256: str, known_source_hashes: frozenset[str]
    ) -> StagingValidationResult:
        issues: list[StagingIssue] = []
        if source_sha256 in known_source_hashes:
            issues.append(
                StagingIssue(StagingIssueCode.DUPLICATE_SOURCE_EVIDENCE, "Source hash was previously ingested.")
            )
        try:
            text = content.decode(self._encoding, errors="strict")
        except UnicodeDecodeError:
            return StagingValidationResult(
                headers=(),
                row_count=0,
                issues=tuple(
                    issues + [StagingIssue(StagingIssueCode.UNSUPPORTED_ENCODING, "Source cannot be decoded.")]
                ),
            )
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return StagingValidationResult(
                headers=(),
                row_count=0,
                issues=tuple(issues + [StagingIssue(StagingIssueCode.EMPTY_SOURCE, "Source has no rows.")]),
            )
        headers = tuple(cell.strip() for cell in lines[0].split(self._delimiter))
        if len(set(headers)) != len(headers):
            issues.append(StagingIssue(StagingIssueCode.DUPLICATE_HEADER, "Header cells must be unique.", row_number=1))
        if headers != self._expected_headers:
            issues.append(
                StagingIssue(
                    StagingIssueCode.INVALID_HEADER, "Header does not match the declared source contract.", row_number=1
                )
            )
        for row_number, line in enumerate(lines[1:], start=2):
            if len(line.split(self._delimiter)) != len(headers):
                issues.append(
                    StagingIssue(
                        StagingIssueCode.ROW_WIDTH_MISMATCH,
                        "Row column count differs from header.",
                        row_number=row_number,
                    )
                )
        return StagingValidationResult(headers=headers, row_count=len(lines) - 1, issues=tuple(issues))
