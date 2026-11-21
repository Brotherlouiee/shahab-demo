# ADR-0006: Versioned conceptual PostgreSQL model before ORM

- Status: Accepted
- Date: 2026-09-18
- Task: `US-04.T01`

## Decision

Model the loan catalogue, recommendation configuration, user-session results and data governance as separate bounded contexts before defining ORM classes or migrations. Loan identity is separated from versioned terms; recommendation output points to the exact loan and configuration version. Raw import data remains distinct from typed core/serving data.

## Consequences

The proposed model favors 3NF and explicit states over repeated strings or ambiguous nulls. It does not introduce a `users` table prematurely, nor any persistence runtime. Later schema work must preserve cardinalities and documented invariants or record an ADR.

## Validation and rollback

The conceptual validator verifies required entities and design markers in ERD/dictionary. The next task converts this contract to physical constraints; no rollback operation is needed because no schema or data changed.
