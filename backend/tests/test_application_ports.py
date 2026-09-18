"""Focused contract tests for the US-03.T03 dependency boundaries."""

from __future__ import annotations

import unittest
from datetime import UTC, datetime

from backend.app.application.ports import Clock, IdGenerator, LoanRepository, RecommendationConfigRepository
from backend.app.domain.loan import LoanReference, RecommendationConfigReference
from scripts.validate_import_boundaries import find_cycles, is_forbidden, validate_repository


class ApplicationPortTests(unittest.TestCase):
    def test_ports_are_runtime_checkable_structural_contracts(self) -> None:
        self.assertTrue(hasattr(LoanRepository, "list_rankable_loans"))
        self.assertTrue(hasattr(RecommendationConfigRepository, "get_approved_config"))
        self.assertTrue(hasattr(Clock, "now"))
        self.assertTrue(hasattr(IdGenerator, "new_id"))
        self.assertEqual(LoanReference("loan-1").loan_id, "loan-1")
        self.assertEqual(RecommendationConfigReference("v1").config_version, "v1")
        self.assertIsNotNone(datetime.now(UTC))

    def test_reverse_dependencies_are_forbidden(self) -> None:
        self.assertTrue(is_forbidden("backend.app.domain.loan", "backend.app.infrastructure.db"))
        self.assertTrue(is_forbidden("backend.app.application.ports", "backend.app.api.v1"))
        self.assertFalse(is_forbidden("backend.app.infrastructure.db", "backend.app.application.ports"))

    def test_cycle_detector_reports_a_cycle(self) -> None:
        self.assertEqual(find_cycles({"a": {"b"}, "b": {"a"}}), [["a", "b", "a"]])

    def test_current_backend_respects_import_boundaries(self) -> None:
        self.assertEqual(validate_repository(), [])
