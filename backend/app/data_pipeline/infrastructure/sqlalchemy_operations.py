"""PostgreSQL implementations of T02 ports, with atomic append-only decisions.

Trusted infrastructure only: compose behind InternalDataOperations after T04
credential verification. The singleton lock serializes low-volume operator writes
across connections. Public serving projections and application wiring are untouched.
"""

from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.data_pipeline.application.operations import ReviewedImport
from backend.app.data_pipeline.domain.publication import (
    ApprovalRecord,
    ServingDataVersion,
    ServingVersionState,
    calculate_catalogue_diff,
)
from backend.app.data_pipeline.infrastructure.operations_codec import (
    decode_diff,
    decode_preparation,
    encode_diff,
    encode_preparation,
)
from backend.app.infrastructure.db.models import AuditEvent, OperationsImport, OperationsVersion, OperationsWorkflowHead

SessionFactory = Callable[[], Session]


def _head(session: Session, *, lock: bool = False) -> OperationsWorkflowHead:
    query = select(OperationsWorkflowHead).where(OperationsWorkflowHead.head_id == 1)
    if lock:
        query = query.with_for_update()
    head = session.scalar(query)
    if head is None:
        raise RuntimeError("operations migration has not initialized the workflow head")
    return head


def _review(session: Session, record: OperationsImport) -> ReviewedImport:
    event = session.scalar(
        select(AuditEvent).where(AuditEvent.import_id == record.import_id, AuditEvent.event_type == "import")
    )
    if event is None:
        raise ValueError("import has no durable decision evidence")
    return ReviewedImport(
        record.import_code,
        event.actor_reference,
        event.reason,
        event.occurred_at,
        decode_preparation(record.preparation, source_hash=record.source_hash, parser_version=record.parser_version),
        event.correlation_id,
    )


def _version(session: Session, record: OperationsVersion, head: OperationsWorkflowHead) -> ServingDataVersion:
    source = session.get(OperationsImport, record.import_id)
    if source is None:
        raise ValueError("version has no reviewed import")
    review = _review(session, source)
    approval_event = session.scalar(
        select(AuditEvent).where(AuditEvent.version_id == record.version_id, AuditEvent.event_type == "approve")
    )
    approval = (
        None
        if approval_event is None
        else ApprovalRecord(
            approval_event.actor_reference,
            approval_event.reason,
            approval_event.occurred_at,
            approval_event.correlation_id,
        )
    )
    if head.version_id == record.version_id:
        state = ServingVersionState.PUBLISHED
    elif session.scalar(select(AuditEvent.event_id).where(AuditEvent.after_version_id == record.version_id).limit(1)):
        state = ServingVersionState.SUPERSEDED
    else:
        state = ServingVersionState.DRAFT if approval is None else ServingVersionState.APPROVED
    return ServingDataVersion(
        record.version_code,
        review.import_id,
        source.source_hash,
        source.parser_version,
        review.preparation.accepted_rows,
        decode_diff(record.diff),
        state,
        approval,
    )


def _decision(actor: str, reason: str, time: datetime) -> None:
    if not actor.strip() or not reason.strip() or time.utcoffset() is None:
        raise ValueError("actor, reason and timezone-aware decision time are required")


def _event(
    session: Session,
    kind: str,
    source_id: UUID,
    decision: ApprovalRecord,
    *,
    version_id: UUID | None = None,
    before: str | None = None,
    after: str,
    previous: UUID | None = None,
    current: UUID | None = None,
) -> None:
    _decision(decision.actor_reference, decision.reason, decision.decided_at)
    session.add(
        AuditEvent(
            event_type=kind,
            import_id=source_id,
            version_id=version_id,
            actor_reference=decision.actor_reference.strip(),
            reason=decision.reason.strip(),
            occurred_at=decision.decided_at.astimezone(UTC),
            correlation_id=decision.correlation_id,
            before_state=before,
            after_state=after,
            before_version_id=previous,
            after_version_id=current,
        )
    )


class SqlAlchemyImportReviewRepository:
    """Immutable reviewed plans; retries return the first committed evidence."""

    def __init__(self, sessions: SessionFactory) -> None:
        self._sessions = sessions

    def get_by_id(self, import_id: str) -> ReviewedImport | None:
        with self._sessions() as session, session.begin():
            row = session.scalar(select(OperationsImport).where(OperationsImport.import_code == import_id))
            return None if row is None else _review(session, row)

    def save_if_absent(self, record: ReviewedImport) -> ReviewedImport:
        _decision(record.actor_reference, record.reason, record.created_at)
        if not record.import_id.strip():
            raise ValueError("import ID is required")
        with self._sessions() as session, session.begin():
            _head(session, lock=True)
            existing = session.scalar(select(OperationsImport).where(OperationsImport.import_code == record.import_id))
            if existing is not None:
                stored = _review(session, existing)
                if (stored.preparation, stored.actor_reference, stored.reason) != (
                    record.preparation,
                    record.actor_reference,
                    record.reason,
                ):
                    raise ValueError("conflicting import retry")
                return stored
            row = OperationsImport(
                import_code=record.import_id,
                source_hash=record.preparation.source_file_sha256,
                parser_version=record.preparation.parser_version,
                preparation=encode_preparation(record.preparation),
            )
            session.add(row)
            session.flush()
            _event(
                session,
                "import",
                row.import_id,
                ApprovalRecord(record.actor_reference, record.reason, record.created_at, record.correlation_id),
                after="reviewed",
            )
            return record


class SqlAlchemyServingVersionRepository:
    """Durable internal version workflow; pointer plus audit commit together."""

    def __init__(self, sessions: SessionFactory) -> None:
        self._sessions = sessions

    def get_current_published(self) -> ServingDataVersion | None:
        with self._sessions() as session, session.begin():
            # Shared lock prevents a reader mixing a head with a later transition.
            head = session.scalar(
                select(OperationsWorkflowHead).where(OperationsWorkflowHead.head_id == 1).with_for_update(read=True)
            )
            if head is None:
                raise RuntimeError("operations migration is required")
            record = None if head.version_id is None else session.get(OperationsVersion, head.version_id)
            return None if record is None else _version(session, record, head)

    def get_by_id(self, version_id: str) -> ServingDataVersion | None:
        with self._sessions() as session, session.begin():
            head = _head(session, lock=True)
            row = session.scalar(select(OperationsVersion).where(OperationsVersion.version_code == version_id))
            return None if row is None else _version(session, row, head)

    def save_draft(self, version: ServingDataVersion, *, decision: ApprovalRecord | None = None) -> None:
        if decision is None or version.state is not ServingVersionState.DRAFT or version.approval is not None:
            raise ValueError("draft preparation requires its own decision")
        with self._sessions() as session, session.begin():
            head = _head(session, lock=True)
            source = session.scalar(select(OperationsImport).where(OperationsImport.import_code == version.import_id))
            if source is None:
                raise ValueError("reviewed import is required")
            review = _review(session, source)
            plan = review.preparation
            if not plan.is_publishable_candidate or (
                version.source_file_sha256,
                version.parser_version,
                version.rows,
            ) != (source.source_hash, source.parser_version, plan.accepted_rows):
                raise ValueError("draft must match its clean reviewed import")
            current = None if head.version_id is None else session.get(OperationsVersion, head.version_id)
            previous_rows = () if current is None else _version(session, current, head).rows
            if version.diff != calculate_catalogue_diff(previous_rows, version.rows):
                raise ValueError("publication head changed during preparation; retry with a fresh diff")
            row = OperationsVersion(
                version_code=version.version_id, import_id=source.import_id, diff=encode_diff(version.diff)
            )
            session.add(row)
            session.flush()
            _event(session, "prepare", source.import_id, decision, version_id=row.version_id, after="draft")

    def replace_version(self, version: ServingDataVersion) -> None:
        with self._sessions() as session, session.begin():
            head = _head(session, lock=True)
            record = self._require(session, version.version_id)
            stored = _version(session, record, head)
            if (
                stored.state is not ServingVersionState.DRAFT
                or version.approval is None
                or version != replace(stored, state=ServingVersionState.APPROVED, approval=version.approval)
            ):
                raise ValueError("only immutable draft-to-approved transition is allowed")
            source = session.get(OperationsImport, record.import_id)
            if source is None or not _review(session, source).preparation.is_publishable_candidate:
                raise ValueError("approval requires a clean reviewed import")
            _event(
                session,
                "approve",
                record.import_id,
                version.approval,
                version_id=record.version_id,
                before="draft",
                after="approved",
            )

    def publish_atomically(
        self, approved_version: ServingDataVersion, *, decision: ApprovalRecord | None = None
    ) -> ServingDataVersion:
        if decision is None:
            raise ValueError("publication requires its own decision")
        with self._sessions() as session, session.begin():
            head = _head(session, lock=True)
            record = self._require(session, approved_version.version_id)
            stored = _version(session, record, head)
            if (
                stored != approved_version
                or stored.state is not ServingVersionState.APPROVED
                or stored.approval is None
            ):
                raise ValueError("publication target is stale or unapproved")
            _event(
                session,
                "publish",
                record.import_id,
                decision,
                version_id=record.version_id,
                before="approved",
                after="published",
                previous=head.version_id,
                current=record.version_id,
            )
            head.version_id = record.version_id
            return replace(stored, state=ServingVersionState.PUBLISHED)

    def rollback_atomically(
        self, target: ServingDataVersion, *, expected_current_version_id: str, decision: ApprovalRecord
    ) -> ServingDataVersion:
        with self._sessions() as session, session.begin():
            head = _head(session, lock=True)
            current = None if head.version_id is None else session.get(OperationsVersion, head.version_id)
            if current is None or current.version_code != expected_current_version_id:
                raise ValueError("rollback current version is stale")
            record = self._require(session, target.version_id)
            stored = _version(session, record, head)
            if stored != target or stored.state is not ServingVersionState.SUPERSEDED or stored.approval is None:
                raise ValueError("rollback requires the unchanged approved historical version")
            _event(
                session,
                "rollback",
                record.import_id,
                decision,
                version_id=record.version_id,
                before="superseded",
                after="published",
                previous=head.version_id,
                current=record.version_id,
            )
            head.version_id = record.version_id
            return replace(stored, state=ServingVersionState.PUBLISHED)

    @staticmethod
    def _require(session: Session, version_id: str) -> OperationsVersion:
        record = session.scalar(select(OperationsVersion).where(OperationsVersion.version_code == version_id))
        if record is None:
            raise LookupError("serving version was not found")
        return record
