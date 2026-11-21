"""Raw ingest use case: hash, size-check and immutably retain source evidence before parsing."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256

from backend.app.data_pipeline.application.ports import ImmutableRawObjectStore
from backend.app.data_pipeline.domain.raw_source import RawSourceRecord


class RawIngestService:
    """Safely capture a single supplied source object.

    This is intentionally byte-oriented: a `.unitext`, Excel file or a future signed export
    receives identical integrity handling. The max-size gate runs before persistence so an
    oversized or hostile upload cannot consume durable storage. Idempotency is keyed only by
    the SHA-256 digest; same bytes never overwrite or duplicate the evidence object.
    """

    def __init__(self, store: ImmutableRawObjectStore, *, max_bytes: int) -> None:
        if max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        self._store = store
        self._max_bytes = max_bytes

    def ingest_bytes(
        self,
        content: bytes,
        *,
        original_filename: str,
        source_reference: str,
        source_version: str,
        owner_reference: str,
        received_at: datetime,
    ) -> RawSourceRecord:
        """Create one metadata record after immutable content storage succeeds.

        The return value deliberately omits the bytes so callers cannot accidentally log or
        expose source data. Staging will consume the digest through a controlled adapter.
        """
        if len(content) > self._max_bytes:
            raise ValueError("raw source exceeds the configured maximum size")
        digest = sha256(content).hexdigest()
        self._store.put_if_absent(sha256=digest, content=content)
        return RawSourceRecord(
            sha256=digest,
            byte_count=len(content),
            original_filename=original_filename,
            source_reference=source_reference,
            source_version=source_version,
            owner_reference=owner_reference,
            received_at=received_at,
        )
