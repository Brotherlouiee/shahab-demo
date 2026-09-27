"""Persist controlled bank-logo asset references for published serving facts."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "c90f0d6e1a2b"
down_revision = "a62c0b5b005b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("loan_serving_facts", sa.Column("bank_logo_asset_key", sa.String(length=512), nullable=True))
    op.add_column("loan_serving_facts", sa.Column("bank_logo_asset_sha256", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("loan_serving_facts", "bank_logo_asset_sha256")
    op.drop_column("loan_serving_facts", "bank_logo_asset_key")
