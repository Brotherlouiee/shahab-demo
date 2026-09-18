"""3NF SQLAlchemy declarations mirroring the reviewed physical-schema contract.

No session or engine is created here: migrations own DDL and application code depends on
ports. Explicit state columns keep unknown/variable data from becoming ambiguous NULLs.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Single metadata root used by Alembic in US-04.T04."""


class ClassificationState(enum.StrEnum):
    CLASSIFIED = "classified"
    UNKNOWN = "unknown"
    VARIABLE = "variable"
    NEUTRAL = "neutral"


class PublicationState(enum.StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    PUBLISHED = "published"
    RETIRED = "retired"


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Lender(Timestamped, Base):
    __tablename__ = "lenders"
    __table_args__ = (UniqueConstraint("canonical_name", name="uq_lenders_canonical_name"),)
    lender_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_code: Mapped[str | None] = mapped_column(String(100), unique=True)


class LoanProduct(Timestamped, Base):
    __tablename__ = "loan_products"
    __table_args__ = (UniqueConstraint("lender_id", "canonical_name", name="uq_loan_product_lender_name"),)
    loan_product_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    lender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lenders.lender_id"), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)


class LoanProductVersion(Timestamped, Base):
    __tablename__ = "loan_product_versions"
    __table_args__ = (
        UniqueConstraint("loan_product_id", "version_number", name="uq_loan_product_version"),
        CheckConstraint("version_number > 0", name="ck_loan_version_positive"),
    )
    loan_product_version_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    loan_product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("loan_products.loan_product_id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    publication_state: Mapped[PublicationState] = mapped_column(nullable=False, default=PublicationState.DRAFT)
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("data_source_files.data_source_file_id"))


class LoanTerms(Base):
    __tablename__ = "loan_terms"
    __table_args__ = (
        CheckConstraint("max_amount >= 0 OR max_amount IS NULL", name="ck_terms_max_amount_nonnegative"),
        CheckConstraint(
            "monthly_installment >= 0 OR monthly_installment IS NULL", name="ck_terms_installment_nonnegative"
        ),
        CheckConstraint("interest_rate >= 0 OR interest_rate IS NULL", name="ck_terms_interest_nonnegative"),
    )
    loan_terms_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    loan_product_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("loan_product_versions.loan_product_version_id"), unique=True, nullable=False
    )
    max_amount: Mapped[float | None] = mapped_column(Numeric(18, 2))
    monthly_installment: Mapped[float | None] = mapped_column(Numeric(18, 2))
    max_repayment_months: Mapped[int | None] = mapped_column(Integer)
    interest_rate: Mapped[float | None] = mapped_column(Numeric(8, 4))
    max_amount_state: Mapped[ClassificationState] = mapped_column(nullable=False)
    monthly_installment_state: Mapped[ClassificationState] = mapped_column(nullable=False)
    max_repayment_months_state: Mapped[ClassificationState] = mapped_column(nullable=False)
    interest_rate_state: Mapped[ClassificationState] = mapped_column(nullable=False)


class LoanVariable(Base):
    __tablename__ = "loan_variables"
    loan_variable_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    canonical_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)


class VariableCategory(Base):
    __tablename__ = "variable_categories"
    __table_args__ = (UniqueConstraint("loan_variable_id", "canonical_id", name="uq_variable_category"),)
    variable_category_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    loan_variable_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("loan_variables.loan_variable_id"), nullable=False)
    canonical_id: Mapped[str] = mapped_column(String(100), nullable=False)


class QuestionnaireVersion(Timestamped, Base):
    __tablename__ = "questionnaire_versions"
    questionnaire_version_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    version_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint("questionnaire_version_id", "canonical_id", name="uq_question_version_canonical"),
    )
    question_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    questionnaire_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questionnaire_versions.questionnaire_version_id"), nullable=False
    )
    canonical_id: Mapped[str] = mapped_column(String(100), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AnswerOption(Base):
    __tablename__ = "answer_options"
    __table_args__ = (UniqueConstraint("question_id", "canonical_id", name="uq_answer_question_canonical"),)
    answer_option_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.question_id"), nullable=False)
    canonical_id: Mapped[str] = mapped_column(String(100), nullable=False)


class RecommendationConfigVersion(Timestamped, Base):
    __tablename__ = "recommendation_config_versions"
    config_version_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    version_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    decision_id: Mapped[str | None] = mapped_column(String(100))


class QuestionVariableWeight(Base):
    __tablename__ = "question_variable_weights"
    __table_args__ = (
        UniqueConstraint("config_version_id", "question_id", "loan_variable_id", name="uq_question_variable_weight"),
        CheckConstraint("weight >= 0 AND weight <= 1", name="ck_weight_range"),
    )
    question_variable_weight_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    config_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recommendation_config_versions.config_version_id"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.question_id"), nullable=False)
    loan_variable_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("loan_variables.loan_variable_id"), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)


class DataImportRun(Timestamped, Base):
    __tablename__ = "data_import_runs"
    data_import_run_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    state: Mapped[str] = mapped_column(String(30), nullable=False)
    parser_version: Mapped[str] = mapped_column(String(100), nullable=False)


class DataSourceFile(Timestamped, Base):
    __tablename__ = "data_source_files"
    data_source_file_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    data_import_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("data_import_runs.data_import_run_id"), nullable=False
    )
    sha256: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
