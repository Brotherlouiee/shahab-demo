# ADR-0002: FastAPI core bootstrap with redacted logging

- Status: Accepted
- Date: 2026-09-18
- Task: `US-03.T02`

## Decision

Use FastAPI only as the composition root. Typed settings read `SHAHAB_` environment variables; interactive API documentation is disabled in production. The application logger uses a recursive redaction filter for common sensitive fields before a handler emits a record.

## Consequences

No router, database session, recommendation rule or external provider is wired in this task. Future transport adapters receive only explicit dependency providers. Secrets must be supplied by deployment environment or an approved secret manager, never committed to source or default settings.

## Validation and rollback

The core bootstrap tests verify settings validation, production documentation behavior, explicit app composition, and nested secret redaction. Rollback removes this isolated bootstrap without affecting the active Vite prototype.
