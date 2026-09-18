"""Regression test for the physical 3NF schema specification."""

from __future__ import annotations

import unittest

from scripts.validate_physical_schema_spec import validate


class PhysicalSchemaSpecTests(unittest.TestCase):
    def test_physical_schema_specification_is_complete(self) -> None:
        self.assertEqual(validate(), [])
