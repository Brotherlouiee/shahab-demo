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

## US-06.T04 API and active prototype integration

The versioned detail route is `GET /api/v1/loans/{loanId}`. It receives an
opaque ID, invokes `GetLoanDetails`, and maps only the approved serving detail
through `LoanDetailResponse`. The transport adapter exposes parsed `conditions`
but never `conditions_source_text`, a serving-version identifier, provenance,
approval metadata or internal logo references.

The active Vite prototype uses `src/features/loan-details/` because root `src/`
is still the live application. Its small API client validates the minimal public
shape, turns a typed 404 into a distinct absent-detail state, and never displays
server error text. The React view renders condition strings in list nodes, where
React escapes them as text; it provides loading, absent-detail, safe-error and
retry states under a RTL root. It does not calculate recommendation scores or
fall back to the prototype's hard-coded loan details.
