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

## Deferred work

- `US-09.T04`: manual filters, stable sort, accessibility and responsive RTL.
- `US-09.T05`: completed controlled browser journey from the API-client result boundary to safe loan details; live questionnaire/session/API/engine wiring remains `US-09.T06`.
