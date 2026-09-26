# API documentation

قراردادهای نسخه‌دار API، مدل خطا، authentication/authorization و نمونه‌های OpenAPI در US-03 و داستان‌های مصرف‌کننده ثبت می‌شوند. هیچ قرارداد API از روی JSX یا دادهٔ خام استنتاج نمی‌شود.

## US-06.T02 loan response schemas

LoanSummaryResponse and LoanDetailResponse map only allowlisted facts from the
approved serving-catalogue domain models. The schemas reject extra fields and
use camel-case JSON names. They deliberately omit source hashes, serving version,
approval data and internal logo references.

## US-06.T04 loan detail endpoint

`GET /api/v1/loans/{loanId}` accepts only an opaque loan ID and returns one
approved serving-loan detail. The route has no version, provenance, approval or
asset selector, so a caller cannot choose raw, draft, staging or superseded
data. A missing approved record returns the typed `not_found` envelope; an
unconfigured catalogue returns the typed `service_unavailable` envelope without
database details.

`conditions` is the only public rendering of the approved source conditions.
It is an ordered array of plain-text bullets produced by the US-06.T03 parser;
the original raw field is not serialised. Clients must render each item as text,
never through `innerHTML` or an equivalent unsafe HTML path.


## US-09.T02 recommendation-result client contract

The active result client calls `POST /api/v1/recommendations` with exactly one
JSON body field, `sessionId`. The opaque anonymous-session ID stays in active-tab
memory before this call; it must not appear in a URL, browser storage, log, or
response-derived link. Canonical answers, score inputs, sort/filter state, and
data/config selectors are never client-supplied.

A successful response uses the documented recommendation result read model:
`dataVersion`, `configVersion`, server-ordered `rankedRecommendations`, and
score-free `needsReview` entries. The client validates it before presentation.
A non-2xx or malformed response becomes a generic typed client error; it must not
be converted into a fabricated result or expose the server error body.

## US-09.T06 live endpoint gate

The planned `POST /api/v1/recommendations` must accept exactly `{ "sessionId": "<opaque-id>" }` and return only `dataVersion`, `configVersion`, `rankedRecommendations` and `needsReview`. An active 30-minute session and complete canonical answer set are required. Raw answers, session identifiers, trace data and source provenance must never enter this response. Until an approved answer-to-preference configuration and a published, categorized serving snapshot exist, the endpoint must fail closed; this document does not claim the endpoint is implemented.
