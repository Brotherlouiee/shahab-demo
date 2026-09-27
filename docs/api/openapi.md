# US-09 recommendation and loan-detail HTTP contract

FastAPI generates the machine-readable OpenAPI document at `/api/v1/openapi.json` only when API documentation is enabled. This page records the security and ordering semantics that JSON Schema alone cannot express.

## `POST /api/v1/recommendations`

Request body (extra fields are rejected):

```json
{ "sessionId": "opaque-active-session-id" }
```

The session must be active and contain all ten canonical answers. A success response contains only:

```json
{
  "dataVersion": "published-version",
  "configVersion": "approved-config-version",
  "rankedRecommendations": [],
  "lowCompatibilityRecommendations": [],
  "needsReview": []
}
```

`rankedRecommendations` contains `loanId`, `lenderName`, `loanName`, a numeric `compatibilityScore` in `[0.5, 1]`, and `compatibilityReason`. It is ordered by score descending and stable loan ID ascending for ties.

`lowCompatibilityRecommendations` has the same shape, but its score is in `[0, 0.5)`, it is ordered by score ascending and stable loan ID ascending for ties, and its reason clearly marks it as a low match that is not a primary suggestion.

`needsReview` contains the real loan identity and `rankingExcludedReasons`; it has no score or rank. The three arrays form a complete, non-overlapping partition of the active published snapshot.

The response excludes session IDs, answers, traces, source rows, coefficients and provenance. The browser must not calculate score, threshold membership or a new ordering.

## `GET /api/v1/loans/{loanId}`

This route returns the allowlisted facts, an optional public `bankLogoReference` HTTP(S) URL, and plain-text conditions of that exact loan in the active `PUBLISHED` version. It cannot select a draft, staging or superseded version. Missing/non-published IDs return the typed `not_found` envelope; unavailable storage returns the typed `service_unavailable` envelope.

There is currently no public application, payment, OTP or external analysis-provider endpoint. Clients must expose that absence and must not simulate success.


`bankLogoReference`, when present, is validated at the server boundary and is rendered only as an image URL. It is not a source/provenance reference, HTML fragment or database connection detail. Clients show no substitute logo when it is absent.
