# گزارش ممیزی کیفی Phase 4

تاریخ بررسی ۲۶ نوامبر ۲۰۲۶

## نتیجه

ممیزی هنوز به پذیرش کامل نرسیده است. PR #257 باز و از نظر GitHub قابل Merge است، اما از نظر Gateهای این ممیزی آمادهٔ Merge نیست. Branch Coverage، Mutation کامل، Security CI، Performance تولیدی، سازگاری محیط و Graphify نهایی ناقص‌اند. PR را Merge نکردم.

## نسخه و وضعیت مخزن

| مورد | مقدار |
| --- | --- |
| PR | https://github.com/Brotherlouiee/shahab-demo/pull/257 |
| شاخه | fix/phase4-graphify-review |
| Base واقعی PR | 3df5beb8fbec677515ad9b4cd0ea30b7fd055dce |
| Baseline ممیزی قبلی | 392751eaeee882fc770069e3dcd3a161d47a9d26 |
| Commit اجرای کد و آزمون‌ها | ee23df1cd1d04da6fc4a3b05f64655c6c99a4c35 |
| Commit اجرای آزمون‌های منبع | ee23df1cd1d04da6fc4a3b05f64655c6c99a4c35 |
| Commit CI بررسی‌شده برای شواهد | 63e3891c502f95b3763d5edf872f9257211c5acd |
| PR | باز، mergeable، clean |
| CI | چهار Workflow موفق روی Commit انتشار شواهد، پنج Job موفق، هفت Job ردشده، بدون شکست |

Base واقعی PR و Baseline ممیزی مفاهیم جداگانه‌اند. در بررسی فایل‌های کامل مشخص شد دو فایل در ثبت قبلی ناقص بودند. Commit ee23df1 آن‌ها را با نسخهٔ کامل جایگزین کرد و Blob SHA آن‌ها پیش از ثبت با GitHub تطبیق داده شد. CI قبلی این نقص را کشف نکرده بود، چون تغییر مستندی طبقه‌بندی شده بود.

## ۱۲ مأموریت

| مأموریت | وضعیت قبلی | وضعیت فعلی | شواهد و محدودیت |
| --- | --- | --- | --- |
| 1. ممیزی خط‌به‌خط | ناقص | PARTIAL | ماتریس تابعی ساخته شد و Coverage اندازه‌گیری شد. مرور کامل خط‌به‌خط JavaScript و امضای انسانی همهٔ خطوط انجام نشده است. |
| 2. اعتبارسنجی مستقل و Property-based | ناقص | PARTIAL | ۱۰۰ جایگشت معتبر، ۱۰۰ ورودی ساختاری نامعتبر و ۲۰۰ نمونهٔ Hypothesis اجرا شد. پوشش تمام Propertyهای مصوب کامل نیست. |
| 3. Branch Coverage | اجرا نشده | PARTIAL | Coverage شاخه‌ای Python برابر ۷۲٫۰۴٪ است. Branchهای بحرانی ۱۰۰٪ نیستند و Coverage شاخهٔ JavaScript اندازه‌گیری نشد. |
| 4. Mutation Testing | ناقص | PARTIAL | ۳۰/۳۰ مورد هدف کشف شد، شامل ۱۵ جهش منبع کد و ۱۵ تغییر Artifact/Data. امتیاز کامل ۳۰ جهش code-only ادعا نمی‌شود. |
| 5. Fuzz | ناقص | PARTIAL | ۱۰۰۰ ورودی CSV، ۷۷۹ رد کنترل‌شده، ۲۲۱ ردیف با عرض کامل پذیرفته‌شده و صفر Exception غیرمنتظره. سایر دامنه‌های درخواستی Fuzz نشدند. |
| 6. Fault Injection | جزئی | PARTIAL | شکست os.replace برای Mapping و Evidence Index نسخهٔ قبلی را حفظ کرد. Disk-full، شکست fsync، توقف پردازه و نوشتن هم‌زمان اجرا نشدند. |
| 7. Security | اجرا نشده | PARTIAL | Bandit، Ruff و آزمایش XSS اجرا شدند. SAST/SCA در CI به‌دلیل طبقه‌بندی تغییرات Skip شد. |
| 8. Performance/Stress | محدود | PARTIAL | ساختار مصنوعی تا ۱۰ برابر در ۵٫۱۱۴ ثانیه بررسی شد. این آزمون Builder یا رندر Browser را در ۱۰ برابر نمی‌سنجد. |
| 9. سازگاری محیط | ناقص | PARTIAL | Linux، CPython 3.12.14، Node 24.22.3 و Chrome 142 آزموده شدند. Windows، Firefox، Edge و macOS آزموده نشدند. |
| 10. Phase 5 Consumer Smoke | ناقص | PARTIAL | مصرف‌کنندهٔ مستقل قرارداد خروجی، DAG، Snapshotها و ارجاعات را خواند. Integration واقعی Phase 5 اجرا نشد. |
| 11. Graphify Finding ششم | مسدود | BLOCKED | API پنج شرح از شش مورد را برگرداند. شرح ششم در دسترس نیست و سهمیه تا ۱ دسامبر ۲۰۲۶ UTC پر است. |
| 12. تناقض گزارش‌ها | متناقض | PASS | Base، Baseline ممیزی، HEAD و CI جدا ثبت شدند. CI روی Commit انتشار شواهد بررسی شد. Commit اصلاح مستندات بعدی باید جداگانه از نظر CI بررسی شود. |

## آزمون‌ها

- Python Regression موفق شد، ۱۹ از ۱۹.
- Source Coverage موفق شد، ۲۹ از ۲۹ کنترل و صفر خطا.
- Stage 4 Replay موفق شد، ۶۵۷ رکورد، ۳۴۷ فایل Inventory، ۶۹۶ Mapping و ۱۳۴ تصمیم OPEN/BLOCKED.
- Combined Graph موفق شد، ۴٬۴۹۰ Node و ۱۱٬۴۳۵ Edge.
- Chrome 142 در DPRهای ۱ و ۲ آزموده شد. تغییر واقعی پیکسل Canvas، Frame، Filter، Cross-only، Search، انتخاب Node/Edge، Pan، Zoom، Fit، Resize و Source Evidence همگی موفق شدند.
- XSS: Label خصمانه به شکل متن باقی ماند. اسکریپت اجرا و عنصر Image تزریق نشد.
- Hypothesis: ۱۰۰ عنوان معتبر و ۱۰۰ ورودی مرزی یا نامعتبر.
- ۱۰۰ جایگشت داده با Seed برابر 25711026 و ۱۰۰ تغییر ساختاری نامعتبر آزموده شدند.
- Mutation داده ۱۰۰ از ۱۰۰ شناسایی شد. چهار جهش رفتاری موقت Browser نیز کشته شدند. این‌ها معادل مجموعهٔ ۳۰ جهش کد نیستند.
- CSV Fuzz شامل ۱۰۰۰ ورودی بود، با ۷۷۹ رد کنترل‌شده، ۲۲۱ ردیف با عرض کامل پذیرفته‌شده و صفر Exception غیرمنتظره. سایر دامنه‌های Fuzz درخواستی اجرا نشدند.
- Python Coverage شامل ۱٬۶۶۰ Statement بود که ۱٬۲۵۱ مورد پوشش یافتند، برابر ۷۵٫۳۶٪. از ۶۵۸ Branch Arc تعداد ۴۷۴ مورد پوشش یافت، برابر ۷۲٫۰۴٪.
- Ruff تعداد ۵۴۷ هشدار سبک/Lint گزارش کرد که عمدتاً خطوط طولانی یا چنددستوری در فایل‌های موجود بود. بازنویسی گستردهٔ خارج از دامنه انجام نشد.
- Bandit بیست هشدار خام داشت. چهار هشدار High مربوط به SHA-1 برای Git Blob identity بود و ۱۶ هشدار Low به فراخوانی ثابت Git بدون shell مربوط شد. مورد تزریق قابل اقدام تأیید نشد. Exit Code ابزار به‌علت هشدارها ۱ بود.
- Stress مصنوعی ۱۰x شامل ۴۴٬۹۰۰ Node و ۱۱۴٬۳۵۰ Edge بود. زمان ۵٫۱۱۴ ثانیه و Peak tracemalloc برابر ۵۳۱٬۴۱۶٬۷۷۹ بایت بود. این رقم، حافظهٔ Browser یا Builder نیست.

## Graphify

آخرین Review قابل‌بازیابی Run 3d8b2ea8-f719-40b4-a184-18419145964b روی Commit 79574bc806b5a264dca78f5634d0833c1c7e570e است، نه HEAD نهایی. Gate آن PASS، بدون Blocker و با یک یادداشت Coupling دربارهٔ build_search() بود.

| Finding | نتیجه | شواهد |
| --- | --- | --- |
| GF-1 فرض List بودن خروجی read_csv | FALSE_POSITIVE | تابع واقعی (fields, rows) برمی‌گرداند. Builder رسمی دو بار اجرا شد. |
| GF-2 خطای ردیف کوتاه CSV | FALSE_POSITIVE_FOR_CURRENT_CONTRACT | Parser مقدار مفقود را با ValueError کنترل‌شده رد می‌کند. آزمون ردیف کوتاه و شناسهٔ خالی موفق است. |
| GF-3 انتظار صفر برای Cross-only contains | NO_DEFECT_REPRODUCED | Oracle مرورگر روابط task_mapping و decision_scope را مطابق قرارداد Cross-only در نظر می‌گیرد. |
| GF-4 احتمال TypeError برای Endpoint ناموجود | CONTRACT_GUARD_PRESENT | آزمون پیش از دسترسی به Node، وجود هر دو Endpoint را Assert می‌کند. |
| GF-5 جست‌وجو مرکز Node را کنترل نمی‌کند | ALREADY_TESTED | مرورگر مرکز Node مطابق جست‌وجو را در DPR ۱ و ۲ بررسی کرد. |
| GF-6 شرح در دسترس نیست | UNREVIEWED | API شش مورد اعلام کرد، اما پنج شرح برگرداند. شرح ششم حدس زده نشد. |

## داده و خروجی‌ها

Evidence Index، Mapping، Graph JSON و HTML دو بار بازتولید شدند و با cmp بایت‌به‌بایت برابر بودند.

| خروجی | SHA-256 |
| --- | --- |
| evidence-join-index.json | 83f6776478f9c9472bb6f70a45390ceccb45d7b178ef55fe4337618d068dc8aa |
| task-map-mapping.json | bee6643868323bb5e424dbfa59f0607f951c8d17733c41bd0b67bdf496be639c |
| task-map-graph.json | a9ca43d20d7d49db72b840043350381a3d32913a913788369a0257a89067d0b9 |
| task-map-graph.html | 625fba8cb368ce7cf429e53bf669eab3d5a98c11025f5284db27c8d037f07dd5 |

| شاخص | مقدار |
| --- | --- |
| Combined Graph | ۴٬۴۹۰ Node، ۱۱٬۴۳۵ Edge |
| Mapping | ۱۵ MAPPED، ۲۷ PARTIALLY_MAPPED، ۶۵۴ NEW_IMPLEMENTATION |
| Relation Overlay | ۹۹ |
| Candidate و Pending | ۱٬۶۳۳ و صفر |
| Atomic Obligation | ۱٬۲۸۵ |
| Covered، Partial، Open Decision، Uncovered | ۱٬۱۴۹، صفر، ۱۳۴، ۲ |
| تصمیم‌های باز | هر ۱۳۴ مورد OPEN و Mapping همه BLOCKED |

Blob SHA و SHA-256 سه گراف Immutable با مقادیر مصوب برابرند. Blueprint، Wallet، Implementation Plan، Ledgerها و گراف‌های مرجع تغییر نکردند.

## ۲۲ Gate

| Gate | وضعیت نهایی |
| --- | --- |
| 01 Audit Coverage | PARTIAL |
| 02 Confirmed Defects | PARTIAL |
| 03 Findings Disposition | PARTIAL |
| 04 Regression Tests | PASS |
| 05 Data Integrity | PASS |
| 06 Immutable Graphs | PASS |
| 07 Open Decisions | PASS |
| 08 Source Coverage | PASS |
| 09 Stage 4 Replay | PASS |
| 10 Combined Graph Validation | PASS |
| 11 Independent Validation | PARTIAL |
| 12 Critical Branch Coverage | PARTIAL |
| 13 Mutation Testing | PARTIAL |
| 14 Fault Injection | PARTIAL |
| 15 Security | PARTIAL |
| 16 Determinism | PASS |
| 17 Real Browser | PASS |
| 18 Performance | PARTIAL |
| 19 Environment Compatibility | PARTIAL |
| 20 Phase 5 Consumer Readiness | PARTIAL |
| 21 CI | PARTIAL |
| 22 Final Graphify Review | BLOCKED |

تنها مانع Graphify نیست. Coverage، Mutation، SAST/SCA، Performance و سازگاری محیط نیز ناقص‌اند. گزارش‌ها و شواهد تازه باید روی PR ثبت و CI آن Commit دوباره بررسی شود. پذیرش کامل یا آمادگی Merge اعلام نمی‌شود.


## Mutation matrix disposition

تمام ۳۰ مورد هدف در ماتریس کنترل‌شده شناسایی شدند. جهش‌های MUT-12 تا MUT-25 و MUT-30 روی کپی موقت کد Production اجرا و توسط آزمون‌های هدفمند کشته شدند. MUT-01 تا MUT-11 و MUT-26 تا MUT-29 روی Fixtureهای Artifact/Data اجرا شدند و Oracleهای مستقل تغییر را کشف کردند. بنابراین ۱۵/۱۵ جهش منبع کد در زیرمجموعهٔ اجراشده کشته شدند و ۱۵/۱۵ تغییر داده کشف شد؛ این نتیجه معادل اجرای ۳۰ جهش منبع کد نیست و GATE-13 همچنان PARTIAL است. فهرست فایل، تابع، رفتار جهش‌یافته و آزمون کشف‌کننده در `mutation-testing-report.json` ثبت شده است.
