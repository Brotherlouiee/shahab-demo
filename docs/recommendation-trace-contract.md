# Recommendation Trace Contract

## Scope

US-08.T03 introduces a framework-free RecommendationTrace for one loan candidate.
It is deterministic and versioned. It explains a ranking decision without
storing or exposing a questionnaire session, user identity, free-text answer or
raw source value.

## Contract version 1.0

Each trace contains:

- traceVersion, dataVersion, and configVersion;
- the stable loanId;
- a decision: ranked or needs_review;
- raw and normalized score only for a ranked loan;
- effective weight and the neutral variable IDs;
- typed ranking-exclusion reasons;
- per-variable category-ID evidence, classification state, weight, match,
  neutral flag and reason;
- a SHA-256 stableHash of the canonical redacted payload.

The trace uses canonical category identifiers, never Persian raw source text or
a user's submitted answer. stableHash is reproducible when the same candidate,
preferences and versions are supplied, including when preference input order
differs.

## Policy evidence

- depositRequired, depositHoldingMonths, and loanToDepositRatio with a
  non-classified state are marked neutral, receive an explicit reason, and are
  excluded from effective weight.
- A non-classified core value (maxAmount, monthlyInstallment,
  maxRepaymentMonths, or interestRate) records a typed ranking-exclusion reason,
  returns needs_review, and has neither score nor rank.
- This task creates no HTTP response, persistence table, API endpoint, UI
  display or logging sink. US-08.T04 owns use-case composition and later
  boundaries decide any persistence/display contract.

## Example

A deposit-unknown candidate can produce decision=ranked,
effectiveWeight=0.6, neutralVariables=[depositRequired], and a score from the
remaining classified variables. A core-variable candidate marked variable
produces decision=needs_review and
rankingExcludedReasons=[maxAmount:variable]; no score is present.
