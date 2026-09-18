"""Regression test for required US-04.T01 conceptual-model documentation."""

from __future__ import annotations

import unittest

from scripts.validate_conceptual_data_model import validate


class ConceptualDataModelTests(unittest.TestCase):
    def test_conceptual_model_documents_all_required_entities(self) -> None:
        self.assertEqual(validate(), [])
