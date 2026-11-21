"""US-08.T01 tests for the pure deterministic recommendation engine."""

import unittest
from decimal import Decimal

from backend.app.recommendation.domain.entities import (
    AnswerPreference,
    ClassificationState,
    LoanCandidate,
    RecommendationDecision,
    RecommendationInputError,
)
from backend.app.recommendation.engine.scoring import rank_loans, score_loan
from backend.app.recommendation.engine.trace import build_recommendation_trace


class RecommendationEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preferences = (
            AnswerPreference("maxAmount", "amount.high", Decimal("0.6")),
            AnswerPreference("interestRate", "interest.low", Decimal("0.4")),
        )

    def test_scores_a_complete_candidate_with_exact_weighted_ratio(self) -> None:
        result = score_loan(
            LoanCandidate("loan-a", {"maxAmount": "amount.high", "interestRate": "interest.medium"}),
            self.preferences,
        )
        self.assertEqual(result.score, Decimal("0.600000"))

    def test_ranking_is_deterministic_and_uses_identifier_as_tie_breaker(self) -> None:
        ranked = rank_loans(
            (
                LoanCandidate("loan-b", {"maxAmount": "amount.high", "interestRate": "interest.low"}),
                LoanCandidate("loan-a", {"maxAmount": "amount.high", "interestRate": "interest.low"}),
            ),
            self.preferences,
        )
        self.assertEqual([item.loan_id for item in ranked], ["loan-a", "loan-b"])
        self.assertEqual([item.score for item in ranked], [Decimal("1.000000"), Decimal("1.000000")])

    def test_rejects_missing_or_duplicate_required_variables(self) -> None:
        with self.assertRaises(RecommendationInputError):
            score_loan(LoanCandidate("loan-a", {"maxAmount": "amount.high"}), self.preferences)
        with self.assertRaises(RecommendationInputError):
            score_loan(
                LoanCandidate("loan-a", {"maxAmount": "amount.high", "interestRate": "interest.low"}),
                (
                    AnswerPreference("maxAmount", "amount.high", Decimal("0.5")),
                    AnswerPreference("maxAmount", "amount.high", Decimal("0.5")),
                ),
            )

    def test_core_unknown_is_excluded_without_a_score(self) -> None:
        from backend.app.recommendation.engine.scoring import partition_loans

        partition = partition_loans(
            (
                LoanCandidate(
                    "loan-review",
                    {"maxAmount": None, "interestRate": "interest.low"},
                    {"maxAmount": ClassificationState.UNKNOWN},
                ),
            ),
            self.preferences,
        )
        self.assertEqual(partition.ranked, ())
        self.assertEqual(partition.needs_review[0].excluded_reasons, ("maxAmount:unknown",))

    def test_unknown_deposit_attribute_is_neutral_not_zero_score(self) -> None:
        from backend.app.recommendation.engine.scoring import score_loan

        score = score_loan(
            LoanCandidate(
                "loan-neutral",
                {"maxAmount": "amount.high", "depositRequired": None},
                {"depositRequired": ClassificationState.UNKNOWN},
            ),
            (
                AnswerPreference("maxAmount", "amount.high", Decimal("0.6")),
                AnswerPreference("depositRequired", "deposit.required", Decimal("0.4")),
            ),
        )
        self.assertEqual(score.score, Decimal("1.000000"))

    def test_trace_records_neutral_without_penalizing_effective_weight(self) -> None:
        trace = build_recommendation_trace(
            LoanCandidate(
                "loan-neutral",
                {"maxAmount": "amount.high", "depositRequired": None},
                {"depositRequired": ClassificationState.UNKNOWN},
            ),
            (
                AnswerPreference("depositRequired", "deposit.required", Decimal("0.4")),
                AnswerPreference("maxAmount", "amount.high", Decimal("0.6")),
            ),
            data_version="serving.v1",
            config_version="recommendation.v1",
        )
        self.assertEqual(trace.decision, RecommendationDecision.RANKED)
        self.assertEqual(trace.raw_score, Decimal("1.000000"))
        self.assertEqual(trace.effective_weight, Decimal("0.6"))
        self.assertEqual(trace.neutral_variables, ("depositRequired",))
        self.assertEqual(trace.contributions[0].reason, "depositRequired:unknown")
        self.assertTrue(trace.contributions[0].neutral)
        self.assertFalse(trace.contributions[0].included_in_effective_weight)

    def test_trace_excludes_core_unknown_without_score_or_rank(self) -> None:
        trace = build_recommendation_trace(
            LoanCandidate(
                "loan-review",
                {"maxAmount": None, "interestRate": "interest.low"},
                {"maxAmount": ClassificationState.VARIABLE},
            ),
            self.preferences,
            data_version="serving.v1",
            config_version="recommendation.v1",
        )
        self.assertEqual(trace.decision, RecommendationDecision.NEEDS_REVIEW)
        self.assertIsNone(trace.raw_score)
        self.assertIsNone(trace.normalized_score)
        self.assertEqual(trace.ranking_excluded_reasons, ("maxAmount:variable",))

    def test_trace_hash_is_stable_when_preference_input_order_changes(self) -> None:
        candidate = LoanCandidate(
            "loan-a",
            {"maxAmount": "amount.high", "interestRate": "interest.low"},
        )
        first = build_recommendation_trace(
            candidate,
            self.preferences,
            data_version="serving.v1",
            config_version="recommendation.v1",
        )
        second = build_recommendation_trace(
            candidate,
            tuple(reversed(self.preferences)),
            data_version="serving.v1",
            config_version="recommendation.v1",
        )
        self.assertEqual(first.stable_hash, second.stable_hash)
        self.assertEqual(first.contributions, second.contributions)
