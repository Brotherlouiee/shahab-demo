# قرارداد ساخت و گیت ایمیج — US-12.T04A.1/.2

A.1 در #138 مرج شد؛ A.2 از main=`d7c8a2d2589aca6abe748be74a1eaa21b5a6c9fe` همان harness را با Buildx/scan/SBOM/provenance تکمیل می‌کند. نشر واقعی Docker Hub در A.3، مصرف digest در A.4 و استقرار در تسک‌های سرور باقی‌اند. حساب/توکن Docker Hub برای build/scan لازم نیست.

## دو build از ریشهٔ مخزن

```sh
docker build -f Dockerfile -t shahab-api:local-smoke .
docker build -f frontend/Dockerfile -t shahab-frontend:local-smoke .
```

Dockerfile ریشه همچنان Python3.12، backend، Alembic و contracts، user10001 و Uvicorn8000 دارد؛ startup migration یا publication انجام نمی‌دهد. در A.2 پایه به Python3.12 Alpine با digest ثابت تبدیل شد: scan پایهٔ قبلی Debian13 در ۲۰۲۶-۱۰-۱۸، ۴۴ HIGH/CRITICAL بدون fixed version داشت؛ پایهٔ Alpine بررسی‌شده صفر مورد در این دو شدت داشت. این نتیجه اسکن پایه است؛ scan نهایی پس از نصب تمام dependencyها در CI الزامی است. تغییر OS/ساخت user فقط packaging است و سازگاری native wheel/SSL/API با smoke همان image سنجیده می‌شود. Compose و CMD/API تغییر نکرده‌اند.

`requirements/image-runtime.lock` بسته‌های transitively-resolved و hashهای دقیق را قفل می‌کند؛ ۲۸ نسخه با لاگ موفق A.1 یکسان‌اند. `image-build.lock` ابزارهای build را pin/hash می‌کند؛ نصب با `--require-hashes --only-binary=:all:` و سپس پروژه با `--no-deps --no-build-isolation --no-compile` است. ابزارهای build فقط در stage ساخت هستند؛ runtime تنها venv بدون pip/build-tool را از همان پایهٔ ABI می‌گیرد. `pip --python /opt/venv/bin/python check` ناسازگاری را رد می‌کند. pyproject و مسیر نصب توسعه دست‌نخورده‌اند. lockها با uv0.12.23 از pyproject، برای Python3.12 روی linux/amd64 تهیه و حل glibc/musl یکسان بررسی شد؛ تغییر dependency باید در PR همراه scan/test و lock جدید باشد. نمونهٔ بازتولید lock (به‌روزرسانی عمدی، نه هر build):

```sh
uv pip compile pyproject.toml --python-version 3.12 --python-platform x86_64-unknown-linux-musl --generate-hashes --only-binary :all: --no-header --no-annotate -o requirements/image-runtime.lock
```

پایه‌ها و dependencyها pin/hash شده‌اند؛ SOURCE_DATE_EPOCH از commit به BuildKit داده می‌شود. NGINX فقط دو APK اصلاحیِ دقیق `libexpat=2.9.0-r0` و `libx11=1.8.14-r0` را به علت دو HIGH واقعی پایهٔ A.1 به‌روز می‌کند. APK امضاشده از repository رسمی همان Alpine دریافت می‌شود؛ اگر نسخهٔ دقیق حذف شود build باید fail شود، نه نسخهٔ شناور جایگزین. reproducibility ورودی‌ها و برابری static اثبات می‌شود؛ دو rebuild سردِ byte-identical کل image یا mirror دائمی APK/PyPI ادعا نمی‌شود. PostgreSQL/داده/env واقعی هنوز به محیط نیاز دارند؛ liveness به معنی readiness داده نیست.

frontend/Dockerfile مستقل است: Node22 با digest ثبت‌شده → npm ci از lockfile موجود → npm run build → فقط dist در `/srv/shahab` داخل NGINX unprivileged با digest ثابت و UID101/port8080. Node، node_modules و source/backend/raw وارد final-stage فرانت نمی‌شوند؛ هیچ build arg برای secret یا URL داخلی وجود ندارد. API همان `/api/v1` پیش‌فرض کلاینت است. dependency و source/CSS/asset عوض نشده‌اند.

هر دو context ریشه‌اند اما ignore اختصاصی دارند: Dockerfile.dockerignore فقط pyproject/README/دو lock مربوط به image/backend app/Alembic/contracts را می‌فرستد؛ frontend/Dockerfile.dockerignore فقط ورودی‌های واقعی Vite، src/assets/public/contracts و config NGINX. `.env*`، .git، node_modules، dist قبلی، اسناد منابع خام و تست‌ها از contextها بیرون‌اند. root .dockerignore حفظ شده؛ ignore اختصاصی طبق قرارداد Docker بر آن مقدم است. فایل مرجع canonical در Git حذف/تغییر نمی‌کند.

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

workflow کوچک `image-smoke.yml` این harness را در runner اجرا می‌کند؛ فقط read permission و build/test، بدون login/push/tag/release و بدون secrets. این job هفتم **علاوه بر شش چک موجود** است؛ workflowهای قبلی تغییر نمی‌کنند. این بند شرح شاهد A.1 است؛ قرارداد جاری A.2 در ادامه آمده است. artifact `image-smoke.json` فقط SHA سورس، local image ID، شمارش فایل و نتیجه دارد؛ local ID، registry manifest digest یا شاهد انتشار نیست. نگهداری artifact هفت روز مطابق گیت‌های فعلی است.

مرجع فنی: [Docker build context/ignore](https://docs.docker.com/build/concepts/context/)، [NGINX unprivileged](https://github.com/nginx/docker-nginx-unprivileged)، [HTTPS proxy](https://nginx.org/en/docs/http/ngx_http_proxy_module.html). digestهای پایهٔ جدید در ۲۰۲۶-۱۰-۱۸ از metadata عمومی Docker Hub خوانده شدند؛ scan امنیتی نهایی هنوز ادعا نمی‌شود.

Rollback کد packaging با PR revert همین تغییر انجام می‌شود؛ Compose/source/schema/data ثابت‌اند و migration/volume اقدامی ندارد. پس از پذیرش/مرج و build/run موفق، nextTaskId=`US-12.T04A.2`؛ مرج مجوز نشر/استقرار نیست.


## گیت جاری A.2 — build once، smoke و scan همان دو image

`image-smoke.yml` روی PR و push main، با contents:read و checkout بدون credential اجرا می‌شود. PRها و main هر دو فقط build/load/test/scan دارند و `push:false` است؛ login، packages:write، secret، environment نشر یا `latest` وجود ندارد. Buildx0.38.0/BuildKit0.34.0 و actionهای Docker با SHA/digest ثابت‌اند؛ platform فعلی فقط linux/amd64 است. cancel تنها اجراهای قدیمی PR همان ref را لغو می‌کند؛ push main لغو نمی‌شود.

Cache: دو scope ثابت api/web، export فقط push main و mode=min با timeout60s؛ PR فقط cache می‌خواند. cache محلی builder با GC، maxUsedSpace1GB و parallelism2 محدود است؛ سهمیه و eviction cache خارجی تابع GitHub است، سقف ۱GB به cache خارجی نسبت داده نمی‌شود. cache شامل secret نیست؛ دیتابیس Trivy در runner.temp تازه دریافت و زمان DB حداکثر۲۴ساعت بررسی می‌شود؛ cache image جای scan تازه نیست.

برای تغییر ABI به musl، import واقعی psycopg/SQLAlchemy/uvloop/httptools و اتصال psycopg و SQLAlchemy از **خود image نهایی** به PostgreSQL16 موقت CI الزاماً موفق شوند؛ هیچ DB/volume مالک استفاده نمی‌شود. build tools به علت چهار HIGH vendored شناسایی‌شده در scan واقعی در stage جدا باقی می‌مانند و به venv runtime منتقل نمی‌شوند؛ ignore یا حذف SBOM برای پنهان‌کردن finding انجام نمی‌شود. هر image یک بار load می‌شود؛ harness همان output را بدون rebuild می‌آزماید و برای scanner باقی می‌گذارد. scanner با **local config image ID**، نه tag قابل جابه‌جایی، اجرا می‌شود؛ label revision، metadata config digest، smoke SHA و scan ID باید برابر باشند. Trivy0.76.0 binary با SHA256 ثابت بررسی می‌شود؛ اسکن os+library، بدون ignorefile یا ignore-unfixed، همهٔ HIGH/CRITICAL حتی بدون fix را مسدود می‌کند. OS ناشناخته/EOL، DB قدیمی و خطای ابزار موفقیت نیستند. اسکن هر دو image قبل از اعمال نتیجهٔ مجموع انجام می‌شود. گیت SAST/SCA/secret موجود نیز حفظ شده و dependencyهای توسعه را مستقل می‌سنجد.

metadata کامل مستقیم از فایل خروجی --metadata-file همان action/toolkit با SHA ثابت خوانده می‌شود؛ عبور از env محدودیت اندازه دارد. نام image و SHA و یکتایی تطبیق داده می‌شوند؛ ارتقای action نیازمند آزمون دوبارهٔ این مسیر خروجی است. Artifact هفت‌روزه شامل metadata Buildx با `BUILDX_METADATA_PROVENANCE=max`، smoke، گزارش هر دو scan، CycloneDX SBOMهای تبدیل‌شده از همان گزارش و summary با SHA/image ID/digest/count/time/نسخه DB است. به علت Docker load، attestations متصل به manifest رجیستری ادعا نمی‌شود: provenance اینجا **build record metadata** است، نه امضای cryptographic یا registry attestation؛ اتصال attestations هنگام publish در A.3 لازم است. token، build credential، کلید OTP یا فایل env وارد build/artifact نمی‌شود. artifact حتی روی شکست حفظ می‌شود؛ artifact به معنی pass نیست. HIGH/CRITICAL صفر تضمین نبود آسیب‌پذیری نیست؛ یافته‌های دیگر و gateهای محیط همچنان نیازمند بررسی انتشارند.

## بررسی نسخهٔ مصوب بدون نشر — ورودی A.3

`image-release-eligibility.yml` فقط workflow_dispatch صریح از main را می‌پذیرد؛ ورودی‌ها tag موجود `vX.Y.Z` و SHA کامل تأییدشده‌اند. tag خودکار ساخته نمی‌شود. tag ساده/annotated باید دقیقاً همان SHA را resolve کند، commit در تاریخچهٔ main باشد و **آخرین** main-push اجرا در چهار workflow و هر هفت job همان SHA success باشد. اجراهای PR، skipped/pending/failed، SHA متفاوت یا سبز قدیمی پذیرفته نمی‌شوند.

علاوه بر وضعیت job، artifact A.2 همان اجرا دانلود و source/image IDهای build/smoke/scan، صفر HIGH/CRITICAL، provenance و وجود SBOM بررسی می‌شود؛ چک سبز قدیمی A.1 بدون scan نمی‌تواند واجد شرایط شود. حذف/expiry artifact مانع است. eligibility فقط read contents/actions دارد و `eligibleForA3:true,published:false` تولید می‌کند؛ هیچ dispatch واقعی، tag یا approval نشر در A.2 ساخته/اجرا نمی‌شود. آزمون‌های منفی local/CI policy را می‌سنجند؛ اجرای عملی dispatch پس از merge و وجود tag مصوب در A.3 جداست. A.3 باید tag/SHA/gate/scan و مجوز محافظت‌شده را در لحظهٔ publish دوباره تأیید کند؛ artifact فعلی مجوز deploy یا production نیست.

منابع ابزار: [Buildx metadata/provenance](https://docs.docker.com/reference/cli/docker/buildx/build/)، [cache GHA](https://docs.docker.com/build/cache/backends/gha/)، [محدودیت attestations با load](https://docs.docker.com/build/ci/github-actions/attestations/)، [Trivy filtering](https://trivy.dev/docs/latest/guide/configuration/filtering/)، [SBOM](https://trivy.dev/docs/latest/guide/supply-chain/sbom/). شواهد و محدودیت اجرا در [checkpoint A.2](../progress/us-12-t04a2.md) و PR ثبت می‌شوند. Rollback با revert همین packaging/workflow؛ هیچ migration یا reset volume ندارد. قدم بعد پس از پذیرش/مرج: A.3.
