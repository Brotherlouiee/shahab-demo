# قرارداد ساخت ایمیج — US-12.T04A.1

مبنا: `6500ec6ac1b135568705bc91f715b25dcbf0977b` پس از #137. این مرحله فقط build/run ایزوله است؛ نشر Docker Hub، SBOM/provenance/اسکن container و سیاست release در T04A.2/.3، مصرف digest در .4 و استقرار در تسک‌های سرور باقی می‌مانند. هیچ حساب/توکن Docker Hub برای A.1 لازم نیست.

## دو build از ریشهٔ مخزن

```sh
docker build -f Dockerfile -t shahab-api:local-smoke .
docker build -f frontend/Dockerfile -t shahab-frontend:local-smoke .
```

Dockerfile موجود ریشه برای API بدون تغییر است: Python3.12، نصب از pyproject، کد backend، Alembic و contracts، user10001 و Uvicorn8000؛ startup خود image migration یا publication انجام نمی‌دهد. PostgreSQL/دادهٔ مصوب/env واقعی هنوز به محیط نیاز دارند؛ liveness به معنی readiness داده نیست. نسخه‌های Python فعلی range دارند و پایهٔ backend tag است؛ pin/scan/provenance و بازتولیدپذیری کامل زنجیره در A.2 بررسی می‌شود، نه تضمین ساخت بایت‌یکسان در A.1.

frontend/Dockerfile مستقل است: Node22 با digest ثبت‌شده → npm ci از lockfile موجود → npm run build → فقط dist در `/srv/shahab` داخل NGINX unprivileged با digest ثابت و UID101/port8080. Node، node_modules و source/backend/raw وارد final-stage فرانت نمی‌شوند؛ هیچ build arg برای secret یا URL داخلی وجود ندارد. API همان `/api/v1` پیش‌فرض کلاینت است. dependency و source/CSS/asset عوض نشده‌اند.

هر دو context ریشه‌اند اما ignore اختصاصی دارند: Dockerfile.dockerignore فقط pyproject/README/backend app/Alembic/contracts را می‌فرستد؛ frontend/Dockerfile.dockerignore فقط ورودی‌های واقعی Vite، src/assets/public/contracts و config NGINX. `.env*`، .git، node_modules، dist قبلی، اسناد منابع خام و تست‌ها از contextها بیرون‌اند. root .dockerignore حفظ شده؛ ignore اختصاصی طبق قرارداد Docker بر آن مقدم است. فایل مرجع canonical در Git حذف/تغییر نمی‌کند.

## اجرای static و اتصال API

برای دیدن static روی پورت محلی جدا از Compose:

```sh
docker run --rm -p 127.0.0.1:8080:8080 shahab-frontend:local-smoke
```

SPA direct entry/refresh در مسیرهای فعلی به همان index می‌رسد؛ فایل گمشدهٔ assets→404. تا proxy تنظیم نشده، `/api/v1/*` صریحاً JSON503/no-store است؛ هیچ API به index.html نمی‌افتد و هیچ آدرس داخلی/credential در bundle نوشته نمی‌شود. این اجرای static جریان full-stack یا OTP واقعی نیست. Dev Compose روی5173 و Netlify فعال همچنان همان قبلی‌اند.

برای محیط مجاز، فایل بازبینی‌شده با mount فقط‌خواندنی روی `/etc/nginx/shahab-api.conf` جایگزین پیش‌فرض شود. [api-https.conf.example](../../frontend/nginx/api-https.conf.example) نمونهٔ **غیرفعال** با دامنه .invalid است: HTTPS upstream با verify/SNI و CA معتبر، حفظ مسیر کامل، method/body/Origin/Cookie/Set-Cookie و Host مرورگر؛ بدون cache، retry خودکار mutation یا تبدیل خطای API به HTML. مقدار secret در این config نباشد. trust store خصوصی در mount جدا، نه در image عمومی قرار گیرد.

این نمونه incoming TLS را ایجاد نمی‌کند. اگر TLS در ingress دیگری terminate می‌شود، scheme/host خارجی فقط از همان proxy مجاز به‌صورت بازبینی‌شده بازسازی و Uvicorn تنها proxyهای دقیق مجاز را trust کند؛ هدر دلخواه کاربر مرجع نیست. نمونه عمداً X-Forwarded-* ورودی را بازنشر نمی‌کند. `FORWARDED_ALLOW_IPS=*`، حذف Origin، wildcard CORS یا خاموش‌کردن TLS verify راه اتصال نیست. same-origin/CSRF و cookie واقعی Secure/HttpOnly/SameSite در گیت آنلاین [T03](../runbook/preview-smoke.md) اثبات شوند. NGINX access log فقط method/status است؛ sink/error-log و redaction واقعی همچنان گیت محیطی US-11.T04 دارند.

## شاهد قابل بازتولید A.1

روی محیط Docker آزمایشی، ابتدا reference مستقل از همان revision با Node22/lockfile بسازید و سپس harness را اجرا کنید:

```sh
npm ci
npm run build
python tests/images/smoke.py
```

Harness دو image را با docker build می‌سازد و UID تنظیم‌شده/اجرایی را بررسی می‌کند؛ network/container/tag موقت یکتا دارد، فقط localhost را publish و تنها منابع همان اجرا را cleanup می‌کند؛ هیچ volume/DB کاربر mount، prune یا reset نمی‌شود. API با staging، بدون DB و live sender خاموش اجرا می‌شود: health200، catalogue503، profile401 و درخواست ورود503؛ این آزمون محصول با کاتالوگ نیست و migration اجرا نمی‌کند.

برای فرانت، مسیر/refresh/MIME/asset و API503 بررسی و **تمام فایل‌های dist داخل image با SHA256 با build مستقل برابر** شوند. fixture HTTPS مصنوعی با cert/key موقت خارج Git، حفظ Host/path/query/method/body/cookie و عدم پذیرش X-Forwarded جعلی را می‌سنجد؛ CA نامعتبر باید502 بدهد. fixture انتقال header را ثابت می‌کند، نه احراز هویت واقعی، cookie jar مرورگر، TLS دامنهٔ مالک یا deployment. هیچ شماره/credential واقعی و هیچ SMS وجود ندارد.

workflow کوچک `image-smoke.yml` این harness را در runner اجرا می‌کند؛ فقط read permission و build/test، بدون login/push/tag/release و بدون secrets. این job هفتم **علاوه بر شش چک موجود** است؛ workflowهای قبلی تغییر نمی‌کنند. قرارداد کامل buildx/cache/scan و tagهای مصوب هنوز A.2 است. artifact `image-smoke.json` فقط SHA سورس، local image ID، شمارش فایل و نتیجه دارد؛ local ID، registry manifest digest یا شاهد انتشار نیست. نگهداری artifact هفت روز مطابق گیت‌های فعلی است.

مرجع فنی: [Docker build context/ignore](https://docs.docker.com/build/concepts/context/)، [NGINX unprivileged](https://github.com/nginx/docker-nginx-unprivileged)، [HTTPS proxy](https://nginx.org/en/docs/http/ngx_http_proxy_module.html). digestهای پایهٔ جدید در ۲۰۲۶-۱۰-۱۸ از metadata عمومی Docker Hub خوانده شدند؛ scan امنیتی نهایی هنوز ادعا نمی‌شود.

Rollback کد packaging با PR revert همین تغییر انجام می‌شود؛ Compose/source/schema/data ثابت‌اند و migration/volume اقدامی ندارد. پس از پذیرش/مرج و build/run موفق، nextTaskId=`US-12.T04A.2`؛ مرج مجوز نشر/استقرار نیست.
