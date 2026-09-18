# Recommendation data decisions

## Version 1.0.0 — approved 2026-09-18

Machine-readable contract: `data/contracts/recommendation-data-decisions.v1.json`.

### D-001 — interest-rate mapping weight

For `interestRate`, the weight for `Q5` (installment flexibility) is **0.10**. The complete approved mapping is `S13=0.40`, `Q2=0.20`, `Q3=0.15`, `S10=0.15`, `Q5=0.10`; the total is exactly **1.00**. This is a normalized configuration decision, not a modification of the raw source.

### D-002 — neutral unknowns for three deposit attributes

For `depositRequired`, `depositHoldingMonths` and `loanToDepositRatio`, `نامشخص`, `متغیر`, blank and unparseable values are neutral. Neutral means no positive score, no negative score, exclusion from the effective-score denominator, and a required trace reason. Neutral never means a score of zero.

### D-003 — exclusion for unknown core ranking attributes

For `maxAmount`, `monthlyInstallment`, `maxRepaymentMonths` and `interestRate`, the same unknown values exclude the loan from `rankedRecommendations`. The loan belongs in `needsReview`, receives no score or rank, and has a required `rankingExcludedReason`. A future structured, versioned and tested extraction rule may make a value usable; free-text guessing is prohibited.

### D-004 — display metadata is not scoring input

The following source columns are presentation-only and do **not** participate in score calculation, effective weight, ranking eligibility or candidate filtering:

- `نام وام`
- `نام بانک`
- `لوگو بانک`
- `مجموع سود وام`
- `حساب سپرده لازم`
- `شرایط و مقررات`

`شرایط و مقررات` is used later only to build sanitized bullets in the loan-detail view. It is not a scoring feature. Loan/bank names and logos identify the option for the user; they are never recommendation inputs.

## Change control

Changing a decision requires a new `configVersion`, a documented source/owner/reason, updated golden tests, a trace compatibility review, and PR approval. Raw `.unitext` sources remain unchanged.
