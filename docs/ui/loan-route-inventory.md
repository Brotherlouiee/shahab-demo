# Loan route inventory — US-09.T06A–US-09.T06H

This inventory covers every loan-related route reachable from the active Vite application. It records the runtime source of each displayed value and the fail-closed behavior required when a serving contract is absent.

| Route | Purpose | Runtime data source | Safe behavior |
| --- | --- | --- | --- |
| `/loan-results` | Highest, low-compatibility and variable-status result partitions | `POST /api/v1/recommendations` for the active in-memory questionnaire session | A direct visit or refresh has no session and shows a Persian recovery message. It never restores a session from a URL or web storage. |
| `/loan-details?loanId=…` | Facts, conditions and required documents for one loan | `GET /api/v1/loans/{loanId}` from the active `PUBLISHED` loan version; the lender identity resolves to its verified internal logo asset | Missing, unpublished or invalid IDs show an empty/error state; no fallback loan or external logo is selected. |
| `/compare-loans` | Select real result loans for comparison | The three arrays already returned by the recommendation API | Selection changes presentation only. The browser does not score, classify or manufacture candidates. |
| `/compare-result` | Compare approved facts for selected loans | One `GET /api/v1/loans/{loanId}` per selected real loan | At least two real loans are required. Unknown facts render as “اعلام نشده”, never as an inferred number. |
| `/loan-request` | Show whether an approved application method exists | Recommendation result identities; no application/provider contract currently exists | The page states the exact gap and keeps registration/payment disabled. It does not simulate submission, payment, OTP or success. |
| `/ai-analysis` | Preserve the designed explanation screen without manufacturing an external AI result | The approved engine reason or exclusion reasons for the selected result; no external provider contract | It displays only that server-provided reason and clearly states that the external provider is inactive; its input and submit controls are disabled. It does not present invented analysis or AI success. |

## Result partitions

The browser renders three server-owned arrays without re-scoring or reordering:

1. `rankedRecommendations`: valid scores at or above `0.5`, descending by score and then ascending by stable loan ID.
2. `lowCompatibilityRecommendations`: valid scores below `0.5`, ascending by score and then ascending by stable loan ID. Every card is labelled “تطابق پایین؛ پیشنهاد اصلی نیست”.
3. `needsReview`: candidates with explicit exclusion reasons, without score or rank.

Only approved answer-conversion coefficients and the one-to-one category membership are used by the server. Numeric values in the mapping matrix are not scoring or display coefficients (decision D-005).

## Data and privacy boundary

Loan names, lenders, facts and conditions come from the active PostgreSQL `PUBLISHED` serving snapshot. The controlled logo manifest maps that same canonical lender identity to a content-addressed, URL-safe SVG served by the application; result, detail, comparison-selection and comparison-result cards never hotlink a catalogue logo. Fixture values are limited to automated tests. The opaque questionnaire session ID and answers remain in the active React instance and request bodies; they are not written to the URL, `localStorage` or `sessionStorage`. Recommendation traces and source provenance are not public response fields.

## Known serving gap

The published loan contract has no approved application URL, provider identifier, registration workflow, payment contract or production OTP contract. Therefore `/loan-request` is informational and disabled. Operationalizing an external application flow requires a separately approved provider contract and is not simulated by T06A.

## UI stability — T06C

All three result partitions use the same card structure. Scores are server-owned; `needsReview` shows `نامشخص` in the score position. Display numbers use Persian digits and `/` grouping. Every displayed loan percentage is isolated with `bdi dir="ltr"`; its semantic text remains number-then-sign while an explicit reversed flex row places `٪` visually to the left of the number in Persian RTL, including «نرخ بهره اعلامی». Browser tests require the sign's rendered x-position to be smaller than the number's instead of relying only on DOM text order. Comparison uses the real recommendation identities and approved detail API; it does not recreate loan facts.

## Bank identity anchor — T06H

Result, low-match, needs-review, comparison-selection, comparison-result and detail cards share one `BankIdentity` component. Its internal-only approved logo occupies a fixed box anchored from the card's right/top border. The lender name is right-aligned with the logo, always remains complete on one line and is never ellipsized; the centered loan title has a one-line 200px budget that keeps the four-word reference title visible, ellipsizes only longer titles while retaining the complete API value in `title`/accessible text, and is shifted upward by 20% of its own height. The comparison-result title uses the same 78px title row as the other card headers, so its card-relative vertical coordinate remains within 1px of the results title. Compatibility percentages are 1.2 times the surrounding match text, while declared-interest percentages are unchanged. On comparison-selection cards only, the customer-match row is shifted downward by 20% of its own height. Comparison checkboxes have a fixed right offset independent of either name. When returning from comparison-result, the selected real loan IDs rehydrate the green checkboxes from active-tab React memory only; they are never placed in the URL or web storage. Selection and result lists reserve scroll space for their fixed action bars; the final comparison-result card remains at least 20px from the fixed explanation button. The results controls form the stacking context above the card list, with visible overflow and a small local menu layer, so options remain visible and clickable without disabling the cards or using an arbitrary global z-index. Browser geometry checks compare short and long names and require logo/checkbox offsets to remain within 1px in desktop and mobile layouts.
