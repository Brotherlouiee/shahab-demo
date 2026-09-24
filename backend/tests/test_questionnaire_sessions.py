import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from backend.app.questionnaire.domain.configuration import load_questionnaire_configuration
from backend.app.questionnaire.domain.session import (
    CanonicalAnswerValidationError,
    QuestionnaireAnswer,
    QuestionnaireRetentionPolicy,
    QuestionnaireSessionExpiredError,
    new_anonymous_session,
    validate_canonical_answer,
)


class QuestionnaireSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[2]
        cls.configuration = load_questionnaire_configuration(
            root / "data/contracts/questionnaire-configuration.v1.json",
            json.loads((root / "data/contracts/canonical-identifiers.v1.json").read_text(encoding="utf-8")),
        )

    def test_only_canonical_answer_is_accepted(self) -> None:
        self.assertEqual(
            validate_canonical_answer(self.configuration, QuestionnaireAnswer("Q1", "Q1.cash_request")).answer_id,
            "Q1.cash_request",
        )
        with self.assertRaises(CanonicalAnswerValidationError):
            validate_canonical_answer(self.configuration, QuestionnaireAnswer("Q1", "Q2.short_term"))

    def test_expired_session_is_blocked(self) -> None:
        now = datetime(2026, 9, 24, tzinfo=UTC)
        session = new_anonymous_session("v1", QuestionnaireRetentionPolicy(timedelta(minutes=30)), now)
        with self.assertRaises(QuestionnaireSessionExpiredError):
            session.ensure_active(now + timedelta(minutes=30))
