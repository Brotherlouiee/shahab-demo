"""One-statement, consistent read of the active approved recommendation catalogue."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import (
    AnswerCategoryCompatibility,
    AnswerOptionWeight,
    LoanCategoryAssignment,
    LoanProductVersion,
    LoanVariable,
    PublicationState,
    QuestionVariableWeight,
    RecommendationConfigVersion,
    ServingCatalogueMember,
    ServingCatalogueVersion,
    VariableCategory,
)
from backend.app.recommendation.application.ports import RecommendationSnapshotRepository
from backend.app.recommendation.domain.entities import ClassificationState, LoanCandidate, RecommendationSnapshot

REQUIRED_VARIABLES = frozenset(
    {
        "maxAmount",
        "monthlyInstallment",
        "maxRepaymentMonths",
        "interestRate",
        "depositRequired",
        "depositHoldingMonths",
        "loanToDepositRatio",
        "guaranteeType",
    }
)


class SnapshotUnavailableError(RuntimeError):
    """No active approved serving version exists."""


class SnapshotIntegrityError(RuntimeError):
    """The active published version is incomplete or inconsistent."""


class SqlAlchemyRecommendationSnapshotRepository(RecommendationSnapshotRepository):
    """Read one SQL statement to avoid mixed versions at READ COMMITTED isolation."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def read_approved_snapshot(self) -> RecommendationSnapshot:
        weight_count = (
            select(func.count())
            .select_from(QuestionVariableWeight)
            .where(QuestionVariableWeight.config_version_id == ServingCatalogueVersion.config_version_id)
            .scalar_subquery()
        )
        answer_count = (
            select(func.count())
            .select_from(AnswerOptionWeight)
            .where(AnswerOptionWeight.config_version_id == ServingCatalogueVersion.config_version_id)
            .scalar_subquery()
        )
        compatibility_count = (
            select(func.count())
            .select_from(AnswerCategoryCompatibility)
            .where(AnswerCategoryCompatibility.config_version_id == ServingCatalogueVersion.config_version_id)
            .scalar_subquery()
        )
        statement = (
            select(
                ServingCatalogueVersion,
                RecommendationConfigVersion,
                LoanProductVersion,
                LoanCategoryAssignment,
                LoanVariable,
                VariableCategory,
                weight_count,
                answer_count,
                compatibility_count,
            )
            .join(
                RecommendationConfigVersion,
                RecommendationConfigVersion.config_version_id == ServingCatalogueVersion.config_version_id,
            )
            .outerjoin(
                ServingCatalogueMember,
                ServingCatalogueMember.serving_catalogue_version_id
                == ServingCatalogueVersion.serving_catalogue_version_id,
            )
            .outerjoin(
                LoanProductVersion,
                LoanProductVersion.loan_product_version_id == ServingCatalogueMember.loan_product_version_id,
            )
            .outerjoin(
                LoanCategoryAssignment,
                LoanCategoryAssignment.loan_product_version_id == LoanProductVersion.loan_product_version_id,
            )
            .outerjoin(LoanVariable, LoanVariable.loan_variable_id == LoanCategoryAssignment.loan_variable_id)
            .outerjoin(
                VariableCategory, VariableCategory.variable_category_id == LoanCategoryAssignment.variable_category_id
            )
            .where(ServingCatalogueVersion.active.is_(True))
        )
        try:
            rows = self._session.execute(statement).all()
        except SQLAlchemyError as error:
            raise SnapshotUnavailableError("approved recommendation storage is unavailable") from error
        if not rows:
            raise SnapshotUnavailableError("active approved recommendation catalogue is unavailable")
        catalogue, config = rows[0][:2]
        if (
            catalogue.state != "published"
            or not config.approved
            or config.version_code != "1.1.0"
            or rows[0][6:] != (30, 150, 720)
        ):
            raise SnapshotIntegrityError("approved recommendation configuration is incomplete")
        candidates: dict[str, dict[str, tuple[str | None, ClassificationState]]] = {}
        for _, _, version, assignment, variable, category, _, _, _ in rows:
            if version is None:
                continue
            assert isinstance(version, LoanProductVersion)
            if (
                version.publication_state is not PublicationState.PUBLISHED
                or version.source_file_id != catalogue.data_source_file_id
            ):
                raise SnapshotIntegrityError("serving member is not from the published source")
            loan_id = str(version.loan_product_version_id)
            values = candidates.setdefault(loan_id, {})
            if assignment is None or variable is None:
                raise SnapshotIntegrityError("published loan has missing category assignments")
            assert isinstance(assignment, LoanCategoryAssignment)
            assert isinstance(variable, LoanVariable)
            if variable.canonical_id not in REQUIRED_VARIABLES or variable.canonical_id in values:
                raise SnapshotIntegrityError("published loan has duplicate or unknown variables")
            if assignment.classification_state == "classified":
                if not isinstance(category, VariableCategory) or category.loan_variable_id != variable.loan_variable_id:
                    raise SnapshotIntegrityError("classified category does not belong to the loan variable")
                state = ClassificationState.CLASSIFIED
                category_id = category.canonical_id
            else:
                if category is not None or assignment.classification_state not in {
                    "unknown",
                    "variable",
                    "unparseable",
                    "unmapped",
                }:
                    raise SnapshotIntegrityError("invalid unclassified category state")
                state = (
                    ClassificationState.VARIABLE
                    if assignment.classification_state == "variable"
                    else ClassificationState.UNKNOWN
                )
                category_id = None
            values[variable.canonical_id] = (category_id, state)
        for values in candidates.values():
            if values.keys() != REQUIRED_VARIABLES:
                raise SnapshotIntegrityError("published loan does not cover all eight variables")
        return RecommendationSnapshot(
            data_version=catalogue.version_code,
            config_version=config.version_code,
            candidates=tuple(
                LoanCandidate(
                    loan_id=loan_id,
                    categories={key: pair[0] for key, pair in values.items()},
                    category_states={key: pair[1] for key, pair in values.items()},
                )
                for loan_id, values in sorted(candidates.items())
            ),
        )
