# نمای استخراج Core/Wallet — وضعیت Scope مرور C02: RA=PASS / IPA=PASS

**این فایل نمای استخراج/Scope View از CORE_REGISTRY.jsonl است، نه رجیستری پذیرش ۳۶بسته‌ای. وضعیت کل همین رجیستری: PARTIAL؛ آمادگی ممیزی نهایی Scope آن: خیر.**

مرجع رسمی پذیرش برنامه ۳۶ بسته، جدول وضعیت و فصل‌های متناظر در docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md است. وضعیت‌های package/gate و Scope View این رجیستری تاریخچه مرور Source Unit را نشان می‌دهد؛ NOT_STARTED در این نما با پذیرش جاری یک بسته در برنامه تعارض ندارد. رکوردهای تاریخی و قرارداد C02 دست‌نخورده می‌مانند.

C01 با RA=PASS و IPA=PASS در سطح تعریف برنامه حفظ شده است. C02 اکنون RA=PASS و IPA=PASS است؛ پذیرش تعریف برنامه مجوز پیاده‌سازی نیست.

شاخه `docs/phase2-core-remaining-20261117-gpt6`؛ مبنای معتبر `3030623ddb669c9d6cd311d2e032bb911d0cc612`. SHA حامل Checkpoint از Git خوانده شود.

Blob رجیستری مبنا `0b85912bd9b63179fe3572131ea5a6239c130f5b`؛ hash پیشوند تغییرناپذیر `a0c10e1a98e7848a5db43e49857ba9a2b41a9ee0cf6f744289a06e578b84628f`؛ ۲۵۵۴ رکورد قبلی حفظ شده‌اند.

## وضعیت ۱۷ بسته در نمای استخراج (نه شمارنده پذیرش ۳۶بسته‌ای)

| بسته | عنوان | واحدهای مرورشده | نامزد/اتمی | نیازمندی فعال / TE / Task / AC-Test | RA رجیستری/Scope | IPA رجیستری/Scope |
| --- | --- | --- | --- | --- | --- | --- |
| C02 | هویت، سازمان‌ها و مجوزها | 1102 | 102 | 69 / 1 / 5 / 69-69 | PASS | PASS |
| C03 | قراردادها، داده و زیرساخت مشترک | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C04 | اشتراک، پلن و Billing | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C05a | کاتالوگ خدمات شهاب | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C05b | کاتالوگ محصولات مالی و توصیه‌گر | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C06 | پوسته سوپراپ و UI مشترک | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C07 | مالکیت وجوه و مدل اعتبار | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C12a | دفترکل و یکپارچگی مالی | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C08 | شارژ، هدیه و تخفیف | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C09 | مصرف و رزرو | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C10 | انتقال و برداشت | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C11a | استرداد و اصلاحات مالی | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C11b | عملیات دوره‌ای و محدودیت‌ها | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C12b | تطبیق و بازیابی مالی | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C13a | قیمت‌گذاری، تسویه و حسابداری | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C13b | تجربه و پشتیبانی کیف پول | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |
| C14 | سوابق پیام‌ها، اعلان‌ها و Monitoring مشترک | 0 | 0 | ۰ / ۰ / ۰ / ۰ | NOT_STARTED | NOT_STARTED |

## پوشش دو سند و ممیزی معنایی

فهرست G1 نسخه V4 برای هر ۲٬۲۳۰ واحد شناسه، سند، موقعیت و hash دارد. 1363 بازبینی معتبر قبلی استفاده شد و ۸۶۷ واحد تازه در سطح غربال‌گری مشترک تعیین تکلیف شدند؛ ابهام‌های مالکیت با رابطه UNCERTAIN و دلیل ثبت شده‌اند. G1=COMPLETE. از ۳۶ Scope View، یک نما (C02) کامل و ۳۵ نمای بسته‌های آینده INITIAL هستند. C02: 1102 بازبینی عمیق ثبت‌شده، 102 نامزد/رد اتمی، 69 الزام پذیرفته‌شده. شمارش از Commit پایه: ۶۰ Case تکرار سه‌گانه در کل ۲۴۳ مورد (۲۴ فعال و ۳۶ منسوخ/Handoff) و صفر موردِ تکرار فقط دوتایی؛ ۲۴ مورد فعال اصلاح شدند. از ۲۰۷ Case فعال فعلی، 0 مورد با فیلدهای برابر باقی است. RA/IPA=PASS/PASS.

تخصیص بستهٔ دقیق برای حوزه‌های RAG/Assistant در این شاخه قابل اثبات نبود؛ موارد مربوط با owner_domain و pending_package_allocation ثبت شده‌اند. هیچ alias نامعتبر به شناسهٔ بسته تبدیل نشده است. تصمیم‌های باز، اجرای محصول و مستقل‌بودن بازبین ادعا نشده‌اند.

## استفادهٔ مجدد از کد

Existing personal account generation, OTP/session lifecycle and account access tests are reusable for personal identity only. No C02 organization, membership, representative, Shahkar or tenant-scoped customer authorization implementation was found in reviewed backend inventory. Operational admin roles are distinct and not evidence of customer org IAM.

## تعریف برنامه و آزمون

Validator ساختاری و آزمون‌های جهش مستقل اجرا شدند؛ محصول یا رفتار runtime آزموده نشده است. Testهای C02 تعریف دقیق برنامه‌اند و در وضعیت NOT_EXECUTED مانده‌اند.

| مترک | مقدار |
| --- | --- |
| registry records | 6468 |
| C02 candidates and atomic traces | 102 |
| C02 semantic reviews | 1102 |
| accepted atomic requirements | 69 |
| tasks | 5 |
| AC/Test | 69/69 |
| product tests executed | 0 |
| RA/IPA | PASS/PASS |

## وضعیت ادامه

آخرین Scope View کامل رجیستری C02 است؛ مرور عمیق Source Unit برای نماهای بعدی در این workflow ثبت نشده است. C02 در سطح برنامه با RA/IPA تکمیل شده است. C03 را در این Checkpoint آغاز نکن؛ ادامهٔ مجاز بعدی از C03 و با استفاده از G1 تکمیل‌شده و Scope View اولیهٔ همان بسته شروع می‌شود.

نمای ممیزی Source Unit این رجیستری هنوز ۱۷ بسته‌ای و PARTIAL است؛ این وضعیت جای شمارنده پذیرش رسمی برنامه در سند یکپارچه را نمی‌گیرد و `CORE_REMAINING_17_PLANNING_COMPLETE` اعلام نمی‌شود.

## انتشار

انتشار این شاخه برای ایجاد PR به `main` با دستور صریح مالک مجاز شده است؛ Push/PR هنوز انجام نشده و Merge مجاز یا انجام‌شده نیست.

## اعتبارسنجی

```text
python docs/phase2/core/remaining_registry_tools.py --render
python docs/phase2/core/remaining_registry_tools.py --check --mutations
```
