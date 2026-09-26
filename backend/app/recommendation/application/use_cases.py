"""Framework-free application composition for one deterministic recommendation run."""

from __future__ import annotations

from backend.app.recommendation.application.ports import RecommendationSnapshotRepository
from backend.app.recommendation.domain.entities import (
    AnswerPreference,
    RecommendationInputError,
    RecommendationRun,
    RecommendationSnapshot,
)
from backend.app.recommendation.engine.canonical_scoring import (
    CanonicalPartition,
    CategoryImpact,
    score_official_categories,
)
from backend.app.recommendation.engine.scoring import partition_loans
from backend.app.recommendation.engine.trace import build_recommendation_trace


class RecommendLoans:
    """Build ranked and needs-review outputs from one approved, immutable snapshot.

    The use case intentionally accepts already-canonical preferences. Resolving
    questionnaire sessions, HTTP schemas, database transactions and UI rendering
    remain their respective later boundaries. The repository is responsible for
    one consistent approved read; this class never opens an ORM session itself.
    """

    def __init__(self, repository: RecommendationSnapshotRepository) -> None:
        self._repository = repository

    def execute(self, preferences: tuple[AnswerPreference, ...]) -> RecommendationRun:
        """Run the pure engine and produce exactly one redacted trace per candidate."""

        if not preferences:
            raise RecommendationInputError("at least one preference is required")

        snapshot = self._repository.read_approved_snapshot()
        _validate_snapshot(snapshot)
        partition = partition_loans(snapshot.candidates, preferences)
        traces = tuple(
            sorted(
                (
                    build_recommendation_trace(
                        candidate,
                        preferences,
                        data_version=snapshot.data_version,
                        config_version=snapshot.config_version,
                    )
                    for candidate in snapshot.candidates
                ),
                key=lambda trace: trace.loan_id,
            )
        )
        return RecommendationRun(
            data_version=snapshot.data_version,
            config_version=snapshot.config_version,
            ranked_recommendations=partition.ranked,
            needs_review=partition.needs_review,
            traces=traces,
        )


def _validate_snapshot(snapshot: RecommendationSnapshot) -> None:
    """Reject incomplete versions or duplicate identities before scoring begins."""

    if not snapshot.data_version or snapshot.data_version != snapshot.data_version.strip():
        raise RecommendationInputError("data_version is required")
    if not snapshot.config_version or snapshot.config_version != snapshot.config_version.strip():
        raise RecommendationInputError("config_version is required")

    loan_ids = [candidate.loan_id for candidate in snapshot.candidates]
    if len(loan_ids) != len(set(loan_ids)):
        raise RecommendationInputError("snapshot candidate IDs must be unique")


class RecommendCanonicalLoans:
    """Run the source-backed category model against one published snapshot."""

    def __init__(self, repository: RecommendationSnapshotRepository) -> None:
        self._repository = repository

    def execute(self, impacts: tuple[CategoryImpact, ...]) -> tuple[RecommendationSnapshot, CanonicalPartition]:
        snapshot = self._repository.read_approved_snapshot()
        _validate_snapshot(snapshot)
        return snapshot, score_official_categories(snapshot.candidates, impacts)
