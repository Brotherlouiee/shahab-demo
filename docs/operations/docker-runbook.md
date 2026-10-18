# Local Docker operations runbook

Independent release images and their isolated build/run harness are documented in
[the T04A.1 contract](container-images.md). Development Compose, its ports, volumes
and reload commands below remain unchanged; no registry account or publishing is
required for that image test.

## Routine commands

Start or rebuild the local stack:

```bash
docker compose up --build
```

Inspect service state and recent logs:

```bash
docker compose ps
docker compose logs --tail 100 api frontend postgres redis
```

Stop containers without deleting PostgreSQL data:

```bash
docker compose down
```

## Health troubleshooting

- PostgreSQL must become healthy before migrations and FastAPI start.
- FastAPI must answer `/api/v1/health/live` before Vite starts.
- Compose publishes Vite on host and container port `5173`. This avoids the
  `4173` range that Windows/Hyper-V can reserve dynamically.
- The API mounts the repository and Uvicorn reloads when a file under
  `backend/` changes. Rebuild the API only after dependency, Dockerfile, or
  runtime-configuration changes.
- A 404 at FastAPI `/` is expected; use the liveness path instead.
- If the browser receives HTML for an API request, confirm it was started through
  the repository Vite config and inspect the `api` and `frontend` logs.
- The `operator` service is an explicit tools profile for reviewed local audit and
  publication commands. It never runs during ordinary stack startup.

## Data safety

The named `postgres_data` volume persists local database state. Do not run
`docker compose down -v`, remove the volume, or reset migrations unless the exact
local target and data-loss impact have been reviewed and explicitly approved.
Never put production exports, database URLs, passwords, or tokens in the repo or
Compose logs.


## Profile access repair — US-09.T072

After update run `docker compose up -d --build api` to apply routes and the development mock flag. No new migration or data publication command; normal startup applies the existing profile migration. Staging/production profile access remains fail-closed pending real authentication.

In the current SQL-backed adapter, refresh/restart alone does not invalidate an unexpired account session. For 401 inspect credential expiry/revocation and account status; for 503 inspect DB readiness/migration and local/test provider configuration. Never bypass ownership or treat browser storage as successful DB persistence. Disabling the mock flag stops mock login but does not replace durable session revocation; use the session lifecycle runbook for access invalidation. Do not roll back to PR #85's unprotected endpoints.

## OTP request failure repair — US-09.T073

An API container created before T072 may lack the new OTP flag. The previous local default then returned 503 even when Python files had reloaded. Local/test now enable the fake provider by default; explicitly setting SHAHAB_PROFILE_MOCK_OTP_ENABLED=false still disables it. Staging/production remain denied regardless of the flag. The fake code is 123456 and no SMS is sent.

After pulling the repair, recreate the API with `docker compose up -d --build --force-recreate api`. This retains the PostgreSQL volume. For a freshly created API network endpoint, restart frontend with `docker compose restart frontend` if its proxy still fails.

Inspect only non-secret configuration: `docker compose exec api python -c "from backend.app.core.config import get_settings; s=get_settings(); print(s.environment.value, s.profile_mock_otp_enabled)"`. Expected local output is `local True`. A missing route (404), unavailable provider (503), or connection failure requires API/proxy checks; do not bypass database persistence.

The account client now uses VITE_SHAHAB_API_BASE_URL consistently with the existing questionnaire client, including logout. Without a configured base it uses /api/v1 via the Compose Vite proxy. Existing local browser/Node tests using mocked API responses cannot demonstrate that this proxy is connected; a separate CI browser job now uses real Vite, FastAPI and PostgreSQL with no route fixtures.

## ابزار داخلی US-10.T04

CLI operations_tool در محیط trusted با secret manager و DB role محدود اجرا
می‌شود؛ account مالک migration برای ابزار رد می‌شود. provider/customer OTP
یکی نیستند. port عمومی اضافه نشده است؛ protected-tool.md مرجع provisioning
مجوز، عدم ذخیره secrets و خاموش‌کردن ابزار بدون حذف volume/audit است.

## US-11.T02A.2 — انتقال اجرایی هویت

برای aa11b02a2001/2 از [runbook هویت](../database/account-identity-migration-runbook.md) استفاده کن؛ stop API پیش از تغییر کلید و recreate همه workerها پس از head. down -v/reset داده ممنوع؛ expand audit/backfill پیش از contract. rollback چند نسل guard دارد، schema قدیمی به‌تنهایی کافی نیست.

## US-11.T02C — نشست مشترک یک‌ساعته

پیش از C writerهای API stop، cc11b02c0001 روی DB منتخب مطابق [runbook](../security/account-session-lifecycle.md)، سپس recreate backend بدون حذف volume. old tokens backfill نمی‌شوند و login تازه لازم؛ rollback credentials را invalid و business facts حفظ می‌کند.

## US-11.T02E — ابزار نگهداری خام

[runbook پاک‌سازی مستقل](raw-answer-retention.md) برای محیط جدا و
`python -m scripts.cleanup_questionnaire_sessions` (dry-run) است؛ اجرای apply روی
داده واقعی تنها طبق مجوز و نقش محدود عملیات. در Docker از فرمان runbook با سرویس
api به‌روز استفاده شود؛ reset volume/downgrade داده برای این اصلاح لازم نیست.

## US-11.T02F — نشان‌شده‌های پایدار

پس از مرج، image/API با migration ff11b02f0001 هماهنگ شود؛ refresh مرورگر به‌تنهایی
schema را نمی‌سازد. runbook migration/backup موجود، بدون reset volume؛ `alembic upgrade
head` فقط روی DB هدف مجاز، سپس recreate/restart کد جدید. GET/PUT/DELETE bookmarks در
Swagger/Postman همان auth/proof/roles مصوب را نگه می‌دارند. [قرارداد و rollback](../security/account-bookmarks.md).



## OTP کاوه‌نگار — US-11.T06

api از قبل env_file: .env دارد؛ هیچ key یا template در Dockerfile/image/frontend
قرار نمی‌گیرد. flags جدید پیش‌فرض false هستند. بعد از تأیید الگو و مجوز مستقل،
secrets را در محیط خصوصی backend ثبت و فقط سرویس api را recreate کنید؛ schema و
volume تغییری نمی‌کنند، down -v و reset لازم نیست. در محیط production public، mock
هرگز فعال نشود. [تنظیمات، تست و خاموش‌سازی](kavenegar-otp.md).
