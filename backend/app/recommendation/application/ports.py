"""Application boundary for reading one approved recommendation snapshot."""

from __future__ import annotations

from typing import Protocol

from backend.app.recommendation.domain.entities import RecommendationSnapshot


class RecommendationSnapshotRepository(Protocol):
    """Return one immutable, approved data/configuration snapshot per execution.

    An infrastructure adapter owns transaction isolation and serving-version
    filtering. It must not return a mutable live collection or let transport
    code choose a draft/raw version. This keeps a run reproducible when the
    catalogue or configuration changes concurrently after the snapshot read.
    """

    def read_approved_snapshot(self) -> RecommendationSnapshot:
        """Return the candidate set and version identifiers from one approved read."""
