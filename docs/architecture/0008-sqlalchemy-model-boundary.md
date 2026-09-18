# ADR-0008: SQLAlchemy declarations behind application ports

- Status: Accepted
- Date: 2026-09-18
- Task: `US-04.T03`

## Decision

Use SQLAlchemy 2.x declarative metadata inside `backend/app/infrastructure/db`. Models define reviewed PK/FK/UNIQUE/CHECK constraints and explicit classification/publication states, but do not create an engine, session, DDL or migration. Application continues to depend on `Protocol` ports; infrastructure owns persistence details.

## Consequences

The metadata is the single future Alembic source. Financial values use `numeric`, stable identities use UUID, and loan version terms are one-to-one. PostgreSQL, not SQLite, remains the acceptance oracle for constraint and migration behavior in T04.

## Validation and rollback

Metadata-level tests verify core table and constraint declaration. Rollback removes declarations only; no persisted schema/data exists until the next task.
