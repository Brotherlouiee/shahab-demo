"""Persist immutable account-owned recommendation history.

Revision ID: e4c7b9a1d2f3
Revises: d1a9e71b4c3f
"""

import sqlalchemy as sa
from alembic import op

revision = "e4c7b9a1d2f3"
down_revision = "d1a9e71b4c3f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recommendation_history_runs",
        sa.Column("recommendation_history_run_id", sa.Uuid(), primary_key=True),
        sa.Column("owner_phone", sa.String(11), sa.ForeignKey("user_profiles.phone"), nullable=False),
        sa.Column(
            "questionnaire_session_id",
            sa.Uuid(),
            sa.ForeignKey("questionnaire_sessions.questionnaire_session_id"),
            nullable=False,
        ),
        sa.Column("data_version", sa.String(100), nullable=False),
        sa.Column("config_version", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("questionnaire_session_id", name="uq_recommendation_history_session"),
    )
    op.create_index(
        "ix_recommendation_history_owner_created",
        "recommendation_history_runs",
        ["owner_phone", "created_at", "recommendation_history_run_id"],
    )
    op.create_table(
        "recommendation_history_items",
        sa.Column("recommendation_history_item_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "recommendation_history_run_id",
            sa.Uuid(),
            sa.ForeignKey("recommendation_history_runs.recommendation_history_run_id"),
            nullable=False,
        ),
        sa.Column("section", sa.String(30), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column(
            "loan_product_version_id",
            sa.Uuid(),
            sa.ForeignKey("loan_product_versions.loan_product_version_id"),
            nullable=False,
        ),
        sa.Column("lender_name", sa.String(255), nullable=False),
        sa.Column("loan_name", sa.String(255), nullable=False),
        sa.Column("bank_logo_reference", sa.String(512)),
        sa.Column("compatibility_score", sa.Float()),
        sa.Column("compatibility_reason", sa.Text()),
        sa.Column("max_amount_tomans", sa.Numeric(18, 2)),
        sa.Column("monthly_installment_tomans", sa.Numeric(18, 2)),
        sa.Column("max_repayment_months", sa.Integer()),
        sa.Column("interest_rate_percent", sa.Numeric(8, 4)),
        sa.CheckConstraint("section IN ('ranked', 'low', 'review')", name="ck_history_item_section"),
        sa.CheckConstraint("display_order >= 0", name="ck_history_item_display_order"),
        sa.UniqueConstraint("recommendation_history_run_id", "section", "display_order", name="uq_history_item_order"),
    )
    op.create_table(
        "recommendation_history_item_reasons",
        sa.Column(
            "recommendation_history_item_id",
            sa.Uuid(),
            sa.ForeignKey("recommendation_history_items.recommendation_history_item_id"),
            primary_key=True,
        ),
        sa.Column("display_order", sa.Integer(), primary_key=True),
        sa.Column("reason", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("recommendation_history_item_reasons")
    op.drop_table("recommendation_history_items")
    op.drop_index("ix_recommendation_history_owner_created", table_name="recommendation_history_runs")
    op.drop_table("recommendation_history_runs")
