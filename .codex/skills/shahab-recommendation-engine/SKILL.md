---
name: shahab-recommendation-engine
description: Implement, validate, test, or debug Shahab's data-driven loan recommendation engine using the project questionnaire, matrices, and loan data. Use when changing recommendation logic, data import, matching, scoring, explainability, or related results UI.
---

# Shahab Recommendation Engine

## Canonical project-development guide

Before planning, implementing, refactoring, testing, debugging, migrating data, adding backend capabilities, or deploying this project, read `docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md`. It is the project's continuing source of truth for product rules, architecture, database/data pipeline, security, testing and release gates. If another instruction conflicts with it, stop, identify the conflict and request a documented product decision; do not silently bypass the guide.

At the start or resumption of every user story, task, subtask, bug fix, refactor, test, migration, or deployment, reread the guide's non-negotiable rules, current checkpoint, stage gate, and relevant section before changing code. Read all six `.unitext` sources under `.agents/documents/` for any recommendation, data, questionnaire, results, or database change. Record the guide revision, sections, and source documents read in the task checkpoint; do not begin implementation until this is complete.

## Purpose and hard boundaries

Build a transparent matcher between user preferences and loan attributes. It is not credit scoring, approval prediction, or a guarantee of loan eligibility. Do not claim a loan is the best, approved, or certain.

## Start here

1. Inspect the app and the official `.unitext` source documents under `.agents/documents/`.
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
- Keep the domain and application layers independent of React. Split parsers, importers, repositories, use cases, score calculation, tree traversal, normalization, trace building and presenters into focused modules. Depend on repository/config ports rather than concrete data sources.
- Follow SOLID and clean-code boundaries: one responsibility per module, small public APIs, dependency injection at the composition root, and no business scoring formula inside components or routes.
- Read [architecture guidance](references/architecture.md) before creating a new recommendation module, changing a public contract, or refactoring across layers.

## Scoring and candidate discovery

For each category, calculate:

`categoryScore = Σ(questionWeight × answerWeight × compatibilityFactor)`.

Rank categories per variable, then traverse the variable order as a pruned tree. A branch that has no matching loans must stop. For each valid path:

`pathScore = Π(categoryWeight)`

`rawLoanScore = Σ(pathScore)`

Normalize relative to the highest raw score, use the configured threshold (initially 50), and sort only by score descending then stable loan ID ascending. Ties get no commercial secondary rank.

The documents mention both tree matching and sequential filtering: model filtering as the per-level intersection inside the tree. Do not mix unrelated algorithms. If product selects another strategy, make it a separately versioned configuration and test it independently.

## Approved product decisions

- `interestRate` mapping weight for Q5 is **0.10**. Its variable weights must total exactly `1.00`; record this as a versioned data decision rather than altering raw source files.
- For `depositRequired`, `depositHoldingMonths`, and `loanToDepositRatio`, `متغیر`, `نامشخص`, blank, or uncategorizable values are **neutral**. They contribute neither a positive nor negative score and must be excluded from that loan's effective score denominator. Trace `{ neutral: true, reason }`; never treat neutral as incompatible score zero.
- For the core ranking fields `maxAmount`, `monthlyInstallment`, `maxRepaymentMonths`, and `interestRate`, unknown, variable, blank, or uncategorizable data is **not neutral**. Attempt only a versioned, deterministic extraction from structured source data. If it remains unresolved, exclude the loan from `rankedRecommendations`; put it in `needsReview` with explicit `rankingExcludedReasons` and no score, rank, or compatible-recommendation label.
- Keep `requiredDepositAccount` and other non-scoring display fields separate: unknown display data must not by itself exclude a loan from ranking.
- Loan-details conditions come only from the loan database's `شرایط و مقررات` field. Safely parse line breaks and existing bullets to ordered display bullets; do not hard-code the content or render raw HTML.
- The current frontend route map is immutable unless product explicitly changes it: `/question/3..8 → Q1..Q6`, `/question/9 → S7`, `/question/10 → S8`, `/question/11 → S10`, `/question/12 → S13`. Keep it in one route-map adapter, separate from engine IDs.

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

Run tests in execution order, not only at the end: (1) baseline, (2) import/audit, (3) domain/engine, (4) application use cases with fake repositories, (5) route map and details UI, (6) full E2E/release gate. Do not move to the next layer while its test gate fails.

Add golden tests for Q5 interest weight and total 1.00; three paired loans proving neutral unknown differs from incompatibility and does not create a reward; ordered conditions bullet parsing for `•`, line breaks, nested markers and empty input; and both table-driven and browser tests for every route in the approved route map.

Also test ranking eligibility: an otherwise identical loan with an unknown core field must leave `rankedRecommendations`, appear in `needsReview` with the exact reason, and have no score; an unknown deposit-related field must remain rankable with a neutral trace. If all rankable loans are absent but `needsReview` exists, UI must show the distinct insufficient-data state.

## Security and privacy gate

Read [security guidance](references/security.md) before adding backend, persistence, authentication, external API access, data import/export, or deployment. Treat security as defense in depth, not a claim of absolute invulnerability. Do not store secrets in source/client/logs; enforce least privilege, server-side authorization and schema validation; protect sensitive data in transit and at rest; retain auditable versions of loan/config changes; and block release on exploitable high/critical findings, secret leakage, authorization bypass, confirmed XSS, sensitive-data leakage, or untested restore.

## Backend, PostgreSQL and documentation

The backend stack is FastAPI + PostgreSQL. Read [database and pipeline guidance](references/database-and-pipeline.md) before implementing persistence, APIs, imports, migrations or backend modules. Use FastAPI routers only for HTTP concerns, Pydantic schemas at boundaries, SQLAlchemy 2.x repositories, Alembic-only schema migrations, a normalized PostgreSQL design and an idempotent `raw → staging → core → serving` pipeline. Commit ERD, data dictionary, pipeline/runbook, API and module-map documentation with every related change. Backend code requires meaningful detailed comments/docstrings that explain intent, domain invariant, security/transaction implications and trade-offs; never comments that only paraphrase obvious code.

## Ordered delivery and changelog

Follow the ordered user-story roadmap in `docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md` from US-01 through US-12; do not start a later story while the previous story's tests and documentation gate fail. For every task, write or update the relevant test before or alongside code, run the applicable quality/security checks, make only test-protected refactors, update affected documentation and add a Keep-a-Changelog entry under `Unreleased` with the user-story/task ID, behavior, migration/config impact and related ADR/PR. The project is complete only after US-12's release gate passes.

## Incremental, token-efficient delivery and local stack

Work one small task at a time and persist a start/end checkpoint in `docs/progress/current-state.md`; on a later session, read that checkpoint, CHANGELOG and the active feature only before continuing. Optimize context use by reading only the relevant guide section, ADR, contract, fixture and module—not by skipping tests, security or documentation. Commit each finished task separately with its US/task ID. The local stack is Docker Compose with FastAPI, PostgreSQL and the existing frontend; document and verify Docker, Node LTS, Python 3.12+, locked dependency installation, migration, seed/import, health checks, smoke tests and safe shutdown in `docs/local-development.md` and `docs/operations/docker-runbook.md`.

## Hand-off

Report changed files, source and configuration versions, data conflicts, excluded loans and reasons, trace sample, tests run, and any blocker to production. Keep secrets and PII out of commits and logs.
