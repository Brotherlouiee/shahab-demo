"""Retain recommendation-history snapshots when a user hides a card.

Revision ID: a3b7c9d1e2f4
Revises: f1a2b3c4d5e6
"""

from alembic import op
import sqlalchemy as sa

revision = "a3b7c9d1e2f4"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("recommendation_history_runs", sa.Column("hidden_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_recommendation_history_visible_owner_created", "recommendation_history_runs", ["owner_phone", "hidden_at", "created_at", "recommendation_history_run_id"])


def downgrade() -> None:
    op.drop_index("ix_recommendation_history_visible_owner_created", table_name="recommendation_history_runs")
    op.drop_column("recommendation_history_runs", "hidden_at")
