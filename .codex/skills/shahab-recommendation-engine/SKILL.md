---
name: shahab-recommendation-engine
description: Implement, validate, test, or debug Shahab's data-driven loan recommendation engine using the project questionnaire, matrices, and loan data. Use when changing recommendation logic, data import, matching, scoring, explainability, or related results UI.
---

# Shahab Recommendation Engine

## Purpose and hard boundaries

Build a transparent matcher between user preferences and loan attributes. It is not credit scoring, approval prediction, or a guarantee of loan eligibility. Do not claim a loan is the best, approved, or certain.

## Start here

1. Inspect the app and the source documents under `.agents/documents/`.
2. Read the Markdown and Excel sources as separate artifacts. Run a data audit before coding.
3. Work in a feature branch; do not write directly to `main`.
4. Preserve the existing UI unless a change is needed to integrate the engine.

## Canonical inputs

- Behavioral questionnaire: Q1–Q6, S7, S8, S10, S13.
- Eight ordered loan variables: `maxAmount`, `monthlyInstallment`, `maxRepaymentMonths`, `interestRate`, `depositRequired`, `depositHoldingMonths`, `loanToDepositRatio`, `guaranteeType`.
- The question-to-variable mapping, answer weights, and one-to-one compatibility matrix.
- Loan database and its display-required fields.

Use stable internal IDs. Never use Persian display text or an array index as the data key.

## Required implementation shape

- Create a pure engine, a versioned normalized-data layer, input schema validation, and a data adapter.
- Retain an explainability trace for every result and rejection.
- Parse Persian amounts/percentages/durations into normalized values before categorization.
- Exclude loans missing name, provider, principal conditions, or application information; report why.

## Scoring and candidate discovery

For each category, calculate:

`categoryScore = Σ(questionWeight × answerWeight × compatibilityFactor)`.

Rank categories per variable, then traverse the variable order as a pruned tree. A branch that has no matching loans must stop. For each valid path:

`pathScore = Π(categoryWeight)`

`rawLoanScore = Σ(pathScore)`

Normalize relative to the highest raw score, use the configured threshold (initially 50), and sort only by score descending then stable loan ID ascending. Ties get no commercial secondary rank.

The documents mention both tree matching and sequential filtering: model filtering as the per-level intersection inside the tree. Do not mix unrelated algorithms. If product selects another strategy, make it a separately versioned configuration and test it independently.

## Data integrity rules

Fail the data-validation step for missing IDs, unknown categories, coefficients outside `[0,1]`, malformed ranges, duplicated canonical identifiers, or unapproved conflicts between source files. Document the exact file and cell/row. Do not silently repair mapping weights or reverse an answer order.

Known audit risks include inconsistent mapping totals and different question weights between source tables. A configuration that contains a provisional resolution must state `version`, source references, decision, and approval state. Block production release while it is unapproved.

## UX and edge cases

- Missing answer: block the next step and identify the question.
- No candidates: show an actionable questionnaire revision/expand-search state, not an error.
- No results after a user-applied filter: show a distinct state.
- Many results: preserve all valid results.
- Equal scores: preserve deterministic source order/ID.
- Contradictory preferences: return the closest matches with warnings; do not invent a resolution.
- Use Persian RTL UI and accessible loading/error states.

## Test gate

Before handing off, run data audit, unit tests for parsing/categorization/scoring/tree/ties/threshold, fixtures for all canonical questions, integration edge cases, build/lint/typecheck, and a browser E2E through the questionnaire and results. Include test output and configuration/data version in the PR.

## Hand-off

Report changed files, source and configuration versions, data conflicts, excluded loans and reasons, trace sample, tests run, and any blocker to production. Keep secrets and PII out of commits and logs.
