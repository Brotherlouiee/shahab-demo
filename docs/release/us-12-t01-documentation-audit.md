# ممیزی مستندات نسخهٔ فعلی — US-12.T01

## دامنه، مبنا و نتیجه

بازبینی جاری: ۲۰۲۶-۱۰-۱۸، UTC؛ مبنای همگام‌سازی `main=ee5ee159b27c5bbfa2e8817cba3217f3fb5ba075`، tree `1afae8dd6a198c0ef9c5d19ef5499fa20ce0ddbb`. PR #132 و #133 مرج شده‌اند؛ #131 بسته و با #132 جایگزین شده است. مخزن اکنون Public است؛ این بازبینی visibility را تغییر نمی‌دهد.

ممیزی اولیه روی `f5711e78df58366b65c7f00e29fa484ea5fb0b85` انجام شد؛ اندازه‌گیری‌ها و خطاهای آماده‌سازی پایین مربوط به همان اجرای اولیه‌اند. بازبینی جاری ارجاع‌ها، ترتیب مصوب و مستندات OTP را با main پس از دو مرج تطبیق می‌دهد. بخش مستقل T01 آماده است؛ پذیرش نهایی T01/US-12، بازبینی بخش‌های متأثر پس از US-13 و تمام گیت‌های انتشار همچنان بازند.

ترتیب مصوب: کارهای مستقل از سرور US-12 پیش از US-13؛ کارهای نیازمند سرور در «جدول تسک‌های پس از استقرار». Public/Private بودن مخزن شرط ترتیب اجرا نیست.

قواعد `$safe-git-ide-collaboration`، AGENTS، پروتکل و سند جامع main و برنامهٔ مرج‌شدهٔ #132 خوانده شدند. به‌جای استفاده از checkout کثیف قبلی، snapshot متن‌های لازم در پوشهٔ مستقل ساخته و Git blob آن‌ها با tree مبنا تطبیق داده شد. این روش clone کامل یا ممیزی کل تاریخچه نیست. هیچ فایل کد از PRهای باز به این PR کپی نشده است. سند جامع، رجیستری US-13 و سند تداوم در این PR تغییر نمی‌کنند.

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
| پیکربندی آزمون/ورود | PR #133 مرج شده است؛ `.env.example` متغیرهای کاوه‌نگار با مقدارهای خالی/غیرفعال دارد. هر دو پرچم ارسال و تأیید الگو پیش‌فرض false هستند؛ local/test همچنان mock و staging/production بدون تنظیم معتبر fail-closed است. کلید واقعی ثبت نشده؛ تأیید OTP1، تنظیم امن سرور و آزمون واقعی بازند. [راهنمای OTP](../operations/kavenegar-otp.md) مرجع است. |
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

**جدول تسک‌های پس از استقرار در سند جامع** مرجع واحد کارهای نیازمند سرور است: T081/T07، US-10.T04، US-11.T02H/T03/T04/T05، بخش‌های آنلاین US-12.T03/T04/T05 و تأیید/آزمون واقعی OTP T06. وابستگی CI و انتشار registry در T04A.3/.4 جدا از این جدول هستند؛ نیاز به حساب/مجوز registry معادل نیاز به سرور نیست. این ممیزی هیچ ردیف را بسته اعلام نمی‌کند.

بخش مستقل بعدی T02 روی main تازه است. پس از تغییرات US-13، اسناد متأثر با SHA نهایی دوباره تطبیق داده شوند؛ شواهد نسخهٔ جاری به نسخهٔ آینده تعمیم داده نمی‌شوند.

Rollback این تغییر فقط revert فایل‌های مستندات همین PR است؛ migration/downgrade/reset volume یا بازگرداندن endpoint ناامن لازم نیست. این بازبینی هیچ PR را مرج و visibility را تغییر نمی‌دهد؛ deploy، تنظیم secret و ارسال واقعی OTP انجام نشده‌اند.
