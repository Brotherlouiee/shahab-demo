"""Immutable metadata for one captured source object, deliberately separate from parsed loan data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RawSourceRecord:
    """Content-addressed source evidence persisted before any parser is allowed to inspect it.

    `sha256` is both the integrity proof and storage identity. Metadata records who supplied
    the source and which declared version was captured, but never stores credentials or raw
    bytes in logs/database fields. A later staging row refers back to this record by hash.
    """

    sha256: str
    byte_count: int
    original_filename: str
    source_reference: str
    source_version: str
    owner_reference: str
    received_at: datetime

    def __post_init__(self) -> None:
        if len(self.sha256) != 64 or any(character not in "0123456789abcdef" for character in self.sha256):
            raise ValueError("sha256 must be a lowercase 64-character hexadecimal digest")
        if self.byte_count < 0:
            raise ValueError("byte_count must be non-negative")
        for field_name in ("original_filename", "source_reference", "source_version", "owner_reference"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be blank")
        if self.received_at.tzinfo is None:
            raise ValueError("received_at must be timezone-aware")
