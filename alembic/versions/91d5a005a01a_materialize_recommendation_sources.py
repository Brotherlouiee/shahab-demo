"""Persist versioned source categories, conditions and approved config evidence.

Revision ID: 91d5a005a01a
Revises: 7b3f2f4a9c10
"""

import sqlalchemy as sa

from alembic import op

revision = "91d5a005a01a"
down_revision = "7b3f2f4a9c10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("loan_product_versions", sa.Column("source_row_number", sa.Integer(), nullable=True))
    op.create_unique_constraint(
        "uq_loan_version_source_row", "loan_product_versions", ["source_file_id", "source_row_number"]
    )
    op.create_table(
        "loan_category_assignments",
        sa.Column("loan_product_version_id", sa.Uuid(), nullable=False),
        sa.Column("loan_variable_id", sa.Uuid(), nullable=False),
        sa.Column("variable_category_id", sa.Uuid(), nullable=True),
        sa.Column("classification_state", sa.String(20), nullable=False),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["loan_product_version_id"], ["loan_product_versions.loan_product_version_id"]),
        sa.ForeignKeyConstraint(["loan_variable_id"], ["loan_variables.loan_variable_id"]),
        sa.ForeignKeyConstraint(["variable_category_id"], ["variable_categories.variable_category_id"]),
        sa.CheckConstraint("source_row_number > 0", name="ck_assignment_source_row_positive"),
        sa.CheckConstraint(
            "classification_state IN ('classified','unknown','variable','unparseable','unmapped')",
            name="ck_assignment_state",
        ),
        sa.CheckConstraint(
            "(classification_state = 'classified') = (variable_category_id IS NOT NULL)",
            name="ck_assignment_category_state",
        ),
        sa.PrimaryKeyConstraint("loan_product_version_id", "loan_variable_id"),
    )
    op.create_table(
        "loan_conditions",
        sa.Column("loan_product_version_id", sa.Uuid(), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["loan_product_version_id"], ["loan_product_versions.loan_product_version_id"]),
        sa.PrimaryKeyConstraint("loan_product_version_id"),
    )
    op.create_table(
        "answer_option_weights",
        sa.Column("config_version_id", sa.Uuid(), nullable=False),
        sa.Column("answer_option_id", sa.Uuid(), nullable=False),
        sa.Column("loan_variable_id", sa.Uuid(), nullable=False),
        sa.Column("weighted_value", sa.Numeric(8, 6), nullable=False),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["config_version_id"], ["recommendation_config_versions.config_version_id"]),
        sa.ForeignKeyConstraint(["answer_option_id"], ["answer_options.answer_option_id"]),
        sa.ForeignKeyConstraint(["loan_variable_id"], ["loan_variables.loan_variable_id"]),
        sa.CheckConstraint("weighted_value >= 0 AND weighted_value <= 1", name="ck_answer_weight_range"),
        sa.PrimaryKeyConstraint("config_version_id", "answer_option_id", "loan_variable_id"),
    )
    op.create_table(
        "answer_category_compatibilities",
        sa.Column("config_version_id", sa.Uuid(), nullable=False),
        sa.Column("answer_option_id", sa.Uuid(), nullable=False),
        sa.Column("variable_category_id", sa.Uuid(), nullable=False),
        sa.Column("coefficient", sa.Numeric(8, 6), nullable=False),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
        sa.Column("source_column_number", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["config_version_id"], ["recommendation_config_versions.config_version_id"]),
        sa.ForeignKeyConstraint(["answer_option_id"], ["answer_options.answer_option_id"]),
        sa.ForeignKeyConstraint(["variable_category_id"], ["variable_categories.variable_category_id"]),
        sa.CheckConstraint("coefficient >= 0 AND coefficient <= 1", name="ck_compatibility_range"),
        sa.PrimaryKeyConstraint("config_version_id", "answer_option_id", "variable_category_id"),
    )
    op.create_table(
        "serving_catalogue_versions",
        sa.Column("serving_catalogue_version_id", sa.Uuid(), nullable=False),
        sa.Column("version_code", sa.String(100), nullable=False),
        sa.Column("data_source_file_id", sa.Uuid(), nullable=False),
        sa.Column("config_version_id", sa.Uuid(), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("approved_by_reference", sa.String(255), nullable=False),
        sa.Column("approval_reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["data_source_file_id"], ["data_source_files.data_source_file_id"]),
        sa.ForeignKeyConstraint(["config_version_id"], ["recommendation_config_versions.config_version_id"]),
        sa.CheckConstraint("state IN ('published','superseded')", name="ck_serving_catalogue_state"),
        sa.CheckConstraint("active = (state = 'published')", name="ck_serving_catalogue_active_state"),
        sa.PrimaryKeyConstraint("serving_catalogue_version_id"),
        sa.UniqueConstraint("version_code", name="uq_serving_catalogue_version_code"),
    )
    op.create_index(
        "uq_one_active_serving_catalogue",
        "serving_catalogue_versions",
        ["active"],
        unique=True,
        postgresql_where=sa.text("active"),
    )
    op.create_table(
        "serving_catalogue_members",
        sa.Column("serving_catalogue_version_id", sa.Uuid(), nullable=False),
        sa.Column("loan_product_version_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["serving_catalogue_version_id"], ["serving_catalogue_versions.serving_catalogue_version_id"]
        ),
        sa.ForeignKeyConstraint(["loan_product_version_id"], ["loan_product_versions.loan_product_version_id"]),
        sa.PrimaryKeyConstraint("serving_catalogue_version_id", "loan_product_version_id"),
    )


def downgrade() -> None:
    op.drop_table("serving_catalogue_members")
    op.drop_index("uq_one_active_serving_catalogue", table_name="serving_catalogue_versions")
    op.drop_table("serving_catalogue_versions")
    op.drop_table("answer_category_compatibilities")
    op.drop_table("answer_option_weights")
    op.drop_table("loan_conditions")
    op.drop_table("loan_category_assignments")
    op.drop_constraint("uq_loan_version_source_row", "loan_product_versions", type_="unique")
    op.drop_column("loan_product_versions", "source_row_number")
