"""Persist editable local user profiles.

Revision ID: d1a9e71b4c3f
Revises: e8a5c7d2f4b1
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d1a9e71b4c3f"
down_revision = "e8a5c7d2f4b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("phone", sa.String(length=11), primary_key=True),
        sa.Column("first_name", sa.String(length=60), nullable=False, server_default=""),
        sa.Column("last_name", sa.String(length=60), nullable=False, server_default=""),
        sa.Column("income", sa.String(length=40), nullable=False, server_default=""),
        sa.Column("job", sa.String(length=40), nullable=False, server_default=""),
        sa.Column("gender", sa.String(length=10), nullable=False, server_default=""),
        sa.Column("avatar_data_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_profiles")
