# Recommendation Result View-Model Contract

## Scope

`US-09.T01` defines the presentation boundary and `US-09.T02` adds its narrow
client transport adapter. Neither task mounts a result page, alters the score,
persists a result or computes a recommendation in the browser.

## Required server read model

The recommendation API response consumed by `US-09.T02` must provide one read model with:

- `dataVersion` and `configVersion`, both non-blank strings;
- `rankedRecommendations`, ordered by the server, where each item has
  `loanId`, `lenderName`, `loanName`, `compatibilityScore` from 0 to 1 and a
  server-provided `compatibilityReason`;
- `needsReview`, where each item has `loanId`, `lenderName`, `loanName` and
  one or more typed `rankingExcludedReasons`.

The client view-model validates and presents these fields. It does not reorder
items, derive a score, convert an unranked item into a ranked item or generate a
financial compatibility reason.

## Presentation rules

- A ranked item may show the exact `compatibilityScore` supplied by the API and
  the server-provided reason.
- A needs-review item has no score or compatibility claim. It receives only a
  generic uncertainty warning plus its typed exclusion codes.
- Each item gets a same-origin, encoded loan-details route:
  `/loan-details?loanId=<encoded loan id>`.
- Labels and warnings are Persian presentation copy; raw questionnaire answers,
  source values, session identifiers and trace hashes are not part of this view
  model.

## Display states

`US-09.T03` defines distinct ranked, needs-review-only, no-candidate and
zero-after-filter presentation states in `docs/recommendation-result-states.md`.

## Live US-09.T06 endpoint

`POST /api/v1/recommendations` accepts **only** `{ "sessionId": "..." }`.
It reads ten complete answers from an active 30-minute PostgreSQL session,
then uses the active approved serving catalogue (102 source-backed members),
D-005 answer-conversion weighted cells and separate one-to-one coefficients.
For each category the server sums `sourceWeightedValue × impactFactor` over the
selected answers. One classified category per loan variable yields one tree
path; its weight is the product of the eight category scores. The three
unclassified deposit variables are excluded from that product; the four core
unclassified variables go to `needsReview` without a score. Raw paths are
normalized against the largest rankable raw path, and the documented 50%
minimum match threshold applies. Ties sort by stable loan ID.

The response is the allowlisted read model above. A missing session returns
404, an expired one 410, incomplete answers 422, and an absent/inconsistent
approved catalogue 503. No session ID, raw answers, source text, coefficients,
or internal trace crosses this public response boundary. Loan detail text is
returned separately as safe condition bullets from the same published member.
The previous binary-category `RecommendLoans.execute` remains for the legacy
US-08 regression contract; the live endpoint calls `RecommendCanonicalLoans`
with source-backed category impacts and never presents its binary score.

## Deferred work

- `US-09.T04`: manual filters, stable sort, accessibility and responsive RTL.
- `US-09.T05`: completed controlled browser journey from the API-client result boundary to safe loan details; live questionnaire/session/API/engine wiring remains `US-09.T06`.
