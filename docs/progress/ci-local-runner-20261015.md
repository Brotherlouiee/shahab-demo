# اجرای CI روی اجراکنندهٔ محلی شهاب

## محدوده و معیار پذیرش

تسک مستقل زیرساختی `CI-LOCAL-20261015` از `main=f5711e78df58366b65c7f00e29fa484ea5fb0b85`.
علت: سقف مصرف اجراکننده‌های میزبانی‌شده مانع شروع jobها شده است. مطلوب: همان شش job در سه workflow، با نام چک و فرمان آزمون قبلی، روی اجراکنندهٔ دارای برچسب `shahab-local` اجرا شوند. این کار هیچ زیرتسک US-13 را Done نمی‌کند.

سه قانون طلایی رعایت می‌شوند: تغییر کوچک زیرساختی؛ راهنمای جامع با blob `9d4e740ce4908d57ce33522603c4d83cf8df06fc` و پروتکل با blob `7a2e369ee6bef86601cb79b3b02cbe82c9e15d96` در همین جریان کار بازخوانی شده‌اند؛ پایان فقط با شاهد CI روی revision نهایی. منابع دادهٔ unitext موضوع این تغییر نیستند؛ UI، API، schema، scoring و داده دست‌نخورده‌اند.

## محیط و حفاظت از داده

- اجراکننده: WSL/Linux/X64، Docker Desktop، Git روی میزبان و برچسب اضافی `shahab-local`.
- نسخهٔ اصلاح‌شده از ایمیج ازپیش‌ساختهٔ محلی `shahab-ci:local-v1` استفاده می‌کند. عمداً `jobs.container` نیست: runner پیش از job برای image pull تلاش می‌کند؛ wrapper با `docker run --pull=never` از دانلود ایمیج آزمون و PostgreSQL جلوگیری می‌کند. نبود ایمیج خطای روشن است؛ fallback به image/DB دیگری نداریم.
- نود 22.23.3، Python 3.12 و Playwright 1.63.0 در شروع بررسی می‌شوند. دستور ساخت در `ci/local-image/Dockerfile` ثبت شده؛ دو archive ورودی فقط محلی و ignored هستند. نود با SHA256 رسمی بررسی شده؛ zip مرورگر از URL رسمی همان نسخهٔ اعلام‌شده توسط Playwright (Chrome for Testing 153.0.8010.12) دریافت و سلامت archive بررسی می‌شود. بررسی zip معادل تأیید رمزنگاری‌شدهٔ منشأ آن نیست.
- مرورگر آماده در `/opt/chrome/chrome-linux64/chrome` قرار دارد. config عمومی قبلاً متغیر `SHAHAB_E2E_BROWSER_PATH` داشت؛ config پروفایل و چهار launch مستقیمِ دو آزمون baseline هم همان متغیر را مصرف می‌کنند. در نبود متغیر، رفتار قبلی حفظ می‌شود؛ assertionها، viewportها، CSS، baseline SHA و شرط صفرپیکسل تغییر نمی‌کنند. این مرورگر کامل است؛ شواهد جدید باید با همین نسخه واقعاً تأیید شوند.
- هر job کانتینر موقت غیرroot با UID/GID اجراکننده دارد تا فایل‌های checkout/artifact root-owned نشوند. venv تازه در /tmp ساخته می‌شود؛ کتابخانه‌های پروژه هنوز از lockfile/pyproject نصب می‌شوند. cacheهای دانلود npm/pip در پوشهٔ اختصاصی runner نگه داشته می‌شوند؛ هیچ venv یا node_modules قدیمی جایگزین نصب معتبر نمی‌شود.
- PostgreSQL آزمایشی فقط از ایمیج محلی `postgres:16-alpine`، در شبکهٔ تصادفی همان job و با نام داخلی `postgres` ساخته می‌شود. تنها دو نام `shahab_test` و `shahab_profile_test` مجازند. هیچ پورت میزبان publish نمی‌شود و هیچ volume موجود mount نمی‌شود.
- cleanup فقط نام‌های تصادفی همان invocation را حذف می‌کند و anonymous volume خود PostgreSQL آزمایشی را پاک می‌کند. docker compose، global prune، reset و دسترسی به `shahab-demo_postgres_data` وجود ندارد. شکست تست همان کد خروجی شکست را نگه می‌دارد؛ readiness ناموفق DB مانع اجرای suite می‌شود.
- فقط checkout جاری، فایل فرمان read-only و cache دانلود mount می‌شوند؛ docker socket و env محلی برنامه به کانتینر داده نمی‌شوند. مسیرهای baseline /tmp در کانتینر موقت‌اند. artifactها از checkout runner با همان نام و retention قبلی upload می‌شوند.
- این روش به دانلود بسته‌های پروژه، fetch baseline، audit امنیتی و upload artifact هنوز نیاز دارد؛ «CI کاملاً آفلاین» ادعا نمی‌شود. کانتینر مرز امنیتی کافی برای کد مخرب نیست؛ runner به Docker میزبان دسترسی دارد و فقط برای مخزن خصوصی و کد مورد اعتماد است.

## روش استفاده

در Ubuntu و پوشهٔ `~/actions-runner` اجراکننده باید با `./run.sh` روشن و در حالت Listening for Jobs باشد؛ لپ‌تاپ، Ubuntu و Docker Desktop روشن بمانند. با Ctrl+C اجراکننده متوقف می‌شود؛ دادهٔ برنامه حذف نمی‌شود.

همهٔ jobها هر چهار برچسب `self-hosted, Linux, X64, shahab-local` را لازم دارند. اگر job در صف ماند، وضعیت Online و همین برچسب‌ها را در Settings → Actions → Runners بررسی کن. این اتصال ابزار به endpoint مدیریتی runner دسترسی ندارد؛ دریافت واقعی job شاهد مستقل اتصال است.

ابتدا PR همین زیرساخت باید با شش چک واقعی بررسی شود. پس از تأیید و مرج مالک، شاخهٔ PR #131 باید تغییرات جدید main را دریافت کند و روی SHA تازه آزمون شود. صرف rerun اجرای قدیمی، فایل workflow قدیمی را به نسخهٔ جدید تبدیل نمی‌کند. هیچ bypass یا وضعیت موفق دستی جایگزین آزمون نیست.

## اعتبارسنجی و محدودیت

قبل از push: YAML سه workflow، نحو bash wrapper و فرمان‌ها، syntax سه فایل مرورگر، حفظ نام jobها/triggerها/timeoutها/فرمان‌های آزمون/baseline/artifact بررسی شد. پنج آزمون wrapper با Docker شبیه‌سازی‌شده، عدم pull و انتشار پورت، محدودبودن cleanup، رد DB غیرآزمایشی، انتقال شکست تست و readiness ناموفق را اثبات کردند. این آزمون‌ها جای اجرای واقعی Docker نیستند. در محیط Codex فعلی Docker نصب نیست؛ اجرای کانتینر، نصب وابستگی و suiteها فقط روی runner لپ‌تاپ قابل اثبات است. موفقیت بررسی ایستا معادل موفقیت CI نیست.

برای شکست، SHA، job، step و اولین خطای همان attempt بررسی می‌شود. سقف زمان آزمون صرفاً برای سبزشدن افزایش نمی‌یابد. برگشت با revert همین تغییر زیرساخت و بازگشت workflowها به اجراکنندهٔ میزبانی‌شده ممکن است؛ داده یا migration برای برگشت لازم نیست.

## ثبت زمان

شروع بخش ثبت‌شده: 2026-10-15T20:42:30.487Z (UTC). مراحل نصب و راهنمایی پیش از این زمان ثبت دقیق نداشته‌اند.
خواندن/بررسی، آماده‌سازی patch، بررسی ایستا و انتشار در همین تسک ثبت می‌شوند؛ انتظار اجرای لپ‌تاپ جدا از زمان فعالیت است. نتیجهٔ واقعی jobها از صفحهٔ Actions در SHA نهایی خوانده می‌شود، نه از زمان commit.

## علت اصلاح پس از اجرای اول

روی `d9089b7`: job امنیتی `116661336337` در pull اوبونتو 403 گرفت؛ baseline `116661336331` پس از حدود هفت دقیقه دانلود Node لغو شد. تکرار نصب میزبان تازه علت اصلی اتلاف بود. ساخت اولیهٔ image نیز به دلیل منع مکانی CDN مرورگر شکست خورد؛ مالک archive رسمی را با مرورگر دریافت کرد، image را ساخت و موفقیت smoke اجرای صفحه و مرورگر را اعلام کرد. این گزارش مالک جایگزین suiteهای CI نیست.

ادامهٔ ثبت‌شدهٔ اصلاح: 2026-10-15T23:09:37.847Z (UTC). مدت فعالیت راهنمایی و انتظار دانلود/ساخت در فاصلهٔ گفت‌وگو به‌صورت دقیق ثبت نشده و از فاصلهٔ پیام‌ها حدس زده نمی‌شود. بررسی محلی wrapper پنج آزمون موفق داشت؛ نتیجهٔ شش job نهایی فقط پس از اجرای همین revision معتبر است. سه قانون طلایی و نبود merge/deploy/تغییر داده همچنان برقرارند؛ سند تداوم تا پایان داستان تغییر نمی‌کند.

## اصلاح بر پایهٔ شواهد attemptهای بعدی — ۲۰۲۶-۱۰-۱۶

- هر شش job در attempt اول 9a41173 پیش از suite به EACCES پوشهٔ checkout قدیمی خوردند. مالک با chown محدود به checkout اجراکننده مالکیت را اصلاح کرد؛ attempt بعدی checkout را با موفقیت گذراند. wrapper جدید با UID/GID میزبان ادامه می‌دهد؛ نیازی به اجرای runner با root نیست.
- job امنیتی 116726131687: SAST پاس؛ pip-audit شش advisory فقط برای pip 24.0 گزارش کرد، با حداقل fix مشترک 26.2. venv اوبونتو برخلاف setup-python قبلی pip قدیمی دارد. قبل از نصب وابستگی در job امنیتی، `python -m pip install --upgrade "pip>=26.2"` اضافه شد؛ audit و سیاست رد آسیب‌پذیری حفظ شدند. انتشار 26.2 و latest 26.2.1 از JSON رسمی PyPI بررسی شد.
- job تصویری 116726107872: trace در launch مرورگر به سقف 30 ثانیه رسید؛ smoke هم‌شرایط مالک launch=647ms و exit=0 داشت. یک rerun با همین شاهد محیطی مجاز شد. job 116729242074 دیگر timeout نداشت: home/about390 دقیقاً صفر پیکسل اختلاف، اما login390 با bbox(24,33,366,368) و 73972 پیکسل متفاوت شکست خورد؛ PNG مرجع فرم واقعی و candidate اسکلت بارگذاری بود. بنابراین علتِ این failure زمان‌بندی fixture است، نه شاهد تغییر طراحی.
- پیش از screenshot هر دو origin در login، visible بودن `.hp-login-form` و hidden بودن `.hp-deferred-skeleton` به fixture افزوده شد. selector قبلیِ اندازه‌گیری nav، تمام viewportها، تصاویر مستقل baseline/candidate، SHA ثابت و assertion صفرپیکسل حفظ شدند؛ sleep، mask، threshold، تغییر محصول یا افزایش timeout نداریم.
- syntax JavaScript/YAML/bash فرمان اصلاح‌شده پاس شد. suite تصویری و audit واقعی فقط CI همین commit می‌توانند تأیید کنند؛ موفقیت از بررسی ایستا یا تصاویر subset نتیجه‌گیری نمی‌شود. زمان دقیق فعالیت این بخش مستقل ثبت نشده؛ هیچ زمان حدسی از فاصلهٔ پیام‌ها گزارش نمی‌شود.


## ادامهٔ اصلاح لغو و سنجش محدود — ۲۰۲۶-۱۰-۱۶

Checkpoint پیش از تغییر: wrapper هنگام docker run پیش‌زمینه می‌تواند اجرای trap را تا پایان child عقب بیندازد؛ نتیجه مطلوب، خروج با status شکست/لغو و حذف فقط منابع همان invocation است. محدوده فقط CI/scripts/tests/docs است؛ UI/API/schema/data/scoring تغییر نمی‌کند. وابستگی‌ها: شش job سه workflow و wrapper مشترک. اثبات نزدیک: هفت تست mock شامل TERM و فیلتر مالکیت؛ اثبات واقعی روی Docker لپ‌تاپ جدا لازم است.

- docker run در background با wait قابل قطع اجرا می‌شود؛ container/network برچسب run-attempt-job دارند. هر شش job مرحله always برای پاک‌سازی فقط همان برچسب دارند. این کنترل cooperative cancellation است؛ خاموشی میزبان/daemon یا SIGKILL همهٔ پردازش‌ها تضمین cleanup فوری ندارد.
- scripts/ci/diagnose-local-postgres.sh فقط در checkout مستقل اجرا شود. در حضور container آزمون دیگر متوقف می‌شود؛ ابتدا sleep واقعی داخل container را با TERM قطع و نبود container/network همان probe را بررسی می‌کند (۲۰ ثانیه + حداکثر ۱۰ ثانیه kill grace). سپس تنها test_upgrade_fixture_and_downgrade را روی DB آزمایشی wrapper اجرا می‌کند (کل مرحله ۲۴۰ ثانیه + grace)؛ نصب، import، ۲۰ تراکنش موقت و هر subprocess migration زمان مستقل دارند. هیچ fsync/synchronous_commit/full_page_writes تغییر نمی‌کند. suite کامل، مرورگر، npm و workflow جدید اجرا نمی‌شود.
- بررسی منبع نشان داد fixtureها migration را در subprocess و در setup/teardown تکرار می‌کنند؛ این فقط فرضیه اندازه‌گیری است، نه علت قطعی کندی لپ‌تاپ. سقف‌ها و فرمان‌های gateهای موجود حفظ شده‌اند.
- بررسی هدفمند نهایی: ۷/۷ آزمون Node mock، bash -n سه script، Python compile و parse YAML موفق. Docker در محیط Codex موجود نیست؛ سنجش واقعی لغو و PostgreSQL هنوز اجرا نشده است. نتیجه واقعی باید از لپ‌تاپ دریافت شود؛ PR همچنان draft است.
- commit با [skip ci] منتشر می‌شود تا طبق دستور مالک شش gate دوباره وارد صف نشوند؛ این commit اثبات CI موفق یا مجوز merge نیست. پس از بررسی محدود و رفع علت، نسخه نهایی باید gateهای لازم را واقعاً بگذراند.
- ثبت زمان: بررسی اولیه این نوبت پیش از 2026-10-16T07:55:54Z دقیق ثبت نشده؛ اولین checkpoint ساعت 07:55:54Z UTC است. زمان فعالیت بخش‌های پیشین حدس زده نمی‌شود. build/full suite تکرار نشده؛ انتظار ضروری باقی‌مانده اجرای probe روی Docker مالک است.

## حذف نصب تکراری پایتون — ۲۰۲۶-۱۰-۱۶

Checkpoint این نوبت: در خروجی مالک روی f5fba822، نصب ۷۹ ثانیه، import برابر ۰٫۶۴۸، ۲۰ تراکنش ۲٫۵۳۶ و یک migration test برابر ۲۲٫۷۶۵ ثانیه بود؛ upgrade head به‌تنهایی ۱۷٫۶۷۹ ثانیه. عبور برنامه به DB به معنی عبور probe اولیه لغو است. این فقط یک test است و علت زمان تمام suite را اثبات نمی‌کند.

محدوده مصوب: setup پایتون و زمان‌سنجی CI؛ نه تغییر fixture یا assertionهای migration، UI، API، dependency versions، schema، scoring یا داده کاربر. وابستگی‌ها چهار job پایتون، wrapper مشترک و probe محدودند. fixtureهای migration فعلاً حفظ می‌شوند؛ هزینه آن‌ها هنوز در کل suite اندازه‌گیری نشده است.

### رفتار جدید
- prepare-python-environment.py محیط نصب‌شده را در snapshot محلی نگه می‌دارد؛ برای هر container در همان مسیر /tmp/shahab-job-python یک کپی خصوصی بازسازی می‌شود. مسیر editable کد همچنان /workspace جاری است؛ کد PR قبلی از snapshot اجرا نمی‌شود. cache شامل کد منبع برنامه یا HOME/credential نیست.
- کلید شامل pyproject.toml کامل، خود helper، Python/ABI/platform/architecture، profile و شناسه immutable ایمیج آماده است. عمر reuse حداکثر ۲۴ ساعت است چون وابستگی‌های Python range هستند. تغییر این ورودی‌ها یا انقضا باعث نصب تازه می‌شود. profile امنیتی مستقل، pip>=26.2 و bandit/pip-audit با نسخه‌های قبلی دارد؛ audit هر بار اجرا می‌شود.
- cache hit هیچ pip install ندارد؛ فقط استخراج کپی مستقل و pip check انجام می‌شود. cache خراب/ناسازگار بازسازی می‌شود؛ نصب ناموفق snapshot جدید منتشر نمی‌کند. انتشار atomic و lock بین آماده‌سازی‌های هم‌کلید است. استخراج با data filter و بدون symlink مطلق است. interpreterهای venv در snapshot کپی‌اند و lib64 نسبی حفظ می‌شود. cache برای کد مورد اعتماد runner است، نه مرز امنیتی بین PR خصمانه.
- فرمان‌های نصب workflow به bootstrap منتقل شده‌اند، نه اینکه وابستگی‌ها حذف شوند. سه job عمومی پایتون profile project مشترک و job امنیتی profile security دارد. نصب Node و تمام فرمان‌های آزمون/امنیت/browser/baseline و سقف gateها حفظ شده‌اند. هر ۹ مجموعه unittest PostgreSQL با time مدت مستقل می‌دهند.
- probe جدید با --cache ابتدا لغو wrapper را می‌سنجد، سپس یک container برای ساخت/اعتبارسنجی snapshot و container دوم برای cache hit و همان یک migration test اجرا می‌کند. سقف‌ها ۲۰/۱۸۰/۱۲۰ ثانیه و هرکدام حداکثر ۱۰ ثانیه grace هستند؛ آزمون کامل را dispatch نمی‌کند. Docker در Codex موجود نیست؛ زمان بهبود روی لپ‌تاپ هنوز اثبات نشده است.
- linked worktree داخل Docker به .git میزبان خارج از mount اشاره می‌کند؛ probe اکنون آن را پیش از اجرا با خطای روشن رد می‌کند. clone مستقل لازم است. کپی از shallow runner موجب انتقال ناقص commit شد؛ دستور بعدی clone مستقیم تک‌شاخه از GitHub است. این رفت‌وبرگشت‌ها نقص دستور قبلی بود، نه failure محصول.

### بررسی نزدیک و محدودیت
۱۰ آزمون Node شامل لغو/مالکیت، profile/image و ترتیب probe، و ۹ آزمون Python cache موفق‌اند. cache hit بدون نصب، ایزوله‌بودن کپی، invalidation، انقضا، شکست نصب، snapshot خراب و traversal پوشش دارند. یکی از آزمون‌ها venv واقعی و pip/console-script واقعی را بدون دانلود می‌سازد و پس از restore اجرا می‌کند؛ این fixture وابستگی‌های کامل پروژه را ندارد و زمانش به لپ‌تاپ تعمیم داده نمی‌شود. Ruff lint/format، Bandit با همان -ll -ii پروژه، bash syntax، diff check و بررسی YAML/حفظ gateها انجام شده‌اند. خطای import-order فایل probe قبلی نیز با importlib اصلاح شد تا gate formatter/linter را نشکند.

نتیجه واقعی cold/warm در Docker لپ‌تاپ، pip-audit محیط cached و شش gate نسخه نهایی باقی‌اند. commit با [skip ci] منتشر می‌شود؛ PR draft می‌ماند و merge/deploy انجام نمی‌شود. snapshotهای کلیدهای قدیمی روی دیسک cache باقی می‌مانند؛ rebuild به معنای حذف cacheهای نامرتبط یا داده برنامه نیست. rollback با revert همین تغییر cache و برگشت نصب داخل job ممکن است؛ DB/data migration لازم نیست.

### ثبت زمان
اولین timestamp ثبت‌شده این نوبت 2026-10-16T08:37:03Z UTC؛ فعالیت پیش از آن دقیق ثبت نشده است. تا 08:44:04Z بررسی، پیاده‌سازی و آزمون نزدیک انجام شد (۷ دقیقه و ۱ ثانیه دیواری؛ مدت فعال هر بخش جدا ثبت نشده، فعالیت و انتظار با هم جمع نمی‌شوند). آزمون‌های نزدیک پس از تغییرات مرتبط دوباره اجرا شدند؛ full suite یا شش workflow تکرار نشد. عوامل اتلاف هدف‌گرفته‌شده: نصب تکراری → snapshot مستقل؛ دستور worktree/shallow نامناسب → clone مستقیم؛ زمان نامشخص suite → زمان‌سنجی هر module. انتظار باقی‌مانده دریافت سنجش واقعی Docker است.
