# Runbook استقرار محیط پایدار شهاب

> **هدف:** راهنمای عملیاتیِ استقرار یک محیط پایدار برای PostgreSQL، FastAPI و اتصال Netlify است. این سند خودِ استقرار نیست و تکمیل CI یا اجرای Docker محلی را معادل استقرار واقعی نمی‌داند.
>
> **وضعیت محصول:** این runbook کار آماده‌سازیِ `US-09.T07` است. تا وقتی تمام gateهای این سند روی URL واقعی ثبت نشوند، محصول «مستقر/production» اعلام نمی‌شود. انتشار production نهایی و release gate همچنان متعلق به `US-11/US-12` است.

## 1. معماری هدف

```text
کاربر
  │ HTTPS
Netlify (فقط فرانت و تنظیم API عمومی)
  │ HTTPS / allowlist
Reverse proxy + FastAPI
  │ شبکهٔ خصوصی
PostgreSQL دائمی  ←→  Redis
```

- PostgreSQL و Redis نباید از اینترنت عمومی قابل دسترس باشند.
- مرورگر فقط API HTTPS را صدا می‌زند؛ هرگز URL دیتابیس، token readiness یا credential را دریافت نمی‌کند.
- API فقط از کاتالوگ فعال `PUBLISHED` و config تأییدشده استفاده می‌کند؛ در نبود آن‌ها باید fail-closed و `503` بدهد.
- دادهٔ وام و ضرایب در فرانت hard-code نمی‌شوند. تصمیم D-005 پابرجاست: فقط ضرایب جدول تبدیل پاسخ‌ها برای وزن معتبرند؛ اعداد ماتریس نگاشت برای وزن خوانده نمی‌شوند.

## 2. اطلاعاتی که مالک محصول باید پیش از شروع تعیین کند

این جدول را در ticket/PR خصوصی تکمیل کنید، نه در Git.

| مورد | مقدار لازم |
| --- | --- |
| محیط | staging یا production |
| مالک سرور و حساب پرداخت | نام/حساب مسئول |
| ارائه‌دهندهٔ سرور و منطقه | انتخاب‌شده |
| دامنهٔ API | مانند `api.example.com` |
| دامنهٔ Netlify | URL سایت |
| روش secret management | secret manager / فایل مجاز روی سرور |
| مالک backup و سیاست نگهداری | شخص مسئول و مدت |
| پنجرهٔ deploy و مسیر اعلام incident | زمان و کانال |

بدون این موارد، provisioning انجام نشود.

## 3. پیش‌نیازهای زیرساخت

1. سرور Linux به‌روز با Docker Engine و Docker Compose v2؛ دسترسی SSH فقط با کلید و کاربر غیر-root.
2. DNS دامنهٔ API به سرور اشاره کند و TLS معتبر در reverse proxy (Nginx/Caddy یا سرویس معادل) برقرار باشد.
3. firewall فقط پورت‌های لازم HTTPS/SSH را باز کند. PostgreSQL، Redis و پورت داخلی API فقط در شبکهٔ خصوصی باشند.
4. volume یا سرویس PostgreSQL دائمی، رمزنگاری/backup و فضای کافی فراهم باشد.
5. image/version مشخصِ release ساخته و با SHA commit ثبت‌شده deploy شود؛ از branch متغیر یا image بدون tag استفاده نشود.
6. فایل secret روی سرور با permission محدود ساخته شود و هرگز در Git، Netlify client variables، log یا screenshot قرار نگیرد.

### متغیرهای secret سمت سرور

نام‌ها مجازند؛ مقدارها محرمانه‌اند:

```text
SHAHAB_ENVIRONMENT=staging|production
SHAHAB_DATABASE_URL=postgresql+psycopg://...
SHAHAB_REDIS_URL=redis://...
SHAHAB_READINESS_TOKEN=...
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
```

پیش از deploy با secret scanner بررسی کنید که هیچ مقدار واقعی در repository وجود ندارد. از `.env.example` فقط برای ساختار استفاده کنید، نه به‌عنوان تنظیم production.

## 4. ترتیب استقرار

### گام 0 — checkpoint و backup

1. SHA دقیق release، زمان، اپراتور و محیط را ثبت کنید.
2. از PostgreSQL موجود backup سازگار بگیرید و restore آن را در محیط جداگانه تست کنید.
3. اگر محیط تازه است، صراحتاً «دیتابیس خالی» ثبت کنید؛ migration به‌تنهایی کاتالوگ وام یا snapshot توصیه‌گر ایجاد نمی‌کند.
4. سلامت host، فضای volume و وضعیت TLS را تأیید کنید.

**توقف اجباری:** اگر backup/restore قابل‌اثبات نیست، به migration یا import نروید.

### گام 1 — deploy API و سرویس‌ها

1. image release را روی سرور دریافت و فقط با secretهای سمت سرور اجرا کنید.
2. PostgreSQL و Redis را در شبکهٔ خصوصی بالا بیاورید و منتظر readiness database بمانید.
3. migrationهای Alembic را یک‌بار، با همان database URL محیط هدف اجرا کنید.
4. FastAPI را فقط پس از migration اجرا کنید و public liveness را بررسی کنید:

```sh
curl --fail --silent --show-error https://API_DOMAIN/api/v1/health/live
```

پاسخ مورد انتظار: `{"status":"ok"}`. این endpoint فقط زنده بودن process را اثبات می‌کند، نه کامل بودن دادهٔ وام.

### گام 2 — audit و انتشار دادهٔ تأییدشده

این مرحله روی **همان PostgreSQL دائمی** اجرا می‌شود، نه روی دیتابیس محلی یا CI.

1. ابتدا audit فقط‌خواندنی را از release artifact اجرا کنید:

```sh
python -m scripts.materialize_t05a
```

2. خروجی را بررسی کنید. محیط تازه باید پیش از انتشار صفر/خالی باشد؛ محیط موجود نباید اختلاف source row، conditions یا category داشته باشد.
3. فقط با approval ثبت‌شده، دادهٔ رسمی را publish کنید:

```sh
python -m scripts.materialize_t05a \
  --publish \
  --actor-reference "APPROVED_OPERATOR_REFERENCE" \
  --approval-reason "Approved production catalogue publication"
```

4. همان audit را دوباره اجرا کنید و این موارد را ثبت کنید:

   - `publishedLoanVersions: 102`
   - `activeDataVersion` غیرخالی
   - `approvedConfigurations` غیرصفر
   - `missingSourceRows: []`
   - assignmentها و conditions غیرصفر
   - شمارش rankable/needsReview مطابق audit همان run

5. اگر کاتالوگ T05A از قبل با schema قدیمی وجود دارد، فقط طبق [راهنمای T05B](../operations/t05b-serving-readiness.md) و با backfill تأییدشده عمل کنید؛ حذف یا ویرایش مستقیم جدول‌ها ممنوع است.

**نکته:** این command digest منابع رسمی را بررسی می‌کند و فقط نسخهٔ D-005 تأییدشده را publish می‌کند. اگر fail شد، داده را دستی تغییر ندهید؛ خروجی و source mismatch را ثبت و بررسی کنید.

### گام 3 — آزمون API واقعی

پس از publication، API را یک‌بار restart کنید تا state آغازین سرویس از دادهٔ منتشرشده خوانده شود. سپس این سناریوها را روی دامنهٔ HTTPS API اجرا و نتیجه را ثبت کنید:

1. `GET /api/v1/health/live` → 200
2. ساخت session پرسشنامه، ثبت هر ده پاسخ canonical و `POST /api/v1/recommendations` → 200
3. نتیجه فقط از snapshot فعال خوانده شود؛ ranked، low compatibility و needs review طبق پاسخ دیده شوند.
4. `GET /api/v1/loans/{loanId}` برای یک loanId واقعی → 200 و conditions همان وام
5. loanId ناموجود → 404؛ snapshot ناقص/غایب → 503 fail-closed
6. هیچ پاسخ یا URL حاوی پاسخ خام پرسشنامه، credential، trace داخلی یا token نباشد.

شناسه‌های session، payload واقعی کاربر و secret را در log یا PR قرار ندهید.

### گام 4 — اتصال Netlify

1. در تنظیمات امن Netlify فقط URL عمومی HTTPS API را به‌عنوان متغیر build/runtime مجاز فرانت قرار دهید. credential، database URL، Redis URL و readiness token هرگز در Netlify یا Vite client قرار نمی‌گیرند.
2. rewrite/proxy API را پیش از SPA fallback قرار دهید تا مسیرهای `/api/v1/*` به فایل `index.html` نروند.
3. CORS را فقط برای originهای Netlify تأییدشده allowlist کنید؛ wildcard در production نگذارید.
4. یک deploy preview بسازید و سپس URL نهایی Netlify را به release API متصل کنید.
5. در مرورگر واقعی و mobile/desktop مسیر کامل را آزمایش کنید:

   ```text
   پرسشنامه → API → توصیه‌گر → نتایج → جزئیات وام
   ```

6. درخواست‌های Network را بررسی کنید: API باید HTTPS، بدون mixed content و بدون secret باشد.

### گام 5 — آزمون پایداری و restart

1. API، Redis و reverse proxy را طبق روش عملیاتی سرور restart کنید؛ PostgreSQL را فقط در پنجرهٔ تأییدشده restart کنید.
2. بعد از restart دوباره health، یک detail واقعی و مسیر کامل پرسشنامه را آزمون کنید.
3. audit publication را مجدداً فقط‌خواندنی اجرا کنید تا active data version و ۱۰۲ رکورد پابرجا بودن را نشان دهد.
4. زمان، URLهای آزموده‌شده، SHA release و نتیجه را در PR/T07 ثبت کنید.

## 5. rollback و بازیابی

| وضعیت | اقدام مجاز |
| --- | --- |
| خطای deploy API/Netlify، بدون migration یا publish | deploy قبلیِ SHA مشخص را برگردانید و health/smoke را تکرار کنید. |
| migration اجرا شده ولی publication شروع نشده | از backup و طرح migration مصوب استفاده کنید؛ migration downgrade را راه rollback داده فرض نکنید. |
| publication شکست خورده | command transactional است؛ audit فقط‌خواندنی بگیرید. جدول‌ها را دستی repair نکنید. |
| دادهٔ منتشرشدهٔ نادرست | انتشار/بازگردانی فقط با نسخهٔ پیشینِ تأییدشده و approval صریح؛ در نبود آن، از backup بازیابی کنید. |
| 503 توصیه‌گر | وجود database session، active `PUBLISHED` catalogue، config تأییدشده و همهٔ ۸ assignment را با audit بررسی کنید؛ fallback ساختگی ممنوع است. |
| رخداد credential | credential را rotate کنید، دسترسی را محدود کنید و بررسی incident را آغاز کنید؛ secret را در issue/PR منتشر نکنید. |

## 6. معیار تحویل T07

T07 فقط وقتی Done است که همهٔ این‌ها شواهد قابل‌بازبینی داشته باشند:

- PostgreSQL دائمی و backup/restore تأییدشده
- migration و publication تأییدشده روی همان database
- FastAPI روی HTTPS و health قابل‌دسترسی
- Netlify متصل به همان API بدون secret در فرانت
- آزمون URL واقعی: پرسشنامه تا نتایج و جزئیات، desktop و mobile
- آزمون مجدد پس از restart
- SHA release، data/config version، زمان، مالک و rollback ثبت‌شده

سبز بودن CI به‌تنهایی هیچ‌کدام از این‌ها را ثابت نمی‌کند.

## 7. شواهدی که باید در PR T07 ثبت شوند

- URL API و URL Netlify (بدون token یا query حساس)
- SHA release و tag/image digest
- نتیجهٔ migration، audit پیش/پس از publication و شمارش‌ها
- زمان و نتیجهٔ health، recommendation و loan detail
- نتیجهٔ آزمون desktop/mobile و پس از restart
- محل backup، زمان آخرین restore test و مالک آن
- محدودیت‌ها، تصمیم‌های باز و روش rollback

## پیوندهای مرتبط

- [راهنمای materialization T05A](../operations/t05a-materialization.md)
- [راهنمای readiness T05B](../operations/t05b-serving-readiness.md)
- [راهنمای Docker محلی](../operations/docker-runbook.md)
- [سند جامع توسعه](../SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md)
