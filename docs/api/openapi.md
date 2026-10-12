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

There is currently no public application, payment, real SMS-provider or external analysis-provider endpoint. Clients must expose that absence and must not simulate success.


`bankLogoReference`, when present, is validated at the server boundary and is rendered only as an image URL. It is not a source/provenance reference, HTML fragment or database connection detail. Clients show no substitute logo when it is absent.


## Profile access correction — US-09.T072

- POST /api/v1/account-access/request: JSON phone to opaque challengeId and 120-second expiry; explicit local/test mock only.
- POST /api/v1/account-access/verify: challengeId/code to accessToken, phone and 1800-second expiry; single-use, five attempts.
- POST /api/v1/account-access/logout: revoke bearer capability; 204.
- GET /api/v1/profiles/me: actor's own profile; 404 if no record.
- PUT /api/v1/profiles: allowlisted payload; phone must equal server actor, otherwise 403.
- Unauthenticated GET /profiles/{phone} is removed as a security fix. Clients use /me and bearer authorization.
- Missing/invalid/expired token: 401; disabled service: 503; request quota: 429; invalid payload: 422. Protected successes and expected errors use no-store.
- Existing user_profiles migration reused. Browser caches never authorize. Real production authentication/SMS remains blocked; see ADR 0010.

## Verified first-login profile creation — 2026-10-09

Owner clarification: after entering a phone and successfully verifying mock OTP `123456`, the API creates the actor's `user_profiles` record before issuing access. Requesting a code or submitting an invalid code does not create a profile. Repeated login reuses the record without erasing name, income, job, gender or avatar. Personal-info then updates that same database profile before analysis. Creation failure returns 503 without issuing access; resend a code to retry. Existing migration is reused. Real SMS provider remains deferred until the owner supplies its API key; mock remains explicitly local/test. API tests and a real PostgreSQL HTTP integration test cover creation, persistence and repeat login. Follow-up CI must pass before merge.

## US-09.T081 — Generated complete contract

`python -m scripts.export_api_docs` exports the real contract and matching Postman templates; `--check` fails drift in CI. [Manual testing](manual-testing.md) documents cookie-preserving Swagger/Postman flows. Health schemas are opt-in via `SHAHAB_API_DOCS_INCLUDE_OPERATIONS`; readiness remains token-gated, and production docs remain unavailable. Authenticated paths describe bearer OR HttpOnly account cookie; authenticated history additionally needs the questionnaire creator's proof cookie. Errors describe the actual safe `ErrorResponse`, not FastAPI's default validation payload. All online operation results remain pending in [coverage](coverage.md).


## US-10.T04

عملیات مدیریتی از CLI داخلی محافظت‌شده اجرا می‌شود، نه route HTTP جدید.
OpenAPI عمومی و collection فعلی تغییر ندارند. قرارداد ابزار و هویت مستقل در
../operations/protected-tool.md است؛ OTP مشتری مجوز مدیریتی نمی‌دهد.

## US-11.T02A.2 — انتقال اجرایی هویت

method/path/body/response عمومی ثابت؛ phone در response از accounts، authorization با AccountActor UUID از credential متصل و status تازه DB. profile/history/recommendation بر account ID؛ token phone-only قدیمی بعد از cutover/restart نیازمند ورود مجدد است. TTL فعلی ۱۸۰۰ هنوز باقی؛ C نشست یک‌ساعته را اجرا می‌کند. archive endpoint/UI ساخته نشده.

## US-11.T02B — proof معتبر پرسشنامه

resume/write/recommend نیازمند cookie تصادفی سازنده؛ bound questionnaire همان account active را هم می‌خواهد. invalid/missing/unknown=403 عمومی، valid expired=410؛ 422 validation و output shape ثابت. secret فقط Set-Cookie نه JSON/URL؛ Postman/Swagger jar از POST creation حفظ کند، bearer به‌تنهایی کافی نیست. artifacts دوباره تولید؛ [قرارداد](../security/questionnaire-proof.md).

## US-11.T02C — نشست مشترک یک‌ساعته

verify expiresIn=۳۶۰۰ و cookie Max-Age=۳۶۰۰؛ GET account-access/session expiresIn زمان باقی‌مانده، بدون Set-Cookie/تمدید. logout revoke مشترک، restart/worker تازه credential صحیح را restore می‌کند؛ expiry/revoked/archived deny. method/path/body ثابت؛ Swagger/Postman دوباره تولید. [قرارداد](../security/account-session-lifecycle.md).

## US-11.T02F — API نشان‌شده

GET /api/v1/bookmarks: account bearer/cookie، limit۱..۵۰ و cursor opaque owner-scoped،
items همان card DTO سرور و nextCursor؛ no-store، empty با items[].
PUT /api/v1/bookmarks/{loan_id}: UUID نسخه PUBLISHED و JSON {} یا historyId own-visible
matching snapshot؛ desired saved state، retry بدون duplicate، 204 فقط پس از commit.
DELETE همان مسیر: desired removed visibility برای همان actor، idempotent204 حتی
missing/other association، نه DELETE فیزیکی؛ source/history/profile محفوظ.
Extra owner/phone/score/facts رد422، forged/hidden/missing context404، guest/expired/
archived401 و storage503؛ token مشتری مجوز عملیات نیست.
verify/session اکنون accountId سرور می‌دهند تا cache نسل هم‌شماره جدا بماند؛ response
توصیه authenticated، historyId همان saved run می‌دهد برای refresh بدون score JSON
در history.state. request/scoring/TTL unchanged؛ bearer/proof مثل قبل.
OpenAPI/Postman/inventory generated۱۹ عملیات؛ bookmark body نمونه{} معتبر، نه UUID
خالی. [قرارداد F](../security/account-bookmarks.md) و [checkpoint](../progress/us-11-t02f.md).
