# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows Semantic Versioning when production releases begin.

## [Unreleased]

### Changed

- **US-09.T05B (planned):** Added a separate post-T05A server adapter task for an approved PostgreSQL recommendation snapshot, real published loan conditions/details, and durable publication when the database audit proves it missing. Canonical session-to-engine adaptation and the live API/UI journey remain T06; this entry defines work, not completed runtime functionality.

- **US-09.T05A (planned):** Inserted an ordered data and configuration materialization gate before the unchanged T06 live integration. The task consumes the six official sources and approved D-001–D-004 decisions, persists PUBLISHED categories/conditions for existing server use cases, requires audit, provenance and PostgreSQL verification, and introduces no new matching formula or product behavior in this documentation change.


- **US-09.T06 (checkpoint):** documented the missing approved mapping, durable published snapshot and conditions projection that block a truthful live recommendation result. No endpoint, scoring, schema, migration or deployment behavior changed. See the `feature/us-09-live-integration` PR.

### Added

- **US-09.T05**: Added a browser-level recommendation journey contract that exercises the result client, RTL/a11y result surface, manual display controls, typed retry error, and the safe handoff to approved loan-detail conditions through controlled HTTP responses. The live questionnaire/session/API/engine connection remains T06.

- **US-09.T04**: Added server-result presentation controls: lender-only filtering, stable display sorting by lender name, responsive RTL/a11y result markup and typed loading/error states. Score formatting remains display-only; no browser scoring, API/session wiring or static recommendation results were added.

### Changed

- **US-09.T06 (planned)**: Made live end-to-end recommendation delivery a required completion task: the canonical questionnaire session must reach the real recommendation endpoint and server engine, show published loans with server-calculated compatibility percentages, keep `needsReview` score-free, and let the user open safe loan conditions/rules on a testable preview URL. `US-09` is not Done without browser E2E and product-owner manual verification.


- **US-09.T03**: Added a validated display-state contract that distinguishes ranked options, score-free needs-review options, no-candidate results and zero results after later manual filters. It preserves server order and rejects reordered or invented filtered items; no filter/sort computation or result-page wiring is added.

- **US-09.T02**: Added a narrow recommendation-result API client that posts only the opaque active-tab session ID in the JSON body, validates the server read model through the US-09.T01 view model, and turns transport/malformed-response failures into safe typed client errors. No browser scoring, reordering, filtering, persistence or result-page rendering is added.

- **US-09.T01**: Added a presentation-only, validated recommendation result view model and contract for server-calculated results. It preserves server rank/order and score, keeps needs-review entries score-free with a generic uncertainty warning, and builds encoded same-origin detail routes. No API request, React result page, client-side scoring, filtering, persistence or session lookup is added.

- **US-08.T05**: Added bounded golden and property-style regression coverage for deterministic ranking, neutral deposit exclusion, non-classified core review exclusion, score bounds, terminal output completeness and redacted trace determinism.

- **US-08.T04**: Added a framework-free `RecommendLoans` use case that reads one approved immutable recommendation snapshot, returns deterministic ranked and needs-review outputs, and keeps one redacted trace per candidate aligned to the same data/config versions. No FastAPI, React, ORM, database write, session lookup or public result behavior is added.

- **US-08.T03**: Added a pure, versioned and redacted `RecommendationTrace` with deterministic SHA-256 evidence. It records canonical category decisions, effective weight, neutral reasons and core ranking exclusions without session IDs, user identity, free-text answers, API, UI or persistence behavior.

- **US-08.T02**: Added the approved neutral/needs-review policy to the pure engine. Unknown, variable or blank deposit attributes are excluded from the score denominator; unknown core attributes receive no score and are deterministically returned in `needsReview` with typed reasons. No trace/API/UI behavior is added.

- **US-08.T01**: Added a framework-free, deterministic weighted category-matching engine. It validates complete unique positive-weight preferences, rejects missing candidate variables and orders tied results by stable loan ID. It has no database, API, UI, cache, trace, neutral or needs-review policy; those remain later US-08 tasks.

- **US-07.T06**: PostgreSQL now persists anonymous questionnaire sessions and canonical answers as the source of truth; Redis is a hashed-key, best-effort active-session cache with PostgreSQL fallback. A 30-minute expiry cleanup use case removes session-owned answers. No identity, cross-device resume, recommendation result or production deployment is introduced.

- **US-07.T05**: Added browser and API completion-boundary coverage for the behavioural questionnaire: incomplete answers are blocked, canonical body-only answers are persisted through the active-tab session, back navigation preserves the answer, and retryable save failures are announced without progressing. The tests assert no answer/session data appears in the browser URL. No durable PostgreSQL or Redis runtime is introduced; that remains US-07.T06.

- **US-07.T06 (planned)**: Added the required PostgreSQL source-of-truth and Redis cache architecture for anonymous questionnaire sessions, including a 30-minute expiry/cleanup contract, normalized ERD/schema requirements, cache-fallback semantics and mandatory documentation synchronization. No runtime persistence behavior is implemented by this documentation change.

- **US-07.T04**: Connected the behavioural-questionnaire UI to source-traceable canonical questions and a body-only anonymous-session API. The approved retention contract is 30 minutes in the current browser tab; opaque session IDs and answers are not written to browser URLs or web storage. No recommendation score, result, identity or cross-device resume behaviour was added.

- **US-07.T03**: Added anonymous questionnaire session contracts, canonical server-side answer validation, 3NF session/answer migration and an explicit retention-policy boundary. No HTTP answer route, URL answer transport, browser persistence, identity, scoring or automatic deletion policy was introduced.

- **US-01.T01**: Reproducible baseline record and current-state checkpoint; the existing frontend dependency install and production build are verified without changing product behavior.
- **US-01.T02**: Repository, route, dependency, mock, asset, and prototype-risk inventory without changing product behavior.
- **US-01.T03**: Canonical-source inventory with Git/original hash comparison; a source-integrity mismatch is recorded as a blocker for data implementation.
- **US-01.T03a**: Restored all six canonical `.unitext` files using byte-safe Git blobs and verified exact SHA-256/byte-count equality with the original UTF-16 LE sources.
- **US-01.T04**: Added project-document skeletons and an ADR template; no product behavior or data logic changed.
- **US-01.T05**: Added the initial risk and ambiguity register with owners, affected stories, and explicit future gates; no product logic changed.
- **US-02.T01**: Added a versioned canonical identifier contract and static validation for questionnaire IDs, answers, routes, loan variables, categories, and future loan identity.
- **US-02.T02**: Added pure typed schemas and conservative Persian scalar parsers with unit tests; unknown, range, and prose values are never silently inferred.
- **US-02.T03**: Added a read-only canonical-source audit, provenance report, structural evidence, and explicit blocking data issues; no source data changed.
- **US-02.T04**: Added approved, versioned decisions for Q5 interest weight, neutral deposit attributes, core-ranking exclusions, and display-only loan metadata.
- **US-02.T05**: Added versioned golden contract fixtures for canonical answers and complete, neutral, and core-unknown loan-policy boundaries.
- **US-03.T01**: Added staged frontend/backend architecture boundaries, module map, ADR and scaffold validation without moving the active prototype.
- **US-03.T02**: Added a typed FastAPI composition root, safe environment settings, recursive sensitive-field log redaction, dependency providers, focused core tests and local bootstrap runbook.
- **US-03.T03**: Added framework-free domain references, small application ports and AST-based reverse-import/cycle validation without introducing adapters or business behavior.
- **US-03.T04**: Added API v1 composition, typed safe error responses, generated correlation IDs, public minimal liveness and token-gated readiness.
- **US-03.T05**: Added reproducible Ruff/Mypy/test/secret-scan quality gates and a GitHub Actions workflow with no product behavior change.
- **US-04.T01**: Added versioned conceptual ERD, data dictionary, design ADR and documentation validator before physical schema work.
- **US-04.T02**: Added PostgreSQL 3NF physical-schema/constraint specification, migration and rollback operations runbook, ADR and contract validator.
- **US-04.T03**: Added SQLAlchemy 2.x core metadata, explicit database constraints/state enums, transaction boundary port and metadata tests before migrations.
- **US-04.T04**: Added Alembic initial schema migration, bounded SQLAlchemy engine/session composition, Docker Compose local PostgreSQL/API runtime, and real PostgreSQL CI verification of upgrade, fixture write and downgrade.
- **US-04.T05**: Added measured index/query strategy, reversible index migration and PostgreSQL `EXPLAIN (ANALYZE, BUFFERS)` plan-shape verification for selective catalogue lookup.
- **US-05.T01**: Added immutable, content-addressable raw-source capture with SHA-256 integrity, metadata record, size gate and local/test storage adapter; no parsing or serving publication occurs.
- **US-05.T02**: Added strict non-destructive staging validation for encoding, header contract, row width and duplicate source evidence.
- **US-05.T03**: Added conservative normalization and category mapping for all approved loan variables, including typed unmapped outcomes for source-matrix gaps and out-of-range values; no scoring or publication behavior was added.
- **US-05.T04**: Added immutable canonical-row construction, typed rejection evidence, reviewed catalogue diffs, explicit approval records and atomic serving-version publication boundary; no public publication API or scoring behavior was added.
- **US-05.T05**: Added a non-publishing canonical-import preparation command, typed manifest evidence and an operations runbook; no database, approval or serving-pointer mutation can be initiated by the command.
- **US-05.T06**: Added deterministic repeated-import, ambiguous-input and atomic-publication-failure tests; a failed publication demonstrably preserves the prior serving version.
- **US-06.T01**: Added framework-free ListLoans and GetLoanDetails use cases over a serving-only catalogue port; drafts, raw/staging data and provenance internals cannot reach public loan models.
- **US-06.T02**: Added limited, camel-case FastAPI response schemas that allowlist approved public loan facts and reject provenance, raw conditions, internal asset references and extra fields.
- **US-06.T03**: Added a pure plain-text conditions-to-bullets parser; it strips list formatting without generating HTML or interpreting source text as markup.
- **Corrective US-06 dependency**: Added PostgreSQL/SQLAlchemy serving-catalogue adapter with an explicit published-state filter and integration coverage.
- **US-06.T04**: Added the approved-serving loan-detail API endpoint and active RTL API view with loading, absent-detail, safe-error and retry states. Conditions are transported only as parsed plain-text bullets; no migration, recommendation score, raw provenance or internal asset data is exposed.
- **US-06.T05**: Added pinned Playwright Chromium coverage and CI verification for approved-detail RTL rendering, loading, absent-detail, safe retry, hostile condition text and ignored invalid asset/link fields; the public API boundary now also asserts JSON-only, allowlisted behavior.
- **US-07.T01**: Added approved, source-traceable questionnaire configuration for ten canonical questions and fifty stable answers, with a read-only source/identifier validation gate; no route, session, UI, scoring or recommendation behavior changed.
- **US-07.T02**: Added the tested, bidirectional route adapter that maps the immutable `/question/3..12` paths to canonical behavioural question IDs while preserving the prototype's public navigation; no answer/session/API/scoring behavior changed.
