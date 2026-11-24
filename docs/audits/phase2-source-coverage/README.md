# ماتریس پوشش منابع فاز دوم شهاب

این پوشه، خط مبنای منبع، candidateها و ردیابی مقدماتی برنامه را برای Blueprint و Wallet در شاخهٔ PR #251 نگه می‌دارد. فایل‌ها برای پردازش ماشینی CSV/JSON هستند؛ متن مرجع همچنان مرجع نهایی است.

## وضعیت فعلی

شمارنده‌ها و وضعیت جاری از اجرای `build_and_validate.py` در `validation-report.json` و `semantic-validation-report.md` خوانده می‌شوند؛ اعداد این فایل راهنما منبع حقیقت نیستند.

- عنوان‌ها، جدول‌ها، محدوده‌های متنی، سطرهای داده و بلوک‌های fenced از متن مرجع بازاستخراج می‌شوند؛ شمارندهٔ جاری و کنترل اختلاف با baseline در گزارش تولیدشده است.
- Git blob SHA و SHA-256 هر دو منبع در `extraction-manifest.json` هستند؛ گراف پین‌شده Graphify با SHA-256 محتوای این دو منبع هم‌خوان است.
- تمام ۳۶ بسته در `package-execution-index.csv` ثبت شده‌اند.
- `package-semantic-evidence.csv` شواهد قبلی برنامه را برای مسیریابی نگه می‌دارد؛ واردشدن آن به دفتر به معنی بازبینی مستقل تازه نیست. خلاصهٔ بسته‌ای در `package-semantic-audit.csv` این محدودیت را ثبت می‌کند.
- دفتر `semantic-review-dispositions.csv` نگه‌دارندهٔ تعیین‌تکلیف معنایی Candidateهاست. Ledger ساختاری فقط عنوان/ظرف جدول را به‌عنوان locator ثبت می‌کند و محتوای متن یا سطرهای داده را تأیید نمی‌کند.
- طبقه‌بندی‌های ماشینی صرفاً سرنخ‌اند. قضاوت Candidateها در `semantic-review-dispositions.csv` و الزام‌های اتمی در `atomic-obligation-dispositions.csv` ثبت می‌شوند؛ یک Candidate مرکب می‌تواند چند الزام مستقل داشته باشد.
- `semantic-batch-progress.csv` فقط عضویت و ترتیب Candidateهای هر دسته را نگه می‌دارد. نتیجه، شمارنده‌ها و پوشش از اتصال آن به Ledger معنایی و دفتر Atomic Obligation بازتولید می‌شوند.
- تا زمان بازبینی هر Candidate، `normative_status` آن `NEEDS_REVIEW` می‌ماند؛ پیشنهاد قاعده‌محور در `classification_suggestion` جداست.

وضعیت‌های `MATRIX_BUILD_STATUS` و `PROGRAM_COVERAGE_STATUS` مستقل و پویا هستند؛ مقدار آخرین اجرا در ابتدای `semantic-validation-report.md` آمده است.

## فایل‌ها

| فایل | محتوا |
|---|---|
| `source-inventory.csv` | عنوان‌ها، جدول‌ها، محدوده‌های متنی و fenced blocks؛ همراه hierarchy، خطوط، هش، graph references و وضعیت بازبینی |
| `atomic-obligations.csv` | موجودی Candidateهای استخراج‌شده از متن، ردیف‌های جدول و code blockها؛ این فایل به‌تنهایی دفتر الزام‌های اتمی نیست |
| `atomic-obligation-dispositions.csv` | یک یا چند الزام اتمی برای هر Candidate مرکب، با ردیابی منبع، Requirement، Task، AC/Test، شواهد برنامه و وضعیت تصمیم |
| `semantic-batch-progress.csv` | فهرست و ترتیب Candidateهای انتخاب‌شده برای هر دسته؛ شمارنده‌ها از این فهرست و Ledgerهای مرجع بازتولید می‌شوند |
| `execution-trace.csv` | نمای Candidateمحور از مسیرهای احتمالی Source→Package/Requirement/Task/AC/Test؛ تأییدهای معنایی از Ledgerهای جدا می‌آیند |
| `package-execution-index.csv` | ۳۶ بسته و شناسه‌ها/ارجاع‌های استخراج‌شده از سند برنامه؛ شناسه‌های ذکرشده ممکن است مصرف‌کننده باشند، نه مالک |
| `package-semantic-evidence.csv` | locatorهای منبع، candidate، requirement، task و AC/Test ثبت‌شده در بسته‌ها؛ برای مسیریابی شواهد، نه تأیید معنایی جدید |
| `package-semantic-audit.csv` | شمارش شواهد واردشده برای ۳۶ بسته و وضعیت مستقل‌بودن بازبینی؛ فعلاً `NOT_CLAIMED` |
| `semantic-review-dispositions.csv` | قضاوت معنایی هر Candidate با locator منبع، علت و بازبین؛ ورودی بازتولید وضعیت Candidate |
| `source-unit-review-dispositions.csv` | تعیین‌تکلیف مستقل ۳۲۶ عنوان و ۵۸ ظرف جدول به‌عنوان locator ساختاری |
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

## ادامهٔ ممیزی

Candidate بعدی از `semantic-validation-report.md` و `semantic-batch-progress.csv` تعیین می‌شود. هر دسته باید از متن مرجع تا Requirement/Task/AC/Test مقصد بازبینی شود؛ دسته فقط پس از اصلاح نقص‌های قابل‌رفع، بازتولید ماتریس و قبولی کنترل‌ها `COMPLETE` است. دفتر دسته‌ای فقط انتخاب‌ها را نگه می‌دارد و Ledgerهای معنایی/اتمی مرجع وضعیت و نتیجه‌اند. کارهای برنامه‌ای مجاز این مأموریت شامل اصلاح نقص‌های قابل‌رفع‌اند؛ Blueprint و Wallet مرجع تغییرناپذیر باقی می‌مانند.
