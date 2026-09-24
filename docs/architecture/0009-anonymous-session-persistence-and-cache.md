# ADR 0009 — durable anonymous questionnaire sessions with PostgreSQL and Redis

## Status

Implemented in `US-07.T06`; deployment requires PostgreSQL and Redis configuration.

## Context

The questionnaire currently has a 30-minute anonymous-session policy and resumes only in the active browser tab. An in-memory server adapter is insufficient for process restart, horizontal scale, or a controlled 30-minute server-side retention guarantee.

## Decision

- PostgreSQL is the durable, normalized source of truth for `questionnaire_sessions` and `questionnaire_answers`.
- Redis is an optional-but-required-at-deploy cache for active anonymous sessions. It reduces repeated database reads but never becomes the only copy of an answer.
- Every write persists to PostgreSQL first (or atomically with an explicit failure strategy); Redis is updated/invalidated only after that persistence succeeds.
- Cache miss, eviction, restart or Redis outage falls back safely to PostgreSQL. The application must remain correct, though potentially slower, while Redis is unavailable.
- Cache keys are opaque or hashed. Raw answer values, raw session IDs, PII and recommendation outputs are excluded from keys, logs, metrics and traces.
- A TTL-bounded, idempotent cleanup job deletes expired PostgreSQL sessions and their owned answers. Redis entries receive the same or shorter TTL.
- `docs/database/erd.md`, `docs/database/physical-schema-3nf.md`, the data dictionary and migration tests are a single consistency unit. Any later data-model change must update them in the same PR.

## Consequences

- The 30-minute retention promise survives API restart and multi-instance deployment.
- PostgreSQL retains relational integrity: one session has many answers; one answer belongs to exactly one session/question/option; `UNIQUE(session_id, question_id)` prevents duplicates.
- Redis improves load characteristics without weakening privacy or correctness.
- This decision does not add identity, cross-device resume, recommendation scoring, or permanent personal profiles.
