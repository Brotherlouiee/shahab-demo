"""Stable identifiers and validation for the two non-scoring entry questions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FlowStep:
    step_id: str
    answer_ids: frozenset[str]


QUESTIONNAIRE_FLOW_STEPS = (
    FlowStep("loan_type", frozenset({"shahab", "bank"})),
    FlowStep("entity_type", frozenset({"business", "person"})),
)
QUESTIONNAIRE_FLOW_STEP_BY_ID = {step.step_id: step for step in QUESTIONNAIRE_FLOW_STEPS}


def validate_flow_answer(step_id: str, answer_id: str) -> tuple[int, str]:
    step = QUESTIONNAIRE_FLOW_STEP_BY_ID.get(step_id)
    if step is None or answer_id not in step.answer_ids:
        raise ValueError("flow answer is not valid for this step")
    return next(index for index, candidate in enumerate(QUESTIONNAIRE_FLOW_STEPS) if candidate == step), answer_id
