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
