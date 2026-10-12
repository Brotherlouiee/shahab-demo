"""3NF SQLAlchemy declarations mirroring the reviewed physical-schema contract.

No session or engine is created here: migrations own DDL and application code depends on
ports. Explicit state columns keep unknown/variable data from becoming ambiguous NULLs.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
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


class QuestionnaireSessionState(enum.StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"


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
        UniqueConstraint("source_file_id", "source_row_number", name="uq_loan_version_source_row"),
        CheckConstraint("version_number > 0", name="ck_loan_version_positive"),
    )
    loan_product_version_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    loan_product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("loan_products.loan_product_id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    publication_state: Mapped[PublicationState] = mapped_column(nullable=False, default=PublicationState.DRAFT)
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("data_source_files.data_source_file_id"))
    source_row_number: Mapped[int | None] = mapped_column(Integer)


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


class LoanCategoryAssignment(Base):
    """One source-backed classification for every variable on one loan version."""

    __tablename__ = "loan_category_assignments"
    __table_args__ = (
        CheckConstraint("source_row_number > 0", name="ck_assignment_source_row_positive"),
        CheckConstraint(
            "classification_state IN ('classified','unknown','variable','unparseable','unmapped')",
            name="ck_assignment_state",
        ),
        CheckConstraint(
            "(classification_state = 'classified') = (variable_category_id IS NOT NULL)",
            name="ck_assignment_category_state",
        ),
    )
    loan_product_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("loan_product_versions.loan_product_version_id"), primary_key=True
    )
    loan_variable_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("loan_variables.loan_variable_id"), primary_key=True)
    variable_category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("variable_categories.variable_category_id")
    )
    classification_state: Mapped[str] = mapped_column(String(20), nullable=False)
    source_row_number: Mapped[int] = mapped_column(Integer, nullable=False)


class LoanConditions(Base):
    """Exact approved plain-text source conditions for one immutable loan version."""

    __tablename__ = "loan_conditions"
    loan_product_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("loan_product_versions.loan_product_version_id"), primary_key=True
    )
    source_text: Mapped[str] = mapped_column(Text, nullable=False)


class LoanServingFacts(Base):
    """Approved detail facts belonging to exactly one immutable loan version."""

    __tablename__ = "loan_serving_facts"
    __table_args__ = (
        CheckConstraint("deposit_holding_months >= 0", name="ck_serving_deposit_months_nonnegative"),
        CheckConstraint("loan_to_deposit_ratio_percent >= 0", name="ck_serving_deposit_ratio_nonnegative"),
    )
    loan_product_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("loan_product_versions.loan_product_version_id"), primary_key=True
    )
    deposit_required_text: Mapped[str | None] = mapped_column(String(100))
    deposit_holding_months: Mapped[int | None] = mapped_column(Integer)
    loan_to_deposit_ratio_percent: Mapped[float | None] = mapped_column(Numeric(8, 4))
    guarantee_type_text: Mapped[str | None] = mapped_column(String(100))
    required_deposit_account: Mapped[str | None] = mapped_column(String(255))
    bank_logo_reference: Mapped[str | None] = mapped_column(String(512))
    bank_logo_asset_key: Mapped[str | None] = mapped_column(String(512))
    bank_logo_asset_sha256: Mapped[str | None] = mapped_column(String(64))


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
    __table_args__ = (
        UniqueConstraint("question_id", "canonical_id", name="uq_answer_question_canonical"),
        UniqueConstraint("question_id", "answer_option_id", name="uq_answer_option_question_id"),
    )
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


class AnswerOptionWeight(Base):
    """The authoritative weighted answer cell from D-005, without reweighting."""

    __tablename__ = "answer_option_weights"
    config_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recommendation_config_versions.config_version_id"), primary_key=True
    )
    answer_option_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("answer_options.answer_option_id"), primary_key=True)
    loan_variable_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("loan_variables.loan_variable_id"), primary_key=True)
    weighted_value: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    source_row_number: Mapped[int] = mapped_column(Integer, nullable=False)


class AnswerCategoryCompatibility(Base):
    """One cell from the separate one-to-one compatibility matrix."""

    __tablename__ = "answer_category_compatibilities"
    config_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recommendation_config_versions.config_version_id"), primary_key=True
    )
    answer_option_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("answer_options.answer_option_id"), primary_key=True)
    variable_category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("variable_categories.variable_category_id"), primary_key=True
    )
    coefficient: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    source_row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    source_column_number: Mapped[int] = mapped_column(Integer, nullable=False)


class ServingCatalogueVersion(Timestamped, Base):
    """Immutable catalogue publication with one active PostgreSQL pointer."""

    __tablename__ = "serving_catalogue_versions"
    __table_args__ = (
        UniqueConstraint("version_code", name="uq_serving_catalogue_version_code"),
        CheckConstraint("state IN ('published','superseded')", name="ck_serving_catalogue_state"),
        CheckConstraint("active = (state = 'published')", name="ck_serving_catalogue_active_state"),
    )
    serving_catalogue_version_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    version_code: Mapped[str] = mapped_column(String(100), nullable=False)
    data_source_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("data_source_files.data_source_file_id"), nullable=False
    )
    config_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recommendation_config_versions.config_version_id"), nullable=False
    )
    state: Mapped[str] = mapped_column(String(20), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    approved_by_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    approval_reason: Mapped[str] = mapped_column(Text, nullable=False)


class ServingCatalogueMember(Base):
    __tablename__ = "serving_catalogue_members"
    serving_catalogue_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("serving_catalogue_versions.serving_catalogue_version_id"), primary_key=True
    )
    loan_product_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("loan_product_versions.loan_product_version_id"), primary_key=True
    )


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


class Account(Timestamped, Base):
    """One immutable account generation; phone is a login identifier, never its identity."""

    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'archived')", name="ck_account_status"),
        CheckConstraint(
            "(status = 'active' AND archived_at IS NULL) OR "
            "(status = 'archived' AND archived_at IS NOT NULL AND archived_at >= created_at)",
            name="ck_account_archive_time",
        ),
        CheckConstraint(
            "length(phone) = 11 AND phone LIKE '09%' AND "
            "replace(replace(replace(replace(replace(replace(replace(replace(replace(replace("
            "phone,'0',''),'1',''),'2',''),'3',''),'4',''),'5',''),'6',''),'7',''),'8',''),'9','') = ''",
            name="ck_account_phone",
        ),
        Index(
            "uq_account_active_phone",
            "phone",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String(11), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active", server_default="active")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserProfile(Timestamped, Base):
    """Editable facts belong to one account; public phone is joined from accounts."""

    __tablename__ = "user_profiles"
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.account_id", ondelete="RESTRICT"), primary_key=True
    )
    first_name: Mapped[str] = mapped_column(String(60), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(60), nullable=False, default="")
    income: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    job: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    gender: Mapped[str] = mapped_column(String(10), nullable=False, default="")
    avatar_data_url: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class QuestionnaireSession(Timestamped, Base):
    __tablename__ = "questionnaire_sessions"
    __table_args__ = (
        CheckConstraint("expires_at > created_at", name="ck_questionnaire_session_expiry"),
        UniqueConstraint("questionnaire_session_id", "owner_account_id", name="uq_questionnaire_session_owner"),
    )
    questionnaire_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    questionnaire_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questionnaire_versions.questionnaire_version_id"), nullable=False
    )
    state: Mapped[QuestionnaireSessionState] = mapped_column(nullable=False, default=QuestionnaireSessionState.ACTIVE)
    owner_account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("accounts.account_id", ondelete="RESTRICT"), index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class QuestionnaireAnswer(Base):
    __tablename__ = "questionnaire_answers"
    __table_args__ = (
        UniqueConstraint("questionnaire_session_id", "question_id", name="uq_questionnaire_answer_session_question"),
        ForeignKeyConstraint(
            ["question_id", "answer_option_id"],
            ["answer_options.question_id", "answer_options.answer_option_id"],
            name="fk_questionnaire_answer_option_belongs_to_question",
        ),
    )
    questionnaire_answer_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    questionnaire_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questionnaire_sessions.questionnaire_session_id"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.question_id"), nullable=False)
    answer_option_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("answer_options.answer_option_id"), nullable=False)


class RecommendationHistoryRun(Timestamped, Base):
    """Immutable, account-owned record of one successful recommendation response."""

    __tablename__ = "recommendation_history_runs"
    __table_args__ = (
        UniqueConstraint("questionnaire_session_id", name="uq_recommendation_history_session"),
        ForeignKeyConstraint(
            ["questionnaire_session_id", "owner_account_id"],
            ["questionnaire_sessions.questionnaire_session_id", "questionnaire_sessions.owner_account_id"],
            name="fk_history_session_owner",
            ondelete="RESTRICT",
        ),
        Index(
            "ix_recommendation_history_owner_created", "owner_account_id", "created_at", "recommendation_history_run_id"
        ),
    )
    recommendation_history_run_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    owner_account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.account_id", ondelete="RESTRICT"), nullable=False
    )
    questionnaire_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questionnaire_sessions.questionnaire_session_id"), nullable=False
    )
    data_version: Mapped[str] = mapped_column(String(100), nullable=False)
    config_version: Mapped[str] = mapped_column(String(100), nullable=False)
    # A user can hide a run from their own list without destroying the immutable
    # audit snapshot retained for administrative review.
    hidden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RecommendationHistoryItem(Base):
    """Stable display facts for one historical result item; never re-read from mutable serving data."""

    __tablename__ = "recommendation_history_items"
    __table_args__ = (
        UniqueConstraint("recommendation_history_run_id", "section", "display_order", name="uq_history_item_order"),
        CheckConstraint("section IN ('ranked', 'low', 'review')", name="ck_history_item_section"),
        CheckConstraint("display_order >= 0", name="ck_history_item_display_order"),
    )
    recommendation_history_item_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    recommendation_history_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recommendation_history_runs.recommendation_history_run_id"), nullable=False
    )
    section: Mapped[str] = mapped_column(String(30), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    loan_product_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("loan_product_versions.loan_product_version_id"), nullable=False
    )
    lender_name: Mapped[str] = mapped_column(String(255), nullable=False)
    loan_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bank_logo_reference: Mapped[str | None] = mapped_column(String(512))
    compatibility_score: Mapped[float | None] = mapped_column(Float)
    compatibility_reason: Mapped[str | None] = mapped_column(Text)
    max_amount_tomans: Mapped[float | None] = mapped_column(Numeric(18, 2))
    monthly_installment_tomans: Mapped[float | None] = mapped_column(Numeric(18, 2))
    max_repayment_months: Mapped[int | None] = mapped_column(Integer)
    interest_rate_percent: Mapped[float | None] = mapped_column(Numeric(8, 4))


class RecommendationHistoryItemReason(Base):
    __tablename__ = "recommendation_history_item_reasons"
    recommendation_history_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recommendation_history_items.recommendation_history_item_id"), primary_key=True
    )
    display_order: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)


class OperationsImport(Base):
    """Immutable versioned review evidence, not a second live loan catalogue."""

    __tablename__ = "operations_imports"
    import_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    import_code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    source_hash: Mapped[str] = mapped_column(Text, nullable=False)
    parser_version: Mapped[str] = mapped_column(Text, nullable=False)
    preparation: Mapped[dict[str, object]] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=False)
    __table_args__ = (
        CheckConstraint(
            "length(trim(import_code)) > 0 AND length(trim(parser_version)) > 0", name="ck_operations_import_identity"
        ),
    )


class OperationsVersion(Base):
    """Immutable draft identity; current state is projected from the decision ledger."""

    __tablename__ = "operations_versions"
    version_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    version_code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operations_imports.import_id"), nullable=False, index=True)
    diff: Mapped[dict[str, object]] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=False)
    __table_args__ = (
        CheckConstraint("length(trim(version_code)) > 0", name="ck_operations_version_identity"),
        UniqueConstraint("version_id", "import_id", name="uq_operations_version_import"),
    )


class AuditEvent(Base):
    """Append-only actor decision with relational linkage and before/after state."""

    __tablename__ = "audit_events"
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    event_order: Mapped[int] = mapped_column(BigInteger, Identity(), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(16), nullable=False)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operations_imports.import_id"), nullable=False, index=True)
    version_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    actor_reference: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    correlation_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, unique=True)
    before_state: Mapped[str | None] = mapped_column(String(16), nullable=True)
    after_state: Mapped[str] = mapped_column(String(16), nullable=False)
    before_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("operations_versions.version_id"))
    after_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("operations_versions.version_id"))
    __table_args__ = (
        ForeignKeyConstraint(
            ["version_id", "import_id"],
            ["operations_versions.version_id", "operations_versions.import_id"],
            name="fk_audit_version_import",
        ),
        CheckConstraint(
            "event_type IN ('import', 'prepare', 'approve', 'publish', 'rollback')", name="ck_audit_event_type"
        ),
        CheckConstraint("length(trim(actor_reference)) > 0 AND length(trim(reason)) > 0", name="ck_audit_actor_reason"),
        CheckConstraint(
            "COALESCE((event_type = 'import' AND version_id IS NULL AND before_state IS NULL "
            "AND after_state = 'reviewed') OR "
            "(event_type = 'prepare' AND version_id IS NOT NULL AND before_state IS NULL AND after_state = 'draft') OR "
            "(event_type = 'approve' AND version_id IS NOT NULL AND before_state = 'draft' "
            "AND after_state = 'approved') OR "
            "(event_type = 'publish' AND version_id IS NOT NULL AND before_state = 'approved' "
            "AND after_state = 'published' AND after_version_id IS NOT NULL "
            "AND after_version_id = version_id) OR "
            "(event_type = 'rollback' AND version_id IS NOT NULL AND before_state = 'superseded' "
            "AND after_state = 'published' AND after_version_id IS NOT NULL "
            "AND before_version_id IS NOT NULL AND after_version_id = version_id), FALSE)",
            name="ck_audit_transition",
        ),
        CheckConstraint(
            "event_type IN ('publish', 'rollback') OR (before_version_id IS NULL AND after_version_id IS NULL)",
            name="ck_audit_pointer_evidence",
        ),
    )


class OperationsWorkflowHead(Base):
    """Singleton transaction lock and current internal workflow version."""

    __tablename__ = "operations_workflow_head"
    head_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("operations_versions.version_id"))
    __table_args__ = (CheckConstraint("head_id = 1", name="ck_operations_singleton"),)
