# US-11.T06 — اتصال OTP کاوه‌نگار، بدون ارسال واقعی

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
