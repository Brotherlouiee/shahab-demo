Warning: truncated output (original token count: 15286)
Total output lines: 427

# Changelog

- اصلاح فاصلهٔ افقی لوگو و فلش بازگشت در هدر صفحهٔ جزئیات سوابق؛ آزمون مرورگری برای viewportهای موبایل و دسکتاپ افزوده شد. [جزئیات](tests/e2e/loan-details.spec.mjs)

- سند جامع اکنون صف شش باگ گزارش‌شده را با ترتیب فرانت‌اند سپس جریان/API، معیار پذیرش و مرز تشخیص علت ثبت می‌کند؛ رجیستری و شناسه‌های US-13 بدون تغییر ماندند. این commit فقط مستندات است و رفع باگ‌ها هنوز انجام نشده است. [سند جامع](docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md)

- ثبت خط مبنای US-13.T01 روی `main` با SHA `5d4eb6c4545b68736f567d71998656e2f848ba7a`: workflow مستقل مقایسهٔ ۹ نمای اولیه با نسخهٔ منجمد موفق شد و artifact، صفر اختلاف بایت تصویر و geometry برابر را نشان داد. پوشش route/stateهای تعاملی و گزارش فاصله‌های بدون گام بازتولید صریحاً باز ماندند؛ runtime و CSS تغییر نکردند. [سند baseline](docs/ui/us-13-t01-frontend-baseline.md)

- شواهد US-11.T05: backup موجود #150 با GPG AES256 رمز شد؛ decrypt و SHA-256 برابر اصل بود و restore ایزوله PostgreSQL 16 موفق شد (revision ff11b02f0001، ۲۰ نشست). آزمون‌های cleanup/hidden/archived و rollback/retry/هم‌زمانی از suite PostgreSQL موجود ارجاع شدند؛ production تغییر نکرد. ثبت زمان restore و تعیین هدف RPO/RTO برای دامنه فعلی لازم نیست و به آینده موکول شد؛ بار گسترده و scheduler عملیاتی نیز موکول‌اند. [checkpoint](docs/progress/us-11-t05.md)

- بررسی عملیاتی محدود US-11.T04: لاگ‌های پالایش‌شدهٔ API و NGINX، ۱۵ پاسخ 503 درخواست OTP با علت نامشخص به‌دلیل در دسترس نبودن لاگ کانتینر قبلی، و سلامت فعلی HTTPS=200 ثبت شد؛ هیچ تنظیم production تغییر نکرد. [checkpoint](docs/progress/us-11-t04.md)

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows Semantic Versioning when production releases begin.

## [Unreleased]

- فاصلهٔ کارت جزئیات وام تا هدر به ۸ پیکسل کاهش یافت.

- فاصلهٔ کارت جزئیات وام تا هدر نصف شد؛ اندازهٔ بصری آیکن‌های شبکه‌های اجتماعی در صفحهٔ تماس با ما هم‌تراز شد و آزمون‌های مرورگر هندسهٔ هر دو مورد را کنترل می‌کنند.

- در refresh نتیجه یا مقایسه، تا زمان بازیابی snapshot از API حالت بارگذاری نمایش داده می‌شود؛ پیام «نتیجه در دسترس نیست» فقط پس از تشخیص واقعیِ نبود نتیجه یا خطای بازیابی می‌آید. آزمون مرورگر نیز نبود پیام خطای گذرا را پس از refresh بررسی می‌کند.

- اصلاح باگ‌های فرانت و جریان: دکمهٔ تحلیل هوش مصنوعی در انتهای مقایسه واقعاً disabled و خاکستری شد؛ متن گزینهٔ `/question/2` اصلاح شد؛ مقایسه از نتیجهٔ تاریخچه به همان snapshot وصل شد. پاسخ‌های canonical نشست و شناسهٔ وام‌های انتخاب‌شده از API/`history.state` بازیابی می‌شوند تا refresh نتیجه و مقایسه پرسشنامه را از ابتدا نخواهد. آزمون مرورگر با PostgreSQL واقعی افزوده شد. تصویر شفاف بشقاب‌پرنده با PNG همان‌اندازه و پیکسل‌به‌پیکسل برابر بهینه شد: ۱٬۰۵۹٬۱۸۸ بایت به‌جای ۱٬۱۵۸٬۴۷۵ بایت (۸٫۶٪ کاهش)؛ بارگذاری تصویر خالی اولویت بالاتر و رمزگشایی ناهمگام دارد. API و schema بک‌اند تغییر نکردند؛ انقضای ۳۰ دقیقه‌ای نشست مطابق سیاست موجود باقی است.

- بررسی محدود امنیت (US-11.T03): توسعهٔ اختیاری ابزار خواندنی موجود از چهار به شش GET برای artifactهای تنظیمات/Git، تشخیص SPA fallback و پالایش خطای شبکه؛ ثبت شواهد SAST/SCA و candidate پاک و بازماندن رفع عملیاتی brotli در image مستقر. اجرای شش GET روی VM با findings=[] موفق شد؛ استقرار v0.1.3 و رفع HIGH با brotli-libs=1.2.1-r0 و musl/musl-utils=1.2.6-r3، healthy دو image و HTTPS health=200 از خروجی مالک تأیید شد؛ بدون تغییر کد runtime/API/DB یا اسکن گسترده.

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

- Test (US-12.T02): اجرای همهٔ unitهای فرانت با discovery، اصلاح harness تست dedupe و انتقال journey کامل به suite واقعی FastAPI/PostgreSQL با فرم/OTP و selectorهای جاری؛ ثبت پوشش و محدودیت شواهد مستقل از سرور، بدو…5286 tokens truncated…greSQL history. The authenticated menu now links to paginated recommendation history; cards show the server-created Tehran date/time and ranked-result count. Reopening a run uses the existing result UI without rescoring, keeps all three partitions and returns from loan details to that history entry. Anonymous sessions remain transient and the 30-minute questionnaire retention policy is unchanged.

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

