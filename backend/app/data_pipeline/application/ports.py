"""Ports for raw evidence storage; no parser or database implementation leaks into the use case."""

from __future__ import annotations

from typing import Protocol


class ImmutableRawObjectStore(Protocol):
    """Store source bytes once by digest and report whether this call created a new object."""

    def put_if_absent(self, *, sha256: str, content: bytes) -> bool:
        """Atomically create the object or preserve the pre-existing exact content."""
