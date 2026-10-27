"""Allow an explicit new questionnaire answer to supersede prior progress.

Revision ID: d8c4a2f1b607
Revises: a17d9c4e6b20
"""

from alembic import op
import sqlalchemy as sa

revision = "d8c4a2f1b607"
down_revision = "a17d9c4e6b20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Preserve expired_at and raw answers; the existing retention job remains the
    # sole owner of their eventual purge. This timestamp only revokes access.
    op.add_column("questionnaire_sessions", sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("questionnaire_sessions", "superseded_at")
