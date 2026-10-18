# Shahab

شهاب رابط React/Vite و API مبتنی بر FastAPI برای پرسشنامه، توصیهٔ وام، پروفایل، سوابق و نشان‌شده‌های حساب دارد. توصیه‌گر از کاتالوگ منتشرشده و پیکربندی تأییدشدهٔ سرور استفاده می‌کند؛ رابط به‌تنهایی backend یا دادهٔ منتشرشده ایجاد نمی‌کند.

## اجرای محلی

پیش‌نیازها: Git، Docker Engine/Desktop با Compose v2؛ برای اجرای ابزارهای میزبان Node.js 22.12+ و Python 3.12+.

از ریشهٔ مخزن، `.env.example` را به `.env` نادیده‌گرفته‌شده کپی و مقادیر نمونهٔ محلی را جایگزین کنید؛ سپس:

```sh
docker compose up --build
```

فرانت: `http://localhost:5173/`؛ API: `http://127.0.0.1:8000`؛ liveness: `/api/v1/health/live`؛ Swagger غیرproduction: `/docs`. PostgreSQL و Redis پورت میزبان ندارند. ورود محلی با OTP آزمایشی `123456` پیامک نمی‌فرستد و مالکیت واقعی تلفن را اثبات نمی‌کند؛ staging/production آن را رد می‌کنند.

[راهنمای توسعه](docs/local-development.md) تنظیم محیط، انتشار صریح کاتالوگ آزمایشی و بررسی proxy/API را توضیح می‌دهد. [راهنمای Docker](docs/operations/docker-runbook.md) برای خطای راه‌اندازی و توقف امن است؛ `docker compose down` volume داده را نگه می‌دارد. حذف volume راه رفع خطای عادی نیست.

برای فرانت میزبان پس از راه‌اندازی API:

```sh
npm ci
npm run dev
```

## آزمون و ساخت

```sh
npm run quality
npm run build
```

وابستگی‌ها و محیط موردنیاز هر suite در [گیت‌های کیفیت](docs/testing/quality-gates.md) ثبت‌اند؛ اجرای فرانت بدون API/PostgreSQL اثبات مسیر کامل نیست. راهنمای [Swagger/Postman](docs/api/manual-testing.md) و [ماتریس ۱۹ عملیات](docs/api/coverage.md) قرارداد فعلی را پوشش می‌دهند؛ آزمون آنلاین T081 هنوز شاهد میزبان HTTPS می‌خواهد.

`dist` خروجی ایستای فرانت است. `netlify.toml` فعلی فقط build و SPA fallback دارد و API را مستقر یا proxy نمی‌کند؛ build فرانت به‌تنهایی سایت متصل به backend ایجاد نمی‌کند. [runbook استقرار](docs/runbook/production-deployment.md) وابستگی‌های محیط و مجوز انتشار را مشخص می‌کند. ارسال پیامک واقعی، درخواست بانکی و سرویس تحلیل خارجی در main مبنای ممیزی فعال نیستند.

## مراجع

- [سند جامع و ترتیب کار](docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md) و [پروتکل اجرای تسک](docs/TASK_EXECUTION_PROTOCOL.md)
- [نقشهٔ ماژول‌ها](docs/architecture/module-map.md)، [فهرست ADRها](docs/adr/README.md) و [مدل اجرایی دیتابیس](docs/database/README.md)
- [ممیزی مستندات US-12.T01](docs/release/us-12-t01-documentation-audit.md)، شامل SHA مبنا، اصلاحات و محدودیت پذیرش نهایی

آیکن‌های منفرد پروژه در assets و بستهٔ اولیه در `design/icons.zip` نگهداری می‌شوند. بعضی عکس‌ها/فونت‌ها URL خارجی دارند؛ دسترس‌پذیری آن‌ها باید در محیط انتشار بررسی شود.
