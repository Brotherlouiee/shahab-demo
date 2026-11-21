"""Account-owned immutable recommendation-result history persistence."""

from __future__ import annotations

import uuid
from collections import defaultdict
from collections.abc import Sequence
from typing import Any, cast

from sqlalchemy import CursorResult, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.accounts.identity import AccountActor, require_active_account
from backend.app.infrastructure.db.models import (
    QuestionnaireSession,
    RecommendationHistoryItem,
    RecommendationHistoryItemReason,
    RecommendationHistoryRun,
)


class RecommendationHistoryRepository:
    """Persist one complete immutable snapshot for each questionnaire session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self, actor: AccountActor, questionnaire_session_id: str, result: Any, *, authorized_proof_digest: str
    ) -> RecommendationHistoryRun:
        """Save a complete run, or return its existing owner-scoped idempotent result."""
        require_active_account(actor.account_id, self._session)
        session_id = uuid.UUID(questionnaire_session_id)
        # Bind the completed anonymous questionnaire to the authenticated actor
        # atomically. Subsequent accounts cannot claim or persist its snapshot.
        claim_result = cast(
            CursorResult[object],
            self._session.execute(
                update(QuestionnaireSession)
                .where(QuestionnaireSession.questionnaire_session_id == session_id)
                .where(
                    or_(
                        QuestionnaireSession.owner_account_id.is_(None),
                        QuestionnaireSession.owner_account_id == actor.account_id,
                    )
                )
                .where(QuestionnaireSession.creator_proof_digest == authorized_proof_digest)
                .where(QuestionnaireSession.expires_at > func.now())
                .values(owner_account_id=actor.account_id)
            ),
        )
        claimed = claim_result.rowcount
        if claimed != 1:
            raise PermissionError("questionnaire session belongs to another account")
        existing = self._existing(session_id)
        if existing is not None:
            return self._owned(existing, actor)

        try:
            with self._session.begin_nested():
                run = RecommendationHistoryRun(
                    owner_account_id=actor.account_id,
                    questionnaire_session_id=session_id,
                    data_version=result.data_version,
                    config_version=result.config_version,
                )
                self._session.add(run)
                self._session.flush()
                self._add_items(run, result)
            return run
        except IntegrityError:
            # A concurrent request may have inserted the same session. The nested
            # transaction rolls back without discarding the request transaction.
            existing = self._existing(session_id)
            if existing is None:
                raise
            return self._owned(existing, actor)

    def list_for_owner(
        self, actor: AccountActor, limit: int, cursor: tuple[object, uuid.UUID] | None = None
    ) -> Sequence[tuple[RecommendationHistoryRun, int]]:
        require_active_account(actor.account_id, self._session)
        ranked_count = (
            select(func.count(RecommendationHistoryItem.recommendation_history_item_id))
            .where(
                RecommendationHistoryItem.recommendation_history_run_id
                == RecommendationHistoryRun.recommendation_history_run_id,
                RecommendationHistoryItem.section == "ranked",
            )
            .correlate(RecommendationHistoryRun)
            .scalar_subquery()
        )
        statement = select(RecommendationHistoryRun, ranked_count.label("ranked_count")).where(
            RecommendationHistoryRun.owner_account_id == actor.account_id,
            RecommendationHistoryRun.hidden_at.is_(None),
        )
        if cursor is not None:
            created_at, run_id = cursor
            statement = statement.where(
                or_(
                    RecommendationHistoryRun.created_at < created_at,
                    (RecommendationHistoryRun.created_at == created_at)
                    & (RecommendationHistoryRun.recommendation_history_run_id < run_id),
                )
            )
        return self._session.execute(
            statement.order_by(
                RecommendationHistoryRun.created_at.desc(),
                RecommendationHistoryRun.recommendation_history_run_id.desc(),
            ).limit(limit)
        ).all()

    def read_for_owner(
        self, actor: AccountActor, run_id: str
    ) -> tuple[RecommendationHistoryRun, Sequence[RecommendationHistoryItem], dict[uuid.UUID, tuple[str, ...]]]:
        require_active_account(actor.account_id, self._session)
        run = self._session.scalar(
            select(RecommendationHistoryRun).where(
                RecommendationHistoryRun.recommendation_history_run_id == uuid.UUID(run_id),
                RecommendationHistoryRun.owner_account_id == actor.account_id,
                RecommendationHistoryRun.hidden_at.is_(None),
            )
        )
        if run is None:
            raise LookupError("history entry was not found")
        items = self._session.scalars(
            select(RecommendationHistoryItem)
            .where(RecommendationHistoryItem.recommendation_history_run_id == run.recommendation_history_run_id)
            .order_by(RecommendationHistoryItem.section, RecommendationHistoryItem.display_order)
        ).all()
        reasons: dict[uuid.UUID, list[str]] = defaultdict(list)
        if items:
            for item_id, reason in self._session.execute(
                select(
                    RecommendationHistoryItemReason.recommendation_history_item_id,
                    RecommendationHistoryItemReason.reason,
                )
                .where(
                    RecommendationHistoryItemReason.recommendation_history_item_id.in_(
                        [item.recommendation_history_item_id for item in items]
                    )
                )
                .order_by(
                    RecommendationHistoryItemReason.recommendation_history_item_id,
                    RecommendationHistoryItemReason.display_order,
                )
            ):
                reasons[item_id].append(reason)
        return run, items, {item_id: tuple(values) for item_id, values in reasons.items()}

    def hide_for_owner(self, actor: AccountActor, run_id: str) -> bool:
        """Hide an owned run without deleting its immutable database snapshot."""
        require_active_account(actor.account_id, self._session)
        result = cast(
            CursorResult[object],
            self._session.execute(
                update(RecommendationHistoryRun)
                .where(RecommendationHistoryRun.recommendation_history_run_id == uuid.UUID(run_id))
                .where(RecommendationHistoryRun.owner_account_id == actor.account_id)
                .where(RecommendationHistoryRun.hidden_at.is_(None))
                .values(hidden_at=func.now())
            ),
        )
        return result.rowcount == 1

    def _existing(self, session_id: uuid.UUID) -> RecommendationHistoryRun | None:
        return self._session.scalar(
            select(RecommendationHistoryRun).where(RecommendationHistoryRun.questionnaire_session_id == session_id)
        )

    @staticmethod
    def _owned(run: RecommendationHistoryRun, actor: AccountActor) -> RecommendationHistoryRun:
        if run.owner_account_id != actor.account_id:
            raise PermissionError("recommendation session belongs to another account")
        return run

    def _add_items(self, run: RecommendationHistoryRun, result: Any) -> None:
        for section, items in (
            ("ranked", result.ranked_recommendations),
            ("low", result.low_compatibility_recommendations),
            ("review", result.needs_review),
        ):
            for position, item in enumerate(items):
                summary = item.loan_summary
                stored = RecommendationHistoryItem(
                    recommendation_history_run_id=run.recommendation_history_run_id,
                    section=section,
                    display_order=position,
                    loan_product_version_id=uuid.UUID(item.loan_id),
                    lender_name=item.lender_name,
                    loan_name=item.loan_name,
                    bank_logo_reference=item.bank_logo_reference,
                    compatibility_score=getattr(item, "compatibility_score", None),
                    compatibility_reason=getattr(item, "compatibility_reason", None),
                    max_amount_tomans=summary.max_amount_tomans,
                    monthly_installment_tomans=summary.monthly_installment_tomans,
                    max_repayment_months=summary.max_repayment_months,
                    interest_rate_percent=summary.interest_rate_percent,
                )
                self._session.add(stored)
                self._session.flush()
                for reason_position, reason in enumerate(getattr(item, "ranking_excluded_reasons", ())):
                    self._session.add(
                        RecommendationHistoryItemReason(
                            recommendation_history_item_id=stored.recommendation_history_item_id,
                            display_order=reason_position,
                            reason=reason,
                        )
                    )
