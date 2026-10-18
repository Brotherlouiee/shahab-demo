# Preview و smoke — بخش مستقل US-12.T03

این سند و [نمونه‌ها](../examples/preview/netlify.toml.example) فقط آماده‌سازی‌اند؛ هیچ محیطی را فعال نمی‌کنند. دستورالعمل اصلی [استقرار](production-deployment.md) و ترتیب T081→T07 پابرجاست. اجرای آنلاین T03 در همان «جدول تسک‌های پس از استقرار» [سند جامع](../SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md) باز می‌ماند؛ CI، build یا parse نمونه معادل preview موفق نیست.

## پیش‌نیاز و مرز محیط

| مورد | پیش‌نیاز اجرای آنلاین |
| --- | --- |
| مجوز و نسخه | مالک/اپراتور، بازه و URLهای دقیق مجاز؛ SHA پذیرفته‌شده، digest artifact و CI همان نسخه ثبت شود. پس از US-13 آزمون‌های متأثر روی نسخهٔ نهایی تکرار شوند. |
| سایت/دامنه | preview محدود با دسترسی تست‌کنندگان مصوب؛ DNS و TLS معتبر روی هر دو مسیر browser→frontend و proxy→API؛ دامنه‌های نمونهٔ `.invalid` قابل استفاده نیستند. قابلیت و تنظیم دسترسی حساب میزبان هنگام اجرا بررسی شود. |
| API و شبکه | همان FastAPI با environment=staging، ingress محدود، timeout/body limit و private PostgreSQL/Redis. پورت DB یا API داخلی عمومی نشود. تست روی DB مالک/production ممنوع؛ DB آزمایشی پایدار و backup/restore جدا لازم است. |
| schema و داده | migration مصوب و audit فقط‌خواندنی روی همان DB؛ دادهٔ PUBLISHED و config تأییدشده. publication فقط با مسیر مجاز runbook اصلی؛ migration به‌تنهایی داده نمی‌سازد. SHA/dataVersion/configVersion و revision واقعی ثبت شوند. |
| Netlify | دسترسی config/deploy مجاز، build با Node22 و lockfile؛ publish=dist. تنظیم فعال ریشه در این تسک تغییر نمی‌کند. نمونهٔ proxy پس از بازبینی و مجوز جدا می‌تواند در تغییر استقرار به config فعال تبدیل شود. |
| OTP | تا تأیید واقعی OTP1 و مجوز ارسال، live خاموش و mock در staging ممنوع؛ ورود ممکن است 503 بدهد. عبور ناقص را smoke کامل گزارش نکنید. |

## فایل‌های آماده و محل مقادیر

- [backend.env.example](../examples/preview/backend.env.example): فقط نام env و defaults غیرحساس؛ خالی بودن secrets یعنی **آمادهٔ اجرا نیست**. Settings وجود DB/داده را با parse اثبات نمی‌کند. این فایل را در Netlify یا فرانت بارگذاری نکنید.
- [netlify.toml.example](../examples/preview/netlify.toml.example): نمونهٔ غیرفعال API rewrite پیش از SPA fallback؛ مقصد عمداً نامعتبر است. proxy نهایی باید path/method/body/Origin و Set-Cookie را درست عبور دهد، پاسخ API را cache نکند و API404/503 را به index.html تبدیل نکند.
- [smoke-evidence.json](../examples/preview/smoke-evidence.json): فرم خالی شواهد، نه نتیجهٔ تست. برای هر اجرا در محل خصوصی عملیات کپی شود؛ مقدارهای null/not-run فقط با شاهد همان اجرا تغییر کنند. هیچ loader یا job به این فایل متصل نیست.

| محل | مقادیر مجاز/لازم |
| --- | --- |
| secret store سرور API | SHAHAB_DATABASE_URL با postgresql+psycopg، SHAHAB_REDIS_URL، SHAHAB_READINESS_TOKEN؛ پس از مجوز live، SHAHAB_KAVENEGAR_API_KEY و SHAHAB_OTP_CODE_SECRET مستقل حداقل۳۲کاراکتر. مقدار/URL کلیددار در Git، PR، log یا screenshot نباشد. |
| پیکربندی غیرحساس API | environment=staging، debug=false، operations docs=false، CORS فقط originهای دقیق مصوب، mock=false؛ template=OTP1 و دو flag live=false تا تأیید/مجوز. جزئیات [راهنمای کاوه‌نگار](../operations/kavenegar-otp.md). |
| Netlify build | فقط VITE_SHAHAB_API_BASE_URL=/api/v1؛ این مقدار عمومی و داخل bundle است. هیچ secret سمت API، DB، Redis، readiness یا OTP در VITE_* یا Netlify فرانت قرار نگیرد. |
| provisioning خصوصی | کاربر/رمز DB، backup credentials و کلید مدیریت فقط در سامانهٔ عملیاتی مربوط؛ این نمونهٔ backend جای تنظیم سرویس PostgreSQL/Redis یا secret manager را نمی‌گیرد. |

## شرط سازگاری proxy و cookie

کلاینت فعلی account از credentials=same-origin استفاده می‌کند. API جداگانه در VITE_SHAHAB_API_BASE_URL و CORS به‌تنهایی بازیابی cookie را درست نمی‌کند؛ مرورگر باید `/api/v1` روی همان origin فرانت را ببیند. برای درخواست‌های cookieدار، CSRF server علاوه بر CORS، same-origin را بررسی می‌کند.

**gate قبل از پذیرش proxy:** scheme/host مؤثر در FastAPI باید با HTTPS origin مرورگر برای درخواست‌های cookieدار همخوان باشد. Host و forwarded headers فقط از زنجیرهٔ proxy مصوب پذیرفته شوند؛ API ورودی مستقیم/هدر جعلی را قابل اعتماد فرض نکند. یک rewrite عمومی به‌تنهایی این را اثبات نمی‌کند. اگر میزبان فعلی این قرارداد را حفظ نکرد، اجرا blocked است و config زیرساخت با بازبینی جدا اصلاح می‌شود؛ حذف Origin، شل‌کردن CSRF، wildcard CORS یا تغییر SameSite راه‌حل این تسک نیست.

cookieهای account و questionnaire باید Secure، HttpOnly، SameSite=Lax و Path=/api/v1 باشند؛ Domain به upstream یا wildcard بازنویسی نشود. مرورگر cookie را در origin فرانت دریافت/ارسال کند. HTTPS upstream، HSTS و عدم cache روی success/error API از بیرون اثبات شوند. readiness محافظت‌شده نیز جای audit DB/schema/catalogue را نمی‌گیرد.

## ترتیب smoke پس از استقرار مجاز

تا پیش‌نیازهای T081/T07 و مجوز URLها فراهم نشده این فرمان را اجرا نکنید. ابزار موجود فقط چهار GET منفی/health، TLS و headerها را بررسی می‌کند؛ OTP، تغییر داده و DAST کامل انجام نمی‌دهد:

```sh
python -m scripts.authorized_staging_security_smoke --authorized-test-origin https://APPROVED_TEST_ORIGIN
```

`APPROVED_TEST_ORIGIN` با origin واقعیِ دقیق و مجاز بدون path/query جایگزین شود. ابتدا origin API و سپس origin فرانتِ دارای proxy، هرکدام با مجوز خود، آزموده شوند. redirect یا TLS نامعتبر/خطای شبکه شکست است؛ با خاموش‌کردن TLS یا دنبال‌کردن redirect دور زده نشود.

| مرحله | شاهد/انتظار لازم |
| --- | --- |
| health و خطا | health/live→200، profiles/me و bookmarks بدون دسترسی→401، مسیر ناموجود→404؛ پاسخ API JSON است، نه HTML. ابزار موجود no-store/nosniff/HSTS و نبود wildcard را می‌سنجد؛ Content-Type/body هم جدا بررسی شود. |
| proof پرسشنامه | با مرورگر تست و دادهٔ مصنوعی session بسازید؛ cookie proof امن دریافت شود، نوشتن و refresh همان session مجاز و مرورگر دوم بدون proof غیرمجاز باشد؛ مقادیر cookie/session در گزارش عمومی ثبت نشوند. |
| داده/توصیه | APIهای موجود و پاسخ‌های canonical مصوب را روی DB تست به‌کار ببرید؛ سه partition، جزئیات و conditions از نسخهٔ PUBLISHED و config همان اجرا؛ نبود داده→503، نه fallback ساختگی. اسناد [API](../api/README.md) و [نقشهٔ T02](../testing/us-12-t02.md) مرجع‌اند؛ fixture CI روی DB مستقر publish نشود. |
| ظاهر و navigation | موبایل390/430 و دسکتاپ1440؛ asset/font/RTL، direct entry/refresh/Back، پرسشنامه و جزئیات بدون تغییر مصوب و بدون console/import/mixed-content error. screenshot بدون دادهٔ شخصی/راز و فقط مرجع پالایش‌شده نگهداری شود. |
| ورود واقعی | پس از تأیید و مجوز مستقل کاوه‌نگار، شمارهٔ تست مجاز: دریافت SMS، verify، profile، refresh/restore، logout و عدم replay؛ account cookie نیز معیارهای بالا را بگذراند. تا آن زمان این ردیف blocked است؛ mock123456 یا environment=local جای آزمون staging نیست. |
| restart | طبق پنجرهٔ مجاز API/proxy و سرویس‌ها؛ health، audit نسخه‌ها، detail و مسیر قبلاً موفق تکرار و دوام DB اثبات شود. تمرین rollback/restore تفصیلی در T04 و گیت آنلاین خودش باقی می‌ماند. |

برای هر ردیف status، UTC، اپراتور، SHA/digest، data/config version و مرجع پالایش‌شدهٔ شاهد ثبت شود؛ raw token، phone، OTP، answer، HAR یا dump DB وارد Git نشود. UI کامل پرسشنامه→فرم→OTP→نتیجه بدون provider تأییدشده همچنان blocked است، حتی اگر API ناشناس توصیه‌گر موفق باشد.

## توقف و تحویل

خطای TLS/proxy/cookie/CSRF، دادهٔ تأییدنشده، نبود backup یا شکست smoke مانع پذیرش است. اجرای mutation یا SMS را متوقف و طبق runbook استقرار rollback کنید؛ reset DB، downgrade حدسی یا تغییر کنترل امنیتی مجاز نیست. این تسک Dockerfile/registry، استقرار، backup rehearsal یا پایان فاز۱ را تحویل نمی‌دهد. مرج آن فقط آماده‌سازی مستقل T03 را می‌بندد؛ برای ادامهٔ مستقل، `US-12.T04` و برای آزمون آنلاین، ردیف موجود جدول پس از استقرار پیگیری می‌شود.
