"""Bind recommendation history writes to an account-owned questionnaire.

Revision ID: f1a2b3c4d5e6
Revises: e4c7b9a1d2f3
"""

from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "e4c7b9a1d2f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questionnaire_sessions", sa.Column("owner_phone", sa.String(length=11), nullable=True))
    op.create_foreign_key("fk_questionnaire_sessions_owner_phone", "questionnaire_sessions", "user_profiles", ["owner_phone"], ["phone"])
    op.create_index("ix_questionnaire_sessions_owner_phone", "questionnaire_sessions", ["owner_phone"])


def downgrade() -> None:
    op.drop_index("ix_questionnaire_sessions_owner_phone", table_name="questionnaire_sessions")
    op.drop_constraint("fk_questionnaire_sessions_owner_phone", "questionnaire_sessions", type_="foreignkey")
    op.drop_column("questionnaire_sessions", "owner_phone")
