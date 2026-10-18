# ممیزی مستندات نسخهٔ فعلی — US-12.T01

## دامنه، مبنا و نتیجه

تاریخ: ۲۰۲۶-۱۰-۱۸، UTC. دستور مالک: اجرای بخش مستقل T01 و PR جداگانه #134 پیش از Public. این بخش از ممیزی روی **نسخهٔ فعلی آماده شد**؛ Done نهایی T01/US-12 یا مجوز merge/deploy نیست. بازبینی بخش‌های متأثر روی SHA نهایی پس از US-13 و همهٔ گیت‌های انتشار باقی‌اند.

| مرجع | revision و وضعیت هنگام ممیزی |
| --- | --- |
| مبنای کد و اسناد main | `f5711e78df58366b65c7f00e29fa484ea5fb0b85`، tree `e15583f3cf1c1271c8c875fe32a2f26bf4909273` |
| سند جامع main | blob `9d4e740ce4908d57ce33522603c4d83cf8df06fc`؛ رجیستری/استثنای تکمیلی PR #132 هنوز وارد آن نشده |
| برنامه و اصلاح CI در PR #132 | head `09f6190a7802861bc508bba43a2661ace494a05c`، باز و مرج‌نشده؛ متن پیشنهادی و دستور صریح مالک مبنای آماده‌سازی محدود است، نه ادعای مرج برنامه |
| OTP کاوه‌نگار در PR #133 | head `a2a78fd031a196a236e5df2f950d52d75bd79ec8`، باز/Draft و مرج‌نشده؛ الگوی OTP1، تأیید provider و تنظیم/آزمون واقعی جدا هستند |
| PR #131 | باز و مرج‌نشده؛ پیشنهاد قبلی برنامه، نه وضعیت main یا مجوز انتقال فرانت |

قواعد `$safe-git-ide-collaboration`، AGENTS، پروتکل و سند جامع main/پیشنهاد #132 خوانده شدند. به‌جای استفاده از checkout کثیف قبلی، snapshot متن‌های لازم در پوشهٔ مستقل ساخته و Git blob آن‌ها با tree مبنا تطبیق داده شد. این روش clone کامل یا ممیزی کل تاریخچه نیست. هیچ فایل کد از PRهای باز به این PR کپی نشده است. سند جامع، رجیستری US-13 و سند تداوم در این PR تغییر نمی‌کنند.

## یافته‌ها و اصلاح انجام‌شده

| یافتهٔ قابل بازتولید | شاهد در کد مبنا | اصلاح مستندات |
| --- | --- | --- |
| README توصیه‌گر را صرفاً demo و میزبانی static را کافی معرفی می‌کرد | router توصیه و SQL serving، Compose چهار سرویس اصلی؛ Netlify فقط build/fallback | README با مسیر راه‌اندازی، وابستگی backend/catalogue و مرجع تست/استقرار اصلاح شد |
| پوشش دستی هنوز ۱۶ عملیات و بدون bookmarks بود؛ liveness هم وابسته به mock معرفی شده بود | decoratorهای API و generated/operations.json، هر دو ۱۹ عملیات | ماتریس کامل، save/list/remove و تست حساب دوم؛ liveness فقط سلامت پردازه |
| runbook آنلاین و راهنمای محلی از نشست حافظه‌ای، ابطال با restart و TTL حساب ۳۰ دقیقه می‌گفتند | accounts/sqlalchemy_access.py، account_access.py؛ issued/expires مطلق و cookie Max-Age=3600 | account=یک ساعت، questionnaire=۳۰ دقیقه، OTP=۱۲۰ ثانیه؛ shared DB و restore بدون renewal، تفکیک mock از production |
| شمارهٔ ADR در دو پوشه تکرار و توضیحات قدیمی با وضعیت فعلی مخلوط بود | docs/architecture و docs/adr؛ افزوده‌های A.2/B/C/E/F/G | فهرست با مسیر کامل و تقدم قرارداد جدید؛ سابقه حفظ شد؛ وضعیت proof/purge در ADR history تصحیح شد |
| ERD/dictionary/3NF با طرح مفهومی آغاز و موجودی اجرایی روشن نبود | ۳۵ __tablename__ در ORM، ۱۸ migration با یک head ff11b02f0001 | فهرست کامل جدول‌های اجرایی، view approval_records و نام‌های صرفاً مفهومی؛ برچسب تاریخی و پیوند از سه سند اصلی |
| module map یک جداکنندهٔ literal در جدول داشت و scaffold/future را با کد جاری مخلوط می‌کرد | جدول مرز questionnaire و بخش‌های تاریخی همان سند | شکست سطر جدول و تقدم فرانت فعال src/، SQL/session/proof/bookmarks اصلاح شد |

هیچ method/path/body، داده/وزن/config version، schema/constraint، migration، UI/CSS/asset، provider یا workflow تغییر نکرد. چهار artifact تولیدی API byte-for-byte همان مبنا هستند؛ بازتولید صرفاً برای کنترل drift انجام شد.

## ممیزی تنظیمات و مرز انتشار اطلاعات

| سطح بررسی | نتیجهٔ همین نوبت |
| --- | --- |
| فایل‌های env و context ساخت | در tree مبنا تنها فایل با نام `.env*`، `.env.example` است؛ مقدارهای change-me-local-only نمونه‌اند. `.gitignore` env واقعی را مستثنا و `.dockerignore` .env را حذف می‌کند. secret جدید نصب/دریافت/ثبت نشد؛ ignore، فایل قبلاً commitشده یا تاریخچه را محرمانه نمی‌کند. |
| مسیر واقعی اجرا | `docker-compose.yml` و Dockerfile ریشه، pyproject.toml ریشه و Vite در src/؛ مسیرهای compose.yaml یا backend/Dockerfile در فهرست هدف سند جامع، فایل‌های فعلی محسوب نشوند. Compose توسعه reload/bind mount و localhost:5173/8000 دارد؛ PostgreSQL/Redis پورت میزبان ندارند. |
| build و hosting | Netlify تنها dist/fallback را می‌سازد؛ proxy توسعه در scripts/vite-dev-config.mjs است. این تنظیم به معنی API آنلاین نیست. دو image تولیدی/scan/registry متعلق به T04A و خارج از T01 هستند. |
| پیکربندی آزمون/ورود | main هنوز mock local/test و deny در staging/production دارد. هیچ Kavenegar key/secret به example یا کد افزوده نشد. متغیرها و تغییر provider پیشنهادی #133 پس از مرج باید دوباره با docs/env تطبیق داده شوند. |
| دانش فنی و منابع قابل مشاهده | tree شامل `.agents/documents/*.unitext`، data/contracts، الگوریتم/آزمون‌های توصیه‌گر، سند جامع، ERD و تصمیم‌های محصول است؛ Public کردن همان مخزن این اطلاعات tracked را پنهان نمی‌کند. در این تسک هیچ‌یک حذف، تفکیک یا به مخزن دیگری منتقل نشد. پذیرش ریسک موقت مالک از گفتگو، تضمین محرمانگی یا مجوز خودکار Public نیست. |
| دامنهٔ secret scan | scanner موجود روی snapshot متن‌های انتخاب‌شده بدون finding عبور کرد؛ این scanner الگوهای محدود assignment دارد و همهٔ فایل‌های tree، binaryها، تاریخچه، PR/comment/artifact و تنظیمات خصوصی GitHub/میزبان را پوشش نمی‌دهد. نتیجه «راز وجود ندارد» یا تأیید نهایی انتشار عمومی نیست. |
| dependency/reproducibility | package-lock موجود و محدوده‌های Python در pyproject بررسی شدند؛ dependency جدید یا lockfile ساختگی ایجاد نشد. نسخهٔ واقعی محیط آزمون پایین ثبت است؛ full CI/SCA و image scan روی SHA پذیرفته‌شده همچنان شاهد مستقل می‌خواهند. |

## بررسی‌های اجراشده

محیط ایزوله: Python 3.12.14، FastAPI 0.143.5، SQLAlchemy 2.1.5؛ dependencyهای ازقبل‌موجود در مسیر خارج snapshot، بدون نصب یا تغییر lockfile. مسیر import برنامه به همین snapshot مبنا محدود شد. فرمان‌ها از ریشهٔ پروژه، با محیط Python دارای dependencyهای اعلام‌شده:

```bash
python -m scripts.export_api_docs --check
python -m unittest backend.tests.test_api_documentation -v
python -m unittest backend.tests.test_database_models -v
python -m scripts.validate_physical_schema_spec
python -m scripts.scan_repository_secrets
python -m scripts.validate_import_boundaries
```

- OpenAPI/Postman drift: موفق؛ چهار artifact بدون تغییر. هفت تست API documentation: موفق، بدون skip؛ این‌ها تست قرارداد و policy هستند، نه ارسال SMS یا اثبات HTTPS/PostgreSQL.
- validator فیزیکی: موفق؛ این ابزار markerهای سند را کنترل می‌کند، نه اجرای DDL. secret scan محدود snapshot و import boundary: موفق.
- دو تست موجود metadata دیتابیس نیز موفق‌اند؛ این نتیجه اجرای migration روی PostgreSQL نیست.
- تطبیق مستقل ایستا: مجموعهٔ ۱۹ زوج method/path ماتریس دقیقاً برابر operations.json؛ پوشش همهٔ ۳۵ نام جدول ORM در فهرست DB؛ زنجیرهٔ ۱۸ revision فقط یک head، ff11b02f0001، دارد.
- کنترل لینک و diff/allowlist و وضعیت CI روی head این PR در [checkpoint](../progress/us-12-t01.md) ثبت می‌شود.

اولین اجرای تست drift فقط به‌دلیل نیاوردن دو فایل Postman به snapshot محلی خطای FileNotFound داد؛ پس از دریافت همان blobهای main، هفت تست موفق شدند. این شکست آماده‌سازی بود و فایل تولیدی مخزن یا assertion تغییر نکرد. اجرای پس از اصلاح مستندات نیز موفق بود. full browser/build/PostgreSQL/DAST و restore اجرا نشدند؛ این PR صرفاً مستندات است و محیط Docker/DB آنلاین در اختیار نداشت.

## کارهای باز و تحویل مرحلهٔ بعد

**دفتر معوقات موجود سند جامع** همچنان مرجع واحد است؛ این گزارش جدول backlog موازی یا شناسهٔ اجرایی جدید نمی‌سازد. در نسخهٔ پیشنهادی #132، ردیف‌های T081/T07، US-10.T04، US-11.T02H/T03/T04/T05، US-12.T03/T04/T05، registry T04A.3/.4، OTP T06 و «وابستگی نسخه و CI» بازند. هیچ ردیف با این ممیزی بسته نشد.

بخش مستقل بعدی طبق دستور/ترتیب مصوب، T02 روی main تازه است؛ ابتدا وضعیت واقعی #132/#133 و SHA بررسی شود. بعد از مرج آن‌ها و هر تغییر US-13، موارد تحت اثر این ممیزی (API/env/provider، workflow، مرز feature/CSS و README/ADR/DB) با revision نهایی تطبیق داده شوند. شواهد فعلی به نسخهٔ جدید تعمیم داده نمی‌شوند. پذیرش نهایی T01 و release تا آن زمان باز است.

Rollback این تغییر فقط revert فایل‌های مستندات همین PR است؛ migration/downgrade/reset volume یا بازگرداندن endpoint ناامن لازم نیست. وضعیت فعلی مخزن Private حفظ شد؛ merge، Public کردن، deploy، تنظیم secret یا ارسال واقعی OTP انجام نشد.
