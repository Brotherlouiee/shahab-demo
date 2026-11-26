# ممیزی مستقل کیفی Phase 4 شهاب

**وضعیت:** `CONDITIONALLY_COMPLETED` برای یافته‌های بازتولیدشده و کنترل‌های اجراشده؛ پذیرش نهایی مسدود است.

## خلاصه اجرایی

در شاخهٔ بررسی PR #257 سه نقص قطعی مرتبط با وضعیت انتخاب نمایشگر، نمایش Source Evidence برای Contract Reference و Exit Code اعتبارسنج Source Coverage اصلاح شدند. انتشار Evidence Join Index نیز اکنون با فایل موقت هم‌مسیر و `os.replace` اتمیک انجام می‌شود. آزمون شکست replace حفظ فایل معتبر قبلی را ثابت کرد. داده‌های Ledger بازنویسی‌شده در بازتولید رسمی بدون diff باقی ماندند. هیچ تغییری در تصمیم‌های محصولی یا گراف‌های مرجع ایجاد نشد.

این ممیزی را نمی‌توان «جامعِ نهایی» اعلام کرد، چون سهمیهٔ Graphify برای این ماه تمام شده، شرح یکی از شش مورد بررسی خودکار در API در دسترس نیست، و mutation/performance/branch-coverage و چند Gate از prompt اجرا نشده‌اند. موارد اجرا نشده PASS محسوب نشده‌اند.

## وضعیت مخزن و دامنه

- Base: `392751eaeee882fc770069e3dcd3a161d47a9d26` در PR #257، شاخهٔ `fix/phase4-graphify-review`، مبنا `main`
- PR: https://github.com/Brotherlouiee/shahab-demo/pull/257، باز و هنوز merge نشده
- فایل‌های اصلاح‌شده: `build_and_validate.py`, `build_evidence_join_index.py`, `build_task_map_graph.py`, `task-map-graph.html`, `test_graphify_review.py`, `test_graphify_viewer.cjs`
- دامنهٔ اصلی: دو builder Source Coverage، Stage 4 Replay و Combined Graph، خروجی‌های مشتق‌شده و دو آزمون regression؛ فایل‌های مرجع دیگر فقط برای تطبیق خوانده شدند.
- شناسنامهٔ توابع در `audit-coverage-matrix.csv` ثبت شده است. این رجیستر جایگزین ممیزی دستیِ کامل هر مسیر نیست.

## حوزه‌های ممیزی

| حوزه | نتیجه |
| --- | --- |
| صحت الگوریتم و داده، ساختار گراف، معنای روابط، حفظ اطلاعات و Schema | PASS در بررسی مستقل شمارش‌ها، کلیدها، Endpointها، Snapshotها، ارجاعات و روابط؛ کنترل‌های رسمی نیز PASS |
| مرزها، خطاها و ایمنی فایل | دو سناریوی failure-injection برای انتشار Mapping/Index اجرا شد؛ ماتریس کامل خطای فایل اجرا نشد |
| بازتولیدپذیری | PASS برای خروجی‌های دو Builder در دو اجرا و دو `PYTHONHASHSEED` در Replay/Source Coverage |
| اعتبارسنجی مستقل، کیفیت کد و امنیت | بخشی از قراردادها بررسی شد؛ ابزارهای کامل امنیتی و type/lint اجرا نشدند |
| کارایی و مقیاس | آزمون performance با baseline قابل‌مقایسه انجام نشد |
| مرورگر واقعی و ترکیب فیلتر/حالت | PASS در Chrome 142، DPR 1/2؛ تغییر Canvas با pixel bitmap سنجیده شد |
| سازگاری محیط و آمادگی Phase 5 | Linux و ساختار ورودی مصرف‌کننده بررسی شد؛ Windows، مرورگرهای دیگر و ارزیابی کامل مصرف‌کننده Phase 5 اجرا نشد |

## یافته‌ها و اصلاحات

1. **انتخاب پنهان و جزئیات قدیمی** — FIXED. فیلتر عادی می‌توانست Node/Edge انتخاب‌شده را مخفی کند ولی جزئیات قبلی را نگه دارد. `rebuild()` اکنون انتخاب نامرئی را پاک می‌کند. آزمون مرورگر برای Node، Edge و Open Decision اضافه شد.
2. **Source Evidence گره Contract Reference** — FIXED. گره فاقد `source_ref` بود و Evidence داخل `source_data` داشت. نمایشگر اکنون دادهٔ مستقیم گره را به‌عنوان fallback می‌خواند. آزمون Chromium canonical reference را بررسی می‌کند.
3. **Exit Code اعتبارسنج Source Coverage** — FIXED. Builder فقط `structural_errors` را در Exit Code لحاظ می‌کرد و شکست کنترل ماشینی می‌توانست با Exit موفق خاتمه یابد. شرط خروجی اکنون structural و machine validation را بررسی می‌کند؛ regression سه حالت را می‌آزماید.
4. **نوشتن غیراتمیک Evidence Join Index** — FIXED. انتشار نهایی اکنون با temp sibling، flush/fsync و replace انجام می‌شود. تزریق شکست `replace` ثابت کرد نسخهٔ قبلی حفظ و فایل موقت پاک می‌شود.
5. **Graphify: read_csv tuple** — FALSE POSITIVE. تابع واقعی `(fields, rows)` برمی‌گرداند. ساخت Index و تست‌ها موفق‌اند.
6. **Graphify: short CSV row** — FALSE POSITIVE نسبت به parser واقعی فعلی. ردیف کوتاه و شناسهٔ تهی با خطای کنترل‌شده رد می‌شوند.
7. **Graphify: Cross-only expectation** — نقص آزمون اصلاح شد. انتظار اکنون از مجموعهٔ روابط مجاز واقعی ساخته می‌شود.
8. **Graphify: endpoint lookup** — در harness بررسی صریح Endpointها اضافه است و Validator گراف نیز Endpointها را کنترل می‌کند.
9. **Graphify: Search Enter centering** — نقص آزمون اصلاح شد تا مرکز Node مطابق bitmap و جزئیات انتخابی اثبات شود.
10. **Graphify مورد ششم** — UNREVIEWED. API شمارش شش مورد را اعلام کرد ولی فقط پنج شرح را بازگرداند. هویت و محتوای مورد ششم قابل استنتاج نیست.

توضیح شش مورد و شواهد دقیق در `defect-register.csv` است.

## آزمون‌ها و بازتولید

- 19 آزمون regression پایتون: PASS.
- 29 کنترل Source Coverage: PASS، صفر خطا.
- Stage 4 Replay: PASS، 696 Mapping، 134 تصمیم OPEN و 134 BLOCKED، 99 Relation Overlay، 657 رکورد در 347 فایل. SHA projection برابر `44e4970d7a40853d19dfd8b758466a04f0e8c19389f060d6b135869fab2dd5f5`.
- Combined Graph: PASS، 4,490 Node، 11,435 Edge، 181 Community.
- وضعیت Mapping: 15 MAPPED، 27 PARTIALLY_MAPPED، 654 NEW_IMPLEMENTATION. Overlay برابر 99. Candidate برابر 1,633؛ Atomic Obligation برابر 1,285؛ Covered برابر 1,149؛ Partial برابر 0؛ Open Decision برابر 134؛ Uncovered برابر 2.
- Browser واقعی: Chrome for Testing 142.0.7444.175، DPR 1 و 2. فیلترهای Domain/Package/Community/Node Type/Mapping Status/Relation/Decision، Cross-only و ترکیب فیلترها، Search، انتخاب Node/Edge، Pan، wheel/button Zoom، Fit، Resize، Source Evidence و idle repaint اجرا شدند. Console/page errors برابر صفر.
- Evidence Index، Graph JSON و HTML در دو بار تولید مستقل Byte-for-byte یکسان بودند. دو مقدار `PYTHONHASHSEED` نیز Replay و کنترل پوشش را بدون تغییر projection یا نتیجه گذراندند.
- هش خروجی‌ها و immutable graphها در `test-execution-report.json` درج شده‌اند.

## سه گراف مرجع و تصمیم‌ها

Git Blob و SHA-256 پیش و پس از بازتولید ثابت ماندند: Semantic Graph `a43c1732e85eeebdf83709b9d76233e59ae1a1af` / `f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93`; Code Graph `c19d700b408206458d56798809ec1c7009e08acc` / `0a496833d1a58a6d07e58f3d5d2b59f2c0306a924d8573a687fc4067c549c982`; Task Graph `2393556b74016a437d9a126bee3b04cdcc42be25` / `deb940949583007628dccb89de538c8f3b278aef1c6f99d1386f613f107fa0f7`.

تمام 134 Open Decision همچنان OPEN و Mappingهای آن‌ها BLOCKED هستند. هیچ Ledger، Blueprint، Wallet، Implementation Plan یا گراف مرجع در diff نیست.

## روش‌های آزمون

Static syntax، review مستقل محدود، unit، integration، end-to-end browser، determinism، two-hash-seed، fault injection محدود اجرا شدند. Property-based عمومی، mutation، fuzz، stress، performance budget، Windows، Firefox و Edge اجرا نشدند و در gateها NOT_RUN/BLOCKED هستند.

## Graphify و CI

آخرین بررسی موجود Graphify، PR #257 را روی `79574bc806b5a264dca78f5634d0833c1c7e570e` دیده است؛ gate آن PASS با صفر blocker و یک advisory coupling بود. این بررسی روی HEAD فعلی نیست. سهمیه 10/10 است و تا 2026-12-01 UTC تجدید نمی‌شود. `graphify-final-review.md` شرح محدودیت را دارد.

CI commit `392751e` موفق بود؛ skipped jobs به‌عنوان PASS شمرده نشدند. نتیجهٔ CI commit نهایی این تغییرات باید پس از ثبت Commit از GitHub بررسی و در PR گزارش شود.

## Gateها و تصمیم نهایی

نتیجهٔ هر 22 Gate در `acceptance-gates.json` ثبت شده است. GATE-01، 03، 21 و 22 مسدودند؛ GATE-12، 13، 15 و 18 اجرا نشده‌اند؛ GATE-11، 14، 19 و 20 محدودیت دارند. بنابراین این کار `COMPLETED` نیست و PR را برای Merge تأیید نمی‌کند. PR باز می‌ماند و Merge انجام نمی‌شود.

## شواهد

- `audit-coverage-matrix.csv` — رجیستر فایل‌ها و توابع
- `defect-register.csv` — یافته‌ها و تعیین تکلیف
- `test-execution-report.json` — دستورها، نسخه‌ها، نتیجه‌ها و SHAها
- `acceptance-gates.json` — 22 Gate
- `performance-baseline.json` و `performance-final.json` — وضعیت نبود اندازه‌گیری
- `graphify-final-review.md` — نتیجه و محدودیت آخرین Graphify
