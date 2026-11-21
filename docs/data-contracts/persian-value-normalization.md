# Persian value normalization — US-02.T02

## Contract boundary

The pure parser modules under `backend/app/recommendation/domain/` normalize approved scalar notation only. They have no FastAPI, database, React, file-import, scoring, or category-assignment dependency. Their typed output is either a `ParsedScalar(value, unit, raw)` or an `UnknownScalar(reason, raw)`.

## Approved scalar formats

| Value | Output unit | Examples |
| --- | --- | --- |
| Money | `toman` | `۷۷,۴۱۹,۴۴۳ تومان`, `۲ میلیارد تومان`, `۱/۵ میلیارد تومان` |
| Rate | `percent` | `23 ٪`, `۰.۰۱٪` |
| Duration | `months` | `36 ماه` |

The parser accepts Persian, Arabic-Indic, and ASCII digits. A bare rial scalar is converted to toman by dividing by 10. A single slash between short digits immediately before a magnitude unit is the source convention for a decimal (`۱/۵ میلیارد` = 1.5 billion); slash-separated long values remain grouping separators.

## Unknown and ambiguous input

`نامشخص`, `متغیر`, blank input, malformed values, ranges, and explanatory prose do not become zero or an inferred category. They are represented as typed unknowns. Whether an unknown is neutral or ranking-excluding is a separate `US-02.T04` data-decision policy and must be traceable later.

Examples deliberately left unparseable: `50 تا 150 میلیون تومان`, `بین 2 تا 12 درصد`, `یک تا 9 ماه`, and conditions text. A later importer may extract structured alternatives only through explicit, versioned, tested rules; it must not guess from prose.

## Test command

Run `python -m unittest discover -s backend/tests -p "test_*.py"`. The test suite covers digit normalization, money/rial/percent/month conversion, unknown labels, ranges, malformed values, and negative inputs.
