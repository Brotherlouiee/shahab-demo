# راهنمای عملیات داده و آموزش اپراتور — US-10.T05

این راهنما از ریشه مخزن و روی revision بازبینی‌شده اجرا می‌شود. مسیر تغییر داده
ابزار `scripts.operations_tool` است؛ دسترسی به جدول‌ها مجوز ویرایش دستی نیست.
[قرارداد دقیق ابزار](protected-tool.md)، [مجوزها](authorization.md) و
[شواهد audit](audit-runbook.md) مرجع‌اند. هیچ route مدیریتی عمومی وجود ندارد.

## ۱. پیش‌نیاز و مسئولیت

| مسئول | کار لازم پیش از اجرا |
| --- | --- |
| مالک محیط | ثبت محیط/هدف/مجوز عملیات، revision، backup قابل بازیابی و دسترسی محدود سیستم |
| مسئول زیرساخت | migration مصوب با حساب جدا، DB role ابزار غیرمالک، شبکه محدود و secret manager |
| مسئول هویت | authority HTTPS معتبر، audience مستقل، MFA انسان، نقش صریح و امکان ابطال token |
| data-editor | بررسی منبع، import، review و diff نسخه قبل از درخواست تأیید |
| admin | بررسی مستقل شواهد و دلیل، سپس approve/publish یا rollback |
| بازبین فقط‌خواندنی | بررسی head، catalogue و audit با حساب جدا و فیلدهای محدود |

admin مجوز ضمنی import/review ندارد؛ ترکیب editor و admin نیازمند grant صریح
است. service فقط import دارد، حتی با نقش انسانیِ اضافی در پاسخ authority.
OTP مشتری، شماره تلفن و تغییر role در JSON راه ورود اپراتور نیست.

پیش از شروع، سلامت چهار gate commit منتخب، مسیر و محیط DB، migration head و
نسخه config را مسئول محیط تأیید کند. migration حساب runtime نیست و CLI مالک
جدول/superuser/DDL را رد می‌کند. grant حداقلی در قرارداد ابزار و fixture
`backend/tests/test_operations_tool_postgresql.py` مشخص است؛ grant عمومی به
تمام جدول‌ها، استفاده از account API یا دسترسی به profile/answer/history ممنوع.
secretهای `SHAHAB_DATABASE_URL` و `SHAHAB_OPERATIONS_AUTHORITY` فقط در process
مجاز تزریق شوند؛ authority از قرارداد T04 و certificate معتبر استفاده می‌کند.
توکن انسان با prompt بدون echo، یا برای automation از secret manager در
`SHAHAB_OPERATIONS_ACCESS_TOKEN` گرفته می‌شود. secret را در argument، فایل دستور،
shell history، Git، screenshot یا گزارش نگذارید. رمز/token نمونه تولید نکنید.

provider و سرور واقعی هنوز آماده نیستند. تا آماده‌سازی و تأیید محیط، فقط نمونه‌ها
را بخوانید یا تمرین را روی محیط آموزشی جدا اجرا کنید. CI اثبات فعال‌سازی نیست.
آزمون‌های PostgreSQL مخزن upgrade/downgrade و حذف role آزمایشی دارند؛ فقط روی
DB disposable، هرگز روی development مشترک، staging یا production اجرا شوند.

## ۲. پیش‌بررسی فقط‌خواندنی

با حساب read-only جدا محیط را بررسی کنید: نسخه migration از `alembic_version`،
head داخلی، catalogue فعال و config تأییدشده. اجازه SELECT فقط روی جدول‌های
لازم داده شود؛ audit دلیل/هویت داخلی دارد و عمومی یا قابل اشتراک آزاد نیست.
نبود head singleton، catalogue ناسازگار، source/config تأییدنشده یا اتصال نامعلوم
یعنی توقف عملیات و بررسی مسئول محیط؛ دستور SQL تعمیر ننویسید.

نمونه‌های پایین فقط SELECT در transaction فقط‌خواندنی هستند. `import_id` و
`version_id` داخل command **کد متنی اپراتور** هستند؛ columnهای `import_id` و
`version_id` دیتابیس UUID داخلی‌اند. برای یافتن آن‌ها از import_code/version_code
استفاده کنید؛ UUID را به جای کد داخل command نگذارید.

```sql
BEGIN READ ONLY;
SELECT version_num FROM alembic_version;
SELECT h.head_id, v.version_code
FROM operations_workflow_head AS h
LEFT JOIN operations_versions AS v ON v.version_id = h.version_id
WHERE h.head_id = 1;
SELECT c.version_code, c.state, c.active, c.approved_by_reference,
       cfg.version_code AS config_version, cfg.approved,
       count(m.loan_product_version_id) AS member_count
FROM serving_catalogue_versions AS c
JOIN recommendation_config_versions AS cfg ON cfg.config_version_id = c.config_version_id
LEFT JOIN serving_catalogue_members AS m
  ON m.serving_catalogue_version_id = c.serving_catalogue_version_id
WHERE c.active = true
GROUP BY c.version_code, c.state, c.active, c.approved_by_reference,
         cfg.version_code, cfg.approved
LIMIT 10;
COMMIT;
```

publication فعلی فقط extraction رسمی موجود و config `1.1.0`/D-005 را قبول می‌کند.
شناسه عمومی از hash منبع و config ساخته می‌شود و با revisionهای داخلی یکسان نیست.
برای منبع رسمی، catalogue شامل ۱۰۲ وام است؛ ۸۸ بالقوه قابل رتبه‌بندی و ۱۴ نیازمند
بررسی توصیف audit منبع است، نه تعداد پیشنهاد هر پرسشنامه. شمارش واقعی محیط را
از query/API همان محیط بخوانید؛ خالی‌بودن catalogue پیش از اولین publish به‌تنهایی
خطای منبع نیست. catalogue فعال متفاوت یا وام‌های منتشرشده ناسازگار نیازمند
reconciliation بازبینی‌شده‌اند؛ آن‌ها را حذف/غیرفعال یا دوباره import نکنید.

## ۳. import تا انتشار

شناسه‌های `training-official-01` و `training-v1` مثال‌اند. در عملیات واقعی، کد
منحصربه‌فرد و دلیل مصوب همان تغییر را انتخاب و در همه مراحل ثابت نگه دارید.
فایل‌های UTF-8 زیر را در پوشه خصوصی خارج مخزن بسازید. هر بار فقط یک command:

```bash
python -m scripts.operations_tool --command /private/01-import.json
```

این مسیر نمونه است؛ آن را با مسیر خصوصی واقعی عوض کنید. دستورهای بعدی نیز همین
فرمان با نام فایل همان مرحله‌اند. secret در فایل نیست و ابزار source/hash/parser/
rows را از فایل‌های trusted revision می‌سازد؛ manifest دلخواه نمی‌گیرد.

### 01-import.json — data-editor یا service

```json
{"operation":"import","import_id":"training-official-01","reason":"ورود منبع رسمی برای بررسی آموزشی"}
```

خروجی شامل accepted/rejected/issues/eligible و شاهد issue است؛ import انتشار نیست.

### 02-review.json — data-editor

```json
{"operation":"review","import_id":"training-official-01"}
```

فقط با eligible=true و rejected=0 و issues=0 به prepare بروید. needsReview محوری
سیاست مصوب داده است و با rejection واردسازی یکی نیست؛ برای آن score نسازید.
خطای blocking را با حذف issue، تغییر hash یا پاک‌کردن audit حل نکنید.

### 03-prepare.json — data-editor

```json
{"operation":"prepare","import_id":"training-official-01","version_id":"training-v1","reason":"آماده‌سازی نسخه مطابق بررسی منبع رسمی"}
```

خروجی state=draft. بازبین باید پیوند import، hash/parser، diff ذخیره‌شده و head
زمان آماده‌سازی را بررسی کند؛ هیچ diff/source از command پذیرفته نمی‌شود.

### 04-approve.json — admin

```json
{"operation":"approve","version_id":"training-v1","reason":"تأیید پس از بررسی شواهد منبع و اختلاف نسخه"}
```

خروجی state=approved. تأیید به‌تنهایی انتشار نیست و دلیل باید غیرحساس و واقعی باشد.

### 05-publish.json — admin

```json
{"operation":"publish","version_id":"training-v1","reason":"انتشار نسخه تأییدشده در محیط آموزشی مجاز"}
```

خروجی state=published فقط بعد از commit موفق transaction است. سپس head، catalogue
فعال/config/member_count و event publish را دوباره بخوانید. API جزئیات و یک نتیجه
روی session آزمایشی همان محیط باید داده همان catalogue را بخوانند؛ هویت/نشست
مشتری برای smoke جدا از token اپراتور است. گزارش شامل محیط، revision، source/
config version، import/version code، actor، reason، UTC و correlation ثبت‌شده باشد.
credentials و پاسخ خام مشتری را ذخیره/منتشر نکنید. exit 0 جای بازخوانی نیست.

## ۴. خواندن audit و diff

با حساب read-only و SELECT محدود، query نمونه زیر را اجرا کنید. literalهای
training را با کد غیرحساس هدف خود جایگزین کنید؛ در ابزار query از bind parameter
استفاده شود، نه ساختن SQL با متن ورودی. صفحه حداکثر ۱۰۰ event است؛ event_order
آخرین سطر را برای صفحه بعد به جای 0 قرار دهید. فاصله sequence عادی است.

```sql
BEGIN READ ONLY;
SELECT i.import_code, i.source_hash, i.parser_version
FROM operations_imports AS i WHERE i.import_code = 'training-official-01';
SELECT v.version_code, i.import_code, v.diff
FROM operations_versions AS v
JOIN operations_imports AS i ON i.import_id = v.import_id
WHERE v.version_code = 'training-v1';
SELECT a.event_order, a.event_type, i.import_code, v.version_code,
       a.actor_reference, a.reason, a.occurred_at, a.correlation_id,
       a.before_state, a.after_state, a.before_version_id, a.after_version_id
FROM audit_events AS a
JOIN operations_imports AS i ON i.import_id = a.import_id
LEFT JOIN operations_versions AS v ON v.version_id = a.version_id
WHERE i.import_code = 'training-official-01' AND a.event_order > 0
ORDER BY a.event_order LIMIT 100;
COMMIT;
```

review فقط خواندن است و event mutation جدید نمی‌سازد. approval_records نمای
همان approve event است؛ جدول تأیید موازی یا state دستی نسازید. actor از authority
می‌آید، زمان/UUID correlation در سرور ساخته می‌شوند. diff شاهد نسخه‌دار است؛
آن را فقط برای target معین بخوانید، نه predicate عمومی یا export حجیم.

## ۵. rollback داده و نتیجه نامعلوم

rollback فقط target قبلاً منتشرشده و اکنون superseded با approval اصلی را می‌گیرد.
expected_current_version_id باید کد head خوانده‌شده باشد. target دلخواه/draft
یا مقدار expected قدیمی رد می‌شود؛ expected را بدون بررسی فقط عوض نکنید.
تمرین دو revision یک منبع: پس از انتشار v1، با editor نسخه v2 را prepare و با
admin approve/publish کنید؛ سپس با admin به v1 برگردید:

### 06-prepare-v2.json

```json
{"operation":"prepare","import_id":"training-official-01","version_id":"training-v2","reason":"آماده‌سازی بازبینی دوم همان منبع آموزشی"}
```

### 07-approve-v2.json

```json
{"operation":"approve","version_id":"training-v2","reason":"تأیید بازبینی دوم همان منبع آموزشی"}
```

### 08-publish-v2.json

```json
{"operation":"publish","version_id":"training-v2","reason":"انتشار بازبینی دوم همان منبع آموزشی"}
```

### 09-rollback.json

```json
{"operation":"rollback","version_id":"training-v1","expected_current_version_id":"training-v2","reason":"بازگشت آموزشی به نسخه تأییدشده قبلی"}
```

خروجی published برای target؛ head باید v1، event rollback تازه و member_count
همچنان ۱۰۲ باشد. rows/approval تاریخی دست‌نخورده می‌مانند. هر دو revision به
همان public projection immutable منبع/config فعلی وصل‌اند؛ این rollback تغییر
شرایط وام یا بازگردانی میان source/configهای جدید نیست. در رخداد واقعی‌ای که
منبع/config نامعتبر است، این دستور راه درمان عمومی نیست؛ writers را متوقف و
به مسئول داده/امنیت ارجاع دهید تا مسیر نسخه/restore بازبینی‌شده تعیین شود.

| رخداد | اقدام معتبر |
| --- | --- |
| timeout/قطع ارتباط و نتیجه نامعلوم | قبل retry، audit و head و catalogue را با target بخوانید؛ نبود stdout شکست commit را ثابت نمی‌کند |
| retry import یکسان | فقط همان ID/content/actor/reason، شاهد اولیه reuse می‌شود؛ تغییر محتوا/actor/reason زیر همان ID رد می‌شود |
| approve/publish/rollback دوباره یا stale | خودکار retry نکنید؛ state و event را بررسی کنید؛ همه transitionها idempotent نیستند |
| token منقضی، MFA قدیمی، ابطال یا role نامجاز | credential تازه مجاز یا اصلاح grant توسط مسئول هویت؛ OTP/owner DB fallback نیست |
| provider/TLS/redirect/5xx | اجرا متوقف؛ مسئول provider بررسی کند؛ verify TLS را خاموش نکنید |
| DB owner/DDL یا grant ناقص | حساب محدود و grant حداقل توسط مسئول زیرساخت؛ مجوز سراسری ندهید |
| شکست materializer/audit | تراکنش rollback می‌شود؛ با read-only تأیید و علت را بررسی کنید؛ UPDATE دستی ممنوع |
| catalogue drift یا source/config جدید | عملیات متوقف؛ تصمیم داده/نسخه و PR مستقل، نه جعل hash مصوب |

CLI عمداً پیام خطای عمومی و exit 1 می‌دهد؛ این پیام علت دقیق را اثبات نمی‌کند.
خروجی غیرحساس، مرحله، UTC و کد target را برای triage ثبت و با شواهد DB/provider
تطبیق دهید؛ secret environment، token یا stack trace حساس را dump نکنید.

rollback کد یعنی توقف دسترسی اجرای ابزار/revoke credential و بازگشت artifact
بازبینی‌شده، با حفظ داده و audit. downgrade schema rollback داده نیست؛ migration
T03 شواهد را حذف می‌کند و فقط با backup/restore آزموده، توقف writers و مجوز
جدا طبق [audit runbook](audit-runbook.md) مجاز است. این راهنما backup واقعی یا
restore production را انجام نداده؛ rehearsal مربوط به US-11.T05 باقی است.

## ۶. آموزش کوتاه و تحویل اپراتور

تمرین فقط با هویت آموزشی معتبر و DB جدا: مراحل ۱ تا ۹، بازخوانی شواهد و سه
سناریوی زیر. حساب آموزشی/service و credentialها بعد تمرین revoke شوند؛ در
محیط مشترک برای پاک‌سازی، audit/loan را حذف نکنید. fixture TLS فقط CI است و
جای MFA واقعی یا authority عملیاتی نیست.

| سؤال/سناریو | پاسخ و معیار قبولی |
| --- | --- |
| «برای اصلاح نرخ، یک UPDATE در DB بزنم؟» | خیر؛ source/config جدید به تصمیم، نسخه، parser/golden و PR نیاز دارد؛ CLI فعلی تغییر نرخ دلخواه ندارد |
| «admin هستم؛ چرا import رد می‌شود؟» | نقش admin مجوز editor ندارد؛ grant صریح مسئول هویت لازم است، نه role در command |
| publish جواب نداد؛ دوباره Send/اجرا کنم؟ | ابتدا event/head/catalogue را بخوان؛ نتیجه نامعلوم را با شکست اشتباه نگیر |
| rollback با expected قدیمی یا target draft | رد و بدون تغییر head؛ بازبینی تازه لازم است، نه تغییر SQL |
| service می‌خواهد approve کند | رد؛ فقط انسان با MFA و مجوز admin می‌تواند |

تحویل آموزشی ثبت کند: اپراتور/بازبین مسئول، تاریخ UTC، محیط و revision، نسخه
source/config، کدهای target، نتیجه هر مرحله و deny scenario، بازخوانی audit/head/
catalogue و تأیید عدم ویرایش مستقیم DB. خروجی را خصوصی و بدون secret/PII نگه دارید.
خالی‌بودن این فرم یعنی آموزش یا پذیرش محیط هنوز انجام نشده، نه تکمیل پنهان.

## وضعیت تحویل

T01–T04 سیاست، use case، audit دائمی و CLI محافظت‌شده را فراهم کرده‌اند؛ T05
راهنمای بهره‌برداری و آموزش را تکمیل می‌کند. این سند آمادگی production، آموزش
انسان واقعی یا استقرار را ادعا نمی‌کند. US-09.T07 و بخش آنلاین T081 همچنان بازند؛
شروع US-11 نیازمند بررسی gate و دستور مالک است. [runbook استقرار](../runbook/production-deployment.md)
و [پروتکل اجرا](../TASK_EXECUTION_PROTOCOL.md) مراحل بعد را تعیین می‌کنند.
