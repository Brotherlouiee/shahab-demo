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
| تعیین‌تکلیف ردیفی انجام‌شده | 147 از 1633 candidate؛ 58 سرستون، 11 جداکننده، 21 ردیف مثال و 31 نگاشت معنایی بررسی‌شده |
| تعیین‌تکلیف Candidateهای متنی | 11 از 1136 محدودهٔ متن، 87 از 470 ردیف جدول، 0 از 27 بلوک fenced |
| ردیف‌های pending review | 1486؛ این‌ها شکاف قطعی نیستند |
| Atomic Obligationهای دارای نگاشت Covered | 52 |
| نگاشت تأییدشدهٔ covered/partial/uncovered | 52/13/0 |
| شکاف معنایی قطعی | هنوز تعیین نشده |
| پیشنهادهای قاعده‌محورِ تأییدنشده | {"DESCRIPTIVE": 125, "EXAMPLE": 111, "MIXED": 104, "NEEDS_REVIEW": 762, "NORMATIVE_APPROVED": 506, "NORMATIVE_OPEN_DECISION": 19, "OUT_OF_SCOPE": 1, "SUPERSEDED": 5} |

## پیشرفت دسته‌ای

| Batch ID | Candidate IDs | Reviewed Before→After | Pending Before→After | Atomic Obligations | Covered/Partial/Uncovered | Open Decisions |
|---|---|---:|---:|---:|---:|---:|
| PILOT-001 | BP-TR-007-03, WL-C-1098, BP-C-0100 | 96→97 | 1537→1536 | 9 | 5/4/0 | 4 |
| WALLET-REFUND-001 | WL-C-0854, WL-C-0855, WL-C-0856, WL-C-0857, WL-C-0858, WL-C-0859, WL-C-0860, WL-C-0861, WL-C-0862, WL-C-0863, WL-C-0864, WL-C-0865, WL-C-0866, WL-C-0867, WL-C-0868, WL-C-0869, WL-TR-053-02, WL-TR-053-03, WL-TR-053-04 | 97→116 | 1536→1517 | 24 | 17/7/0 | 6 |
| WALLET-AUTOTOPUP-001 | WL-C-0870, WL-C-0871, WL-C-0872, WL-C-0873, WL-C-0874, WL-C-0875, WL-C-0876, WL-C-0877, WL-C-0878, WL-C-0879, WL-C-0880 | 116→127 | 1517→1506 | 14 | 9/5/0 | 4 |
| WALLET-PERIODIC-LIMITS-001 | WL-C-0881, WL-C-0882, WL-C-0883, WL-C-0884, WL-C-0885, WL-C-0886, WL-C-0887, WL-C-0888, WL-C-0889, WL-C-0890, WL-C-0891, WL-C-0892, WL-C-0893, WL-C-0894, WL-C-0895, WL-C-0896, WL-C-0897, WL-C-0898, WL-C-0899, WL-C-0900 | 127→147 | 1506→1486 | 22 | 17/5/0 | 1 |

## کنترل‌های ماشینی

| کنترل | نتیجه | توضیح |
|---|---|---|
| تعداد Heading/Table | PASS | 326 Heading و 58 Table |
| هش Git blob دو منبع | PASS | برابر manifest جاری |
| SHA-256 دو منبع | PASS | با اثر انگشت graph پین‌شده تطبیق داده شد |
| محدوده‌های متنی و سلول‌های جدول | PARTIAL | تمام rangeها و rowها ثبت شده‌اند؛ طبقه‌بندی معنایی و اتمی‌سازی هنوز باز است |
| Package Execution Index | PASS | ردیف‌های برنامه‌ای استخراج شدند؛ پیوند معنایی مستقل هنوز بررسی نشده |
| تکراری نبودن IDهای منبع/candidate | PASS/PASS | IDs بررسی‌شده: 1547 source units، 1633 candidateها |
| یکپارچگی دفتر Atomic Obligation | PASS | 73 الزام مستقل؛ چند الزام می‌توانند به یک Candidate متصل شوند |
| یکپارچگی دفتر دسته‌ها | PASS | 53 انتخاب Candidate با نتیجهٔ متصل به Ledger معنایی |
| شناسه‌های Graph | DISCOVERY_ONLY | هم‌پوشانی مکانیکی منبع؛ نه شاهد entailment |
| صحت نحوی ارجاع‌های Package/Req/Task/AC/Test | PASS | تعداد tokenهای کنترل‌شده: 8732؛ معنای نگاشت‌ها هنوز UNVERIFIED است |
| یکپارچگی ارجاع‌های Package Index | PASS | 3706 شناسهٔ استخراج‌شده با سند برنامه تطبیق شد |
| پوشش کامل trace rowها | PASS | 1633 ردیف |
| علت‌دار بودن candidateهای نیازمند بازبینی | PASS | 1633 ردیف |
| پیوندهای Source→Package→Req→Task→AC/Test | UNVERIFIED | همهٔ ارجاع‌های واژگانی فقط candidate هستند |
| وضعیت نگاشت نامعتبر/شکسته | OPEN | پس از اعتبارسنجی IDهای درون برنامه و بازبینی معنایی تعیین می‌شود |

## نقص‌های استخراج که اصلاح شدند

- ۲۶ محدودهٔ متنیِ غیرجدولی در baseline اولیهٔ ۱۱۱۰تایی جا افتاده بود؛ استخراج مجدد ۱۱۳۶ range را یافت و ۲۶ range جدید به شناسه‌های candidate اضافه شد.
- هر ۵۸ جدول به‌صورت block ثبت شده بود اما محتوای ۴۷۰ سطر سرآیند/داده در ledger الزام‌ها نبود؛ ۴۷۰ row به‌عنوان candidate مستقل افزوده شد تا محتوایشان قابل بازبینی باشد. این‌ها الزام اتمی تأییدشده نیستند.
- بلوک fencedهای کد/نمونه نیز جداگانه شمرده و ثبت شد: 27 بلوک؛ محتوای آن‌ها خودکار الزام محسوب نشده است.
- end_line سرعنوان ریشهٔ Blueprint برابر ۲۵۵۱ ثبت شده بود، در حالی‌که آخرین خط فیزیکی فایل ۲۵۵۰ است؛ محدوده اصلاح شد.
- Graph node IDs خالی بود؛ ارجاع‌های مکانی گراف پین‌شده به‌عنوان discovery references اضافه شدند.

## محدودیت معنایی

Rule-based labelها صرفاً برای اولویت‌بندی‌اند. متن چندرفتاری، نمونه، تصمیم باز و قاعده مصوب ممکن است در یک paragraph یا یک سطر جدول کنار هم آمده باشند؛ بنابراین تا تطبیق مستقیم با متن منبع، `Atomic Obligation ID` تخصیص نیافته و هیچ trace به `VERIFIED_COVERED` ارتقا نیافته است. تعداد candidateها با تعداد الزام‌های اتمی برابر نیست.

## منابع و گراف

- `docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md`: Git blob `9681c2bf6c3149317c3788516748084cfb6eac7c`, SHA-256 `0709c84fe9e47e1d9218c6d0f93a82c89a62d6b234565e9b0ca2d4158759f266`, خطوط واقعی `2550`.
- `docs/SHAHAB_DIGITAL_WALLET.md`: Git blob `1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a`, SHA-256 `8b8d139b64f25f8f9592f936c070ece37b3e97df55d4e6b1d0cf305933960b74`, خطوط واقعی `1780`.
- گراف: `17622bf4dd56108bee10d880a9dc5eb9617482fd:knowledge-graph/phase2-reference-docs/semantic/graph.json`؛ SHA-256 `f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93`؛ استفاده برای کشف/ارجاع، نه تأیید نگاشت.
- متن کامل RTF معیارها (در پیوست قبلی) از QG-14 قطع می‌شود؛ این مأموریت براساس پرامپت تکمیلی جاری اجرا شده است.

## مرحلهٔ بعد

بازبین باید candidateها را به ترتیب ریسک و section بررسی کند، موارد MIXED را به اجزای مستقل تقسیم کند، وضعیت هنجاری را با متن مصوب تثبیت کند، سپس فقط پس از تطبیق متن واقعی Requirement/Task/AC/Test به trace وضعیت verified بدهد. موارد باقی‌مانده با علت در `coverage-gap-register.csv` می‌مانند؛ این فایل هنوز gapهای قطعی ادعا نمی‌کند.
