# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows Semantic Versioning when production releases begin.

## [Unreleased]

### Added

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
