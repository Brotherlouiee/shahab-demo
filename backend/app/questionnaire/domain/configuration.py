"""Immutable, source-traceable questionnaire configuration contracts.

The module validates the committed configuration artifact before any later
route/session code can consume it. It deliberately has no HTTP, ORM, file-import
or recommendation-engine dependency: question wording and answer identifiers
are a stable product contract, while navigation and persistence are separate
US-07 responsibilities.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class QuestionnaireConfigurationError(ValueError):
    """Raised when a configuration cannot safely be used as a canonical contract."""


@dataclass(frozen=True)
class AnswerOptionConfiguration:
    """One required, stable answer identifier and its source-derived display label."""

    answer_id: str
    label: str


@dataclass(frozen=True)
class QuestionConfiguration:
    """One source-traceable question; display ordering is source ordering, not a route index."""

    question_id: str
    source_question_number: int
    prompt: str
    required: bool
    answer_options: tuple[AnswerOptionConfiguration, ...]


@dataclass(frozen=True)
class QuestionnaireConfiguration:
    """Approved questionnaire contract used by future adapters and session use cases."""

    schema_version: str
    questionnaire_version: str
    source_path: str
    source_sha256: str
    questions: tuple[QuestionConfiguration, ...]


def load_questionnaire_configuration(path: Path, canonical_identifiers: dict[str, Any]) -> QuestionnaireConfiguration:
    """Load and validate a committed configuration against canonical identifier policy.

    Args:
        path: JSON artifact generated from the verified behavioral questionnaire source.
        canonical_identifiers: Parsed stable-ID contract from `data/contracts`.

    Raises:
        QuestionnaireConfigurationError: If the artifact is malformed, incomplete,
            unapproved, or inconsistent with the canonical identifier contract.
    """

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise QuestionnaireConfigurationError("questionnaire configuration is unreadable") from error

    if raw.get("schemaVersion") != "1.0.0" or raw.get("approved") is not True:
        raise QuestionnaireConfigurationError("configuration must be approved schema version 1.0.0")

    source = raw.get("source")
    if (
        not isinstance(source, dict)
        or not isinstance(source.get("path"), str)
        or not isinstance(source.get("sha256"), str)
    ):
        raise QuestionnaireConfigurationError("configuration must declare source path and SHA-256")

    expected_questions = canonical_identifiers.get("questionIds")
    expected_answers = canonical_identifiers.get("questions")
    if not isinstance(expected_questions, list) or not isinstance(expected_answers, dict):
        raise QuestionnaireConfigurationError("canonical identifier contract is incomplete")

    raw_questions = raw.get("questions")
    if not isinstance(raw_questions, list):
        raise QuestionnaireConfigurationError("configuration questions must be a list")

    questions: list[QuestionConfiguration] = []
    seen_question_ids: set[str] = set()
    seen_source_numbers: set[int] = set()
    for raw_question in raw_questions:
        if not isinstance(raw_question, dict):
            raise QuestionnaireConfigurationError("every question must be an object")
        question_id = raw_question.get("questionId")
        source_question_number = raw_question.get("sourceQuestionNumber")
        prompt = raw_question.get("prompt")
        required = raw_question.get("required")
        raw_options = raw_question.get("answerOptions")
        if (
            not isinstance(question_id, str)
            or not isinstance(source_question_number, int)
            or not isinstance(prompt, str)
            or not prompt.strip()
            or required is not True
            or not isinstance(raw_options, list)
        ):
            raise QuestionnaireConfigurationError("question fields are invalid or incomplete")
        if question_id in seen_question_ids or source_question_number in seen_source_numbers:
            raise QuestionnaireConfigurationError("question IDs and source question numbers must be unique")

        expected_keys = expected_answers.get(question_id)
        if not isinstance(expected_keys, list) or len(raw_options) != len(expected_keys):
            raise QuestionnaireConfigurationError(f"{question_id} does not have the approved answer set")

        options: list[AnswerOptionConfiguration] = []
        seen_answer_ids: set[str] = set()
        for raw_option, expected_key in zip(raw_options, expected_keys, strict=True):
            if not isinstance(raw_option, dict):
                raise QuestionnaireConfigurationError("every answer option must be an object")
            answer_id = raw_option.get("answerId")
            label = raw_option.get("label")
            if answer_id != f"{question_id}.{expected_key}" or not isinstance(label, str) or not label.strip():
                raise QuestionnaireConfigurationError(f"{question_id} has an invalid answer option")
            if answer_id in seen_answer_ids:
                raise QuestionnaireConfigurationError(f"{question_id} contains duplicate answer IDs")
            seen_answer_ids.add(answer_id)
            options.append(AnswerOptionConfiguration(answer_id=answer_id, label=label))

        seen_question_ids.add(question_id)
        seen_source_numbers.add(source_question_number)
        questions.append(
            QuestionConfiguration(
                question_id=question_id,
                source_question_number=source_question_number,
                prompt=prompt,
                required=required,
                answer_options=tuple(options),
            )
        )

    if [question.question_id for question in questions] != expected_questions:
        raise QuestionnaireConfigurationError("question order must exactly follow the canonical contract")
    if not isinstance(raw.get("questionnaireVersion"), str) or not raw["questionnaireVersion"].strip():
        raise QuestionnaireConfigurationError("configuration must declare questionnaireVersion")

    return QuestionnaireConfiguration(
        schema_version=raw["schemaVersion"],
        questionnaire_version=raw["questionnaireVersion"],
        source_path=source["path"],
        source_sha256=source["sha256"],
        questions=tuple(questions),
    )
