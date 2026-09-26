# Recommendation Result Display States

## Scope

`US-09.T03` defines the display-state contract after the API client has returned
the validated `US-09.T01` view model. It does not implement manual filtering,
sorting, an API request, client-side scoring, persistence or a new result route.

## Separate states

| Situation | `emptyState.kind` | User-facing message | Separate section |
| --- | --- | --- | --- |
| Server ranked one or more options | none | none | `ranked` |
| Server also has incomplete options | may coexist with ranked | no ranking claim | `needsReview` |
| Server has no ranked options but has incomplete options | `needsReviewOnly` | «دادهٔ کافی برای رتبه‌بندی دقیق موجود نیست.» | `needsReview` |
| Server has neither ranked nor review options | `noCandidate` | invite the user to review answers | none |
| A later manual filter removes every server-ranked option | `zeroAfterFilter` | invite the user to change filters | `needsReview` may still appear |

A `needsReview` entry remains score-free. Ranked item score and order are
preserved exactly from the server view model. The contract accepts a filtered
subset only when it remains a subsequence of the server order; it rejects a
reordered or invented item.

## Deferred work

- `US-09.T04`: completed manual lender filtering, stable lender-name display sort, responsive RTL and accessibility contract.
- `US-09.T05`: browser E2E from questionnaire to loan details; `US-09.T06` then completes live session/API/engine integration and preview verification.
