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
