"""Application use cases for explicit approval and atomic serving publication."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Protocol

from backend.app.data_pipeline.domain.canonical_row import CanonicalLoanRow
from backend.app.data_pipeline.domain.publication import (
    ApprovalRecord,
    ServingDataVersion,
    ServingVersionState,
    calculate_catalogue_diff,
)


class ServingVersionRepository(Protocol):
    """Persistence port; implementations must make pointer changes atomic."""

    def get_current_published(self) -> ServingDataVersion | None:
        """Return the current immutable serving version, if one exists."""

    def get_by_id(self, version_id: str) -> ServingDataVersion | None:
        """Return a stored version without exposing mutable repository state."""

    def save_draft(self, version: ServingDataVersion, *, decision: ApprovalRecord | None = None) -> None:
        """Persist a unique draft; existing versions are immutable."""

    def replace_version(self, version: ServingDataVersion) -> None:
        """Replace a version after a legal state transition only."""

    def publish_atomically(
        self, approved_version: ServingDataVersion, *, decision: ApprovalRecord | None = None
    ) -> ServingDataVersion:
        """Publish one approved version and supersede the old pointer atomically."""

    def rollback_atomically(
        self,
        target: ServingDataVersion,
        *,
        expected_current_version_id: str,
        decision: ApprovalRecord,
    ) -> ServingDataVersion:
        """Compare-and-switch plus decision recording in one transaction.

        Reject stale current/target state. Preserve rows and original approval;
        rollback evidence is a new decision, never replacement of that approval.
        A durable adapter must commit pointer and evidence together.
        """


class ServingPublicationService:
    """Coordinates draft, approval and publish while keeping decisions server-side.

    This low-level trusted primitive is not a public authorization boundary.
    InternalDataOperations guards the operations flow; existing OS-trusted CLI
    jobs remain distinct. Never expose this primitive directly as a route.
    """

    def __init__(self, repository: ServingVersionRepository) -> None:
        self._repository = repository

    def prepare(
        self,
        *,
        version_id: str,
        import_id: str,
        source_file_sha256: str,
        parser_version: str,
        rows: tuple[CanonicalLoanRow, ...],
        decision: ApprovalRecord | None = None,
    ) -> ServingDataVersion:
        """Create a draft and diff; duplicate source/version IDs are port errors."""
        if not all((version_id, import_id, source_file_sha256, parser_version)):
            raise ValueError("version, import, source hash and parser version are required")
        if not rows:
            raise ValueError("a serving version requires at least one canonical row")
        previous = self._repository.get_current_published()
        version = ServingDataVersion(
            version_id=version_id,
            import_id=import_id,
            source_file_sha256=source_file_sha256,
            parser_version=parser_version,
            rows=rows,
            diff=calculate_catalogue_diff((), rows)
            if previous is None
            else calculate_catalogue_diff(previous.rows, rows),
            state=ServingVersionState.DRAFT,
        )
        self._repository.save_draft(version, decision=decision)
        return version

    def approve(
        self, *, version_id: str, actor_reference: str, reason: str, decided_at: datetime
    ) -> ServingDataVersion:
        """Attach a human approval to a draft; published versions cannot change."""
        version = self._require_version(version_id)
        if version.state is not ServingVersionState.DRAFT:
            raise ValueError("only a draft version can be approved")
        if not actor_reference.strip() or not reason.strip():
            raise ValueError("approval actor and reason are required")
        approved = replace(
            version,
            state=ServingVersionState.APPROVED,
            approval=ApprovalRecord(actor_reference.strip(), reason.strip(), decided_at),
        )
        self._repository.replace_version(approved)
        return approved

    def publish(self, *, version_id: str, decision: ApprovalRecord | None = None) -> ServingDataVersion:
        """Move only an approved version through the atomic persistence port."""
        version = self._require_version(version_id)
        if version.state is not ServingVersionState.APPROVED or version.approval is None:
            raise ValueError("only an approved version can be published")
        return self._repository.publish_atomically(version, decision=decision)

    def get_version(self, *, version_id: str) -> ServingDataVersion:
        """Trusted read for the authorized coordinator's resource linkage check."""
        return self._require_version(version_id)

    def rollback(
        self,
        *,
        version_id: str,
        expected_current_version_id: str,
        actor_reference: str,
        reason: str,
        decided_at: datetime,
    ) -> ServingDataVersion:
        """Restore an already approved historical version, never a draft.

        CAS must be repeated inside the repository transaction, not inferred
        from this read; a concurrent publication must not be silently lost.
        """
        target = self._require_version(version_id)
        if target.state is not ServingVersionState.SUPERSEDED or target.approval is None:
            raise ValueError("rollback requires an approved superseded version")
        if not actor_reference.strip() or not reason.strip() or not expected_current_version_id.strip():
            raise ValueError("rollback actor, reason and expected current version are required")
        if decided_at.utcoffset() is None:
            raise ValueError("rollback time must be timezone aware")
        return self._repository.rollback_atomically(
            target,
            expected_current_version_id=expected_current_version_id,
            decision=ApprovalRecord(actor_reference.strip(), reason.strip(), decided_at),
        )

    def _require_version(self, version_id: str) -> ServingDataVersion:
        version = self._repository.get_by_id(version_id)
        if version is None:
            raise LookupError("serving version was not found")
        return version
