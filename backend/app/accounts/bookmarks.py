"""Owner-scoped bookmark persistence. No score calculation or catalogue copies.

API callers own the short transaction. Active-account locks precede association
locks, matching archive/logout ordering. PUT and DELETE express desired state,
so network retries do not invert a toggle or create duplicate records.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import case, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from backend.app.accounts.identity import AccountActor, require_active_account
from backend.app.infrastructure.db.models import (
    AccountBookmark,
    Lender,
    LoanProduct,
    LoanProductVersion,
    LoanServingFacts,
    LoanTerms,
    PublicationState,
    RecommendationHistoryItem,
    RecommendationHistoryRun,
)


class AccountBookmarkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, actor: AccountActor, loan_id: UUID, history_id: UUID | None = None) -> None:
        require_active_account(actor.account_id, self.db)
        version = self.db.scalar(
            select(LoanProductVersion.loan_product_version_id).where(
                LoanProductVersion.loan_product_version_id == loan_id,
                LoanProductVersion.publication_state == PublicationState.PUBLISHED,
            )
        )
        if version is None:
            raise LookupError("loan is unavailable")
        context = (
            select(RecommendationHistoryRun.recommendation_history_run_id)
            .join(
                RecommendationHistoryItem,
                RecommendationHistoryItem.recommendation_history_run_id
                == RecommendationHistoryRun.recommendation_history_run_id,
            )
            .where(
                RecommendationHistoryRun.owner_account_id == actor.account_id,
                RecommendationHistoryRun.hidden_at.is_(None),
                RecommendationHistoryItem.loan_product_version_id == loan_id,
            )
        )
        if history_id is not None:
            context = context.where(RecommendationHistoryRun.recommendation_history_run_id == history_id)
        source = self.db.scalar(
            context.order_by(
                RecommendationHistoryRun.created_at.desc(),
                RecommendationHistoryRun.recommendation_history_run_id.desc(),
            ).limit(1)
        )
        if history_id is not None and source is None:
            # Same response for another owner, missing, hidden or mismatched loan.
            raise LookupError("history context is unavailable")
        insert = pg_insert if self.db.get_bind().dialect.name == "postgresql" else sqlite_insert
        statement = insert(AccountBookmark).values(
            account_id=actor.account_id, loan_product_version_id=loan_id, source_history_run_id=source
        )
        self.db.execute(
            statement.on_conflict_do_update(
                index_elements=[AccountBookmark.account_id, AccountBookmark.loan_product_version_id],
                set_={
                    "removed_at": None,
                    "source_history_run_id": case(
                        (AccountBookmark.removed_at.is_not(None), source), else_=AccountBookmark.source_history_run_id
                    ),
                },
            )
        )

    def remove(self, actor: AccountActor, loan_id: UUID) -> None:
        require_active_account(actor.account_id, self.db)
        self.db.execute(
            update(AccountBookmark)
            .where(
                AccountBookmark.account_id == actor.account_id,
                AccountBookmark.loan_product_version_id == loan_id,
                AccountBookmark.removed_at.is_(None),
            )
            .values(removed_at=func.now())
        )

    def list_for_owner(self, actor: AccountActor, limit: int, cursor: tuple[datetime, UUID] | None = None):
        require_active_account(actor.account_id, self.db)
        # At most one deterministic item from the referenced original snapshot.
        # The loan facts are immutable version facts; absent historical context
        # has no invented personalized match percentage.
        context_id = (
            select(RecommendationHistoryItem.recommendation_history_item_id)
            .where(
                RecommendationHistoryItem.recommendation_history_run_id == AccountBookmark.source_history_run_id,
                RecommendationHistoryItem.loan_product_version_id == AccountBookmark.loan_product_version_id,
            )
            .order_by(RecommendationHistoryItem.display_order, RecommendationHistoryItem.recommendation_history_item_id)
            .limit(1)
            .correlate(AccountBookmark)
            .scalar_subquery()
        )
        statement = (
            select(AccountBookmark, LoanProduct, Lender, LoanTerms, LoanServingFacts, RecommendationHistoryItem)
            .join(
                LoanProductVersion,
                LoanProductVersion.loan_product_version_id == AccountBookmark.loan_product_version_id,
            )
            .join(LoanProduct, LoanProduct.loan_product_id == LoanProductVersion.loan_product_id)
            .join(Lender, Lender.lender_id == LoanProduct.lender_id)
            .outerjoin(LoanTerms, LoanTerms.loan_product_version_id == AccountBookmark.loan_product_version_id)
            .outerjoin(
                LoanServingFacts, LoanServingFacts.loan_product_version_id == AccountBookmark.loan_product_version_id
            )
            .outerjoin(
                RecommendationHistoryItem, RecommendationHistoryItem.recommendation_history_item_id == context_id
            )
            .where(
                AccountBookmark.account_id == actor.account_id,
                AccountBookmark.removed_at.is_(None),
            )
        )
        if cursor is not None:
            created, identifier = cursor
            statement = statement.where(
                or_(
                    AccountBookmark.created_at > created,
                    (AccountBookmark.created_at == created) & (AccountBookmark.loan_product_version_id > identifier),
                )
            )
        return self.db.execute(
            statement.order_by(AccountBookmark.created_at, AccountBookmark.loan_product_version_id).limit(limit + 1)
        ).all()
