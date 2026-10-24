# US-11.T06 — اتصال OTP کاوه‌نگار و پذیرش آنلاین

## وضعیت جاری — ۲۰۲۶-۱۰-۲۴؛ گزارش مالک و ادامهٔ پذیرش

مبنا main@92b39e0371209e2acb674e8558450d446fe0b607 پس از مرج #155 است. اسکیل همکاری، AGENTS، پروتکل و سند جامع بازخوانی شدند؛ سه قانون طلایی، حفظ تغییرات worktree قبلی و شاخهٔ مستقل Codex رعایت می‌شوند. این بخش بر وضعیت‌های تاریخی «الگو تأیید نشده/ارسال خاموش» پایین مقدم است؛ تاریخچه پاک نمی‌شود. زمان شروع ثبت ابزار ۲۰۲۶-۱۰-۲۴ ساعت ۱۴:۱۶ تهران؛ بخش پیش از ثبت و تفکیک فعالیت‌ها اندازه‌گیری نشده‌اند.

مالک تأیید الگوی OTP1 را اعلام کرد. تنظیمات private سرور با ورود مخفی کلید و حفظ راز مستقل موجود به‌روزرسانی شد؛ خروجی ارائه‌شدهٔ مالک، بازسازی سالم فقط API را نشان می‌دهد. سپس مالک دریافت پیامک واقعی و ورود موفق در https://shahabfintech.ir/ را تأیید کرد. شماره، کد، token، cookie، کلید، DSN و خروجی محیط خصوصی دریافت یا در Git ثبت نشدند. این شاهد، گزارش مالک است؛ عامل دسترسی SSH مستقل ندارد.

نسخهٔ واقعی API طبق خروجی مالک همان digest قبلی `sha256:7e9366e8ad69aaba5fcbba702d0cbd60a935c3816daf89841b490f53bb73fb7e` (انتشار v0.1.0) است؛ فرانت v0.1.2 با digest `sha256:d869f9e036df83f5be1fb45a0434ebf60c643a5e747d0f4a713281e4c6e60e77`. ارتقای فرانت به معنی ارتقای backend نیست. diff بین v0.1.0 و main فعلی برای provider، SqlAlchemyAccountAccess، router و تست اختصاصی kavenegar خالی است؛ دریافت SMS به ساخت ایمیج تازه نیاز نداشت.

| بررسی | وضعیت و شاهد |
| --- | --- |
| تأیید الگو، نصب تنظیمات، سلامت API | تأیید/خروجی مالک در همین تحویل؛ completed |
| دریافت SMS و ورود از مرورگر سایت | گزارش صریح مالک؛ passed |
| قرارداد provider، خطای ارسال، quota/attempts/restart | تست‌های موجود؛ [Quality main مبنا](https://github.com/Brotherlouiee/shahab-demo/actions/runs/40015328895) موفق است؛ خطای واقعی provider روی production القا نمی‌شود |
| کد اشتباه، single-use، restore/profile، logout/revocation، انقضای واقعی کد روی HTTPS | اجرای مالک با commit 756ec67 و SHA-256 ابزار 04e43bf2a21a5c39e5a1fcad14b28bc7e83259f0b843e9120df7f386712d37b3؛ همهٔ موارد passed |

محدودهٔ این تغییر: ابزار CLI مستقل پذیرش و تست ایمنی آن، گزارش، runbook، guide و CHANGELOG. runtime، frontend، schema، منابع/scoring، نصب جدید روی سرور، restart و workflow تغییر نمی‌کنند. ابزار فقط API عمومی موجود روی دامنهٔ ثابت HTTPS را با شمارهٔ خود مالک صدا می‌زند؛ حداکثر دو request پیامک، بدون retry/redirect/proxy محیطی، بدون API key/DB، بدون نوشتن profile و بدون نمایش شماره/کد/token. نشست خودش را خارج می‌کند؛ اعتبارسنجی revoke عمداً از token قبلی استفاده می‌کند تا پاک‌شدن cookie به‌تنهایی با لغو سروری اشتباه نشود. کد دوم پس از TTL واقعی بررسی می‌شود؛ زمان/DB سرور دست‌کاری نمی‌شود.

نتیجهٔ زنده: مالک خروجی `live_checks_passed` با `smsRequests: 2` را ارائه کرد؛ بخش عملیاتی T06 کامل است. بستن تحویل PR به ثبت همین شاهد و CI سبز head نهایی وابسته است. ساخت ابزار یا CI موفق جای اجرای زنده را نمی‌گیرد. هیچ NetBird، staging، آزمونگر دوم، کمپین DAST یا آزمون بار اضافه نمی‌شود. سند تداوم چون پایان US-11 نیست تغییر نمی‌کند.

بررسی محلی: چهار تست ابزار بدون شبکه موفق؛ عدم درخواست سوم SMS، توقف روی redirect/endpoint نامجاز، استفاده از token قدیمی، پاک‌سازی نشست در موفقیت غیرمنتظره و عدم افشای ورودی/exception بررسی شدند. Ruff و secret/diff check روی نسخهٔ نهایی ثبت می‌شوند. اجرای اولیهٔ suite قدیمی در Python این محیط به نبود fastapi/sqlalchemy پیش از شروع تست خورد؛ آن را موفق اعلام نکردیم و وابستگی/نسخهٔ محصول را عوض نکردیم. CI موجود مبنا و CI PR جدید شاهد مستقل‌اند. زمان کل و مصرف توکن دقیق اندازه‌گیری نشده‌اند.


## بازبینی برای مرج پس از PR #132 — ۲۰۲۶-۱۰-۱۸

دستور مالک: بررسی و آماده‌کردن همین PR برای مرج توسط خودش؛ تأیید الگوی OTP1 هنوز منتظر است. مبنای تازه main برابر `2f78336ebe84e0fdf965caa5176b9cf478b7d28d` (مرج #132) و head قبلی OTP برابر `a2a78fd031a196a236e5df2f950d52d75bd79ec8` است. شاخه به Codex سپرده شده؛ snapshot مستقل و update با expected_sha، بدون force و بدون دست‌کاری IDE/main.

پیش از تغییر: هم‌پوشانی فقط guide و CHANGELOG بود؛ هدف همگام‌سازی شاخه با main، حفظ تمام تصمیم‌های #132 و کد OTP موجود، سپس اجرای CI واقعی روی ترکیب جدید است. دامنه این همگام‌سازی: همان ۱۹ فایل PR؛ runtime/test blobها دقیقاً همان head قبلی OTP، بدون تغییر رفتار یا رفع حدسی. ریسک merge دو برنامه با حفظ کامل registry و محتوای main کنترل می‌شود؛ راه بازگشت revert merge/کد طبق runbook، بدون reset دیتابیس است.

۵۶ تست بدون SMS در snapshot مستقل و با blobهای runtime/test برابر head موفق شدند: kavenegar_otp، profile_access، account_session_lifecycle، transport_hardening، account_bookmarks، operational_observability، api_documentation و api_health. قرارداد Lookup با transport مصنوعی است؛ کلید واقعی/ارسال شبکه لازم نیست. مرز import و OpenAPI drift نیز موفق‌اند؛ PostgreSQL و browser در شش CI جدید روی head همگام‌شده اثبات می‌شوند، نه با skip محلی.

خاموش‌بودن پیش‌فرض هر دو flag، رد فعال‌سازی بدون تأیید/secret/PostgreSQL، رد sender واقعی در TEST/CI، عدم fallback production به mock، quota/expiry/مصرف یک‌باره و خطای امن بررسی شدند. pending واقعی تأیید الگو و دریافت SMS روی سایت در «جدول تسک‌های پس از استقرار» main باز است؛ مرج کد پایان آن بخش نیست. هیچ key واقعی، SMS، استقرار یا merge این PR انجام نمی‌شود.

Ruff lint، mypy روی۱۱۰فایل، secret scan و OpenAPI drift موفق‌اند. اولین CI روی head همگام‌شده در format:check شش EOF خالی اضافه را رد کرد؛ عیناً محلی بازتولید و فقط یک newline اضافه از هر شش فایل حذف شد. Python AST قبل/بعد برای هر شش فایل یکسان است و format --check کل app/tests و lint اکنون موفق‌اند؛ کد provider و آزمون‌ها ضعیف/عوض نشده‌اند. شش چک روی head اصلاح‌شده دوباره ملاک پذیرش‌اند؛ موفقیت head قبلی تعمیم داده نمی‌شود. SHA و لینک/خلاصه CI در بدنه PR است. checkpointهای پایین سابقهٔ پیاده‌سازی اولیه‌اند و به معنی Private بودن فعلی مخزن یا باقی‌بودن شکست اولیهٔ CI نیستند. برآورد بازبینی/همگام‌سازی و CI: حدود ۵–۱۰ دقیقه؛ زمان واقعی در PR ثبت می‌شود. یک فرمان محلی پیش از ایجاد پوشه هدف خطای cwd داد؛ پوشه ساخته شد و تست‌ها بدون تغییر محصول موفق شدند.

## checkpoint آغاز — ۲۰۲۶-۱۰-۱۸

مجوز مالک: پیاده‌سازی مستقل اتصال با الگوی OTP1، اجرای تست بدون ارسال و ساخت PR؛
مجوز Public کردن، merge، deploy، دریافت کلید یا ارسال پیامک صادر نشده است.
مبنای main: f5711e78df58366b65c7f00e29fa484ea5fb0b85.
سه قانون طلایی تأیید شد؛ کل guide با blob
9d4e740ce4908d57ce33522603c4d83cf8df06fc و پروتکل با blob
7a2e369ee6bef86601cb79b3b02cbe82c9e15d96 بازخوانی شدند.

estimatedWorkScope: یک provider و اتصال به challenge موجود، config، تست و اسناد؛
completionBudget: چرخه محدود backend، بدون UI، migration، داده یا استقرار.
مالکیت: شاخه مستقل Codex؛ فایل‌های قدیمی workspace منتقل نمی‌شوند. دریافت snapshot
از GitHub App روی SHA ثابت انجام شد؛ clone/pull محلیِ احرازشده در این محیط در دسترس
نیست. commit محلی snapshot فقط ابزار diff است و تاریخچه آن به مخزن ارسال نمی‌شود.

| مورد | قرارداد |
| --- | --- |
| فعلی/مطلوب | کد ثابت local/test → provider قابل فعال‌سازی صریح برای ارسال Lookup و بررسی کد مختص challenge |
| مرز | accounts، composition/config و تست؛ schema/contract/API/UI/scoring ثابت |
| وابستگی | AccountAccess و SqlAlchemyAccountAccess، profile creation، cookie/session و quota مشترک |
| محیط | Python 3.12؛ fake transport بدون شبکه؛ API با DB مصنوعی؛ PostgreSQL در صورت دسترسی مستقل |
| حداقل اثبات | body صحیح، timeout/redirect/error، انقضا/تلاش/یک‌بارمصرف، worker جدید و خطای ارسال بدون credential |
| خطر | افشای URL حاوی key، ارسال تکراری، قبول challenge آزمایشی، fallback حافظه، نگه‌داشتن lock هنگام شبکه |

منابع مرتبط: REST رسمی Lookup، Python SDK رسمی، ADR 0010، lifecycle حساب و threat
model پروفایل. منابع توصیه‌گر تغییر/تفسیر نمی‌شوند؛ شش unitext در دامنه این تسک نیستند.
کلید/نام الگو در تنظیمات محیط؛ متن پیامک متعلق به پنل کاوه‌نگار است.
تأیید الگو هنوز pending و آزمون واقعی/پایان gate آنلاین باز است.

## checkpoint پایان پیاده‌سازی آفلاین

actualScope: provider و اتصال به دو access adapter، config/composition، ۱۰ تست جدید
بدون شبکه و دو تست PostgreSQL در suite موجود، اسناد/CHANGELOG؛ بدون dependency،
migration، frontend، داده رسمی، CI workflow، merge، deploy یا SMS واقعی.
سه قانون طلایی در تحویل رعایت شدند؛ ادعای Done نهایی یا پایان story وجود ندارد.
برنامه US-13 و PRهای131/132 دست‌نخورده‌اند؛ افزوده guide فقط تعریف همین تسک مستقل است.

### شواهد روی نسخه نهایی کد

- Python3.12.14؛ ۶۰ تست یکتای بدون SMS موفق: kavenegar_otp(۱۰)، profile_access،
  account_session_lifecycle، transport_hardening، account_bookmarks،
  operational_observability (در مجموع۴۶)، recommendation_history_api(۴)،
  api_documentation(۷) و api_health(۳). تست اختصاصی/اسناد پس از آخرین اصلاح دوباره
  اجرا شدند؛ تست‌های بدون تغییر بی‌دلیل تکرار نشدند.
- فرمان اصلی: `python -m unittest backend.tests.test_kavenegar_otp backend.tests.test_profile_access backend.tests.test_account_session_lifecycle backend.tests.test_transport_hardening backend.tests.test_account_bookmarks backend.tests.test_operational_observability` →۴۶ موفق.
- `python -m unittest backend.tests.test_recommendation_history_api` →۴ موفق؛
  `python -m unittest backend.tests.test_kavenegar_otp backend.tests.test_api_documentation` →۱۷ موفق؛
  `python -m unittest backend.tests.test_api_health` →۳ موفق.
- `ruff check` روی app و دو فایل تست مربوط موفق؛ `ruff format --check` دو فایل جدید
  موفق؛ `mypy backend/app` روی۱۱۰فایل موفق؛ boundary/secret و `git diff --check` موفق.
- `python -m scripts.export_api_docs --check` بدون drift؛ هیچ فایل generated تغییر
  نکرده است. قرارداد endpoint/schema عمومی ثابت است.
- Bandit1.9.4 روی کل backend: بدون high، ۳medium با confidence پایین و۷low در
  فایل‌های تغییرنکرده؛ روی تمام۶فایل runtime همین تغییر صفر یافته. سیاست pinned CI
  با Bandit1.8.6 و همان flags نیز جدا اجرا می‌شود؛ نتیجه در PR ثبت خواهد شد.
- `python -m unittest backend.tests.test_account_access_postgresql`: هفت تست skip
  به علت نبود PostgreSQL/SHAHAB_TEST_DATABASE_URL؛ این شامل۲تست جدید است و عبور
  PostgreSQL محسوب نمی‌شود. تست race/lock و migration در CI موجود هنوز لازم است.
- نصب PostgreSQL در این محیط به محدودیت permission/setgroups خورد؛ ادامه نصب یا
  دورزدن محدودیت انجام نشد. هیچ DB یا volume کاربر هدف قرار نگرفت.
- browser/full frontend build اجرا نشدند: فایل فرانت/CSS/asset تغییر نکرده است؛
  gateهای CI موجود حذف یا تضعیف نشده‌اند. CI معتبر exact head هنوز لازم است.
- هیچ key واقعی دریافت/استفاده نشد، هیچ شبکه کاوه‌نگار و هیچ پیامک انجام نشد.

### اصلاح‌های آزمون و محدودیت محیط

اولین فرمان به نام اشتباه test_account_access_shared اشاره کرد؛ با module واقعی
account_session_lifecycle جایگزین و تست موفق شد. fixture دیتابیس تاریخچه ابتدا
در snapshot موجود نبود؛ سه منبع لازم با Git blob اصلی تأیید و فقط محلی آماده شدند
(f14d0d82a13708e87eea93c1d96ff14f4797c10b،
0854a5c3ad6b7640ddb7d6d9ae24ae0b2a4733fc،
7eeed38450067f7fe3ba6be4846999d768ed697c). هیچ بایت منبع به Git ارسال نمی‌شود.
نسخه متنی connector ابتدا باینری UTF-16 را تبدیل کرده بود؛ مصرف نشد و پس از تطبیق
کامل blob بایت صحیح برای تست استفاده شد. یک تفاوت newline محلیِ artifact دریافت‌شده
نیز اصلاح شد؛ تولید OpenAPI با main برابر ماند. تست worker تازه، object cache SQLite
را قبل از بازخوانی خالی می‌کند؛ این قرارداد جای تست locking PostgreSQL نیست.

### زمان و اقدام بعد

شروع ثبت زمان: 2026-10-18T09:34:06Z (۱۳:۰۴تهران)؛ بررسی کوتاه پیش از آن ثبت نشده.
مدت خواندن/پیاده‌سازی/آزمون جداگانه ثبت نشد؛ مدت دیواری و انتظار ابزار در توضیح PR
ثبت می‌شود و جمع موازی ساختگی گزارش نمی‌شود. عوامل اتلاف: snapshot ناقص/encoding
connector و آماده‌سازی fixture؛ نام اشتباه suite؛ نبود PostgreSQL. اقدام بعد: دریافت
fixture از blob تأییدشده و انتخاب نام suite از فهرست واقعی، سپس CI با PostgreSQL.

nextTaskId: همین US-11.T06، اثبات CI روی head و سپس تأیید الگو/تست زنده با مجوز؛
نه شروع ماژولارسازی یا اعلام پایانUS-11. تا آن زمان implemented/offline verified،
pending PostgreSQL CI and online evidence. PR آماده بررسی و تا gate معتبر غیرقابل merge.
Rollback/config/rotation در runbook؛ سند تداوم پایان story طبق دستور مالک تغییر نکرد.

## نتیجهٔ نهایی پذیرش HTTPS — ۲۰۲۶-۱۰-۲۴

شاهد: اجرای تعاملی فایل checksum-verified روی سرور توسط مالک؛ مشاهدهٔ مستقل SSH توسط عامل ادعا نمی‌شود. دریافت دو پیامک واقعی و ورود مرورگر پیش‌تر نیز تأیید شده است. خروجی پالایش‌شدهٔ ارائه‌شده:

```text
PASS anonymous_session HTTP 401
PASS first_sms_requested HTTP 200
PASS wrong_code HTTP 401
PASS valid_code HTTP 200
PASS cookie_session_restore HTTP 200
PASS profile_read HTTP 200
PASS consumed_code_rejected HTTP 401
PASS logout HTTP 204
PASS revoked_session_rejected HTTP 401
PASS revoked_profile_rejected HTTP 401
PASS second_sms_requested HTTP 200
PASS expired_code_rejected HTTP 401
{"task": "US-11.T06", "result": "live_checks_passed", "smsRequests": 2}
```

مرز نتیجه: بخش آنلاین T06 روی backend مستقر v0.1.0 و frontend v0.1.2 موفق است؛ نه پایان US-11/فاز۱ و نه آزمون بار/اختلال عمدی provider. CI head اولیهٔ PR156 شش موفق و یک شکست دارد: ساخت/اسکن تصاویر در run40087533704 به HIGH تازهٔ CVE-2026-111497 در brotli-libs نسخهٔ 1.2.0-r1 فرانت رسیده؛ FixedVersion گزارش 1.2.1-r0 است. این شکست مستقل از OTP در اصلاح امنیتی جدا پیگیری می‌شود و تا gate سبز تحویل قابل مرج ادعا نمی‌شود. کد ابزار آزموده‌شده پس از اجرای زنده تغییر نکرده و تکرار SMS لازم نیست.
