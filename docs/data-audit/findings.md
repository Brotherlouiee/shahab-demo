# Data-audit findings — US-02.T03

## Verified run

`scripts/data_audit.py` ran in read-only mode against the six byte-verified UTF-16 LE original files. The complete machine-readable evidence is `docs/data-audit/report.v1.json`.

| Check | Result |
| --- | --- |
| Canonical source files | 6, with SHA-256, byte count, encoding and role recorded |
| Questionnaire | 10 expected rows (`1–8`, `10`, `13`), each with 5 options; no duplicates |
| Loan variables/categories | 8 variables with required 8/6/6/5/2/5/4/3 category counts |
| Question-to-variable weights | All eight variable totals equal 1.00; no invalid weights |
| Answer-weight values | 180 numeric cells, range 0.02–0.65 |
| Compatibility coefficients | 860 numeric cells, range 0–0.95 |
| Loan database | 102 loan rows, 17 columns; 14 non-empty headers and 3 proven-empty trailing headers |

## Recorded issues

1. The source database contains core values that are `نامشخص` or `متغیر`: one interest-rate value, nine maximum-amount values, twelve monthly-installment values and four maximum-repayment-duration values. They remain blocking audit issues until `US-02.T04` records and tests the approved extraction/exclusion policy.
2. The three non-core deposit attributes contain approved unknown/blank values. Their neutral treatment is a data-decision policy, not a parser default.
3. Two loan display names are duplicated (`طرح کارگشا`, `طرح شایان`). A future opaque `loanId`, source fingerprint and approved version are required; display name must not be used as identity.
4. The source labels `نرخ سود` and `نرخ سود وام` are explicitly mapped to the same canonical variable only within the audit alias table. The canonical machine ID remains `interestRate`.

No source data has been changed, normalized, imported, or used for recommendation output in this task.
