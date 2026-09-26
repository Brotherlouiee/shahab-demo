"""Source-to-serving regression without claiming a production database is populated."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from backend.app.infrastructure.db.models import (
    AnswerCategoryCompatibility,
    AnswerOptionWeight,
    Base,
    LoanCategoryAssignment,
    LoanConditions,
    LoanProductVersion,
    QuestionVariableWeight,
    ServingCatalogueMember,
    ServingCatalogueVersion,
)
from scripts.audit_source_weight_conflicts import build_report as weight_audit
from scripts.audit_t05a_sources import build_report as loan_audit
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config
from scripts.materialize_t05a import audit_database

ROOT = Path(__file__).resolve().parents[2]


class OfficialSourceMaterializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loan = build_manifest()
        cls.config = build_config()
        cls.questionnaire = json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text())
        cls.identifiers = json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text())

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.engine.dispose()

    def _materialize(self, session, *, manifest=None, config=None):
        return materialize_official_sources(
            session,
            loan_manifest=self.loan if manifest is None else manifest,
            config_manifest=self.config if config is None else config,
            questionnaire=self.questionnaire,
            identifiers=self.identifiers,
            actor_reference="reviewed-operator",
            approval_reason="verified official source fixture",
        )

    def test_source_audit_and_authoritative_config_are_complete(self):
        self.assertEqual(
            (len(self.loan["rows"]), len(self.config["questionWeights"]), len(self.config["compatibilities"])),
            (102, 30, 720),
        )
        self.assertEqual(self.config["configVersion"], "1.1.0")
        self.assertEqual(
            weight_audit()["authoritativeWeightSource"], ".agents/documents/تبدیل پاسخ‌ها به وزن‌های عددی.unitext"
        )
        self.assertEqual(len(weight_audit()["nonAuthoritativeDifferences"]), 5)
        audit = loan_audit()
        self.assertEqual((audit["loanCount"], audit["rankableCount"], audit["needsReviewCount"]), (102, 88, 14))
        self.assertEqual(audit["conditionsPresent"], 102)
        self.assertEqual(audit["statesByVariable"]["guaranteeType"]["classified"], 102)

    def test_publishes_all_source_facts_atomically_and_reuses_identical_version(self):
        with Session(self.engine) as session:
            with session.begin():
                first = self._materialize(session)
            self.assertFalse(first.reused)
            self.assertEqual((first.loan_count, first.rankable_count, first.needs_review_count), (102, 88, 14))
            for model, expected in (
                (LoanProductVersion, 102),
                (LoanCategoryAssignment, 816),
                (LoanConditions, 102),
                (QuestionVariableWeight, 30),
                (AnswerOptionWeight, 150),
                (AnswerCategoryCompatibility, 720),
                (ServingCatalogueMember, 102),
            ):
                self.assertEqual(session.scalar(select(func.count()).select_from(model)), expected)
            self.assertTrue(all(record.source_text for record in session.scalars(select(LoanConditions))))
            audit = audit_database(session)
            for key in (
                "missingSourceRows",
                "unexpectedSourceRows",
                "identityMismatchRows",
                "conditionsMismatchRows",
                "incompleteCategoryRows",
                "categoryMismatchCells",
            ):
                self.assertEqual(audit[key], [], key)
            session.commit()
            with session.begin():
                again = self._materialize(session)
            self.assertTrue(again.reused)
            self.assertEqual(session.scalar(select(func.count()).select_from(ServingCatalogueVersion)), 1)

    def test_invalid_source_and_missing_approval_cannot_publish(self):
        invalid = {**self.loan, "sourceFileSha256": "0" * 64}
        with Session(self.engine) as session:
            with self.assertRaises(ValueError), session.begin():
                self._materialize(session, manifest=invalid)
            self.assertEqual(session.scalar(select(func.count()).select_from(ServingCatalogueVersion)), 0)
            session.commit()
            unapproved = {**self.config, "approved": False}
            with self.assertRaises(ValueError), session.begin():
                self._materialize(session, config=unapproved)
            self.assertEqual(session.scalar(select(func.count()).select_from(ServingCatalogueVersion)), 0)

    def test_edited_conditions_or_coefficient_with_original_source_hash_fail_closed(self):
        edited_loan = copy.deepcopy(self.loan)
        edited_loan["rows"][0]["displayFields"]["conditions"] = "edited"
        edited_config = copy.deepcopy(self.config)
        edited_config["compatibilities"][0]["coefficient"] = "0"
        with Session(self.engine) as session:
            for manifest, config in ((edited_loan, self.config), (self.loan, edited_config)):
                with self.assertRaises(ValueError), session.begin():
                    self._materialize(session, manifest=manifest, config=config)
            self.assertEqual(session.scalar(select(func.count()).select_from(ServingCatalogueVersion)), 0)


if __name__ == "__main__":
    unittest.main()
