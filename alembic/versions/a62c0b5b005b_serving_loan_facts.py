"""Add approved loan-version detail facts for the serving read adapter.

Revision ID: a62c0b5b005b
Revises: 91d5a005a01a
"""

import sqlalchemy as sa

from alembic import op

revision = "a62c0b5b005b"
down_revision = "91d5a005a01a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "loan_serving_facts",
        sa.Column("loan_product_version_id", sa.Uuid(), nullable=False),
        sa.Column("deposit_required_text", sa.String(100)),
        sa.Column("deposit_holding_months", sa.Integer()),
        sa.Column("loan_to_deposit_ratio_percent", sa.Numeric(8, 4)),
        sa.Column("guarantee_type_text", sa.String(100)),
        sa.Column("required_deposit_account", sa.String(255)),
        sa.Column("bank_logo_reference", sa.String(512)),
        sa.CheckConstraint("deposit_holding_months >= 0", name="ck_serving_deposit_months_nonnegative"),
        sa.CheckConstraint("loan_to_deposit_ratio_percent >= 0", name="ck_serving_deposit_ratio_nonnegative"),
        sa.ForeignKeyConstraint(["loan_product_version_id"], ["loan_product_versions.loan_product_version_id"]),
        sa.PrimaryKeyConstraint("loan_product_version_id"),
    )


def downgrade() -> None:
    op.drop_table("loan_serving_facts")
