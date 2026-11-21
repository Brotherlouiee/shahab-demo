# ادامهٔ US-09.T081 — آمادگی محیط محدود آنلاین

> **تصمیم جدید مالک، ۲۰۲۶-۱۰-۲۱:** طرح VM، زیردامنه، تونل و دسترسی SSH آزمایشی این سند دیگر مجاز به اجرا نیست. محیط آزمون فقط Docker/WSL لپ‌تاپ است؛ production نباید تغییر کند. authority انتشار نیز آماده نیست و import/publish انجام نمی‌شود. مشاهده‌های خواندنی VM زیر فقط سابقهٔ ممیزی‌اند. نتیجهٔ آزمون محلی در [checkpoint جدا](us-09-t081-local-verification-2026-10-21.md) ثبت شده است؛ پذیرش آنلاین T081 باز است.

**وضعیت: پیش از provisioning؛ آزمون‌های مثبت و دوحسابی همچنان بازند.** این checkpoint ادامهٔ ممیزی [قبلی](us-09-t081-online-audit-2026-10-21.md) است. PR #148 در ۲۰۲۶-۱۰-۲۱ ساعت ۰۸:۰۷ UTC مرج شد؛ مبنای این بررسی `main@14bef9c427b20198c36f1f4affe29c30d78918e9` است. شروع ثبت زمان این نوبت ۰۸:۲۱:۱۹ UTC است؛ زمان پیش از آن ثبت نشده است. هیچ سرویس، داده، DNS، secret یا تنظیم production تغییر نکرد.

## محدوده و حداقل اثبات

هدف، یک محیط **test آنلاین محدود و مستقل** برای اجرای دستی قرارداد همان image است. تغییر UI، scoring، API عمومی، migration قدیمی، دادهٔ مصوب یا production در این مرحله مجاز نیست. حداقل اثبات پذیرش: HTTPS قابل استفاده برای دو آزمونگر مجاز، رد دسترسی شخص ثالث به docs/schema/API، PostgreSQL و secretهای مجزا، انتشار رسمی داده/config، درخواست واقعی همهٔ ۱۹ مسیر، کنترل دو نشست/مالکیت و بازخوانی ماندگاری پس از restart فقط در test. CI یا health جای این اثبات نیست.

## مشاهدهٔ خواندنی تازه از VM

| مورد | مشاهده و نتیجه |
| --- | --- |
| ظرفیت | دو vCPU؛ RAM کل ۳۹۱۷ MiB و available برابر ۳۱۷۶ MiB؛ دیسک `/home/shahab` روی پارتیشن ۲۳ GiB با ۱۹ GiB آزاد و بدون swap. مجموع حافظهٔ چهار کانتینر در لحظهٔ نمونه‌برداری حدود ۱۲۹ MiB بود. این ظرفیت امکان بررسی stack دوم را می‌دهد، ولی تعهد ظرفیت تحت بار نیست. |
| جداسازی فعلی | فقط پروژهٔ Compose `shahab-prod` با دو شبکهٔ `app`/`data` و volume نام‌دار `shahab-prod_postgres_data` دیده شد. پوشهٔ استقرار آزمایشی زیر `/home/shahab` وجود ندارد. چهار سرویس production حدود ۴۲ ساعت healthy بودند؛ API/DB/Redis پورت عمومی ندارند و frontend به `127.0.0.1:8080/8443` bind است. |
| ترافیک | NGINX میزبان روی ۸۰ فعال و برای دامنهٔ production به frontend loopback proxy می‌کند؛ CDN آروان جلوی دامنه است. در خطوط فعال NGINX، `real_ip_header` یا `set_real_ip_from` دیده نشد؛ بنابراین allowlist کاربر بر پایهٔ IP در NGINX پشت CDN، بدون تنظیم/اثبات لایهٔ trusted IP، قابل اتکا نیست. `GET /api/v1/health/live` از دامنهٔ HTTPS پاسخ ۲۰۰ و TLS verify=0 داد. |
| کد و DB | digestهای production همان جفت v0.1.0 ممیزی قبلی‌اند. Alembic دیتابیس متصل به API `ff11b02f0001 (head)` است. شمار کل `serving_catalogue_versions`، `serving_catalogue_members`، `loan_product_versions` و `recommendation_config_versions` هر یک صفر بود؛ import/migration روی production اجرا نشد. |
| OTP | runtime همچنان `production` است؛ mock، کاوه‌نگار، تأیید قالب و وجود API key همگی false هستند. مقدار secret یا `.env.prod` خوانده/چاپ نشد. |
| ابزار داده | شش منبع رسمی و `scripts.operations_tool` در مخزن موجودند، اما image runtime و پوشهٔ استقرار VM اسکریپت import/منابع خام را ندارند. runbook انتشار مستقیم با `materialize_t05a --publish` را ممنوع کرده و OAuth authority با introspection HTTPS/MFA، نقش‌های جدا و DB role غیرمالک می‌خواهد. وجود چنین authority و مجوز اپراتورها هنوز تأیید نشده است. |

## طرح پیشنهادی، پیش از هر mutation

- **میزبان:** همان VM فعلی، در پوشه و پروژهٔ Compose مستقل مانند `/home/shahab/t081-test` و `shahab-t081-test`. imageهای منتشرشدهٔ موجود با digest ثابت استفاده شوند؛ هیچ image جدیدی به Docker Hub منتشر نشود. API، PostgreSQL و Redis آزمایشی شبکه و volumeهای نام‌دار اختصاصی داشته باشند و به شبکه/volume/secret پروژهٔ `shahab-prod` متصل نشوند. frontend برای آزمون API لازم نیست. API فقط روی loopback یک پورت متفاوت bind شود.
- **HTTPS و محدودسازی:** یک origin جدا مانند `api-test.shahabfintech.ir` با مسیرهای اصلی `/docs`، `/api/v1/openapi.json` و `/api/v1/*`، بدون SPA fallback. قبل از روشن‌کردن mock یا بازکردن docs، DNS/TLS معتبر و سیاست allowlist دقیق دو آزمونگر در لایهٔ آروان یا VPN مجاز اثبات شود؛ خارج از allowlist هر سه گروه مسیر باید رد شوند. چون origin فعلی IP واقعی کاربر را در NGINX تشخیص نمی‌دهد، تغییر فرضی `allow` در NGINX کافی نیست. پیکربندی production و trusted headers موجود حفظ شود.
- **secrets و داده:** فایل خصوصی جدا با مجوز ۶۰۰ یا secret manager، بدون کپی `.env.prod`. `SHAHAB_ENVIRONMENT=test` فقط برای stack جدا و محدود؛ mock OTP فقط بعد از اثبات کنترل دسترسی. این روش مالکیت واقعی شماره یا ارسال SMS را اثبات نمی‌کند. DB تازهٔ test پیش از migration snapshot خالی و سپس backup/restore آزمایشی بگیرد؛ migration موجود فقط تا head یک‌بار اجرا شود. import/review/prepare/approve/publish فقط با منابع رسمی، ابزار محافظت‌شده و authority/نقش‌های مجاز انجام شود. image runtime ابزار و منبع ندارد؛ مسیر اجرای امن ابزار از checkout تأییدشده و DB role محدود باید پیش از publication مشخص شود. هیچ دادهٔ production کپی یا reset نشود.
- **آزمون:** Collection موجود به origin محدود اشاره کند. دو browser context/cookie jar مستقل؛ status و نتیجهٔ مثبت/منفی ۱۹ مسیر مطابق [ماتریس](../api/coverage.md)، proof پرسشنامه، عدم تصاحب/عدم دسترسی متقابل، انقضا، خروج، persisted profile/history/bookmarks و restart فقط stack test ثبت شود. readiness token فقط در بررسی خصوصی اپراتور استفاده شود.

## ورودی‌های لازم و مرز اجرا

۱. تصمیم مالک دربارهٔ origin آزمایشی روی همین VM، روش دسترسی محدود، دو IP/شبکهٔ مجاز و امکان اعمال و آزمودن DNS/WAF آروان. تا اثبات رد دسترسی بیرونی، mock و Swagger روشن نمی‌شوند.

۲. authority عملیات با introspection HTTPS/MFA و دسترسی data-editor/admin مستقل یا تصمیم مشخص برای فراهم‌کردن آن در test، به‌همراه approval انتشار منابع رسمی و محل امن credentialها. بدون آن، publication رسمی و آزمون توصیه/وام ممکن نیست؛ مسیر legacy جایگزین نمی‌شود.

۳. تأیید مسئول ظرفیت/هزینهٔ VM و سیاست backup/restore برای volume آزمایشی پیش از migration و import. استفاده از VM فعلی خرید سرور تازه را پیش‌فرض نمی‌کند؛ نتیجهٔ نمونه‌برداری لحظه‌ای تضمین ظرفیت نیست.

تا دریافت این ورودی‌ها، هیچ endpoint مثبت وابسته به OTP، catalogue، دو حساب یا restart آزموده نشده و T081 **Done نیست**. اسناد امنیتی/مالکیت و سلامت داده برای سبز کردن ماتریس دور زده نمی‌شوند.
