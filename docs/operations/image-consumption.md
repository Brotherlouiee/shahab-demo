# مصرف و بازگشت جفت ایمیج — US-12.T04A.4

## انتشار واقعی و محدوده

نسخهٔ v0.1.0 از commit `2c1a0acc5ed487b48df5bd87b816277bd41f9b35` در
[اجرای موفق نشر](https://github.com/Brotherlouiee/shahab-demo/actions/runs/39224423986)
منتشر شد. [manifest پایدار](../release/images/v0.1.0.json) از journal واقعی artifact
شمارهٔ 12172903771 استخراج شده است: UTC آغاز/پایان، run و source SHA، دو tag،
digest هر دو manifest، ID/config و digest پیوست SBOM/provenance در آن ثبت‌اند.
هش journal اصلی نیز ثبت شده؛ هیچ PAT یا config محیط واقعی در این فایل نیست.
این trace به اجرای مورداعتماد GitHub تکیه دارد؛ امضای مستقل رمزنگاری‌شده ادعا نمی‌کند.

| بخش | مقصد و دسترسی | digest واقعی |
| --- | --- | --- |
| بک‌اند | shahab2026/shahab-backend؛ خصوصی | `sha256:7e9366e8ad69aaba5fcbba702d0cbd60a935c3816daf89841b490f53bb73fb7e` |
| فرانت‌اند | shahab2026/shahab-frontend؛ عمومی | `sha256:ad0129b5cdc9998afd838ff8ab11b9dcdc5b5ad946f13b39f75f47589110089a` |

دو tag هر image عبارت‌اند از `v0.1.0` و
`sha-2c1a0acc5ed487b48df5bd87b816277bd41f9b35`؛ هیچ latest تولید نشده است.
مصرف باید با digest باشد، نه tag متغیر یا digest محلی Buildx exporter.

## اجرای آزمون دریافت از registry

پس از merge این workflow روی main: در Actions، گزینهٔ **Consume published image pair by digest**
و Run workflow را انتخاب کنید؛ branch برابر main، version برابر v0.1.0 و
previous_version خالی باشد. سپس Review deployments و محیط dockerhub-publish را تأیید کنید.
این approval صرفاً دریافت/آزمون image است و به معنی deploy سایت نیست.
برای backend خصوصی از Secretهای موجود همان محیط در docker/login-action استفاده می‌شود؛
مقدار token هرگز در ورودی، command، JSON یا artifact قرار نمی‌گیرد. این workflow هیچ
push، tag، حذف registry، migration یا دسترسی به میزبان پروژه ندارد.
برای token مصرفِ مستقل، Read-only کافی است؛ credential موجود نشر Read/Write است و
در این مسیر فقط برای login/pull استفاده می‌شود، نه اینکه scope واقعی آن Read-only نامیده شود.

پیش از login، تنظیم reviewer/branch محیط و اجرای موفق main از workflow نشر بررسی
می‌شود. artifact دقیق به run/ID و hash journal تطبیق می‌شود؛ جفت ناقص، منبع اشتباه،
run ناموفق/PR و manifest دستکاری‌شده رد می‌شوند. artifact نشر ۳۰روز retention دارد؛
انقضا خطای صریح است، نه مجوز حذف کنترل شاهد. پیش از انقضا، مالک باید گزارش کامل را
در محل مجاز پرونده release نگه دارد؛ بازیابی شاهد منقضی مسیر بازبینی مستقل می‌خواهد.

کد آزمون در checkout tooling از main و reference در checkout source از SHA داخل
manifest قرار می‌گیرد. Node22 و lockfile همان source فقط dist مرجع مستقل را می‌سازند؛
هیچ Dockerfile یا image دوباره ساخته نمی‌شود. سپس هر دو digest از Docker Hub pull،
RepoDigests و ID/config و label revision و non-root تطبیق می‌شوند و smoke موجود همان
source اجرا می‌شود: API liveness، 401 و 503 fail-closed، غیرفعال‌بودن mock OTP در staging،
SPA refresh، MIME، تطبیق تمام static bytes با dist مستقل، proxy TLS مصنوعی معتبر و
رد CA نامعتبر. منابع صرفاً container/network تصادفی با portهای loopback هستند و harness
در finally همان منابع را حذف می‌کند؛ volume کاربر یا PostgreSQL موجود هدف آزمون نیست.
هیچ phone واقعی، SMS، اطلاعات کاربر یا snapshot عملیاتی در این smoke مصرف نمی‌شود.

خروجی artifact با نام image-consumption-evidence شامل image-consumption.json و
smoke همان source است. status مصرف و rollback جدا هستند. سبزشدن jobِ اولین نسخه تنها
«مصرف موفق و rollback فاقد نسخهٔ قبلی» را ثابت می‌کند، نه Done کل A.4 یا انتشار سایت.

## فرمان دریافت دستی در محیط ایزولهٔ مجاز

ابتدا با Docker login امن و ورود PAT در password prompt به repository خصوصی دسترسی
بگیرید؛ PAT را در command line ننویسید. سپس دریافت دقیق هر دو image:

```bash
docker pull --platform linux/amd64 docker.io/shahab2026/shahab-backend@sha256:7e9366e8ad69aaba5fcbba702d0cbd60a935c3816daf89841b490f53bb73fb7e
docker pull --platform linux/amd64 docker.io/shahab2026/shahab-frontend@sha256:ad0129b5cdc9998afd838ff8ab11b9dcdc5b5ad946f13b39f75f47589110089a
```

برای smoke از workflow بالا استفاده کنید؛ صرف pull یا روشن‌شدن کانتینر پایان آزمون نیست.
این فرمان‌ها هیچ service، دیتابیس یا volume موجود را تغییر نمی‌دهند.

## توافق سازگاری و داده/config

فرانت و API فقط به‌صورت جفت همان release پذیرفته‌اند؛ اختلاط digest دو نسخه بدون
بازبینی مجاز نیست. API `/api/v1` و schema source با Alembic head `ff11b02f0001` مرجع‌اند.
این شماره وصف کد است، نه ادعای اجرای migration روی سرور. dataSnapshot/configSnapshot
عمداً null هستند: runtime image دادهٔ serving منتشرشده یا credential ندارد و این smoke
بدون DB است. ماتریس‌ها، D-005 و داده رسمی نه تغییر کرده‌اند و نه برای تست در DB واقعی
منتشر شده‌اند. پیش از استقرار باید revision واقعی DB و active serving snapshot/config
مصوب همان محیط audit و در پرونده release ثبت شوند؛ نبود آن‌ها deploymentEligible=false
و blocker محیط باقی می‌ماند. health=200 جای آمادگی داده/ورود/مسیر کامل کاربر نیست.

## بازگشت ایمن و محدودیت اولین نسخه

این اولین انتشار است: previousRelease=null. هیچ جفت مستقل قبلی وجود ندارد؛ v0.1.0
را به خودش rollback نمی‌نامیم و tag صوری نمی‌سازیم. وضعیت دقیق
blocked-no-previous-release تا وجود جفت قبلی مستقل و سازگار باز می‌ماند.
برای راه‌اندازی نخست، برنامهٔ توقف پذیرش ترافیک در صورت شکست و حفظ محیط/شواهد لازم
است؛ «برگشت به سایت سالم قبلی» بدون نسخهٔ قبلی قابل وعده نیست.

پس از انتشار نسخهٔ بعدی، manifest آن با PR مستقل و trace واقعی ثبت می‌شود؛ فیلد
previousRelease باید نسخهٔ قبلی منتخب را صریح معرفی کند. یک جفت قدیمی با SHA و دو
digest مستقل و زمان نشر قبلی، API/schema/data/config سازگار و شاهد بازبینی لازم است.
پارامتر previous_version همان نسخهٔ ثبت‌شده را می‌گیرد؛ workflow هر دو source و dist
را جدا آماده و current → previous → current را با pull و restart/smoke جفت‌ها تمرین
می‌کند. این فقط rehearsal بدون DB و بدون ترافیک واقعی است. تفاوت schema یا data/config
در validation رد می‌شود و طرح سازگاری مستقل می‌خواهد؛ null به معنای سازگاری با DB
واقعی نیست. تست مصنوعی این منطق جای rehearsal دو نسخهٔ واقعی نیست.

در rollback محیط واقعی، writers/ترافیک طبق مجوز محیط متوقف، جفت قبلی با digest
انتخاب و config قبلی سازگار از secret store بازیابی شود؛ schema و DB حفظ شوند و پس
از smoke/مالکیت/نشست/data audit و مجوز مسئول، ترافیک باز شود. بازگشت کد، downgrade
schema و restore داده سه اقدام متفاوت‌اند. از حذف volume، reset دیتابیس یا downgrade
خودکار استفاده نشود. قواعد guard، backup، raw-expired و archived/hidden در
[طرح release/migration/rollback](../runbook/release-migration-rollback.md) برقرارند.

## صورت‌جلسه و پذیرش

تحویل کد: manifest قابل ردیابی + workflow دریافت و آزمون + قرارداد و تست منفی + این
runbook. تحویل اجرایی: run جدید، UTC، digest/ID/revision هر دو image، نتیجهٔ smoke و
rollbackStatus از artifact ثبت شود. تا اجرای پس از merge، pull واقعی در این زیرگام
ادعا نمی‌شود. تا وجود previous واقعی، پذیرش کامل rollback باز است. سند تداوم داستان
و همه gateهای سرور/OTP/US-13/production بدون تغییرند.

منابع رسمی: [Docker pull by digest](https://docs.docker.com/reference/cli/docker/image/pull/)،
[اجرای دستی workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)،
[محیط و approval](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).
