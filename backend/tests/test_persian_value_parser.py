import unittest
from decimal import Decimal

from backend.app.recommendation.domain.persian_value_parser import (
    normalize_source_text,
    parse_money_tomans,
    parse_months,
    parse_percentage,
    unknown_scalar,
)
from backend.app.recommendation.domain.value_schemas import ParsedScalar, UnknownReason, UnknownScalar


class PersianValueParserTests(unittest.TestCase):
    def assert_scalar(self, result, value, unit):
        self.assertIsInstance(result, ParsedScalar)
        self.assertEqual(result.value, Decimal(value))
        self.assertEqual(result.unit, unit)

    def assert_unknown(self, result, reason):
        self.assertIsInstance(result, UnknownScalar)
        self.assertEqual(result.reason, reason)

    def test_normalizes_persian_arabic_digits_and_separators(self):
        self.assertEqual(normalize_source_text(" ۲۳ ٪ "), "23 %")
        self.assertEqual(normalize_source_text("١٢٫٥"), "12.5")

    def test_parses_grouped_toman_amount(self):
        self.assert_scalar(parse_money_tomans("۷۷,۴۱۹,۴۴۳ تومان"), "77419443", "toman")

    def test_parses_million_and_decimal_billion_source_notation(self):
        self.assert_scalar(parse_money_tomans("۲ میلیارد تومان"), "2000000000", "toman")
        self.assert_scalar(parse_money_tomans("۱/۵ میلیارد تومان"), "1500000000", "toman")

    def test_converts_plain_rial_scalar_to_toman(self):
        self.assert_scalar(parse_money_tomans("۵۰۰ ریال"), "50", "toman")

    def test_parses_percentage_and_months(self):
        self.assert_scalar(parse_percentage("23 ٪"), "23", "percent")
        self.assert_scalar(parse_percentage("۰.۰۱٪"), "0.01", "percent")
        self.assert_scalar(parse_months("36 ماه"), "36", "months")

    def test_explicit_unknowns_are_not_converted_to_zero(self):
        self.assert_unknown(parse_money_tomans("نامشخص"), UnknownReason.UNKNOWN_LABEL)
        self.assert_unknown(parse_percentage("متغیر"), UnknownReason.VARIABLE_LABEL)
        self.assert_unknown(parse_months(" "), UnknownReason.BLANK)

    def test_ranges_and_free_text_remain_unparseable(self):
        self.assert_unknown(parse_money_tomans("50 تا 150 میلیون تومان"), UnknownReason.UNPARSEABLE)
        self.assert_unknown(parse_percentage("بین 2 تا 12 درصد"), UnknownReason.UNPARSEABLE)
        self.assert_unknown(parse_months("یک تا 9 ماه"), UnknownReason.UNPARSEABLE)

    def test_invalid_or_negative_values_remain_unparseable(self):
        self.assert_unknown(parse_money_tomans("-۵ میلیون تومان"), UnknownReason.UNPARSEABLE)
        self.assert_unknown(parse_percentage("23"), UnknownReason.UNPARSEABLE)
        self.assert_unknown(parse_months("12.5 ماه"), UnknownReason.UNPARSEABLE)

    def test_unknown_helper_returns_none_for_parseable_text(self):
        self.assertIsNone(unknown_scalar("23 درصد"))


if __name__ == "__main__":
    unittest.main()
