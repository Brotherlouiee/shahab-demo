"""Pure construction of deterministic, redacted recommendation evidence."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from hashlib import sha256
from json import dumps

from backend.app.recommendation.domain.entities import (
    AnswerPreference,
    ClassificationState,
    LoanCandidate,
    RecommendationDecision,
    RecommendationInputError,
    RecommendationTrace,
    TraceContribution,
)
from backend.app.recommendation.engine.scoring import (
    CORE_VARIABLE_IDS,
    NEUTRAL_VARIABLE_IDS,
    _validate_preference,
    score_loan,
)


def build_recommendation_trace(
    candidate: LoanCandidate,
    preferences: tuple[AnswerPreference, ...],
    *,
    data_version: str,
    config_version: str,
    trace_version: str = "1.0",
) -> RecommendationTrace:
    """Explain one candidate decision without retaining session or raw answer content.

    Category identifiers are safe, stable technical evidence. The trace deliberately
    excludes user identity, session identifiers, free-text answers and raw source
    values, so it can be stored or inspected without turning into questionnaire data.
    """

    _validate_version("data_version", data_version)
    _validate_version("config_version", config_version)
    _validate_version("trace_version", trace_version)

    seen_variables: set[str] = set()
    excluded_reasons: list[str] = []
    neutral_variables: list[str] = []
    contributions: list[TraceContribution] = []

    for preference in preferences:
        _validate_preference(preference, seen_variables)
        state = candidate.state_for(preference.variable_id)
        candidate_category_id = candidate.categories.get(preference.variable_id)
        is_core_excluded = preference.variable_id in CORE_VARIABLE_IDS and state is not ClassificationState.CLASSIFIED
        is_neutral = preference.variable_id in NEUTRAL_VARIABLE_IDS and state is not ClassificationState.CLASSIFIED

        if is_core_excluded:
            reason = f"{preference.variable_id}:{state}"
            excluded_reasons.append(reason)
        elif is_neutral:
            reason = f"{preference.variable_id}:{state}"
            neutral_variables.append(preference.variable_id)
        elif preference.variable_id not in candidate.categories:
            raise RecommendationInputError("candidate is missing a required variable")
        else:
            reason = None

        contributions.append(
            TraceContribution(
                variable_id=preference.variable_id,
                preferred_category_id=preference.category_id,
                candidate_category_id=candidate_category_id,
                classification_state=state,
                preference_weight=preference.weight,
                included_in_effective_weight=not is_core_excluded and not is_neutral,
                matched=candidate_category_id == preference.category_id if not is_core_excluded and not is_neutral else None,
                neutral=is_neutral,
                reason=reason,
            )
        )

    ordered_contributions = tuple(sorted(contributions, key=lambda item: item.variable_id))
    ordered_reasons = tuple(sorted(excluded_reasons))
    ordered_neutral_variables = tuple(sorted(neutral_variables))

    if ordered_reasons:
        return _trace(
            trace_version=trace_version,
            data_version=data_version,
            config_version=config_version,
            candidate=candidate,
            decision=RecommendationDecision.NEEDS_REVIEW,
            raw_score=None,
            normalized_score=None,
            effective_weight=Decimal("0"),
            neutral_variables=ordered_neutral_variables,
            ranking_excluded_reasons=ordered_reasons,
            contributions=ordered_contributions,
        )

    score = score_loan(candidate, preferences)
    effective_weight = sum(
        (item.preference_weight for item in ordered_contributions if item.included_in_effective_weight),
        Decimal("0"),
    )
    return _trace(
        trace_version=trace_version,
        data_version=data_version,
        config_version=config_version,
        candidate=candidate,
        decision=RecommendationDecision.RANKED,
        raw_score=score.score,
        normalized_score=score.score,
        effective_weight=effective_weight,
        neutral_variables=ordered_neutral_variables,
        ranking_excluded_reasons=(),
        contributions=ordered_contributions,
    )


def _trace(
    *,
    trace_version: str,
    data_version: str,
    config_version: str,
    candidate: LoanCandidate,
    decision: RecommendationDecision,
    raw_score: Decimal | None,
    normalized_score: Decimal | None,
    effective_weight: Decimal,
    neutral_variables: tuple[str, ...],
    ranking_excluded_reasons: tuple[str, ...],
    contributions: tuple[TraceContribution, ...],
) -> RecommendationTrace:
    """Create the immutable object after hashing its canonical, redacted payload."""

    trace = RecommendationTrace(
        trace_version=trace_version,
        data_version=data_version,
        config_version=config_version,
        loan_id=candidate.loan_id,
        decision=decision,
        raw_score=raw_score,
        normalized_score=normalized_score,
        effective_weight=effective_weight,
        neutral_variables=neutral_variables,
        ranking_excluded_reasons=ranking_excluded_reasons,
        contributions=contributions,
        stable_hash="",
    )
    payload = {
        "traceVersion": trace.trace_version,
        "dataVersion": trace.data_version,
        "configVersion": trace.config_version,
        "loanId": trace.loan_id,
        "decision": trace.decision.value,
        "rawScore": _decimal_text(trace.raw_score),
        "normalizedScore": _decimal_text(trace.normalized_score),
        "effectiveWeight": _decimal_text(trace.effective_weight),
        "neutralVariables": trace.neutral_variables,
        "rankingExcludedReasons": trace.ranking_excluded_reasons,
        "contributions": [
            {
                "variableId": item.variable_id,
                "preferredCategoryId": item.preferred_category_id,
                "candidateCategoryId": item.candidate_category_id,
                "classificationState": item.classification_state.value,
                "preferenceWeight": _decimal_text(item.preference_weight),
                "includedInEffectiveWeight": item.included_in_effective_weight,
                "matched": item.matched,
                "neutral": item.neutral,
                "reason": item.reason,
            }
            for item in trace.contributions
        ],
    }
    return replace(trace, stable_hash=sha256(_canonical_json(payload).encode()).hexdigest())


def _canonical_json(payload: object) -> str:
    return dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _decimal_text(value: Decimal | None) -> str | None:
    return format(value, "f") if value is not None else None


def _validate_version(label: str, value: str) -> None:
    if not value or value != value.strip():
        raise RecommendationInputError(f"{label} is required")
