# Loan route inventory — US-09.T06A

This inventory covers every loan-related route reachable from the active Vite application. It records the runtime source of each displayed value and the fail-closed behavior required when a serving contract is absent.

| Route | Purpose | Runtime data source | Safe behavior |
| --- | --- | --- | --- |
| `/loan-results` | Highest, low-compatibility and variable-status result partitions | `POST /api/v1/recommendations` for the active in-memory questionnaire session | A direct visit or refresh has no session and shows a Persian recovery message. It never restores a session from a URL or web storage. |
| `/loan-details?loanId=…` | Facts, conditions and required documents for one loan | `GET /api/v1/loans/{loanId}` from the active `PUBLISHED` loan version | Missing, unpublished or invalid IDs show an empty/error state; no fallback loan is selected. |
| `/compare-loans` | Select real result loans for comparison | The three arrays already returned by the recommendation API | Selection changes presentation only. The browser does not score, classify or manufacture candidates. |
| `/compare-result` | Compare approved facts for selected loans | One `GET /api/v1/loans/{loanId}` per selected real loan | At least two real loans are required. Unknown facts render as “اعلام نشده”, never as an inferred number. |
| `/loan-request` | Show whether an approved application method exists | Recommendation result identities; no application/provider contract currently exists | The page states the exact gap and keeps registration/payment disabled. It does not simulate submission, payment, OTP or success. |
| `/ai-analysis` | Explain one result | Recommendation API reason/exclusion reasons plus the same loan-detail conditions | It identifies the content as engine output, not AI. No external analysis provider is claimed or simulated. |

## Result partitions

The browser renders three server-owned arrays without re-scoring or reordering:

1. `rankedRecommendations`: valid scores at or above `0.5`, descending by score and then ascending by stable loan ID.
2. `lowCompatibilityRecommendations`: valid scores below `0.5`, ascending by score and then ascending by stable loan ID. Every card is labelled “تطابق پایین؛ پیشنهاد اصلی نیست”.
3. `needsReview`: candidates with explicit exclusion reasons, without score or rank.

Only approved answer-conversion coefficients and the one-to-one category membership are used by the server. Numeric values in the mapping matrix are not scoring or display coefficients (decision D-005).

## Data and privacy boundary

Loan names, lenders, facts and conditions come from the active PostgreSQL `PUBLISHED` serving snapshot. Fixture values are limited to automated tests. The opaque questionnaire session ID and answers remain in the active React instance and request bodies; they are not written to the URL, `localStorage` or `sessionStorage`. Recommendation traces and source provenance are not public response fields.

## Known serving gap

The published loan contract has no approved application URL, provider identifier, registration workflow, payment contract or production OTP contract. Therefore `/loan-request` is informational and disabled. Operationalizing an external application flow requires a separately approved provider contract and is not simulated by T06A.
