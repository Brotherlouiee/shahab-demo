"""US-08.T04 tests for application-level recommendation composition."""

from __future__ import annotations

import unittest
from decimal import Decimal

from backend.app.recommendation.application.use_cases import RecommendLoans
from backend.app.recommendation.domain.entities import (
    AnswerPreference,
    ClassificationState,
    LoanCandidate,
    RecommendationDecision,
    RecommendationInputError,
    RecommendationSnapshot,
)


class _FakeSnapshotRepository:
    def __init__(self, snapshot: RecommendationSnapshot) -> None:
        self.snapshot = snapshot
        self.reads = 0

    def read_approved_snapshot(self) -> RecommendationSnapshot:
        self.reads += 1
        return self.snapshot


class RecommendLoansTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preferences = (
            AnswerPreference("maxAmount", "amount.high", Decimal("0.6")),
            AnswerPreference("interestRate", "interest.low", Decimal("0.4")),
        )

    def test_returns_one_deterministic_snapshot_run_and_trace_per_candidate(self) -> None:
        repository = _FakeSnapshotRepository(
            RecommendationSnapshot(
                data_version="serving.v1",
                config_version="recommendation.v1",
                candidates=(
                    LoanCandidate("loan-b", {"maxAmount": "amount.high", "interestRate": "interest.low"}),
                    LoanCandidate("loan-a", {"maxAmount": "amount.high", "interestRate": "interest.low"}),
                ),
            )
        )

        run = RecommendLoans(repository).execute(self.preferences)

        self.assertEqual(repository.reads, 1)
        self.assertEqual(run.data_version, "serving.v1")
        self.assertEqual(run.config_version, "recommendation.v1")
        self.assertEqual([result.loan_id for result in run.ranked_recommendations], ["loan-a", "loan-b"])
        self.assertEqual([trace.loan_id for trace in run.traces], ["loan-a", "loan-b"])
        self.assertTrue(all(trace.decision is RecommendationDecision.RANKED for trace in run.traces))

    def test_keeps_core_unknown_out_of_ranked_output_but_preserves_its_trace(self) -> None:
        repository = _FakeSnapshotRepository(
            RecommendationSnapshot(
                data_version="serving.v1",
                config_version="recommendation.v1",
                candidates=(
                    LoanCandidate("loan-ranked", {"maxAmount": "amount.high", "interestRate": "interest.low"}),
                    LoanCandidate(
                        "loan-review",
                        {"maxAmount": None, "interestRate": "interest.low"},
                        {"maxAmount": ClassificationState.UNKNOWN},
                    ),
                ),
            )
        )

        run = RecommendLoans(repository).execute(self.preferences)

        self.assertEqual([result.loan_id for result in run.ranked_recommendations], ["loan-ranked"])
        self.assertEqual(run.needs_review[0].loan_id, "loan-review")
        review_trace = next(trace for trace in run.traces if trace.loan_id == "loan-review")
        self.assertEqual(review_trace.decision, RecommendationDecision.NEEDS_REVIEW)
        self.assertEqual(review_trace.ranking_excluded_reasons, ("maxAmount:unknown",))

    def test_rejects_invalid_snapshot_before_engine_execution(self) -> None:
        repository = _FakeSnapshotRepository(
            RecommendationSnapshot(
                data_version="",
                config_version="recommendation.v1",
                candidates=(),
            )
        )

        with self.assertRaises(RecommendationInputError):
            RecommendLoans(repository).execute(self.preferences)
