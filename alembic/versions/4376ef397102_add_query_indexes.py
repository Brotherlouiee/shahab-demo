"""add query indexes

Revision ID: 4376ef397102
Revises: f0d0c68db55a
Create Date: 2026-09-19 09:05:09.494757
"""

from alembic import op

revision = "4376ef397102"
down_revision = "f0d0c68db55a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add only indexes justified by v1 catalogue, questionnaire and provenance query contracts."""
    op.create_index("ix_loan_products_lender_id", "loan_products", ["lender_id"])
    op.create_index("ix_loan_product_versions_loan_product_id", "loan_product_versions", ["loan_product_id"])
    op.create_index("ix_loan_product_versions_publication_state", "loan_product_versions", ["publication_state"])
    op.create_index("ix_data_source_files_data_import_run_id", "data_source_files", ["data_import_run_id"])
    op.create_index("ix_questions_version_display_order", "questions", ["questionnaire_version_id", "display_order"])
    op.create_index("ix_answer_options_question_id", "answer_options", ["question_id"])
    op.create_index("ix_variable_categories_loan_variable_id", "variable_categories", ["loan_variable_id"])


def downgrade() -> None:
    """Remove indexes in reverse dependency order; no application data is changed."""
    op.drop_index("ix_variable_categories_loan_variable_id", table_name="variable_categories")
    op.drop_index("ix_answer_options_question_id", table_name="answer_options")
    op.drop_index("ix_questions_version_display_order", table_name="questions")
    op.drop_index("ix_data_source_files_data_import_run_id", table_name="data_source_files")
    op.drop_index("ix_loan_product_versions_publication_state", table_name="loan_product_versions")
    op.drop_index("ix_loan_product_versions_loan_product_id", table_name="loan_product_versions")
    op.drop_index("ix_loan_products_lender_id", table_name="loan_products")
