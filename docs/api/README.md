# API documentation

قراردادهای نسخه‌دار API، مدل خطا، authentication/authorization و نمونه‌های OpenAPI در US-03 و داستان‌های مصرف‌کننده ثبت می‌شوند. هیچ قرارداد API از روی JSX یا دادهٔ خام استنتاج نمی‌شود.

## US-06.T02 loan response schemas

LoanSummaryResponse and LoanDetailResponse map only allowlisted facts from the
approved serving-catalogue domain models. The schemas reject extra fields and
use camel-case JSON names. They deliberately omit source hashes, serving version,
approval data, raw conditions and internal logo references. A router is added
only in a later API integration task.
