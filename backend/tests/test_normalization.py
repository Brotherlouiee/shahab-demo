from __future__ import annotations

import unittest

from backend.app.data_pipeline.domain.normalization import (
    NormalizationState,
    normalize_deposit_required,
    normalize_guarantee_type,
    normalize_numeric_variable,
    normalize_variable,
)


class NormalizationTests(unittest.TestCase):
    def test_numeric_categories_and_persian_digits(self) -> None:
        self.assertEqual(normalize_numeric_variable("interestRate", "۱۵ درصد").category_id, "rate_15_20")
        self.assertEqual(normalize_numeric_variable("maxRepaymentMonths", "12 ماه").category_id, "term_6_12m")
        self.assertEqual(normalize_numeric_variable("depositHoldingMonths", "۳ ماه").category_id, "holding_1_3m")
        self.assertEqual(normalize_numeric_variable("loanToDepositRatio", "۲۰۰٪").category_id, "ratio_100_200")

    def test_shared_boundaries_belong_to_the_earlier_matrix_row(self) -> None:
        self.assertEqual(normalize_numeric_variable("maxAmount", "۵۰ میلیون تومان").category_id, "amount_0_50m")
        self.assertEqual(
            normalize_numeric_variable("monthlyInstallment", "۵۰۰۰۰۰۰ تومان").category_id, "installment_5_15m"
        )
        self.assertEqual(normalize_numeric_variable("interestRate", "۴٪").category_id, "rate_0_4")

    def test_matrix_gaps_and_capped_amounts_are_not_inferred(self) -> None:
        self.assertEqual(normalize_numeric_variable("maxRepaymentMonths", "5 ماه").state, NormalizationState.UNMAPPED)
        self.assertEqual(normalize_numeric_variable("interestRate", "۴٫۵٪").state, NormalizationState.UNMAPPED)
        self.assertEqual(normalize_numeric_variable("maxAmount", "۳۶ میلیارد تومان").state, NormalizationState.UNMAPPED)

    def test_ambiguity_is_never_inferred(self) -> None:
        self.assertEqual(normalize_numeric_variable("interestRate", "متغیر").state, NormalizationState.VARIABLE)
        self.assertEqual(
            normalize_numeric_variable("interestRate", "۱۲ تا ۱۵ درصد").state, NormalizationState.UNPARSEABLE
        )

    def test_explicit_text_categories_only(self) -> None:
        self.assertEqual(normalize_deposit_required("دارد").category_id, "deposit_required")
        self.assertEqual(normalize_deposit_required("وابسته به طرح").state, NormalizationState.UNMAPPED)
        self.assertEqual(normalize_guarantee_type("تعهد شخص ثالث").category_id, "thirdPartyUndertaking")
        self.assertEqual(normalize_guarantee_type("تعهدات شخص ثالث").category_id, "thirdPartyUndertaking")
        self.assertEqual(normalize_guarantee_type("تعهدات فردی").category_id, "personalUndertaking")
        self.assertEqual(normalize_guarantee_type("چک و ضامن").state, NormalizationState.UNMAPPED)

    def test_dispatcher_covers_every_approved_variable(self) -> None:
        self.assertEqual(normalize_variable("depositRequired", "ندارد").category_id, "deposit_not_required")
        self.assertEqual(normalize_variable("guaranteeType", "تعهد فردی").category_id, "personalUndertaking")
        with self.assertRaisesRegex(ValueError, "unsupported numeric variable"):
            normalize_variable("notApproved", "۱")
