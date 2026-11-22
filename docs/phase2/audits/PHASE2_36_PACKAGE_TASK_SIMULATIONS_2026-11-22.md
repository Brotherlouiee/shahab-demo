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

### انتخاب Task: `C12B-T03` — بازیابی و جلوگیری از تکرار

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

**وضعیت شبیه‌سازی:** دو Task متمایز C04 (یکی پیچیده، یکی پرریسک) ثبت شد. این‌ها مجوز فعال‌سازی پرداخت یا پذیرش محصول نیستند.
