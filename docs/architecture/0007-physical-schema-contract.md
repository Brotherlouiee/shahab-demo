# ADR-0007: 3NF physical schema contract before ORM and migrations

- Status: Accepted
- Date: 2026-09-18
- Task: `US-04.T02`

## Decision

Adopt a PostgreSQL physical-schema contract that separates stable loan identity, immutable loan terms versions, recommendation configuration, session/result data and raw/staging governance data. Unknown/variable/neutral states are explicit and are not represented by undocumented nulls. Numeric financial facts use `numeric`; associations use FK tables rather than repeated strings or JSONB.

## Consequences

The contract preserves 3NF and version reproducibility while keeping raw payload only in staging. It adds no ORM, DDL, migration or persisted data. The next task must translate every declared constraint to ORM/database constraints or document an intentional PostgreSQL-specific implementation.

## Validation and rollback

The specification validator checks required entities, type/constraint markers and migration/rollback obligations. Because there is no physical schema yet, rollback is limited to reverting this documentation commit.
