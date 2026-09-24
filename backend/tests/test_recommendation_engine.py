"""US-08.T01 tests for the pure deterministic recommendation engine."""

import unittest
from decimal import Decimal

from backend.app.recommendation.domain.entities import AnswerPreference, LoanCandidate, RecommendationInputError
from backend.app.recommendation.engine.scoring import rank_loans, score_loan


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
        from backend.app.recommendation.domain.entities import ClassificationState
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
        from backend.app.recommendation.domain.entities import ClassificationState
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
