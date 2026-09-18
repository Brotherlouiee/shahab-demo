# Migration و rollback operations — US-04.T02

## قانون عملیاتی

تنها مسیر تغییر schema، Alembic migration نسخه‌دار است. اجرای دستی DDL روی production، تغییر مستقیم data serving یا migrate بدون backup/rollback plan ممنوع است. این runbook پیش‌شرط `US-04.T04` است؛ دستور اجرایی Alembic پس از ایجاد migration واقعی افزوده می‌شود.

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
