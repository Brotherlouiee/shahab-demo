# اجرای محافظت‌شدهٔ انتشار نخست T07 از SSH محلی

**وضعیت: طرح آمادهٔ بازبینی؛ هیچ‌یک از تنظیم‌های این سند روی سرور اعمال نشده‌اند.**
این مسیر جایگزین محدود CLI برای نبود authority سازمانی OAuth/MFA است؛ ادعای MFA ندارد. endpoint جدید، تغییر auth مشتری، ایمیج جدید و انتشار مستقیم با SQL یا materializer ندارد. تصمیم مالک برای استفاده از Docker/NGINX/آروان موجود و حذف staging/NetBird/Netlify در [checkpoint](../progress/us-09-t07-live-audit-2026-10-22.md) ثبت شده است.

## ورودی و مقصد ثابت

- مقصد: PostgreSQL سرویس `postgres` در شبکهٔ `shahab-prod_data`، پروژهٔ Compose `shahab-prod` و schema در revision `ff11b02f0001`؛ DB/Redis پورت عمومی ندارند.
- منبع: `.agents/documents/دیتابیس وام های بانکی.unitext` در checkout بازبینی‌شدهٔ همین PR، SHA-256 `598052635954071b192bb43505e572f30ee88efd99b4d5ae757f6d555bfaae45`، parser `loan-source.v1`، ۱۰۲ ردیف.
- config: `1.1.0` از منابع وزن/ضریبِ hash-verified و تصمیم‌های D-001 تا D-005. از fixture یا ورودی JSON اختیاری برای catalogue/config استفاده نمی‌شود.
- سازگاری: commit مستقر `2c1a0acc5ed487b48df5bd87b816277bd41f9b35` جدّ checkout است؛ diff در `backend/app/infrastructure/db/models.py`، migrationها، repository انتشار و builderهای منبع/config تا `main@f9e0732` خالی است. ایمیج API فعلی ابزار CLI را ندارد، اما Python و dependencyها را دارد؛ wrapper کد بازبینی‌شده را read-only mount می‌کند.
- کد import: `t07-prod-official-598052635954-20261022`؛ کد workflow: `t07-prod-official-598052635954-1.1.0`. پیش از اجرا، نبود این دو کد در DB فقط‌خواندنی تأیید شود.

## پیش‌نیاز دسترسی، فقط پس از تأیید تجمیع‌شدهٔ مالک

۱. مطابق تصمیم مالک، فقط هویت SSH موجودِ مالک با UID صفر به‌کار می‌رود. حساب، کلید یا بازبین دوم ساخته نمی‌شود. مالک هر مرحلهٔ editor و admin را جداگانه و صریح اجرا می‌کند؛ audit در هر دو مرحله همان actor واقعیِ اتصال root را ثبت می‌کند. این روش کنترل دو نفره یا اثبات فردی در صورت اشتراک کلید root نیست؛ کنترل دو نفره به آینده موکول شده است. wrapper، policy، checkout و command JSON باید متعلق به root باشند. root از قبل اختیار کامل سرور دارد؛ محدودیت CLI جایگزین حفاظت از خود حساب SSH نیست.

۲. از checkout commit مشخصِ PR #150، `git archive` بسازید، hash archive را در دو سوی انتقال بررسی کنید و آن را در `/home/shahab/t07-reviewed-checkout` با مالک root و مجوز خواندن محدود استخراج کنید. فایل `scripts/run_t07_local_operations.sh` را root-owned در `/usr/local/sbin/shahab-t07-operations` نصب کنید. این artifact جدا از `/home/shahab/app` است؛ Compose و NGINX بازنویسی نمی‌شوند.

۳. policy غیرمحرمانهٔ root-owned `/etc/shahab/operations-operators.json` با mode `0644` و والدهای root-owned/non-writable فقط UID صفر، actor واحد، هر دو نقش `data-editor` و `admin`، و `expiresAt` UTC حداکثر ۲۴ ساعت آینده داشته باشد. نام actor باید شناسهٔ عملیاتیِ همین حساب SSH باشد؛ اگر حساب root مشترک است، audit فرد انسانی را اثبات نمی‌کند. نمونه:

```json
{"schemaVersion":1,"singleOwner":true,"operators":[{"uid":0,"actor":"owner-ssh-root","roles":["data-editor","admin"],"expiresAt":"<UTC-within-24-hours>"}]}
```

۴. یک DB role غیرمالک و فاقد DDL بسازید. grantها فقط همان جدول‌های import/serving/audit و sequence لازمِ fixture `test_operations_tool_postgresql.py` باشند؛ `user_profiles`، پاسخ‌ها، تاریخچه و جدول‌های مشتری مجوز ندارند. password با prompt خصوصی تنظیم شود؛ در history، دستور، PR یا خروجی قرار نگیرد. DSN این نقش فقط در `/etc/shahab/operations-db.env` با مالک root و mode `0600` قرار می‌گیرد. wrapper آن را به کانتینر موقت با **ایمیج API فعلی** تزریق می‌کند؛ اپراتورها به فایل secret و Docker socket دسترسی ندارند. `verify_operations_database_role` پیش از هر عملیات owner/DDL را رد می‌کند.

دستور grant، با اتصال خصوصیِ مسئول DB به **همان دیتابیس پروژه** و پس از بررسی نبود نقش هم‌نام، به این جدول‌ها محدود است. `\password shahab_ops_t07` در نشست تعاملی `psql` رمز را بدون echo تنظیم می‌کند؛ نام دیتابیس در DSN خصوصی از همان اتصال واقعی گرفته می‌شود.

```sql
CREATE ROLE shahab_ops_t07 LOGIN;
GRANT USAGE ON SCHEMA public TO shahab_ops_t07;
GRANT SELECT, INSERT ON data_import_runs, data_source_files, lenders,
  loan_products, loan_product_versions, loan_terms, loan_variables,
  variable_categories, loan_category_assignments, loan_conditions,
  loan_serving_facts, questionnaire_versions, questions, answer_options,
  recommendation_config_versions, question_variable_weights,
  answer_option_weights, answer_category_compatibilities,
  serving_catalogue_versions, serving_catalogue_members,
  operations_imports, operations_versions, audit_events TO shahab_ops_t07;
GRANT SELECT, UPDATE ON operations_workflow_head TO shahab_ops_t07;
GRANT UPDATE ON serving_catalogue_versions TO shahab_ops_t07;
GRANT USAGE, SELECT ON SEQUENCE audit_events_event_order_seq TO shahab_ops_t07;
```

پیش از فعال‌سازی، با همان نقش `verify_operations_database_role` و نداشتن `SELECT` روی `user_profiles` و جداول پاسخ/تاریخچه بررسی شود. فایل sudoers یا حساب SSH جدید ساخته نمی‌شود. مالک wrapper را مستقیماً از نشست root موجود اجرا می‌کند؛ اجرای آن از زمینهٔ sudo رد می‌شود.

۵. JSONهای root-owned در `/etc/shahab/operations-commands/` ساخته شوند؛ هیچ secret، role، actor، source path یا DB URL داخلشان نباشد. محتوای دقیق پیشنهادی:

```text
01-import.json   {"operation":"import","import_id":"t07-prod-official-598052635954-20261022","reason":"ورود منبع رسمی تأییدشده برای T07"}
02-review.json   {"operation":"review","import_id":"t07-prod-official-598052635954-20261022"}
03-prepare.json  {"operation":"prepare","import_id":"t07-prod-official-598052635954-20261022","version_id":"t07-prod-official-598052635954-1.1.0","reason":"آماده‌سازی نسخهٔ منطبق با ممیزی منبع"}
04-approve.json  {"operation":"approve","version_id":"t07-prod-official-598052635954-1.1.0","reason":"تأیید صریح مالک پس از بررسی اختلاف نسخه و شواهد منبع؛ بدون بازبین مستقل"}
05-publish.json  {"operation":"publish","version_id":"t07-prod-official-598052635954-1.1.0","reason":"انتشار نخست پس از تأیید مالک و backup بازیابی‌شده"}
```

wrapper فقط یکی از نام‌های `01-import` تا `05-publish` را می‌پذیرد و فرمان ثابت `python -m scripts.operations_tool --local-owner-operator --command /private/command.json` را با bindهای read-only اجرا می‌کند. چون Dockerfile ایمیج API به‌طور معمول `appuser` دارد، فقط همین کانتینر موقت مدیریتی با `--user 0:0` اجرا می‌شود؛ capها حذف، filesystem خواندنی و `no-new-privileges` فعال‌اند. سرویس API و کاربر آن تغییر نمی‌کنند. UID صفر و policy تک‌مالک هر بار بررسی می‌شوند؛ actor از JSON فرمان گرفته نمی‌شود. هر مرحله باید جداگانه اجرا و نتیجه‌اش بازبینی شود. کدهای command و دلیل در audit پایدار می‌مانند. نسخهٔ ابزار و source پیش از نصب با commit/hash نهایی همین شاخه تطبیق داده شوند.

## ترتیب عملیات و کنترل پس از هر مرحله

پیش از نوشتن، تازه‌بودن backup بررسی شود؛ اگر DB از آخرین backup تغییر کرده، `pg_dump -Fc` تازه با permission خصوصی بگیرید، hash انتقال را مقایسه و آن را در PostgreSQL موقت مستقل restore کنید. backup ساعت `2026-10-22T15:35:30Z` با SHA-256 `4c34dbbc75e3e6549609ef2c6df60681632b50e4792991eb840f10e39244d4ed` در PostgreSQL 16 موقت و بدون شبکه restore شد؛ revision ‏`ff11b02f0001` و کاتالوگ خالی تأیید شدند. backup خصوصی قبلی نیز حفظ است. هیچ‌کدام مجوز overwrite روی DB زنده نیستند. migration یا reset/restart لازم نیست.

از نشست SSH فعلی مالک، یک‌به‌یک `/usr/local/sbin/shahab-t07-operations 01-import`، سپس `02-review` و پس از بررسی `eligible=true`، `accepted=102`، `rejected=0`، `issues=0`، دستور `03-prepare` اجرا شود. مالک diff و head ذخیره‌شده را بررسی و سپس `04-approve` و `05-publish` را جداگانه اجرا کند. نتیجهٔ مبهم/timeout پیش از retry با audit/read-only DB بررسی می‌شود؛ کد و operation به‌صورت کور تکرار نمی‌شوند.

پس از publish، از همان DB متصل به API، head و audit، یک catalogue فعال دارای ۱۰۲ عضو، config فعال `1.1.0` و وام‌های PUBLISHED بازخوانی شوند. سپس API سایت از HTTPS با نشست عادی پرسشنامه برای توصیهٔ موفق و GET جزئیات یکی از همان وام‌ها آزموده شود. اگر OTP واقعی مانع است، mock در production روشن نشود و فقط سناریوی مستقل مجاز API اجرا و محدودیت مرورگر ثبت شود.

## بازگشت

این نخستین انتشار است و نسخهٔ PUBLISHED قبلی برای rollback نسخه‌ای وجود ندارد. خطای پیش از commit باید با تراکنش بی‌اثر بماند. پس از publish، در صورت ایراد، انتشار اصلاحیِ بازبینی‌شده ترجیح دارد. restore backup روی production فقط با مجوز مستقل، توقف کنترل‌شدهٔ مسیرهای نوشتن، backup جدیدِ وضعیت پس از انتشار و تطبیق نوشتن‌های کاربران مجاز است؛ backup قدیمی روی DB زنده overwrite نمی‌شود. این برنامه مجوز restore یا حذف داده نیست.

## نتیجهٔ اجرای تأییدشده

مالک اجرای مدل تک‌مالک را فقط برای PostgreSQL اصلی `shahab-prod` و منبع رسمی ۱۰۲ وام/config `1.1.0` تأیید کرد. backup تازهٔ خصوصی `/home/shahab/backups/t07/shahab-t07-20261022T170011Z-execution.dump` با SHA-256 `b13451a6d238b31ab23c9052e5acb1c194d8334ff5494442ffed9fab832cd3a0` روی PostgreSQL 16 موقت و بدون شبکه بازیابی شد. نصب role محدود، policy و فرمان‌های ثابت انجام گرفت؛ پنج مرحله به‌صورت جداگانه موفق شدند. در دیتابیس متصل به API، کاتالوگ `official-598052635954-1.1.0` با ۱۰۲ عضو و config `1.1.0` فعال است و چهار رویداد audit با actor واقعی واحد ثبت شده‌اند. دو تأییدکنندهٔ مستقل و MFA عملیاتی وجود ندارند.

wrapper استخراج‌شده در سرور در اجرای نخست خطای CRLF داشت و قبل از import رد شد؛ همان فایل پس از تبدیل به LF و بررسی `sh -n` و SHA-256 نصب شد. blob commit `1705f0b` دارای LF است؛ منشأ تبدیل در انتقال مشخص نیست. در تکرار عملیات، پایان‌خط artifact استخراج‌شده را پیش از نصب بررسی کنید. جزئیات API و محدودیت مرورگر در [checkpoint](../progress/us-09-t07-live-audit-2026-10-22.md) ثبت شده است. backup فقط برای بازیابی مشروط نگهداری می‌شود و روی دیتابیس زنده restore نشده است.
