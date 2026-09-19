# Loan catalogue use cases

## US-06.T01 boundary

ListLoans and GetLoanDetails are framework-free read use cases. They use only
the ServingLoanCatalogueRepository port, whose contract permits a repository to
return records from the current approved serving version only. Draft, rejected,
superseded, raw and staging records are outside the port and must never reach
these use cases.

ListLoans returns deterministic summaries sorted by lender name, loan name and
opaque loan ID. GetLoanDetails accepts only a non-empty opaque ID and returns
none for an item absent from the approved serving catalogue. Neither use case
exposes serving-version IDs, source hashes, raw provenance, approval actors or
internal state.

The conditions source text is deliberately retained as plain text in LoanDetail.
US-06.T03 owns parsing it to safe bullets; this task must not render, sanitize
or interpret it. API schemas are US-06.T02 and React integration is US-06.T04.

## Corrective persistence boundary

SqlAlchemyServingLoanCatalogueRepository is the durable read adapter for the
existing PostgreSQL catalogue tables. Its query has an explicit PUBLISHED state
predicate, so draft, raw, staging and superseded data cannot reach the use cases.

## US-06.T03 conditions parser

parse_conditions_bullets preserves source conditions as ordered plain text. It
removes common Persian/ASCII list markers and empty lines only. It never returns
HTML, and a presentation layer must render every bullet as text.
