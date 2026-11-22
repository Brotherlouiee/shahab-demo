# ماتریس پوشش منابع فاز دوم شهاب

این پوشه، خط مبنای منبع، candidateها و ردیابی مقدماتی برنامه را برای Blueprint و Wallet در شاخهٔ PR #251 نگه می‌دارد. فایل‌ها برای پردازش ماشینی CSV/JSON هستند؛ متن مرجع همچنان مرجع نهایی است.

## وضعیت فعلی

- ۳۲۶ عنوان و ۵۸ جدول Markdown (۳۸۴ واحد ساختاری) ثبت شده‌اند.
- ۱٬۱۳۶ محدودهٔ متنی غیرجدولی، ۴۷۰ سطر سرآیند/دادهٔ جدول و ۲۷ بلوک fenced ثبت شده‌اند. از ۱٬۱۱۰ candidate اولیه، ۲۶ محدودهٔ متنی از قلم افتاده بود و با شناسه‌های افزوده بازیابی شد.
- Git blob SHA و SHA-256 هر دو منبع در `extraction-manifest.json` هستند؛ گراف پین‌شده Graphify با SHA-256 محتوای این دو منبع هم‌خوان است.
- تمام ۳۶ بسته در `package-execution-index.csv` ثبت شده‌اند.
- ۳٬۰۶۴ locator و disposition قبلی بسته‌ها از سند برنامه در `package-semantic-evidence.csv` وارد شده‌اند؛ این شواهد پیشین‌اند و بازبینی مستقل تازه محسوب نمی‌شوند. خلاصهٔ بسته‌ای در `package-semantic-audit.csv` این محدودیت را صریح ثبت می‌کند.
- طبقه‌بندی‌های ماشینی صرفاً سرنخ‌اند. هیچ Atomic Obligation یا نگاشت اجرا به‌عنوان معنایی‌تأییدشده/`VERIFIED_COVERED` ثبت نشده است.
- تا زمان بازبینی انسانی، ستون `normative_status` برای همهٔ candidateها `NEEDS_REVIEW` است؛ دسته‌بندی قاعده‌محور جداگانه با عنوان `classification_suggestion` نگه‌داری می‌شود.

**MATRIX_BUILD_STATUS: `INCOMPLETE`** — ساختارها، متن‌ها، سطرهای جدول و index بسته‌ها ثبت شده‌اند؛ بازبینی معنایی و اتمی‌سازی کامل نشده است.

**PROGRAM_COVERAGE_STATUS: `INDETERMINATE`** — هنوز نمی‌توان پوشش کامل یا تعداد شکاف‌های واقعی را نتیجه گرفت.

## فایل‌ها

| فایل | محتوا |
|---|---|
| `source-inventory.csv` | عنوان‌ها، جدول‌ها، محدوده‌های متنی و fenced blocks؛ همراه hierarchy، خطوط، هش، graph references و وضعیت بازبینی |
| `atomic-obligations.csv` | ۱٬۶۳۳ source candidate شامل پاراگراف‌ها، ردیف‌های جدول و code blocks؛ ستون Atomic Obligation ID تا بازبینی انسانی خالی می‌ماند |
| `execution-trace.csv` | نگاشت‌های واژگانیِ پیشنهادی Source→Package/Requirement/Task/AC/Test؛ همه pending/unverified هستند |
| `package-execution-index.csv` | ۳۶ بسته و شناسه‌ها/ارجاع‌های استخراج‌شده از سند برنامه؛ شناسه‌های ذکرشده ممکن است مصرف‌کننده باشند، نه مالک |
| `package-semantic-evidence.csv` | locatorهای منبع، candidate، requirement، task و AC/Test ثبت‌شده در بسته‌ها؛ برای مسیریابی شواهد، نه تأیید معنایی جدید |
| `package-semantic-audit.csv` | شمارش شواهد واردشده برای ۳۶ بسته و وضعیت مستقل‌بودن بازبینی؛ فعلاً `NOT_CLAIMED` |
| `coverage-gap-register.csv` | موارد نیازمند بازبینی؛ ردیف `PENDING_SEMANTIC_REVIEW` شکاف قطعی محسوب نمی‌شود |
| `extraction-manifest.json` | منبع، blob SHA، SHA-256، آمار استخراج، گراف و محدودیت‌ها |
| `semantic-validation-report.md` | نتیجهٔ ممیزی، خطاهای استخراج اصلاح‌شده، کنترل‌ها و محدودیت معناشناختی |
| `validation-report.json` | شمارنده‌ها و نتیجهٔ کنترل‌های تکرارپذیر |

## بازتولید و کنترل

از ریشهٔ مخزن اجرا کن:

```bash
python docs/audits/phase2-source-coverage/build_and_validate.py
python docs/audits/phase2-source-coverage/build_and_validate.py --check-only
python docs/audits/phase2-source-coverage/build_semantic_evidence.py
```

اسکریپت گراف پین‌شدهٔ Graphify را از commit ثبت‌شده در manifest می‌خواند. ارجاع گراف یا هم‌پوشانی خطوط به‌تنهایی شاهد نگاشت معنایی نیست. فقط پس از خواندن متن اصلی و Requirement/Task/AC/Test واقعی، نگاشت را verified کن.

## مرحلهٔ بعد

۱. طبقه‌بندی هنجاری هر range و محتوای هر جدول/بلوک کد را با متن کامل و وضعیت تصمیم تطبیق بده. ۲. رفتارهای مصوب را بدون ادغام یا خردکردن مصنوعی به Atomic Obligation تبدیل کن. ۳. index برنامه را با مرز مالکیت و dependency تطبیق بده. ۴. فقط نگاشت‌های دارای شاهد معنایی را تأیید کن؛ بقیه را `VERIFIED_PARTIAL`، `VERIFIED_UNCOVERED`، `OPEN_DECISION`، `NOT_APPLICABLE` یا `PENDING_REVIEW` نگه دار. ۵. هر نقص برنامه را در gap register ثبت کن؛ این مرحله مجوز اصلاح بسته‌ها را نمی‌دهد.
