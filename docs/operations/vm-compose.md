# اجرای VM با ایمیج آماده؛ بدون build

فایل مستقل [docker-compose.prod.yml](../../docker-compose.prod.yml) همان جفت منتشرشدهٔ
v0.1.0 را با digest مصرف می‌کند؛ هیچ Docker build، npm، pip، source checkout داخل
کانتینر یا dev server روی VM اجرا نمی‌شود. فایل Compose توسعه عوض نشده است.
این فایل آماده‌سازی زیرساخت است، نه شاهد پایان استقرار T081/T07 یا مجوز production.

## فایل‌های لازم روی VM

فایل‌های docker-compose.prod.yml، deploy/vm/nginx.conf.template، deploy/vm/api-grants.sql
و نمونهٔ .env.prod.example کافی‌اند؛ source برنامه و Dockerfileها برای اجرا لازم نیستند.
نگاشت API/frontend از [manifest انتشار](../release/images/v0.1.0.json) است. PostgreSQL16
و Redis7 نیز با digest رسمی pin شده‌اند. مقصد VM باید Linux x86_64 و Docker Engine
با Compose v2.20+ یا نسخهٔ سازگار جدیدتر باشد؛ image فعلی فقط linux/amd64 منتشر شده است.

| سرویس | نقش | دسترسی |
| --- | --- | --- |
| فرانت | NGINX غیرروت، static همان image، TLS و proxy هم‌مبدأ | host80→8080 و443→8443؛ پیش‌فرض فقط loopback |
| بک‌اند | FastAPI غیرروت، filesystem خواندنی، trust فقط IP فرانت | بدون port عمومی؛ شبکه app و data |
| پایگاه‌داده | PostgreSQL16 و volume پایدار | فقط data داخلی؛ هیچ port روی VM منتشر نمی‌شود |
| کش | Redis7؛ cache موقت، نه منبع نشست | فقط data داخلی؛ بدون port عمومی |
| مهاجرت | همان image بک‌اند، فقط Alembic upgrade مصوب | profile دستی maintenance؛ در up معمولی اجرا نمی‌شود |

TLS در NGINX همان VM پایان می‌یابد؛ مسیر NGINX→API روی bridge خصوصی همان میزبان
HTTP است و از VM خارج نمی‌شود. API فقط IP ثابت فرانت را برای forwarded headers قبول
می‌کند؛ wildcard اعتماد وجود ندارد. X-Forwarded-* ارسالی مرورگر بازنویسی و Host/Origin
حفظ می‌شوند تا Secure cookie و CSRF با HTTPS واقعی هم‌خوان باشند. اگر دو سرویس روی
دو میزبان یا شبکهٔ غیرقابل‌اعتماد قرار گرفتند، این مدل قابل استفاده نیست و TLS upstream
باید جدا طراحی و آزموده شود. این فایل تنظیم Netlify فعلی را تغییر نمی‌دهد.

## تنظیم خصوصی و مرحلهٔ نخست

نمونهٔ .env.prod.example را روی VM به .env.prod کپی و permission را 600 کنید؛ همهٔ
فیلدهای الزامی را خصوصی پر کنید. .env محلی توسعه را استفاده یا source نکنید. envهای
exportشدهٔ shell بر فایل Compose اولویت دارند؛ از shell تمیز برای این محیط استفاده کنید.
نه فایل راز و نه خروجی کامل compose config در Git/چت/artifact منتشر نشود؛ برای validation
از config --quiet استفاده کنید. کلید Docker Hub نیز در این فایل نیست.

آدرس SHAHAB_DATABASE_URL متعلق به role جداگانهٔ shahab_api است، نه POSTGRES_USER؛
آدرس SHAHAB_MIGRATION_DATABASE_URL فقط متعلق به مالک schema/مهاجرت است. نمونهٔ قالب
URL: postgresql+psycopg://USER:URL_ENCODED_PASSWORD@postgres:5432/shahab؛ رمز باید URL-encode
شود. مقدارها را در محیط خصوصی خود وارد کنید؛ هیچ credential آمادهٔ قابل استفاده عرضه نشده است.

دامنهٔ SHAHAB_PUBLIC_HOST فقط نام DNS با حروف کوچک است؛ scheme/path/port ندارد.
گواهی معتبر همان دامنه و زنجیرهٔ کامل در fullchain.pem و private key در privkey.pem
در پوشهٔ مطلق SHAHAB_TLS_DIRECTORY قرار می‌گیرند. فایل‌ها باید واقعی و قابل‌خواندن برای
UID/GID101 باشند؛ private key را world-readable نکنید. روش مناسب، مالک root و گروه101،
permission640 کلید و750 پوشه است. symlink به فایل خارج از bind mount قابل‌خواندن نیست؛
مسیر export امن گواهی را انتخاب کنید. تمدید گواهی توسط ابزار/اپراتور میزبان و reload
کنترل‌شدهٔ frontend انجام شود؛ این Compose خودکار گواهی صادر یا تمدید نمی‌کند.

نام project پیش‌فرض shahab-prod است. این نام و نام volume در اجراهای بعد ثابت بمانند؛
تعویض project ممکن است DB خالی تازه‌ای بسازد. اگر VM قبلاً DB دارد، قبل از هر اقدام،
volume/نسخه/backup و طرح اتصال همان داده بررسی شود؛ نام volume محلی لپ‌تاپ را کپی نکنید.
POSTGRES_* فقط init دیتابیس تازه را انجام می‌دهد؛ تغییر env رمز volume موجود را عوض نمی‌کند.

## فرمان‌های مرحله‌ای روی VM

پس از تنظیم فایل خصوصی و گواهی و فقط در محیط استقرار مجاز:

```bash
docker login --username shahab2026
```

توکن Read فقط برای pull بک‌اند خصوصی کافی است؛ در password prompt وارد شود، نه command line.
سپس بررسی config، دریافت imageها و راه‌اندازی زیرساخت:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml --profile maintenance config --quiet
docker compose --env-file .env.prod -f docker-compose.prod.yml --profile maintenance pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build --wait postgres redis
```

روی DB موجود، ابتدا audit و backup/restore طبق [راهنمای استقرار](../runbook/production-deployment.md)
لازم است. پس از انتخاب DB صحیح و approval همان مرحله، migration صریح، جدا از up:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml --profile maintenance run --rm migrate
```

این فرمان schema موجود را طبق migrationهای image ارتقا می‌دهد، نه اینکه catalogue مصوب
را وارد کند. اجرای آن روی سرور این PR انجام نشده و صرف وجود این فرمان مجوز اجرا نیست.

پس از migration، در psql خصوصیِ owner یک role مستقل بسازید؛ اگر قبلاً موجود است،
مالکیت/عضویت/مجوزهای آن بررسی شود و نقش یا دادهٔ موجود را overwrite نکنید:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec postgres sh -c 'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

فرمان‌های درون psql برای DB تازه؛ password به‌صورت تعاملی وارد می‌شود:

```sql
CREATE ROLE shahab_api LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;
\password shahab_api
\q
```

سپس grant محدودِ همین نسخه؛ این فایل عملیات/کاتالوگ و DDL را به API واگذار نمی‌کند:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T postgres sh -c 'exec psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < deploy/vm/api-grants.sql
```

role نباید owner، عضو owner/operator یا دارای CREATE روی schema باشد. دیتابیس‌های قدیمی
با PUBLIC grants گسترده نیازمند ممیزی جدا هستند؛ فایل GRANT مجوزهای قبلی را جادویی حذف
نمی‌کند. تغییر schema جدید به review grant نیاز دارد و default grant گسترده ایجاد نشده است.
SHAHAB_DATABASE_URL باید با همین username/password خصوصی تطابق داشته باشد.

پس از schema و role، راه‌اندازی عادی فقط دریافت/اجرای image است:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build --wait
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

فرانت تا سالم‌شدن API شروع نمی‌شود. health وضعیت process را نشان می‌دهد، نه اینکه
loan snapshot، OTP یا تمام مسیر کاربر آماده است. برای بازکردن ورودی عمومی، ابتدا
DNS، firewall، TLS، مجوز محیط و محدودسازی تست‌کنندگان بررسی و سپس SHAHAB_BIND_IP را
صریحاً به IP مجاز یا0.0.0.0 تغییر دهید. subnet app و IP ثابت فرانت با شبکه‌های VM
تداخل نداشته باشند؛ هر دو متغیر با هم تنظیم شوند. پورت DB/Redis/API را public نکنید.

## آنچه با pull/run خودکار انجام نمی‌شود

داده و config رسمی، audit و انتشار serving از مسیر مصوب موجود و با approval مستقل
انجام می‌شوند؛ image runtime اسکریپت‌های import و شش منبع خام را همراه ندارد. این فایل
نه دادهٔ آزمایشی را جای دادهٔ واقعی می‌گذارد و نه importer دوم می‌سازد. بدون publication
ممکن است API داده/توصیه 503 بدهد. ابزار عملیات، نقش/authority و mount منابع متعلق به
[مسیر محافظت‌شده](protected-tool.md) و مرحلهٔ استقرار مستقل است.

OTP فیک همیشه خاموش است. live هم پیش‌فرض خاموش می‌ماند؛ بدون تأیید OTP1 و رازهای
مجاز و آزمون واقعی، ورود ممکن است503 بدهد. API docs تولیدی عمومی نیستند؛ T081 نیازمند
محیط محدود و روش مستقل دسترسی ابزار است، نه روشن‌کردن mock در production.
backup/encryption، scheduler، monitoring و آزمون URL واقعی همچنان gateهای بازند.

برای توقف، stop و برای حذف سرویس‌ها، down بدون حذف volume استفاده شود. rollback
تصویر فقط جفت سازگار با digest و نسخهٔ DB/data/config فعلی؛ هیچ downgrade یا reset
خودکار و حذف volume وجود ندارد. نسخهٔ اول، جفت قبلی ندارد؛ [مرز rollback](image-consumption.md)
و [طرح داده/schema](../runbook/release-migration-rollback.md) برقرارند.

## اثبات و محدودیت

تست config از CLI واقعی Compose استفاده می‌کند؛ image-pair، no-build، عدم port عمومی
DB، جدایی role، trust IP و نبود راز ضروری کنترل می‌شوند. CI موجود، همین Compose را
با override مخصوص آزمون روی imageهای candidate از قبل ساخته‌شده، DB/role مصنوعی و
گواهی مصنوعی اجرا می‌کند: migration، API غیرمالک، TLS معتبر آزمایشی، same-origin،
cookie/proof، رد Origin و هدر جعلی و دوام نشست پس از restart. هیچ SMS یا دادهٔ رسمی
منتشر نمی‌شود. این تست با دریافت واقعی digestهای منتشرشده و استقرار VM یکی نیست؛
دریافت registry متعلق به A.4 است و اجرای URL واقعی پس از provision اثبات می‌شود.

منابع: [Compose services](https://docs.docker.com/reference/compose-file/services/)،
[startup order](https://docs.docker.com/compose/how-tos/startup-order/)،
[NGINX proxy headers](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_set_header).

## بررسی محدود استقرار — US-11.T02H

برای استقرار موجود، `scripts/verify_t02h_host.py` از commit ثابت بازبینی‌شده دریافت، hash بررسی و با Python3 روی خود VM اجرا شود. ابزار فقط وضعیت چهار کانتینر shahab-prod، دستورهای مؤثر NGINX فرانت و listenerهای host را می‌خواند و شش درخواست HTTP محدود به دامنهٔ ثابت shahabfintech.ir می‌فرستد. هیچ `.env`، cookie، کلید، DSN یا بدنهٔ پاسخ چاپ نمی‌شود؛ config کامل نیز به چت/Git منتقل نشود. خروجی PASS/FAIL و digestهای عمومی برای گزارش کافی است.

این فرمان نصب/بازسازی/restart/SQL/SMS ندارد. در FAIL، فقط همان شاهد تحلیل شود و تا مشخص‌شدن اصلاح، تغییر خودکار سرور انجام نشود. روش بررسی جای تست بار یا سیاست جامع DAST نیست؛ rate-limit و timeout/body در حد config مؤثر بررسی می‌شوند و اثبات cookie واقعی از [پذیرش T06](../progress/us-11-t06-kavenegar-otp.md) ارجاع می‌شود. نتیجه در [checkpoint H](../progress/us-11-t02h.md) ثبت می‌شود؛ اجرای محلی/CI جای اجرای VM نیست.

شاهد ۲۰۲۶-۱۰-۲۴: اجرای مالک با شش HTTP request و صفر SMS به `host_checks_passed` رسید؛ config و سرویس تغییر نکردند. SHA ابزار اجراشده و digestهای واقعی در checkpoint H ثبت‌اند. مسیر config نسخهٔ تازه از فرمان کانتینر استخراج می‌شود، نه از فرض مسیر ثابت.

## بررسی هدفمند T03 و یافتهٔ image مستقر

برای شش GET مجاز بدون login/SMS از ابزار موجود `authorized_staging_security_smoke.py --authorized-test-origin https://shahabfintech.ir --include-exposure-checks` استفاده شود؛ فایل از commit ثابت دریافت و hash بررسی شود. ابزار body/secret/cookie چاپ نمی‌کند و profile/history را تغییر نمی‌دهد. نتیجه را با scan/headers/cookie شواهد قبلی مخلوط نکنید.

استقرار frontend v0.1.2 هنوز inventory قدیمی brotli-libs=1.2.0-r1 دارد؛ merge #157 به‌تنهایی آن را اصلاح نکرده است. نسخهٔ اصلاح‌شده از pipeline موجود منتشر، digest ثبت و با backup Compose و حفظ env/volume روی VM جایگزین شود؛ روی VM build، migration، import یا reset انجام نشود. کلید OTP قبلی باید حفظ شود. وضعیت و شاهد رفع در checkpoint T03 ثبت خواهد شد؛ تا آن زمان high شناخته‌شده باز است.
