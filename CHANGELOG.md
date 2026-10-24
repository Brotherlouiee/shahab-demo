# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows Semantic Versioning when production releases begin.

## [Unreleased]

- بررسی محدود امنیت (US-11.T03): توسعهٔ اختیاری ابزار خواندنی موجود از چهار به شش GET برای artifactهای تنظیمات/Git، تشخیص SPA fallback و پالایش خطای شبکه؛ ثبت شواهد SAST/SCA و candidate پاک و بازماندن رفع عملیاتی brotli در image مستقر. اجرای شش GET روی VM با findings=[] موفق شد؛ استقرار اصلاح امنیتی هنوز باز است؛ بدون تغییر runtime/API/DB یا اسکن گسترده.

- راستی‌آزمایی استقرار (US-11.T02H): ابزار خواندنی محدود برای پورت‌ها، trust/config پراکسی و شش پاسخ HTTP مربوط به TLS، cache و Origin/CORS، همراه هشت تست آفلاین و ارجاع شواهد cookie واقعی T06؛ اجرای مالک روی VM با شش درخواست HTTP و صفر SMS موفق شد. بدون تغییر runtime، تنظیمات، داده، image، restart یا SMS.

- عملیات و پذیرش (US-11.T06): ثبت تأیید مالک برای الگوی OTP1، فعال‌سازی خصوصی و دریافت SMS/ورود واقعی؛ ابزار تعاملی محدود به دو پیامک برای بررسی HTTPS کد اشتباه، مصرف مجدد، خروج/revocation و انقضا، همراه آزمون آفلاین بدون SMS. اجرای زندهٔ مالک با دو پیامک و تمام بررسی‌ها موفق شد؛ بدون تغییر runtime، API، schema یا image.

- اصلاح امنیت ایمیج فرانت: ارتقای دقیق brotli-libs از 1.2.0-r1 به 1.2.1-r0 برای CVE-2026-111497 با شدت HIGH؛ کنترل موجودی واقعی و رد نسخهٔ قدیمی/مفقود. بدون تغییر UI، OTP، API یا داده؛ انتشار و استقرار جداست.

- مستندات: ثبت استقرار و تأیید مالک برای صفحهٔ تماس و اینماد با فرانت v0.1.2 و تعیین ادامهٔ US-11.T06 به‌عنوان تسک بعدی؛ فقط تغییر اولویت، بدون تغییر شناسه، دامنه یا معیار پذیرش و بدون حذف US-11.T02H یا تغییر برنامهٔ US-13.

- اصلاح امنیت ایمیج: نصب دقیق `musl` و `musl-utils` نسخهٔ `1.2.6-r3` در runtime بک‌اند و فرانت برای رفع یافتهٔ `CVE-2026-107891` اجرای انتشار صفحهٔ تماس؛ بررسی موجودی واقعی بسته‌ها و رد نسخهٔ قدیمی/مفقود اضافه شد. بدون تغییر API، داده یا استقرار.

- اصلاح (US-09.T082): پارامتر لینک استعلام اینماد از `code` به `Code` مطابق مقصد موفق مالک اصلاح شد؛ ارسال Referer مبدأ هنگام کلیک در آزمون مرورگر بررسی می‌شود. بدون تغییر ظاهر، backend یا داده.

- افزوده (US-09.T082): صفحهٔ ماژولار تماس با ما مطابق دیزاین مالک، شمارهٔ قابل تماس، ساعات پاسخگویی، لینک LinkedIn و استعلام رسمی اینماد با تصویر محلی؛ سه شبکهٔ بدون صفحه غیرفعال‌اند. گزینهٔ تماس در منو پیش از درباره ما افزوده و متن مشاورهٔ قدیمی حذف شد. بدون تغییر backend/داده یا استقرار؛ انتشار پس از پذیرش و مرج جدا انجام می‌شود.

- مستندات (برنامهٔ پس از استقرار): ثبت US-09.T082 به‌عنوان تسک بعدی و انتشار صفحه پس از پذیرش محلی، بدون انتظار برای US-13؛ حفظ شرح الزامات قبلی با وضعیت تعویق آینده و شرط بازنگری، ثبت دامنهٔ محلی T081، روش SSH تک‌مالک و شواهد انتشار PR #150. امنیت پایه، مالکیت، صحت داده و backup/بازیابی حفظ‌اند؛ بدون تغییر کد، اجرا یا استقرار.

- عملیات داده (US-09.T07): پس از backup و restore آزمایشی، منبع رسمی ۱۰۲ وام و config 1.1.0 با مسیر محافظت‌شدهٔ تک‌مالک در PostgreSQL سایت منتشر شد؛ توصیه و جزئیات از HTTPS API موفق بودند. آزمون تازهٔ Chrome به timeout راه‌اندازی خورد و تأیید بصری پس از انتشار و ورود OTP باز است. کنترل دو نفره/MFA عملیاتی ادعا نمی‌شود.


- آزمون CI: سقف زمانی فقط job مرورگر Profile OTP از ۱۰ به ۲۰ دقیقه رسید؛ دو اجرای آخر هنگام نصب وابستگی Chromium به سقف قبلی خوردند و پیش از آغاز تست لغو شدند. خود تست‌ها و معیارهای پذیرش تغییری نکردند.

- ابزار داخلی (US-09.T07): مسیر مدیریتی SSH برای یک مالک واقعی با policy متعلق به root، دو نقش صریح editor/admin و actor یکسان در audit آماده شد؛ مراحل جداگانه با ایمیج موجود و DB role غیرمالک اجرا می‌شوند. کنترل دو نفره وجود ندارد و به آینده موکول است؛ حساب یا کلید صوری ساخته نمی‌شود. نصب دسترسی‌ها و انتشار production پس از تأیید نهایی برنامهٔ تک‌مالک انجام می‌شود؛ API/UI و ایمیج مستقر تغییر نکردند.

- مستندات (US-09.T07): منبع رسمی ۱۰۲ وام و config `1.1.0` با hash و تصمیم‌های مصوب مخزن تطبیق داده شد؛ backup دیتابیس اصلی گرفته و بازیابی schema/data در PostgreSQL موقت لپ‌تاپ آزموده شد. نبود checkout و authority عملیاتی روی سرور و برنامهٔ دقیق انتشار محافظت‌شده، تأیید مالک و بازگشت ثبت شد؛ هنوز داده‌ای در production منتشر نشده است.

- مستندات (US-09.T07): ممیزی خواندنی سایت مستقر و آزمون کوتاه Chrome دسکتاپ/موبایل در معماری موجود Docker/NGINX/آروان ثبت شد. مسیر خانه تا ذخیرهٔ پاسخ پرسشنامه کار کرد، اما کاتالوگ/config فعال production صفر و OTP واقعی خاموش است؛ توصیه و جزئیات موفق تأیید نشدند. برنامهٔ انتشار محافظت‌شده و بازگشت بدون تغییر production ثبت شد؛ staging/NetBird/Netlify و تکرار آزمون‌های PR #149 طبق تصمیم مالک کنار گذاشته شدند.

- مستندات (US-09.T081): مطابق تصمیم ۲۰۲۶-۱۰-۲۲ مالک، دامنهٔ محلی مصوب PR #149 تکمیل و آمادهٔ بازبینی است؛ آزمون دو نفره/NetBird شرط مرج این PR نیست. بررسی سایت مستقر، داده/config عملیاتی و OTP واقعی در تسک‌های مربوط باز می‌مانند.

- آزمون (US-09.T081): پاک‌سازی رکورد نشان fixture پیش از downgrade اجباری اصلاح شد. ابزار تازهٔ `--container-http` کاتالوگ رسمی تست را با authority آزمایشی TLS در PostgreSQL مستقل منتشر و ۱۹ مسیر API را از راه HTTP به کانتینر loopback بررسی می‌کند؛ دادهٔ غیرخالی پس از restart فقط API و انقضای نشست نیز سنجیده می‌شوند. پذیرش HTTPS توسط دو آزمونگر واقعی و تأیید دادهٔ عملیاتی همچنان باز است.

- آزمون (US-09.T081): پس از مجوز صریح مالک، fixture رسمی فقط در PostgreSQL تازهٔ موقت لپ‌تاپ با TLS authority آزمایشی و ابزار محافظت‌شدهٔ عملیات منتشر و مسیر مثبت توصیه، وام، تاریخچه، نشان، مالکیت و ماندگاری پاس شد؛ ابزار آزمون HTTP محلی و guardهای آن افزوده شدند. پذیرش آنلاین دو آزمونگر، دادهٔ مصوب عملیاتی، MFA واقعی و SMS همچنان باز هستند؛ production و ایمیج منتشرشده تغییر نکردند.

- Docs (US-09.T081): تصمیم مالک برای آزمون فقط روی Docker/WSL لپ‌تاپ و نبود authority انتشار ثبت شد؛ آزمون HTTP واقعی با دو حساب و PostgreSQL مستقل، کنترل مالکیت، persistence و restart محلی گذشت، اما توصیهٔ موفق وابسته به داده/config و پذیرش آنلاین همچنان مسدودند. هیچ import، انتشار image یا تغییر production انجام نشد.

- Docs (US-09.T081): پس از مرج ممیزی PR #148، ظرفیت و جداسازی VM، مسیر HTTPS/CDN، خالی‌بودن کاتالوگ و پیش‌نیازهای دسترسی/authority محیط test محدود دوباره بررسی و ثبت شد؛ provisioning، import، SMS، انتشار image و تغییر production انجام نشد و آزمون مثبت T081 باز ماند.

- Docs (US-09.T081): ممیزی خواندنی نسخهٔ مستقر v0.1.0، TLS، digest، migration، وضعیت داده/config و ماتریس ۱۹ مسیر API ثبت شد؛ آزمون‌های دستی وابسته به دو حساب، OTP و دادهٔ منتشرشده همچنان مسدودند و تسک Done اعلام نشده است. هیچ سرویس، داده یا تصویر production تغییر نکرد.
- Added (مستندات عامل): ثبت عین مهارت ارسالی مالک در `.agents/skills/safe-git-ide-collaboration/SKILL.md` و ارجاع از `AGENTS.md`؛ بدون جایگزینی پروتکل اجرای تسک یا تغییر محصول/داده/استقرار.

- Added (برنامهٔ US-09.T082): ثبت صفحهٔ ارتباط با ما شامل تلفن، ساعات پاسخگویی، شبکه‌های اجتماعی و اینماد رسمی، وابسته به دیزاین/محتوای مالک؛ انتشار نسخهٔ جدید ایمیج پس از ریفکتور کامل US-13. فقط مستندات؛ بدون تغییر UI/API/DB یا اجرای استقرار.

- مستندات: نقطهٔ تداوم میانی به درخواست مالک با شواهد انتشار و مصرف v0.1.0، مرج Compose بدون build، موانع rollback/استقرار/OTP و تصمیم ادامه پیش از US-13 به‌روز شد؛ پایان داستان یا استقرار ادعا نمی‌شود.

- Added (آماده‌سازی VM / US-09.T081–T07): فایل مستقل docker-compose.prod.yml فقط با imageهای منتشرشده و digest، PostgreSQL پایدار/Redis داخلی، proxy HTTPS هم‌مبدأ و مهاجرت دستی جدا؛ نمونه env خصوصی، grant محدود API و تست واقعی topology در CI. بدون build روی VM، تغییر محصول/داده یا استقرار سرور. [راهنما](docs/operations/vm-compose.md).

- Added (US-12.T04A.4): ثبت manifest واقعی جفت v0.1.0 با دو digest و trace انتشار، workflow دستی pull-by-digest و smoke ایزوله با کنترل هویت و راهنمای سازگاری/بازگشت؛ بدون build/push تصویر یا تغییر محصول/داده/استقرار. اولین نسخه target قبلی ندارد؛ rollback باز می‌ماند و اجرای خصوصی پس از merge/approval لازم است. [راهنما](docs/operations/image-consumption.md).

- Security (US-12.T04A.3): حذف pip/ensurepip غیرلازم از Python پایهٔ runtime، نصب zlib و libxpm اصلاح‌شده با نسخهٔ دقیق و کنترل inventory واقعی برای رفع هر ۹ یافتهٔ باقی‌مانده؛ بدون تغییر کد محصول، dependencyهای برنامه، digest پایه، UI/API/schema/data/scoring یا publish/deploy. [شواهد](docs/progress/us-12-runtime-security.md).

- Fixed (US-12.T04A.3): اصلاح مقصد Docker Hub بک‌اند به `shahab2026/shahab-backend` طبق نام مصوب مالک، تطبیق تست و راهنما و ثبت محدودیت یک مخزن خصوصی Personal؛ بدون تغییر image/runtime یا عمومی‌کردن مخزن.

- Added (US-12.T04A.3): مسیر دستی انتشار همان دو image آزموده/scanشده به Docker Hub با approval محیط، version/SHA immutable، بازخوانی digest/config و اتصال SBOM/provenance؛ journal انتشار جزئی و تست‌های policy. نشر واقعی هنوز وابسته به namespace/secrets/tag و پذیرش ریسک مالک است؛ هیچ deploy یا تغییر محصول انجام نشده. [راهنما](docs/operations/dockerhub-publish.md).

- Security (US-12.T04A.2): گیت Buildx/cache محدود و scan واقعی OS/library هر دو image با رد تمام HIGH/CRITICAL، SBOM و metadata provenance؛ قفل hash وابستگی‌های image با همان نسخه‌های A.1، پایهٔ Python Alpine و دو APK امنیتی NGINX؛ بررسی read-only tag/SHA/main و هفت گیت برای A.3، با افزودن trigger main به baseline موجود بدون تغییر معیار آن. بدون registry push، تغییر UI/API/schema/data/scoring یا deploy. [قرارداد](docs/operations/container-images.md).

- Fixed (CI / US-12.T04A.2): همگام‌سازی helper ورود مرورگر با پاسخ واقعی restore/logout برای رفع race اثبات‌شده در trace؛ همان قرارداد و همهٔ assertions، بدون تغییر محصول، timeout یا retry.

- Added (US-12.T04A.1): ایمیج مستقل static فرانت با runtime غیرروت و پایهٔ digest-pinned، contextهای allowlist برای دو build، proxy HTTPS غیرفعال و harness واقعی build/run/TLS/static-byte comparison در CI بدون publish؛ Dockerfile بک‌اند، Compose/Netlify و source/UI/schema/data ثابت. [قرارداد](docs/operations/container-images.md).

- Docs (US-12.T04): پیش‌نویس release notes، زنجیرهٔ واقعی migration، طرح تفکیک بازگشت کد/schema/داده و restore با گیت ابطال credential، purge پاسخ منقضی و حفظ archived/hidden؛ فرم شواهد خالی، بدون تغییر runtime یا اجرای migration/deploy. [یادداشت](docs/release/us-12-t04-release-notes.md).

- Docs (US-12.T03): نمونه‌های غیرفعال backend/Netlify و فرم شواهد، راهنمای preview/smoke با شرط same-origin/proxy و cookie، محل secrets و gateهای آنلاین؛ بدون تغییر تنظیم فعال یا استقرار/ارسال SMS. [راهنما](docs/runbook/preview-smoke.md).

- Test (US-12.T02): اجرای همهٔ unitهای فرانت با discovery، اصلاح harness تست dedupe و انتقال journey کامل به suite واقعی FastAPI/PostgreSQL با فرم/OTP و selectorهای جاری؛ ثبت پوشش و محدودیت شواهد مستقل از سرور، بدون تغییر UI/API/schema/data/scoring یا شل‌کردن gateها. [نقشهٔ تست](docs/testing/us-12-t02.md).

- Docs (US-12 / ترتیب ۲۰۲۶-۱۰-۱۸، PR #132): انجام کارهای مستقل از سرور US-12 پیش از US-13؛ حذف شرط تقدم/تأخر انتشار مخزن، تغییر نام همان جدول به «جدول تسک‌های پس از استقرار» و جداسازی وابستگی CI/registry از سرور؛ رجیستری و پذیرش داخلی US-13 و تمام gateهای نهایی محفوظ، بدون تغییر runtime/workflow. [checkpoint](docs/progress/us-12-preparation-order-20261018.md).

- CI: اجرای مستقل مجموعه‌های PostgreSQL روی دیتابیس‌های موقت با concurrency محدود؛ حفظ همهٔ مجموعه‌ها، شکست در skip/zero-test و پاک‌سازی ایمن. مقایسهٔ baseline روی build، اجرای مرورگر عمومی در دو مرحله با اثبات پوشش کامل discovery، readiness واقعی refresh و بررسی‌های مستقل Swagger با API واقعی؛ بدون تغییر source محصول، timeout یا معیار صفرپیکسل.

- Documentation (US-13؛ PR #132): تجمیع برنامه و تمام ۲۰ جفت شناسهٔ PR #131 در سند جامع؛ تطبیق با main واقعی، اصلاح رابطهٔ CardView/StatsMarquee، تعیین تکلیف ردیف‌های بدون مصرف، تقسیم صریح پرسشنامه به هفت مسئولیت با مالکیت و پذیرش مستقل، ثبت وضعیت چهار تسک و صف Hero با معیار پذیرش؛ بدون تغییر runtime/ظاهر/API/داده یا اعلام پایان داستان.

- CI/browser: محدودکردن worker مرورگر محلی به یک، انتظار واقعی decode تصویر و آزادسازی کنترل‌شدهٔ document fallback؛ تفکیک مسیر/viewportهای مستقل با حفظ همهٔ assertionها و شرط صفرپیکسل. suite واقعی API روی خروجی build همان revision با FastAPI/PostgreSQL واقعی بررسی می‌شود.

- CI: اجرای checkout و venv در tmpfs محدود خصوصی و دیتابیس fixture در tmpfs اختصاصی، با حفظ تنظیم‌های PostgreSQL و خروجی تصاویر/trace؛ تغییر آزمایشی برای سنجش کندی I/O، بدون ادعای رسیدن به سقف پنج دقیقه.

- CI: ذخیرهٔ محیط نصب‌شدهٔ Python با کلید وابستگی/ایمیج/profile و عمر ۲۴ساعته، بازیابی کپی مستقل برای هر job، حفظ audit امنیتی و زمان‌سنجی جداگانهٔ ۹ مجموعه PostgreSQL؛ probe مستقل برای مقایسه cold/warm بدون اجرای خودکار gateهای کامل.

- CI: قطع‌پذیرشدن wrapper و پاک‌سازی محدود به run/attempt/job پس از لغو؛ افزودن probe محدود برای زمان نصب، import، تراکنش و یک آزمون migration، بدون اجرای خودکار gateها یا تغییر timeout و معیارهای قبلی.

- CI: به‌روزرسانی pip محیط آزمون امنیتی به نسخهٔ دارای اصلاح advisoryها و انتظار برای فرم واقعی ورود پیش از مقایسهٔ تصویر، با حفظ gate صفرپیکسل و بدون تغییر محصول.

- CI: اجرای شش job فعلی با ایمیج آمادهٔ محلی shahab-ci:local-v1 و منع pull هنگام آزمون؛ cache دانلود npm/pip، PostgreSQL موقت بدون پورت میزبان، cleanup محدود و پنج آزمون wrapper. پشتیبانی از مسیر مرورگر آماده در تست‌های baseline و پروفایل با حفظ assertionها و همهٔ gateهای قبلی.
- Docs (US-12.T01): ممیزی مستندات main با SHA مشخص؛ اصلاح README و راهنمای نشست مشترک یک‌ساعته، پوشش دستی ۱۹ عملیات شامل نشان‌شده‌ها، موجودی ۳۵ جدول/۱۸ migration و تقدم ADR/اسناد تاریخی؛ ثبت مرز اطلاعات قابل انتشار و گیت‌های باز. بدون تغییر runtime، schema، workflow یا برنامهٔ US-13؛ پذیرش نهایی روی نسخهٔ پس از refactor همچنان باز است.

- Test/Documentation (US-13.T03.01): مستندسازی no-move برای قواعد درهم‌تنیدهٔ CSS صفحهٔ درباره ما با profile/saved/header و افزودن گیت مستقل تطابق computed style/geometry با baseline؛ هیچ انتقال CSS، redesign یا تغییر رفتار.

- Refactor (US-13.T02.01): انتقال بی‌تغییرِ صفحه «درباره ما» به ماژول مستقل و تزریق هدر فعلی، بدون جابه‌جایی CSS، متن، آیکن، دارایی، DOM یا تغییر رفتار؛ آزمون مقایسهٔ ناوبری/تصویر در کنار خط مبنای صفرپیکسلی.

- Test (US-13.T01): الزام برابری دقیق تمام پیکسل‌های تصاویر صفحه‌های خانه/درباره‌ما/ورود با نسخهٔ پذیرفته‌شدهٔ پیش از ریفکتور در ۹ ترکیب route×viewport، بدون mask/threshold و بدون تغییر UI.

- Test (US-13.T01): افزوده‌شدن workflow مستقلِ تصویرگیری از نسخهٔ منجمد پیش از ریفکتور و head برای خانه، درباره ما و ورود در ۳ viewport، بدون تغییر UI؛ assertion هندسه و artifact PNG برای ممیزی دقیق.

- Docs (US-13.T01): موجودی ماژول‌های فعال فرانت، ماتریس مسیر و وضعیت و viewport، Git blob baseline ثابت، رجیستری پیشنهادی ریزگام‌های T02/T03 و شکاف‌های باقی‌ماندهٔ شواهد مستقل پیش از استخراج؛ بدون تغییر کد، CSS، asset یا رفتار محصول.

- Docs: ثبت تصمیم جدید مالک برای اجرای US-13 و gate ریفکتور **پیش از** فعالیت‌های قابل اجرا از US-12؛ باقی‌ماندن گیت‌های آنلاین/انتشار و تسک Docker Hub در صف بدون کاهش معیار پذیرش.


- Docs (US-12.T04A): تصویب تسک ساخت و آزمون دو ایمیج تولیدی بک‌اند و فرانت‌اند با GitHub Actions و انتشار نسخه‌دار در Docker Hub پس از ایجاد حساب/Secrets مالک؛ بدون تغییر runtime، workflow فعلی یا انتشار واقعی.

- US-11.T05: اجرای امن تک‌نوبتی پایش پاک‌سازی پاسخ خام با حالت dry-run و کد وضعیت backlog؛ ثبت runbook تمرین پشتیبان رمزگذاری‌شده، بازیابی ایزوله و آزمون بار بعد از تأیید سرور، بدون اتصال خودکار scheduler یا دست‌کاری دادهٔ کاربر.

- US-11.T04: ثبت لاگ با قالب ممیزی‌شده و محافظت برابر نشت دادهٔ شخصی؛ متریک‌های تجمعی داخل پردازه و هشدارهای 403/429/5xx و شکست ورود؛ راهنمای مدیریت رخداد و ثبت وابستگی پایش آنلاین. بدون تغییر API عمومی، UI، دیتابیس یا نگهداری داده.

- Docs: افزودن دفتر مستقل تسک‌ها و شواهد معوق وابسته به سرور آنلاین در سند جامع پروژه؛ بدون تغییر ترتیب تسک‌ها، معماری یا رفتار محصول.

- US-11.T03: افزودن دروازهٔ مستقل بررسی ایستای امنیتی، ممیزی آسیب‌پذیری وابستگی‌های Python/Node و ابزار DAST محدود برای محیط آزمایشی HTTPS دارای مجوز، همراه با ثبت blocker استقرار.

- US-11.T02H: افزودن سخت‌سازی پاسخ‌های خصوصی، CORS/CSRF، هدرهای امنیتی و محدودیت حجم درخواست API همراه با آزمون‌های منفی؛ بدون تغییر طراحی، احراز هویت یا دیتابیس.

- US-11.T02G: استفادهٔ داخلی برای بایگانی اتمیک حساب و ابطال تمامی نشست‌ها؛ ورود دوباره همان شماره، نسل مستقل می‌سازد. بدون UI یا endpoint حذف.

### Added

- US-11.T06: اتصال قابل فعال‌سازی OTP کاوه‌نگار با الگوی محیطی، ارسال HTTPS Lookup، کد challenge-bound بدون ذخیره خام و حفظ quota/expiry/session؛ آزمون‌های بدون پیامک و runbook [فعال‌سازی/بازگشت](docs/operations/kavenegar-otp.md). schema/API/UI/منابع توصیه‌گر تغییر نمی‌کنند؛ تأیید الگو و تست واقعی همچنان pending.

- US-11.T02F: نشان‌شده‌های حساب‌محور در association نرمال account_bookmarks و API
  owner-scoped desired-state، migration افزایشی ff11b02f0001، optional own-snapshot
  reference بدون کپی مشخصات/score. sync دستگاه/refresh، retry/rollback/PK و index tests.

### Security

- US-11.T02F: profile/form/bookmark/result cache فقط memory؛ logout revoke و cookie/
  storage/state شهاب پاک، late response/نسل تازه رد و failed logout fail-closed.
  historyId opaque برای refresh همان snapshot بدون JSON شخصی در navigation؛ legacy
  browser bookmark خودکار upload نمی‌شود. CSS/asset/engine/source unchanged؛ visual
  مقایسه مستقل و راهنمای rollback nonempty guard. [قرارداد](docs/security/account-bookmarks.md).

### Security

- US-11.T02E: پاک‌سازی transactional/bounded پاسخ‌های کامل/نیمه‌کاره expired، حفظ
  snapshot و metadata مرتبط با history حتی hidden/archived؛ حذف metadata غیرمرتبط.
  CLI داخلی dry-run/apply با counts بدون payload، retry/rollback و PostgreSQL race
  verification؛ بدون migration یا تغییر UI/scoring. scheduler/restore/monitor در T05.

### Security

- US-11.T02C: نشست account-bound با expiry مطلق۳۶۰۰ و revocation دائمی/shared در
  PostgreSQL؛ restore زمان باقی‌مانده، بدون renewal و restart/worker صحیح. OTP
  challenge/attempt/quota مشترک، migration افزایشی cc11b02c0001 و PG race/rollback.
  [قرارداد](docs/security/account-session-lifecycle.md). profile/history/source/UI ثابت؛
  token قدیمی نیازمند login تازه، real provider/OTP flow D/archive G جدا.


### Security

- US-11.T02B: رفع F01 با proof تصادفی مخصوص پرسشنامه، digest پایدار و expiry/creator/
  account gate روی read/write/recommend و history CAS. migration bb11b02b0001؛
  legacy ثابت fail-closed بدون حذف snapshot/answer. PostgreSQL regression و
  [قرارداد/rollback](docs/security/questionnaire-proof.md)؛ ظاهر/scoring/حذف حساب UI ثابت.


### Changed

- US-11.T02A.2: هویت مستقل UUID حساب، profile و مالکیت session/history نرمال،
  token متصل به همان نسل و status تازه DB. snapshot قبلی و UI/scoring ثابت.
  migrationهای افزایشی aa11b02a2001/2 با backfill تکرارپذیر، partial unique/composite FK،
  rollback guard، تست PostgreSQL و [runbook](docs/database/account-identity-migration-runbook.md).
  پس از cutover توقف/restart همه writerها و ورود مجدد لازم؛ C/OTP-flow/purge/archive جدا.


### Added

- US-11.T02A.1: قرارداد هویت account UUID، active/archived و یک active phone،
  ERD هدف مستقل، روابط 3NF/account owner و طرح migration/backfill/rollback نسل‌ها؛
  [ADR 0008](docs/adr/0008-account-identity-lifecycle.md).
  ردیف A.1/A.2 قابل جست‌وجو به guide افزوده شد. طراحی فقط؛ model/migration/runtime/
  UI/scoring/data تغییر نکرده، F01/F02 هنوز باز و اجرای persistence در A.2 است.


### Changed

- US-11.T01 owner decisions: PD01–PD08 و ترتیب زیرتسک‌های مستقل T02A–H
  برای هویت نسلی حساب، proof، نشست یک‌ساعته، اصلاح جریان ورود بدون OTP تکراری،
  raw purge۳۰دقیقه، bookmarks حساب‌محور، archive و transport gate ثبت شدند.
  سیاست مصوب از runtime فعلی/موارد باز جدا شد؛ [guide](docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md).
  فقط docs؛ هیچ migration، رفتار، حذف داده یا deploy اجرا نشده است.


### Added

- US-11.T01: مدل تهدید سراسری و بررسی حریم خصوصی/retention با inventory داده،
  شواهد دو client/پاک‌سازی FK و کنترل log، یافته‌های F01–F07 و تصمیم‌های P01–P06.
  [checkpoint](docs/progress/us-11-t01.md). F01/F02 همچنان blocker release هستند؛
  review به معنی رفع یا production نیست. runtime/API/schema/UI/scoring/retention
  و deployment تغییر نکرده‌اند.


### Changed

- US-13 ordering (owner decision, 2026-10-12): ریفکتور فرانت از US-10R به
  US-13 و آخرین داستان، بعد از تکمیل بک‌اند و همه gateهای US-01 تا US-12 منتقل
  شد. وابستگی ریفکتور از US-11/US-12 حذف و شرط پایان کل توسعه همسو شد؛
  همه احتیاط‌های حفظ ظاهر/رفتار پابرجاست. [checkpoint](docs/progress/us-13-plan.md).
  فقط برنامه/مستندات؛ runtime/CSS/API/DB/scoring/deploy تغییر نکرده‌اند.


### Added

- US-10R safeguards: مرجع ثابت کل داستان و هر PR، آزمون اعتبار baseline،
  مقایسه رفتار/شبکه و CSS در dev/build، محیط fixture مستقل و gate توقف/revert
  به جزئیات تسک‌ها افزوده شد. برنامه فقط؛ runtime/CSS/DB تغییر نکرده است.


- US-10R planning: یوزر استوری مستقل ماژولارسازی فرانت پیش از US-11، با چهار
  تسک و زوج‌های کوچک استخراج صفحه/CSS، baseline تصویری و رفتاری مستقل و
  ممنوعیت تغییر ظاهر، React state، CSS cascade، API، DB و scoring.
  [checkpoint](docs/progress/us-10r-plan.md). برنامه‌ریزی فقط؛ T01/refactor
  اجرا نشده، استقرار T07 و بخش آنلاین T081 همچنان بازند.

### Changed

- Owner-directed continuity v13: refreshed the authoritative handoff after merged
  US-10.T05 / PR #103, including durable audit, protected CLI/runbook and exact
  feature/main CI evidence. Preserved historical checkpoints; online T081/T07,
  real providers and production gates remain open. Documentation only: no
  runtime, UI, API, migration, source, scoring or deployment changes.

### Added

- US-10.T05: [راهنمای عملیات و آموزش اپراتور](docs/operations/operations-runbook.md)
  با نمونه command معتبر، بررسی فقط‌خواندنی audit/catalogue، retry و rollback
  و منع ویرایش مستقیم DB. ارجاع‌های تاریخی و مسیر انتشار runbook استقرار به
  CLI محافظت‌شده فعلی متصل شدند؛ runtime/schema/data/scoring/deploy تغییر نکرد.


### Added

- US-10.T04: ابزار داخلی محافظت‌شده با تأیید authority HTTPS/MFA و مجوز تازه،
  اتصال تراکنشی materializer رسمی به audit و آزمون PostgreSQL با نقش محدود.
  [ADR 0007](docs/adr/0007-protected-operations-tool.md). بدون API عمومی یا migration جدید.

### Added

- US-10.T03: PostgreSQL review/version adapters and append-only operations decisions;
  additive `b4d8e1f2a3c5` migration, approval view and real transaction/race verification.
  [ADR 0006](docs/adr/0006-durable-operations-audit.md). No public transport or live catalogue changes.

### Added

- **US-10.T02:** Authorized internal import/review/prepare/approve/publish/rollback use cases reuse the pipeline. Stored clean-import linkage prevents partial or mismatched approval; rollback uses an atomic expected-pointer contract and preserves original evidence. Local/test adapters and targeted security/transition tests accompany [the contract](docs/operations/data-use-cases.md). Owner-authorized independent T02 sequencing is recorded; production adapters/audit/tooling remain T03/T04. No UI/API/schema/scoring/deployment change.

- **US-10.T01:** Explicit least-privilege import/review/approval/publication/rollback/config permissions and a server-owned current-grant authorization port. Unknown, expired, revoked, mismatched and mock/customer identities fail closed; app composition defaults to deny all. Role/permission and public escalation tests, boundary checks and [operations security documentation](docs/operations/authorization.md) accompany it. No management endpoint, operator credential provider, schema/migration, scoring or UI change; T02–T04 retain their enforcement/audit/tool responsibilities.

### Changed

- **Owner sequencing decision (2026-10-11):** Canonical guide permits independent US-10.T01 development after dependency review while US-09.T07 awaits server purchase and online US-09.T081 remains open. Later task dependencies must be separately recorded; US-09 completion, deployment/security gates and the continuity document are unchanged.

### Added

- **US-09.T081 implementation checkpoint:** Added a complete generated OpenAPI/Postman contract, safe synthetic examples, cookie-preserving pinned Swagger, opt-in restricted health schemas, targeted contract/browser checks and CI drift validation. Manual testing, operation coverage and restricted hosting runbook are included. Existing production docs/auth/ownership, data/schema/migrations, scoring and UI are unchanged. Online HTTPS/PostgreSQL publication and two-tester verification remain blocked by missing hosting/access; T081 is not Done.

### Added

- **US-09.T081 planning:** Define a shareable online Swagger or Postman surface for real manual testing of every implemented API before US-09.T07. Include the required restricted HTTPS API/PostgreSQL test environment and reuse it in T07; preserve production docs/auth controls, safe examples, complete operation coverage and drift checks. Feasibility/planning only; no runtime or publication performed.


### Added

- **Task execution protocol (2026-10-10):** Added mandatory dependency/test-environment checks, targeted pre-push verification, evidence-based CI diagnosis and measured time reporting in docs/TASK_EXECUTION_PROTOCOL.md. Root AGENTS.md and the canonical guide require it for every task without weakening existing security or quality gates. Documentation only.


### Changed

- **Owner-directed continuity refresh (2026-10-10):** Version 12 reconciles the handoff with merged PR #93 and successful main CI, records profile/session/history migrations and remaining US-09.T07 deployment gate, and replaces obsolete current/next-task statements. Documentation only; no runtime, data, schema or design changes.


### Fixed

- **US-09.T080:** Clicking the red account-logout control now opens a centered confirmation warning. Choosing «خیر» preserves the verified session; choosing «بله» invokes the existing server-backed logout flow. No API, database, migration, scoring or retention behavior changed.

- **US-09.T079 follow-up:** A signed-in user can now hide a recommendation-history card through a centered warning confirmation. The owner-scoped DELETE API records `hidden_at` instead of deleting the immutable run, items or reasons; hidden runs are absent from that user's list and detail route while remaining available for database administration. The history list uses the same no-menu account header as About and Saved Loans.

- **US-09.T079 follow-up:** Recommendation-history authorization now survives a browser refresh through an HttpOnly, same-site server session cookie; no credential is persisted in browser storage. The browser that creates a questionnaire receives a separate HttpOnly proof cookie, so a session ID alone cannot be attached to an account; the database then atomically binds the verified owner before its immutable history snapshot is written. History pagination uses a stable newest-first cursor, a failed list remains an error rather than an empty state, and the successful empty state reuses the existing saved-loans artwork. Historical results retain the original result controls and no longer alter the result presentation.

- **US-09.T079:** Authenticated recommendation responses are persisted once per questionnaire session as immutable, owner-scoped PostgreSQL history. The authenticated menu now links to paginated recommendation history; cards show the server-created Tehran date/time and ranked-result count. Reopening a run uses the existing result UI without rescoring, keeps all three partitions and returns from loan details to that history entry. Anonymous sessions remain transient and the 30-minute questionnaire retention policy is unchanged.

- **US-09.T078:** The option-card border on `/question/2` is 30% shorter (117px to 82px at the supported mobile viewport), with no change to options, typography, actions, routes, or other questionnaire cards.

- **US-09.T077:** The supplied vector Shahab mark replaces the previous application logo everywhere it is rendered. Existing logo elements, dimensions, layout classes, spacing and page behaviour are unchanged.

- **US-09.T076:** Questionnaire cards now use their content height with an exact 28px inset above the first option and below the last option, while their existing option rhythm is preserved; questionnaire navigation rows sit exactly 28px below each question card and 28px above the end of the page, without artificial empty page height; the home amount selector uses the shared 8px chevron geometry; and the unavailable readiness and AI-analysis actions are visibly disabled in grey.

- **US-09.T075:** Saved Loans now renders the supplied empty-state artwork when no loan is saved, hides filters for zero or one saved loan, preserves `/saved-loans` as the detail return target, aligns the header inset, and gives the document link the same icon as result cards. No API, scoring, data, or storage-policy change.

- **US-09.T074:** صفحهٔ home فقط هدر، منوی همبرگری و بخش ابتداییِ درخواست وام را نگه می‌دارد. بخش‌های آمار، ویژگی‌ها، CTA و footer از رندر صفحهٔ خانه حذف شدند؛ مسیر پرسشنامه، OTP، API، داده‌های PUBLISHED و scoring تغییری ندارند.

- Verified first mock-OTP login now creates the database profile; subsequent logins preserve existing data. Personal-info updates that same profile. Failed creation does not issue access.

### Security

- **US-09.T072:** Replace unprotected phone lookup with owned /profiles/me; writes require server capability. Explicit local/test mock OTP has expiry, quotas and revocation, and is blocked in staging/production. ADR 0010; no real SMS or production authentication.

### Fixed

- **US-09.T072:** Persist personal-info after development verification before analysis; show retryable storage errors, preserve draft and existing avatar/gender, and retain eleven-digit phones. Existing schema reused; no scoring, published loan data or design changes.


### Fixed

- **US-09.T06Z:** دکمهٔ ورود از home حذف شد و فقط منوی مهمان آن را نشان می‌دهد. پس از تکمیل OTP نمایشی، منوی کوتاه کاربر با پروفایل، سوابق درخواست، وام‌های نشان‌شده، درباره ما و خروج نمایش داده می‌شود؛ خروج profile محلی را پاک می‌کند. این تغییر UI-only است و provider احراز هویت، API، session پرسشنامه، داده، scoring، D-005، migration و deploy را تغییر نمی‌دهد.

- **US-09.T06X:** stylesheet فونت دیگر نخستین paint را مسدود نمی‌کند و تصویرهای پایینِ home lazy/async decode می‌شوند. fallback document و Skeletonهای React برای home، پرسشنامه، نتایج/مقایسه و جزئیات با هندسهٔ همان صفحه نمایش داده می‌شوند؛ هیچ داده، API، D-005، scoring، migration یا استقراری تغییر نکرده است.

- **US-09.T06W:** fallback نخستین paint پس از ۵۰ms برای home/refresh افزوده شد، انتظار ثبت پاسخ پرسشنامه Skeleton همان ناحیه را نشان می‌دهد و دکمهٔ «مقایسه کن» با یک انتخاب خاکستری و غیرقابل‌کلیک است. داده، API، D-005، scoring، migration و استقرار تغییری نکرده‌اند.

- **US-09.T06V:** استاندارد Skeleton با تأخیر ۵۰ms برای loading داده در نتیجه، جزئیات و مقایسه اضافه شد؛ متن‌های loading جایگزین شدند. null monetary value دیگر با «تومان» نمایش داده نمی‌شود؛ کارت‌های comparison به جزئیات همان وام می‌روند، ترتیب انتخاب از بیشترین تطابق است و دکمهٔ مقایسه تا دو انتخاب disabled می‌ماند. داده، API، D-005، scoring، retention و استقرار تغییری نکرده‌اند.

- **US-09.T06U:** کاتالوگ مرجع پرسشنامه در lifecycle یک‌بار آماده می‌شود و پاسخ‌های بعدی دیگر آن را query/commit نمی‌کنند. جزئیات یک وام با شناسهٔ همان loan و predicateهای PUBLISHED از PostgreSQL خوانده می‌شود؛ endpoint دیگر کل serving catalogue را برای یافتن یک وام scan نمی‌کند. قرارداد API، داده، D-005، scoring، retention، Redis fallback، UI و استقرار تغییری نکرده‌اند.

- **US-09.T06T:** FastAPI اکنون engine و session factory SQLAlchemy را یک‌بار در lifecycle می‌سازد و فقط در shutdown dispose می‌کند. هر request یک Session مستقل و بسته‌شونده می‌گیرد؛ timing ایمن development فقط endpoint ثابت، status و مدت را log می‌کند. PostgreSQL، Redis fallback، retention، دادهٔ PUBLISHED، D-005، scoring و قرارداد API تغییری نکرده‌اند.

- **Local development:** Compose now publishes Vite on `5173`, avoiding the
  Windows-reserved `4173` range. FastAPI mounts the local source and reloads
  changes under `backend/`, so normal backend edits no longer require an image
  rebuild. No production runtime, API contract, data, or recommendation logic
  changed.

- **US-09.T06S:** endpoint توصیه یک snapshot تأییدشده را فقط یک‌بار می‌خواند و چهار fact واقعیِ کارت را از همان serving catalogue در پاسخ برمی‌گرداند. کارت نتیجه با این خلاصهٔ server-owned دیگر پس از spinner برای هر وام درخواست جزئیات جداگانه نمی‌فرستد؛ شروط کامل فقط در صفحهٔ جزئیات خوانده می‌شوند. داده، score، ضرایب D-005، threshold، session و استقرار تغییر نکرده‌اند.

### Security

- **US-09.T06R:** زنجیرهٔ توسعهٔ Vite به نسخهٔ pin‌شدهٔ امن `8.3.3` ارتقا یافت؛ lockfile نسخه‌های امن PostCSS، nanoid و source-map-js را ثبت می‌کند. `npm audit` نهایی صفر آسیب‌پذیری گزارش می‌دهد. UI، API، داده و استقرار تغییری نکرده‌اند.

### Added

- **US-09.T06Y:** پوشهٔ `docs/runbook/` و runbook استقرار محیط پایدار اضافه شد؛ مسیر PostgreSQL دائمی، publication دادهٔ تأییدشده، FastAPI HTTPS، Netlify، آزمون URL واقعی، restart، backup و rollback را ثبت می‌کند. این تغییر هیچ سرور، secret، داده، API یا deployment واقعی ایجاد نکرده است.

- **US-09.T06Q:** fallback static صفحهٔ mock از `index.html` حذف شد؛ `#root` پیش از mount React خالی است و آزمون واحد و E2E refresh، نبود متن‌های صفحهٔ جعلی را قفل می‌کنند. UI فعال، داده، API، score و استقرار تغییری نکردند.

- **US-09.T06P:** صفحهٔ mock قدیمیِ خارج از runtime حذف شد تا refresh هرگز UI ساختگی نمایش ندهد؛ قاب CTA جزئیات با ارتفاع صریح ۱۱۷px و فاصله‌های قطعی ۳۵/۴۸/۳۴px ساخته و در E2E اندازه‌گیری شد.


- **US-09.T06O:** انقضای session پرسشنامه بی‌صدا با ساخت session تازه و replay پاسخ‌های موجود بازیابی می‌شود؛ کارت «نشست منقضی» نمایش داده نمی‌شود. درخواست‌های هم‌زمان جزئیات یک وام نیز در همان tab deduplicate و cache می‌شوند. قاب CTA جزئیات دارای ۳۵px فاصلهٔ بالا و ۳۴px فاصلهٔ پایینِ نمونهٔ تأییدشده است؛ API، داده، score و استقرار تغییری نکرده‌اند.

- **US-09.T06N:** دکمهٔ تحلیلِ جزئیات اکنون یک toolbar ثابتِ متصل به پایین viewport است و برای آخرین شرط وام فضای مستقل رزرو می‌شود. logoهای مخصوص spinner فقط در همان صفحه بارگیری می‌شوند؛ درخواست واقعی توصیه هم‌زمان با شمارش پنج‌ثانیه‌ای شروع می‌شود، فقط یک درخواست در پرواز می‌ماند و خطا فقط با اقدام صریح کاربر retry می‌شود. دادهٔ PUBLISHED، API، score، session policy و استقرار تغییری نکرده‌اند.

- **US-09.T06L:** کنترل ذخیرهٔ وام اکنون با assetهای تأییدشدهٔ outline/fill قابل toggle است؛ پیام موفقیتِ موقت بالای همان کارت می‌آید. دکمهٔ «تحلیل با هوش مصنوعی» به انتهای جزئیات اضافه شد، state فعال نتیجه در history همان browser برای refresh-detail→Back حفظ می‌شود، دو قانون انتخاب مقایسه اعمال شد و asset بانک ملی با پس‌زمینهٔ شفاف و hash جدید ثبت گردید. API، دادهٔ وام، scoring، provider خارجی و استقرار تغییر نکرده‌اند.

- **US-09.T06J:** متن‌های قابل‌مشاهدهٔ وام در نتیجه/جزئیات/مقایسه رقم فارسی می‌گیرند؛ border و درصد تطابق کارت فقط بر پایهٔ همان درصدِ server-owned در پنج بازهٔ مصوب رنگ می‌گیرند؛ دکمهٔ /compare-result «تحلیل با هوش مصنوعی» است؛ و SVG کنترل‌شدهٔ بانک ملی با encoding قابل‌رندر و hash جدید ثبت شد. داده، API، score، threshold، D-005 و استقرار تغییر نکرده‌اند.
- **US-09.T06I questionnaire layout alignment:** `/personal-info` and `/verify-code` now use the same responsive content rail, stage-board dimensions, actions, and symmetric side margins as the preceding questionnaire pages. Browser geometry tests cover desktop and mobile. This is UI-only and does not change profile data handling, OTP, APIs, or recommendation logic.
- **US-09.T06I follow-up:** پاسخ نهایی S13 دیگر صفحه‌های اطلاعات شخصی و OTP را skip نمی‌کند؛ flow کامل پرسشنامه به `/personal-info`، سپس `/verify-code` و spinner پنج‌ثانیه‌ای می‌رسد و فقط پس از آن نتیجهٔ واقعی/fail-closed را درخواست می‌کند.
- **US-09.T06I:** بازگردانی محافظه‌کارانهٔ جریان UI اطلاعات شخصی، کد OTP نمایشی و spinner پنج‌ثانیه‌ای؛ کد ثابت فقط پروفایل محلی را برای منوی همبرگری نگه می‌دارد و پس از پایان به همان نتایج fail-closed/واقعی می‌رود. دادهٔ وام، API، scoring، migration، provider و deployment تغییر نکرده‌اند.
- US-09.T06H comparison-card correction: فقط row «تطابق با وضعیت مشتری» در layout جابه‌جا شد؛ checkbox دست‌نخورده ماند، ارتفاع کارت انتخاب با کارت نتیجهٔ مقایسه برابر شد و center متن/checkbox با E2E تا ۱px هم‌راستا کنترل می‌شود.
- US-09.T06H comparison return follow-up: بازگشت از نتیجهٔ مقایسه، checkbox وام‌های واقعیِ انتخاب‌شده را از حافظهٔ همان tab سبز نگه می‌دارد؛ URL و web storage برای این انتخاب‌ها استفاده نمی‌شوند و Playwright مسیر بازگشت را کنترل می‌کند.
- US-09.T06H compare-result alignment follow-up: عنوان وام در کارت نتیجهٔ مقایسه اکنون از همان title row کارت‌های دیگر استفاده می‌کند؛ آزمون browser برابری مختصات عمودی آن با کارت نتایج را تا تلرانس ۱px کنترل می‌کند.
- US-09.T06H typography follow-up: عنوان وام در همهٔ کارت‌ها ۲۰٪ ارتفاع خودش بالاتر رفت، ردیف «تطابق با وضعیت مشتری» در انتخاب مقایسه ۲۰٪ پایین‌تر قرار گرفت و عدد/نماد درصد تطابق بدون تغییر نرخ بهرهٔ اعلامی ۲۰٪ بزرگ‌تر شد؛ Playwright نسبت‌های واقعی geometry و font را در desktop/mobile کنترل می‌کند.
- US-09.T06H follow-up: نام کامل بانک بدون ellipsis و هم‌راستا با logo نمایش داده می‌شود؛ بودجهٔ عنوان وام، عبارت چهارکلمه‌ای مرجع را کامل نگه می‌دارد و فقط عنوان بلندتر را کوتاه می‌کند؛ آخرین کارت نتیجهٔ مقایسه نیز حداقل ۲۰px از دکمهٔ ثابت فاصله دارد. تغییر فقط UI/test/docs است و داده، API، migration و scoring را تغییر نمی‌دهد.
- US-09.T06H follow-up: نام بانک و عنوان وام در همهٔ کارت‌ها تک‌خطی شدند، checkbox مقایسه در راست ثابت شد، برای نوار ثابتِ مقایسه فضای scroll رزرو شد و stacking/overflow فیلترها بدون workaround قطع pointer اصلاح شد؛ تست هندسی و screenshot موبایل/دسکتاپ با ۱۰ وام افزوده شد. داده، API، migration و scoring تغییر نکردند.
- US-09.T06H: یک component مشترک هویت بانک با box ثابت logo، نام مستقل و عنوان مستقل برای همهٔ کارت‌های نتیجه، مقایسه و جزئیات؛ بدون تغییر داده/API/migration یا scoring.
- US-09.T06F: نگهداری ۲۹ SVG تأییدشدهٔ بانک در assetهای کنترل‌شده، ثبت key/hash در serving facts و نمایش از مسیر پایدار برنامه.
- US-09.T06G: مسیرهای URL-safe برای SVGها، نمایش RTL پایدارِ درصد و کنترل browser برای هر فیلتر.


### Fixed

- **US-09.T06K:** On `/loan-results`, bank choices now scroll after four bank names, the existing server-supplied low-compatibility partition is presented from its highest displayed score to lowest, and every card has a tab-local save bookmark with a two-second `#BFFFE9` confirmation. The disabled header CTA now reads «بررسی آمادگی دریافت وام». No loan data, API contract, score, threshold, engine ranking or deployment behavior changed.

- **US-09.T06G follow-up:** Decoded the controlled bank-logo payloads into renderable SVG bytes, made each internal filename/hash content-addressed, restored logos on comparison-result cards, and enforced the Persian RTL rule that `٪` renders visually to the left of its number (including «نرخ بهره اعلامی»), with browser geometry assertions for result, detail and comparison views.

- **Local full-stack development:** Added a same-origin Vite `/api/v1` proxy,
  Compose-managed frontend/API readiness ordering, packaged runtime contracts, an
  explicit read-only/operator catalogue workflow, focused proxy and opt-in live
  browser tests, and safe local startup/troubleshooting documentation. The host UI
  uses port 4173 to avoid common Windows exclusions. No schema, migration, source
  data, credential, or production deployment behavior changed.

### Added

- **US-09.T06C:** Corrected result-card parity and mobile overflow, Persian number/percent display, centered detail link, safe bank-logo rendering, and the real comparison-route card dependency. No recommendation rule, data import, provider workflow, deployment or continuity checkpoint changed.

- **US-09.T06B:** Extracted the active loan-result and loan-detail screens from the home-page monolith into feature-owned components, retained the approved RTL card/filter layout, and exposed an optional validated public bank-logo URL from the same active `PUBLISHED` loan record. No score, total-interest amount, or loan fact is calculated in the browser; deployment remains T07.


- **US-09.T06A:** Replaced all reachable loan-result, detail, comparison,
  action and explanation prototype data with active `PUBLISHED` PostgreSQL
  serving data. The recommendation API now exposes server-owned highest,
  low-compatibility and needs-review partitions with deterministic ordering;

- **US-09.T071:** Added browser-local saved loans, editable profile fields and About page; PR #85 also introduced profile API and the user_profiles migration. Scoring and published loan data were unchanged.


Sidebar owner clarification: show the server profile name; use «کاربر» for a phone-only profile without a name. Refresh the owned profile when opening the menu with a valid capability. Personal-info uses the confirmed server response. Browser regression verifies named and unnamed profiles.

## US-09.T073 — Local OTP request repair (2026-10-09)

Owner reported failures in both login and personal-info on local Docker. Reproduced local API 503 with the new mock flag absent (old-container environment). Local/test now default to fake OTP 123456; explicit false still disables it, and staging/production remain fail-closed. This supersedes T072's opt-in-only local default without enabling real SMS or production authentication. The profile client honors VITE_SHAHAB_API_BASE_URL for every request. Existing schema, design, icons, About text, D-005 and published source data remain unchanged. New CI browser integration runs against real FastAPI/PostgreSQL through Vite, not API route fixtures. See Docker runbook for non-destructive container recreation.

## US-11.T02D — اصلاح OTP تکراری

- personal-info نشست معتبر را از سرور می‌خواند، profile جاری و phone readonly، ذخیره مستقیم بدون OTP؛ مهمان/منقضی همان flow موجود.
- خطای restore/storage حفظ draft و retry؛ probe دیررس پس از logout actor را بازنمی‌گرداند؛ raw TTL با replay تمدید نمی‌شود.
- unit و regression مرورگر عمومی/واقعی PostgreSQL؛ هیچ CSS، asset، schema یا scoring تغییر ندارد. جزئیات و وضعیت gate در [checkpoint](docs/progress/us-11-t02d.md) و PR #112.

### اصلاح پیش از مرج US-11.T02D — شماره متفاوت

- personal-info نام و شماره حساب فعلی را پیش‌فرض دارد؛ شماره یکسان بدون OTP و شماره تغییرکرده تنها پس از OTP همان شماره ادامه می‌یابد. شماره profile همچنان immutable است.
- Back شماره draft را حفظ می‌کند؛ account/profile/history قدیمی rename یا منتقل نمی‌شوند؛ حساب شماره جدید از OTP تأییدشده انتخاب می‌شود. regression واقعی PostgreSQL افزوده شد.

