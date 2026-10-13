# پاک‌سازی پاسخ خام — US-11.T02E

## قرارداد و مرز اجرا

PD01: پاسخ کامل/نیمه‌کاره فقط تا expires_at اولیه (۱۸۰۰ ثانیه)؛ raw به history،
analytics، log یا archive کپی نشود. profile و snapshot durable سیاست مستقل دارند.
این فرمان scheduler/انتشار نیست؛ در E هیچ پایگاه دادهٔ کاربر purge نمی‌شود.
T05 باید تناوب job، backlog/خطا/آخرین موفقیت، restore rehearsal و gate پیش از
بازگشایی را اثبات کند. تنها قطع دسترسی به پاسخ expired کافی نیست.

یک batch فقط answers expired را حذف می‌کند؛ session دارای history مستقل از
visible/hidden/account status با state EXPIRED نگه داشته و session فاقد history
حذف می‌شود. metadata مرتبط همان UUID/version/owner/timestamps/state/digest موجود
برای FK/idempotency/evidence به عمر همیشگی snapshot retained؛ digest immutable
محرمانه/قابل‌پیوند است ولی raw secret/answer نیست، نه anonymization. NULL legacy
اعتبار ایجاد نمی‌کند. account/profile/history/item/reason/versions نوشته نمی‌شوند.
بدون DDL، cascade، archive table، JSON تازه، session TTL renewal یا HTTP endpoint.

## preflight و نقش

فقط اپراتور دارای مجوز عملیات روی محیط هدف مشخص؛ credential در secret manager/
environment `SHAHAB_DATABASE_URL`، نه argv/کد/log. account token مشتری مجوز این
CLI نیست. role runtime/cleanup بدون DDL/superuser: SELECT فقط برای clock،
questionnaire_sessions/answers و history linkage؛ DELETE روی answers/session و
UPDATE فقط state نشست. هیچ write روی history/account/profile/version لازم نیست.
provisioning/اجرای production و اثبات role واقعی در T05؛ این PR grant نمی‌دهد.

ابتدا revision برنامه و Alembic را بررسی کنید؛ head فعلی cc11b02c0001 سازگار است.
قبل از نخستین اجرای مجاز روی محیط دارای داده، policy حذف خام/نسخه release و
backup امن با retention کنترل‌شده را ثبت کنید. volume/reset/downgrade لازم نیست.
فرمان dry-run فقط SELECT/count و rollback هنگام close، هیچ seed/reference write:

```bash
python -m scripts.cleanup_questionnaire_sessions
```

در Docker local API از image کد به‌روز و environment موجود:

```bash
docker compose exec api python -m scripts.cleanup_questionnaire_sessions
```

پس از تأیید هدف/مجوز، یک batch پیش‌فرض۱۰۰ (حد سخت۱۰۰۰) را اعمال کنید:

```bash
python -m scripts.cleanup_questionnaire_sessions --apply --batch-size 100 --max-batches 1
```

اجرای bounded چند batch برای محیط مجاز (max-batches از۱ تا۱۰۰۰۰):

```bash
docker compose exec api python -m scripts.cleanup_questionnaire_sessions --apply --batch-size 100 --max-batches 10
```

cutoff فقط clock PostgreSQL؛ پارامتر زمان دلخواه/شناسه/مالک/شماره وجود ندارد.
stdout فقط mode و completed_batches/processed_sessions/deleted_answers/
deleted_sessions/retained_sessions/pending_sessions/pending_answers. صفر processed
در یک batch ممکن است ناشی از row lock باشد، نه backlog صفر. خروج۰ موفق؛ خروج۲
اعمال موفق با کار باقی‌مانده (limit/lock)، خروج۱ خطا با counts batchهای واقعاً
commit‌شده. خطا traceback، DSN، UUID، phone، proof یا answer افشا نمی‌کند.

## هم‌زمانی، شکست و بازیابی

ترتیب expiry/UUID، FOR UPDATE SKIP LOCKED، چند statement ثابت؛ قفل account گرفته
نمی‌شود تا ترتیب account→session endpointها وارونه نشود. expired proof/state
همچنان در DB چک می‌شود؛ Redis فقط metadata با TTL، هیچ پاسخ/digest ندارد. cleanup
از service پس از commit cache را invalidate می‌کند؛ CLI به TTL cache متکی است،
access به Redis اعتماد نمی‌کند. outage Redis نمی‌تواند حذف خام DB را rollback کند.

حذف answer، EXPIRED و حذف unlinked در یک transaction؛ شکست rollback کل همان batch.
batchهای پیش‌تر commit‌شده برنمی‌گردند. پس از رفع علت، همان فرمان bounded و سپس
dry-run counts را تکرار کنید. record linked EXPIRED بدون answer از retry خارج است؛
دیگر snapshot دوباره تولید/امتیازدهی نمی‌شود. raw purge برگشت‌ناپذیر است: revert
کد پاسخ حذف‌شده را احیا نمی‌کند و اجرای کد قدیمی F02 را برمی‌گرداند؛ roll-forward
ترجیح دارد. restore نسخه backup در محیط جدا، purge expired و حفظ archived/hidden/
owner/generation قبل از reopen؛ audit/count بدون داده شخصی. rehearsal کامل در T05.

## اثبات

`test_questionnaire_retention_postgresql` فقط روی PostgreSQL16 disposable CI:
full/partial/empty/unlinked/active، visible snapshot readable، hidden/archive graph
byte-equivalent، retry، failure atomic، دو اتصال held-lock و drain پس از آزادسازی،
dry-run بدون write و counts شکست جزئی. CI موفق مجوز deploy/purge production نیست.


## US-11.T05 — فراخوانی تک‌نوبتی برای زمان‌بند مجاز

پس از آماده‌سازی محیط آزمایشی جدا و تأیید کتبی هدف، فقط مسئول عملیات می‌تواند یک اجرای **بدون حذف** برای دیدن backlog انجام دهد:

```bash
python -m scripts.retention_tick
```

برای اجرای **حذف واقعی فقط در محیطی که از قبل مجوز گرفته** (هیچ فرمانی دیتابیس هدف را خودش انتخاب نمی‌کند):

```bash
python -m scripts.retention_tick --apply --batch-size 100 --max-batches 10
```

هر فراخوانی دقیقاً یک tick است و حداکثر ۱۰ batch را پردازش می‌کند؛ این اسکریپت زمان‌بند خودکار، تضمین عدم اجرای هم‌پوشان چند میزبان یا watcher پیوسته نیست. کد خروج: `0` اجرا کامل یا dry-run، `2` پاک‌سازی انجام‌شده اما backlog باقی است (برای retry/alert)، `1` خطا (هشدار و بررسی علت در کانال امن). JSON فقط count غیرشخصی و نام event دارد؛ exception/credential چاپ نشود. عدم‌وجود pending در یک لحظه الزاماً سلامت دوره‌ای یا رعایت expiry ۳۰ دقیقه‌ای را ثابت نمی‌کند.

در راه‌اندازی تولیدی، scheduler/leader-election، تناوب مبتنی بر SLA مصوب، service role محدود، آستانه backlog/last-success و اعلان واقعی را طبق [checkpoint T05](../progress/us-11-t05.md) پس از provision محیط آزمایشی و آزمون هم‌پوشانی تعیین کنید. رمزنگاری بک‌آپ با کلید و restore فقط در پایگاه‌دادهٔ مجزا انجام شود؛ هیچ دیتابیس یا volume متعلق به کاربر reset نشود.
