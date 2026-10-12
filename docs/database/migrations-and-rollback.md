# Migration و rollback operations — US-04.T02

## قانون عملیاتی

تنها مسیر تغییر schema، Alembic migration نسخه‌دار است. اجرای دستی DDL روی production، تغییر مستقیم data serving یا migrate بدون backup/rollback plan ممنوع است. این runbook در `US-04.T04` با Alembic و تست PostgreSQL واقعی اجرا شده است.

## اجرای محلی ایمن

1. `cp .env.example .env` و همهٔ مقادیر `change-me-local-only` را فقط در فایل محلی جایگزین کن؛ `.env` هرگز commit نمی‌شود.
2. `docker compose up -d --build` را اجرا کن. سرویس API فقط پس از healthy شدن PostgreSQL، `alembic upgrade head` را اجرا می‌کند.
3. liveness محلی: `GET /api/v1/health/live`. readiness فقط با header دارای توکن local قابل بررسی است.
4. توقف با حفظ داده محلی: `docker compose down`. حذف داده فقط با تصمیم صریح: `docker compose down -v`.

## کنترل migration

- migrationها در `alembic/versions/` غیرقابل‌ویرایش و ترتیبی‌اند؛ migration اولیه `f0d0c68db55a` تمام tableهای 3NF مصوب را می‌سازد.
- اجرای دستی: `SHAHAB_DATABASE_URL='postgresql+psycopg://…' alembic upgrade head`.
- rollback آزمایش‌شده: `SHAHAB_DATABASE_URL='postgresql+psycopg://…' alembic downgrade base`.
- تست integration از متغیر جداگانهٔ `SHAHAB_TEST_DATABASE_URL` استفاده می‌کند و هم upgrade روی database خالی، هم نوشتن fixture نماینده و هم downgrade کامل را می‌سنجد.
- CI یک PostgreSQL 16 موقت ایجاد می‌کند؛ credential آن صرفاً test credential است و هیچ secret عملیاتی در workflow یا log قرار نمی‌گیرد.

## مسیر امن expand/contract

1. migration **expand** سازگار: جدول/column/index جدید nullable یا با default امن ایجاد کن.
2. backend سازگار deploy کن که reader قدیم/جدید را تحمل کند؛ health readiness نباید جزئیات schema را افشا کند.
3. backfill idempotent را در job جدا و batchهای کوتاه اجرا کن؛ progress/audit ثبت شود.
4. constraint را پس از اثبات backfill فعال کن؛ serving version فقط بعد approval جابه‌جا شود.
5. در release بعد reader قدیم و سپس field قدیم را با migration **contract** حذف کن.

## rollback و recovery

- هر migration باید `upgrade` و `downgrade` عملی داشته باشد؛ drop یا rename برگشت‌ناپذیر بدون snapshot و ADR مسدود است.
- پیش از migration: snapshot backup، نسخهٔ Alembic فعلی، تعداد rowهای کلیدی و release identifier ثبت می‌شود.
- rollback: backend را به reader سازگار برگردان، downgrade آزمایش‌شده را اجرا کن، integrity/audit/serving version را verify کن؛ اگر data migration lossless نیست، restore از snapshot در محیط جدا و سپس promotion طبق incident runbook لازم است.
- migration failed: transaction را rollback کن، هیچ serving version را publish نکن، event و owner را در audit ثبت کن.

## دسترسی و عملیات PostgreSQL

- role migration فقط در pipeline deploy و محدود به DDL؛ role application فقط DML لازم؛ role read-only برای analytics؛ هیچ role با credential shared در source یا CI log نیست.
- اتصال application با TLS، timeout/pool محدود و secret manager انجام می‌شود. rotation secret بدون commit و با deployment-controlled configuration است.
- backup رمزنگاری‌شده و restore در محیط جدا باید در US-04.T04/T05 اثبات شود. retention backup و RPO/RTO به تصمیم عملیات/حقوقی نیاز دارد و نباید حدس زده شود.

## معیار خروجی مرحله‌های بعد

`US-04.T03`: schema model/constraint declaration و repository port. `US-04.T04`: upgrade/downgrade روی PostgreSQL خالی و fixture. `US-04.T05`: index strategy و `EXPLAIN (ANALYZE, BUFFERS)` با dataset نماینده.

## US-10.T03 — b4d8e1f2a3c5

Add operations_imports, operations_versions, audit_events, operations_workflow_head,
approval_records view and append-only triggers. Previous head a3b7c9d1e2f4.
No existing-row backfill or customer/catalogue mutation. Frozen DDL in migration;
future ORM changes do not rewrite this revision. Upgrade/downgrade proof runs
in the existing disposable PostgreSQL CI job (test_operations_postgresql).
Code rollback leaves additive evidence intact. Destructive schema downgrade needs
verified backup/export and stopped writers; see ../operations/audit-runbook.md.

## US-11.T02A.2 — انتقال اجرایی هویت

aa11b02a2001 expand و aa11b02a2002 contract، parent b4d8e1f2a3c5؛ writers متوقف، backfill مستقل repeatable، cutover و restart همه workerها. rollback قبل از archive/multiple generation lossless؛ پس از آن guard رد می‌کند. [runbook هویت](account-identity-migration-runbook.md) مرجع فرمان و ترتیب است.

## US-11.T02B — proof معتبر پرسشنامه

bb11b02b0001 parent aa11b02a2002، nullable digest و CHECK/immutable trigger؛ هیچ backfill secret ثابت. writers متوقف، upgrade و backend جدید restart، جریان تازه/سوابق قبلی smoke. downgrade داده را حفظ ولی proof را invalid می‌کند؛ binary قدیمی F01 دارد و نباید public reopen شود؛ roll-forward و [runbook امنیت proof](../security/questionnaire-proof.md).
