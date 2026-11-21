import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
IDENTIFIERS = json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text(encoding="utf-8"))
DECISIONS = json.loads((ROOT / "data/contracts/recommendation-data-decisions.v1.json").read_text(encoding="utf-8"))
FIXTURES = json.loads((ROOT / "data/fixtures/recommendation-contract-fixtures.v1.json").read_text(encoding="utf-8"))


class RecommendationContractFixtureTests(unittest.TestCase):
    def test_fixture_versions_match_contract_versions(self):
        self.assertEqual(FIXTURES["contractVersion"], IDENTIFIERS["contractVersion"])
        self.assertEqual(FIXTURES["dataDecisionVersion"], DECISIONS["configVersion"])

    def test_questionnaire_fixture_covers_each_canonical_question_once(self):
        answers = FIXTURES["questionnaire"]["answers"]
        self.assertEqual(list(answers), IDENTIFIERS["questionIds"])
        for question_id, answer_id in answers.items():
            prefix, answer_key = answer_id.split(".", maxsplit=1)
            self.assertEqual(prefix, question_id)
            self.assertIn(answer_key, IDENTIFIERS["questions"][question_id])

    def test_fixture_categories_are_canonical(self):
        category_ids = IDENTIFIERS["categoryIds"]
        for loan in FIXTURES["loanFixtures"]:
            for variable, category_id in loan["categories"].items():
                self.assertIn(category_id, category_ids[variable])

    def test_neutral_fixture_uses_only_approved_neutral_variables(self):
        neutral_variables = set(DECISIONS["unknownPolicies"]["neutralVariables"])
        fixture = next(item for item in FIXTURES["loanFixtures"] if item["fixtureId"] == "neutral-deposit-attributes")
        self.assertEqual(set(fixture["unknowns"]), neutral_variables)
        self.assertTrue(fixture["expected"]["rankingEligible"])
        self.assertEqual(set(fixture["expected"]["neutralVariables"]), neutral_variables)

    def test_core_unknown_fixture_cannot_be_ranked(self):
        excluded = set(DECISIONS["unknownPolicies"]["rankingExclusionVariables"])
        fixture = next(
            item for item in FIXTURES["loanFixtures"] if item["fixtureId"] == "core-interest-rate-needs-review"
        )
        self.assertEqual(set(fixture["unknowns"]), {"interestRate"})
        self.assertIn("interestRate", excluded)
        self.assertFalse(fixture["expected"]["rankingEligible"])
        self.assertTrue(fixture["expected"]["needsReview"])


if __name__ == "__main__":
    unittest.main()
