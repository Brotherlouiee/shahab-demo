# وضعیت Graphify و تعیین تکلیف یافته‌ها

آخرین Review قابل‌بازیابی Run `3d8b2ea8-f719-40b4-a184-18419145964b` است و Commit بررسی‌شده `79574bc806b5a264dca78f5634d0833c1c7e570e` بود. Gate آن PASS با صفر Blocker و یک یادداشت Coupling دربارهٔ `build_search()` بود. این Review روی HEAD نهایی `ee23df1cd1d04da6fc4a3b05f64655c6c99a4c35` انجام نشده است.

API شش مورد احتمالی اعلام کرد، ولی پنج شرح را برگرداند. پنج شرح قابل‌مشاهده با کد، Builder رسمی، Regression Test و آزمون مرورگر بررسی شدند.

| Finding | تعیین تکلیف | شواهد |
| --- | --- | --- |
| GF-1، فرض اینکه `read_csv` یک List ساده می‌دهد | `FALSE_POSITIVE` | تابع واقعی `(fields, rows)` برمی‌گرداند. Evidence Join Builder دو بار اجرا شد و خروجی برابر بود. |
| GF-2، ردیف کوتاه CSV باعث `AttributeError` می‌شود | `FALSE_POSITIVE_FOR_CURRENT_CONTRACT` | Parser مقدار مفقود را با `ValueError` رد می‌کند و CLI آن را می‌گیرد. تست ردیف کوتاه و شناسهٔ خالی موفق است. |
| GF-3، انتظار صفر برای Cross-only و `contains` | `NO_DEFECT_REPRODUCED` | آزمون Browser روابط `task_mapping` و `decision_scope` را مطابق قرارداد Cross-only لحاظ می‌کند و مقدار صفر ثابت ندارد. |
| GF-4، Endpoint ناموجود باعث TypeError در Browser Test می‌شود | `CONTRACT_GUARD_PRESENT` | آزمون قبل از دسترسی به Node وجود هر دو Endpoint را Assert می‌کند. اعتبارسنجی Endpointهای گراف نیز موفق است. |
| GF-5، Enter جست‌وجو مرکز Node را نمی‌سنجد | `ALREADY_TESTED` | Browser Test مرکز Node و جزئیات آن را در DPR ۱ و ۲ می‌سنجد. |
| GF-6، شرح در دسترس نیست | `UNREVIEWED` | API شش مورد را اعلام کرد ولی پنج شرح داد. هیچ شرحی حدس زده نشد. |

سهمیهٔ Review ماه جاری ۱۰ از ۱۰ مصرف شده و در ۱ دسامبر ۲۰۲۶ UTC بازنشانی می‌شود. Review تازه درخواست نشد. هیچ نتیجه‌ای برای HEAD نهایی ادعا نمی‌شود.


## Targeted delta review status

One read-only status retrieval for PR #257 returned the completed review on `79574bc806b5a264dca78f5634d0833c1c7e570e`. The gate is PASS with zero blockers and one advisory. Investigation reports zero confirmed bugs and six possible issues marked unconfirmed. The response exposed five descriptions. The sixth remains unavailable and is recorded as `UNREVIEWED — EXTERNAL_BLOCKER`. The quota resets at `2026-12-01T00:00:00Z`. No new review was requested.
The delta changed Graph Builder validation and publication. It did not change the Viewer, so the five previously adjudicated Viewer investigation leads were not re-opened.
