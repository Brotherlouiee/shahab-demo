# دانش برنامه‌ریزی استخراج‌شده از Blueprint فاز دوم

**هدف:** نگهداری یافته‌های حاکم بر طراحی و برنامه‌ریزی Phase 5.0 برای یکپارچه‌سازی بعدی. این یادداشت جایگزین Blueprint، سند کیف پول، مصوبات مالک یا پرونده شواهد یک انتشار نیست و در این مأموریت قرارداد Phase 5 را تغییر نمی‌دهد.

## خط مبنا و اعتبار شواهد

| مورد | مقدار احرازشده |
|---|---|
| منبع | `docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` |
| Source commit | `8ce742b640bbcbb87be5fc29f3a5a28d92593dec` |
| Blob SHA | `9681c2bf6c3149317c3788516748084cfb6eac7c` |
| شمار واقعی خطوط | ۲٬۵۵۰ (`wc -l`) |
| SHA-256 محتوای نسخه حاضر | `0709c84fe9e47e1d9218c6d0f93a82c89a62d6b234565e9b0ca2d4158759f266` |
| پوشش معنایی | ۲٬۵۵۰ از ۲٬۵۵۰ خط؛ بدون شکاف؛ همه بازه‌های پیش‌تر PARTIAL بازخوانی شدند |

مبنای شواهد Blueprint بخش‌های ۱ تا ۳، ۴۰ تصمیم اصولی RAG، مصوبات بعدی A01–A09، B01–B06، D01–D03، E01–E04، O5-01 تا O5-14 و الحاقیه‌های تاریخی A و V1.1/V1.2/V1.4/V1.5/V1.6 است. بخش تاریخی تنها وضعیت همان تاریخ را گواهی می‌کند؛ وضعیت جدیدتر در متن سند بر یادداشت تاریخی مقدم است. هر ادعای runtime، migration، CI یا دسترسی منبع نیازمند شاهد مستقل همان محیط و نسخه است.

## یافته‌های مؤثر بر برنامه‌ریزی

### ۱. مرز معماری، مالکیت داده و ترتیب استقرار

- معماری هدف سه واحد منطقی Core، Adviser و Assistant دارد؛ Core مونولیت ماژولار است، Adviser سرویس مستقل مشاوره/دانش و Assistant سرویس مستقل اجرای کار است. در RAG R1 فقط Core و Adviser مستقر می‌شوند و Assistant در حد مرز و قرارداد معماری می‌ماند. نمودار منطقی مجوز استقرار مستقل، فناوری یا زمان‌بندی نیست. (B:790–810؛ B:811–860؛ A01)
- مالکیت داده و تراکنش در هر سرویس باقی می‌ماند، حتی اگر PostgreSQL/Redis مشترک باشد. دسترسی به داده سرویس دیگر فقط با قرارداد نسخه‌دار و مجوز هدفمند است؛ وابستگی به ORM/جدول خصوصی، تراکنش توزیع‌شده یا مرجع هویت موازی ممنوع است. Outbox فقط برای مصرف‌کننده/نیاز واقعی و در همان تراکنش محلی توجیه دارد. (B:861–910؛ B:1161–1210؛ A02/A05)
- عملیات کوتاه و قطعی با API هم‌زمان نسخه‌دار انجام می‌شود؛ کار طولانی در صورت نیاز، Job پایدار متعلق به مالک داده دارد. PostgreSQL مرجع durable state است؛ Redis تنها گزینه صف/اجرای اختیاری است. Broker مستقل و استخراج فیزیکی سرویس پیش‌فرض نیستند. (B:911–960؛ B:1161–1210؛ A03–A06)
- R1 نباید به Assistant، کیف پول، فروش اشتراک، درگاه پرداخت یا توسعه ظرفیت/زیرساخت جدید وابسته شود. هر افزایش ظرفیت، سرویس جدید یا تغییر معماری تصمیم جداگانه با اندازه‌گیری بار، شکست، امنیت، هزینه و تأیید مالک است. (B:1061–1110؛ B:1161–1210؛ B:2198–2297؛ A01)

**اثر برنامه‌ریزی:** در P5 هیچ فناوری/سرویس فیزیکی، dependency، release یا زمان‌بندی از دیاگرام، WBS فاز دوم یا نام یک ابزار نتیجه نمی‌شود. مرزهای مالکیت، قرارداد و نوع عملیات باید به‌عنوان قیود هر Deliverable مرتبط ثبت شوند.

### ۲. دامنه خدمت، مسیریابی، مجوز و اجرای ایمن

- Service Catalog مرجع منطقی نسخه‌دار دامنه/خدمت/قابلیت است؛ وجود مورد در کاتالوگ نه انتشار آن را ثابت می‌کند، نه دسترسی به داده شخصی یا اختیار اجرای عملیات را. Adviser و Assistant کاتالوگ Core را از API می‌خوانند و سرویس مالک، اجرای تخصصی را حفظ می‌کند. (B:861–910؛ E02)
- حوزه نشست ثابت می‌ماند. مسیریابی بر اساس هدف درخواست است، نه واژه منفرد. درخواست مستقل حوزه دیگر فقط پس از اقدام صریح کاربر منتقل می‌شود؛ همکاری پیش‌نیازمحور میان دو حوزه می‌تواند زیرکار نسخه‌دار داشته باشد، با مجوز مستقل و بدون جابه‌جایی حوزه نشست. ابهام مؤثر، اقدام حساس را متوقف می‌کند. (B:861–910؛ B01–B03)
- LLM می‌تواند هدف، پرسش روشن‌کننده، ابزار یا تحلیل را پیشنهاد کند؛ Backend و سرویس مالک، دامنه، مجوز، انتشار، شرایط جاری، رضایت و تأیید حساس را در مرز هر اقدام اثرگذار کنترل می‌کنند. نتیجه پرداخت، قیمت، وضعیت پرونده و مجوز را حافظه مدل تعیین نمی‌کند. (B:901–960؛ B04)
- اقدام مؤثر سه شرط مستقل دارد: حق دسترسی/Entitlement، رضایت و مجوز معتبر مشتری، و امکان قانونی/فنی. رمز بانکی ذخیره نمی‌شود. ابزار نوشتنی/تراکنشی نیازمند تأیید مناسب، idempotency، ثبت نتیجه و audit است. مشاهده endpoint در ترافیک مرورگر مجوز فراخوانی یا بازاستفاده از token/session نیست. (B:1150–1210)

**اثر برنامه‌ریزی:** برای هر دامنه مرتبط، Deliverable و پذیرش باید API owner، scope، مجوز، تأیید و رفتار denial/unknown را روشن کند. پیشنهاد LLM، حضور خدمت در کاتالوگ یا UI قابل مشاهده، معیار پذیرش کافی نیست. این‌ها قیود مصوب‌اند؛ متن Blueprint به‌تنهایی endpoint و تسک اجرایی تصویب نمی‌کند.

### ۳. Workflow، رویداد، هشدار و معیار ارزش

- گردش‌کار Assistant باید وضعیت پرونده، انتظار، توقف/ادامه، لغو، خطا، retry، انقضا و audit را پایدار نگه دارد. بازیابی worker و مهاجرت موتور باید نسخه‌دار و تدریجی باشد؛ کارهای در حال اجرا روی semantics سازگار قبلی می‌مانند. نتیجه بانکی نامعلوم پیش از retry تطبیق می‌شود؛ retry کور ممنوع است. (B:911–960؛ A04)
- رویداد صرفاً «نامزد بررسی» ایجاد می‌کند، نه اعلان یا دستور عملیات. شناسه پایدار، ترتیب لازم، deduplication، replay امن و مشاهده‌پذیری ضروری‌اند؛ Broker مستقل فقط در صورت نیاز و ظرفیت اثبات‌شده. (B:951–970؛ A03/A05)
- Feedback درباره وضعیت/نتیجه مشاهده‌شده است؛ Feedforward درباره ریسک/فرصت آینده و می‌تواند بدون پرسش جدید باشد؛ Monitoring فیچر مستقل کاربرمحور با trigger، entitlement، رضایت، چرخه عمر و بودجه مستقل است. Monitoring در Bronze غیرفعال و در Silver/Gold محدود به تعداد پایش هم‌زمان است؛ مقدار سقف عددی و هزینه مستقل احتمالی بازند. (B:961–1060؛ D01–D03؛ E01)
- هشدار دارای شناسه/وضعیت و نسخه شواهد است. ارتباط، تازگی، کفایت شواهد، entitlement و رضایت پیش‌نیاز اطلاع‌رسانی‌اند. In-App تاریخچه پایدار؛ تلاش Push/SMS، تحویل، مشاهده و اقدام وضعیت‌های جدا هستند. SMS مشروط است و محتوای بیرونی نباید جزئیات حساس افشا کند. ادغام هشدارهای تکراری نباید تغییر واقعاً جدید را حذف کند. (B:961–1010؛ D02/D03)
- کیفیت را با نرخ هشدار نادرست/تکراری، ارتباط، سودمندی، تأخیر تشخیص تا اطلاع‌رسانی و هزینه هشدار مفید بسنجید؛ کلیک به‌تنهایی ارزش نیست. بدون داده معتبر، احتمال عددی یا ادعای قطعیت حقوقی نسازید. (B:961–1010)

**اثر برنامه‌ریزی:** به P5-D07/D08/D12/D13 قید می‌دهد که ارزش و پذیرش باید outcome/کیفیت/ریسک و شواهد را ببیند و برای سنجه‌های عددی خط مبنا و تصمیم لازم است. چرخه‌های محصولی حاضر را به WBS یا schedule فاز پنجم تبدیل نکنید.

### ۴. سیاست‌های محصول و مالی مصوب در برابر جزئیات باز

- مدل تجاری سه جریان مستقل دارد: عضویت سالانه برای Entitlement، تعرفه ثابت هر نوع اجرای دستیار، و مصرف مشاور بر پایه تعداد prompt قابل صورتحساب × شدت تحلیل. عمق/کیفیت شواهد مشاور به پلن وابسته نیست. مصرف فنی، هزینه داخلی و قیمت مشتری برابر نیستند؛ خام‌مصرف توکن به‌تنهایی فرمول قیمت مصوب نیست. (B:1011–1060؛ B:1111–1160؛ E01)
- پلن Bronze پیش‌فرض و مقصد انقضاست؛ دامنه خدمات Bronze ⊆ Silver ⊆ Gold. تغییر پلن مجوز داده/اقدام نیست. تعهد معتبر خریداری‌شده با تغییر پلن خودکار حذف نمی‌شود؛ پایش فاقد entitlement معلق می‌شود و تاریخچه مجاز حذف نمی‌شود. Monitoring سقف فعال دارد؛ عدد سقف و نرخ احتمالی آن باز است. (B:1011–1060؛ E01/E04)
- اصول کیف پول E03 و سند نسخه 0.20 تصویب شده‌اند: موجودی عمومی، تفکیک حقوق اجزای اعتبار و منشأ، دفترکل ریالی و حساب‌های جدا، idempotency، atomicity، reconciliation، بازگشت به مسیر پرداخت‌کننده/منشأ و منع تبدیل هدیه/تخفیف به حق نقدی. سقف رزرو خودکار ۱۲۰٪ برآورد اولیه، مجوز headroom است نه کارمزد. هزینه داخلی/خارجی و مبلغ مشتری جدا ثبت می‌شوند. ضریب مشاوره داخل عملیات دستیار دقیقاً ۱/۲ نرخ مستقل است. (B:1011–1110؛ B:1111–1160؛ Wallet §§5–9)
- E04 اشتراک را با دوره/نسخه قیمت، ارتقا/تنزل، بازپرداخت، لغو اولیه، تمدید، consent و وضعیت‌های مستقل تعریف می‌کند. تمدید خودکار پیش‌فرض خاموش و افزایش قیمت نیازمند رضایت صریح است؛ نتیجه نامعلوم پیش از retry تطبیق می‌شود. قاعده بزرگ‌ترین باقیمانده برای تقسیم ریال مصوب است و فقط tie-break باز می‌ماند. (B:1061–1110؛ E04-O01…O23؛ Wallet §§6–9)
- FD-01 انتخاب فناوری/بانک کیف پول، پارامترها و انطباق حقوقی؛ FD-02 معماری/زمان فعال‌سازی اشتراک؛ FD-03 درگاه و خروجی حسابداری/مالیاتی؛ FD-04 قیمت عددی، معیار دقیق مصرف و هزینه، از اصول تجاری مصوب مستقل‌اند و برای RAG اول خارج دامنه‌اند. (B:1061–1160؛ B:2198–2297؛ FD-01…04)

**اثر برنامه‌ریزی:** P5-D04/D05/D06 باید تلاش/زمان/توکن/مصرف ابزار/هزینه توسعه/هزینه عملیات/قیمت مشتری را در واحد و معنا جدا کند. Policy مصوب را در رجیستر به‌عنوان تصمیم باز دوباره عرضه نکنید؛ اعداد و روش اجرایی فقط وقتی باز بمانند که مرجع آن‌ها را صریحاً باز گذاشته است. هیچ جریان مالی در RAG نخست فرض نشود.

### ۵. امنیت، قابلیت اطمینان، تخمین و شواهد

- نیازهای resilience شامل timeout budget، retry محدود با Backoff فقط برای خطای گذرا، circuit breaker در وابستگی ناپایدار، bulkhead تعاملی/پس‌زمینه، recovery و idempotency است؛ مقادیر و آستانه‌ها باید از بار و آزمون واقعی بیایند. (B:911–960؛ B:1161–1210؛ A06)
- Telemetry از OpenTelemetry/trace غیرشخصی پشتیبانی می‌کند، اما نباید OTP، token، هویت، پرسشنامه خام یا payload حساس را ذخیره کند. مالی audit دائمی از retention لاگ فنی جداست. RUM به page load/Web Vitals/خطای فرانت محدود است؛ click/session/form capture در این دامنه نیست. (B:1161–1210؛ A07/A09)
- ظرفیت، SLO، latency، throughput، CPU/RAM و هزینه هر نتیجه موفق باید روی workload نسخه‌دار اندازه‌گیری شوند. میزبان تاریخی، تعداد کاربر یا آستانه دلخواه proof ظرفیت نیست. توسعه و هزینه عملیاتی جدا تخمین زده شوند؛ پس از هر چرخه، برآورد با actual ساعت/نفرساعت/token/هزینه/rework مقایسه و علت تغییر forecast ثبت شود. (B:§§5.2.1, 5.14.4؛ A09؛ ارجاع implementation در §5.2.1)
- F06 در O5-10 sixteen rule حاکمیتی را تکمیل می‌کند و گیت تازه نیست: risk class R1–R4، اختیار و بازبینی مستقل متناسب، Go/Conditional Go/Hold/No-Go با دامنه/دلیل، حق توقف فوری برای مانع معتبر، رفع مانع/آزمون/تأیید مجدد، بودجه‌های جدا، و اعتبار decision برای نسخه مشخص کد/تنظیمات/قرارداد/Snapshot/دامنه/بودجه. Conditional Go محدود، مالک‌دار، زمان‌دار و بدون تمدید خودکار است. پرونده باید متن کامل RG/REL و نگاشت بندبه‌بند را حفظ کند؛ F06 جایگزین آن نیست. (B:2198–2247)
- حوزه‌های F06 شامل دامنه/ارزش، ریسک، کیفیت، امنیت/حریم خصوصی، منبع/قرارداد/Snapshot، بودجه/ظرفیت، reliability، توقف/بازیابی، اختیار/اختلاف و پایش پس از انتشار است. بودجه/آستانه/مسئول بدون خط مبنا و تصمیم تعیین نمی‌شود. (B:2198–2247)

**اثر برنامه‌ریزی:** P5-D03/04/05/06/12/13/15 باید تخمین مبتنی بر evidence، unknown/block، عدم قطعیت، risk-weighted acceptance و ردیابی نتیجه را حفظ کند. اینها حداقل کنترل‌های planning هستند، نه evidence اجرای release.

### ۶. تقدم الزام‌آور، پوشش و تصمیم‌گیری

- O5-01…O5-14 و سیاست سه‌مرحله‌ای مصوب‌اند. ترتیب بخش 5.14.1، **ترتیب پیشنهادی بررسی شواهد** است، نه dependency DAG خشک؛ موضوعات مستقل می‌توانند موازی بررسی شوند. برنامه اجرایی نهایی، scope/release/time/budget و سپس Epic/Story/Task/Test/AC/DoD نیازمند شواهد، رفع تعارض و تأیید صریح مالک است. (B:2198–2247؛ §§5.14.1–5.15)
- COV-01…20، AC-01…20 و G-COV-1/2/3 مصوب‌اند: ممیزی الزام‌به‌الزام، سازگاری بین‌تصمیمی، آمادگی اجرا. تمام قابلیت‌های مصوب از جمله scope کیف پول 0.20 با برچسب selected/approved/released/deferred نگهداری می‌شوند؛ تعویق حذف scope نیست و بی‌تصمیم owner به date commitment تبدیل نمی‌شود. (B:§5.14.3، 2248–2297)
- O5-14/EXP growth gates از O5-10 جدا هستند و جای آن را نمی‌گیرند. رشد خدمت، ظرفیت عملیاتی و معماری سه تصمیم جداست. فرصت جدید نیازمند evidence از تقاضا، ارزش، مجوز، ریسک، build/compliance/operating cost، reuse و failure blast radius است. عددی از پیش فرض نمی‌شود؛ ورود به portfolio مجوز توسعه نیست. (B:§5.14.4، 2198–2297)
- قبل از برنامه اجرایی باید scope/coverage فصل‌های ۱–۳، امکان‌سنجی فنی/حقوقی/منابع، release و dependency، AC/cost/rollback، انطباق فاز اول و retrospective، رفع تعارض و تأیید صریح owner انجام شود. حتی approval برنامه، خودبه‌خود مجوز task/PR/code نیست. (B:2248–2297)

### ۷. مرز تاریخی و نوع شواهد

- پیوست A ممیزی ساختاری مخزن را از runtime audit جدا می‌کند؛ شمار migration، tag/SHA/digest، وجود pgvector، آزمون محلی/CI و ادعای تولیدی هرکدام شاهد جدا لازم دارند. Proposed ports (SourceAccess/DocumentLifecycle/Retrieval/Advisor/IdentityPrivacy/Operational) قراردادهای طراحی‌اند، نه API یا پیاده‌سازی موجود. (B:2298–2347)
- V1.1/V1.2 یافته‌های تاریخ‌دار source audit هستند؛ unknown یا مشاهده مرورگری، عدم وجود API یا مجوز را اثبات نمی‌کند. عمومی بودن صفحه برابر مجوز جمع‌آوری ماشینی، ذخیره کامل، embedding، بازنشر یا استفاده تجاری نیست. شرایط مجوز باید برای هر منبع و روش جدا بررسی شود. S1–S5 به هر منبع/روش اعمال می‌شوند؛ V1.2 نسبت به V1.1 در تعارض وضعیت آزمون مقدم است. (B:2348–2550)
- عبور به Delivery Preparation یعنی PRD/AC، RFC، PoC ایزوله، WBS و approval قبل از code؛ نه اجازه کدنویسی یا تولید. اصول O5 مصوب‌اند، اما گیت‌های اجرایی با تصویب سیاست به‌تنهایی پاس نمی‌شوند. V1.4–V1.6 تاریخچه جانمایی/تکمیل قواعد مالی و مصوبات‌اند، نه مجوز توسعه. (B:2448–2550)

## نگاشت به تصمیمات P5 موجود

نگاشت زیر **قید/شاهد حاکم** است، نه پاسخ یا تصویب هیچ‌یک از تصمیمات P5:

| تصمیم P5 | دانش مرتبط Blueprint | مرز تصمیم باز برای مالک |
|---|---|---|
| P5-D01 مدل Deliverable | O5-13 پوشش نسخه‌دار؛ PRD، RFC، PoC و release evidence تفکیک؛ خدمت کاتالوگ با implementation یکی نیست (B:861–910; 2248–2297; 2498–2550) | خود مدل deliverable Phase 5 باید مالک تصویب کند؛ محصولی یا logical architecture به‌تنهایی تعریف قرارداد نیست. |
| P5-D02 دانه‌بندی تخصیص | ابتدا scope/feasibility/dependency/AC/cost/rollback، سپس Epic→Story→Task/Subtask؛ خدمات و زیرکار بین‌حوزه‌ای دارای owner/interface (B:861–960; 2248–2297; 2498–2550) | اندازه/واحد تعهد و decomposition Phase 5 همچنان P5 open؛ این ترتیب آماده‌سازی مجوز تخصیص نیست. |
| P5-D03 ظرفیت | measured workload, concurrency, latency, failures, recovery, costs; no historical host/user count as proof; separate service/capacity/architecture growth (B:1161–1210; 2198–2297) | ظرفیت واقعی/threshold باید از داده و owner approval بیاید. |
| P5-D04 effort | مجزا از duration/token/cost؛ مقایسه estimate با actual hours/person-hours/rework و علت forecast (B:2198–2247; §5.2.1) | روش، واحد و دقت estimate Phase 5 به تصویب نیاز دارد. |
| P5-D05 token | telemetry/resource consumption ≠ internal cost ≠ customer price؛ اندازه‌گیری جداگانه tool/API/model usage (B:1111–1160; 1161–1210) | روش تخمین/بودجه Token و forecast P5 باز می‌ماند؛ raw token pricing policy نیست. |
| P5-D06 cost | توسعه و run/operation جدا؛ شامل API/model/device/support/compliance، هزینه به ازای نتیجه موفق؛ customer fee جدا از internal cost (B:1061–1160; 2198–2297) | مقادیر و مالک هزینه، خط مبنا و روش forecast نیازمند تصمیم‌اند. |
| P5-D07 value | outcome مفید، کیفیت هشدار، سودمندی و هزینه هر هشدار مفید؛ کلیک alone معیار نیست (B:961–1010; 1111–1160) | ارزش و outcome target هر deliverable Phase 5 هنوز owner choice است. |
| P5-D08 prioritization | سیاست سه‌مرحله‌ای؛ O5 review order فقط ترتیب جمع‌آوری شواهد؛ growth و risk gates با هم جدا (B:2198–2297; 2498–2550) | scoring/trade-off و اولویت واقعی باید تصویب شوند؛ ترتیب پیشنهادی source dependency مصوب نمی‌سازد. |
| P5-D09 weekly scheduling | source ordering explicitly non-rigid؛ stage/release/readiness/task approval از هم جدا (B:2198–2247; 2248–2297) | weekly assignments, dates and capacity remain open; no task allocated here. |
| P5-D10 decision management | status مصوب/باز، owner, evidence, rationale, date, affected clauses; F06/O5 policy approved while implementation details remain open (B:2198–2247; 2248–2297) | register should distinguish already approved policies from new P5 choices; no status change without owner evidence. |
| P5-D11 Discovery/Delivery | source audit and PoC may proceed as bounded preparation; PRD/RFC/PoC before WBS/code; no unapproved production crawl (B:2398–2447; 2448–2550) | allocation ratio and capacity split for P5 remains a distinct owner decision. |
| P5-D12 uncertainty/risk | Unknown source access/rights remains unknown; no invented thresholds; risk-classed evidence, fail-closed, bounded Conditional Go and stop/revalidation (B:911–1010; 1161–1210; 2198–2247; 2398–2497) | numeric risk tolerance/confidence and uncertainty treatment for P5 must be chosen, with evidence. |
| P5-D13 weekly acceptance | accepted policy is not passed gate; each release needs full RG/REL mapping, actual evidence, tests, version, rollback/recovery, owner authority (B:2198–2247; 2298–2347) | weekly value/DoD acceptance definition remains owner decision. |
| P5-D14 planner infrastructure | Core/Adviser boundaries constrain product architecture but do not select the Phase 5 planning engine; shared infra ≠ shared data; broker/physical split only justified by evidence (B:790–810; 1161–1210) | P5 planner architecture/tool/infrastructure remains open; no architecture is auto-selected by Blueprint. |
| P5-D15 validation | G-COV 1–3, COV/AC mappings, source checks, real test vs local/CI vs runtime distinction, per-source S1–S5 and version evidence (B:2248–2347; 2398–2497) | P5 validator semantics and adequate evidence must be decided; old test success cannot cover unseen source semantics. |
| P5-D16 replanning | new evidence may change scope/sequence only via impact/owner approval; deferrals persist; growth does not create automatic stage/budget; changed artifact version invalidates affected decision evidence (B:2198–2297; 2248–2297) | trigger, cadence, decision authority and changes to committed week/scope require owner-approved P5 rule. |

## مرز این ثبت

این یادداشت Blueprint را با تصمیمات P5 موجود crosswalk می‌کند تا در گام یکپارچه‌سازی استفاده شود. هیچ تصمیم P5 را حل یا تصویب نمی‌کند، هیچ عبارت قرارداد را تغییر نمی‌دهد، هیچ Task/Week یا Deliverable اجرایی نمی‌سازد و Phase 5.1 را آغاز نمی‌کند. F01 همچنان به مطالعه کامل سایر منابع و مصرف artifactهای ماشینی/مقایسه نهایی نیاز دارد؛ تکمیل Blueprint به‌تنهایی F01 را نمی‌بندد.
