# گزارش اصلاحی PR #258 — قرارداد برنامه‌ریزی فاز پنجم

**تاریخ:** ۲۰۲۶-۱۱-۲۸، منطقهٔ زمانی Asia/Tehran
**مخزن:** `Brotherlouiee/shahab-demo`
**PR:** #258، باز و Draft؛ ادغام نشده
**وضعیت قرارداد:** `PENDING_OWNER_APPROVAL`
**وضعیت اجرای Phase 5 و Phase 5.1:** `NOT_STARTED`

## A. وضعیت اجرایی

- `main` در ابتدای اصلاح و در بررسی نهایی: `e207860d82ccaf665241258256565d064ddd901d`.
- HEAD شاخهٔ PR پیش از اصلاح: `3124c39ddec912eac146411be765df0bca0549a3`.
- SHA نهایی commit در شرح PR ثبت می‌شود؛ درج SHA یک commit در خود همان commit چرخهٔ خودارجاع و تغییر هش ایجاد می‌کند.
- محل کار در worktree ایزوله از PR؛ تغییرات محلی موجود در clone دیگر دست‌نخورده ماندند.
- مسیرهای مجاز تغییرشده: ۹ فایل، همگی زیر `docs/phase5/planning-contract/`؛ فهرست دقیق در بخش «فایل‌های تغییرکرده» است.
- هیچ کد محصول، دادهٔ تثبیت‌شدهٔ Phase 4، mapping، overlay، گراف یا snapshot بازتولید/تغییر نکرده است. هیچ task به هفته تخصیص نیافته و هیچ تصمیم بازی تصویب نشده است.
- ثبت زمان از `2026-11-28 10:39:14 +03:30` آغاز شد؛ مدت پیش از این لحظه اندازه‌گیری نشده و `NOT_MEASURED` است. مدت کار فعال تا checkpoint نهایی پیش از انتشار: `00:22:50` (تا `11:02:04 +03:30`)؛ مدت انتظار CI پس از انتشار جداگانه ثبت می‌شود.
- مصرف توکن در دسترس ابزار نیست: `NOT_MEASURED`.

## B. مطالعه منابع و مصرف داده

| منبع | پوشش واقعی در این اصلاح |
|---|---|
| `AGENTS.md` و `docs/TASK_EXECUTION_PROTOCOL.md` | کامل خوانده شد. |
| راهنمای Git/همکاری محلی | کامل خوانده شد؛ شاخهٔ PR در worktree ایزوله بررسی شد. |
| `SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md` (۱٬۷۸۸ خط؛ blob `680d60fd8fd2038e43714ceca24a5ea4bb7351a4`) | مقدمه و قواعد حاکمیت/تقدم؛ محتوای خطوط ۱–۴۹۷ و بخش‌های مرتبط ۱۲۵۵–۱۴۶۷ مرور شد. کل سند معنایی بازبینی نشده است. |
| `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` (۲٬۵۵۰ خط؛ blob `9681c2bf6c3149317c3788516748084cfb6eac7c`) | §5.2.1، §§5.3–5.4، O5-09/O5-10/F06، §5.14 و A01 بررسی شد؛ کل سند بررسی نشده است. |
| `SHAHAB_DIGITAL_WALLET.md` (۱٬۷۷۹ خط؛ blob `1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a`) | عنوان‌ها/ساختار و بخش‌هایی از safety/ownership/idempotency/retention مرور شد؛ کل سند بررسی نشده است. |
| `SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md` (۸٬۷۶۱ خط؛ blob `daa448b2dbb204b4ab081a38bc13548f1a8c8de6`) | فهرست ساختاری و عنوان بسته‌ها بررسی شد؛ متن بخش‌ها مصرف کامل معنایی نشده است. |
| Snapshot Manifest و ۲۷ artifact | Manifest به‌طور کامل parse شد؛ هویت، hash/size و byte identity هر ۲۷ artifact به‌وسیلهٔ validator کنترل شد. مرور انسانی کامل تمام ledgerها/گراف‌ها انجام نشد. |
| Snapshot/closure/readiness/audit artifacts | اعتبار Snapshot، وضعیت‌های readiness/conditional، محدودیت‌ها و مرز معنایی order/dependency بررسی شد. |

هویت چهار سند حجیم با commit گواهی‌شدهٔ `8ce742b640bbcbb87be5fc29f3a5a28d92593dec` و blob SHA بررسی شد؛ محتوای محلی با همان blobها مطابق است. این احراز هویت، جایگزین مطالعهٔ معنایی نیست.

۲۲ اصل §5.2.1 در trace ثبت شده‌اند؛ O5-01…O5-14، F06، A01…A09 و مرجع کیف پول از تصمیمات جدید جدا شده‌اند. هیچ مصوبهٔ مالک از دادهٔ Phase 4 یا پیشنهاد جدید استنتاج نشده است.

**P5-B03: `NOT_PASS_SOURCE_READING_INCOMPLETE`.** برای تکمیل آن باید مطالعهٔ معنایی با locator و trace منابع باقی‌مانده انجام شود. بر همین اساس **F01 باز می‌ماند**؛ گزارش ادعای تکمیل مطالعه نمی‌کند.

## C. اصلاحات F01–F07

| Finding | علت | اصلاح و فایل‌ها | آزمون/شاهد | باقیمانده | وضعیت |
|---|---|---|---|---|---|
| F01 | پوشش مطالعهٔ منابع حاکم کامل و قابل اثبات نبود. | پوشش انجام‌شده و محدودیت‌ها در همین گزارش شفاف شد؛ trace منابع با locator/commit/blob در `source-policy-trace.csv` نگه داشته شد. | بررسی byte identity؛ خوانش بخش‌های مشخص؛ Snapshot Validator. | بازبینی معنایی کامل اسناد و artifactهای ورودی انجام نشده است؛ B03 NOT PASS. | `OPEN` |
| F02 | وابستگی‌های تصمیمات فاقد نوع و می‌توانستند به‌اشتباه blocker/cycle تلقی شوند. | ۵۸ رابطه با نوع صریح `INFLUENCES`، جهت، rationale و وضعیت پیشنهاد؛ ترتیب بررسی و گروه‌های هم‌تصمیم جداگانه در `decision-register.json` ثبت شد. هیچ رابطهٔ hard prerequisite بدون شاهد ساخته نشد. | ۵۳ fixture مثبت/منفی؛ گراف تقدم الزام‌آور بدون چرخه؛ ۱۶ تصمیم همچنان OPEN. | ترتیب و گروه‌ها پیشنهادی‌اند و نیاز به تصویب مالک دارند. | `RESOLVED_WITH_EVIDENCE` |
| F03 | شواهد CI می‌توانستند از HEAD قدیمی به HEAD جدید نسبت داده شوند و skippedها به‌عنوان موفقیت ظاهر شوند. | commit SHA، run ID، job conclusion و وضعیت `SKIPPED` تفکیک شد؛ سابقهٔ 442b66 حفظ، شواهد HEAD 3124 جدا ثبت؛ شواهد commit نهایی تا اجرای Actions pending است. | API run/job و تطبیق SHA برای HEAD 3124؛ پس از push باید HEAD نهایی دوباره بررسی شود. | CI نهایی این اصلاح هنوز اجرا نشده است. | `PARTIALLY_RESOLVED` |
| F04 | ارجاعات به‌صورت متن/بازه/نام مبهم و فاقد resolver/version بودند. | نوع مرجع، ID دقیق، relation، commit/blob/locator و رفتار مرجع مفقود به schema و رجیستری‌ها افزوده؛ بازه‌ها به IDهای دقیق باز شدند. | مرجع‌سنجی در validator، parse و ۵۳ fixture. | معنای منبع برای بخش‌های مطالعه‌نشده نیازمند تکمیل است. | `RESOLVED_WITH_EVIDENCE` |
| F05 | مدل گراف، نوع بعضی node/edgeها و برش کار چند‌هفته‌ای تعریف کافی نداشت. | رجیستری schema پیشنهادی با endpoint/cardinality و edgeهای تکمیلی از جمله `HAS_WORK_SLICE`؛ سه گزینهٔ چند‌هفته‌ای و مدل exception ثبت شد. | آزمون endpoint/cardinality، چرخه‌ها و fixtureهای چند‌هفته‌ای. | همهٔ نوع‌ها/گزینه‌ها پیشنهادند؛ انتخاب B هنوز تصویب نشده است. | `RESOLVED_WITH_EVIDENCE` |
| F06 | الزام مصوب برآورد قبل از تعهد، با وجود یا نبود قید هزینه تضعیف شده بود. | برآورد effort، هزینهٔ توسعه و بهره‌برداری، token/tool و ظرفیت قبل از هر commitment لازم است؛ Unknown مانع commitment است؛ وضعیت‌ها و واحدها تفکیک شدند. | کنترل schema و fixtureهای unknown/measured/estimate و commitment. | روش/آستانه‌ها و داده‌های واقعی نیازمند تصمیم و اندازه‌گیری‌اند؛ عدد واقعی جعل نشده است. | `RESOLVED_WITH_EVIDENCE` |
| F07 | کنترل ساختاری قبلی، معنای رابطه‌ها، lifecycle، CI و scope را به اندازه کافی نمی‌آزمود. | `validate_planning_contract.py` به‌عنوان validator محدود Phase 5.0 و schema پیشنهادی افزوده شد؛ آزمون‌های مثبت/منفی و کنترل مسیر/Scope دارد. | ۵۳/۵۳ fixture موفق، صفر خطای real validation؛ Snapshot Validator مجدد موفق. | این validator موتور برنامه‌ریزی تولیدی نیست؛ F01 را جایگزین نمی‌کند. | `RESOLVED_WITH_EVIDENCE` |

## D. تصمیمات باز

تمام تصمیم‌های `P5-D01…P5-D16` باز و `PENDING_APPROVAL` هستند. تمام ۵۸ رابطهٔ تصمیمی از نوع `INFLUENCES` و غیرمسدودکننده‌اند؛ ترتیب زیر پیشنهاد مرور است، نه تقدم مصوب. گروه‌های مشترک نیز پیشنهاد هستند.

| ترتیب | شناسه | موضوع | گروه مرور مشترک |
|---:|---|---|---|
| 1 | P5-D01 | مدل تعریف Deliverable | G-DATA-SHAPE |
| 2 | P5-D02 | دانه‌بندی تخصیص کار | G-DATA-SHAPE |
| 3 | P5-D14 | معماری زیرساخت برنامه‌ریزی | G-DATA-SHAPE |
| 4 | P5-D15 | اعتبارسنجی برنامه‌ریزی | G-DATA-SHAPE |
| 5 | P5-D10 | مدیریت تصمیم باز | مستقل؛ تعامل با G-DATA-SHAPE |
| 6 | P5-D03 | مدل ظرفیت توسعه | G-ESTIMATE-CAPACITY |
| 7 | P5-D04 | مدل تخمین effort | G-ESTIMATE-CAPACITY |
| 8 | P5-D05 | مدل تخمین Token | G-ESTIMATE-CAPACITY |
| 9 | P5-D06 | مدل هزینه توسعه | G-ESTIMATE-CAPACITY |
| 10 | P5-D11 | تخصیص Discovery و Delivery | G-ESTIMATE-CAPACITY |
| 11 | P5-D07 | مدل ارزش Deliverable | G-VALUE-UNCERTAINTY |
| 12 | P5-D08 | مدل اولویت‌بندی | G-VALUE-UNCERTAINTY |
| 13 | P5-D12 | عدم‌قطعیت و ریسک | G-VALUE-UNCERTAINTY |
| 14 | P5-D09 | مدل زمان‌بندی هفتگی | G-CYCLE-RELEASE |
| 15 | P5-D13 | پذیرش هفتگی | G-CYCLE-RELEASE |
| 16 | P5-D16 | بازبرنامه‌ریزی مستمر | G-CYCLE-RELEASE |

مصوبات مرتبط برای trace: O5-01…O5-14، BP52-01…22، F06، A01…A09 و WALLET-v0.20. این‌ها تصمیم P5 تازه نیستند و در رجیستری به‌عنوان baseline مصوب/قید trace شده‌اند. شرح مسئله، ۴۹ گزینه و مثال‌های فرضی در `decision-register.json` موجود است؛ هیچ هزینه یا ظرفیت عددی فرضی به‌عنوان واقعیت ثبت نشده است.

## E. آزمون‌ها و Gateها

| Test ID | فرمان/روش | مبنا | نتیجهٔ مورد انتظار | نتیجهٔ واقعی | Exit | شاهد | وضعیت |
|---|---|---|---|---|---:|---|---|
| P5-T01 | `python docs/phase5/planning-contract/validate_planning_contract.py` | 3124c39 + working tree | ۵۳ fixture موفق، صفر خطا، Snapshot معتبر | ۵۳ موفق، صفر ناموفق، صفر خطای real validation | 0 | خروجی محلی `/tmp/p5-final-validation.json` | PASS |
| P5-T02 | `python docs/phase4/task-map-graph/validate_phase4_snapshot.py` | 3124c39 + working tree | ۲۷ artifact؛ source commit و snapshot ID ثابت | `CERTIFIED_SNAPSHOT_VALID`؛ source `8ce742b…`؛ snapshot `phase4-45ed4ec10d34216cf935` | 0 | خروجی فرمان | PASS |
| P5-T03 | `python -c "import csv,json,pathlib; p=pathlib.Path('docs/phase5/planning-contract'); [json.loads(x.read_text()) for x in p.glob('*.json')]; f=p/'source-policy-trace.csv'; r=list(csv.DictReader(f.open(encoding='utf-8-sig',newline=''))); assert len(r)==51; print('JSON PASS; CSV PASS: 51 rows, 14 columns')"` | 3124c39 + working tree | Parse همه JSONها؛ CSV با header، ۵۱ ردیف و ۱۴ ستون | `JSON PASS; CSV PASS: 51 rows, 14 columns` | 0 | پنج JSON و CSV خوانده شدند | PASS |
| P5-T04 | fixtureهای مثبت/منفی validator و real validation | 3124c39 + working tree | typed refs، DAG، graph endpoints، estimate states، lifecycle و scope | ۵۳/۵۳ fixture؛ صفر خطای واقعی؛ ۹ مسیر مجاز | 0 | خروجی validator | PASS |
| P5-T05 | `BASE_SHA=main HEAD_SHA=HEAD python scripts/ci/validate_markdown.py` | 3124c39 + working tree | مستندات تغییرکرده معتبر | دو Markdown معتبر | 0 | `Documentation validation passed for 2 changed Markdown files.` | PASS |
| P5-T06 | `git diff --check`; `git diff --name-status 3124c39`; بازبینی diff نسبت به main | 3124c39 + working tree | whitespace سالم؛ فقط ۹ فایل مجاز | ۹ فایل فقط در `docs/phase5/planning-contract`; بدون تغییر Phase 4 یا کد محصول | 0 | خروجی Git در این اجرا | PASS در working tree؛ کنترل commit نهایی باقی است |

گیت‌های اصلاحی: C01، C02، C04–C13 و C15–C19 با شاهد محلی/ساختاری PASS؛ C03=`PARTIAL` به دلیل مطالعهٔ ناقص منابع؛ C14 و C20 تا CI نهایی=`PENDING_EXTERNAL_CI`. این وضعیت‌ها، تصویب مالک نیستند. CI روی HEAD قبلی 3124 در چهار workflow موفق بود، اما jobهای محصولی طبق طبقه‌بندی docs-only `SKIPPED` شدند و PASS محسوب نمی‌شوند. شواهد دقیق run/job به `planning-contract-validation.json` پیوست شده است.

## فایل‌های تغییرکرده

۱. `PHASE_5_BOOTSTRAP_REPORT.md`
۲. `PHASE_5_EXECUTION_CONTRACT.md`
۳. `acceptance-gates.json`
۴. `decision-register.json`
۵. `output-artifact-registry.json`
۶. `planning-contract-schema.json` (schema پیشنهادی)
۷. `planning-contract-validation.json`
۸. `source-policy-trace.csv`
۹. `validate_planning_contract.py` (validator محدود و غیرعملیاتی)

## F. نتیجه نهایی

- آیا هر هفت ایراد کاملاً رفع شده‌اند؟ **خیر.** F01 باز است و F03 تا تأیید CI commit نهایی جزئی است.
- آیا مأموریت اصلاحی کامل است؟ **خیر؛** B03/P5-C03 کامل نیست و CI نهایی باید بررسی شود.
- آمادگی فنی Phase 5.0: **READY نیست؛ `NOT_READY_SOURCE_READING_AND_FINAL_CI_PENDING`.**
- قرارداد: `PENDING_OWNER_APPROVAL`.
- ۱۶ تصمیم باز حفظ شده‌اند.
- وضعیت PR #258: باید پس از انتشار نهایی همچنان `OPEN_DRAFT` بماند.
- Phase 5.1: `NOT_STARTED`؛ اجرای آن خودکار ممنوع است.
- هیچ merge، deploy، تخصیص واقعی، artifact عملیاتی یا تصمیم مالک انجام نشده است.

گزارش نهایی، HEAD نهایی، مدت اندازه‌گیری‌شده، آزمون‌های نهایی، GitHub Actions و وضعیت هر Gate باید پس از push و اجرای CI در همین فایل تکمیل شوند. اگر CI روی commit نهایی انجام شود، نتیجه در این گزارش/PR description ثبت می‌شود و برای ثبت CI commit دیگری ساخته نمی‌شود.
