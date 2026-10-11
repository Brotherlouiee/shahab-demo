# محیط محدود تست آنلاین API — US-09.T081

این سند مسیر اجرایی آمادهٔ استقرار است؛ **هیچ سرور، دامنه یا دیتابیس آنلاین جدیدی هنوز ساخته/آزموده نشده است**. میزبان فعلی Netlify فرانت را build می‌کند؛ Swagger/Postman نیز میزبان FastAPI یا PostgreSQL نیستند.

## ورودی ضروری برای اجرا

مالک باید سرور/حساب دارای دسترسی مجاز، مالک هزینه و سقف آن، دامنهٔ API/TLS، شبکهٔ مجاز برای خودش و تست‌کنندهٔ دوم، و محل امن secretها را مشخص کند. credential را در Git، PR یا متن عمومی قرار ندهید. برای این مرحله، محیط **test یا local کاملاً محدود به تست‌کنندگان** و دیتابیس مستقل از production لازم است. staging/production mock OTP را رد می‌کنند؛ guard را حذف یا محیط عمومی staging را صرفاً به test تغییرنام ندهید.

## راه‌اندازی با مسیر موجود

۱. از SHA دقیق PR پذیرفته‌شده در پوشه و پروژهٔ Compose مستقل سرور استفاده کنید؛ repository و `.env` لپ‌تاپ کاربر را تغییر ندهید. PostgreSQL و Redis خصوصی باشند و API فقط روی loopback/شبکهٔ خصوصی bind شود. هزینه یا سرویس جدید بدون انتخاب محیط مجاز ایجاد نکنید.

۲. ابتدا firewall/VPN یا allowlist دقیق تست‌کنندگان را برای **تمام** مسیرهای host (docs، schema و API) اعمال کنید. HTTPS معتبر را در reverse proxy برقرار کنید و HTTP را redirect کنید. از اینترنت خارج allowlist درخواست بفرستید و ردشدن آن را ثبت کنید. cookie/auth و POSTها از داخل allowlist همچنان باید به API برسند. از token مشترک یا عمومی‌کردن mock برای رفع خطای ورود استفاده نکنید.

۳. Compose و runbook موجود را برای PostgreSQL دارای volume، Redis و API reuse کنید: [Docker runbook](../operations/docker-runbook.md). در `.env` خصوصی و محدود سرور، نام متغیرهای زیر تنظیم می‌شوند؛ مقدار secret در مستندات نیست:

```text
SHAHAB_ENVIRONMENT=test
SHAHAB_API_DOCS_INCLUDE_OPERATIONS=true
SHAHAB_PROFILE_MOCK_OTP_ENABLED=true
SHAHAB_DATABASE_URL
SHAHAB_REDIS_URL
SHAHAB_READINESS_TOKEN
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

از پیش‌فرض `change-me-local-only` خارج توسعه استفاده نکنید. در محیط آنلاین محدود command اجرای API را بدون `--reload` و با یک worker تنظیم کنید: سرویس OTP فعلی در حافظهٔ process است و چند worker/replica نشست یکسان ندارند؛ restart آن نشست حساب را باطل می‌کند. state پرسشنامه و history مطابق سیاست موجود PostgreSQL باقی می‌مانند. این محدودیت را auth production تلقی نکنید.

۴. پیش از mutation دیتابیس موجود، backup/restore و audit را مطابق [runbook استقرار موجود](production-deployment.md) انجام دهید. روی DB انتخاب‌شده، migration موجود `python -m alembic upgrade head` و سپس audit فقط‌خواندنی `python -m scripts.materialize_t05a` اجرا شود. publication فقط با approval ثبت‌شده و command موجود آن runbook انجام شود. اجرای مجدد نباید دادهٔ تکراری تولید کند. این تسک migration، importer یا pipeline دوم ندارد و sourceهای canonical تغییر نمی‌کنند.

۵. reverse proxy مسیرهای `/docs`، `/api/v1/openapi.json` و `/api/v1/*` را روی **یک origin HTTPS** حفظ کند؛ SPA fallback فرانت به این host اضافه نکنید. ترجیح اجرای Swagger در ریشهٔ host است تا cookie path موجود `/api/v1` درست بماند. URL مستندات root_path proxy را می‌شناسد، اما mount زیر prefix جدید نیازمند اثبات cookie path است و از آن به‌صورت خودکار پشتیبانی کامل ادعا نمی‌شود. Authorization، Cookie و Set-Cookie به‌درستی عبور کنند؛ header/query/body حساس در access log ثبت نشود. wildcard CORS و تغییر auth برای Try it out ممنوع است.

۶. API پس از publication restart و به database/config همان محیط متصل شود. liveness یا readiness فعلی به‌تنهایی کافی نیست: audit catalogue و GET detail واقعی، توصیه و بازخوانی history را طبق [راهنمای دستی](../api/manual-testing.md) انجام دهید. localhost/CI جای URL واقعی نیست.

## gate و شواهد

- SHA/image دقیق، URL HTTPS بدون credential، مالک محیط و data/config version ثبت شود.
- بیرون شبکهٔ مجاز، docs/schema و **همهٔ API** رد شوند؛ داخل شبکه مالک و تست‌کنندهٔ دوم وارد شوند.
- ۱۶ عملیات در Swagger باشند؛ درخواست واقعی، cookieهای حساب/اثبات پرسشنامه، مالکیت و رد دسترسی حساب دیگر بررسی شوند.
- پروفایل، snapshot تاریخچه و hide با بازخوانی API/DB همان محیط اثبات شوند؛ خروج 204 و درخواست بعدی 401 باشد.
- جدول [پوشش](../api/coverage.md) با شاهد پالایش‌شده تکمیل شود. کوئیری/توکن/شماره/پاسخ خام را در گزارش مشترک ثبت نکنید.
- T07 همین API و PostgreSQL را reuse می‌کند؛ اتصال Netlify و gate کامل محصول متعلق به T07 است، نه این مستندات.

## بازگشت

برای خطای صرفاً docs، SHA قبلی API را با همان DB و تنظیمات امن برگردانید؛ migration یا دادهٔ تازه‌ای در patch مستندات نیست. خاموش‌کردن `SHAHAB_API_DOCS_INCLUDE_OPERATIONS` health را فقط از schema خارج می‌کند؛ **کنترل ورود شبکه را باز نکنید**. در صورت نشت credential آن را revoke/rotate کنید. rollback داده/migration فقط با backup و مسیر مصوب runbook موجود است؛ volume، history یا catalogue را برای اصلاح docs reset نکنید.
