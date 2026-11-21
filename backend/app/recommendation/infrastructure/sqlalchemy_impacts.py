"""Read the D-005 answer conversion and one-to-one cells from the active config."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import (
    AnswerCategoryCompatibility,
    AnswerOption,
    AnswerOptionWeight,
    LoanVariable,
    Question,
    QuestionVariableWeight,
    RecommendationConfigVersion,
    ServingCatalogueVersion,
    VariableCategory,
)
from backend.app.recommendation.engine.canonical_scoring import CategoryImpact
from backend.app.recommendation.infrastructure.sqlalchemy_snapshot import (
    SnapshotIntegrityError,
    SnapshotUnavailableError,
)


class SqlAlchemyCanonicalImpactRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def read_approved_impacts(self, answers: dict[str, str], config_version: str) -> tuple[CategoryImpact, ...]:
        statement = (
            select(
                Question.canonical_id,
                AnswerOption.canonical_id,
                LoanVariable.canonical_id,
                VariableCategory.canonical_id,
                QuestionVariableWeight.weight,
                AnswerOptionWeight.weighted_value,
                AnswerCategoryCompatibility.coefficient,
                AnswerCategoryCompatibility.source_row_number,
                AnswerCategoryCompatibility.source_column_number,
            )
            .select_from(ServingCatalogueVersion)
            .join(
                RecommendationConfigVersion,
                RecommendationConfigVersion.config_version_id == ServingCatalogueVersion.config_version_id,
            )
            .join(
                AnswerOptionWeight,
                AnswerOptionWeight.config_version_id == RecommendationConfigVersion.config_version_id,
            )
            .join(AnswerOption, AnswerOption.answer_option_id == AnswerOptionWeight.answer_option_id)
            .join(Question, Question.question_id == AnswerOption.question_id)
            .join(LoanVariable, LoanVariable.loan_variable_id == AnswerOptionWeight.loan_variable_id)
            .join(
                QuestionVariableWeight,
                (QuestionVariableWeight.config_version_id == RecommendationConfigVersion.config_version_id)
                & (QuestionVariableWeight.question_id == Question.question_id)
                & (QuestionVariableWeight.loan_variable_id == LoanVariable.loan_variable_id),
            )
            .join(
                AnswerCategoryCompatibility,
                (AnswerCategoryCompatibility.config_version_id == RecommendationConfigVersion.config_version_id)
                & (AnswerCategoryCompatibility.answer_option_id == AnswerOption.answer_option_id),
            )
            .join(
                VariableCategory,
                (VariableCategory.variable_category_id == AnswerCategoryCompatibility.variable_category_id)
                & (VariableCategory.loan_variable_id == LoanVariable.loan_variable_id),
            )
            .where(
                ServingCatalogueVersion.active.is_(True),
                RecommendationConfigVersion.approved.is_(True),
                RecommendationConfigVersion.version_code == config_version,
                AnswerOption.canonical_id.in_(tuple(answers.values())),
            )
        )
        try:
            rows = self._session.execute(statement).all()
        except SQLAlchemyError as error:
            raise SnapshotUnavailableError("approved recommendation configuration is unavailable") from error
        # 30 source conversion cells cover the ten selected answers; 144 one-to-one
        # cells cover every published category for each of these answer/variable pairs.
        if len(rows) != 144 or len({(r[0], r[2]) for r in rows}) != 30:
            raise SnapshotIntegrityError("selected answer/category configuration is incomplete")
        impacts: list[CategoryImpact] = []
        for question_id, answer_id, variable_id, category_id, question_weight, weighted, factor, row, column in rows:
            if answers.get(question_id) != answer_id or Decimal(weighted) > Decimal(question_weight):
                raise SnapshotIntegrityError("selected conversion cell conflicts with approved source")
            impacts.append(
                CategoryImpact(variable_id, category_id, answer_id, Decimal(weighted), Decimal(factor), row, column)
            )
        return tuple(impacts)
