"""Bounded, atomic raw-answer purge, independent of durable result snapshots.

The caller supplies a dedicated Session without pending writes. Each invocation
owns one transaction. No account locks, history writes or reference seeding.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import delete, exists, func, or_, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import (
    QuestionnaireAnswer,
    QuestionnaireSession,
    QuestionnaireSessionState,
    RecommendationHistoryRun,
)

DEFAULT_BATCH_SIZE = 100
MAX_BATCH_SIZE = 1000


@dataclass(frozen=True)
class PurgeBatch:
    processed_sessions: int = 0
    deleted_answers: int = 0
    deleted_sessions: int = 0
    retained_sessions: int = 0
    # Internal cache invalidation only; never include identifiers in public counts.
    session_ids: tuple[str, ...] = field(default=(), repr=False)

    def counts(self) -> dict[str, int]:
        return {
            "processed_sessions": self.processed_sessions,
            "deleted_answers": self.deleted_answers,
            "deleted_sessions": self.deleted_sessions,
            "retained_sessions": self.retained_sessions,
        }


def validate_batch_size(batch_size: int) -> None:
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or not 1 <= batch_size <= MAX_BATCH_SIZE:
        raise ValueError("batch_size must be between 1 and 1000")


def _eligible(cutoff: datetime):
    has_answers = exists().where(
        QuestionnaireAnswer.questionnaire_session_id == QuestionnaireSession.questionnaire_session_id
    )
    has_history = exists().where(
        RecommendationHistoryRun.questionnaire_session_id == QuestionnaireSession.questionnaire_session_id
    )
    return (
        QuestionnaireSession.expires_at <= cutoff,
        or_(has_answers, ~has_history, QuestionnaireSession.state != QuestionnaireSessionState.EXPIRED),
    )


def database_cutoff(db: Session) -> datetime:
    """Read database time, not CLI/user clock; SQLite is a local contract fixture."""
    value = db.scalar(select(func.clock_timestamp() if db.get_bind().dialect.name == "postgresql" else func.now()))
    if not isinstance(value, datetime):
        raise RuntimeError("database clock is unavailable")
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def pending_counts(db: Session) -> dict[str, int]:
    """Read-only aggregate preflight; does not instantiate the seeding repository."""
    cutoff = database_cutoff(db)
    sessions = db.scalar(select(func.count()).select_from(QuestionnaireSession).where(*_eligible(cutoff)))
    answers = db.scalar(
        select(func.count())
        .select_from(QuestionnaireAnswer)
        .join(QuestionnaireSession)
        .where(QuestionnaireSession.expires_at <= cutoff)
    )
    return {"pending_sessions": int(sessions or 0), "pending_answers": int(answers or 0)}


def purge_expired_batch(
    db: Session, *, batch_size: int = DEFAULT_BATCH_SIZE, now: datetime | None = None
) -> PurgeBatch:
    """Delete expired answers, keep linked evidence, remove unlinked metadata.

    A linked EXPIRED row without answers is complete and excluded on retry.
    SKIP LOCKED lets concurrent workers avoid both account/session lock inversion
    and long request waits. Empty work does not prove the entire backlog drained:
    another connection may hold expired rows; use pending_counts afterwards.
    """
    validate_batch_size(batch_size)
    if now is not None and (now.tzinfo is None or now.utcoffset() is None):
        raise ValueError("cutoff must be timezone-aware")
    if db.new or db.dirty or db.deleted:
        raise ValueError("purge requires a Session without pending writes")
    try:
        cutoff = now or database_cutoff(db)
        identifiers = tuple(
            db.scalars(
                select(QuestionnaireSession.questionnaire_session_id)
                .where(*_eligible(cutoff))
                .order_by(QuestionnaireSession.expires_at, QuestionnaireSession.questionnaire_session_id)
                .limit(batch_size)
                .with_for_update(skip_locked=True)
            )
        )
        if not identifiers:
            db.commit()
            return PurgeBatch()
        linked = set(
            db.scalars(
                select(RecommendationHistoryRun.questionnaire_session_id).where(
                    RecommendationHistoryRun.questionnaire_session_id.in_(identifiers)
                )
            )
        )
        deleted = db.execute(
            delete(QuestionnaireAnswer).where(QuestionnaireAnswer.questionnaire_session_id.in_(identifiers))
        )
        assert isinstance(deleted, CursorResult)
        if linked:
            db.execute(
                update(QuestionnaireSession)
                .where(QuestionnaireSession.questionnaire_session_id.in_(linked))
                .values(state=QuestionnaireSessionState.EXPIRED)
            )
        unlinked = set(identifiers) - linked
        if unlinked:
            db.execute(delete(QuestionnaireSession).where(QuestionnaireSession.questionnaire_session_id.in_(unlinked)))
        result = PurgeBatch(
            len(identifiers), deleted.rowcount, len(unlinked), len(linked), tuple(map(str, identifiers))
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
