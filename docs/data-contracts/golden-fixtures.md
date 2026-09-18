# Golden contract fixtures — US-02.T05

The versioned fixture file is `data/fixtures/recommendation-contract-fixtures.v1.json`. It is intentionally small and deterministic; it does not contain real bank records, production scores, or recommendation ranks.

| Fixture | Purpose | Expected contract result |
| --- | --- | --- |
| `all-canonical-questions-valid` | One valid canonical answer for every `Q1–Q6`, `S7`, `S8`, `S10`, `S13` | Every answer ID resolves to a known question and semantic answer key |
| `complete-core-and-deposit-values` | Loan with all eight known categories | Eligible for future ranking; no neutral variables |
| `neutral-deposit-attributes` | Same core eligibility with three approved deposit unknowns | Ranking-eligible; three neutral variables; no score asserted yet |
| `core-interest-rate-needs-review` | Unknown interest rate | Not ranking-eligible; `needsReview`; no score asserted |

These fixtures lock contracts and policy boundaries only. `US-08` adds engine golden fixtures with score, trace, ordering, threshold and determinism assertions. Any data-contract or decision-version change requires fixture review and a version update.
