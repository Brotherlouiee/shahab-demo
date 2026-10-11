"""Authorized internal import/review/approval/publication/rollback coordination.

This is an application boundary, not a credential verifier or HTTP handler.
Existing normalization and publication rules remain the only implementation of
those rules. A trusted T04 adapter must supply identity; T03 must provide durable
review/audit adapters before operational exposure. Customer OTP never qualifies.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from backend.app.data_pipeline.application.prepare_import import (
    ImportManifestRow,
    ImportPreparation,
    prepare_import_manifest,
)
from backend.app.data_pipeline.application.publish_serving_version import ServingPublicationService
from backend.app.data_pipeline.domain.publication import ApprovalRecord, ServingDataVersion
from backend.app.operations.authorization import OperationsAuthorizer, OperationsIdentity, utc_now
from backend.app.operations.policy import Permission


@dataclass(frozen=True, slots=True)
class ReviewedImport:
    """Server-retained immutable preparation; callers select an ID, not its content."""

    import_id: str
    actor_reference: str
    reason: str
    created_at: datetime
    preparation: ImportPreparation


class ImportReviewRepository(Protocol):
    """Review evidence port; duplicate IDs must never overwrite stored evidence."""

    def get_by_id(self, import_id: str) -> ReviewedImport | None: ...

    def save_if_absent(self, record: ReviewedImport) -> ReviewedImport:
        """Atomically insert or return an identical retry; conflicting plans fail."""
        ...


class InternalDataOperations:
    """Require current authority before every read/write, including review reads.

    Operator review does not erase issues or repair unknown loan variables.
    Correct rejected input by creating a new import; approval requires its exact
    clean preparation. Configuration editing is intentionally outside T02.
    """

    def __init__(
        self,
        authorizer: OperationsAuthorizer,
        reviews: ImportReviewRepository,
        publication: ServingPublicationService,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._authorizer = authorizer
        self._reviews = reviews
        self._publication = publication
        self._clock = clock

    def import_data(
        self,
        identity: OperationsIdentity | None,
        *,
        import_id: str,
        source_file_sha256: str,
        parser_version: str,
        rows: Sequence[ImportManifestRow],
        reason: str,
    ) -> ReviewedImport:
        actor = self._authorizer.require(identity, Permission.IMPORT)
        now = self._decision_time(reason)
        if not import_id.strip():
            raise ValueError("import ID is required")
        plan = prepare_import_manifest(source_file_sha256=source_file_sha256, parser_version=parser_version, rows=rows)
        # Retain dirty plans for review. Import never publishes or silently
        # drops rejected rows; even a clean plan requires separate approval.
        return self._reviews.save_if_absent(ReviewedImport(import_id, actor, reason.strip(), now, plan))

    def review_import(self, identity: OperationsIdentity | None, *, import_id: str) -> ReviewedImport:
        self._authorizer.require(identity, Permission.REVIEW)
        return self._require_import(import_id)

    def prepare_version(
        self, identity: OperationsIdentity | None, *, import_id: str, version_id: str, reason: str
    ) -> ServingDataVersion:
        actor = self._authorizer.require(identity, Permission.IMPORT)
        now = self._decision_time(reason)
        record = self._require_import(import_id)
        self._require_clean(record)
        plan = record.preparation
        return self._publication.prepare(
            version_id=version_id,
            import_id=record.import_id,
            source_file_sha256=plan.source_file_sha256,
            parser_version=plan.parser_version,
            rows=plan.accepted_rows,
            decision=ApprovalRecord(actor, reason.strip(), now),
        )

    def approve_version(
        self, identity: OperationsIdentity | None, *, version_id: str, reason: str
    ) -> ServingDataVersion:
        actor = self._authorizer.require(identity, Permission.APPROVE)
        now = self._decision_time(reason)
        self._require_linked_version(version_id)
        return self._publication.approve(version_id=version_id, actor_reference=actor, reason=reason, decided_at=now)

    def publish_version(
        self, identity: OperationsIdentity | None, *, version_id: str, reason: str
    ) -> ServingDataVersion:
        actor = self._authorizer.require(identity, Permission.PUBLISH)
        now = self._decision_time(reason)
        self._require_linked_version(version_id)
        return self._publication.publish(version_id=version_id, decision=ApprovalRecord(actor, reason.strip(), now))

    def rollback_version(
        self,
        identity: OperationsIdentity | None,
        *,
        version_id: str,
        expected_current_version_id: str,
        reason: str,
    ) -> ServingDataVersion:
        actor = self._authorizer.require(identity, Permission.ROLLBACK)
        now = self._decision_time(reason)
        self._require_linked_version(version_id)
        return self._publication.rollback(
            version_id=version_id,
            expected_current_version_id=expected_current_version_id,
            actor_reference=actor,
            reason=reason,
            decided_at=now,
        )

    def _require_import(self, import_id: str) -> ReviewedImport:
        record = self._reviews.get_by_id(import_id)
        if record is None:
            raise LookupError("import was not found")
        return record

    @staticmethod
    def _require_clean(record: ReviewedImport) -> None:
        if not record.preparation.is_publishable_candidate:
            raise ValueError("import has blocking review issues")

    def _require_linked_version(self, version_id: str) -> None:
        version = self._publication.get_version(version_id=version_id)
        record = self._require_import(version.import_id)
        self._require_clean(record)
        plan = record.preparation
        if (
            version.source_file_sha256 != plan.source_file_sha256
            or version.parser_version != plan.parser_version
            or version.rows != plan.accepted_rows
        ):
            raise ValueError("version does not match its reviewed import")

    def _decision_time(self, reason: str) -> datetime:
        if not reason.strip():
            raise ValueError("operation reason is required")
        now = self._clock()
        if now.utcoffset() is None:
            raise ValueError("operation time must be timezone aware")
        return now.astimezone(UTC)
