# شبیه‌سازی اجرایی Taskهای ۳۶ بستهٔ فاز دوم

**مقصد:** PR #251، همان سند و شاخهٔ برنامه‌ریزی ۳۶ بسته
**وضعیت:** در حال انجام؛ این دفتر فقط شبیه‌سازی‌های تکمیل‌شده را ثبت می‌کند.
**محدودیت:** شبیه‌سازی برنامه‌ای است؛ هیچ تست محصول، مهاجرت، پرداخت یا استقراری اجرا نشده است.

## C12a — دفترکل و یکپارچگی مالی

### انتخاب Task: `TASK:CORE:C12A:005` — معماری، دوام و پذیرش ledger

**انتخاب پیچیدگی و ریسک:** این Task هم پیچیده است و هم پرریسک؛ بنابراین یک Task برای هر دو معیار انتخاب شده است. زنجیرهٔ backup/restore/migration با دوام سوابق مالی، توازن و lineage پیوند دارد؛ خطا می‌تواند رخداد یا رابطهٔ منشأ را از بین ببرد. منبع مصوب Wallet W:1331 و الزامات `REQ:CORE:C12A:012–013` است.

| بُعد شبیه‌سازی | مسیر و کنترل |
|---|---|
| Preconditions | تعریف مفهومی ledger و invariantهای C12a:001–011 حاضر باشد؛ تغییرات طراحی Core و قراردادهای دادهٔ C01/C03 قابل‌دسترسی باشند. تصمیم‌های باز فناوری، رسانه، تناوب backup و RPO/RTO همچنان باز بمانند. |
| Required inputs | رجیستری رویدادهای مالی دائمی؛ شناسه‌های transaction/entry/account و lineage؛ وضعیت migrationهای مبدأ؛ کنترل دسترسی backup؛ oracleهای توازن، کامل‌بودن و زنجیرهٔ parent/child. |
| Dependencies | C01 برای زیرساخت و migration/restore؛ C02 برای هویت و مجوز دسترسی؛ C03 برای قراردادهای داده و Job؛ C12b برای تطبیق و نتیجهٔ نامعلوم؛ C13a برای نگاشت حسابداری. مالکیت ledger به این بسته‌ها منتقل نمی‌شود. |
| Relevant architecture | دفترکل و دادهٔ مالی تحت مالکیت سرویس Core؛ عملیات recovery در محیط غیرمحصولی؛ زیرساخت restore متعلق به C01. هیچ فناوری یا سرویس مستقل تازه‌ای فرض نمی‌شود. |
| Affected components | طراحی ledger، lineage، مرز restore/migration، کنترل دسترسی، audit trail و گیت پذیرش مالی. |
| Data/API contracts | برای هر entry شناسهٔ پایدار و پیوند مبدأ/والد حفظ شود؛ manifest بازیابی باید تعداد رکوردها و edgeها را قابل تطبیق کند. قرارداد موجود نسخه‌دار و مالکیت‌دار مصرف شود؛ schema فیزیکی یا provider جدید در این Task انتخاب نمی‌شود. |
| Security | دسترسی بازیابی به نقش مجاز محدود و قابل ممیزی باشد؛ backup حفاظت‌شده بماند. روش رمزنگاری، مدیریت کلید و فناوری حفاظت، تا تصمیم معماری باز است و نباید حدس زده شود. |
| Implementation sequence | ۱) invariantها و منبع مبدأ را فهرست کن؛ ۲) چک‌لیست/manifest بازیابی را با C01/C03 تعریف کن؛ ۳) restore یا migration را در محیط آزمون‌پذیر و ایزوله اجرا کن؛ ۴) تعداد، توازن مالی و lineage را با مبدأ مقایسه کن؛ ۵) orphan، اختلاف یا نقص را ثبت و تا رفع آن پذیرش را متوقف کن؛ ۶) گزارش قابل بازبینی و گیت پذیرش را ارائه کن. |
| Deliverables | ماتریس backup/restore/migration؛ مجموعه oracleهای تطبیق کامل‌بودن/توازن/lineage؛ گزارش اجرای محیط غیرمحصولی؛ فهرست اختلاف‌ها و نتیجهٔ گیت پذیرش. |
| Failure scenarios | entry یا edge جاافتاده/تغییرکرده؛ وضعیت partial restore؛ شکست میان بازیابی و تطبیق؛ مجوز نامعتبر؛ ناسازگاری نسخهٔ schema؛ ادعای موفقیت backup ناقص. |
| Recovery | بازیابی ناموفق یا ناقص «موفق» اعلام نشود؛ ورودی/نسخهٔ مبدأ حفظ و اختلاف قرنطینه شود؛ تا تعیین علت، retry کور یا migration بعدی متوقف بماند؛ مسیر اصلاحی پس از تأیید C12a/C01/C12b اجرا شود. |
| Required tests | `AC/TEST:C12A:012`: backup/restore کامل تاریخچه و parent links؛ رکورد یا edge مفقود/تغییریافته شناسایی و رد شود. `AC/TEST:C12A:013`: پس از restore/migration تعداد، توازن و lineage با مبدأ برابر باشد؛ orphan یا اختلاف مانع پذیرش شود؛ partial failure پذیرفته نشود. |
| Acceptance criteria | AC 012 و 013 بدون اختلاف پاس شوند؛ backup ناقص هرگز موفق اعلام نشود؛ تمام اختلاف‌ها شناسه و نتیجهٔ رسیدگی داشته باشند؛ اثر مالی تازه‌ای در restore آزمون ساخته نشود. |
| Definition of Done | ماتریس و oracleها بازبینی شده‌اند؛ اجرای غیرمحصولی شاهد دارد؛ کامل‌بودن، توازن و lineage با مبدأ تطبیق شده‌اند؛ خطاهای باز مسدودکننده ثبت‌اند؛ فناوری‌ها و اهداف بازیابی باز، به‌عنوان تصمیم باز مستند شده‌اند. |
| Integration dependencies | خروجی C01/C03 برای restore و قرارداد داده؛ ورودی/تطبیق C12b؛ کنترل مجوز C02؛ اتصال حسابداری C13a. C14 فقط برای سوابق/اعلان مربوطه مصرف می‌شود و آزمون دوام ledger را جایگزین نمی‌کند. |
| PR/delivery boundary | PR این Task فقط قرارداد/ماتریس آزمون و گیت پذیرش را تغییر می‌دهد؛ بدون تغییر schema عملیاتی، provider، رازها، credential، دادهٔ واقعی یا migration روی محیط مشترک. |
| Open decisions | فناوری ledger/DB/schema/provider؛ رسانه و تناوب backup؛ اهداف RPO/RTO؛ جزئیات مدیریت کلید. این موارد تصمیم مالک‌اند و در این شبیه‌سازی تصویب نمی‌شوند. |
| Blockers | اجرای restore واقعی تا فراهم‌شدن محیط آزمون، دسترسی مجاز و تصمیم‌های معماری محدود است. نبود این تصمیم‌ها مانع تدوین ماتریس و oracleهای مستقل از فناوری نیست. |
| Implementation risks | آزمون ناقص که توازن را بسنجد اما lineage را جا بیندازد؛ اختلاط restore با ثبت اثر تازه؛ دسترسی بیش از حد؛ پنهان‌ماندن orphan؛ تلقی آزمون برنامه‌ای به‌عنوان اثبات runtime. |
| Execution readiness verdict | **آمادهٔ تحویل مشخصات و گیت پذیرش؛ اجرای آزمون واقعی BLOCKED_BY_DECISION/ENVIRONMENT.** یک توسعه‌دهنده+Codex می‌تواند همین Task مستندسازی/طراحی را بدون انتخاب فناوری انجام دهد؛ نمی‌تواند انطباق runtime یا آمادگی انتشار را بدون تصمیم و محیط لازم اعلام کند. |

**وضعیت پوشش QG‑13:** یک شبیه‌سازی Task برای C12a ثبت شد. ۳۵ بستهٔ دیگر و انتخاب/شبیه‌سازی دوم برای هر بسته هنوز باید تکمیل شود؛ نتیجهٔ QG‑13 فعلاً `FAIL` باقی می‌ماند.

## C12b — تطبیق و بازیابی مالی

### انتخاب Task: `TASK:CORE:C12B:003` — بازیابی و جلوگیری از تکرار

**انتخاب پیچیدگی و ریسک:** این Task هر دو معیار را دارد: نتیجهٔ بانکی ممکن است نامعلوم بماند و همزمان callback/replay/retry خطر اثر مالی تکراری ایجاد می‌کند. برای این Task یک شبیه‌سازی مشترک ثبت می‌شود؛ این هم‌پوشانی فقط برای همین Task مستدل است.

| بُعد شبیه‌سازی | مسیر و کنترل |
|---|---|
| Preconditions | قرارداد inquiry و شناسهٔ پایدار operation در دسترس باشد؛ مالک posting/یکتایی C12a و Job/idempotency عمومی C03 حفظ شوند. وضعیت واقعی بانک با timeout به موفق/ناموفق تبدیل نشود. |
| Required inputs | شناسهٔ operation و correlation؛ مبلغ/در معرض تعهد؛ پاسخ provider و زمان دریافت؛ وضعیت inquiry؛ سابقه callback/replay؛ سقف retry و مهلت‌ها، فقط پس از تصمیم مالک. |
| Dependencies | C12a برای یکتایی و ثبت اثر؛ C03 برای Job/event؛ C11b برای exposure و محدودیت دوره‌ای؛ C14 برای هشدار؛ قرارداد provider/API در بستهٔ مالک عملیات. |
| Relevant architecture | C12b نتیجهٔ تطبیق و مسیر بازیابی را مالک است؛ C12a تنها مالک state/posting دفترکل است. وضعیت خدمت، بانک و ledger سه چرخهٔ جدا اما linked می‌مانند. |
| Affected components | worker تطبیق، operation-status inquiry، unresolved queue، callback handler، retry controller و پروندهٔ مغایرت. |
| Data/API contracts | retry همان operation ID را نگه می‌دارد؛ inquiry با correlation ID پایدار می‌شود؛ ledger write فقط از قرارداد C12a؛ نتیجهٔ نامعلوم به‌عنوان `unresolved/unknown` تحویل داده می‌شود. شماره/نام endpoint provider در برنامه تعیین نشده و ساخته نمی‌شود. |
| Security | مجوز سرویس‌به‌سرویس و audit دسترسی/تغییر؛ حداقل دادهٔ بانکی؛ عدم نمایش داده به نقش نامجاز. جزئیات credential/provider خارج این Task و تحت قراردادهای مالک مربوط است. |
| Implementation sequence | ۱) transitionهای unknown/inquiry/resolved را تثبیت کن؛ ۲) شناسه و idempotency کل مسیر را بررسی کن؛ ۳) inquiry پیش از retry؛ ۴) retry محدود همان operation؛ ۵) duplicate callback/replay را بی‌اثر کن؛ ۶) unresolved را صف/پرونده کن و فقط پس از resolution به C12a نتیجه بده؛ ۷) هشدار مادی را به C14 handoff کن. |
| Deliverables | state model؛ قرارداد inquiry/retry؛ منطق صف unresolved؛ پروندهٔ قابل ممیزی؛ test matrix duplicate/replay/unknown؛ گزارش تعامل با C12a/C03/C14. |
| Failure scenarios | inquiry نامعلوم؛ callback تکراری/خارج از ترتیب؛ timeout در حین retry؛ provider موفق اما ledger هنوز pending؛ سقف retry تمام؛ پاسخ provider با شناسهٔ ناسازگار. |
| Recovery | status inquiry و بررسی پرونده پیش از اقدام؛ تا resolution exposure متناسب نگه داشته شود؛ retry همان operation و محدود؛ هیچ عملیات مالی تازه برای «اصلاح» ساخته نشود؛ posting و reconciliation از مرز مالک C12a/C12b تبعیت کند. |
| Required tests | `C12B-AC/TD04`: unknown با inquiry موفق/unknown؛ `AC/TD05`: retry همان operation و محدود؛ `AC/TD06`: duplicate event و provider redelivery اثر دوم نسازد؛ `AC/TD08`: exposure فقط تا resolution حفظ شود. |
| Acceptance criteria | نامعلوم بدون inquiry تعیین تکلیف نشود؛ retry operation جدید نسازد؛ callback/replay اثر مالی دوم نداشته باشد؛ exhaustion به unresolved/پرونده ختم شود؛ C12b state دفترکل را مستقیم تغییر ندهد. |
| Definition of Done | transition و قرارداد مالکیت‌دار؛ تست‌های مثبت/منفی/مرزی؛ duplicate/replay و timeout پوشش‌دار؛ وضعیت unresolved قابل مشاهده؛ اتصال C12a/C03 مستند؛ هیچ پارامتر باز به‌صورت مقدار مصوب جعل نشده باشد. |
| Integration dependencies | C03 Job/event idempotency؛ C12a posting و status ledger؛ C11b exposure/limits؛ C14 هشدار. Adviser/Assistant وابستگی اجرایی ندارند. |
| PR/delivery boundary | تغییرات محدود به C12b worker/contract/tests و مستندات؛ provider واقعی، credential، پول واقعی، migration و تنظیمات production خارج از PR. |
| Open decisions | سقف/فاصله/مهلت retry، escalation owner/SLA، قرارداد provider و threshold هشدار. تصمیمی در این شبیه‌سازی اتخاذ نمی‌شود. |
| Blockers | اتصال واقعی provider و مقادیر retry تا قرارداد و تصمیم مالک مشخص نشده باشد؛ تست قرارداد با mock/fixture و طراحی idempotency قابل انجام است. |
| Implementation risks | دوگانگی source of truth برای وضعیت؛ retry جدید به‌جای retry همان operation؛ callback دیررس پس از پرونده‌بندی؛ تمیزکردن unresolved با دستکاری ledger؛ آستانهٔ فرضی. |
| Execution readiness verdict | **آماده برای طراحی state/contract و تست‌های شبیه‌سازی‌شده؛ اجرای provider و تأیید SLA BLOCKED_BY_DECISION.** توسعه‌دهنده+Codex می‌تواند مرز و کنترل‌های مصوب را پیاده کند؛ فعال‌سازی مسیر بانکی بدون تصمیم‌های باز مجاز نیست. |

**وضعیت پوشش:** برای C12b یک شبیه‌سازی Task ثبت شد. C12b نیز هنوز شبیه‌سازی دوم و سایر بسته‌ها را لازم دارد؛ QG‑13 همچنان `FAIL` است.

## C04 — اشتراک، پلن و Billing

### Task پیچیده: `TASK:CORE:C04:007` — قراردادهای Billing، اسناد و اختلاف

| بُعد | شبیه‌سازی |
|---|---|
| Preconditions / inputs | تصمیم‌های E04 مربوط به قیمت و سفارشِ مصوب از Wallet؛ شناسه و version اشتراک؛ قراردادهای C01:03–06؛ stateهای پرداخت و نمونه‌های receipt/invoice. FD‑03 و معنای سند حسابداری قطعی نشده‌اند. |
| Dependencies / architecture | C04 مالک state رویداد Subscription؛ C12a دفترکل؛ C12b تطبیق؛ C13a سند حسابداری؛ C13b receipt/تجربه؛ C14 اعلان. رویداد و API در معماری Core نسخه‌دار و سرویس‌مالک می‌مانند. |
| Components / contracts | event envelope، correlation/idempotency، audit/history، invoice/receipt references، پرونده اختلاف. معناهای invoice، وصول، مصرف، receipt و سند مالیاتی جدا می‌مانند؛ هیچ سرویس مقصد را C04 تصاحب نمی‌کند. |
| Security | دسترسی tenant و سوابق طبق C02؛ اسرار پرداخت ذخیره/اعلان نمی‌شوند؛ صورت‌حساب سازمانی فقط به عضو مجاز. |
| Work sequence | تعریف owner و schema قراردادی؛ تعیین state و correlation؛ افزودن پیوند سند با شناسهٔ خارجی و نوع سند؛ مدل پرونده اختلاف و مسئول؛ طراحی out-of-order/duplicate؛ افزودن contract tests با مصرف‌کننده‌های مقصد؛ ثبت Handoff برای موارد نامعلوم. |
| Deliverables | قرارداد API/Event؛ مدل reference سند؛ state machine اختلاف؛ ماتریس consumerها و tests ناسازگاری/دوباره‌رسیدن. |
| Failure / recovery | duplicate event، سند ناموجود/نامتوازن، consumer ناسازگار، تأخیر reconciliation، اختلاف بی‌مسئول. رویداد تکراری idempotent؛ وضعیت اختلاف باز و قابل ارجاع می‌ماند؛ سند مالی جدید حدس زده نمی‌شود. |
| Tests / AC | REQ:CORE:185–188 و AC/TEST:C04:052–056،059–060: idempotency، status history، فاکتور سازمانی پیش از پرداخت، جدایی سندها، اعلان بدون consent، access isolation. |
| DoD / integration | producer/consumer و version اعلام‌شده؛ AC/Test و مالک هر state پیوند دارند؛ قرارداد با C12a/C12b/C13a/C13b/C14 بازبینی شده؛ migration یا provider اجرا نشده. |
| PR boundary | فقط قرارداد، state و test fixtures؛ بدون داده/credential واقعی یا migration. |
| Open decisions / blockers | FD‑03 و الزامات متخصص برای قالب اسناد؛ SLA اختلاف؛ provider/payment implementation. این موارد فعال‌سازی پولی را متوقف می‌کنند، نه تعریف قرارداد دامنه را. |
| Risks / readiness | خطر مالکیت مبهم اسناد، تعارض semantics سند و اعلان به‌عنوان پرداخت. **آماده برای تغییر قراردادی برنامه‌ریزی‌شده؛ پذیرش سند قانونی و اجرا تا تصمیم متخصص مسدود است.** |
| Required inputs | شناسه subscription/operation، نوع سند، version/issuer، وضعیت reconciliation و purpose دسترسی؛ نبود هر فیلد به‌عنوان OPEN/ناموجود ثبت شود. |
| Relevant architecture | C04 مالک state اشتراک و ارتباط سندی است؛ C12a/C12b/C13a/C13b/C14 مالکیت‌های مستقل را حفظ می‌کنند. |
| Affected components | قرارداد subscription event، سند reference، اختلاف، history و integration tests؛ migration یا provider انتخاب نمی‌شود. |
| Data/API contracts | هر event دارای identity/version/correlation؛ receipt/invoice نوع‌دار و پیوند به operation؛ state source-owned و idempotent. |
| Failure scenarios | دریافت تکراری/خارج از ترتیب، سند صادرنشده/ناسازگار، consumer قدیمی، اختلاف بدون owner یا اعلان اشتباه. |
| Recovery | رویداد تکراری بی‌اثر؛ سند نامعتبر quarantine؛ اختلاف unresolved ارجاع؛ هیچ receipt یا posting جدید برای ترمیم حدس زده نشود. |
| Acceptance criteria | AC/TEST:C04:052–056,059–060: history و idempotency برقرار؛ invoice ≠ payment؛ مصرف‌کننده مجاز؛ اطلاع‌رسانی consent-aware. |
| Blockers | قالب حقوقی/مالی نهایی و SLA اختلاف نیازمند owner متخصص؛ پیاده‌سازی قرارداد و fixture می‌تواند مستقل پیش برود. |

### Task پرریسک: `TASK:CORE:C04:008` — گیت فعال‌سازی/حالت آماده

| بُعد | شبیه‌سازی |
|---|---|
| Preconditions / inputs | CONTRACT:C01:05 و :07؛ تصمیم FD‑02؛ evidence dossier مالی، امنیتی، مجوزی، حقوقی و شکست/بازیابی؛ مقدار flag نسخه‌دار. |
| Dependencies / architecture | Release/Finance Governance مالک تصمیم rollout؛ C04 مصرف‌کنندهٔ flag؛ C01 مالک قراردادهای آماده‌سازی/Kill Switch. هیچ وابستگی به RAG یا Assistant ایجاد نمی‌شود. |
| Components / contracts | PREPARE_ONLY/Enable/Kill Switch؛ backend enforcement؛ gate evaluator و audit record. Flag فقط زیرساخت را آماده/غیرفعال نگه می‌دارد و هرگز مجوز/پرداخت را جایگزین نمی‌کند. |
| Security | default-deny؛ احراز نقش/دسترسی؛ change audit؛ kill switch آزموده؛ هیچ اثر مالی از مسیر UI/flag بدون گیت backend. |
| Work sequence | تعریف شروط دودویی evidence؛ بررسی مالک و نسخهٔ هر مدرک؛ اعمال flag در حالت بدون اثر؛ آزمون bypass و kill; تمرین failure/recovery؛ produce decision record Enable Now/Prepare Only/Defer؛ توقف در اولین شاهد ناقص. |
| Deliverables | gate checklist، evidence dossier، flag contract، kill-switch test، decision record. |
| Failure / recovery | نقص/انقضای evidence، bypass از endpoint، flag ناسازگار، kill switch نامؤثر، rollback ناقص. حفظ حالت غیرفعال؛ توقف درخواست rollout؛ rollback به حالت آماده؛ بررسی و ثبت رخداد. |
| Tests / AC | `AC/TEST:C04:057`: PREPARE_ONLY و KILL_SWITCH بدون اثر مالی، flag دسترسی را اعطا نکند. `AC/TEST:C04:058`: هر gate ناقص، Enable را رد کند؛ هیچ اشتراک/پرداخت واقعی پیش از تکمیل gateها. |
| DoD / integration | همهٔ evidenceها معتبر و versioned؛ آزمون bypass/failure/recovery و kill pass؛ تصمیم صریح ثبت‌شده؛ مالک مجاز تأیید کند؛ در نبود هر شرط، status Defer/Prepare Only باقی بماند. |
| PR boundary | فقط gate documentation/contract/tests. این Task خودِ rollout یا فعال‌سازی نیست و درخواست Enable را بدون approval مالک اجرا نمی‌کند. |
| Open decisions / blockers | FD‑02 و پذیرش حقوقی/مالی/امنیتی؛ فقط owner می‌تواند وضعیت را Enable Now کند. |
| Risks / readiness | مالی و reputational high risk؛ پرچم به‌اشتباه مجوز تلقی شود. **مشخصات و آزمون fail-closed آماده‌اند؛ Enable مسدود تا تأیید تمام gates.** |
| Required inputs | نسخهٔ flag، وضعیت PREPARE_ONLY، evidence dossier دارای owner/expiry/version، نتیجهٔ gate و مجوز تصمیم rollout. |
| Relevant architecture | release owner تصمیم می‌گیرد؛ C04 مصرف می‌کند؛ C01 قرارداد config/gate/Kill Switch را مالک است؛ backend policy مستقل از UI می‌ماند. |
| Affected components | gate evaluator، backend action path، audit record، kill-switch path، compatibility/rollback dossier. |
| Data/API contracts | flag فقط typed operational state؛ enable command باید actor، scope، evidence revision و approval reference داشته باشد. |
| Failure scenarios | evidence missing/expired، bypass endpoint، role revoked، flag stale، kill-switch failure، rollback ناسازگار. |
| Recovery | deny-by-default؛ PREPARE_ONLY یا Defer حفظ؛ rollback فقط به نسخه سازگار؛ بررسی incident پیش از هر درخواست تازه. |
| Acceptance criteria | AC/TEST:C04:057–058؛ flag مجوز ندهد؛ هیچ side-effect واقعی در آماده‌سازی؛ نقص هر gate مانع Enable شود. |
| Blockers | approval مالک و تکمیل حقوقی/مالی/امنیتی صریح است؛ این شبیه‌سازی اجازهٔ rollout صادر نمی‌کند. |

**وضعیت شبیه‌سازی:** دو Task متمایز C04 (یکی پیچیده، یکی پرریسک) ثبت شد. این‌ها مجوز فعال‌سازی پرداخت یا پذیرش محصول نیستند.

## C02 — هویت، سازمان‌ها و مجوزها

### Task پیچیده: `TASK:CORE:C02:002` — چرخهٔ عضویت سازمان

**انتخاب:** پیچیدگی از چند حالت عضویت (فهرست اولیه، دعوت، احراز، پذیرش، تطبیق حساب، فعال، سابق و بازیابی مدیر)، حفظ جدایی عضویت‌های چندسازمانی، و اثر حذف عضو بر سوابق ناشی می‌شود. این Task به‌تنهایی برای معیار ریسک مالی انتخاب نشد؛ Task 005 شبیه‌سازی پرریسک جداگانه دارد.

| بُعد | شبیه‌سازی و شاهد برنامه |
|---|---|
| Preconditions | قرارداد سازمانی TASK 001 بازبینی شده باشد؛ baseline رفتار حساب شخصی ثبت شود؛ تصمیم‌های DECISION:C02:01/:02 فقط پیش از تطبیق بیرونی، بازیابی نماینده یا فعال‌سازی حل شوند. |
| Required Inputs | synthetic org/member/account IDs؛ ورودی roster؛ دعوت و پذیرش؛ وضعیت حساب؛ نقش/وابستگی؛ سوابق متعلق به عضو؛ شواهد قرارداد/نمایندگی و audit transition. |
| Dependencies | TASK 001 برای هویت/قرارداد؛ TASK 003 برای scope/مجوز؛ C01 قرارداد API و migration؛ C13b برای receipt شخصی عضو سابق در حد handoff. |
| Relevant Architecture | سرویس Core مالک هویت و چرخه عضویت است؛ فهرست roster به‌تنهایی عضویت فعال نمی‌سازد؛ خروجی‌های Ledger، حسابداری یا Wallet با خروج عضو منتقل یا حذف نمی‌شوند. |
| Affected Components | مدل سازمان/عضو/دعوت، قیدهای پایگاه داده، import roster، پذیرش دعوت، لغو عضویت، بازیابی مدیر و مجوز دسترسی عضو سابق. |
| Data/API Contracts | transition و actor/tenant/object scope باید ثبت شود؛ کلیدهای پایدار سازمان و عضو؛ یکتایی دعوت/عضویت؛ API version و خطای قابل مشاهده از قرارداد C01؛ قرارداد فیزیکی تا تصمیم مالک باز می‌ماند. |
| Security Requirements | fail-closed در تطبیق حساب/نماینده؛ جدایی tenant؛ فقط عضو سابق به receipt متعلق به خودش دسترسی دارد؛ حذف عضویت حق مالکیت یا مشاهدهٔ دادهٔ شخصی دیگران نمی‌دهد. |
| Implementation Work Sequence | ۱) مدل فعلی را inventory کن؛ ۲) transition table را با 056/057/060–063/070/072–074 تطبیق بده؛ ۳) قیود و idempotency دعوت را طرح کن؛ ۴) import roster را بدون activation اجراپذیر کن؛ ۵) پذیرش/لغو/بازیابی را در transaction مرزبندی کن؛ ۶) دسترسی عضو سابق و حفظ سوابق را بیازمای؛ ۷) migration/backfill را فقط پس از baseline و تصمیم‌های لازم پیشنهاد کن. |
| Deliverables | state machine عضویت؛ قرارداد roster/import/invitation؛ ماتریس دسترسی چندسازمانی؛ طرح constraint و migration؛ آزمون‌های انتقال/حذف/بازیابی. |
| Failure Scenarios | roster تکراری؛ دعوت replay؛ حساب متعلق به شخص دیگری؛ عضو در دو سازمان؛ نمایندهٔ نامعتبر؛ لغو همزمان با read؛ بازیابی مدیر بدون مدرک؛ حساب legacy ناسازگار. |
| Recovery Strategy | import قابل تکرار و بدون activation؛ transition نامعتبر rollback شود؛ عضویت مبهم قرنطینه و handoff شود؛ دادهٔ مالی/receipt حذف یا منتقل نشود؛ بازیابی مدیر تا شواهد معتبر متوقف بماند. |
| Required Tests | `AC:CORE:C02:007/008/011–014/021/023–025`; `TEST:CORE:C02:*` سناریوهای synthetic برای roster-only عدم activation، جدایی tenant، دسترسی receipt عضو سابق و حفظ سوابق پس از removal؛ همه `NOT_EXECUTED`. |
| Acceptance Criteria | roster-only inactive بماند؛ دو سازمان دادهٔ یکدیگر را نخوانند؛ حذف دسترسی آینده را ببندد ولی سوابق متعلق را حفظ کند؛ receipt سابق محدود به خودش باشد؛ بازیابی مدیر بدون شواهد رد شود. |
| Definition of Done | هر transition مالک و oracle دارد؛ قیود مانع duplicate هستند؛ positive/negative/boundary/failure برای import، invitation، revoke و recovery مشخص است؛ baseline و migration risk مستندند. |
| Integration Dependencies | C01 API/migration؛ TASK 001 identity evidence؛ TASK 003 authorization؛ C13b receipt boundary؛ هرگونه دفترکل/تعهد مالی فقط از مالک Wallet/Ledger مصرف می‌شود. |
| PR/Delivery Boundary | طراحی و پیاده‌سازی برنامه‌ای Core Identity، constraints و تست‌های ایزوله؛ بدون اتصال شاهکار/ثبت احوال واقعی، فعال‌سازی سازمان یا migration روی داده مشترک. |
| Open Decisions | provider و شروط تطبیق بیرونی، بازیابی نماینده و الزامات قانونی/قرارداد طبق DECISION:C02:01/:02 باز می‌مانند. |
| Blockers | فعال‌سازی تطبیق بیرونی/بازیابی نماینده تا تصمیم‌های بالا؛ baseline و طراحی transition محلی مستقل قابل انجام است. |
| Implementation Risks | roster به‌اشتباه authority شود؛ membership مشترک بین tenantها؛ حذف سوابق به همراه دسترسی؛ race عضویت/revoke؛ تغییر رفتار حساب شخصی. |
| Execution Readiness Verdict | **آماده برای state/contract/fixture و طراحی migration؛ بخش‌های متکی به DECISION:C02:01/:02 مسدود.** بررسی واقعی baseline پروژه پیش‌نیاز تغییر اجرایی است و محصول هنوز اجرا/تست نشده. |

### Task پرریسک: `TASK:CORE:C02:005` — step-up و شواهد دسترسی

**انتخاب:** ریسک بالا به علت تغییر مجوز یا limit در فاصلهٔ بررسی و اثر حساس (برداشت/افزایش هزینه)، stale authorization و احتمال باقی‌ماندن دسترسی پس از revoke. TASK 003/004 پیش‌نیازند.

| بُعد | شبیه‌سازی و شاهد برنامه |
|---|---|
| Preconditions | ماتریس مجوز TASK 003 و قرارداد session TASK 004 بازبینی شوند؛ DECISION:C02:03 پیش از فعال‌کردن freshness threshold یا retention حل شود؛ حالت اولیه synthetic و کم‌دسترسی باشد. |
| Required Inputs | actor/tenant/action/object؛ permission و limit version؛ timestamp/revalidation state؛ تغییر نقش/revoke؛ نیاز step-up؛ action checkpoint؛ حداقل access-event fields. |
| Dependencies | C02 TASK 003/004؛ C01 config/flag/error/API contract؛ C12a/C03/C14 فقط برای handoff نگهداری مالی/Job/event، نه تصاحب IAM access evidence. |
| Relevant Architecture | authorization server-side در Core؛ gate در نقطهٔ پیش از reservation/increase/new cost؛ بازبینی مجدد نزدیک commit؛ IAM access log مستقل از ledger retention. |
| Affected Components | policy evaluator، session/auth cache، step-up adapter، action checkpoint، safe-stop/hold، audit-event schema. |
| Data/API Contracts | action، scope، policy version، decision، time و trace reference حداقلی؛ بدون secret/OTP/raw credential؛ قرارداد access event و نسخه با ownerهای مشترک ثبت شود. |
| Security Requirements | deny-by-default؛ revoke و کاهش limit فوراً مؤثر در next critical checkpoint؛ step-up مختص action؛ عدم ثبت secret؛ no UI-only authority. |
| Implementation Work Sequence | ۱) حساسیت actionها را طبق مصوبه فهرست کن؛ ۲) trigger و revalidation predicate را به قرارداد موجود وصل کن؛ ۳) نقطهٔ check پیش از reservation/cost مشخص کن؛ ۴) تغییر مجوز میان check/commit را inject کن؛ ۵) safe-stop/hold را طراحی و بازیابی امن را بیازمای؛ ۶) IAM event حداقلی را از مالی جدا کن؛ ۷) DECISION:C02:03 را گیت تنظیمات باقی بگذار. |
| Deliverables | action-specific step-up matrix؛ state machine revoke/hold؛ قرارداد access-event؛ ماتریس تست race، limit و secret exclusion؛ handoff retention. |
| Failure Scenarios | revoke بعد از pre-check؛ کاهش limit میان رزرو و commit؛ step-up timeout/ناموفق؛ cache stale؛ event sink unavailable؛ تلاش logging برای secret. |
| Recovery Strategy | state را hold/deny کن؛ state مجوز را تازه بخوان؛ پس از رفع فقط همان action را دوباره ارزیابی کن؛ اقدام مالی تکراری نساز؛ logging failure را بی‌صدا موفق اعلام نکن؛ طبق قرارداد safe-stop مسیر رسیدگی. |
| Required Tests | AC C02:022/027–029/069–071/075–076/081 و `TEST:CORE:C02:*`; revoke race، limit boundary، allowed access event، نبود secret، و جدایی retention ledger. `NOT_EXECUTED`. |
| Acceptance Criteria | revoke/limit جدید در checkpoint enforce شود؛ action حساس بدون step-up لازم commit نشود؛ deny هیچ اثر مالی نداشته باشد؛ audit فقط حداقل داده را نگه دارد؛ ledger retention به آزمون IAM نسبت داده نشود. |
| Definition of Done | هر action trigger/oracle/خطا/recovery دارد؛ race و cache freshness پوشش آزمونی دارند؛ event owner/fields/retention handoff مشخص است؛ DECISION باز به مقدار فرضی تبدیل نشده است. |
| Integration Dependencies | C01 برای config/error/change audit؛ C02 TASK 003/004؛ C12a مالک ledger؛ C03/C14 طبق قرارداد خود برای رویداد/نگهداری. |
| PR/Delivery Boundary | IAM authorization, checkpoints و test harness synthetic؛ بدون دسترسی credential واقعی، اثر مالی واقعی، تعیین threshold یا تنظیم production. |
| Open Decisions | DECISION:C02:03 درباره freshness/retention و جزئیات step-up باز است؛ عدد یا SLA تازه تعریف نمی‌شود. |
| Blockers | فعال‌سازی threshold/retention دقیق تا DECISION:C02:03؛ policy و fail-closed tests با threshold unset قابل تدوین است. |
| Implementation Risks | race در check/commit؛ bypass در یکی از endpointها؛ confusion میان audit مالی و IAM؛ cache invalidation ناقص؛ نگهداری PII بیش از حد. |
| Execution Readiness Verdict | **آمادهٔ طراحی fail-closed و آزمون synthetic؛ تنظیم آستانه/retention و اجرای محصول BLOCKED_BY_DECISION.** برنامه مالک، Task، AC و سناریوهای متناظر می‌دهد؛ محصول آزموده نشده است. |

**نتیجهٔ QG-13 برای C02:** دو مسیر واقعی از Taskهای موجود شبیه‌سازی شدند؛ یکی پیچیده و دیگری پرریسک. آمادگی بخش‌های وابسته به تصمیم باز صریحاً محدود است. این نتیجه قبولی QG-13 کل برنامه را تغییر نمی‌دهد.

## C01 — معماری و مبانی مشترک Core

### Task پیچیده: `TASK:CORE:C01:006` — Outbox تراکنشی و مصرف idempotent

**انتخاب پیچیدگی:** ترتیب atomic write، publish، duplicate/out-of-order و schema evolution در چند مالک سرویس مداخله می‌کند؛ شرط برنامه این است که فقط برای جریان async اثبات‌شده اعمال شود.

| بُعد | شبیه‌سازی مبتنی بر `REQ:CORE:012/043/044`, `AC:CORE:C01:012/043/044` |
|---|---|
| Preconditions | مالک داده و public port از `TASK:CORE:C01:002` روشن؛ use case واقعاً async و consumer مشخص؛ job contract از `TASK:CORE:C01:005` موجود؛ اگر مصرف‌کنندهٔ لازم نیست، outbox تحمیل نشود. |
| Required Inputs | owner transaction، event purpose/schema/version، producer و consumer، idempotency key، ordering need، failure/replay fixtures و مرجع تغییر سازگار. |
| Dependencies | `TASK:CORE:C01:002` hard؛ `TASK:CORE:C01:005` contract؛ سرویس مالک event و consumer مربوط؛ C03 فقط طبق data/Job ownership. |
| Relevant Architecture | modular monolith و ماژول‌های مالک داده؛ outbox محلی با تراکنش مالک؛ publisher/consumer از port؛ broker/engine جدید پیش‌فرض نیست. |
| Affected Components | transaction boundary، outbox table/interface، publisher، consumer inbox/dedup، schema registry/compatibility check و runbook recovery. |
| Data/API Contracts | event ID، owner, type, version, correlation, occurred-at و payload حداقلی؛ consumer نسخه ناشناخته را رد/قرنطینه کند؛ payload حساس بی‌جهت منتشر نشود. |
| Security Requirements | دسترسی publisher/consumer کمینه؛ tenant scope و audit؛ secrets/PII در payload/log نرود؛ رویداد به‌تنهایی مجوز یا منبع حقیقت مالی نیست. |
| Implementation Work Sequence | ۱) رویدادهای واقعاً ضروری را شناسایی؛ ۲) owner transaction و invariant را تعیین؛ ۳) schema/version و dedupe key را تصویب/ثبت؛ ۴) commit+outbox atomarity را مدل کن؛ ۵) crash هر مرز را fault inject کن؛ ۶) duplicate/out-of-order/unknown version را مدل کن؛ ۷) recovery و telemetry را با consumer بازبینی کن. |
| Deliverables | فهرست event/use case مجاز؛ contract envelope/version؛ state transitions؛ fixture و fault matrix؛ consumer compatibility و recovery instructions. |
| Failure Scenarios | commit بدون event؛ event بدون commit؛ crash پس از publish پیش از mark؛ duplicate؛ out-of-order؛ poison payload؛ نسخه ناشناخته؛ consumer unavailable. |
| Recovery Strategy | redelivery با همان event ID؛ consumer idempotent؛ quarantine برای schema ناشناخته؛ replay محدود و قابل audit؛ هیچ side effect خارج مالک تکرار نشود. |
| Required Tests | AC/TEST مربوط به `C01:012/043/044`: commit atomicity، crash/replay، duplicate و schema incompatibility؛ هیچ مورد برنامه‌ای اجراشده محسوب نمی‌شود. |
| Acceptance Criteria | رویداد بدون transaction معتبر منتشر نشود؛ crash منجر به گم‌شدن خاموش یا اثر دوگانه نشود؛ consumer/version ثبت؛ async فقط برای جریان مصوب؛ unknown schema از مسیر عادی جدا شود. |
| Definition of Done | مرز مالک/consumer، قرارداد نسخه‌دار، oracleهای fault-injection و rollback/replay review شده؛ use case ضرورت دارد؛ acceptance به broker یا فناوری جدید وابسته نشده. |
| Integration Dependencies | `TASK:CORE:C01:005`, C03 data/Job contract، producer/consumerهای مشخص؛ اگر مسیر financial است، C12a مالک posting باقی می‌ماند. |
| PR/Delivery Boundary | contract, test fixture و تغییر Core در scope؛ بدون راه‌اندازی broker/engine جدید، انتشار production یا توسعهٔ مسیرهای فرضی. |
| Open Decisions | انتخاب engine/transport و هر SLA/retention عددی فقط در صورت نیاز مستند، با owner decision؛ از این Task استنتاج نمی‌شود. |
| Blockers | consumer/use case واقعی نامشخص مانع فعال‌سازی event می‌شود؛ قراردادهای محلی و fault matrix قابل تهیه‌اند. |
| Implementation Risks | outbox عمومی و بی‌دلیل؛ consumer به source of truth تبدیل شود؛ dedupe window فرضی؛ schema version bypass؛ مخلوط‌شدن رویداد مالی با telemetry. |
| Execution Readiness Verdict | **آماده برای طراحی مشروط و آزمون قراردادی پس از اثبات use case؛ اجرای event flow تا producer/consumer واقعی متوقف است.** بدون انتخاب معماری تازه قابل تحویل است. |

### Task پرریسک: `TASK:CORE:C01:009` — پیکربندی، اسرار و سیاست مالی

**انتخاب ریسک:** اختلاط secret، feature flag و policy مالی می‌تواند افشای credential یا فعال‌سازی ناخواستهٔ رفتار مالی ایجاد کند. عدد/سیاست جدید وارد نمی‌شود.

| بُعد | شبیه‌سازی مبتنی بر `REQ:CORE:017/018/045/046`, `AC:CORE:C01:017/018/045/046` |
|---|---|
| Preconditions | baseline موجود از `TASK:CORE:C01:001`؛ قرارداد versioning از `TASK:CORE:C01:008`؛ owner مشخص برای هر config و policy؛ تصمیم secret storage/rotation مطابق `DECISION:C01:09` باز بماند. |
| Required Inputs | نام/نوع/مصرف config موجود؛ طبقه‌بندی secret/runtime/flag/financial policy؛ consumer؛ validation rules؛ compatibility version؛ rollback state و audit. |
| Dependencies | `TASK:CORE:C01:001` hard؛ `TASK:CORE:C01:008` contract؛ C03 deploy/config ownership؛ policy owners در C04/C07/C08 حسب دامنه. |
| Relevant Architecture | config فقط مقدار typed runtime؛ secret جدا و محافظت‌شده؛ flag فقط control exposure؛ policy مالی از owner domain می‌آید؛ Core modular authority حفظ می‌شود. |
| Affected Components | `core/config.py`، settings/schema، deployment injection، CI secret checks، flag gate، policy reader، audit/rollback path. |
| Data/API Contracts | کلید/نوع/version/owner/environment؛ ممنوعیت secret در logs/errors; default برای required secret fail-closed؛ policy envelope با owner/version/effective status، نه مقدار فرضی. |
| Security Requirements | هیچ secret در git/artifact/log/API؛ حداقل دسترسی؛ scope محیطی؛ rotation/revocation طبق تصمیم owner؛ fail closed برای نبود/نوع غلط؛ audit تغییر بدون افشای value. |
| Implementation Work Sequence | ۱) config paths موجود را inventory؛ ۲) هر مورد را در چهار گروه طبقه‌بندی؛ ۳) owner و consumer را ثبت؛ ۴) typed validation و compatibility طرح؛ ۵) secret masking و CI checks؛ ۶) flag disable/rollback و dependency check؛ ۷) negative tests missing/malformed/incompatible؛ ۸) مشخصات مبهم را `DECISION:C01:09` handoff کن. |
| Deliverables | four-category config inventory؛ schema/type contract؛ secret handling map؛ flag dependency/rollback plan؛ tests و decision handoff. |
| Failure Scenarios | missing secret؛ wrong type؛ credential log leak؛ incompatible rollout؛ flag enabled before dependency; rollback to incompatible code/data; policy accidentally stored as runtime toggle. |
| Recovery Strategy | startup/operation fail-closed برای required config؛ rotate/revoke طبق owner؛ flag to safe disabled state؛ rollback فقط با compatible code/schema; audit record without secret. |
| Required Tests | `AC/TEST:C01:017/018/045/046`: required/malformed config، secret leak scan، authorized policy change، dependency-aware flag rollback؛ CI control آزمایش‌شده، محصول NOT_EXECUTED. |
| Acceptance Criteria | invalid/missing config blocks affected path; secrets absent from repository/output; flags cannot override financial policy; rollback checks dependent API/job/data versions. |
| Definition of Done | inventory 100% از مسیرهای موجود؛ owner/type/version assigned؛ masked error; negative/recovery cases; `DECISION:C01:09` باقی است و no storage method invented. |
| Integration Dependencies | C03 environment/config owner؛ C04/C07/C08 policy owner؛ C01 API compatibility; migration/feature dependencies documented. |
| PR/Delivery Boundary | config contract/code/tests in isolated env; no secret values, actual rotations, production flag activation or money movement. |
| Open Decisions | secret storage, rotation/revocation and environment isolation from `DECISION:C01:09`; no provider/tool specified. |
| Blockers | production wiring and rotation blocked by owner decision/access; inventory, schema, CI test design independent. |
| Implementation Risks | secret copied to config/artifact; emergency flag bypass; fallback uses stale credentials; rollback crosses schema contract; policy coupling. |
| Execution Readiness Verdict | **آماده برای inventory، typed validation و fail-closed tests؛ production secret wiring/rotation BLOCKED_BY_DECISION.** |

**نتیجهٔ QG-13 برای C01:** دو Task متفاوت شبیه‌سازی شدند؛ C01 به ۲ بستهٔ قبلی اضافه شد. این شبیه‌سازی‌ها گیت کل برنامه را PASS نمی‌کنند.

## C03 — قراردادها، داده و زیرساخت مشترک

### Task پیچیده: `TASK:CORE:C01:005` — الگوی Job پایدارِ تحت مالکیت سرویس

**انتخاب:** چند سرویس مصرف‌کننده با نوع کار و lifecycle متفاوت‌اند و برنامه عمداً یک workflow engine واحد تحمیل نمی‌کند. آزمون از C03 perspective است: پیاده‌سازی قرارداد مشترک توسط C03، در حالی‌که state Job نزد سرویس مالک می‌ماند.

| بُعد | مسیر شبیه‌سازی |
|---|---|
| Preconditions | مالک سرویس/داده طبق `TASK:CORE:C01:002` روشن؛ use case طولانی واقعاً شناسایی شده باشد؛ قرارداد `CONTRACT:C01:03` هنوز design-only و versioned. |
| Required Inputs | service/job owner، job type/version، requester/correlation، input ref، states، retry/recovery policy source، retention owner و consumer scope. |
| Dependencies | `TASK:CORE:C01:002` hard؛ `TASK:CORE:C01:005`; `CONTRACT-LINK:C03:03`→`CONTRACT:C01:03`; consumer `TEST:CORE:C03:002/003/010–015`. |
| Relevant Architecture | هر سرویس مالک state و Jobهایش است؛ C03 الگوی reusable/port را پیاده می‌کند؛ synchronous calls جدا؛ shared table/engine اجباری نیست. |
| Affected Components | Job contract/port، service-owned persistence adapter، worker lifecycle، status API، recovery/runbook و integration fixtures. |
| Data/API Contracts | job ID پایدار، owner/type/version/status/timestamps/correlation/input reference؛ بدون private table access؛ error/status معنایی ثابت؛ consumer مجاز. |
| Security Requirements | actor/service authorization و purpose؛ کمینه‌سازی payload؛ secrets/PII در queue/log نرود؛ status برای tenant/service نامربوط افشا نشود. |
| Implementation Work Sequence | ۱) sync را از long job تفکیک؛ ۲) مالک و حداقل state machine را تعیین؛ ۳) port و schema versioned design؛ ۴) state در adapter مالک؛ ۵) worker-crash/restart و migration fixtures؛ ۶) consumer compatibility؛ ۷) فقط برای use case تأییدشده اجرا. |
| Deliverables | port/adapter contract، state transition model، job status interface، worker crash/migration acceptance matrix و نمونه consumer. |
| Failure Scenarios | worker crash پیش/پس از side effect؛ job duplicate؛ migration هنگام job قدیمی؛ consumer نسخه ناسازگار؛ owner service unavailable؛ state گم‌شده. |
| Recovery Strategy | resume با همان job ID و idempotency contract؛ حفظ unknown state تا inquiry/reconciliation؛ migration سازگار old/new؛ عدم retry نامحدود و عدم کپی state به C03. |
| Required Tests | `TEST:CORE:C03:002/003/010–015` در سطح contract؛ owner isolation، crash/restart، migration compatibility و status transitions. همه برنامه‌ای/NOT_EXECUTED. |
| Acceptance Criteria | job state فقط یک owner دارد؛ duplicate اجرا اثر دوم ندارد؛ restart با همان ID قابل پیگیری است؛ مسیر sync بی‌دلیل به job تبدیل نمی‌شود؛ consumer نسخه‌دار و مجاز است. |
| Definition of Done | owner/use case، schema/version، failure recovery و integration oracle پذیرفته شده؛ shared port consumer tests دارد؛ انتخاب engine/queue لازم یا تحمیل نشده. |
| Integration Dependencies | C01 modular ownership/versioned contracts؛ سرویس‌های مالک Job؛ C11b/C14 برای عملیات دوره‌ای/وضعیت فقط از قرارداد owner. |
| PR/Delivery Boundary | contract/port/adapter و test fixtures در scope؛ نصب queue infrastructure یا production worker خارج از برنامهٔ این Task. |
| Open Decisions | فناوری queue/engine، SLA/retention و retry numbers تا تصمیم/اندازه‌گیری باز؛ این simulation آن‌ها را انتخاب نمی‌کند. |
| Blockers | فعال‌سازی concrete adapter بدون service/use case owner ممنوع؛ contract design و fixture قابل تحویل‌اند. |
| Implementation Risks | C03 تصاحب state؛ universal engine؛ retry side effect؛ jobهای کوتاه بی‌دلیل؛ migration که state نامعلوم را overwrite کند. |
| Execution Readiness Verdict | **آماده برای قرارداد و adapter محدود پس از تعیین use case؛ انتخاب فناوری و SLA باز می‌ماند.** |

### Task پرریسک: `TASK:CORE:C01:006` — Outbox و مصرف idempotent در C03

**انتخاب:** شکست بین commit محلی و انتشار event یا مصرف تکراری می‌تواند وضعیت دو سرویس را divergent کند. این شبیه‌سازی اجرای مالکیت C03 برای همان قرارداد C01 است؛ قرارداد C01 تغییر معنایی یا کپی نمی‌شود.

| بُعد | مسیر شبیه‌سازی |
|---|---|
| Preconditions | event producer/consumer و transaction owner مشخص؛ `CONTRACT:C01:04` و ownership `TASK:CORE:C01:002` معتبر؛ async use case اثبات شده باشد. |
| Required Inputs | owner transaction، event ID، schema/version، correlation، consumer registry، idempotency record، fault points و rollback/replay rules. |
| Dependencies | C01 `TASK:CORE:C01:006` contract; C03 data/job boundary; producer/consumer package owners؛ C12a هر اثر دفترکل را مستقل مالک است. |
| Relevant Architecture | outbox محلی در data owner؛ C03 مسئول قرارداد/اجرا فقط در حیطه پذیرفته‌شده؛ consumer state نزد consumer؛ no mandatory broker. |
| Affected Components | transaction adapter، outbox publisher, consumer dedupe/inbox, schema compatibility gate, retry/replay observability. |
| Data/API Contracts | event ID/version/correlation/owner/purpose؛ payload حداقلی؛ unknown schema explicit; consumer acknowledgment semantics؛ no implicit ledger authority. |
| Security Requirements | service identity+least purpose؛ enforce tenant boundaries؛ redact sensitive values؛ authorization مستقل از event arrival. |
| Implementation Work Sequence | ۱) prove event need؛ ۲) map commit/publish/ack boundaries؛ ۳) define idempotency key/version; ۴) inject crash at each boundary؛ ۵) replay/reorder fixtures؛ ۶) verify consumer state and audit; ۷) gate deployment on owner compatibility. |
| Deliverables | event contract/compatibility matrix، transaction failure matrix، consumer idempotency checks، replay runbook. |
| Failure Scenarios | event lost after commit; published before transaction commit; ack lost; duplicate/reorder; unknown version; subscriber partial failure. |
| Recovery Strategy | redeliver same event ID; consumer dedupe atomic with side effect; quarantine incompatible event; preserve source record and reconcile; never fabricate success from ack alone. |
| Required Tests | `TEST:CORE:C03:004/016/017` plus C01 `TEST:CORE:C01:012/043/044`; atomic local write, duplicate, replay, ordering and schema negative cases. `NOT_EXECUTED`. |
| Acceptance Criteria | source state/event consistency; duplicate causes no duplicate business effect; unknown schema observable and contained; every consumer contract owner/versioned; no event grants permission. |
| Definition of Done | positive, negative, boundary, failure/recovery fixtures reviewed; end-to-end producer/consumer ownership clear; no broker assumption. |
| Integration Dependencies | source module transaction owner, consumer owner, C01 contract compatibility, C12a financial state owner where relevant. |
| PR/Delivery Boundary | contract implementation/fixture only; no production event publication, schema migration on shared data, real money or broker rollout. |
| Open Decisions | transport/broker, delivery SLO, retention and per-event retry caps remain decisions only if required by accepted use case. |
| Blockers | unresolved producer/consumer ownership blocks activation, not design; no test can assume event exists without source use case. |
| Implementation Risks | duplicate side effect; schema drift; unauthorized replay; source-of-truth split; accidental conversion of every request to async. |
| Execution Readiness Verdict | **Contract/fault design ready when concrete producer/consumer pair is named; unresolved pair blocks execution.** |

**نتیجهٔ QG-13 برای C03:** دو مسیر از قراردادهای مشترک واقعی شبیه‌سازی شدند؛ C03 مالک State Job/دادهٔ سرویس‌های مصرف‌کننده نشده است.

## C05a — کاتالوگ خدمات شهاب

### Task پیچیده: `TASK:CORE:C05A:001` — مدل Domain/Service/Capability

**مبنای انتخاب:** روابط مستقل Domain/Service/Capability، شناسه پایدار، purpose، schema ورودی/خروجی، capability dependencies، executor و contract version در یک مدل باید سازگار شوند؛ Task ۴۰۰؟ خیر، دامنه فقط ۱۹۱–۲۰۰ و ۲۰۳–۲۰۴ است.

| بُعد | شبیه‌سازی بر مبنای برنامه |
|---|---|
| Preconditions | مالکیت داده C01:01؛ domain/catalog owner مشخص؛ هیچ schema عملیاتی منتشرشده فرض نشود. |
| Required Inputs | Domain/Service/Capability IDs، purpose/owner، input/output schema، capability refs، executor ref، contract version و وضعیت publication. |
| Dependencies | C01 data ownership؛ C02 permission؛ C04 entitlement فقط ارجاع؛ C06/R02 ورودی و UI؛ A02 اجرای پایدار workflow. |
| Relevant Architecture | C05a معنای Catalog و route قرارداد را مالک است؛ C02 اختیار؛ C06 UI؛ A02 workflow. Catalog خود سرویس اجرایی نیست. |
| Affected Components | رکوردهای مجزا، stable IDs، referential constraints، schema/version compatibility، API projection. |
| Data/API Contracts | ID مستقل از عنوان؛ relation valid؛ owner/purpose/schema/version صریح؛ API read-only نسخه‌دار; no private table reads. |
| Security Requirements | مالکیت/دسترسی داده به‌صورت metadata مصرف می‌شود اما مجوز صادر نمی‌شود؛ tenant/domain scope و least purpose. |
| Implementation Work Sequence | ۱) invariants را استخراج؛ ۲) انواع رکورد و رابطه را جدا؛ ۳) ID و constraints را تثبیت؛ ۴) schema/version را ثبت؛ ۵) orphan/duplicate/unknown relation را مدل؛ ۶) API projection را با C01/C02 هماهنگ؛ ۷) migration/rollback را طرح کن. |
| Deliverables | domain model، constraints/invariants، API projection، compatibility matrix و migration/rollback plan. |
| Failure Scenarios | duplicate ID؛ Service بدون Domain؛ orphan capability؛ executor نامعلوم؛ schema mismatch؛ title change موجب ID change؛ dependency cycle. |
| Recovery Strategy | write نامعتبر fail؛ رکورد orphan quarantine؛ ID پایدار حفظ؛ schema ناسازگار فقط نسخه جدید/مهاجرت کنترل‌شده؛ هیچ capability فعال نشود. |
| Required Tests | AC/TEST:C05A:001–008: انواع جدا، duplicate، stable ID، missing target، orphan relation و schema/version cases؛ program tests NOT_EXECUTED. |
| Acceptance Criteria | type constraints enforce؛ عنوان ID را عوض نکند؛ نامشخص با مقدار فرضی پر نشود؛ قابلیت به‌تنهایی release/permission ندهد. |
| Definition of Done | هر فیلد owner و Requirement/AC/Test دارد؛ constraints و compatibility review شده؛ migration rollback plan پذیرفته. |
| Integration Dependencies | C01 model/contract; C02 permission; C04 tariff reference; C06 UI projection; R02/A02 consume contract. |
| PR/Delivery Boundary | طرح مدل و contract/fixtures؛ بدون entitlement جدید، tariff value یا endpoint واقعی منتشرشده. |
| Open Decisions | physical schema، endpoint و انتشار اجرایی بعداً در اختیار owner؛ هیچ technology انتخاب نشده. |
| Blockers | انتشار API تا schema/version/policy acceptance؛ طراحی مفهومی و contract tests مانع ندارد. |
| Implementation Risks | catalog رکورد را active/authorized فرض کند؛ duplicate authority در C02/C04؛ breaking schema برای consumerها. |
| Execution Readiness Verdict | **آمادهٔ تبدیل به migration/contract design پس از بازبینی owner؛ انتشار و مجوز عملیاتی در این Task نیست.** |

### Task پرریسک: `TASK:CORE:C05A:004` — مسیریاب تجربه و نتیجه ارزیابی

**مبنای انتخاب:** خطای route می‌تواند کاربر را به دامنه/نقش/خدمت ممنوع ببرد؛ LLM فقط پیشنهاددهنده است و تغییر حوزه نیازمند اقدام کاربر است.

| بُعد | شبیه‌سازی بر مبنای برنامه |
|---|---|
| Preconditions | Domain ID/role از C02؛ ورودی و نمایش C06/R02؛ سیاست B02/B03؛ backend permission check مستقل. |
| Required Inputs | user request, confirmed domain, actor/role/consent, catalog status, purpose/scope, ambiguity and permission result. |
| Dependencies | C02 authority؛ C05a catalog/routing policy؛ C06 user interaction؛ R02 retrieval boundary؛ A01/A02 only by contract when handoff is user-confirmed. |
| Relevant Architecture | route classifier proposes; backend validates; user explicitly confirms transition; no assistant/adviser domain conflation. |
| Affected Components | route result contract، confidence/ambiguity state، backend policy check، UI confirmation event، handoff and safe stop. |
| Data/API Contracts | target domain/service ID, proposal vs confirmed status, owner/version, reason code, permission reference; no hidden role change. |
| Security Requirements | deny-by-default for unauthorized domain/action; catalog active/plan membership isn't authorization; private inputs not leaked cross-domain. |
| Implementation Work Sequence | ۱) route states define; ۲) explicit user-confirmation transition; ۳) authorization at backend; ۴) ambiguous/out-of-domain outputs; ۵) revoked permission race; ۶) handoff only after confirmation; ۷) audit route decision without raw sensitive text. |
| Deliverables | route result schema, policy matrix, confirmation workflow, error/deny contract, tests for ambiguity and cross-domain. |
| Failure Scenarios | false positive domain; prompt injection; stale permission; inactive/unpublished service; user rejects suggestion; C06 confirmation event lost. |
| Recovery Strategy | remain in current context or safe-stop; ask clarifying question; recheck permission; do not silently transfer or execute; failed handoff retains correlation. |
| Required Tests | AC/TEST:C05A:020–021, 016 and 018: public input no domain action; rejection stays; permission revocation denies; route failure not success. NOT_EXECUTED. |
| Acceptance Criteria | no response/action from unconfirmed domain; LLM cannot change role; backend denies without permission; explicit route/result visible; retry is idempotent. |
| Definition of Done | route states and permission oracle mapped; UI and backend agreement; failure/negative/boundary fixtures and handoff owner reviewed. |
| Integration Dependencies | C02 role/scope; C06 confirmation UI; R02 evidence handling; A02 only after explicit accepted handoff; C14 status notification consumer. |
| PR/Delivery Boundary | routing contract and isolated tests; no live sensitive retrieval, financial operation, or permission policy duplication. |
| Open Decisions | threshold/route confidence values and exact API remain with owners; no numeric value invented. |
| Blockers | production routing activation until exact schema and policy-owner review; contract design is available. |
| Implementation Risks | silent domain switch; model output treated as permission; stale/unauthorized catalog; handoff creates second workflow. |
| Execution Readiness Verdict | **Fail-closed design and tests ready; thresholds/API rollout gated by owners; no architectural redesign required.** |

**نتیجهٔ QG-13 برای C05a:** دو Task با رفتارهای کاتالوگ و مسیریابی و AC/Testهای همان بسته شبیه‌سازی شدند.

## C05b — کاتالوگ محصولات مالی و توصیه‌گر

### Task پیچیده: `TASK:CORE:C05B:002` — کشف، استخراج و تشخیص تغییر

**انتخاب:** مسیر از محرک/منبع تا extraction، entity matching، lineage و change report با حفظ نسخه و سابقه چندمرحله‌ای است؛ schema نامشخص به تصمیم باز می‌رود.

| بُعد | شبیه‌سازی بر اساس Task و Requirementهای C05b |
|---|---|
| Preconditions | مدل/registry `TASK:CORE:C05B:001` و `CONTRACT:C01:01` حاضر؛ هر منبع مجاز و شرایط دسترسی‌اش ثبت؛ Job contract فقط اگر long-running flow اثبات شد. |
| Required Inputs | source/product IDs، permission/license status، raw artifact ref/hash، extraction schema, field provenance, timestamp/version، prior snapshot و matcher evidence. |
| Dependencies | C01 data owner/schema; C05a stable service refs; R03 canonical legal doc is downstream handoff; C03 job only if proven; C05b owns product data. |
| Relevant Architecture | Core Catalog product lineage; source-specific adapters; retrieval/legal source graph belongs R03, not duplicated; approved catalog is not answer authority. |
| Affected Components | source trigger/scheduler adapter، extractor/parser، entity matching، change detector، lineage/version registry، review queue. |
| Data/API Contracts | every field traces to source/ref/version/time; raw artifact never silently overwritten; uncertain match remains candidate; changes linked to prior record. |
| Security Requirements | ingest only permitted sources and permitted purpose; protect credentials; limit raw data; audit reads and transformations. |
| Implementation Work Sequence | ۱) verify source access; ۲) classify trigger demand/scheduled/change; ۳) parse structured fields with provenance; ۴) match to stable entity; ۵) compare versioned prior; ۶) separate new/change/uncertain; ۷) route uncertain cases for review; ۸) publish nothing automatically before validation gate. |
| Deliverables | source/trigger matrix، extraction schema، provenance contract، entity matching/change report، uncertain-review queue and fixtures. |
| Failure Scenarios | source unavailable/robots/license refusal; malformed table; duplicate product; ambiguous entity; stale data; source changes schema; extraction drops a field. |
| Recovery Strategy | keep last valid snapshot; retain raw hash/ref; mark partial/unavailable; replay same versioned artifact; never overwrite canonical record from uncertain match. |
| Required Tests | `AC/TEST:CORE:C05B` around source provenance, field extraction, matching/change history, access denial and partial source failure; designs remain NOT_EXECUTED. |
| Acceptance Criteria | every extracted field has provenance; ambiguous match is not merged; source/license denial prevents fetch; prior version remains reproducible; unsupported value is not inferred. |
| Definition of Done | source permissions, adapter contract, field-level lineage, unknown behavior and recoverable change history reviewed; no open field gets guessed. |
| Integration Dependencies | C01 ownership and catalog API; C05a service IDs; downstream R03/R05/R06 only through Handoff; C03 job pattern if warranted. |
| PR/Delivery Boundary | design, adapter contract and synthetic fixtures; no real source crawling outside approved access, provider credentials, canonical law publication or loan recommendation change. |
| Open Decisions | physical schema, source schedule, extraction technology and matching threshold remain owner decisions when required. |
| Blockers | source authorization/license blocks live ingestion; sample fixtures can validate schema behavior. |
| Implementation Risks | legal and product catalogs mixed; unlicensed fetch; silent entity merge; derived value masquerades as source fact; stale snapshot overwritten. |
| Execution Readiness Verdict | **Model and extraction design executable after permitted source inventory; live ingestion gated by source access/technology decisions.** |

### Task پرریسک: `TASK:CORE:C05B:003` — اعتبارسنجی و انتشار Snapshot محصول

**انتخاب:** توصیه‌گر فقط باید بر Snapshot معتبر و سازگار با دادهٔ منتشرشده کار کند؛ انتشار ناقص/متعارض می‌تواند نتیجهٔ وام گمراه‌کننده تولید کند.

| بُعد | شبیه‌سازی بر اساس C05B-R و `AC/TEST:CORE:C05B:007–009` |
|---|---|
| Preconditions | محصول/منبع versioned از Task 001–002؛ سیاست انتشار C01/C03؛ golden snapshot معتبر قبل از candidate. آستانه/تازگی/تعارض باز باقی بماند. |
| Required Inputs | candidate snapshot ID/hash، field completeness, source validity/freshness evidence, conflicts, prior published version, consumer compatibility. |
| Dependencies | C01 `REQ:CORE:009` snapshot authority; C05b Tasks 001/002; C05b 004 read contract; C01 deterministic recommender 004 consumer. |
| Relevant Architecture | immutable/pinned published snapshot; staging candidate separate; atomic switch to validated snapshot; previous valid stays available. |
| Affected Components | validator، freshness/conflict status، review queue، snapshot version registry، publish gate and recommender input pointer. |
| Data/API Contracts | source/version/hash and validation status; publication event references exact snapshot; one request cannot mix fields from two snapshot versions. |
| Security Requirements | only authorized owner may approve publication; audit actor/version; no production change without release gate; data quality does not grant permission to use product. |
| Implementation Work Sequence | ۱) load candidate to staging; ۲) validate required fields/source lineage; ۳) classify stale/uncertain/conflict without invented thresholds; ۴) route decision-required cases to review; ۵) build atomic snapshot; ۶) consumer reads pinned version; ۷) rollback by restoring previous valid pointer. |
| Deliverables | validation status model, gate checklist, atomic snapshot/rollback plan, conflict fixtures and consumer contract tests. |
| Failure Scenarios | missing required field; inconsistent source; stale provider data; partial publication; pointer update failure; concurrent candidate; recommender reads mixed versions. |
| Recovery Strategy | do not publish invalid candidate; preserve old snapshot; restore pointer; report stale/unavailable explicitly; reconcile candidate without altering past result. |
| Required Tests | `AC/TEST:CORE:C05B:007–009`: freshness states, conflict hold, prior snapshot retention, atomic publication/no mix; NOT_EXECUTED. |
| Acceptance Criteria | only a validated exact snapshot is selectable; incomplete/uncertain candidate blocked; rollback returns old complete version; trace links recommendation to snapshot and rule version. |
| Definition of Done | independent validation oracle, source lineage, publication authorization, failure rollback and consumer consistency have evidence; owner decision thresholds remain open. |
| Integration Dependencies | C01 deterministic recommender; C05b Task 004 API; C05a stable service refs; C03 publication/event contract where used. |
| PR/Delivery Boundary | staged fixtures and versioned publication spec; no live loan recommendation, data migration, production pointer switch or customer decision. |
| Open Decisions | numeric freshness/conflict thresholds and provider source policy remain open; simulation does not pick them. |
| Blockers | numeric policy and source acceptance block production publication, but gate design and tests are deliverable. |
| Implementation Risks | broad threshold guesses; stale snapshot treated current; rollback loses lineage; mixed version response; weak conflict review. |
| Execution Readiness Verdict | **Fail-closed publication design executable; live publish and scoring are BLOCKED_BY_DECISION until source/threshold gates are approved.** |

**نتیجهٔ QG-13 برای C05b:** extraction/change و snapshot publication دو Task واقعی و مستقل شبیه‌سازی شدند؛ کاتالوگ قانونی R03 با محصول بانکی یکی نشده است.

## C06 — پوسته سوپراپ و UI مشترک

### Task پیچیده: `TASK:CORE:C06:003` — slotها و status از مالک

| بُعد | شبیه‌سازی و معیار برنامه‌ای |
|---|---|
| Preconditions | C05a catalog/API و C02 permission contracts معلوم؛ C06 فقط presentation shell است؛ status مالک از API versioned خوانده شود. |
| Required Inputs | allowed slot schema، component/service ID، owner API version/status/error, user role/domain, loading/unknown states. |
| Dependencies | C05a catalog; C02 role/permission; C14 status/history; C13b receipts; no direct query into owner tables. |
| Relevant Architecture | UI consumes contracts; backend/service remains authority; Assistant remains off unless separate gate. |
| Affected Components | slot renderer, API adapter, status mapper, schema validation and generic error/unknown UI. |
| Data/API Contracts | allowlisted slot fields, versioned owner response, explicit pending/unknown/error; unsupported payload rejected. |
| Security Requirements | no privileged field from UI payload; authorization server-side; no secret/transcript in logs. |
| Implementation Work Sequence | inventory current slots; bind each to owner/schema; validate payload; map states without inventing success; handle unknown; verify user scope; add owner-link evidence. |
| Deliverables | slot schema, status/error mapping, contract fixture set and screen state matrix. |
| Failure Scenarios | unknown slot, stale status, owner timeout, incompatible schema, permission revocation, partial payload. |
| Recovery Strategy | safe fallback; fetch owner state again only within bounded policy; keep unresolved visible; do not synthesize active/paid state. |
| Required Tests | `AC/TEST:CORE:C06:009–012` (allowed schema, invalid payload rejected, status from API) and relevant boundary cases; NOT_EXECUTED. |
| Acceptance Criteria | only allowlisted slots render; invalid version fails visibly; status equals owner response; stale/unknown cannot authorize action. |
| Definition of Done | owners/schema/errors and UI oracle reviewed; positive/negative/boundary cases cover 4 state classes; visual shell does not own business state. |
| Integration Dependencies | C05a catalog, C02 role/scope, C13b receipt, C14 message/history; source service for status. |
| PR/Delivery Boundary | shell contract/UI tests only; no new endpoint or backend permissions. |
| Open Decisions | precise component schema and version remain design inputs from owners. |
| Blockers | consumer integration blocked until owner API version published; shell contract work can proceed with fixtures. |
| Implementation Risks | UI maps unknown to success; direct data access; stale state; hidden action exposure. |
| Execution Readiness Verdict | **Ready for contract-driven shell implementation after exact owner schemas are provided; no redesign of business ownership needed.** |

### Task پرریسک: `TASK:CORE:C06:004` — پرونده و ورودی امن

| بُعد | شبیه‌سازی و معیار برنامه‌ای |
|---|---|
| Preconditions | secure input purpose and backend owner defined; Assistant computer-use remains separately gated; C02 privacy/session contract. |
| Required Inputs | synthetic user/session, field classification, consent/purpose, form state, error traces, log/transcript sinks. |
| Dependencies | C02 session/authorization/privacy; C14 history/notification; C06 secure input; no credential persistence. |
| Relevant Architecture | secure input is isolated from display/transcript/log; backend validates; page shell cannot grant authority. |
| Affected Components | case form, secure-entry component, submit boundary, error renderer and telemetry redaction. |
| Data/API Contracts | allowlisted fields, purpose and correlation; no OTP/password in state dumps; status response from domain owner. |
| Security Requirements | secrets absent from logs/transcript; scope and consent checked; autocomplete/clipboard restrictions follow approved policy; backend authorization. |
| Implementation Work Sequence | classify inputs; define redaction boundary; wire synthetic secure-input component; inject validation/failure; inspect rendered/logged artifacts; exercise revoke/timeout; verify user sees non-sensitive status. |
| Deliverables | field data-classification table, secure input interface, redaction tests and failure UX. |
| Failure Scenarios | accidental secret logging; session mismatch; stale auth; partial submit; timeout with unknown result; UI replay. |
| Recovery Strategy | clear sensitive ephemeral input; keep action outcome unknown until owner inquiry; safe-stop; do not resubmit automatically. |
| Required Tests | `AC/TEST:CORE:C06:013–014` plus 004 secure-input cases: record persists, secrets in transcript/log =0, invalid session blocked; NOT_EXECUTED. |
| Acceptance Criteria | no secret in client logs/transcript; invalid permission denies; unknown does not imply success; case context stays scoped. |
| Definition of Done | data flow and log sinks reviewed; redaction oracle; failure/retry manual and explicit; owner API state traced. |
| Integration Dependencies | C02 auth/session; C14 observability; domain owner status; C13b only for receipt UI. |
| PR/Delivery Boundary | UI and synthetic contract tests; no real credentials, OTP, or production transaction. |
| Open Decisions | approved field-specific clipboard/autofill behavior and exact form schema remain owner/product decisions. |
| Blockers | sensitive live form cannot activate until owner/privacy contract accepted. |
| Implementation Risks | secret replay through logging; unknown result duplicate submission; form state crossing users. |
| Execution Readiness Verdict | **Fail-closed design and synthetic verification executable; live sensitive entry awaits field-policy approval.** |

## C07 — مالکیت وجوه و مدل اعتبار

### Task پیچیده: `TASK:CORE:C07:003` — منشأ، حقوق و مهلت اعتبار

| بُعد | شبیه‌سازی بر اساس C07-R010–014 و AC/TEST:CORE:C07:010–014 |
|---|---|
| Preconditions | انواع منبع اعتبار مصوب W؛ C02 actor/tenant; C08/C09/C10/C11a/C12a ownership boundary; amounts/version synthetic. |
| Required Inputs | component ID, source/owner, legal/economic rights, expiry, transferability/cashability, service scope, obligation references. |
| Dependencies | C02 authorization; C08 gift/top-up; C09 consumption/reservation; C10 transfer; C11a return; C12a ledger. |
| Relevant Architecture | C07 owns credit rights/provenance model; ledger C12a records entries, not redefines rights; downstream packages consume typed components. |
| Affected Components | credit component registry, provenance chain, rights matrix, expiry state and package contracts. |
| Data/API Contracts | stable component ID, source, owner, rights/version/expiry and source transaction ref; no implicit right changes on transfer. |
| Security Requirements | tenant-scoped reads; only authorized operations; noncashable gift stays noncashable; audit rights changes. |
| Implementation Work Sequence | enumerate source types; map rights by source; encode expiry/owner; define transfer transformation; map downstream readers; test stale/expired/ineligible; reconcile to C12a. |
| Deliverables | source-to-rights matrix, component contract, expiry transition model, consumer mapping and fixture set. |
| Failure Scenarios | missing lineage; owner mismatch; expiry boundary race; gift marked cashable; duplicate component; downstream unsupported type. |
| Recovery Strategy | reject or quarantine component; preserve original provenance; no rights expansion; repair only with authoritative source event; downstream safe-stop. |
| Required Tests | `AC/TEST:CORE:C07:010–014`: source/owner, rights, expiry, transfer no right creation, expired state; NOT_EXECUTED. |
| Acceptance Criteria | each component has source/owner/rights; expiry stable; transfer cannot cash out restricted gift; downstream cannot mutate source rights. |
| Definition of Done | rights matrix versioned; all source types map to AC/Test; unmapped type blocked; ledger authority separate. |
| Integration Dependencies | C08/09/10/11a for operations; C12a for accounting record; C02 for actor permission. |
| PR/Delivery Boundary | domain model/contracts and synthetic tests; no real balances or ledger migration. |
| Open Decisions | open legal edge cases remain with source/owner; no withdrawal or tax policy invented. |
| Blockers | unapproved source/right blocks that source class only; other approved types testable. |
| Implementation Risks | rights escalation; expiry loss; cross-package duplicate authority; hidden cashability inference. |
| Execution Readiness Verdict | **Ready for typed model/contracts using approved rights; unresolved source classes must remain blocked.** |

### Task پرریسک: `TASK:CORE:C07:004` — state، ترتیب مصرف و دقت پول

| بُعد | شبیه‌سازی بر اساس C07-R015–019 و AC/TEST:CORE:C07:015–019 |
|---|---|
| Preconditions | source components and rights from TASK 003; W rounding/customer-favor and allocation rules; C09 reserve/capture boundary; C12a ledger contract. |
| Required Inputs | balance components, sequence/expiry, amount in IRR, allocation rule, pending/reserved/captured states, idempotency and concurrency fixture. |
| Dependencies | C09 reservation/consumption; C12a double-entry and atomicity; C08/C10/C11a operations; C02 permissions. |
| Relevant Architecture | C07 computes ownership/available rights; C09 consumes/reserves; C12a persists financial entries; no shared mutable balance authority. |
| Affected Components | available-credit calculation, ordering/expiry allocator, precision/rounding, pending states and concurrency gate. |
| Data/API Contracts | integer IRR or approved representation; exact source components and allocation result; reservation ID/correlation; no float rounding. |
| Security Requirements | actor authorized; amount and source scoped; race cannot overspend; errors reveal no other tenant balance. |
| Implementation Work Sequence | define permitted state transitions; apply approved ordering; calculate exact integer amounts; reserve atomically via C09; ledger write C12a; inject duplicate/concurrent requests; reconcile. |
| Deliverables | state machine, rounding oracle, allocation matrix, concurrency/idempotency tests and C09/C12a contract traces. |
| Failure Scenarios | concurrent double spend; rounding penny drift; expired source used; pending treated as captured; retry duplicates; ledger mismatch. |
| Recovery Strategy | reject/hold conflicting reservation; same idempotency key; reconcile to C12a; preserve pending/unknown state; never silently rebalance to customer disadvantage. |
| Required Tests | `AC/TEST:CORE:C07:015–019`: state distinction, allocation/expiry, exact IRR rounding, cap, retry and ledger invariants; NOT_EXECUTED. |
| Acceptance Criteria | no overspend; sum allocated equals operation amount under approved rule; rounding favors customer per decision; pending != captured; no duplicate entry. |
| Definition of Done | arithmetic oracle and race fixtures; state/owner contract; errors/recovery; source provenance preserved across debit/credit. |
| Integration Dependencies | C09 reserve/release; C12a posting; C08 source balances; C02 authorization; C10/C11a consume only through their interfaces. |
| PR/Delivery Boundary | tests/contracts with synthetic ledger; no payment or real balance movement. |
| Open Decisions | any unapproved operation limits remain open; approved rounding is fixed, no new cap introduced. |
| Blockers | live money execution requires release gates and authorized environment; domain model/test design ready. |
| Implementation Risks | floating point; race; partial cross-service update; premature capture; source components collapsed. |
| Execution Readiness Verdict | **Critical behavior can be specified and fixture-tested; product activation remains gated by C09/C12a contracts and financial release approvals.** |

**نتیجهٔ QG-13 برای C06 و C07:** هر بسته یک Task پیچیده و یک پرریسک از محدوده و AC/Testهای خودش دارد؛ آزمون محصول اجرا نشده.

## C08 — شارژ، هدیه و تخفیف

### Task پیچیده: `TASK:CORE:C08:004` — کمپین هدیه/تخفیف

| بُعد | شبیه‌سازی بر مبنای C08 و AC/TEST C08:010–014 |
|---|---|
| Preconditions | حقوق component از C07؛ قیمت‌گذاری/تعرفه از C13a؛ کمپین فقط با اختیار مالک و budget fixture؛ سقف/مخاطب مصوب در دسترس. |
| Required Inputs | campaign ID/version, audience, service, eligibility, start/end, activation/expiry, budget/count cap, gift vs discount type. |
| Dependencies | C07 rights/expiry; C13a price; C09 final consumption amount; C12a atomic usage/budget; C02 actor and org scope. |
| Relevant Architecture | C08 campaign evaluation; C07 component ownership; discount changes price, gift creates credit; no direct ledger authority. |
| Affected Components | campaign rules, audience matcher, concurrent budget/use counter, entitlement/effective price interface. |
| Data/API Contracts | campaign state/version and eligibility proof; computed discount/gift separated; source and expiry refs; idempotency by operation/campaign. |
| Security Requirements | authorized campaign editor; tenant/customer scope; no overexposure of audience data; no self-grant or privilege from code alone. |
| Implementation Work Sequence | define gift/discount semantics; validate targeting and period; compute discounted price before credit use; reserve budget/counter atomically; record eligible result; send typed effect to C07/C09; reconcile failures. |
| Deliverables | campaign state model, eligibility/policy contract, concurrency/budget fixture, price/credit separation and integration matrix. |
| Failure Scenarios | simultaneous last-use requests; expired code; wrong service; budget exhausted; duplicate redeem; price change mid-order; partial gift credit. |
| Recovery Strategy | same operation idempotent; release unused reservation only on definitive failure; preserve unknown status; no duplicate credit/discount; manual review if budget state conflicts. |
| Required Tests | `AC/TEST:CORE:C08:010–014`: gift vs discount, configurable scope, concurrent budget, caps/activation expiry, transfer does not reset term; NOT_EXECUTED. |
| Acceptance Criteria | discount lowers payable price without credit posting; gift posts only once; campaign budget never exceeded; eligibility and dates are versioned; unknown cannot consume twice. |
| Definition of Done | rule oracle, owner, constraints and consumer contracts reviewed; concurrency/failure cases; open numeric limits remain open if not decided. |
| Integration Dependencies | C07 credit rights; C09 consumption; C13a rates; C12a persistence; C02 authority. |
| PR/Delivery Boundary | synthetic campaign and contract tests; no real credit issuance/customer messaging or production campaign. |
| Open Decisions | management UI technical owner and unspecified campaign values remain decisions/handoff; not filled by simulation. |
| Blockers | live issuance until configuration owner, values and accounting flow accepted; model design is executable. |
| Implementation Risks | treating discount as credit; budget race; activation term resets on transfer; campaign grants permission. |
| Execution Readiness Verdict | **Ready for typed campaign/effect contracts; live campaign activation is blocked until open owners/values resolve.** |

### Task پرریسک: `TASK:CORE:C08:002` — وصول، وضعیت و یکتایی شارژ

| بُعد | شبیه‌سازی بر مبنای C08:004–006 و AC/TESTهای متناظر |
|---|---|
| Preconditions | destination/request ID and payer authorized; provider outcome is not assumed; C12b inquiry/reconciliation and C12a posting contracts retained. |
| Required Inputs | stable request/operation ID, payer/wallet, provider reference/status, callback/replay history, settlement proof and time. |
| Dependencies | C02 payer/authority; C07 wallet rights; C12b provider unknown/inquiry; C12a durable credit; C03 idempotency; C14 status display. |
| Relevant Architecture | C08 owns recharge flow status; C12b owns bank outcome; C12a owns ledger; C07 defines credit meaning. |
| Affected Components | provider status adapter, event handler, recharge state machine, dedupe key, ledger handoff and customer-visible history. |
| Data/API Contracts | one request ID across callback/inquiry/retry; only verified receipt can credit; unknown distinct from failed; callback version/correlation. |
| Security Requirements | verify callback authenticity per provider contract; no client supplied receipt accepted as settlement; least privilege; audit without secrets. |
| Implementation Work Sequence | create destination-bound request; receive provider event; validate evidence; query C12b when unknown; post once via C12a; update status; reconcile duplicate/out-of-order events. |
| Deliverables | state transition table, provider contract mapping, idempotency fixture, settlement oracle, reconciliation handoff. |
| Failure Scenarios | delayed callback; forged/replayed callback; payment success but response timeout; duplicate inquiry; wrong wallet destination; posting fails after settlement. |
| Recovery Strategy | unresolved remains pending/unknown; inquiry before retry; retry same operation; keep receipt evidence; no second credit; C12a reconcile partial post. |
| Required Tests | `AC/TEST:CORE:C08:004/005/006`: valid credit only, unknown not failure, duplicate no second credit and stable reference; NOT_EXECUTED. |
| Acceptance Criteria | one valid settlement yields at most one credit; no valid settlement yields none; unknown not auto-failed; destination never inferred from payer alone. |
| Definition of Done | provider-state mapping and C12a/C12b handoffs reviewed; duplicate/replay/failure tests have explicit oracle; live provider remains gated. |
| Integration Dependencies | C12b outcome/inquiry, C12a posting, C03 idempotency, C07 component rights, C14 history. |
| PR/Delivery Boundary | synthetic provider fixtures only; no payment, credential or real balance movement. |
| Open Decisions | provider-specific signature schema, retry timings and unknown resolution SLA remain under provider/owner decisions. |
| Blockers | provider activation and thresholds; state model and mock contract are independently deliverable. |
| Implementation Risks | forged settlement; double credit; unknown converted to failed and retried; wrong destination; non-atomic state/posting. |
| Execution Readiness Verdict | **Fail-closed/idempotent contract is implementable with synthetic fixtures; live integration BLOCKED_BY_PROVIDER_DECISION.** |

## C09 — مصرف و رزرو

### Task پیچیده: `TASK:CORE:C09:002` — برآورد، رضایت و چرخهٔ reserve

| بُعد | شبیه‌سازی بر مبنای C09:002 و AC/TEST متناظر |
|---|---|
| Preconditions | payer and eligible component from C02/C07; quote/rate owner C13a; cap and approved W reserve/expiry rules known; C12a transaction contract available. |
| Required Inputs | operation ID, payer, estimate/rate version, eligible components, amount cap, consent, expiry, current pending/reserved/captured status. |
| Dependencies | C07 rights/allocation; C13a quote; C12a durable reservation; C02 actor; C05a service eligibility; C11b/C14 only as appropriate. |
| Relevant Architecture | C09 owns reserve/consume state; C12a posts durable ledger; C07 owns rights; price/entitlement don't grant access. |
| Affected Components | quote confirmation, reserve engine, expiry worker, cap evaluator, customer status and release/capture interface. |
| Data/API Contracts | reservation ID, operation ID, rate version, component allocation, expiry and cap; state transitions explicit and idempotent. |
| Security Requirements | verify payer and permission immediately before reserve; prevent cross-tenant component use; consent tied to quote/version; no amount from UI trusted. |
| Implementation Work Sequence | quote from owner; present terms; record consent; validate eligibility/cap; reserve components atomically; process actual usage; handle approved increase ceiling only; expire/release on definitive outcome. |
| Deliverables | state machine, reservation allocation contract, cap/expiry fixture, quote/consent record and failure/recovery matrix. |
| Failure Scenarios | insufficient balance; concurrent reserve; quote expires; user consents to old version; worker crash; unknown external outcome; partial capture. |
| Recovery Strategy | reservation durable by ID; inquiry/reconcile unknown before release; release only definitive unused amount; preserve hold as mandated; never silently change quote. |
| Required Tests | AC/TEST:C09:002 and related 003/007/008: consent, reserve amount, expiry, bounded increase, unknown exposure; NOT_EXECUTED. |
| Acceptance Criteria | no reserve without consent and authority; cap enforced; reserved distinct from captured; retry same reservation; amount/version traceable. |
| Definition of Done | quote/version, permission check and atomic reserve/release tested as planned; open limits remain explicit; integration owners agree. |
| Integration Dependencies | C07 component rights; C13a pricing; C12a ledger; C12b unknown settlement where payment flow; C11a refund on adjustment. |
| PR/Delivery Boundary | synthetic balances/test DB; no real charge, financial activation or migration. |
| Open Decisions | domain-specific caps and some expiry settings only where W leaves open; no new amount chosen. |
| Blockers | production activation until provider/release gates; design with fixed approved rules is ready. |
| Implementation Risks | reserve treated as capture; cap ignored on increase; concurrent overspend; stale rate/consent; premature release under unknown result. |
| Execution Readiness Verdict | **Reserve lifecycle is sufficiently specified for isolated implementation; product money movement remains behind release gates.** |

### Task پرریسک: `TASK:CORE:C09:004` — اتمیک‌بودن حقوق و جلوگیری از اثر دوم

| بُعد | شبیه‌سازی بر مبنای C09:015 و AC/TEST:C09:015 |
|---|---|
| Preconditions | operation/action IDs and source component authority; C03 idempotency envelope; C12a durable atomic write and recovery. |
| Required Inputs | repeated command/event, concurrent actors, balance/version, permission, operation state, ledger entry ref and replay marker. |
| Dependencies | C02 authorization; C07 rights; C03 event identity; C12a durable posting/reconciliation; C09 reservation/capture. |
| Relevant Architecture | validation and idempotency at durable transaction boundary; cache/provider idempotency is insufficient; ledger owner remains C12a. |
| Affected Components | pre-write validator, operation key registry, transaction boundary, dedupe storage, reconciliation and safe failure. |
| Data/API Contracts | separate reservation/capture/release action IDs linked to parent operation; same repeat key yields same outcome; conflict returns observable status. |
| Security Requirements | revalidate actor/tenant at write; prevent replay under another actor; no balance inference from cache; auditable denial. |
| Implementation Work Sequence | validate permission/component; begin atomic operation; compare operation ID and action type; enforce uniqueness; persist state via C12a contract; inject crashes; verify replay and recovery. |
| Deliverables | idempotency contract, database uniqueness/transaction plan, concurrent/replay fixtures, recovery runbook. |
| Failure Scenarios | duplicate HTTP command; duplicate outbox; race across workers; crash after ledger write; same key different payload; stale actor permission. |
| Recovery Strategy | return original operation result for identical retry; reject key/payload mismatch; reconcile uncertain write before retry; no new financial effect. |
| Required Tests | C09 AC/TEST:015 and C12a/C03 contract tests: duplicate operation, cross-worker race, crash recovery and unauthorized replay; NOT_EXECUTED. |
| Acceptance Criteria | one logical action has <=1 durable effect; reservation/capture/release distinct; mismatch denied; restart recovers from source of truth. |
| Definition of Done | DB constraint/transaction oracle plus contract tests; behavior correct without cache; ledger and consumer owners review. |
| Integration Dependencies | C03 idempotency; C12a durable ledger; C02 auth; C07 component; C12b inquiry if external unknown. |
| PR/Delivery Boundary | isolated tests and contract change; no real funds/provider activation. |
| Open Decisions | physical database mechanism/retry parameters remain architecture owner decisions if not specified. |
| Blockers | durable persistence implementation waits on C12a/C03 contract; design/gap review can proceed. |
| Implementation Risks | duplicate debit/credit; key reuse payload mutation; auth revoked after precheck; cache eviction permits replay. |
| Execution Readiness Verdict | **Critical invariant and failure oracle are clear; implementation depends on accepted C03/C12a durable contracts, not an invented policy.** |

**نتیجهٔ QG-13 برای C08 و C09:** برای هر بسته یک سناریوی پیچیده و یک پرریسک با مرزهای مالکیت مالی مستقل ثبت شد.

## C10 — انتقال و برداشت

### Task پیچیده: `TASK:CORE:C10:004` — چرخهٔ برداشت و نتیجه

| بُعد | شبیه‌سازی بر مبنای TASK:CORE:C10:004 و AC/TEST:CORE:C10:008–009 |
|---|---|
| Preconditions | مقصد و اختیار C02 تأیید؛ component rights از C07؛ سقف/feeهای مصوب یا OPEN مشخص؛ قرارداد inquiry C12b و ledger C12a. |
| Required Inputs | intent ID، source components، payee/account ref، amount/fee preview، consent version، provider status/correlation. |
| Dependencies | C02 identity/permission; C07 cashability; C03 idempotency; C12a reserve/post; C12b bank outcome; C13a fee; C13b presentation. |
| Relevant Architecture | C10 owns transfer/withdraw orchestration; C12b bank truth; C12a durable financial record; no client/proxy overrides. |
| Affected Components | preview/confirm, reserve, send, capture/release state, unknown inquiry, customer status. |
| Data/API Contracts | stable intent/operation IDs; destination and amount bound to approval; versioned fee; explicit unknown and references. |
| Security Requirements | revalidate actor, account ownership and org allowlist; no UI-only permission; sensitive account data minimized. |
| Implementation Work Sequence | evaluate eligible source; resolve payee; compute/display amount+fee; secure confirm; reserve; send once; inquiry on unknown; capture/release only on authoritative outcome. |
| Deliverables | transfer state machine, approval snapshot, C12a/C12b contract mapping, recovery and tests. |
| Failure Scenarios | destination changes after preview; account verification timeout; provider accepted but callback lost; duplicate send; ledger post failure. |
| Recovery Strategy | bind same idempotency ID; query status before retry; retain reservation on unknown; reconcile before release/capture. |
| Required Tests | AC/TEST C10:004/005/008/009 plus failure cases: preview binding, verification fail-closed, unknown reserved, replay no duplicate. NOT_EXECUTED. |
| Acceptance Criteria | only confirmed destination/amount proceeds; unknown remains unresolved; one intent yields at most one bank effect and one ledger effect. |
| Definition of Done | state transitions/owners/oracles and rollback reviewed; payment flags and limits remain outside inference. |
| Integration Dependencies | C02,C03,C07,C12a,C12b,C13a,C13b. |
| PR/Delivery Boundary | synthetic provider/ledger; no real transfer, credentials or production activation. |
| Open Decisions | provider, bank API, thresholds, fee and account freshness rules remain owner decisions. |
| Blockers | live bank operation waits provider/account-verification and release decisions; simulation contract can be completed. |
| Implementation Risks | double send, wrong destination, unauthorized org funding, unknown converted to failure, premature release. |
| Execution Readiness Verdict | **Contract/state design ready; live withdrawal BLOCKED_BY_PROVIDER_AND_RELEASE_DECISIONS.** |

### Task پرریسک: `TASK:CORE:C10:002` — احراز مقصد بانکی و مجوز

| بُعد | شبیه‌سازی بر مبنای C10-R005 و AC/TEST:C10:005 |
|---|---|
| Preconditions | destination ownership/source contract and actor context; organization account path distinct from personal; provider not selected. |
| Required Inputs | actor, wallet owner, destination ref, account verification state, purpose, permission/allowlist and freshness evidence. |
| Dependencies | C02 identity/role/allowlist; C07 ownership; authorized provider verification; C10 transfer policy. |
| Relevant Architecture | C10 consumes verified destination contract; C02 owns identity/authorization; unknown is not verified. |
| Affected Components | destination verification port, scope validator, fail-closed state, approval binding. |
| Data/API Contracts | verified/failed/unknown/expired states; stable destination reference; owner and verification timestamp, no raw account secret in logs. |
| Security Requirements | deny on mismatch/unknown/timeout; prevent personal admin card funding org; restrict sensitive details. |
| Implementation Work Sequence | request verification; map provider result; validate wallet-owner match; enforce personal/org rules; bind result to preview; revalidate before send; audit minimal metadata. |
| Deliverables | verification port contract, account ownership matrix, error mapping, fixtures for unknown/mismatch/expired. |
| Failure Scenarios | provider timeout, name mismatch, revoked verification, destination swap, personal card on org wallet. |
| Recovery Strategy | no send; request explicit correction or fresh verification; no retry with altered destination; route unknown to inquiry. |
| Required Tests | AC/TEST:C10:005: owner valid, another owner denied, timeout not treated as success; NOT_EXECUTED. |
| Acceptance Criteria | only fresh verified owner-matched account accepted; destination immutable after consent; no administrative bypass. |
| Definition of Done | provider contract owner, freshness rule source and negative oracle captured; no method/vendor invented. |
| Integration Dependencies | C02 authorization, C07 owner, C10:T04 approval. |
| PR/Delivery Boundary | fixture-based contract only; no real bank data or provider credentials. |
| Open Decisions | provider, freshness and organization proof criteria open. |
| Blockers | real verification waits owner/provider decision. |
| Implementation Risks | stale proof; cross-tenant account; administrator shortcut; sensitive account leak. |
| Execution Readiness Verdict | **Fail-closed contract testable; live use BLOCKED_BY_DECISION.** |

## C11a — استرداد و اصلاحات مالی

### Task پیچیده: `TASK:CORE:C11A:002` — تخصیص جزءبه‌جزء بازگشت

| بُعد | شبیه‌سازی بر مبنای C11A-R002/003/005 و AC/TEST 002/003/005 |
|---|---|
| Preconditions | original payment and component lineage; C07 rights/cashability; C12a immutable original entry; accepted largest-remainder rule. |
| Required Inputs | original amount/components, eligible refund amount, per-component rights/expiry and source, allocation version. |
| Dependencies | C12a original posting; C07 components; C05a/C13a refundable amount and cause; C08/09 source flows. |
| Relevant Architecture | C11a calculates wallet-return allocation; C12a records adjustment; original entry never overwritten. |
| Affected Components | refund allocator, component restore path, provenance, rounding/tie-break decision record. |
| Data/API Contracts | original tx link, component IDs, refund ID, amount, allocation algorithm version and total invariant. |
| Security Requirements | refund actor authorized; destination original payer; tenant scoping; audit amount/cause. |
| Implementation Work Sequence | calculate eligible amount; distribute by original component ratios; apply largest remainder; enforce approved tie-break only; check rights/expiry; post linked adjustment via C12a; verify sum. |
| Deliverables | allocation function contract, exact arithmetic oracle, component rights matrix, adjustment trace. |
| Failure Scenarios | partial refund rounding; missing component; expired gift; mismatch total; duplicate request; tie-break absent. |
| Recovery Strategy | block unresolved tie-break case; preserve original; reconcile linked correction; no cash conversion or guessed allocation. |
| Required Tests | C11A AC/TEST:002/003/005: full/partial split, equal remainders, expiry/cashability; NOT_EXECUTED. |
| Acceptance Criteria | sum of allocations exactly equals eligible amount; rights/expiry preserved; no component exceeds original refundable share; audit linked. |
| Definition of Done | algorithm/version and tie-break owner recorded; arithmetic fixtures and failure path accepted. |
| Integration Dependencies | C07 rights, C12a posting, C13a eligible amount, C11a refund flow. |
| PR/Delivery Boundary | synthetic values only; no real refunds or ledger rewriting. |
| Open Decisions | `OPEN:C11A:02` tie-break/version remains open; no default order introduced. |
| Blockers | exact component allocation when tie-break unresolved; remaining cases can be specified. |
| Implementation Risks | float drift; gift gains cashability; original overwritten; total mismatch. |
| Execution Readiness Verdict | **Core arithmetic contract ready; affected tie cases BLOCKED_BY_OWNER_DECISION.** |

### Task پرریسک: `TASK:CORE:C11A:005` — correction idempotency و unknown

| بُعد | شبیه‌سازی بر مبنای C11A-R009 و AC/TEST 009 |
|---|---|
| Preconditions | original transaction ID and payer/components; C03 event/idempotency; C12a durable adjustment; C12b unknown inquiry. |
| Required Inputs | adjustment intent ID, original reference, cause/eligibility, provider status, retry/replay markers and payer. |
| Dependencies | C05a/C13a amount and cause; C03 idempotency; C12a posting; C12b bank inquiry; C02 auth. |
| Relevant Architecture | C11a applies wallet return only; bank refund is separate owner flow; correction links original and never edits it. |
| Affected Components | correction command, durable idempotency, original reference validation, status inquiry and adjustment entry. |
| Data/API Contracts | unique adjustment ID, original payment link, actor/cause/version, unknown/confirmed/failure states. |
| Security Requirements | no clawback without valid cause/authority; no payer substitution; audit without sensitive payload. |
| Implementation Work Sequence | validate original/eligibility; query existing adjustment; check unknown bank status; apply same keyed wallet adjustment once; link source; verify no original mutation. |
| Deliverables | correction state machine, uniqueness constraint plan, replay/unknown fixtures and C12b/C12a handoffs. |
| Failure Scenarios | duplicate event, unknown return, original missing, another payer supplied, posting crash, bank response late. |
| Recovery Strategy | query before retry; same key; hold ambiguous case; reconcile with C12a; never create replacement original transaction. |
| Required Tests | AC/TEST:C11A:009: repeated request no second effect, unknown stays unresolved, original immutable. NOT_EXECUTED. |
| Acceptance Criteria | at most one adjustment per accepted intent; correct original/payer; unknown not treated as failed/settled; audit lineage complete. |
| Definition of Done | unique link and query path, negative/duplicate/failure fixtures, owner boundaries validated. |
| Integration Dependencies | C03 event; C12a adjustment ledger; C12b bank outcome; C13a eligibility. |
| PR/Delivery Boundary | planning/contract and mock tests only; no real reversal. |
| Open Decisions | reason classification and processing period `OPEN:C11A:01`; no SLA invented. |
| Blockers | disputed cause/unknown outcome waits owner; design remains actionable. |
| Implementation Risks | duplicate refund, wrong payer, erasing original, clawback without consent, false failure. |
| Execution Readiness Verdict | **High-risk invariants are specified; exact cause/SLA cases remain owner-gated.** |

## C11b — عملیات دوره‌ای و محدودیت‌ها

### Task پیچیده: `TASK:CORE:C11B:002` و `TASK:CORE:C11B:004` — اعمال هم‌زمان سقف‌های فعال

| بُعد | شبیه‌سازی بر مبنای C11B-R008 و AC/TEST:C11B:008 |
|---|---|
| Preconditions | policies and periods registered; member/org identity C02; available balance C07; accounting/atomicity C12a. |
| Required Inputs | active daily/monthly/operation caps, zone/period version, pending and completed amount, member/org scope. |
| Dependencies | C02 membership; C07 balance; C12a atomic counters; C11b scheduler and C14 status. |
| Relevant Architecture | C11b owns recurring operation scheduler and active-cap enforcement; C08 generic recharge caps stay there. |
| Affected Components | policy evaluator, rolling/calendar window, org/member aggregation, concurrency reservation. |
| Data/API Contracts | cap ID/version, scope, period, zone, pending/settled status, requested amount and decision. |
| Security Requirements | no cross-org counter read; only owner changes limits; logs contain no secret financial data. |
| Implementation Work Sequence | load active policies; derive period with configured zone; aggregate same-scope pending/settled; reserve capacity atomically; return explicit deny/allow reason. |
| Deliverables | cap precedence matrix, period evaluator, aggregate counter contract and concurrency fixtures. |
| Failure Scenarios | two concurrent requests at remaining capacity; zone boundary; one limit disabled; pending outcome unknown; member/org counter conflation. |
| Recovery Strategy | serialize/atomic reservation; hold unknown capacity; reconcile definitive result; do not free capacity on mere timeout. |
| Required Tests | C11B AC/TEST:008–009; daily blocks despite monthly headroom; disabled cap ignored; concurrent requests don't exceed active limits. NOT_EXECUTED. |
| Acceptance Criteria | all active limits enforced together; period/source explicit; unknown capacity remains held; member spend limited by org and actor authority. |
| Definition of Done | owner/period/zone scope and oracle approved; concurrency atomicity with C12a reviewed; open numeric values remain open. |
| Integration Dependencies | C02 actor, C07 rights, C12a entry/counter, C08 overall caps, C13a tariff. |
| PR/Delivery Boundary | synthetic schedule/ledger; no automatic bank charge. |
| Open Decisions | `OPEN:C11B:01/02` zone/period and configurable amounts. |
| Blockers | exact period/caps unresolved until owner sets values; evaluator contract can be implemented parametrically. |
| Implementation Risks | off-by-one boundary; pending ignored; duplicate capacity; wrong tenant aggregation. |
| Execution Readiness Verdict | **Evaluator and concurrency design are ready; enabling requires owner-approved period and values.** |

### Task پرریسک: `TASK:CORE:C11B:003` — نتیجه نامعلوم و retry همان درخواست

| بُعد | شبیه‌سازی بر مبنای C11B-R007 و AC/TEST:C11B:007 |
|---|---|
| Preconditions | stable recurring intent ID; C12b inquiry; C03 idempotency; next-run scheduler gated on definitive prior outcome. |
| Required Inputs | operation/period ID, provider status, inquiry result, retry count, notification state and current cap reservation. |
| Dependencies | C12b bank outcome; C03 job/event; C12a posted effect; C14 notice; C11b next-run gate. |
| Relevant Architecture | technical retry replays same request; new period's financial run is a different decision; unknown blocks new run. |
| Affected Components | status inquiry, retry controller, unresolved queue, capacity hold and scheduler gate. |
| Data/API Contracts | same operation ID for technical retry; separate period ID for new run; unknown/resolved statuses and correlation. |
| Security Requirements | no automatic new authorization; protected provider credentials; status access only to owner. |
| Implementation Work Sequence | classify unknown; inquiry original; replay same idempotency key only if policy permits; update C12a/C12b outcome; release capacity only on definitive result; then evaluate next scheduled run. |
| Deliverables | unknown transition model, same-ID retry rule, next-run guard and failure fixture. |
| Failure Scenarios | inquiry remains unknown; late success callback; exhausted retry; duplicate callback; next period begins while prior unresolved. |
| Recovery Strategy | retain unresolved and reserved capacity; escalate via owner; don't start next financial action; reconcile late event to same operation. |
| Required Tests | C11B AC/TEST:007: unknown requires inquiry; repeated message same ID no second effect; late definitive response doesn't auto-reenable schedule. NOT_EXECUTED. |
| Acceptance Criteria | unknown is neither failure nor success; same retry only; no new period run until policy gate; outcome visible and auditable. |
| Definition of Done | inquiry/replay/capacity/next-run guard and notification mapped to owner contract. |
| Integration Dependencies | C03, C12a, C12b, C14, C11b scheduler. |
| PR/Delivery Boundary | mock provider and state tests; no real bank action. |
| Open Decisions | retry thresholds, SLA, notice route remain `OPEN:C11B:03–05`. |
| Blockers | active scheduling until retry/SLA/zone owner decisions; state model is ready. |
| Implementation Risks | retry creates new debit; late success after new run; unknown capacity prematurely released. |
| Execution Readiness Verdict | **Safe-stop/idempotency design actionable; schedule activation blocked on open retry and period policies.** |

**نتیجهٔ QG-13 برای C10/C11a/C11b:** شش مسیر ۲۰‌بُعدی با شناسه‌های Task و AC/Testهای مرجع ثبت شد؛ نقاط وابسته به تصمیم بانکی/زمان‌بندی باز باقی مانده‌اند.


## تکمیل شبیه‌سازی بسته‌های C13a، C13b و C14

این شش شبیه‌سازی به Task، AC و Test Definition موجود در برنامه متصل‌اند؛ وضعیت‌ها همچنان برنامه‌ای‌اند و اجرای محصول را ادعا نمی‌کنند.

### C13a — `TASK:CORE:C13A:003`: failure, same-scope correction and supplier settlement

**انتخاب:** Task complex؛ سناریوها مستقیماً از معیارهای C13A-R07–R09; C13A-AC07–09; C13A-TD07–09 انتخاب شده‌اند.

| بُعد شبیه‌سازی | نتیجهٔ اجرای فرضی و کنترل لازم |
|---|---|
| Preconditions | پیش‌شرط‌ها: قرارداد و مرز مالکیت C13a حاضر؛ تصمیم‌های باز مرتبط همچنان باز. |
| Required inputs | ورودی‌ها: شناسه، نسخه/وضعیت مبدأ، actor و رخدادهای ورودی لازم برای failure, same-scope correction and supplier settlement. |
| Dependencies | وابستگی‌ها: C12b inquiry and reconciliation; C12a immutable posting; C11a customer correction; supplier contract. |
| Relevant architecture | معماری: مالکیت دامنه و منبع حقیقت در بستهٔ مالک باقی می‌ماند؛ این Task orchestration/مصرف را انجام می‌دهد. |
| Affected components | اجزای متاثر: TASK:CORE:C13A:003 و Subtaskهای تعریف‌شده در plan؛ مصرف‌کنندگان و مسیر خطای مرتبط با سناریوها. |
| Data/API contracts | قرارداد داده/API: شناسه و correlation پایدار؛ version/status صریح؛ هیچ مقدار یا endpoint تعریف‌نشده جعل نمی‌شود. |
| Security | امنیت: least privilege، scope جاری، redaction داده حساس و ثبت ممیزی بدون افشای secret/OTP/token. |
| Implementation sequence | توالی: آماده‌سازی منبع و مجوز؛ اجرای سناریوهای cancellation with delivered output; internal failure without output; unknown provider outcome; correction of same scope vs new customer request; supplier payable before/after reconciliation؛ بررسی state/side effect؛ ثبت شاهد و نتیجه؛ توقف در تصمیم باز. |
| Deliverables | خروجی: نتیجهٔ مورد انتظار هر سناریو، ردّ AC/Test، خطای مشاهده‌شده و handoff مالک مربوط. |
| Failure scenarios | شکست‌ها: cancellation with delivered output; internal failure without output; unknown provider outcome; correction of same scope vs new customer request; supplier payable before/after reconciliation. |
| Recovery | بازیابی: وضعیت قطعی از unknown جدا؛ inquiry یا مسیر مجاز قبل از retry؛ تکرار بدون side effect اضافی؛ موارد unresolved ارجاع می‌شوند. |
| Required tests | آزمون برنامه‌ای: C13A-R07–R09; C13A-AC07–09; C13A-TD07–09 با مسیر مثبت، مرزی، تکرار/ناموفق و کنترل دسترسی مندرج در Test Definition. |
| Acceptance criteria | پذیرش: Unknown remains unresolved pending inquiry; internal failure has no customer charge; same-scope correction has zero added customer charge; supplier payment waits for matched evidence and never creates a second debit. |
| Definition of Done | DoD: ACها و Test Definitionها trace شده؛ سناریوهای خطا و مرزی ثبت؛ decision gap حل‌نشده صریح و مانع activation مربوط است. |
| Integration dependencies | یکپارچگی: C12b inquiry and reconciliation; C12a immutable posting; C11a customer correction; supplier contract; خروجی با مالک مصرف‌کننده تطبیق می‌شود، بدون انتقال مالکیت. |
| PR/delivery boundary | مرز تحویل: فقط برنامه/قرارداد و آزمون ایزوله؛ بدون پرداخت واقعی، provider واقعی، migration یا فعال‌سازی production. |
| Open decisions | تصمیم باز: مقادیر/سیاست‌هایی که منبع آن‌ها را OPEN دانسته، OPEN می‌مانند؛ C12b inquiry and reconciliation; C12a immutable posting; C11a customer correction; supplier contract. |
| Blockers | مانع: اجرای runtime وابسته به محیط/تصمیم/دسترسی؛ شبیه‌سازی مشخصات را بدون آن‌ها می‌سنجد. |
| Implementation risks | ریسک: اشتباه گرفتن حالت unknown با failure، پذیرش side effect تکراری، scope نادرست یا ساختن مقدار پیش‌فرض. |
| Execution readiness verdict | حکم آمادگی: **Unknown remains unresolved pending inquiry; internal failure has no customer charge; same-scope correction has zero added customer charge; supplier payment waits for matched evidence and never creates a second debit.** شبیه‌سازی برنامه‌ای است؛ اجرای محصول هنوز انجام نشده است. |

### C13a — `TASK:CORE:C13A:002`: usage measurement and execution price snapshot

**انتخاب:** Task high-risk؛ سناریوها مستقیماً از معیارهای C13A-R04–R06; C13A-AC04–06; C13A-TD04–06 انتخاب شده‌اند.

| بُعد شبیه‌سازی | نتیجهٔ اجرای فرضی و کنترل لازم |
|---|---|
| Preconditions | پیش‌شرط‌ها: قرارداد و مرز مالکیت C13a حاضر؛ تصمیم‌های باز مرتبط همچنان باز. |
| Required inputs | ورودی‌ها: شناسه، نسخه/وضعیت مبدأ، actor و رخدادهای ورودی لازم برای usage measurement and execution price snapshot. |
| Dependencies | وابستگی‌ها: execution ID and tariff version; start-time snapshot; usage/internal cost/customer price as separate linked facts; metric and numeric rate remain OPEN. |
| Relevant architecture | معماری: مالکیت دامنه و منبع حقیقت در بستهٔ مالک باقی می‌ماند؛ این Task orchestration/مصرف را انجام می‌دهد. |
| Affected components | اجزای متاثر: TASK:CORE:C13A:002 و Subtaskهای تعریف‌شده در plan؛ مصرف‌کنندگان و مسیر خطای مرتبط با سناریوها. |
| Data/API contracts | قرارداد داده/API: شناسه و correlation پایدار؛ version/status صریح؛ هیچ مقدار یا endpoint تعریف‌نشده جعل نمی‌شود. |
| Security | امنیت: least privilege، scope جاری، redaction داده حساس و ثبت ممیزی بدون افشای secret/OTP/token. |
| Implementation sequence | توالی: آماده‌سازی منبع و مجوز؛ اجرای سناریوهای price changes during a running execution; replayed answer; new execution after stop; provider cost differs from customer price; missing usage metric؛ بررسی state/side effect؛ ثبت شاهد و نتیجه؛ توقف در تصمیم باز. |
| Deliverables | خروجی: نتیجهٔ مورد انتظار هر سناریو، ردّ AC/Test، خطای مشاهده‌شده و handoff مالک مربوط. |
| Failure scenarios | شکست‌ها: price changes during a running execution; replayed answer; new execution after stop; provider cost differs from customer price; missing usage metric. |
| Recovery | بازیابی: وضعیت قطعی از unknown جدا؛ inquiry یا مسیر مجاز قبل از retry؛ تکرار بدون side effect اضافی؛ موارد unresolved ارجاع می‌شوند. |
| Required tests | آزمون برنامه‌ای: C13A-R04–R06; C13A-AC04–06; C13A-TD04–06 با مسیر مثبت، مرزی، تکرار/ناموفق و کنترل دسترسی مندرج در Test Definition. |
| Acceptance criteria | پذیرش: Current execution keeps start snapshot; replay/inquiry is not fresh billable usage; a new authorized execution uses then-current tariff; no guessed metric or numeric rate; all three financial measures remain distinct. |
| Definition of Done | DoD: ACها و Test Definitionها trace شده؛ سناریوهای خطا و مرزی ثبت؛ decision gap حل‌نشده صریح و مانع activation مربوط است. |
| Integration dependencies | یکپارچگی: execution ID and tariff version; start-time snapshot; usage/internal cost/customer price as separate linked facts; metric and numeric rate remain OPEN; خروجی با مالک مصرف‌کننده تطبیق می‌شود، بدون انتقال مالکیت. |
| PR/delivery boundary | مرز تحویل: فقط برنامه/قرارداد و آزمون ایزوله؛ بدون پرداخت واقعی، provider واقعی، migration یا فعال‌سازی production. |
| Open decisions | تصمیم باز: مقادیر/سیاست‌هایی که منبع آن‌ها را OPEN دانسته، OPEN می‌مانند؛ execution ID and tariff version; start-time snapshot; usage/internal cost/customer price as separate linked facts; metric and numeric rate remain OPEN. |
| Blockers | مانع: اجرای runtime وابسته به محیط/تصمیم/دسترسی؛ شبیه‌سازی مشخصات را بدون آن‌ها می‌سنجد. |
| Implementation risks | ریسک: اشتباه گرفتن حالت unknown با failure، پذیرش side effect تکراری، scope نادرست یا ساختن مقدار پیش‌فرض. |
| Execution readiness verdict | حکم آمادگی: **Current execution keeps start snapshot; replay/inquiry is not fresh billable usage; a new authorized execution uses then-current tariff; no guessed metric or numeric rate; all three financial measures remain distinct.** شبیه‌سازی برنامه‌ای است؛ اجرای محصول هنوز انجام نشده است. |

### C13b — `TASK:CORE:C13B:001`: financial history with combined filters and scoped query

**انتخاب:** Task complex؛ سناریوها مستقیماً از معیارهای C13B-R01–R02; C13B-AC01–02; C13B-TD01–02 انتخاب شده‌اند.

| بُعد شبیه‌سازی | نتیجهٔ اجرای فرضی و کنترل لازم |
|---|---|
| Preconditions | پیش‌شرط‌ها: قرارداد و مرز مالکیت C13b حاضر؛ تصمیم‌های باز مرتبط همچنان باز. |
| Required inputs | ورودی‌ها: شناسه، نسخه/وضعیت مبدأ، actor و رخدادهای ورودی لازم برای financial history with combined filters and scoped query. |
| Dependencies | وابستگی‌ها: C12a source-owned operation ID/time/status; C03 read API; C02 current membership/tenant scope. |
| Relevant architecture | معماری: مالکیت دامنه و منبع حقیقت در بستهٔ مالک باقی می‌ماند؛ این Task orchestration/مصرف را انجام می‌دهد. |
| Affected components | اجزای متاثر: TASK:CORE:C13B:001 و Subtaskهای تعریف‌شده در plan؛ مصرف‌کنندگان و مسیر خطای مرتبط با سناریوها. |
| Data/API contracts | قرارداد داده/API: شناسه و correlation پایدار؛ version/status صریح؛ هیچ مقدار یا endpoint تعریف‌نشده جعل نمی‌شود. |
| Security | امنیت: least privilege، scope جاری، redaction داده حساس و ثبت ممیزی بدون افشای secret/OTP/token. |
| Implementation sequence | توالی: آماده‌سازی منبع و مجوز؛ اجرای سناریوهای combined type/status/time filters; empty result; timeout; date boundary; former organization member; other tenant؛ بررسی state/side effect؛ ثبت شاهد و نتیجه؛ توقف در تصمیم باز. |
| Deliverables | خروجی: نتیجهٔ مورد انتظار هر سناریو، ردّ AC/Test، خطای مشاهده‌شده و handoff مالک مربوط. |
| Failure scenarios | شکست‌ها: combined type/status/time filters; empty result; timeout; date boundary; former organization member; other tenant. |
| Recovery | بازیابی: وضعیت قطعی از unknown جدا؛ inquiry یا مسیر مجاز قبل از retry؛ تکرار بدون side effect اضافی؛ موارد unresolved ارجاع می‌شوند. |
| Required tests | آزمون برنامه‌ای: C13B-R01–R02; C13B-AC01–02; C13B-TD01–02 با مسیر مثبت، مرزی، تکرار/ناموفق و کنترل دسترسی مندرج در Test Definition. |
| Acceptance criteria | پذیرش: Authorized rows alone appear; filters compose without widening scope; empty is not success; timeout is not empty; former member and foreign tenant are denied/audited. |
| Definition of Done | DoD: ACها و Test Definitionها trace شده؛ سناریوهای خطا و مرزی ثبت؛ decision gap حل‌نشده صریح و مانع activation مربوط است. |
| Integration dependencies | یکپارچگی: C12a source-owned operation ID/time/status; C03 read API; C02 current membership/tenant scope; خروجی با مالک مصرف‌کننده تطبیق می‌شود، بدون انتقال مالکیت. |
| PR/delivery boundary | مرز تحویل: فقط برنامه/قرارداد و آزمون ایزوله؛ بدون پرداخت واقعی، provider واقعی، migration یا فعال‌سازی production. |
| Open decisions | تصمیم باز: مقادیر/سیاست‌هایی که منبع آن‌ها را OPEN دانسته، OPEN می‌مانند؛ C12a source-owned operation ID/time/status; C03 read API; C02 current membership/tenant scope. |
| Blockers | مانع: اجرای runtime وابسته به محیط/تصمیم/دسترسی؛ شبیه‌سازی مشخصات را بدون آن‌ها می‌سنجد. |
| Implementation risks | ریسک: اشتباه گرفتن حالت unknown با failure، پذیرش side effect تکراری، scope نادرست یا ساختن مقدار پیش‌فرض. |
| Execution readiness verdict | حکم آمادگی: **Authorized rows alone appear; filters compose without widening scope; empty is not success; timeout is not empty; former member and foreign tenant are denied/audited.** شبیه‌سازی برنامه‌ای است؛ اجرای محصول هنوز انجام نشده است. |

### C13b — `TASK:CORE:C13B:003`: access checks and controlled export

**انتخاب:** Task high-risk؛ سناریوها مستقیماً از معیارهای C13B-R05–R06; C13B-AC05–06; C13B-TD05–06 انتخاب شده‌اند.

| بُعد شبیه‌سازی | نتیجهٔ اجرای فرضی و کنترل لازم |
|---|---|
| Preconditions | پیش‌شرط‌ها: قرارداد و مرز مالکیت C13b حاضر؛ تصمیم‌های باز مرتبط همچنان باز. |
| Required inputs | ورودی‌ها: شناسه، نسخه/وضعیت مبدأ، actor و رخدادهای ورودی لازم برای access checks and controlled export. |
| Dependencies | وابستگی‌ها: C02 is sole authorization owner; organization/member scope; export policy/capability remains OPEN until approved. |
| Relevant architecture | معماری: مالکیت دامنه و منبع حقیقت در بستهٔ مالک باقی می‌ماند؛ این Task orchestration/مصرف را انجام می‌دهد. |
| Affected components | اجزای متاثر: TASK:CORE:C13B:003 و Subtaskهای تعریف‌شده در plan؛ مصرف‌کنندگان و مسیر خطای مرتبط با سناریوها. |
| Data/API contracts | قرارداد داده/API: شناسه و correlation پایدار؛ version/status صریح؛ هیچ مقدار یا endpoint تعریف‌نشده جعل نمی‌شود. |
| Security | امنیت: least privilege، scope جاری، redaction داده حساس و ثبت ممیزی بدون افشای secret/OTP/token. |
| Implementation sequence | توالی: آماده‌سازی منبع و مجوز؛ اجرای سناریوهای active owner; revoked former member; other tenant; export role absent; export capability unset؛ بررسی state/side effect؛ ثبت شاهد و نتیجه؛ توقف در تصمیم باز. |
| Deliverables | خروجی: نتیجهٔ مورد انتظار هر سناریو، ردّ AC/Test، خطای مشاهده‌شده و handoff مالک مربوط. |
| Failure scenarios | شکست‌ها: active owner; revoked former member; other tenant; export role absent; export capability unset. |
| Recovery | بازیابی: وضعیت قطعی از unknown جدا؛ inquiry یا مسیر مجاز قبل از retry؛ تکرار بدون side effect اضافی؛ موارد unresolved ارجاع می‌شوند. |
| Required tests | آزمون برنامه‌ای: C13B-R05–R06; C13B-AC05–06; C13B-TD05–06 با مسیر مثبت، مرزی، تکرار/ناموفق و کنترل دسترسی مندرج در Test Definition. |
| Acceptance criteria | پذیرش: Recheck authorization on every read/export; deny revoked/foreign actor; fail closed if export policy is unset; record audit metadata without copying protected financial details. |
| Definition of Done | DoD: ACها و Test Definitionها trace شده؛ سناریوهای خطا و مرزی ثبت؛ decision gap حل‌نشده صریح و مانع activation مربوط است. |
| Integration dependencies | یکپارچگی: C02 is sole authorization owner; organization/member scope; export policy/capability remains OPEN until approved; خروجی با مالک مصرف‌کننده تطبیق می‌شود، بدون انتقال مالکیت. |
| PR/delivery boundary | مرز تحویل: فقط برنامه/قرارداد و آزمون ایزوله؛ بدون پرداخت واقعی، provider واقعی، migration یا فعال‌سازی production. |
| Open decisions | تصمیم باز: مقادیر/سیاست‌هایی که منبع آن‌ها را OPEN دانسته، OPEN می‌مانند؛ C02 is sole authorization owner; organization/member scope; export policy/capability remains OPEN until approved. |
| Blockers | مانع: اجرای runtime وابسته به محیط/تصمیم/دسترسی؛ شبیه‌سازی مشخصات را بدون آن‌ها می‌سنجد. |
| Implementation risks | ریسک: اشتباه گرفتن حالت unknown با failure، پذیرش side effect تکراری، scope نادرست یا ساختن مقدار پیش‌فرض. |
| Execution readiness verdict | حکم آمادگی: **Recheck authorization on every read/export; deny revoked/foreign actor; fail closed if export policy is unset; record audit metadata without copying protected financial details.** شبیه‌سازی برنامه‌ای است؛ اجرای محصول هنوز انجام نشده است. |

### C14 — `TASK:CORE:C14:003`: versioned message lifecycle, deduplication and revocation

**انتخاب:** Task complex؛ سناریوها مستقیماً از معیارهای C14-R05–R06; C14-AC05–06; C14-TD05–06 انتخاب شده‌اند.

| بُعد شبیه‌سازی | نتیجهٔ اجرای فرضی و کنترل لازم |
|---|---|
| Preconditions | پیش‌شرط‌ها: قرارداد و مرز مالکیت C14 حاضر؛ تصمیم‌های باز مرتبط همچنان باز. |
| Required inputs | ورودی‌ها: شناسه، نسخه/وضعیت مبدأ، actor و رخدادهای ورودی لازم برای versioned message lifecycle, deduplication and revocation. |
| Dependencies | وابستگی‌ها: C03 source event identity/version and lineage; C02 authorization; C12b/domain impact evidence; priority threshold remains OPEN. |
| Relevant architecture | معماری: مالکیت دامنه و منبع حقیقت در بستهٔ مالک باقی می‌ماند؛ این Task orchestration/مصرف را انجام می‌دهد. |
| Affected components | اجزای متاثر: TASK:CORE:C14:003 و Subtaskهای تعریف‌شده در plan؛ مصرف‌کنندگان و مسیر خطای مرتبط با سناریوها. |
| Data/API contracts | قرارداد داده/API: شناسه و correlation پایدار؛ version/status صریح؛ هیچ مقدار یا endpoint تعریف‌نشده جعل نمی‌شود. |
| Security | امنیت: least privilege، scope جاری، redaction داده حساس و ثبت ممیزی بدون افشای secret/OTP/token. |
| Implementation sequence | توالی: آماده‌سازی منبع و مجوز؛ اجرای سناریوهای same event redelivery; newer version supersedes; revoke; out-of-order stale version; material vs low impact with numeric threshold unset؛ بررسی state/side effect؛ ثبت شاهد و نتیجه؛ توقف در تصمیم باز. |
| Deliverables | خروجی: نتیجهٔ مورد انتظار هر سناریو، ردّ AC/Test، خطای مشاهده‌شده و handoff مالک مربوط. |
| Failure scenarios | شکست‌ها: same event redelivery; newer version supersedes; revoke; out-of-order stale version; material vs low impact with numeric threshold unset. |
| Recovery | بازیابی: وضعیت قطعی از unknown جدا؛ inquiry یا مسیر مجاز قبل از retry؛ تکرار بدون side effect اضافی؛ موارد unresolved ارجاع می‌شوند. |
| Required tests | آزمون برنامه‌ای: C14-R05–R06; C14-AC05–06; C14-TD05–06 با مسیر مثبت، مرزی، تکرار/ناموفق و کنترل دسترسی مندرج در Test Definition. |
| Acceptance criteria | پذیرش: One logical message per same version; newer valid version supersedes with lineage; revoke invalidates; stale delivery cannot restore; prioritize by impact without inventing a numeric threshold. |
| Definition of Done | DoD: ACها و Test Definitionها trace شده؛ سناریوهای خطا و مرزی ثبت؛ decision gap حل‌نشده صریح و مانع activation مربوط است. |
| Integration dependencies | یکپارچگی: C03 source event identity/version and lineage; C02 authorization; C12b/domain impact evidence; priority threshold remains OPEN; خروجی با مالک مصرف‌کننده تطبیق می‌شود، بدون انتقال مالکیت. |
| PR/delivery boundary | مرز تحویل: فقط برنامه/قرارداد و آزمون ایزوله؛ بدون پرداخت واقعی، provider واقعی، migration یا فعال‌سازی production. |
| Open decisions | تصمیم باز: مقادیر/سیاست‌هایی که منبع آن‌ها را OPEN دانسته، OPEN می‌مانند؛ C03 source event identity/version and lineage; C02 authorization; C12b/domain impact evidence; priority threshold remains OPEN. |
| Blockers | مانع: اجرای runtime وابسته به محیط/تصمیم/دسترسی؛ شبیه‌سازی مشخصات را بدون آن‌ها می‌سنجد. |
| Implementation risks | ریسک: اشتباه گرفتن حالت unknown با failure، پذیرش side effect تکراری، scope نادرست یا ساختن مقدار پیش‌فرض. |
| Execution readiness verdict | حکم آمادگی: **One logical message per same version; newer valid version supersedes with lineage; revoke invalidates; stale delivery cannot restore; prioritize by impact without inventing a numeric threshold.** شبیه‌سازی برنامه‌ای است؛ اجرای محصول هنوز انجام نشده است. |

### C14 — `TASK:CORE:C14:008`: privacy, retention, incident ownership and Monitoring boundary

**انتخاب:** Task high-risk؛ سناریوها مستقیماً از معیارهای C14-R12–R14/R16; C14-AC12–14/16; C14-TD12–14/16 انتخاب شده‌اند.

| بُعد شبیه‌سازی | نتیجهٔ اجرای فرضی و کنترل لازم |
|---|---|
| Preconditions | پیش‌شرط‌ها: قرارداد و مرز مالکیت C14 حاضر؛ تصمیم‌های باز مرتبط همچنان باز. |
| Required inputs | ورودی‌ها: شناسه، نسخه/وضعیت مبدأ، actor و رخدادهای ورودی لازم برای privacy, retention, incident ownership and Monitoring boundary. |
| Dependencies | وابستگی‌ها: C02 privacy/access; C12a financial-history ownership; C04 entitlement; C13a pricing; retention/incident owner and fee/cap values remain OPEN. |
| Relevant architecture | معماری: مالکیت دامنه و منبع حقیقت در بستهٔ مالک باقی می‌ماند؛ این Task orchestration/مصرف را انجام می‌دهد. |
| Affected components | اجزای متاثر: TASK:CORE:C14:008 و Subtaskهای تعریف‌شده در plan؛ مصرف‌کنندگان و مسیر خطای مرتبط با سناریوها. |
| Data/API contracts | قرارداد داده/API: شناسه و correlation پایدار؛ version/status صریح؛ هیچ مقدار یا endpoint تعریف‌نشده جعل نمی‌شود. |
| Security | امنیت: least privilege، scope جاری، redaction داده حساس و ثبت ممیزی بدون افشای secret/OTP/token. |
| Implementation sequence | توالی: آماده‌سازی منبع و مجوز؛ اجرای سناریوهای RUM Web Vital vs form/session/click replay; financial record vs technical log expiry; privileged read; Monitoring without entitlement; unresolved fee/cap؛ بررسی state/side effect؛ ثبت شاهد و نتیجه؛ توقف در تصمیم باز. |
| Deliverables | خروجی: نتیجهٔ مورد انتظار هر سناریو، ردّ AC/Test، خطای مشاهده‌شده و handoff مالک مربوط. |
| Failure scenarios | شکست‌ها: RUM Web Vital vs form/session/click replay; financial record vs technical log expiry; privileged read; Monitoring without entitlement; unresolved fee/cap. |
| Recovery | بازیابی: وضعیت قطعی از unknown جدا؛ inquiry یا مسیر مجاز قبل از retry؛ تکرار بدون side effect اضافی؛ موارد unresolved ارجاع می‌شوند. |
| Required tests | آزمون برنامه‌ای: C14-R12–R14/R16; C14-AC12–14/16; C14-TD12–14/16 با مسیر مثبت، مرزی، تکرار/ناموفق و کنترل دسترسی مندرج در Test Definition. |
| Acceptance criteria | پذیرش: Allowlisted performance signals only; no form/session/click recording; technical-log lifecycle cannot delete financial history; privileged access is audited; Monitoring is denied absent entitlement; fee/cap is not assumed. |
| Definition of Done | DoD: ACها و Test Definitionها trace شده؛ سناریوهای خطا و مرزی ثبت؛ decision gap حل‌نشده صریح و مانع activation مربوط است. |
| Integration dependencies | یکپارچگی: C02 privacy/access; C12a financial-history ownership; C04 entitlement; C13a pricing; retention/incident owner and fee/cap values remain OPEN; خروجی با مالک مصرف‌کننده تطبیق می‌شود، بدون انتقال مالکیت. |
| PR/delivery boundary | مرز تحویل: فقط برنامه/قرارداد و آزمون ایزوله؛ بدون پرداخت واقعی، provider واقعی، migration یا فعال‌سازی production. |
| Open decisions | تصمیم باز: مقادیر/سیاست‌هایی که منبع آن‌ها را OPEN دانسته، OPEN می‌مانند؛ C02 privacy/access; C12a financial-history ownership; C04 entitlement; C13a pricing; retention/incident owner and fee/cap values remain OPEN. |
| Blockers | مانع: اجرای runtime وابسته به محیط/تصمیم/دسترسی؛ شبیه‌سازی مشخصات را بدون آن‌ها می‌سنجد. |
| Implementation risks | ریسک: اشتباه گرفتن حالت unknown با failure، پذیرش side effect تکراری، scope نادرست یا ساختن مقدار پیش‌فرض. |
| Execution readiness verdict | حکم آمادگی: **Allowlisted performance signals only; no form/session/click recording; technical-log lifecycle cannot delete financial history; privileged access is audited; Monitoring is denied absent entitlement; fee/cap is not assumed.** شبیه‌سازی برنامه‌ای است؛ اجرای محصول هنوز انجام نشده است. |


## Adviser و Assistant — ۳۲ شبیه‌سازی مستقل با Taskهای منبع‌دار

برای هر یک از بسته‌های R01–R10 و A01–A08 یک Task پیچیده و یک Task پرریسک انتخاب شده است. هر شبیه‌سازی ۲۰ بُعد را جدا ثبت می‌کند. ردیف‌ها سناریوهای طرح‌اند و شاهد اجرای محصول محسوب نمی‌شوند.

### R01 — `TASK:RAG:R01:003` — Evidence sufficiency and route selection

**انتخاب:** Task complex؛ ردیابی: R01-004–006 / AC+TEST 004–006.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R01 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R01:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: کمبود سند برای یک need؛ Core API نسخه ناسازگار؛ داده شخصی بدون purpose؛ فقط need ناکافی نیازمند live retrieval. |
| Dependencies | R03 evidence/snapshot؛ C01/C02 access; R02 source result. |
| Relevant architecture | R01 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R01:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های کمبود سند برای یک need؛ Core API نسخه ناسازگار؛ داده شخصی بدون purpose؛ فقط need ناکافی نیازمند live retrieval؛ بررسی هر transition و side-effect؛ تطبیق با R01-004–006 / AC+TEST 004–006؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R01-004–006 / AC+TEST 004–006؛ فهرست open decision و owner. |
| Failure scenarios | کمبود سند برای یک need؛ Core API نسخه ناسازگار؛ داده شخصی بدون purpose؛ فقط need ناکافی نیازمند live retrieval. |
| Recovery | similarity به تنهایی کافی نیست؛ مسیر هر need جدا؛ Core و personal فقط از owner contract؛ retrieval زنده هدفمند و مجاز در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R01-004–006 / AC+TEST 004–006: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | similarity به تنهایی کافی نیست؛ مسیر هر need جدا؛ Core و personal فقط از owner contract؛ retrieval زنده هدفمند و مجاز. |
| Definition of Done | هر AC/TEST در R01-004–006 / AC+TEST 004–006 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R03 evidence/snapshot؛ C01/C02 access; R02 source result؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R01: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** similarity به تنهایی کافی نیست؛ مسیر هر need جدا؛ Core و personal فقط از owner contract؛ retrieval زنده هدفمند و مجاز |

### R01 — `TASK:RAG:R01:004` — Failure recovery and risk/budget stop policy

**انتخاب:** Task high-risk؛ ردیابی: R01-007–008 / AC+TEST 007–008.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R01 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R01:004 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: live source timeout؛ cache قدیمی؛ retry exhaustion؛ هزینه/بودجه عددی تعریف‌نشده. |
| Dependencies | R02 allowed source/failure؛ R03 freshness; numeric parameters OPEN. |
| Relevant architecture | R01 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R01:004 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های live source timeout؛ cache قدیمی؛ retry exhaustion؛ هزینه/بودجه عددی تعریف‌نشده؛ بررسی هر transition و side-effect؛ تطبیق با R01-007–008 / AC+TEST 007–008؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R01-007–008 / AC+TEST 007–008؛ فهرست open decision و owner. |
| Failure scenarios | live source timeout؛ cache قدیمی؛ retry exhaustion؛ هزینه/بودجه عددی تعریف‌نشده. |
| Recovery | retry محدود با policy مجاز؛ fallback فقط تازگی/ریسک سازگار؛ stop reason روشن؛ هیچ آستانه‌ای ساخته نمی‌شود در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R01-007–008 / AC+TEST 007–008: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | retry محدود با policy مجاز؛ fallback فقط تازگی/ریسک سازگار؛ stop reason روشن؛ هیچ آستانه‌ای ساخته نمی‌شود. |
| Definition of Done | هر AC/TEST در R01-007–008 / AC+TEST 007–008 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R02 allowed source/failure؛ R03 freshness; numeric parameters OPEN؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R01: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** retry محدود با policy مجاز؛ fallback فقط تازگی/ریسک سازگار؛ stop reason روشن؛ هیچ آستانه‌ای ساخته نمی‌شود |

### R02 — `TASK:RAG:R02:004` — Persian extraction, normalization and quality/quarantine

**انتخاب:** Task complex؛ ردیابی: R02-006–009 / extraction AC/TEST.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R02 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R02:004 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: OCR فارسی جابه‌جایی ترتیب جدول؛ نیم‌فاصله/عدد؛ صفحه ناخوانا؛ استخراج partial و quarantine. |
| Dependencies | R03 evidence identity; C14 observability; extraction QA. |
| Relevant architecture | R02 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R02:004 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های OCR فارسی جابه‌جایی ترتیب جدول؛ نیم‌فاصله/عدد؛ صفحه ناخوانا؛ استخراج partial و quarantine؛ بررسی هر transition و side-effect؛ تطبیق با R02-006–009 / extraction AC/TEST؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R02-006–009 / extraction AC/TEST؛ فهرست open decision و owner. |
| Failure scenarios | OCR فارسی جابه‌جایی ترتیب جدول؛ نیم‌فاصله/عدد؛ صفحه ناخوانا؛ استخراج partial و quarantine. |
| Recovery | table header/row provenance حفظ؛ ابهام و کیفیت جدا؛ نقص بحرانی quarantine؛ منبع خام R02 باقی می‌ماند در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R02-006–009 / extraction AC/TEST: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | table header/row provenance حفظ؛ ابهام و کیفیت جدا؛ نقص بحرانی quarantine؛ منبع خام R02 باقی می‌ماند. |
| Definition of Done | هر AC/TEST در R02-006–009 / extraction AC/TEST به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R03 evidence identity; C14 observability; extraction QA؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R02: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** table header/row provenance حفظ؛ ابهام و کیفیت جدا؛ نقص بحرانی quarantine؛ منبع خام R02 باقی می‌ماند |

### R02 — `TASK:RAG:R02:005` — Untrusted-source and prompt-injection defense

**انتخاب:** Task high-risk؛ ردیابی: R02-010–012 / security AC/TEST.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R02 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R02:005 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: متن منبع شامل prompt injection؛ دستور tool؛ لینک مخرب؛ اسرار در payload. |
| Dependencies | C01 tool boundary; C02 access; R02 source permission. |
| Relevant architecture | R02 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R02:005 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های متن منبع شامل prompt injection؛ دستور tool؛ لینک مخرب؛ اسرار در payload؛ بررسی هر transition و side-effect؛ تطبیق با R02-010–012 / security AC/TEST؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R02-010–012 / security AC/TEST؛ فهرست open decision و owner. |
| Failure scenarios | متن منبع شامل prompt injection؛ دستور tool؛ لینک مخرب؛ اسرار در payload. |
| Recovery | متن منبع untrusted data؛ tool execution=0؛ مجوز R02/C02 حفظ؛ secret به log/answer نرود در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R02-010–012 / security AC/TEST: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | متن منبع untrusted data؛ tool execution=0؛ مجوز R02/C02 حفظ؛ secret به log/answer نرود. |
| Definition of Done | هر AC/TEST در R02-010–012 / security AC/TEST به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C01 tool boundary; C02 access; R02 source permission؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R02: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** متن منبع untrusted data؛ tool execution=0؛ مجوز R02/C02 حفظ؛ secret به log/answer نرود |

### R03 — `TASK:RAG:R03:004` — Compatible snapshot validation and atomic activation

**انتخاب:** Task complex؛ ردیابی: R03 snapshot/publication AC/TEST.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R03 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R03:004 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: candidate ناسازگار؛ دو نسخه هم‌زمان؛ failure هنگام activation؛ read در حین تغییر pointer. |
| Dependencies | R03 owner؛ R05 consumer; C01 release gates. |
| Relevant architecture | R03 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R03:004 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های candidate ناسازگار؛ دو نسخه هم‌زمان؛ failure هنگام activation؛ read در حین تغییر pointer؛ بررسی هر transition و side-effect؛ تطبیق با R03 snapshot/publication AC/TEST؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R03 snapshot/publication AC/TEST؛ فهرست open decision و owner. |
| Failure scenarios | candidate ناسازگار؛ دو نسخه هم‌زمان؛ failure هنگام activation؛ read در حین تغییر pointer. |
| Recovery | اعتبارسنجی تمام اعضا قبل از publish؛ atomic pointer؛ reader snapshot واحد؛ rollback به نسخه معتبر قابل ردیابی در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R03 snapshot/publication AC/TEST: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | اعتبارسنجی تمام اعضا قبل از publish؛ atomic pointer؛ reader snapshot واحد؛ rollback به نسخه معتبر قابل ردیابی. |
| Definition of Done | هر AC/TEST در R03 snapshot/publication AC/TEST به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R03 owner؛ R05 consumer; C01 release gates؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R03: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** اعتبارسنجی تمام اعضا قبل از publish؛ atomic pointer؛ reader snapshot واحد؛ rollback به نسخه معتبر قابل ردیابی |

### R03 — `TASK:RAG:R03:005` — Dependency lineage, selective invalidation and historical citation/rollback

**انتخاب:** Task high-risk؛ ردیابی: R03 lineage/invalidation AC/TEST.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R03 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R03:005 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: تغییر upstream با زنجیره چندمرحله‌ای؛ orphan; rollback تاریخی؛ citation از snapshot پیشین. |
| Dependencies | R03 canonical/lineage; R05 index; R06 citation. |
| Relevant architecture | R03 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R03:005 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های تغییر upstream با زنجیره چندمرحله‌ای؛ orphan; rollback تاریخی؛ citation از snapshot پیشین؛ بررسی هر transition و side-effect؛ تطبیق با R03 lineage/invalidation AC/TEST؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R03 lineage/invalidation AC/TEST؛ فهرست open decision و owner. |
| Failure scenarios | تغییر upstream با زنجیره چندمرحله‌ای؛ orphan; rollback تاریخی؛ citation از snapshot پیشین. |
| Recovery | فقط closure lineage تأییدشده invalidate؛ history حفظ؛ orphan/نامعلوم بررسی دستی؛ raw artifact حذف نمی‌شود در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R03 lineage/invalidation AC/TEST: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | فقط closure lineage تأییدشده invalidate؛ history حفظ؛ orphan/نامعلوم بررسی دستی؛ raw artifact حذف نمی‌شود. |
| Definition of Done | هر AC/TEST در R03 lineage/invalidation AC/TEST به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R03 canonical/lineage; R05 index; R06 citation؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R03: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** فقط closure lineage تأییدشده invalidate؛ history حفظ؛ orphan/نامعلوم بررسی دستی؛ raw artifact حذف نمی‌شود |

### R04 — `TASK:RAG:R04:003` — Source classification, trust and use-rights metadata

**انتخاب:** Task high-risk؛ ردیابی: R04 trust/use-rights AC/TEST.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R04 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R04:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: license نامعلوم؛ تغییر منبع؛ دامنه مصرف/بازنشر مبهم؛ trust با freshness متفاوت. |
| Dependencies | R02 access policy; R03 canonical source metadata; legal decision OPEN. |
| Relevant architecture | R04 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R04:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های license نامعلوم؛ تغییر منبع؛ دامنه مصرف/بازنشر مبهم؛ trust با freshness متفاوت؛ بررسی هر transition و side-effect؛ تطبیق با R04 trust/use-rights AC/TEST؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R04 trust/use-rights AC/TEST؛ فهرست open decision و owner. |
| Failure scenarios | license نامعلوم؛ تغییر منبع؛ دامنه مصرف/بازنشر مبهم؛ trust با freshness متفاوت. |
| Recovery | منع use تا policy/rights روشن؛ trust و freshness مستقل؛ evidence/source state مالکانه ثبت در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R04 trust/use-rights AC/TEST: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | منع use تا policy/rights روشن؛ trust و freshness مستقل؛ evidence/source state مالکانه ثبت. |
| Definition of Done | هر AC/TEST در R04 trust/use-rights AC/TEST به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R02 access policy; R03 canonical source metadata; legal decision OPEN؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R04: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** منع use تا policy/rights روشن؛ trust و freshness مستقل؛ evidence/source state مالکانه ثبت |

### R04 — `TASK:RAG:R04:005` — Idempotent discovery job and recovery contract

**انتخاب:** Task complex؛ ردیابی: R04 job/recovery AC/TEST.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R04 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R04:005 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: job duplicate؛ worker crash؛ backpressure؛ retry exhaustion؛ event redelivery. |
| Dependencies | C01/C03 Job; C14 telemetry; each service owns job state. |
| Relevant architecture | R04 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R04:005 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های job duplicate؛ worker crash؛ backpressure؛ retry exhaustion؛ event redelivery؛ بررسی هر transition و side-effect؛ تطبیق با R04 job/recovery AC/TEST؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R04 job/recovery AC/TEST؛ فهرست open decision و owner. |
| Failure scenarios | job duplicate؛ worker crash؛ backpressure؛ retry exhaustion؛ event redelivery. |
| Recovery | stable job ID؛ bounded retry؛ terminal failure قابل مشاهده؛ queue technology باز و job owner محفوظ در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R04 job/recovery AC/TEST: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | stable job ID؛ bounded retry؛ terminal failure قابل مشاهده؛ queue technology باز و job owner محفوظ. |
| Definition of Done | هر AC/TEST در R04 job/recovery AC/TEST به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C01/C03 Job; C14 telemetry; each service owns job state؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R04: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** stable job ID؛ bounded retry؛ terminal failure قابل مشاهده؛ queue technology باز و job owner محفوظ |

### R05 — `TASK:RAG:R05:003` — Eligibility, relation expansion and service coverage

**انتخاب:** Task complex؛ ردیابی: R05-004–006 / AC+TEST 004–006.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R05 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R05:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: رابطه confirmed در برابر ambiguous؛ منبع نامعتبر؛ نیاز خدمت با فیلد غایب؛ similar candidate خارج scope. |
| Dependencies | R03 relation/snapshot; C01 authenticity; C05b evidence contract. |
| Relevant architecture | R05 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R05:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های رابطه confirmed در برابر ambiguous؛ منبع نامعتبر؛ نیاز خدمت با فیلد غایب؛ similar candidate خارج scope؛ بررسی هر transition و side-effect؛ تطبیق با R05-004–006 / AC+TEST 004–006؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R05-004–006 / AC+TEST 004–006؛ فهرست open decision و owner. |
| Failure scenarios | رابطه confirmed در برابر ambiguous؛ منبع نامعتبر؛ نیاز خدمت با فیلد غایب؛ similar candidate خارج scope. |
| Recovery | eligibility به‌صورت قید؛ فقط relation confirmed traversal؛ گپ هر need با دلیل؛ سرویس evidence از C05b در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R05-004–006 / AC+TEST 004–006: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | eligibility به‌صورت قید؛ فقط relation confirmed traversal؛ گپ هر need با دلیل؛ سرویس evidence از C05b. |
| Definition of Done | هر AC/TEST در R05-004–006 / AC+TEST 004–006 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R03 relation/snapshot; C01 authenticity; C05b evidence contract؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R05: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** eligibility به‌صورت قید؛ فقط relation confirmed traversal؛ گپ هر need با دلیل؛ سرویس evidence از C05b |

### R05 — `TASK:RAG:R05:005` — Budgeted recovery and validity-aware cache

**انتخاب:** Task high-risk؛ ردیابی: R05-009–010 / AC+TEST 009–010.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R05 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R05:005 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: cache key با scope یا snapshot متفاوت؛ source revoked؛ retry budget تمام؛ stale fallback. |
| Dependencies | R01 stop policy; R02 access; R03 lineage; C02 scope. |
| Relevant architecture | R05 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R05:005 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های cache key با scope یا snapshot متفاوت؛ source revoked؛ retry budget تمام؛ stale fallback؛ بررسی هر transition و side-effect؛ تطبیق با R05-009–010 / AC+TEST 009–010؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R05-009–010 / AC+TEST 009–010؛ فهرست open decision و owner. |
| Failure scenarios | cache key با scope یا snapshot متفاوت؛ source revoked؛ retry budget تمام؛ stale fallback. |
| Recovery | cache key شامل tuple مصوب؛ invalidation انتخابی؛ stale data مردود؛ محدودیت attempts ثبت و escalation در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R05-009–010 / AC+TEST 009–010: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | cache key شامل tuple مصوب؛ invalidation انتخابی؛ stale data مردود؛ محدودیت attempts ثبت و escalation. |
| Definition of Done | هر AC/TEST در R05-009–010 / AC+TEST 009–010 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R01 stop policy; R02 access; R03 lineage; C02 scope؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R05: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** cache key شامل tuple مصوب؛ invalidation انتخابی؛ stale data مردود؛ محدودیت attempts ثبت و escalation |

### R06 — `TASK:RAG:R06:002` — Independent Citation Guard and uncertainty decision

**انتخاب:** Task complex؛ ردیابی: R06-003–005 / AC+TEST 003–005.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R06 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R06:002 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: ادعای مرکب با citation URL کلی؛ شواهد متعارض/قدیمی؛ بخشی مستند و بخشی نامطمئن. |
| Dependencies | R05 sufficiency; R03 legal relation/version; R01 routing. |
| Relevant architecture | R06 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R06:002 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های ادعای مرکب با citation URL کلی؛ شواهد متعارض/قدیمی؛ بخشی مستند و بخشی نامطمئن؛ بررسی هر transition و side-effect؛ تطبیق با R06-003–005 / AC+TEST 003–005؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R06-003–005 / AC+TEST 003–005؛ فهرست open decision و owner. |
| Failure scenarios | ادعای مرکب با citation URL کلی؛ شواهد متعارض/قدیمی؛ بخشی مستند و بخشی نامطمئن. |
| Recovery | ادعا اتمی؛ exact provision/version/scope؛ مستقل از generation؛ پاسخ جزئی/تکمیلی/امتناع بر اساس claim در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R06-003–005 / AC+TEST 003–005: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | ادعا اتمی؛ exact provision/version/scope؛ مستقل از generation؛ پاسخ جزئی/تکمیلی/امتناع بر اساس claim. |
| Definition of Done | هر AC/TEST در R06-003–005 / AC+TEST 003–005 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R05 sufficiency; R03 legal relation/version; R01 routing؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R06: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** ادعا اتمی؛ exact provision/version/scope؛ مستقل از generation؛ پاسخ جزئی/تکمیلی/امتناع بر اساس claim |

### R06 — `TASK:RAG:R06:004` — Prompt, authorization and privacy boundary

**انتخاب:** Task high-risk؛ ردیابی: R06-008 / AC+TEST 008.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R06 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R06:004 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: prompt injection از سند؛ context خصوصی بدون purpose؛ chain-of-thought یا متن حساس در trace. |
| Dependencies | C02 consent; C01 tool boundary; R02 untrusted input. |
| Relevant architecture | R06 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R06:004 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های prompt injection از سند؛ context خصوصی بدون purpose؛ chain-of-thought یا متن حساس در trace؛ بررسی هر transition و side-effect؛ تطبیق با R06-008 / AC+TEST 008؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R06-008 / AC+TEST 008؛ فهرست open decision و owner. |
| Failure scenarios | prompt injection از سند؛ context خصوصی بدون purpose؛ chain-of-thought یا متن حساس در trace. |
| Recovery | fail-closed tool/data policy؛ minimize/redact trace؛ no alternate ACL; no chain-of-thought persistence در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R06-008 / AC+TEST 008: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | fail-closed tool/data policy؛ minimize/redact trace؛ no alternate ACL; no chain-of-thought persistence. |
| Definition of Done | هر AC/TEST در R06-008 / AC+TEST 008 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C02 consent; C01 tool boundary; R02 untrusted input؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R06: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** fail-closed tool/data policy؛ minimize/redact trace؛ no alternate ACL; no chain-of-thought persistence |

### R07 — `TASK:RAG:R07:003` — ارزیابی candidate و صدور درخواست selective-ingestion/relation review

**انتخاب:** Task complex؛ ردیابی: R07-005–007 / AC+TEST 005–007.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R07 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R07:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: candidate lexical/semantic-only؛ relation ambiguous؛ انتخاب متن کامل؛ selective ingestion request. |
| Dependencies | R02 authorized access; R03 write; ADR-RAG-06/23/30/34. |
| Relevant architecture | R07 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R07:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های candidate lexical/semantic-only؛ relation ambiguous؛ انتخاب متن کامل؛ selective ingestion request؛ بررسی هر transition و side-effect؛ تطبیق با R07-005–007 / AC+TEST 005–007؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R07-005–007 / AC+TEST 005–007؛ فهرست open decision و owner. |
| Failure scenarios | candidate lexical/semantic-only؛ relation ambiguous؛ انتخاب متن کامل؛ selective ingestion request. |
| Recovery | signals جدا؛ ranking approval نیست؛ fetch فقط از R02؛ R03 canonical write owner؛ ambiguity به review در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R07-005–007 / AC+TEST 005–007: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | signals جدا؛ ranking approval نیست؛ fetch فقط از R02؛ R03 canonical write owner؛ ambiguity به review. |
| Definition of Done | هر AC/TEST در R07-005–007 / AC+TEST 005–007 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R02 authorized access; R03 write; ADR-RAG-06/23/30/34؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R07: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** signals جدا؛ ranking approval نیست؛ fetch فقط از R02؛ R03 canonical write owner؛ ambiguity به review |

### R07 — `TASK:RAG:R07:004` — durable job، dedupe، retry و مشاهده‌پذیری workflow

**انتخاب:** Task high-risk؛ ردیابی: R07-008 / AC+TEST 008.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R07 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R07:004 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: duplicate observation؛ retry after worker crash؛ dead letter؛ telemetry missing. |
| Dependencies | C01/C03 jobs; C14 event history; R04 observation. |
| Relevant architecture | R07 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R07:004 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های duplicate observation؛ retry after worker crash؛ dead letter؛ telemetry missing؛ بررسی هر transition و side-effect؛ تطبیق با R07-008 / AC+TEST 008؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R07-008 / AC+TEST 008؛ فهرست open decision و owner. |
| Failure scenarios | duplicate observation؛ retry after worker crash؛ dead letter؛ telemetry missing. |
| Recovery | same stable candidate/job ID؛ bounded retry؛ terminal status؛ no duplicate ingestion; recovery observable در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R07-008 / AC+TEST 008: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | same stable candidate/job ID؛ bounded retry؛ terminal status؛ no duplicate ingestion; recovery observable. |
| Definition of Done | هر AC/TEST در R07-008 / AC+TEST 008 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C01/C03 jobs; C14 event history; R04 observation؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R07: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** same stable candidate/job ID؛ bounded retry؛ terminal status؛ no duplicate ingestion; recovery observable |

### R08 — `TASK:RAG:R08:003` — impact analysis مبتنی بر dependency lineage

**انتخاب:** Task complex؛ ردیابی: R08-005 / AC+TEST 005.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R08 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R08:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: نسخه تغییر کرده و چند مشتق/سرویس downstream؛ رابطه تاییدنشده؛ دامنه blast radius. |
| Dependencies | R03 lineage; C05b service evidence; R03 relation state. |
| Relevant architecture | R08 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R08:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های نسخه تغییر کرده و چند مشتق/سرویس downstream؛ رابطه تاییدنشده؛ دامنه blast radius؛ بررسی هر transition و side-effect؛ تطبیق با R08-005 / AC+TEST 005؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R08-005 / AC+TEST 005؛ فهرست open decision و owner. |
| Failure scenarios | نسخه تغییر کرده و چند مشتق/سرویس downstream؛ رابطه تاییدنشده؛ دامنه blast radius. |
| Recovery | manifest فقط lineage/confirmed relation closure؛ مسیر و دلیل هر affected item؛ unknown برای review در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R08-005 / AC+TEST 005: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | manifest فقط lineage/confirmed relation closure؛ مسیر و دلیل هر affected item؛ unknown برای review. |
| Definition of Done | هر AC/TEST در R08-005 / AC+TEST 005 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R03 lineage; C05b service evidence; R03 relation state؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R08: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** manifest فقط lineage/confirmed relation closure؛ مسیر و دلیل هر affected item؛ unknown برای review |

### R08 — `TASK:RAG:R08:004` — بازسازی مشتقات و گیت‌های انتشار ownerها

**انتخاب:** Task high-risk؛ ردیابی: R08-006–007 / AC+TEST 006–007.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R08 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R08:004 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: درخواست rebuild؛ ناسازگاری نسخه؛ تلاش R08 برای نوشتن index/pointer؛ release gate fail. |
| Dependencies | R03 publication; R05 index; R06 answer; C01 release. |
| Relevant architecture | R08 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R08:004 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های درخواست rebuild؛ ناسازگاری نسخه؛ تلاش R08 برای نوشتن index/pointer؛ release gate fail؛ بررسی هر transition و side-effect؛ تطبیق با R08-006–007 / AC+TEST 006–007؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R08-006–007 / AC+TEST 006–007؛ فهرست open decision و owner. |
| Failure scenarios | درخواست rebuild؛ ناسازگاری نسخه؛ تلاش R08 برای نوشتن index/pointer؛ release gate fail. |
| Recovery | owner-specific handoff؛ R08 canonical/index/snapshot نمی‌نویسد؛ انتشار فقط بعد owner gates در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R08-006–007 / AC+TEST 006–007: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | owner-specific handoff؛ R08 canonical/index/snapshot نمی‌نویسد؛ انتشار فقط بعد owner gates. |
| Definition of Done | هر AC/TEST در R08-006–007 / AC+TEST 006–007 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | R03 publication; R05 index; R06 answer; C01 release؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R08: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** owner-specific handoff؛ R08 canonical/index/snapshot نمی‌نویسد؛ انتشار فقط بعد owner gates |

### R09 — `TASK:RAG:R09:002` — اتصال entity/evidence و transition revalidation

**انتخاب:** Task complex؛ ردیابی: R09-003–004 / AC+TEST 003–004.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R09 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R09:002 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: تغییر بانک/محصول؛ entity alias؛ evidence shared و entity-specific؛ snapshot version changed. |
| Dependencies | C05a/b IDs; R03 evidence; R01/R05 route. |
| Relevant architecture | R09 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R09:002 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های تغییر بانک/محصول؛ entity alias؛ evidence shared و entity-specific؛ snapshot version changed؛ بررسی هر transition و side-effect؛ تطبیق با R09-003–004 / AC+TEST 003–004؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R09-003–004 / AC+TEST 003–004؛ فهرست open decision و owner. |
| Failure scenarios | تغییر بانک/محصول؛ entity alias؛ evidence shared و entity-specific؛ snapshot version changed. |
| Recovery | stable IDs and version tuple؛ dependent evidence revalidated؛ shared evidence only if R05 confirms scope در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R09-003–004 / AC+TEST 003–004: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | stable IDs and version tuple؛ dependent evidence revalidated؛ shared evidence only if R05 confirms scope. |
| Definition of Done | هر AC/TEST در R09-003–004 / AC+TEST 003–004 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C05a/b IDs; R03 evidence; R01/R05 route؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R09: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** stable IDs and version tuple؛ dependent evidence revalidated؛ shared evidence only if R05 confirms scope |

### R09 — `TASK:RAG:R09:003` — continuity مجاز و interaction تغییر حوزه

**انتخاب:** Task high-risk؛ ردیابی: R09-005–006 / AC+TEST 005–006.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R09 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R09:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: cross-domain request; session expiry; active case; user consent missing/withdrawn. |
| Dependencies | C02 consent/session; case owner; user-memory owner remains OPEN. |
| Relevant architecture | R09 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R09:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های cross-domain request; session expiry; active case; user consent missing/withdrawn؛ بررسی هر transition و side-effect؛ تطبیق با R09-005–006 / AC+TEST 005–006؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R09-005–006 / AC+TEST 005–006؛ فهرست open decision و owner. |
| Failure scenarios | cross-domain request; session expiry; active case; user consent missing/withdrawn. |
| Recovery | minimal same-domain continuity; explicit purpose-limited consent for transfer; case remains owner service; no inferred permission در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R09-005–006 / AC+TEST 005–006: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | minimal same-domain continuity; explicit purpose-limited consent for transfer; case remains owner service; no inferred permission. |
| Definition of Done | هر AC/TEST در R09-005–006 / AC+TEST 005–006 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C02 consent/session; case owner; user-memory owner remains OPEN؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R09: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** minimal same-domain continuity; explicit purpose-limited consent for transfer; case remains owner service; no inferred permission |

### R10 — `TASK:RAG:R10:002` — Snapshot binding و result provenance

**انتخاب:** Task complex؛ ردیابی: R10-003–004 / AC+TEST 003–004.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R10 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R10:002 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: Core result built from mismatched product snapshot/rule version; R06 cannot resolve citation; replay. |
| Dependencies | Core calculator/C05b; R03 snapshot; R06 claim evidence. |
| Relevant architecture | R10 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R10:002 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های Core result built from mismatched product snapshot/rule version; R06 cannot resolve citation; replay؛ بررسی هر transition و side-effect؛ تطبیق با R10-003–004 / AC+TEST 003–004؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R10-003–004 / AC+TEST 003–004؛ فهرست open decision و owner. |
| Failure scenarios | Core result built from mismatched product snapshot/rule version; R06 cannot resolve citation; replay. |
| Recovery | one compatible tuple, persistent provenance; mixed tuple rejected; claim link resolve; no recalculation in Adviser در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R10-003–004 / AC+TEST 003–004: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | one compatible tuple, persistent provenance; mixed tuple rejected; claim link resolve; no recalculation in Adviser. |
| Definition of Done | هر AC/TEST در R10-003–004 / AC+TEST 003–004 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | Core calculator/C05b; R03 snapshot; R06 claim evidence؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R10: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** one compatible tuple, persistent provenance; mixed tuple rejected; claim link resolve; no recalculation in Adviser |

### R10 — `TASK:RAG:R10:003` — جداسازی outputها و خطای دامنه

**انتخاب:** Task high-risk؛ ردیابی: R10-005–006 / AC+TEST 005–006.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته R10 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:RAG:R10:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: calculator unavailable; malformed required input; unknown status; temptation to infer amount. |
| Dependencies | Core error contract; C02 input access; R06 disposition. |
| Relevant architecture | R10 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:RAG:R10:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های calculator unavailable; malformed required input; unknown status; temptation to infer amount؛ بررسی هر transition و side-effect؛ تطبیق با R10-005–006 / AC+TEST 005–006؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به R10-005–006 / AC+TEST 005–006؛ فهرست open decision و owner. |
| Failure scenarios | calculator unavailable; malformed required input; unknown status; temptation to infer amount. |
| Recovery | typed domain error/unknown; no numeric output; LLM arithmetic zero; distinct computed value/eligibility/rank/action در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | R10-005–006 / AC+TEST 005–006: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | typed domain error/unknown; no numeric output; LLM arithmetic zero; distinct computed value/eligibility/rank/action. |
| Definition of Done | هر AC/TEST در R10-005–006 / AC+TEST 005–006 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | Core error contract; C02 input access; R06 disposition؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های R10: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** typed domain error/unknown; no numeric output; LLM arithmetic zero; distinct computed value/eligibility/rank/action |

### A01 — `TASK:ASSISTANT:A01:002` — catalog binding و taxonomy ابزار

**انتخاب:** Task complex؛ ردیابی: A01 catalog binding AC/TEST 002–003.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A01 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A01:002 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: route catalog has unsupported capability version; duplicate alias; platform absent; owner contract mismatch. |
| Dependencies | C01/C05a route catalog; service owner API. |
| Relevant architecture | A01 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A01:002 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های route catalog has unsupported capability version; duplicate alias; platform absent; owner contract mismatch؛ بررسی هر transition و side-effect؛ تطبیق با A01 catalog binding AC/TEST 002–003؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A01 catalog binding AC/TEST 002–003؛ فهرست open decision و owner. |
| Failure scenarios | route catalog has unsupported capability version; duplicate alias; platform absent; owner contract mismatch. |
| Recovery | only published service/capability ID; unresolved alias blocked; fallback route requires explicit valid capability در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A01 catalog binding AC/TEST 002–003: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | only published service/capability ID; unresolved alias blocked; fallback route requires explicit valid capability. |
| Definition of Done | هر AC/TEST در A01 catalog binding AC/TEST 002–003 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C01/C05a route catalog; service owner API؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A01: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** only published service/capability ID; unresolved alias blocked; fallback route requires explicit valid capability |

### A01 — `TASK:ASSISTANT:A01:003` — Backend action gate

**انتخاب:** Task high-risk؛ ردیابی: A01 backend action-gate AC/TEST 003.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A01 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A01:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: valid suggestion but entitlement revoked; consent stale; role changed; model requests sensitive action. |
| Dependencies | C02 permission; C04 entitlement; owner service conditions. |
| Relevant architecture | A01 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A01:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های valid suggestion but entitlement revoked; consent stale; role changed; model requests sensitive action؛ بررسی هر transition و side-effect؛ تطبیق با A01 backend action-gate AC/TEST 003؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A01 backend action-gate AC/TEST 003؛ فهرست open decision و owner. |
| Failure scenarios | valid suggestion but entitlement revoked; consent stale; role changed; model requests sensitive action. |
| Recovery | server authoritative gate re-evaluates C02/C04 immediately before action; deny stale/unauthorized; no model bypass در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A01 backend action-gate AC/TEST 003: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | server authoritative gate re-evaluates C02/C04 immediately before action; deny stale/unauthorized; no model bypass. |
| Definition of Done | هر AC/TEST در A01 backend action-gate AC/TEST 003 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C02 permission; C04 entitlement; owner service conditions؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A01: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** server authoritative gate re-evaluates C02/C04 immediately before action; deny stale/unauthorized; no model bypass |

### A02 — `TASK:ASSISTANT:A02:001` — قرارداد Workflow/Parent–Child

**انتخاب:** Task complex؛ ردیابی: A02 parent-child workflow contract AC/TEST 001.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A02 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A02:001 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: parent dispatches several child tasks; one returns unknown; duplicate callback/out-of-order child result. |
| Dependencies | C01 job envelope; C05a route; C05b recommendation ref. |
| Relevant architecture | A02 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A02:001 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های parent dispatches several child tasks; one returns unknown; duplicate callback/out-of-order child result؛ بررسی هر transition و side-effect؛ تطبیق با A02 parent-child workflow contract AC/TEST 001؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A02 parent-child workflow contract AC/TEST 001؛ فهرست open decision و owner. |
| Failure scenarios | parent dispatches several child tasks; one returns unknown; duplicate callback/out-of-order child result. |
| Recovery | stable parent/child IDs and owner references; partial status explicit; reconcile before resume; no loss of sibling state در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A02 parent-child workflow contract AC/TEST 001: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | stable parent/child IDs and owner references; partial status explicit; reconcile before resume; no loss of sibling state. |
| Definition of Done | هر AC/TEST در A02 parent-child workflow contract AC/TEST 001 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C01 job envelope; C05a route; C05b recommendation ref؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A02: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** stable parent/child IDs and owner references; partial status explicit; reconcile before resume; no loss of sibling state |

### A02 — `TASK:ASSISTANT:A02:003` — action gate و reconciliation

**انتخاب:** Task high-risk؛ ردیابی: A02 action gate/reconciliation AC/TEST 003.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A02 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A02:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: permission revoked between propose and dispatch; target state changed; action outcome unknown. |
| Dependencies | C02 action permission; target service; C01/C03 idempotency. |
| Relevant architecture | A02 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A02:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های permission revoked between propose and dispatch; target state changed; action outcome unknown؛ بررسی هر transition و side-effect؛ تطبیق با A02 action gate/reconciliation AC/TEST 003؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A02 action gate/reconciliation AC/TEST 003؛ فهرست open decision و owner. |
| Failure scenarios | permission revoked between propose and dispatch; target state changed; action outcome unknown. |
| Recovery | recheck authorization/current conditions; inquiry before retry; same operation ID; hold until owner confirms در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A02 action gate/reconciliation AC/TEST 003: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | recheck authorization/current conditions; inquiry before retry; same operation ID; hold until owner confirms. |
| Definition of Done | هر AC/TEST در A02 action gate/reconciliation AC/TEST 003 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C02 action permission; target service; C01/C03 idempotency؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A02: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** recheck authorization/current conditions; inquiry before retry; same operation ID; hold until owner confirms |

### A03 — `TASK:ASSISTANT:A03:003` — TASK:ASSISTANT:A03:003

**انتخاب:** Task complex؛ ردیابی: A03-007–009 / AC+TEST 007–009.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A03 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A03:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: past outcome vs future risk; evidence confidence inadequate; plan entitlement differs; contradictory events. |
| Dependencies | event producer; C02/C04; Adviser evidence. |
| Relevant architecture | A03 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A03:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های past outcome vs future risk; evidence confidence inadequate; plan entitlement differs; contradictory events؛ بررسی هر transition و side-effect؛ تطبیق با A03-007–009 / AC+TEST 007–009؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A03-007–009 / AC+TEST 007–009؛ فهرست open decision و owner. |
| Failure scenarios | past outcome vs future risk; evidence confidence inadequate; plan entitlement differs; contradictory events. |
| Recovery | feedback and feedforward remain distinct; uncertainty explicit; evidence owner cited; entitlement from C04; no auto action در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A03-007–009 / AC+TEST 007–009: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | feedback and feedforward remain distinct; uncertainty explicit; evidence owner cited; entitlement from C04; no auto action. |
| Definition of Done | هر AC/TEST در A03-007–009 / AC+TEST 007–009 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | event producer; C02/C04; Adviser evidence؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A03: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** feedback and feedforward remain distinct; uncertainty explicit; evidence owner cited; entitlement from C04; no auto action |

### A03 — `TASK:ASSISTANT:A03:002` — TASK:ASSISTANT:A03:002

**انتخاب:** Task high-risk؛ ردیابی: A03-004–006/009–010 / AC+TEST.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A03 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A03:002 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: consent missing; plan expired; stale evidence; budget parameter unset; event suggests action. |
| Dependencies | C02/C04; owner evidence; A02 action gate. |
| Relevant architecture | A03 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A03:002 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های consent missing; plan expired; stale evidence; budget parameter unset; event suggests action؛ بررسی هر transition و side-effect؛ تطبیق با A03-004–006/009–010 / AC+TEST؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A03-004–006/009–010 / AC+TEST؛ فهرست open decision و owner. |
| Failure scenarios | consent missing; plan expired; stale evidence; budget parameter unset; event suggests action. |
| Recovery | fail closed/defer; no numeric threshold invented; event is not authorization; action only via A02 after new consent در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A03-004–006/009–010 / AC+TEST: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | fail closed/defer; no numeric threshold invented; event is not authorization; action only via A02 after new consent. |
| Definition of Done | هر AC/TEST در A03-004–006/009–010 / AC+TEST به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C02/C04; owner evidence; A02 action gate؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A03: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** fail closed/defer; no numeric threshold invented; event is not authorization; action only via A02 after new consent |

### A04 — `TASK:ASSISTANT:A04:003` — TASK:ASSISTANT:A04:003

**انتخاب:** Task complex؛ ردیابی: A04-009–012 / AC+TEST 009–012.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A04 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A04:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: UI changed after observation; ambiguous recipient/button; screenshot stale; step expects financial effect. |
| Dependencies | A02 workflow; C02; A06 UI map advisory. |
| Relevant architecture | A04 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A04:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های UI changed after observation; ambiguous recipient/button; screenshot stale; step expects financial effect؛ بررسی هر transition و side-effect؛ تطبیق با A04-009–012 / AC+TEST 009–012؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A04-009–012 / AC+TEST 009–012؛ فهرست open decision و owner. |
| Failure scenarios | UI changed after observation; ambiguous recipient/button; screenshot stale; step expects financial effect. |
| Recovery | reobserve; validate typed action against step/capability; stop/handoff on ambiguity or stale screen; effect confirmation via owner در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A04-009–012 / AC+TEST 009–012: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | reobserve; validate typed action against step/capability; stop/handoff on ambiguity or stale screen; effect confirmation via owner. |
| Definition of Done | هر AC/TEST در A04-009–012 / AC+TEST 009–012 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | A02 workflow; C02; A06 UI map advisory؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A04: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** reobserve; validate typed action against step/capability; stop/handoff on ambiguity or stale screen; effect confirmation via owner |

### A04 — `TASK:ASSISTANT:A04:004` — TASK:ASSISTANT:A04:004

**انتخاب:** Task high-risk؛ ردیابی: A04-013+ / security and recovery tests.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A04 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A04:004 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: OTP/credential enters screen; screenshot/log persisted; unknown provider result; replay attempt. |
| Dependencies | C01 telemetry; C02 security; owner operation API. |
| Relevant architecture | A04 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A04:004 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های OTP/credential enters screen; screenshot/log persisted; unknown provider result; replay attempt؛ بررسی هر transition و side-effect؛ تطبیق با A04-013+ / security and recovery tests؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A04-013+ / security and recovery tests؛ فهرست open decision و owner. |
| Failure scenarios | OTP/credential enters screen; screenshot/log persisted; unknown provider result; replay attempt. |
| Recovery | secret outside model/history/log; redact; outcome unknown; reconcile owner before retry; no result fabrication در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A04-013+ / security and recovery tests: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | secret outside model/history/log; redact; outcome unknown; reconcile owner before retry; no result fabrication. |
| Definition of Done | هر AC/TEST در A04-013+ / security and recovery tests به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C01 telemetry; C02 security; owner operation API؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A04: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** secret outside model/history/log; redact; outcome unknown; reconcile owner before retry; no result fabrication |

### A05 — `TASK:ASSISTANT:A05:003` — TASK:ASSISTANT:A05:003

**انتخاب:** Task complex؛ ردیابی: A05-010–012 / AC+TEST 010–012.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A05 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A05:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: recipient mismatch; mixed cashable/gift funds; daily limit boundary; provider unknown after dispatch. |
| Dependencies | C02; wallet/C12a; C11b limits; C12b reconcile. |
| Relevant architecture | A05 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A05:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های recipient mismatch; mixed cashable/gift funds; daily limit boundary; provider unknown after dispatch؛ بررسی هر transition و side-effect؛ تطبیق با A05-010–012 / AC+TEST 010–012؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A05-010–012 / AC+TEST 010–012؛ فهرست open decision و owner. |
| Failure scenarios | recipient mismatch; mixed cashable/gift funds; daily limit boundary; provider unknown after dispatch. |
| Recovery | preflight from wallet owner; preserve source restrictions; single idempotent request; unknown inquiry; no copied ledger logic در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A05-010–012 / AC+TEST 010–012: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | preflight from wallet owner; preserve source restrictions; single idempotent request; unknown inquiry; no copied ledger logic. |
| Definition of Done | هر AC/TEST در A05-010–012 / AC+TEST 010–012 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C02; wallet/C12a; C11b limits; C12b reconcile؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A05: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** preflight from wallet owner; preserve source restrictions; single idempotent request; unknown inquiry; no copied ledger logic |

### A05 — `TASK:ASSISTANT:A05:005` — TASK:ASSISTANT:A05:005

**انتخاب:** Task high-risk؛ ردیابی: A05-006/009–012 / AC+TEST.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A05 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A05:005 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: consent or entitlement changes; insufficient wallet balance; reservation expiry; billing replay. |
| Dependencies | C02/C04; wallet owner C12a/C13b; C14 notification. |
| Relevant architecture | A05 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A05:005 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های consent or entitlement changes; insufficient wallet balance; reservation expiry; billing replay؛ بررسی هر transition و side-effect؛ تطبیق با A05-006/009–012 / AC+TEST؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A05-006/009–012 / AC+TEST؛ فهرست open decision و owner. |
| Failure scenarios | consent or entitlement changes; insufficient wallet balance; reservation expiry; billing replay. |
| Recovery | revalidate C02/C04; reserve/capture/release only owner API; unique operation; no debit by assistant; failure safe در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A05-006/009–012 / AC+TEST: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | revalidate C02/C04; reserve/capture/release only owner API; unique operation; no debit by assistant; failure safe. |
| Definition of Done | هر AC/TEST در A05-006/009–012 / AC+TEST به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C02/C04; wallet owner C12a/C13b; C14 notification؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A05: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** revalidate C02/C04; reserve/capture/release only owner API; unique operation; no debit by assistant; failure safe |

### A06 — `TASK:ASSISTANT:A06:003` — TASK:ASSISTANT:A06:003

**انتخاب:** Task complex؛ ردیابی: A06-006–009 / AC+TEST 006–009.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A06 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A06:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: UI fingerprint changed; one route test fails; previous map active; candidate mapping incomplete. |
| Dependencies | A04 consumer; C05a route; service UI owner. |
| Relevant architecture | A06 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A06:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های UI fingerprint changed; one route test fails; previous map active; candidate mapping incomplete؛ بررسی هر transition و side-effect؛ تطبیق با A06-006–009 / AC+TEST 006–009؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A06-006–009 / AC+TEST 006–009؛ فهرست open decision و owner. |
| Failure scenarios | UI fingerprint changed; one route test fails; previous map active; candidate mapping incomplete. |
| Recovery | publish only tested version; preserve previous compatible map; failed test blocks activation; precise diff and evidence در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A06-006–009 / AC+TEST 006–009: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | publish only tested version; preserve previous compatible map; failed test blocks activation; precise diff and evidence. |
| Definition of Done | هر AC/TEST در A06-006–009 / AC+TEST 006–009 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | A04 consumer; C05a route; service UI owner؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A06: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** publish only tested version; preserve previous compatible map; failed test blocks activation; precise diff and evidence |

### A06 — `TASK:ASSISTANT:A06:002` — TASK:ASSISTANT:A06:002

**انتخاب:** Task high-risk؛ ردیابی: A06-003–005 / AC+TEST 003–005.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A06 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A06:002 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: discovery against real banking app; destructive action appears; account/session reused; cleanup fails. |
| Dependencies | owner authorization; A02; sandbox/test environment; no live transaction. |
| Relevant architecture | A06 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A06:002 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های discovery against real banking app; destructive action appears; account/session reused; cleanup fails؛ بررسی هر transition و side-effect؛ تطبیق با A06-003–005 / AC+TEST 003–005؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A06-003–005 / AC+TEST 003–005؛ فهرست open decision و owner. |
| Failure scenarios | discovery against real banking app; destructive action appears; account/session reused; cleanup fails. |
| Recovery | allowlist and authorized test account; non-destructive mode blocks action; isolate session; cleanup failure incident در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A06-003–005 / AC+TEST 003–005: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | allowlist and authorized test account; non-destructive mode blocks action; isolate session; cleanup failure incident. |
| Definition of Done | هر AC/TEST در A06-003–005 / AC+TEST 003–005 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | owner authorization; A02; sandbox/test environment; no live transaction؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A06: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** allowlist and authorized test account; non-destructive mode blocks action; isolate session; cleanup failure incident |

### A07 — `TASK:ASSISTANT:A07:003` — انتقال زمینه بین حوزه‌ها

**انتخاب:** Task complex؛ ردیابی: A07-004–005 / AC+TEST 004–005.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A07 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A07:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: transfer from one domain to another with mixed facts, case ID and revoked consent. |
| Dependencies | C02 consent; A02 case; owner services; R09 continuity. |
| Relevant architecture | A07 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A07:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های transfer from one domain to another with mixed facts, case ID and revoked consent؛ بررسی هر transition و side-effect؛ تطبیق با A07-004–005 / AC+TEST 004–005؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A07-004–005 / AC+TEST 004–005؛ فهرست open decision و owner. |
| Failure scenarios | transfer from one domain to another with mixed facts, case ID and revoked consent. |
| Recovery | purpose-limited allowlist; destination reauthorizes; stable owner references; no role/domain privilege transfer در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A07-004–005 / AC+TEST 004–005: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | purpose-limited allowlist; destination reauthorizes; stable owner references; no role/domain privilege transfer. |
| Definition of Done | هر AC/TEST در A07-004–005 / AC+TEST 004–005 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C02 consent; A02 case; owner services; R09 continuity؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A07: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** purpose-limited allowlist; destination reauthorizes; stable owner references; no role/domain privilege transfer |

### A07 — `TASK:ASSISTANT:A07:004` — گذار نشست و نقش

**انتخاب:** Task high-risk؛ ردیابی: A07-005–009 / AC+TEST 005–009.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A07 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A07:004 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: role switch; session expires while workflow is active; malicious retrieved text tries tool instructions. |
| Dependencies | C02; C06 role; A02 workflow; C01 tool policy. |
| Relevant architecture | A07 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A07:004 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های role switch; session expires while workflow is active; malicious retrieved text tries tool instructions؛ بررسی هر transition و side-effect؛ تطبیق با A07-005–009 / AC+TEST 005–009؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A07-005–009 / AC+TEST 005–009؛ فهرست open decision و owner. |
| Failure scenarios | role switch; session expires while workflow is active; malicious retrieved text tries tool instructions. |
| Recovery | re-evaluate role and consent; session expiry does not erase owner case; isolate retrieved text; deny direct private DB reads در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A07-005–009 / AC+TEST 005–009: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | re-evaluate role and consent; session expiry does not erase owner case; isolate retrieved text; deny direct private DB reads. |
| Definition of Done | هر AC/TEST در A07-005–009 / AC+TEST 005–009 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C02; C06 role; A02 workflow; C01 tool policy؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A07: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** re-evaluate role and consent; session expiry does not erase owner case; isolate retrieved text; deny direct private DB reads |

### A08 — `TASK:ASSISTANT:A08:003` — migration و ماتریس سازگاری

**انتخاب:** Task complex؛ ردیابی: A08-007–012 / AC+TEST 007–012.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A08 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A08:003 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: config classification mixes secret, flag and business policy; missing secret; incompatible rollback. |
| Dependencies | C01/C03 common config; C02 auth; C04 entitlement. |
| Relevant architecture | A08 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A08:003 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های config classification mixes secret, flag and business policy; missing secret; incompatible rollback؛ بررسی هر transition و side-effect؛ تطبیق با A08-007–012 / AC+TEST 007–012؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A08-007–012 / AC+TEST 007–012؛ فهرست open decision و owner. |
| Failure scenarios | config classification mixes secret, flag and business policy; missing secret; incompatible rollback. |
| Recovery | typed categories and owner; fail-closed required secret; flag cannot change policy; rollback compatibility checked; secrets never logged در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A08-007–012 / AC+TEST 007–012: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | typed categories and owner; fail-closed required secret; flag cannot change policy; rollback compatibility checked; secrets never logged. |
| Definition of Done | هر AC/TEST در A08-007–012 / AC+TEST 007–012 به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C01/C03 common config; C02 auth; C04 entitlement؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A08: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** typed categories and owner; fail-closed required secret; flag cannot change policy; rollback compatibility checked; secrets never logged |

### A08 — `TASK:ASSISTANT:A08:005` — authorization، secret و flag governance

**انتخاب:** Task high-risk؛ ردیابی: A08-011,013–014 / AC+TEST.

| بُعد | نتیجهٔ شبیه‌سازی |
|---|---|
| Preconditions | بسته A08 و قراردادهای وابسته در نسخهٔ plan حاضر؛ فقط TASK:ASSISTANT:A08:005 در محدوده است؛ design gapها OPEN می‌مانند. |
| Required inputs | ورودی‌های لازم: identity/version/status/provenance و actor/permission؛ سناریوهای آزمون: attempt to activate Assistant R1; kill switch; incompatible API/contract; partial rollback. |
| Dependencies | C01 release; O5-10; REL gates; Assistant stays “coming soon”. |
| Relevant architecture | A08 نقش مصرف‌کننده/هماهنگ‌کنندهٔ تعیین‌شده را دارد؛ مرجع داده و اختیار اثر در owner service باقی می‌ماند. |
| Affected components | TASK:ASSISTANT:A08:005 و Subtaskهای منبع؛ adapter/worker/guard مربوط؛ audit و error path همین سناریوها. |
| Data/API contracts | شناسه و version/correlation پایدار؛ response typed؛ unknown از failure جدا؛ schema/provider انتخاب‌نشده ساخته نمی‌شود. |
| Security | fail closed در نبود مجوز یا نسخه معتبر؛ حداقل داده؛ redaction secret/OTP؛ audit دسترسی حساس. |
| Implementation sequence | ثبت baseline؛ اجرای ورودی‌های attempt to activate Assistant R1; kill switch; incompatible API/contract; partial rollback؛ بررسی هر transition و side-effect؛ تطبیق با A08-011,013–014 / AC+TEST؛ ثبت gap و handoff owner. |
| Deliverables | جدول ورودی→حالت→نتیجه با شاهد trace به A08-011,013–014 / AC+TEST؛ فهرست open decision و owner. |
| Failure scenarios | attempt to activate Assistant R1; kill switch; incompatible API/contract; partial rollback. |
| Recovery | activation blocked in R1; safe disable; rollback only compatible version; independent release approval evidence در failure نیز برقرار؛ موارد unresolved به owner/صف مربوط می‌روند و retry کور انجام نمی‌شود. |
| Required tests | A08-011,013–014 / AC+TEST: مسیر مثبت و منفی، مرزی، تغییر نسخه/تکرار و مجوز؛ این‌ها برنامه‌ریزی تست‌اند، اجرا نشده‌اند. |
| Acceptance criteria | activation blocked in R1; safe disable; rollback only compatible version; independent release approval evidence. |
| Definition of Done | هر AC/TEST در A08-011,013–014 / AC+TEST به نتیجه آزمون وصل؛ مالکیت، error/recovery و open decisions مستند؛ runtime evidence جدا باقی بماند. |
| Integration dependencies | C01 release; O5-10; REL gates; Assistant stays “coming soon”؛ قرارداد مصرف‌کننده با owner تطبیق می‌شود و authority موازی ایجاد نمی‌شود. |
| PR/delivery boundary | تغییر برنامه/قرارداد و fixture ایزوله؛ بدون provider، داده، credential، اثر مالی یا production activation واقعی. |
| Open decisions | هر فناوری/عدد/آستانه/retention/fee که منبع آن تعیین نکرده OPEN می‌ماند؛ استنتاج تازه ممنوع. |
| Blockers | اجرای runtime مشروط به محیط، قرارداد اجرایی یا تصمیم صریح مربوط؛ بررسی برنامه‌ای مستقل انجام‌پذیر است. |
| Implementation risks | ریسک‌های A08: نقض مرز مالک، تبدیل unknown به success/failure، اثر تکراری، پذیرش stale یا حدس پارامتر. |
| Execution readiness verdict | **آماده برای تحویل/طراحی با قیود فوق؛ اجرای runtime NOT_EXECUTED.** activation blocked in R1; safe disable; rollback only compatible version; independent release approval evidence |
