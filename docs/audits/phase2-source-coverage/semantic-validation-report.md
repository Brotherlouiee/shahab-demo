# گزارش اعتبارسنجی پوشش منابع فاز دوم

**MATRIX_BUILD_STATUS:** `INCOMPLETE`

**PROGRAM_COVERAGE_STATUS:** `INDETERMINATE`
**گیت‌ها:** هیچ گیت RA/IPA/CPA یا QG در این گزارش PASS اعلام نمی‌شود.

## شمارش واقعی

| شاخص | نتیجه |
|---|---:|
| Heading | 326 |
| Table block | 58 |
| واحد ساختاری | 384 |
| عنوان/ظرف جدول تعیین‌تکلیف‌شده به‌عنوان locator | 384 از 384؛ محتوای بخش و سطرهای جدول جداگانه بررسی می‌شوند |
| محدودهٔ متنی غیرجدولی استخراج‌شده | 1136 |
| سطرهای سرآیند/دادهٔ جدول استخراج‌شده | 470 |
| بلوک fenced ثبت‌شده | 27 |
| کل candidate row | 1633 |
| بسته‌های index شده | 36 / 36 |
| تعیین‌تکلیف ردیفی انجام‌شده | 306 از 1633 candidate؛ 58 سرستون، 11 جداکننده، 30 ردیف مثال و 116 نگاشت معنایی بررسی‌شده |
| تعیین‌تکلیف Candidateهای متنی | 11 از 1136 محدودهٔ متن، 128 از 470 ردیف جدول، 0 از 27 بلوک fenced |
| Candidateهای pending review | 1327؛ pending بودن به‌تنهایی شکاف قطعی نیست |
| رکوردهای Gap Register | 1347؛ 1327 بازبینی محتوایی + 20 تصمیم باز |
| Atomic Obligationهای دارای نگاشت Covered | 261 |
| نگاشت تأییدشدهٔ covered/partial/uncovered | 261/21/0 |
| شکاف معنایی قطعی | هنوز تعیین نشده |
| پیشنهادهای قاعده‌محورِ تأییدنشده | {"DESCRIPTIVE": 125, "EXAMPLE": 111, "MIXED": 104, "NEEDS_REVIEW": 762, "NORMATIVE_APPROVED": 506, "NORMATIVE_OPEN_DECISION": 19, "OUT_OF_SCOPE": 1, "SUPERSEDED": 5} |

## پیشرفت دسته‌ای

| Batch ID | Candidate IDs | Reviewed Before→After | Pending Before→After | Atomic Obligations | Covered/Partial/Uncovered | Open Decisions |
|---|---|---:|---:|---:|---:|---:|
| PILOT-001 | BP-TR-007-03, WL-C-1098, BP-C-0100 | 96→97 | 1537→1536 | 9 | 5/4/0 | 4 |
| WALLET-REFUND-001 | WL-C-0854, WL-C-0855, WL-C-0856, WL-C-0857, WL-C-0858, WL-C-0859, WL-C-0860, WL-C-0861, WL-C-0862, WL-C-0863, WL-C-0864, WL-C-0865, WL-C-0866, WL-C-0867, WL-C-0868, WL-C-0869, WL-TR-053-02, WL-TR-053-03, WL-TR-053-04 | 97→116 | 1536→1517 | 24 | 17/7/0 | 6 |
| WALLET-AUTOTOPUP-001 | WL-C-0870, WL-C-0871, WL-C-0872, WL-C-0873, WL-C-0874, WL-C-0875, WL-C-0876, WL-C-0877, WL-C-0878, WL-C-0879, WL-C-0880 | 116→127 | 1517→1506 | 14 | 9/5/0 | 4 |
| WALLET-PERIODIC-LIMITS-001 | WL-C-0881, WL-C-0882, WL-C-0883, WL-C-0884, WL-C-0885, WL-C-0886, WL-C-0887, WL-C-0888, WL-C-0889, WL-C-0890, WL-C-0891, WL-C-0892, WL-C-0893, WL-C-0894, WL-C-0895, WL-C-0896, WL-C-0897, WL-C-0898, WL-C-0899, WL-C-0900 | 127→147 | 1506→1486 | 22 | 17/5/0 | 1 |
| WALLET-LEDGER-FOUNDATION-001 | WL-C-0902, WL-C-0903, WL-C-0904, WL-C-0905, WL-C-0906, WL-C-0907, WL-C-0908, WL-C-0909, WL-C-0910, WL-C-0911, WL-C-0912, WL-C-0913, WL-C-0914, WL-C-0915, WL-C-0916, WL-C-0917, WL-C-0918, WL-C-0919, WL-C-0920 | 147→166 | 1486→1467 | 21 | 17/4/0 | 3 |
| WALLET-LIFECYCLE-IDEMPOTENCY-001 | WL-C-0921, WL-C-0922, WL-C-0923, WL-C-0924, WL-C-0925, WL-C-0926, WL-C-0927, WL-C-0928, WL-C-0929, WL-C-0930, WL-C-0931, WL-C-0932, WL-C-0933, WL-C-0934, WL-C-0935, WL-C-0936, WL-C-0937, WL-C-0938, WL-C-0939, WL-C-0940 | 166→186 | 1467→1447 | 22 | 19/3/0 | 2 |
| WALLET-COMMIT-INVARIANTS-001 | WL-C-0941, WL-C-0942, WL-C-0943, WL-C-0944, WL-C-0945, WL-C-0946, WL-C-0947, WL-C-0948, WL-C-0949, WL-C-0950, WL-C-0951, WL-C-0952 | 186→198 | 1447→1435 | 16 | 14/2/0 | 2 |
| WALLET-RECONCILIATION-RETENTION-001 | WL-C-0953, WL-C-0954, WL-C-0955, WL-C-0956, WL-C-0957, WL-C-0958, WL-C-0959, WL-C-0960, WL-C-0961, WL-C-0962, WL-C-0963, WL-C-0964, WL-C-0965, WL-C-0966, WL-C-0967, WL-C-0968, WL-C-0969, WL-C-0970, WL-C-0971, WL-C-0972, WL-C-0973, WL-C-0974 | 198→220 | 1435→1413 | 22 | 14/8/0 | 4 |
| BLUEPRINT-ROUTER-EXAMPLES-001 | BP-TR-004-05, BP-TR-004-06 | 220→222 | 1413→1411 | 0 | 0/0/0 | 0 |
| BLUEPRINT-RAG-CONTRACTS-001 | BP-C-0077, BP-C-0078, BP-C-0079, BP-C-0080, BP-C-0081, BP-C-0082, BP-C-0083, BP-C-0084, BP-C-0085, BP-C-0086, BP-C-0087, BP-C-0088, BP-C-0089, BP-C-0090, BP-C-0091, BP-C-0092, BP-TR-005-02, BP-TR-005-03, BP-TR-005-04, BP-TR-005-05, BP-TR-005-06, BP-TR-005-07, BP-TR-005-08, BP-TR-005-09, BP-TR-005-10, BP-TR-005-11, BP-C-0093, BP-TR-006-02, BP-TR-006-03, BP-TR-006-04, BP-TR-006-05, BP-TR-006-06, BP-C-0094, BP-C-0095, BP-C-0096, BP-C-0097, BP-C-0098 | 222→259 | 1411→1374 | 63 | 59/4/0 | 2 |
| BLUEPRINT-RAG-DISCOVERY-F05-001 | BP-TR-008-02, BP-TR-008-03, BP-TR-008-04, BP-TR-009-02, BP-TR-009-03, BP-TR-009-04, BP-TR-009-05, BP-TR-010-02, BP-TR-010-03, BP-TR-010-04, BP-TR-010-05, BP-TR-010-06, BP-TR-010-07, BP-TR-010-08, BP-TR-011-02, BP-TR-011-03, BP-TR-011-04, BP-TR-011-05, BP-TR-011-06, BP-TR-011-07, BP-TR-011-08, BP-TR-011-09, BP-TR-011-10, BP-TR-011-11, BP-C-0103, BP-C-0104, BP-C-0105, BP-C-0106, BP-C-0107, BP-C-0108, BP-C-0109, BP-C-0110, BP-C-0111, BP-C-0112, BP-C-0113, BP-C-0114, BP-C-0115, BP-C-0116, BP-C-0117, BP-C-0118, BP-C-0119, BP-C-0120, BP-C-0121, BP-C-0122, BP-C-0123, BP-C-0124, BP-C-0125 | 259→306 | 1374→1327 | 86 | 86/0/0 | 0 |

## کنترل‌های ماشینی

| کنترل | نتیجه | توضیح |
|---|---|---|
| تعداد Heading/Table | PASS | 326 Heading و 58 Table |
| هش Git blob دو منبع | PASS | برابر manifest جاری |
| SHA-256 دو منبع | PASS | با اثر انگشت graph پین‌شده تطبیق داده شد |
| محدوده‌های متنی و سطرهای جدول | PARTIAL | 306 از 1633 Candidate بررسی شده؛ 1327 باقی است |
| Package Execution Index | PASS | ردیف‌های برنامه‌ای استخراج شدند؛ پیوند معنایی مستقل هنوز بررسی نشده |
| تکراری نبودن IDهای منبع/candidate | PASS/PASS | IDs بررسی‌شده: 1547 source units، 1633 candidateها |
| یکپارچگی دفتر Atomic Obligation | PASS | 303 الزام مستقل؛ چند الزام می‌توانند به یک Candidate متصل شوند |
| یکپارچگی دفتر دسته‌ها | PASS | 212 انتخاب Candidate با نتیجهٔ متصل به Ledger معنایی |
| شناسه‌های Graph | DISCOVERY_ONLY | هم‌پوشانی مکانیکی منبع؛ نه شاهد entailment |
| صحت نحوی ارجاع‌های Package/Req/Task/AC/Test | PASS | تعداد tokenهای کنترل‌شده: 9312؛ معنای نگاشت‌ها هنوز UNVERIFIED است |
| یکپارچگی ارجاع‌های Package Index | PASS | 3708 شناسهٔ استخراج‌شده با سند برنامه تطبیق شد |
| پوشش کامل trace rowها | PASS | 1633 ردیف |
| علت‌دار بودن candidateهای نیازمند بازبینی | PASS | 1633 ردیف |
| پیوندهای معنایی Source→Package→Req→Task→AC/Test | PASS | 282 obligation dispositions mapped; remaining candidates are pending |
| وضعیت نگاشت نامعتبر/شکسته | PASS | 0 ledger errors; coverage claims remain limited to cited evidence |

## نقص‌های استخراج که اصلاح شدند

- ۲۶ محدودهٔ متنیِ غیرجدولی در baseline اولیهٔ ۱۱۱۰تایی جا افتاده بود؛ استخراج مجدد ۱۱۳۶ range را یافت و ۲۶ range جدید به شناسه‌های candidate اضافه شد.
- هر ۵۸ جدول به‌صورت block ثبت شده بود اما محتوای ۴۷۰ سطر سرآیند/داده در ledger الزام‌ها نبود؛ ۴۷۰ row به‌عنوان candidate مستقل افزوده شد تا محتوایشان قابل بازبینی باشد. این‌ها الزام اتمی تأییدشده نیستند.
- بلوک fencedهای کد/نمونه نیز جداگانه شمرده و ثبت شد: 27 بلوک؛ محتوای آن‌ها خودکار الزام محسوب نشده است.
- end_line سرعنوان ریشهٔ Blueprint برابر ۲۵۵۱ ثبت شده بود، در حالی‌که آخرین خط فیزیکی فایل ۲۵۵۰ است؛ محدوده اصلاح شد.
- Graph node IDs خالی بود؛ ارجاع‌های مکانی گراف پین‌شده به‌عنوان discovery references اضافه شدند.

## محدودیت معنایی

Rule-based labels فقط سرنخ‌اند. تا این اجرا، 306 از 1633 Candidate با متن منبع و مقصد بررسی شده‌اند و 303 Atomic Obligation ثبت شده؛ 1327 Candidate هنوز نیازمند بازبینی‌اند. Candidate و obligation دو شمارش متفاوت‌اند. وضعیت Covered/Partial/Uncovered از دفتر اتمی و شواهد مشخص آن بازتولید شده است.

## منابع و گراف

- `docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md`: Git blob `9681c2bf6c3149317c3788516748084cfb6eac7c`, SHA-256 `0709c84fe9e47e1d9218c6d0f93a82c89a62d6b234565e9b0ca2d4158759f266`, خطوط واقعی `2550`.
- `docs/SHAHAB_DIGITAL_WALLET.md`: Git blob `1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a`, SHA-256 `8b8d139b64f25f8f9592f936c070ece37b3e97df55d4e6b1d0cf305933960b74`, خطوط واقعی `1780`.
- گراف: `17622bf4dd56108bee10d880a9dc5eb9617482fd:knowledge-graph/phase2-reference-docs/semantic/graph.json`؛ SHA-256 `f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93`؛ استفاده برای کشف/ارجاع، نه تأیید نگاشت.
- متن کامل RTF معیارها (در پیوست قبلی) از QG-14 قطع می‌شود؛ این مأموریت براساس پرامپت تکمیلی جاری اجرا شده است.

## مرحلهٔ بعد

ادامهٔ دسته‌ای از اولین Candidate بررسی‌نشده `BP-TR-012-02` است. هر دسته باید با بازبینی متن، زمینه، تصمیم، ردیابی واقعی Requirement/Task/AC/Test، اصلاح نقص و اعتبارسنجی کامل شود. Candidateهای باقی‌ماندهٔ pending به‌خودی‌خود شکاف قطعی محسوب نمی‌شوند.
