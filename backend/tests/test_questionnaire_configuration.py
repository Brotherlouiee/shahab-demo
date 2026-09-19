"""US-07.T01 tests for immutable questionnaire configuration boundaries."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from backend.app.questionnaire.domain.configuration import (
    QuestionnaireConfigurationError,
    load_questionnaire_configuration,
)

ROOT = Path(__file__).parents[2]
CONFIG_PATH = ROOT / "data/contracts/questionnaire-configuration.v1.json"
IDENTIFIERS = json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text(encoding="utf-8"))


class QuestionnaireConfigurationTests(unittest.TestCase):
    def test_configuration_has_every_canonical_required_question_and_answer(self) -> None:
        configuration = load_questionnaire_configuration(CONFIG_PATH, IDENTIFIERS)

        self.assertEqual(configuration.schema_version, "1.0.0")
        self.assertEqual(configuration.questionnaire_version, "behavioral-preference.v1")
        self.assertEqual([question.question_id for question in configuration.questions], IDENTIFIERS["questionIds"])
        self.assertTrue(all(question.required for question in configuration.questions))
        self.assertEqual(sum(len(question.answer_options) for question in configuration.questions), 50)
        for question in configuration.questions:
            self.assertEqual(
                [answer.answer_id for answer in question.answer_options],
                [f"{question.question_id}.{key}" for key in IDENTIFIERS["questions"][question.question_id]],
            )

    def test_configuration_rejects_a_missing_or_reordered_answer(self) -> None:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        payload["questions"][0]["answerOptions"] = list(reversed(payload["questions"][0]["answerOptions"]))
        with tempfile.TemporaryDirectory() as directory:
            malformed = Path(directory) / "questionnaire.json"
            malformed.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(QuestionnaireConfigurationError):
                load_questionnaire_configuration(malformed, IDENTIFIERS)


if __name__ == "__main__":
    unittest.main()
