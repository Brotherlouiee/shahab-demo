# رفع همهٔ یافته‌های runtime — ادامهٔ US-12.T04A.3

## آغاز و قرارداد

- درخواست مالک: «همه را اصلاح کن»؛ بدون پذیرش موقت ریسک. مبنا main پس از مرج #141 برابر `92a03ea375c50cf6e0259be09b53811c977b7626` و artifact واقعی `12170263586` در run `39217946817`؛ API شش Medium/یک Low و web دو Medium، هر دو High/Critical صفر.
- علت با scan/inventory اثبات شد: pip25.0.1 نصب‌شده در **Python پایه** با مسیر `usr/local/lib/python3.12/site-packages/pip-25.0.1.dist-info/METADATA`؛ venv پروژه pip ندارد ولی base دارد. zlib1.3.2-r0 هر دو image و libxpm3.5.19-r0 فرانت باقی‌اند. OS واقعی Alpine3.24.2 است.
- سه قانون طلایی: مرحله محدود با بودجهٔ بستن چرخه؛ کل guide از ابتدا تا انتها بازخوانی شد (blob `cf716dba4d7ac3f2fab2e4ce6ec97db593f8a5c6`)، AGENTS، protocol و skill همکاری ایمن خوانده شدند؛ Done فقط پس از تست/docs/CHANGELOG/commit و شواهد scan واقعی. هیچ تغییر منبع/موتور/داده‌ای نیست؛ inventory منابع قبلی محفوظ است.
- estimatedWorkScope: حذف ابزار نصب غیرلازم از stage نهایی backend، دو APK اصلاحی pinشده، بررسی regression inventory و scan/اجرای واقعی هر دو image، docs/CHANGELOG/یک PR. build stage و dependencyهای قفل‌شدهٔ برنامه، base digestها، UI/API/schema/data/scoring و guide/US-13/continuity ثابت‌اند.
- completionBudget: اصلاح کوچک و یک دور CI؛ اگر APK دقیق در repository رسمی همان Alpine موجود نباشد، شواهد علت و کوچک‌ترین راه معتبر بررسی می‌شود؛ مخلوط‌کردن edge، tag شناور، ignore، skip یا پذیرش ریسک حدسی ممنوع است.
- معیار: هر ۹ یافتهٔ گزارش‌شده واقعاً رفع، هیچ finding جدید با scan تازه، import/native/PostgreSQL و API/static/TLS smoke همان imageها موفق؛ native ABI، USER/CMD/config سابق حفظ؛ پس از push هر هفت CI روی head نهایی سبز.
- محیط: Docker محلی موجود نیست؛ تست policy/lint/secret محلی، build و اجرای واقعی و scan در runner GitHub. mock شاهد رفع image نیست. DB/volume/secret واقعی مالک mount یا تغییر نمی‌کند.
- مالکیت: worktree تازه clean و شاخه Codex `fix/container-runtime-findings`؛ هیچ تغییر پوشه قبلی یا main، merge/deploy/publish image انجام نمی‌شود. rollback با revert PR بسته‌بندی بدون migration/reset است.
- زمان: از آغاز بررسی در ابزار ثبت شده؛ بخش خواندن کامل راهنما و منابع، implementation/test/docs، CI و تکرار با علت در PR پایان تفکیک می‌شوند. خروجی اولیه راهنما/یک URL موقت artifact بریده یا منقضی بود و دوباره درست خوانده شد؛ scan یا CI برای این موضوع rerun نشد.

## بررسی و patch

- APKINDEX رسمی `https://dl-cdn.alpinelinux.org/alpine/v3.24/main/x86_64/APKINDEX.tar.gz` به‌صورت فقط‌خواندنی بررسی شد: zlib1.3.2-r1 و libxpm3.5.20-r0 موجود؛ libexpat/libx11 قبلی نیز همان نسخه‌اند. تلاش اولیه URL با patchlevel سیستم‌عامل (v3.24.2) 404 بود؛ شاخهٔ صحیح v3.24 استفاده شد، نه تغییر به edge یا fallback شناور.
- Dockerfile backend فقط runtime را patch و pip نصب‌شده/ensurepip را واقعاً حذف می‌کند؛ global Python نبود هر دو را assert می‌کند. frontend فقط دو APK اصلاحی دیگر می‌گیرد. stage build و همان ۲۸ نسخهٔ برنامه ثابت‌اند.
- guard inventory واقعی در scanner و یک آزمون regression با حالت‌های installer برگشته، بسته غایب و نسخه قدیمی اضافه شد. ۱۹ آزمون policy و ruff موفق‌اند؛ تست مصنوعی شاهد image نیست. اسکن کامل هر دو image و API/DB/TLS/static-byte و archive روی CI لازم‌اند.
- ریسک باقی‌مانده: ABI/رفتار بسته‌های پایه و دسترسی نسخهٔ دقیق؛ همین smoke موجود روی image نهایی اثبات می‌کند. نسخهٔ قدیمی package با حذف SBOM/CVE یا ریسک‌پذیری عبور داده نمی‌شود. عدم وجود Docker محلی صریح است؛ runbook جدیدی برای محیط مالک/سرور ساخته نمی‌شود.
