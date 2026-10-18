# Quality gates — US-03.T05

Run the complete local quality gate before opening a PR:

```bash
python -m pip install -e ".[test,quality]"
npm ci
npm run quality
```

`quality` runs formatting verification, Python lint, Python type checking, all backend unit/API tests, canonical/data-architecture validators, secret scan and the existing Vite production build. The GitHub Actions workflow runs the same command on every pull request and each push to `main`.

The secret scan is intentionally conservative: it detects credential-shaped literal assignments, not every sensitive word. It is a defense-in-depth gate and never replaces secret-manager use, code review or the future SAST/SCA gates. Documented test placeholders are the only allowed literals.

Use `npm run format:python` only after reviewing its diff; CI always runs `format:check` and never rewrites files.

## US-11.T02E — raw retention

`python -m unittest backend.tests.test_questionnaire_retention` قرارداد محلی SQLite/
cache/CLI را می‌سنجد؛ اثبات FK/transaction/concurrency فقط
`python -m unittest backend.tests.test_questionnaire_retention_postgresql` در job
PostgreSQL با database **disposable** است. fixture upgrade/downgrade و synthetic
archive دارد؛ هرگز URL کاربر/production را به SHAHAB_TEST_DATABASE_URL ندهید.
suite PG شامل visible/hidden/archived snapshot، full/partial/empty/unlinked/active،
rollback و retry، دو اتصال SKIP LOCKED و CLI dry-run/partial-failure counts است.

## US-11.T02F

API contract۵، client۷، PostgreSQL۶ در job واقعی: owner/device، constraint/upgrade/
rollback guard، atomic failure/retry/race و index؛ real profile-live دو context و
logout cookie/storage/refresh؛ pixel/geometry قبل/بعد saved card و empty در۳۹۰/۱۴۴۰
با baseline detached main مستقل و fixture/fonts یکسان. CI baseline در /tmp، هیچ
snapshot از candidate به baseline بدل نمی‌شود؛ tolerance/mask صفر. artifacts مصنوعی
در us-11-t02f-visual-evidence؛ gateهای قبلی و۱۹ operation Swagger پوشش دارند.

## US-12.T02 — پوشش کامل نسخهٔ جاری

`quality` اکنون همهٔ ۱۵ فایل unit فرانت را با `npm run test:unit` کشف می‌کند؛ loan-details-api و vite-proxy دیگر بیرون گیت نیستند. مسیر full-stack از suite فاقد DB به profile-live واقعی منتقل و با فرم/OTP فعلی هماهنگ شده است، بدون تغییر محصول یا افزایش timeout کلی. [نقشهٔ پوشش/محیط و محدودیت‌ها](us-12-t02.md) مرجع تفکیک unit، pipeline، PostgreSQL، browser و شواهد پس از استقرار است. هر شش check موجود روی head همان PR لازم‌اند.
