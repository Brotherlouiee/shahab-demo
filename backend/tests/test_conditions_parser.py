"""US-06.T03 tests for safe plain-text loan-conditions bullets."""

from __future__ import annotations

import unittest

from backend.app.loans.domain.conditions import parse_conditions_bullets


class ConditionsParserTests(unittest.TestCase):
    def test_mixed_markers_and_nested_markers_become_ordered_plain_text(self) -> None:
        self.assertEqual(
            parse_conditions_bullets("• اصل کارت ملی\n  - ۱. چک صیادی \n●\tضامن معتبر"),
            ("اصل کارت ملی", "چک صیادی", "ضامن معتبر"),
        )

    def test_blank_lines_and_empty_input_do_not_create_bullets(self) -> None:
        self.assertEqual(parse_conditions_bullets("\n \r\n  \n"), ())
        self.assertEqual(parse_conditions_bullets(None), ())

    def test_html_is_retained_as_text_not_rendering_instruction(self) -> None:
        bullet = parse_conditions_bullets("• <script>alert(1)</script>\nمدرک معتبر")
        self.assertEqual(bullet, ("<script>alert(1)</script>", "مدرک معتبر"))
