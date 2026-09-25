"""US-08.T05 regression, property-style and golden tests for the recommendation core."""

from __future__ import annotations

from decimal import Decimal
from itertools import permutations, product
import unittest

from backend.app.recommendation.application.use_cases import RecommendLoans
from backend.app.recommendation.domain.entities import (
    AnswerPreference,
    ClassificationState,
    LoanCandidate,
    RecommendationDecision,
    RecommendationSnapshot,
)
from backend.app.recommendation.engine.scoring import partition_loans, score_loan
from backend.app.recommendation.engine.trace import build_recommendation_trace


class _SnapshotRepository:
    def __init__(self, snapshot: RecommendationSnapshot) -> None:
        self._snapshot = snapshot

    def read_approved_snapshot(self) -> RecommendationSnapshot:
        return self._snapshot


class RecommendationEngineGoldenTests(unittest.TestCase):
    """Protect approved policy behavior without adding transport or persistence."""

    def setUp(self) -> None:
        self.core_preferences = (
            AnswerPreference("maxAmount", "amount.high", Decimal("0.4")),
            AnswerPreference("monthlyInstallment", "installment.low", Decimal("0.3")),
            AnswerPreference("maxRepaymentMonths", "term.long", Decimal("0.2")),
            AnswerPreference("interestRate", "interest.low", Decimal("0.1")),
        )

    def test_golden_complete_catalogue_ranks_score_then_stable_loan_id(self) -> None:
        candidates = (
            LoanCandidate(
                "loan-z",
                {
                    "maxAmount": "amount.high",
                    "monthlyInstallment": "installment.low",
                    "maxRepaymentMonths": "term.long",
                    "interestRate": "interest.low",
                },
            ),
            LoanCandidate(
                "loan-b",
                {
                    "maxAmount": "amount.high",
                    "monthlyInstallment": "installment.low",
                    "maxRepaymentMonths": "term.long",
                    "interestRate": "interest.low",
                },
            ),
            LoanCandidate(
                "loan-a",
                {
                    "maxAmount": "amount.low",
                    "monthlyInstallment": "installment.low",
                    "maxRepaymentMonths": "term.short",
                    "interestRate": "interest.low",
                },
            ),
        )

        partition = partition_loans(candidates, self.core_preferences)

        self.assertEqual(
            partition.ranked,
            (
                score_loan(candidates[1], self.core_preferences),
                score_loan(candidates[0], self.core_preferences),
                score_loan(candidates[2], self.core_preferences),
            ),
        )
        self.assertEqual(
            [item.score for item in partition.ranked],
            [Decimal("1.000000"), Decimal("1.000000"), Decimal("0.400000")],
        )
        self.assertEqual(partition.needs_review, ())

    def test_golden_neutral_deposit_is_excluded_from_score_and_trace_weight(self) -> None:
        preferences = self.core_preferences + (AnswerPreference("depositRequired", "deposit.required", Decimal("0.9")),)
        candidate = LoanCandidate(
            "loan-neutral",
            {
                "maxAmount": "amount.high",
                "monthlyInstallment": "installment.low",
                "maxRepaymentMonths": "term.long",
                "interestRate": "interest.low",
                "depositRequired": None,
            },
            {"depositRequired": ClassificationState.UNKNOWN},
        )

        score = score_loan(candidate, preferences)
        trace = build_recommendation_trace(
            candidate,
            preferences,
            data_version="serving.v1",
            config_version="recommendation.v1",
        )

        self.assertEqual(score.score, Decimal("1.000000"))
        self.assertEqual(trace.decision, RecommendationDecision.RANKED)
        self.assertEqual(trace.effective_weight, Decimal("1.0"))
        self.assertEqual(trace.neutral_variables, ("depositRequired",))
        contribution = next(item for item in trace.contributions if item.variable_id == "depositRequired")
        self.assertTrue(contribution.neutral)
        self.assertFalse(contribution.included_in_effective_weight)
        self.assertIsNone(contribution.matched)

    def test_golden_core_states_are_never_silently_ranked(self) -> None:
        for state in (
            ClassificationState.UNKNOWN,
            ClassificationState.VARIABLE,
            ClassificationState.NEUTRAL,
        ):
            with self.subTest(state=state):
                candidate = LoanCandidate(
                    f"loan-{state}",
                    {
                        "maxAmount": None,
                        "monthlyInstallment": "installment.low",
                        "maxRepaymentMonths": "term.long",
                        "interestRate": "interest.low",
                    },
                    {"maxAmount": state},
                )

                partition = partition_loans((candidate,), self.core_preferences)
                trace = build_recommendation_trace(
                    candidate,
                    self.core_preferences,
                    data_version="serving.v1",
                    config_version="recommendation.v1",
                )

                self.assertEqual(partition.ranked, ())
                self.assertEqual(partition.needs_review[0].excluded_reasons, (f"maxAmount:{state}",))
                self.assertEqual(trace.decision, RecommendationDecision.NEEDS_REVIEW)
                self.assertIsNone(trace.raw_score)
                self.assertEqual(trace.ranking_excluded_reasons, (f"maxAmount:{state}",))


class RecommendationEnginePropertyTests(unittest.TestCase):
    """Small exhaustive properties provide deterministic regression coverage."""

    def test_preference_and_candidate_permutations_preserve_a_complete_run(self) -> None:
        preferences = (
            AnswerPreference("maxAmount", "amount.high", Decimal("0.5")),
            AnswerPreference("interestRate", "interest.low", Decimal("0.3")),
            AnswerPreference("depositHoldingMonths", "deposit.none", Decimal("0.2")),
        )
        candidates = (
            LoanCandidate(
                "loan-b",
                {
                    "maxAmount": "amount.high",
                    "interestRate": "interest.low",
                    "depositHoldingMonths": "deposit.none",
                },
            ),
            LoanCandidate(
                "loan-a",
                {
                    "maxAmount": "amount.low",
                    "interestRate": "interest.low",
                    "depositHoldingMonths": "deposit.none",
                },
            ),
        )
        baseline = RecommendLoans(
            _SnapshotRepository(RecommendationSnapshot("serving.v1", "recommendation.v1", candidates))
        ).execute(preferences)
        expected = (
            baseline.ranked_recommendations,
            baseline.needs_review,
            tuple((trace.loan_id, trace.stable_hash) for trace in baseline.traces),
        )

        for ordered_preferences in permutations(preferences):
            for ordered_candidates in permutations(candidates):
                with self.subTest(
                    preference_order=tuple(item.variable_id for item in ordered_preferences),
                    candidate_order=tuple(item.loan_id for item in ordered_candidates),
                ):
                    run = RecommendLoans(
                        _SnapshotRepository(
                            RecommendationSnapshot("serving.v1", "recommendation.v1", ordered_candidates)
                        )
                    ).execute(ordered_preferences)
                    actual = (
                        run.ranked_recommendations,
                        run.needs_review,
                        tuple((trace.loan_id, trace.stable_hash) for trace in run.traces),
                    )
                    self.assertEqual(actual, expected)

    def test_binary_category_space_always_yields_a_bounded_weighted_score(self) -> None:
        preferences = (
            AnswerPreference("maxAmount", "high", Decimal("0.6")),
            AnswerPreference("interestRate", "low", Decimal("0.4")),
        )

        for amount, interest in product(("high", "low"), repeat=2):
            with self.subTest(amount=amount, interest=interest):
                score = score_loan(
                    LoanCandidate("loan", {"maxAmount": amount, "interestRate": interest}),
                    preferences,
                ).score
                self.assertGreaterEqual(score, Decimal("0"))
                self.assertLessEqual(score, Decimal("1"))
                self.assertIn(
                    score,
                    {
                        Decimal("0.000000"),
                        Decimal("0.400000"),
                        Decimal("0.600000"),
                        Decimal("1.000000"),
                    },
                )

    def test_every_snapshot_candidate_has_exactly_one_terminal_output_and_trace(self) -> None:
        preferences = (
            AnswerPreference("maxAmount", "amount.high", Decimal("0.6")),
            AnswerPreference("interestRate", "interest.low", Decimal("0.4")),
        )
        candidates = (
            LoanCandidate("loan-ranked", {"maxAmount": "amount.high", "interestRate": "interest.low"}),
            LoanCandidate(
                "loan-review",
                {"maxAmount": None, "interestRate": "interest.low"},
                {"maxAmount": ClassificationState.UNKNOWN},
            ),
        )

        run = RecommendLoans(
            _SnapshotRepository(RecommendationSnapshot("serving.v1", "recommendation.v1", candidates))
        ).execute(preferences)
        terminal_ids = {item.loan_id for item in run.ranked_recommendations} | {
            item.loan_id for item in run.needs_review
        }

        self.assertEqual(terminal_ids, {candidate.loan_id for candidate in candidates})
        self.assertEqual(len(run.ranked_recommendations) + len(run.needs_review), len(candidates))
        self.assertEqual([trace.loan_id for trace in run.traces], ["loan-ranked", "loan-review"])


if __name__ == "__main__":
    unittest.main()
