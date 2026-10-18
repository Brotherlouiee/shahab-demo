# Architecture Decision Records

هر تصمیم پایدارِ معماری، داده، امنیت، API، migration یا انتشار باید از قالب `0000-template.md` یک ADR شماره‌دار بسازد. تصمیم‌های پیشنهادی تا تأیید مالک محصول وضعیت `Proposed` دارند و نباید مبنای deploy production شوند.

## فهرست و تقدم نسخهٔ جاری — US-12.T01

دو مجموعهٔ شماره‌گذاری تاریخی وجود دارند: `docs/architecture/0001…0011` و ADRهای `docs/adr/0005…0009`. شمارهٔ تنها مبهم است؛ ارجاع با مسیر کامل باشد. شماره‌ها و سابقه بازنویسی نمی‌شوند. «هنوز اجرا نشده» در ADR قدیمی وضعیت همان task است، نه وضعیت همیشگی main.

| موضوع | تصمیم و مرجع جاری |
| --- | --- |
| لایه‌ها، FastAPI و مرز persistence | [فهرست معماری](../architecture/README.md)، [نقشهٔ ماژول](../architecture/module-map.md) و [SQLAlchemy boundary](../architecture/0008-sqlalchemy-model-boundary.md) |
| نسخهٔ serving | [0005](0005-serving-version-publication.md)؛ adapter حافظه‌ای تاریخی، durable evidence در 0006 و bridge/ابزار در 0007 |
| دفتر تصمیم append-only | [0006](0006-durable-operations-audit.md)؛ approval_records view و exception مستند JSONB |
| ابزار خصوصی عملیات | [0007](0007-protected-operations-tool.md)؛ مجوز مستقل از OTP مشتری |
| هویت نسلی حساب | [0008](0008-account-identity-lifecycle.md)؛ A.1 طراحی، اجرای A.2 و C/F/G در [قرارداد حساب](../database/account-identity-lifecycle.md) و [موجودی DB](../database/README.md) |
| دسترسی و نشست | [معماری 0010](../architecture/0010-profile-access-and-persistence.md) با تقدم اصلاحات US-11؛ [قرارداد یک‌ساعته](../security/account-session-lifecycle.md) |
| snapshot سوابق | [معماری 0011](../architecture/0011-recommendation-history.md)؛ UUID مالک و proof/retention جدید بر phone owner اولیه مقدم‌اند |
| ترتیب refactor/release | [0009](0009-offline-refactor-before-release.md) و سند جامع؛ استثنای آماده‌سازی پیش از Public در PR #132 هنوز مرج‌نشده است و اجرای محدود T01 با دستور صریح مالک انجام می‌شود |

این فهرست تصمیم معماری جدید، پذیرش release یا مجوز deploy نیست. [ممیزی](../release/us-12-t01-documentation-audit.md) SHA و مرز شواهد را مشخص می‌کند.
