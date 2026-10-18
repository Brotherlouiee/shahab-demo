# Local full-stack development

The supported local stack is Vite, FastAPI, PostgreSQL, and Redis under Docker
Compose. Docker Desktop (with Compose v2), Node.js 22+, and Git are required.

## Start

1. Copy `.env.example` to the ignored `.env` file and replace the local-only
   placeholder password and readiness token. Never commit `.env`.
2. Start the stack from the repository root:

   ```bash
   docker compose up --build
   ```

3. Open `http://localhost:5173/`. Browser requests to `/api/v1` stay
   same-origin and Vite proxies them to FastAPI inside the Compose network.

The Compose development stack mounts the repository into both Vite and FastAPI.
Frontend changes use Vite hot reload; backend changes under `backend/` restart
Uvicorn automatically. A full image rebuild is only needed after changing
Python dependencies, the Dockerfile, or the database/runtime configuration.

Release image packaging is separate: [T04A.1 image build/run contract](operations/container-images.md)
adds an independent static frontend image on port8080. It does not replace this
Vite development service or change Netlify. The API keeps its root Dockerfile;
Dockerfile-specific context allowlists exclude local secrets and unrelated files.

## Publish the verified local catalogue

On a new local PostgreSQL volume, first inspect the migrated database without
writing serving data:

```bash
docker compose --profile tools run --rm operator python -m scripts.materialize_t05a
```

Confirm the inventory is empty and matches the reviewed official-source audit,
then explicitly publish the verified local catalogue:

```bash
docker compose --profile tools run --rm operator python -m scripts.materialize_t05a \
  --publish \
  --actor-reference local-developer \
  --approval-reason "Reviewed empty local database and official source audit"
```

This operator profile mounts only the required source/config/script directories
read-only. It is not started by ordinary `docker compose up`, and it does not
expose PostgreSQL outside the Compose network.

## Verify

The public liveness endpoint is available both directly and through Vite:

```bash
curl http://127.0.0.1:8000/api/v1/health/live
curl http://127.0.0.1:5173/api/v1/health/live
```

Both must return JSON containing `{"status":"ok"}`. Opening
`http://localhost:8000/` is expected to return 404 because FastAPI intentionally
has no root route.

Run focused local checks with:

```bash
npm run test:vite-proxy
npm run build
```

The complete browser journey now runs without an opt-in skip in the existing
real-API CI suite. It requires a dedicated disposable PostgreSQL database, its
current migrations and local mock OTP; its fixture rejects other database names.
It is not a check to point at your ordinary Compose data. See the
[US-12.T02 test map](testing/us-12-t02.md) for the exact environment and command.
The CI path covers questionnaire → personal-info → OTP → real recommendation
partitions → published details → comparison. It does not send SMS or deploy.

If the Playwright browser CDN is unavailable, point the check at an already
installed Chromium-compatible browser without committing that machine-specific
path:

```powershell
$env:SHAHAB_E2E_BROWSER_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
npx playwright test --config playwright.profile-live.config.mjs tests/profile-live/fullstack-recommendation.spec.mjs
```

On Windows, set `PYTHONUTF8=1` for host-run Python checks so canonical UTF-8
contracts are not decoded with the legacy system code page:

```powershell
$env:PYTHONUTF8 = "1"
npm run quality
```

## Host-run Vite

When FastAPI is already reachable at `127.0.0.1:8000`, `npm run dev` uses that
address by default. To use another local API, set `VITE_DEV_API_PROXY_TARGET` in
the process environment. This value is development-only and must never contain
credentials.

## Stop safely

Use `docker compose down` to stop the stack while preserving PostgreSQL data.
See [the Docker runbook](operations/docker-runbook.md) before any reset.


## Profile development access — US-09.T072

Development Compose passes SHAHAB_PROFILE_MOCK_OTP_ENABLED (default true for the local stack). Direct API execution also enables the mock by default in local/test; explicit SHAHAB_PROFILE_MOCK_OTP_ENABLED=false disables it. The existing demo code is ۱۲۳۴۵۶; no SMS is sent. Staging/production always reject this mock. Never configure a public production deployment as local.

After code update, recreate API with `docker compose up -d --build api`. The original d1a9e71b4c3f profile migration is historical; the current chain ends at ff11b02f0001 and includes account UUID ownership and shared access. For an existing database follow the account migration runbook, including stopped writers/backfill before contract; do not treat automatic startup as a substitute. A valid current SQL-backed account session survives refresh/API restart until its absolute one-hour expiry; revoked/expired credentials require login again. Personal-info now persists before analysis, and failures remain visible/retryable. See ADR 0010.

## ابزار داخلی US-10.T04

python -m scripts.operations_tool --command /private/command.json؛ نیازمند
authority HTTPS معتبر مستقل و PostgreSQL account غیرمالک است. OTP فیک کاربر
جای آن نیست. secrets از محیط خصوصی، نه argument/command.json. راهنمای کامل
در operations/protected-tool.md؛ هیچ سرویس/port/dependency جدیدی ندارد.

## US-11.T02A.2 — انتقال اجرایی هویت

پس از دریافت این نسخه، API writers را توقف و مطابق [runbook حساب](database/account-identity-migration-runbook.md) دو revision را اجرا و همه workerها را دوباره راه‌اندازی کن؛ volume reset لازم نیست. داده قبلی حفظ و memory sessions قدیمی نیازمند ورود مجدد هستند. migration روی DB مالک در این PR اجرا نشده.

## US-11.T02B — proof معتبر پرسشنامه

پس از دریافت T02B، bb11b02b0001 را با توقف writerها و runbook proof اجرا کن؛ sessionهای قدیمی با cookie ثابت نیاز به شروع پرسشنامه جدید دارند، سوابق قبلی حفظ‌اند. [قرارداد](security/questionnaire-proof.md)؛ reset volume یا جعل cookie ممنوع. در این PR DB لپ‌تاپ مالک تغییر نکرده.

## US-11.T02C — نشست مشترک یک‌ساعته

C نیازمند migration cc11b02c0001 و restart همه workerهاست؛ داده قبلی حذف/reset نشود. یک login تازه برای session حافظه‌ای قدیمی لازم؛ سپس restore با باقی‌مانده یک ساعت و logout cross-worker. [runbook](security/account-session-lifecycle.md). روی DB مالک این PR migration اجرا نکرده.

## US-11.T02E — ابزار نگهداری خام

[runbook پاک‌سازی مستقل](operations/raw-answer-retention.md) برای محیط جدا و
`python -m scripts.cleanup_questionnaire_sessions` (dry-run) است؛ اجرای apply روی
داده واقعی تنها طبق مجوز و نقش محدود عملیات. در Docker از فرمان runbook با سرویس
api به‌روز استفاده شود؛ reset volume/downgrade داده برای این اصلاح لازم نیست.

## US-11.T02F — نشان‌شده‌های پایدار

پس از مرج، image/API با migration ff11b02f0001 هماهنگ شود؛ refresh مرورگر به‌تنهایی
schema را نمی‌سازد. runbook migration/backup موجود، بدون reset volume؛ `alembic upgrade
head` فقط روی DB هدف مجاز، سپس recreate/restart کد جدید. GET/PUT/DELETE bookmarks در
Swagger/Postman همان auth/proof/roles مصوب را نگه می‌دارند. [قرارداد و rollback](security/account-bookmarks.md).



## OTP کاوه‌نگار — US-11.T06

پیش‌فرض local/test همان mock است؛ متغیرهای جدید در .env.example خاموش/خالی‌اند.
برای تست اتصال بدون SMS از `python -m unittest backend.tests.test_kavenegar_otp`
استفاده کنید. کلید واقعی برای توسعه/CI لازم نیست. اجرای live به تأیید الگو، مجوز
مالک، PostgreSQL و secrets خصوصی نیاز دارد؛ staging/production mock را نمی‌پذیرند.
[راهنمای کامل](operations/kavenegar-otp.md).
