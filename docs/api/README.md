# API documentation

## مرجع جاری — ممیزی US-12.T01، ۲۰۲۶-۱۰-۱۸

قرارداد ماشینی جاری در [OpenAPI تولیدی](generated/openapi.json) و موجودی [۱۹ عملیات](coverage.md) است؛ [راهنمای دستی](manual-testing.md) همهٔ آن‌ها، از جمله GET/PUT/DELETE نشان‌شده‌ها را پوشش می‌دهد. متن‌های تاریخ‌دار پایین سابقهٔ توسعه‌اند. account UUID و وضعیت DB مالکیت را تعیین می‌کنند؛ نشست حساب عمر مطلق ۳۶۰۰ ثانیه و پرسشنامه TTL مستقل ۱۸۰۰ ثانیه دارد. restore حساب بدون تمدید و با cookie HttpOnly است؛ proof تصادفی سازنده برای resume/write/recommend لازم است. [قرارداد نشست](../security/account-session-lifecycle.md) و [proof](../security/questionnaire-proof.md) بر شرح‌های قدیمی مقدم‌اند. کد ارسال واقعی OTP در PR #133 در SHA مبنای این ممیزی هنوز مرج نشده است؛ تست آنلاین T081 نیز باز است.

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
`dataVersion`, `configVersion`, server-ordered `rankedRecommendations`, ascending
`lowCompatibilityRecommendations`, and score-free `needsReview` entries. The
client validates it before presentation.
A non-2xx or malformed response becomes a generic typed client error; it must not
be converted into a fabricated result or expose the server error body.

## US-09.T06/T06A live endpoint

The implemented `POST /api/v1/recommendations` accepts exactly `{ "sessionId":
"<opaque-id>" }`. An active 30-minute session and complete canonical answer set
are required. It reads the active published PostgreSQL snapshot and returns the
three server-owned result partitions documented in [openapi.md](openapi.md).
Raw answers, session identifiers, trace data and source provenance never enter
the response. Missing configuration or serving data fails closed.

## US-09.T05B serving data boundary

The existing `GET /api/v1/loans/{loanId}` reads only active `PUBLISHED` serving members. `conditions` is an ordered plain-text bullet array derived from the exact conditions record of that loan version; an empty source is `[]`, and an absent/nonmember loan is 404. A storage failure returns the typed 503 envelope. The public allowlist excludes source rows, approval, catalogue/config IDs, recommendation traces, session IDs and raw answers. T05B adds no public recommendation endpoint; that belongs to T06. CI tests do not imply a persistent deployed API; T07 requires URL evidence.

## US-09.T081 — Interactive testing

See [manual testing](manual-testing.md), [operation coverage](coverage.md) and [restricted deployment runbook](../runbook/api-testing.md). The generated OpenAPI/Postman templates list all implemented operations, including opt-in operational documentation. They do not constitute an online deployment. Production docs and existing authentication/ownership rules remain enforced.

