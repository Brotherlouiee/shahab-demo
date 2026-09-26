import json
import unittest
from pathlib import Path

CONFIG_PATH = Path(__file__).parents[2] / "data/contracts/recommendation-data-decisions.v1.json"


class RecommendationDataDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_interest_rate_weights_are_approved_and_sum_to_one(self):
        weights = self.config["interestRateQuestionWeights"]
        self.assertTrue(self.config["approved"])
        self.assertEqual(weights["Q5"], 0.1)
        self.assertAlmostEqual(sum(weights.values()), 1.0)

    def test_answer_conversion_is_the_only_authoritative_weight_source(self):
        policy = self.config["weightSourcePolicy"]
        self.assertEqual(self.config["configVersion"], "1.1.0")
        self.assertEqual(policy["decisionId"], "D-005")
        self.assertTrue(policy["authoritativePath"].endswith("تبدیل پاسخ‌ها به وزن‌های عددی.unitext"))
        self.assertFalse(policy["ignoredNumericWeightsMayBeScored"])

    def test_neutral_and_core_exclusion_variables_are_disjoint(self):
        policies = self.config["unknownPolicies"]
        neutral = set(policies["neutralVariables"])
        excluded = set(policies["rankingExclusionVariables"])
        self.assertFalse(neutral & excluded)
        self.assertFalse(policies["neutralBehavior"]["includedInEffectiveWeight"])
        self.assertTrue(policies["rankingExclusionBehavior"]["needsReview"])
        self.assertFalse(policies["rankingExclusionBehavior"]["scoreAssigned"])

    def test_every_nonempty_source_column_has_one_non_scoring_or_scoring_role(self):
        roles = self.config["sourceColumnRoles"]
        scoring = set(roles["scoring"])
        display_only = set(roles["displayOnly"])
        self.assertFalse(scoring & display_only)
        self.assertEqual(len(scoring), 8)
        self.assertIn("نام وام", display_only)
        self.assertIn("نام بانک", display_only)
        self.assertIn("لوگو بانک", display_only)
        self.assertIn("شرایط و مقررات", display_only)
        self.assertFalse(self.config["displayOnlyBehavior"]["participatesInScoring"])
        self.assertFalse(self.config["displayOnlyBehavior"]["participatesInRankingEligibility"])


if __name__ == "__main__":
    unittest.main()
