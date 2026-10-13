# US-13.T01 — موجودی فرانت، خط مبنای تغییرناپذیر و رجیستری استخراج

**ثبت:** ۲۰۲۶-۱۰-۱۳**گردآوری قابل‌تکرار T01:****شاهد بررسی‌شده روی اجرای CI پیشین:** [workflow 38418578360](https://github.com/Brotherlouiee/shahab-demo/actions/runs/38418578360)، artifact `us13-t01-original-vs-candidate` (ID 11825860358): هر ۹ جفت PNG (خانه/درباره‌ما/ورود × ۳۹۰/۴۳۰/۱۴۴۰) با script مستقلِ decode RGBA مقایسه شدند، اندازه یکسان و **صفر پیکسل متفاوت** داشتند؛ سپس assertion `Buffer.equals` با tolerance=0 به خود تست افزوده شد و قبولی روی SHA نهایی نیازمند CI تازه است. این خط مبنا فقط guest initial states این ۳ صفحه را پوشش می‌دهد، نه تعامل منو، OTP یا سایر صفحات.

 `.github/workflows/us13-baseline.yml` نسخهٔ منجمد `f5e50da...` را جداگانه با Vite روی 4177 اجرا می‌کند؛ `tests/e2e/us13-baseline-inventory.spec.mjs` با Playwright از home/about/login در سه viewport مرجع و candidate تصویر و boundingBox ثبت می‌کند. این گردآوری **اکنون برای همین ۹ نمونه assertion برابری کامل پیکسل‌ها دارد**؛ خروجی artifact بررسی انسانی/بعدی می‌خواهد و coverage سایر سطرها باز است. آزمون سخت‌گیرانهٔ موجود کارت saved-loan بدون تغییر باقی مانده.

 · **وضعیت:** موجودی و طراحی قرارداد حفاظت ثبت شده؛ **گیت تصویر مستقلِ جامع برای تمام حالت‌ها هنوز کامل نیست؛ آغاز T02 تا تکمیل شاهد همان محدوده مجاز نیست**.

## ۱. منابع الزام‌آور و مرز تسک

- مالک: `Brotherlouiee/shahab-demo`؛ آخرین مبنای تأییدشده هنگام آغاز `main = f5e50da0ea29b7d933a813736a2616169ee9b8f3` (مرج PR #125). این شناسه **مرجع منجمد پیش از هر ریفکتور US-13** است و در T02/T03 نباید از HEAD بعدی به‌عنوان «baseline جدید» جایگزین شود.
- تقدم: قوانین طلایی و `docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md`؛ `docs/TASK_EXECUTION_PROTOCOL.md`؛ `AGENTS.md`؛ `docs/adr/0009-offline-refactor-before-release.md`؛ سند تداوم نسخه ۱۵؛ قرارداد Git/IDE `$safe-git-ide-collaboration`.
- **قبل/بعد از T01:** محصول هیچ تفاوتِ مجازی ندارد. تنها بررسی ساختار، مستندسازی وابستگی و شواهد پیش از ریفکتور. **هیچ استخراج React، انتقال CSS، جابه‌جایی asset، تغییر API/route/state، migration یا deploy در این PR انجام نمی‌شود.**
- داده‌های واقعیِ کاربر، `localStorage` مالک، PostgreSQL و volumeها لمس نمی‌شوند؛ snapshotهای آینده باید دادهٔ مصنوعی و بدون secret داشته باشند.
- محدودیت مهم: این کار از طریق اتصال GitHub انجام می‌شود، نه checkout روی IDE مالک؛ بنابراین **وضعیت فایل‌های ذخیره‌نشده/committed نشدهٔ IDE مالک قابل مشاهده یا تأیید نیست**. قبل از هر اجرای محلی، کاربر/IDE باید `git status` و diff محلی را بررسی کند؛ ممنوعیت overwrite پابرجاست.

## ۲. اثر انگشت مستقلِ source/asset / ابزار

| مورد | مسیر | Git blob SHA در baseline |
| --- | --- | --- |
| Composition اصلی | `src/home page.jsx` (۳۱۷۲ خط، ~۱۳۳ KB) | `8fcc0f31f9f1ea610f5c950d76df5bc59352d69c` |
| CSS سراسری فعال | `src/App.css` (۶۱۴۹ خط، ~۱۲۲ KB) | `f0fe7d22bb5d1dc147f04ee5f6c769166ddaef41` |
| Entry و StrictMode | `src/main.jsx` | `beb229b62d552d7344f8459cad5b4d5ba8a46d96` |
| مرز اثر ناوبری | `src/features/questionnaire/questionnaireRouteMap.mjs` | `08e9c01019657a392643bd0962cf37a4a011b0b2` |
| کلاینت هویت | `src/features/account/profileClient.mjs` | `433a7b70c2db45071bb7437b2543f3aa4a50de89` |
| حافظهٔ حساب در مرورگر | `src/features/account/accountBrowserState.mjs` | `3d591015619db6a6413f78e4022f828e1f88b8e6` |
| نمایش نشان‌شده‌ها | `src/features/account/savedLoansPresentation.mjs` | `15f1ac6c74291a58ce2ea6fb0b3ee0c5d72858a4` |
| کارت مشترک نتیجه | `src/features/recommendation/ui/LoanResultsScreen.jsx` | `1d585674e4da97194f7f9e85a8e2274d9b8f94cc` |
| جزئیات | `src/features/loan-details/LoanDetailsScreen.jsx` | `db55f6403a0efffff83750ffcc888dc3d7db829f` |
| Test runner | `playwright.config.mjs` | `6ca4564e4c3e92ae6cd5669bbc00c3f268d34a41` |
| Visual oracle موجود | `tests/e2e/bookmarks-visual-preservation.spec.mjs` | `e138676ac982ca741cce968e4feb2a951476ed50` |
| Logo اصلی | `assets/shahab-logo.svg` | `01af7c2899c74fa307d013a26a45707c2b8d6bc4` |
| نشان‌کردن | `assets/book-saved.svg` | `392ea24f0408d70614802d1fbc7781cd359b460a` |
| هشدار تأیید | `assets/danger.svg` | `11eac57674644966ff7928b311137a1bab47c526` |

این‌ها **Git object SHA** هستند، نه هش محاسبه‌شده از فایل محلی؛ هر خواننده باید آنها را روی ref ثابت baseline کنترل کند. برای تصاویر/فونت‌های تحت پوشش مسیرهای دیگر، tree ثابت `f5e50da...` مرجع بایت‌به‌بایت است؛ هیچ asset نباید هنگام ریفکتور بهینه/بازفشرده/تبدیل شود.

## ۳. نقشهٔ ماژول‌های واقعی و مالکیتِ فعلی

`src/main.jsx`، React `StrictMode` را فعال و از `src/home page.jsx` مؤلفهٔ `HomePage` را mount می‌کند و `src/App.css` را فقط در entry وارد می‌کند. **این import مرکزی و ترتیب cascade نباید عوض شود.**

| ناحیه | کد فعال در `src/home page.jsx` | مرز و حساسیت |
| --- | --- | --- |
| Navigation / layout | `BrandMark` ~103، `Nav` ~447، `SidebarIcon` ~458، `UserSidebar` ~535، `QuestionnaireHeader` ~756، `AccountHeader` ~781 | shared header/sidebar، route و overlay؛ menu، Back، logout confirm و focus باید حفظ شوند |
| Login / OTP | `LoginScreen` ~569، format/validation ~395–445، `profileClient.mjs` | phone/OTP، countdown، session/cookie، duplicate request، invalid/expired code؛ **جداسازی فقط بعد از تست state/اثرها** |
| Questionnaire + personal stage | `getQuestionnaireRouteState` ~199، `QuestionnaireScreen` ~1052–2614 | **بزرگ‌ترین و پرخطرترین بلوک (~۱۵۶۳ خط)**؛ session ID و پاسخ‌ها در React instance، URLهای canonical، route popstate، local-only cache profile؛ تقسیم ریز پیش از هر جابه‌جایی |
| Loan compare | `LoanCompareScreen` ~795، `LoanComparisonResultCard` ~898، `LoanComparisonResultScreen` ~911 | دادهٔ API وام، انتخاب/بازگشت، صفحهٔ مستقل نتیجه، درصد RTL؛ استفادهٔ دوباره از `LoanComparisonCard` و `BankIdentity` |
| AI explanation | `LoanAiAnalysisScreen` ~1010 | فقط توضیح واقعی provider؛ submit disabled؛ هر تغییر محتوای توضیح یا فعال‌سازی دکمه ممنوع |
| Home marketing | `Hero` ~2615، `CardView` ~2703، `StatsMarquee` ~2769، `Features` ~2781، `Footer` ~2817 | ترتیب DOM، animation، لوگو و external images، breakpoint و کلیک‌ها حفظ شوند |
| Account and profile | `ProfileDropdown` ~2854، `AccountPage` ~2861 | read/persist profile، edit dirty state، avatar <=100KB، validation و POST؛ error/confirm/load |
| About | `AboutPage` ~2890 | محتوای فارسی و تصویر /about-us-payment.png باید بایت‌به‌بایت/متن دقیق حفظ شود |
| Saved loans | `SavedLoansPage` ~2894؛ مصرف‌کنندهٔ `LoanResultsScreen` | `refreshSavedLoans`، listener `shahab:saved-loans` و focus، mount/unmount و status error/empty؛ مرورگر کارت 390/1440 |
| Recommendation history | `RecommendationHistoryPage` ~2911 | pagination، hide(confirm/cancel)، local date timeZone، unauthorized, saved/archived lineage |
| App composition | `HomePage` ~2944 تا انتها | **state و handlerهای ناوبری بالادستی**، session initialization، `popstate`، conditional mount و مسیرها؛ آخرین و حساس‌ترین extraction |

کدهای feature موجود در `src/features/recommendation/`، `src/features/loan-details/`، `src/features/account/` و `src/features/questionnaire/` **نباید دوباره ساخته شوند**. ساختار `frontend/src/` طبق `docs/architecture/module-map.md` فعلاً هدف مهاجرت و نه entry فعال است؛ تغییر entry به آن **خارج از scope** است.

## ۴. مسیرها × وضعیت‌ها × آزمونِ موجود و شکاف‌ها

| دسته | URLهای واقعی | fixture / state الزامی | آزمون موجود | شاهد تصویری مستقل و اقدام باقیمانده پیش از extraction |
| --- | --- | --- | --- | --- |
| Home/nav/about | `/`, `/about` | guest، menu open/close، responsive، navigation/back، scroll | `initial-and-questionnaire-loading.spec.mjs` تا حد صفحهٔ اول | **شکاف:** baseline تصویری کامل 390،430،1440 و دو سوی breakpointها برای home/about/sidebar ثبت و با محیط یکسان مقایسه شود |
| OTP login | `/login`, `/login/otp` | input فارسی/لاتین، timer، invalid/success، back/refresh، error, auth | `personal-info-access.spec.mjs`, `profile-persistence.spec.mjs` و real API suite | **شکاف:** عکس و rect فرم/keyboard focus/errors با fixture ثابت ثبت شود؛ تست مرورگر real-API صرفاً جایگزین عکس نیست |
| Questionnaire | `/question/1` تا `/question/12`, `/personal-info`, `/verify-code`, `/analysis` | answer selection، saving/error، reload/back، initial skeleton، loading، auth transition، canonical URL map | `questionnaire-route-map.spec.mjs`, `questionnaire-session-flow.spec.mjs`, `us-09-t076-question-controls.spec.mjs`, `initial-and-questionnaire-loading.spec.mjs` | **شکاف:** screenshot state+responsive coverage و network count برای هر زیرمسئولیت مرتبط، خصوصاً ۳۶۰/۳۹۰/۴۳۰/۷۰۰/۹۰۰ |
| Result/detail | `/loan-results`, `/loan-details?loanId=...`, `/loan-request` | ranked/low/review، no-session، skeleton/error، detail refresh/back و API 404 | `recommendation-result-journey.spec.mjs`, `loan-details.spec.mjs`, `live-recommendation-route.spec.mjs` | شواهد نتیجه/جزئیات موجودند ولی snapshot baseline برای **هر حالت/viewport تحت اثر** باید قبل از T02 آن قسمت کامل شود |
| Compare/explain | `/compare-loans`, `/compare-result`, `/ai-analysis` | انتخاب ۲ وام واقعی، بازگشت با checkbox حفظ‌شده، detail facts، provider disabled | `recommendation-result-journey.spec.mjs`, `loan-details.spec.mjs` | **شکاف:** geometry، popup/select/focus و screenshot پیش/پس در هر viewport |
| Profile | `/profile` | session valid/invalid، read/edit/save/error، avatar/upload، dropdown | `profile-persistence.spec.mjs`, `personal-info-access.spec.mjs` | **شکاف:** baseline مستقل برای dropdown، edited/unsaved و modal/RTL |
| Saved loans | `/saved-loans`, `/loan-details?loanId=...&from=saved` (query مطابق helper واقعی کنترل شود) | empty/populated, waiting/error, toggle, focus-refresh/logout | `saved-loans.spec.mjs`, `bookmarks-visual-preservation.spec.mjs` | **موجود:** baseline پیش از F با Chromium و 390/1440 برای کارت و empty artwork؛ **شکاف:** خط مبنای جامع 430 و page layout/overlay و سایر حالت‌ها |
| History | `/recommendation-history`, `/recommendation-history/:id`, detail `from=history` | empty/error/paginated، hide cancel/yes، back/refresh و عدم نمایش داده حساب دیگر | `saved-loans.spec.mjs` و suiteهای profile مرتبط (پوشش اختصاصی باید با تست مرورگر اثبات شود) | **شکاف:** baseline حالت‌های تاریخ/حذف/کارت برای 390/430/1440، بررسی datetime fixture |

**برچسب شاهد:** «وجود فایل spec» اثبات نمی‌کند همهٔ سطرها و حالت‌های این ماتریس تحت تست‌اند. هر زیرتسک باید **نام test case، screenshot مستقل یا artifact معتبر، URL/viewport/state، fixture و شمارهٔ CI** را به این جدول یا سند فرزند بیفزاید؛ جای خالی = پوشش تأییدنشده، نه Pass.

### پیکربندی خط مبنا برای اجرای واقعی قبل از T02

- baselineِ مستقل: `git worktree add --detach <new-path> f5e50da0ea29b7d933a813736a2616169ee9b8f3`، بدون overwrite workspace مالک؛ یا runner checkout دوم در CI به همین SHA. candidate روی head کوچکِ T02/T03.
- `npm ci` مطابق lockfile، همان Node 22 و Playwright Chromium نسخهٔ قفل‌شده در هر دو؛ Linux runner `ubuntu-24.04`؛ در هر دو `deviceScaleFactor=1`، locale/clock/viewport ثابت، font آماده، image complete، animation تنها طبق قرارداد reproducible و network mocking یکسان. تصاویر باید در artifact با baseline SHA و candidate SHA ذخیره شوند.
- viewports **حداقل** `360×800`, `390×844`, `420×900` (یک سوی breakpoint 420)، `430×932`، `700×900`، `701×900`، `900×900`، `901×900` و `1440×900` **برای مسیرهایی که selector مشترکِ تحت اثر دارند**. `38rem` نیز در font-size واقعی تست شده و نباید بدون بررسی به px حدس زده شود.
- comparator: عنصر/صفحهٔ مرتبط + bounding box/computed style + تعامل/متن/asset + request sequence. **هر pixel diff واقعی blocker**؛ نوسان rasterization گوشه فقط با artifact raw/baseline-on-same-source evidence، نه threshold/mask/rebaseline حل می‌شود. نمونهٔ CI محافظت موجود: `tests/e2e/bookmarks-visual-preservation.spec.mjs`، که مستقل از baseline قبل F بوده و اکنون raster flags تثبیت‌شده دارد؛ این **کل frontend را پوشش نمی‌دهد**.
- آینده: هر snapshot baseline باید **قبل از شروع آن زوج استخراج، روی نسخهٔ پذیرفته‌شدهٔ قبل از ریفکتور ثبت و سبز** شود؛ برای زیرمجموعهٔ نیازمند ابزار یا state تازه، در یک PR test-only جداگانه characterization افزوده و CI سبز شود. baseline باید در برابر regression عمدی fail شود؛ هیچ تست بدون شاهد شکست‌پذیری کافی نیست.

## ۵. خطرهای CSS و ترتیب cascade

`src/App.css` یک stylesheet فعال با **۶۱۴۹ خط** و selectorهای مشترک `.hp-*` است؛ بررسی مقدماتی `@media`ها `max-width: 900px`، `700px`، `420px`، `360px` و `38rem` را پیدا کرده است. **این inventory متن است، نه گواه computed-style اختصاصی برای هر مسیر.**

- ترتیب اصلی stylesheet و specificity/cascade، pseudo-classهای `:focus`، `:hover`، `:visited`، state classهای `.is-*`، z-index، overflow، @keyframes و RTL/positioning باید قبل/بعد **برابر** بمانند.
- **T02.nn اصلاً CSS جابه‌جا نمی‌کند.** T03.nn فقط selectorهای محدود همان بخش را، بعد از دریافت شاهد selector-consumer graph و import order، منتقل می‌کند؛ حتی اصلاح ترتیب ظاهراً تکراری یا متداخل ممنوع است.
- وجود یک selector در چند صفحه یا ترکیب state، دلیل کافی برای جداکردن آن نیست. shared/global CSS ممکن است **عمداً در App.css بماند**؛ «ماژولار کردن» مجوز تغییر behavior یا override نیست.
- برای استخراج دقیق CSS: پیش از T03.nn با Playwright `getComputedStyle`، geometry و screenshot در stateهای نمایان/پنهان/keyboard/open/scroll و هم‌صفحه‌های consumer اندازه‌گیری شود؛ فقط پس از سبزشدن این شواهد یک قانون منتقل شود.

## ۶. رجیستری پیشنهادی ریزگام‌های استخراج؛ **نه مجوز اجرا**

**قرارداد هر سطر:** `T02.nn` تنها پس از مرج `T01` و تکمیل baseline مربوط، سپس `T03.nn` فقط بعد از مرج همان T02.nn؛ هر مرحله از main جدید، یک PR کوچک، با commit فارسی، تست/visual/network gate جدا، rollback. فایل منبع همهٔ استخراج‌ها `src/home page.jsx` است؛ هدف مسیر پیشنهادی است و قبل از create باید با import graph و محافظت نام/identity بازبینی شود.

| جفت | مسئولیت و محدودهٔ خط فعلی | مقصد پیشنهادی/مصرف‌کننده CSS | مالک state و مانع شروع |
| --- | --- | --- | --- |
| `02.01 / 03.01` | `AboutPage` ~2890–2892 | `src/features/about/AboutPage.jsx`؛ `.hp-about-*`, `.hp-account-*` shared | stateless؛ **اول baseline تصویر/متن درباره ما و header mobile/desktop، اثبات عدم تأثیر shared header** |
| `02.02 / 03.02` | `Features` ~2781 و footer در PR مجزا اگر بزرگ | `src/features/home/Features.jsx`; `.hp-feature-*` | بدون state اصلی؛ scroll/breakpoint و ترتیب section ثابت |
| `02.03 / 03.03` | `Footer` ~2817 | `src/features/home/Footer.jsx`; `.hp-footer-*` | وابستگی link/RTL و shared/global |
| `02.04 / 03.04` | `StatsMarquee` ~2769 | `src/features/home/StatsMarquee.jsx`; `.hp-stats-*` | animation timing و layout دقیق |
| `02.05 / 03.05` | `CardView` ~2703 | `src/features/home/CardView.jsx`; `.hp-card-*` | props و card variants / hover |
| `02.06 / 03.06` | `Hero` ~2615 | `src/features/home/Hero.jsx`; `.hp-hero-*` | props navigation + imported assets؛ external image loading و state |
| `02.07 / 03.07` | `AccountHeader` ~781، در صورت امکان خودِ header مستقل | `src/shared/AccountHeader.jsx`; `.hp-account-header` / global | shared across ۴+ صفحات؛ سخت‌ترین CSS consumer. **اگر selector shared غیرقابل انتقال امن بود CSS را در App.css نگه دارید؛ T03 با سند no-move و gate معتبر بسته شود** |
| `02.08 / 03.08` | `ProfileDropdown` ~2854–2857 | `src/features/account/ui/ProfileDropdown.jsx`; `.hp-personal-dropdown-*` | local open/blur/focus؛ نیازمند interaction regression |
| `02.09 / 03.09` | `AccountPage` ~2861–2888 | `src/features/account/ui/AccountPage.jsx`; `.hp-account-*` | dirty/profile fetch/save/upload/error؛ isolation با mock و real API |
| `02.10 / 03.10` | `SavedLoansPage` ~2894–2909 | `src/features/account/ui/SavedLoansPage.jsx`; `.hp-saved-*` | mount/focus/listener/lifecycle؛ visual existing + cross-account |
| `02.11 / 03.11` | `RecommendationHistoryPage` ~2911–2942 | `src/features/account/ui/RecommendationHistoryPage.jsx`; `.hp-recommendation-history-*` | async fetch/error/cursor/hide confirmation |
| `02.12 / 03.12` | `Nav` ~447 و `SidebarIcon` ~458 در صورت کم‌حجم بودن | `src/shared/Nav.jsx` / `SidebarIcon.jsx`; `.hp-nav-`, `.hp-sidebar-` | shared semantic click/back; separate further if needed |
| `02.13 / 03.13` | `UserSidebar` ~535–560 | `src/features/navigation/UserSidebar.jsx`; `.hp-sidebar-*` | popup, logout yes/no, event ordering |
| `02.14 / 03.14` | `LoginScreen` ~569–755 | `src/features/account/ui/LoginScreen.jsx`; `.hp-login-*` | ۱۲۰ ثانیه countdown/session; split smaller BEFORE extraction if necessary |
| `02.15 / 03.15` | `LoanAiAnalysisScreen` ~1010–1050 | `src/features/recommendation/ui/LoanAiAnalysisScreen.jsx`; `.hp-ai-*` | disabled provider; no new action |
| `02.16 / 03.16` | `LoanCompareScreen` ~795–896 | `src/features/recommendation/ui/LoanCompareScreen.jsx`; `.hp-compare-*` | selected IDs owner stays parent, filter/card shared |
| `02.17 / 03.17` | `LoanComparisonResultCard` ~898–910 | `src/features/recommendation/ui/LoanComparisonResultCard.jsx`; match shared card CSS | percentage RTL/card measurements, BankIdentity |
| `02.18 / 03.18` | `LoanComparisonResultScreen` ~911–1009 | `src/features/recommendation/ui/LoanComparisonResultScreen.jsx`; `.hp-compare-*` | API detail requests, back and retained selection |
| `02.19 / 03.19` | `QuestionnaireScreen` ~1052–2614 — **فقط پس از ساخت registry جزئی جدید** | بخش‌های درونی به `src/features/questionnaire/ui/`؛ **هر تغییر یک مسئولیت کوچک، نه یک استخراج ۱۵۰۰ خطی** | React state/effect/order/route/session integrity؛ **فاز تکمیلی قبل از آن باید این ردیف را به چند ردیف کوچک تبدیل کند؛ انتقال یک‌باره ممنوع** |
| `02.20 / 03.20` | `HomePage` ~2944–3172 composition/root | فقط در انتها با route/state diagrams، و **ممکن است در `home page.jsx` باقی بماند** | boundary root، history, StrictMode, conditional mount; safe no-op extraction preferred |

**نکتهٔ ضروری:** این رجیستری **پیشنهاد با identifier ثابت پیش‌نویس** است؛ برای هر سطر باید قبل از شروع T02: target file exact، allowlist، imports و dependent hooks، selectors + shared consumers، suite commands، verified baseline artifact/URL و root ownership ثبت شود. در صورت مشاهدهٔ shared dependency یا ریسک غیرقابل اندازه‌گیری، سطر شکسته یا scope کمتر می‌شود؛ تغییر نام/تقسیم با checkpoint مصوب جدید ثبت شود. هیچ T02/T03 به‌طور خودکار تأیید نیست.

## ۷. دروازه‌های پذیرش و اثبات صادقانه

| گیت | آنچه اکنون قابل اثبات است | وضعیت |
| --- | --- | --- |
| تأیید ref ثابت، Git hashes و inventory فعال | فایل‌ها و tree از GitHub روی `main=f5e50da...` مشاهده و ثبت شدند | ثبت‌شده |
| نقشهٔ route/state/component/API و خطر CSS | از کد واقعی و suite inventory تهیه شده | ثبت‌شده، جزئیات در هر subtask باید کامل شود |
| baseline تصویریِ مستقل کامل همهٔ route/state/viewportها | فایل تصویری برای همهٔ ماتریس هنوز در این PR تولید نشده؛ existing saved-loan pre-F و CI فقط محدودهٔ خودش | **باز؛ قبل از T02 هر جزء اجباری** |
| baseline interaction/network برای همهٔ route/state | suiteهای موجود برخی رفتارها را می‌پوشانند ولی جدول case-level کامل نیست | **باز؛ قبل از T02 هر جزء اجباری** |
| اجرای suite‌های موجود روی آخرین SHA این PR | CI پنج job باید روی head نهایی PR پاس شوند | تا اعلام run نتیجه باز |
| عدم تغییر runtime/CSS/asset/API/data | diff فقط اسناد، checkpoint، CHANGELOG و سه فایل test/CI مربوط به گردآوری baseline باشد | تأیید با changed files و PR diff |
| سند تداوم | طبق مصوبه **فقط پایان User Story**؛ این تسک T01 پایان US-13 نیست | تغییر ندارد |

**خروجیِ درست T01:** نقشهٔ قابل اتکا و baseline SHA منجمد، رجیستری ریزگام‌ها و کشف شکاف‌های واقعی؛ **نه** مجوز ریفکتور بدون پوشش آزمون همان بخش. در صورت باقی‌ماندن شاهدِ اجباری، T01 را «داده/موجودی تکمیل، gate تصویری در حال تکمیل» ثبت کنید و از عنوان Done قطعی تا پذیرش همهٔ موارد پرهیز کنید.
