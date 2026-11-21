"""US-11.T02A.2: expand identity without removing legacy writer columns.

Revision ID: aa11b02a2001
Revises: b4d8e1f2a3c5
"""

import sqlalchemy as sa
from alembic import op

revision = "aa11b02a2001"
down_revision = "b4d8e1f2a3c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("account_id", sa.Uuid(), primary_key=True),
        sa.Column("phone", sa.String(11), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("phone ~ '^09[0-9]{9}$'", name="ck_account_phone"),
        sa.CheckConstraint("status IN ('active', 'archived')", name="ck_account_status"),
        sa.CheckConstraint("(status='active' AND archived_at IS NULL) OR "
                           "(status='archived' AND archived_at IS NOT NULL AND archived_at >= created_at)",
                           name="ck_account_archive_time"),
    )
    op.create_index("uq_account_active_phone", "accounts", ["phone"], unique=True,
                    postgresql_where=sa.text("status = 'active'"))
    op.add_column("user_profiles", sa.Column("account_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_profile_account", "user_profiles", "accounts", ["account_id"], ["account_id"], ondelete="RESTRICT")
    op.create_unique_constraint("uq_profile_account", "user_profiles", ["account_id"])
    for table in ("questionnaire_sessions", "recommendation_history_runs"):
        op.add_column(table, sa.Column("owner_account_id", sa.Uuid(), nullable=True))
        op.create_foreign_key("fk_" + table + "_account", table, "accounts", ["owner_account_id"], ["account_id"], ondelete="RESTRICT")


def downgrade() -> None:
    # Only safe before contract/generations. Contract downgrade restores the
    # legacy columns and mapping first; never erase an unrepresented generation.
    connection = op.get_bind()
    if connection.scalar(sa.text("SELECT count(*) FROM accounts a LEFT JOIN user_profiles p "
                                  "ON p.account_id=a.account_id WHERE p.phone IS NULL OR p.phone <> a.phone")):
        raise RuntimeError("Account expand downgrade refused: unmapped retained account.")
    for table in ("recommendation_history_runs", "questionnaire_sessions"):
        op.drop_constraint("fk_" + table + "_account", table, type_="foreignkey")
        op.drop_column(table, "owner_account_id")
    op.drop_constraint("uq_profile_account", "user_profiles", type_="unique")
    op.drop_constraint("fk_profile_account", "user_profiles", type_="foreignkey")
    op.drop_column("user_profiles", "account_id")
    op.drop_table("accounts")
