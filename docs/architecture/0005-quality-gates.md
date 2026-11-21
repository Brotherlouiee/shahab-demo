# ADR-0005: Reproducible local and CI quality gates

- Status: Accepted
- Date: 2026-09-18
- Task: `US-03.T05`

## Decision

Use Ruff for Python formatting/linting and Mypy for application type checking. Preserve unittest as the lightweight backend test runner. One `npm run quality` command orchestrates every deterministic local check, and GitHub Actions executes the same command with pinned major setup actions on pull requests and `main` pushes.

## Consequences

Formatting checks do not mutate CI files. The AST import-boundary validator and conservative secret scan run in the same gate. Quality tooling is a development extra, not a production runtime dependency. Full SAST/SCA/DAST, integration database tests and deployment checks remain assigned to their later stories.

## Validation and rollback

The quality command must pass locally before this PR. Rollback removes the tooling and workflow only; it changes no product behavior or persisted data.
