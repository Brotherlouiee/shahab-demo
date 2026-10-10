# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows Semantic Versioning when production releases begin.

## [Unreleased]

### Changed

- **Owner-directed continuity refresh (2026-10-10):** Version 12 reconciles the handoff with merged PR #93 and successful main CI, records profile/session/history migrations and remaining US-09.T07 deployment gate, and replaces obsolete current/next-task statements. Documentation only; no runtime, data, schema or design changes.


### Fixed

- **US-09.T079 follow-up:** A signed-in user can now hide a recommendation-history card through a centered warning confirmation. The owner-scoped DELETE API records `hidden_at` instead of deleting the immutable run, items or reasons; hidden runs are absent from that user's list and detail route while remaining available for database administration. The history list uses the same no-menu account header as About and Saved Loans.

- **US-09.T079 follow-up:** Recommendation-history authorization now survives a browser refresh through an HttpOnly, same-site server session cookie; no credential is persisted in browser storage. The browser that creates a questionnaire receives a separate HttpOnly proof cookie, so a session ID alone cannot be attached to an account; the database then atomically binds the verified owner before its immutable history snapshot is written. History pagination uses a stable newest-first cursor, a failed list remains an error rather than an empty state, and the successful empty state reuses the existing saved-loans artwork. Historical results retain the original result controls and no longer alter the result presentation.

- **US-09.T079:** Authenticated recommendation responses are persisted once per questionnaire session as immutable, owner-scoped PostgreSQL history. The authenticated menu now links to paginated recommendation history; cards show the server-created Tehran date/time and ranked-result count. Reopening a run uses the existing result UI without rescoring, keeps all three partitions and returns from loan details to that history entry. Anonymous sessions remain transient and the 30-minute questionnaire retention policy is unchanged.

- **US-09.T078:** The option-card border on `/question/2` is 30% shorter (117px to 82px at the supported mobile viewport), with no change to options, typography, actions, routes, or other questionnaire cards.

- **US-09.T077:** The supplied vector Shahab mark replaces the previous application logo everywhere it is rendered. Existing logo elements, dimensions, layout classes, spacing and page behaviour are unchanged.

- **US-09.T076:** Questionnaire cards now use their content height with an exact 28px inset above the first option and below the last option, while their existing option rhythm is preserved; questionnaire navigation rows sit exactly 28px below each question card and 28px above the end of the page, without artificial empty page height; the home amount selector uses the shared 8px chevron geometry; and the unavailable readiness and AI-analysis actions are visibly disabled in grey.

- **US-09.T075:** Saved Loans now renders the supplied empty-state artwork when no loan is saved, hides filters for zero or one saved loan, preserves `/saved-loans` as the detail return target, aligns the header inset, and gives the document link the same icon as result cards. No API, scoring, data, or storage-policy change.

- **US-09.T074:** صفحهٔ home فقط هدر، منوی همبرگری و بخش ابتداییِ درخواست وام را نگه می‌دارد. بخش‌های آمار، ویژگی‌ها، CTA و footer از رندر صفحهٔ خانه حذف شدند؛ مسیر پرسشنامه، OTP، API، داده‌های PUBLISHED و scoring تغییری ندارند.

- Verified first mock-OTP login now creates the database profile; subsequent logins preserve existing data. Personal-info updates that same profile. Failed creation does not issue access.

### Security

- **US-09.T072:** Replace unprotected phone lookup with owned /profiles/me; writes require server capability. Explicit local/test mock OTP has expiry, quotas and revocation, and is blocked in staging/production. ADR 0010; no real SMS or production authentication.

### Fixed

- **US-09.T072:** Persist personal-info after development verification before analysis; show retryable storage errors, preserve draft and existing avatar/gender, and retain eleven-digit phones. Existing schema reused; no scoring, published loan data or design changes.


### Fixed

- **US-09.T06Z:** دکمهٔ ورود از home حذف شد و فقط منوی مهمان آن را نشان می‌دهد. پس از تکمیل OTP نمایشی، منوی کوتاه کاربر با پروفایل، سوابق درخواست، وام‌های نشان‌شده، درباره ما و خروج نمایش داده می‌شود؛ خروج profile محلی را پاک می‌کند. این تغییر UI-only است و provider احراز هویت، API، session پرسشنامه، داده، scoring، D-005، migration و deploy را تغییر نمی‌دهد.

- **US-09.T06X:** stylesheet فونت دیگر نخستین paint را مسدود نمی‌کند و تصویرهای پایینِ home lazy/async decode می‌شوند. fallback document و Skeletonهای React برای home، پرسشنامه، نتایج/مقایسه و جزئیات با هندسهٔ همان صفحه نمایش داده می‌شوند؛ هیچ داده، API، D-005، scoring، migration یا استقراری تغییر نکرده است.

- **US-09.T06W:** fallback نخستین paint پس از ۵۰ms برای home/refresh افزوده شد، انتظار ثبت پاسخ پرسشنامه Skeleton همان ناحیه را نشان می‌دهد و دکمهٔ «مقایسه کن» با یک انتخاب خاکستری و غیرقابل‌کلیک است. داده، API، D-005، scoring، migration و استقرار تغییری نکرده‌اند.

- **US-09.T06V:** استاندارد Skeleton با تأخیر ۵۰ms برای loading داده در نتیجه، جزئیات و مقایسه اضافه شد؛ متن‌های loading جایگزین شدند. null monetary value دیگر با «تومان» نمایش داده نمی‌شود؛ کارت‌های comparison به جزئیات همان وام می‌روند، ترتیب انتخاب از بیشترین تطابق است و دکمهٔ مقایسه تا دو انتخاب disabled می‌ماند. داده، API، D-005، scoring، retention و استقرار تغییری نکرده‌اند.

- **US-09.T06U:** کاتالوگ مرجع پرسشنامه در lifecycle یک‌بار آماده می‌شود و پاسخ‌های بعدی دیگر آن را query/commit نمی‌کنند. جزئیات یک وام با شناسهٔ همان loan و predicateهای PUBLISHED از PostgreSQL خوانده می‌شود؛ endpoint دیگر کل serving catalogue را برای یافتن یک وام scan نمی‌کند. قرارداد API، داده، D-005، scoring، retention، Redis fallback، UI و استقرار تغییری نکرده‌اند.

- **US-09.T06T:** FastAPI اکنون engine و session factory SQLAlchemy را یک‌بار در lifecycle می‌سازد و فقط در shutdown dispose می‌کند. هر request یک Session مستقل و بسته‌شونده می‌گیرد؛ timing ایمن development فقط endpoint ثابت، status و مدت را log می‌کند. PostgreSQL، Redis fallback، retention، دادهٔ PUBLISHED، D-005، scoring و قرارداد API تغییری نکرده‌اند.

- **Local development:** Compose now publishes Vite on `5173`, avoiding the
  Windows-reserved `4173` range. FastAPI mounts the local source and reloads
  changes under `backend/`, so normal backend edits no longer require an image
  rebuild. No production runtime, API contract, data, or recommendation logic
  changed.

- **US-09.T06S:** endpoint توصیه یک snapshot تأییدشده را فقط یک‌بار می‌خواند و چهار fact واقعیِ کارت را از همان serving catalogue در پاسخ برمی‌گرداند. کارت نتیجه با این خلاصهٔ server-owned دیگر پس از spinner برای هر وام درخواست جزئیات جداگانه نمی‌فرستد؛ شروط کامل فقط در صفحهٔ جزئیات خوانده می‌شوند. داده، score، ضرایب D-005، threshold، session و استقرار تغییر نکرده‌اند.

### Security

- **US-09.T06R:** زنجیرهٔ توسعهٔ Vite به نسخهٔ pin‌شدهٔ امن `8.3.3` ارتقا یافت؛ lockfile نسخه‌های امن PostCSS، nanoid و source-map-js را ثبت می‌کند. `npm audit` نهایی صفر آسیب‌پذیری گزارش می‌دهد. UI، API، داده و استقرار تغییری نکرده‌اند.

### Added

- **US-09.T06Y:** پوشهٔ `docs/runbook/` و runbook استقرار محیط پایدار اضافه شد؛ مسیر PostgreSQL دائمی، publication دادهٔ تأییدشده، FastAPI HTTPS، Netlify، آزمون URL واقعی، restart، backup و rollback را ثبت می‌کند. این تغییر هیچ سرور، secret، داده، API یا deployment واقعی ایجاد نکرده است.

- **US-09.T06Q:** fallback static صفحهٔ mock از `index.html` حذف شد؛ `#root` پیش از mount React خالی است و آزمون واحد و E2E refresh، نبود متن‌های صفحهٔ جعلی را قفل می‌کنند. UI فعال، داده، API، score و استقرار تغییری نکردند.

- **US-09.T06P:** صفحهٔ mock قدیمیِ خارج از runtime حذف شد تا refresh هرگز UI ساختگی نمایش ندهد؛ قاب CTA جزئیات با ارتفاع صریح ۱۱۷px و فاصله‌های قطعی ۳۵/۴۸/۳۴px ساخته و در E2E اندازه‌گیری شد.


- **US-09.T06O:** انقضای session پرسشنامه بی‌صدا با ساخت session تازه و replay پاسخ‌های موجود بازیابی می‌شود؛ کارت «نشست منقضی» نمایش داده نمی‌شود. درخواست‌های هم‌زمان جزئیات یک وام نیز در همان tab deduplicate و cache می‌شوند. قاب CTA جزئیات دارای ۳۵px فاصلهٔ بالا و ۳۴px فاصلهٔ پایینِ نمونهٔ تأییدشده است؛ API، داده، score و استقرار تغییری نکرده‌اند.

- **US-09.T06N:** دکمهٔ تحلیلِ جزئیات اکنون یک toolbar ثابتِ متصل به پایین viewport است و برای آخرین شرط وام فضای مستقل رزرو می‌شود. logoهای مخصوص spinner فقط در همان صفحه بارگیری می‌شوند؛ درخواست واقعی توصیه هم‌زمان با شمارش پنج‌ثانیه‌ای شروع می‌شود، فقط یک درخواست در پرواز می‌ماند و خطا فقط با اقدام صریح کاربر retry می‌شود. دادهٔ PUBLISHED، API، score، session policy و استقرار تغییری نکرده‌اند.

- **US-09.T06L:** کنترل ذخیرهٔ وام اکنون با assetهای تأییدشدهٔ outline/fill قابل toggle است؛ پیام موفقیتِ موقت بالای همان کارت می‌آید. دکمهٔ «تحلیل با هوش مصنوعی» به انتهای جزئیات اضافه شد، state فعال نتیجه در history همان browser برای refresh-detail→Back حفظ می‌شود، دو قانون انتخاب مقایسه اعمال شد و asset بانک ملی با پس‌زمینهٔ شفاف و hash جدید ثبت گردید. API، دادهٔ وام، scoring، provider خارجی و استقرار تغییر نکرده‌اند.

- **US-09.T06J:** متن‌های قابل‌مشاهدهٔ وام در نتیجه/جزئیات/مقایسه رقم فارسی می‌گیرند؛ border و درصد تطابق کارت فقط بر پایهٔ همان درصدِ server-owned در پنج بازهٔ مصوب رنگ می‌گیرند؛ دکمهٔ /compare-result «تحلیل با هوش مصنوعی» است؛ و SVG کنترل‌شدهٔ بانک ملی با encoding قابل‌رندر و hash جدید ثبت شد. داده، API، score، threshold، D-005 و استقرار تغییر نکرده‌اند.
- **US-09.T06I questionnaire layout alignment:** `/personal-info` and `/verify-code` now use the same responsive content rail, stage-board dimensions, actions, and symmetric side margins as the preceding questionnaire pages. Browser geometry tests cover desktop and mobile. This is UI-only and does not change profile data handling, OTP, APIs, or recommendation logic.
- **US-09.T06I follow-up:** پاسخ نهایی S13 دیگر صفحه‌های اطلاعات شخصی و OTP را skip نمی‌کند؛ flow کامل پرسشنامه به `/personal-info`، سپس `/verify-code` و spinner پنج‌ثانیه‌ای می‌رسد و فقط پس از آن نتیجهٔ واقعی/fail-closed را درخواست می‌کند.
- **US-09.T06I:** بازگردانی محافظه‌کارانهٔ جریان UI اطلاعات شخصی، کد OTP نمایشی و spinner پنج‌ثانیه‌ای؛ کد ثابت فقط پروفایل محلی را برای منوی همبرگری نگه می‌دارد و پس از پایان به همان نتایج fail-closed/واقعی می‌رود. دادهٔ وام، API، scoring، migration، provider و deployment تغییر نکرده‌اند.
- US-09.T06H comparison-card correction: فقط row «تطابق با وضعیت مشتری» در layout جابه‌جا شد؛ checkbox دست‌نخورده ماند، ارتفاع کارت انتخاب با کارت نتیجهٔ مقایسه برابر شد و center متن/checkbox با E2E تا ۱px هم‌راستا کنترل می‌شود.
- US-09.T06H comparison return follow-up: بازگشت از نتیجهٔ مقایسه، checkbox وام‌های واقعیِ انتخاب‌شده را از حافظهٔ همان tab سبز نگه می‌دارد؛ URL و web storage برای این انتخاب‌ها استفاده نمی‌شوند و Playwright مسیر بازگشت را کنترل می‌کند.
- US-09.T06H compare-result alignment follow-up: عنوان وام در کارت نتیجهٔ مقایسه اکنون از همان title row کارت‌های دیگر استفاده می‌کند؛ آزمون browser برابری مختصات عمودی آن با کارت نتایج را تا تلرانس ۱px کنترل می‌کند.
- US-09.T06H typography follow-up: عنوان وام در همهٔ کارت‌ها ۲۰٪ ارتفاع خودش بالاتر رفت، ردیف «تطابق با وضعیت مشتری» در انتخاب مقایسه ۲۰٪ پایین‌تر قرار گرفت و عدد/نماد درصد تطابق بدون تغییر نرخ بهرهٔ اعلامی ۲۰٪ بزرگ‌تر شد؛ Playwright نسبت‌های واقعی geometry و font را در desktop/mobile کنترل می‌کند.
- US-09.T06H follow-up: نام کامل بانک بدون ellipsis و هم‌راستا با logo نمایش داده می‌شود؛ بودجهٔ عنوان وام، عبارت چهارکلمه‌ای مرجع را کامل نگه می‌دارد و فقط عنوان بلندتر را کوتاه می‌کند؛ آخرین کارت نتیجهٔ مقایسه نیز حداقل ۲۰px از دکمهٔ ثابت فاصله دارد. تغییر فقط UI/test/docs است و داده، API، migration و scoring را تغییر نمی‌دهد.
- US-09.T06H follow-up: نام بانک و عنوان وام در همهٔ کارت‌ها تک‌خطی شدند، checkbox مقایسه در راست ثابت شد، برای نوار ثابتِ مقایسه فضای scroll رزرو شد و stacking/overflow فیلترها بدون workaround قطع pointer اصلاح شد؛ تست هندسی و screenshot موبایل/دسکتاپ با ۱۰ وام افزوده شد. داده، API، migration و scoring تغییر نکردند.
- US-09.T06H: یک component مشترک هویت بانک با box ثابت logo، نام مستقل و عنوان مستقل برای همهٔ کارت‌های نتیجه، مقایسه و جزئیات؛ بدون تغییر داده/API/migration یا scoring.
- US-09.T06F: نگهداری ۲۹ SVG تأییدشدهٔ بانک در assetهای کنترل‌شده، ثبت key/hash در serving facts و نمایش از مسیر پایدار برنامه.
- US-09.T06G: مسیرهای URL-safe برای SVGها، نمایش RTL پایدارِ درصد و کنترل browser برای هر فیلتر.


### Fixed

- **US-09.T06K:** On `/loan-results`, bank choices now scroll after four bank names, the existing server-supplied low-compatibility partition is presented from its highest displayed score to lowest, and every card has a tab-local save bookmark with a two-second `#BFFFE9` confirmation. The disabled header CTA now reads «بررسی آمادگی دریافت وام». No loan data, API contract, score, threshold, engine ranking or deployment behavior changed.

- **US-09.T06G follow-up:** Decoded the controlled bank-logo payloads into renderable SVG bytes, made each internal filename/hash content-addressed, restored logos on comparison-result cards, and enforced the Persian RTL rule that `٪` renders visually to the left of its number (including «نرخ بهره اعلامی»), with browser geometry assertions for result, detail and comparison views.

- **Local full-stack development:** Added a same-origin Vite `/api/v1` proxy,
  Compose-managed frontend/API readiness ordering, packaged runtime contracts, an
  explicit read-only/operator catalogue workflow, focused proxy and opt-in live
  browser tests, and safe local startup/troubleshooting documentation. The host UI
  uses port 4173 to avoid common Windows exclusions. No schema, migration, source
  data, credential, or production deployment behavior changed.

### Added

- **US-09.T06C:** Corrected result-card parity and mobile overflow, Persian number/percent display, centered detail link, safe bank-logo rendering, and the real comparison-route card dependency. No recommendation rule, data import, provider workflow, deployment or continuity checkpoint changed.

- **US-09.T06B:** Extracted the active loan-result and loan-detail screens from the home-page monolith into feature-owned components, retained the approved RTL card/filter layout, and exposed an optional validated public bank-logo URL from the same active `PUBLISHED` loan record. No score, total-interest amount, or loan fact is calculated in the browser; deployment remains T07.


- **US-09.T06A:** Replaced all reachable loan-result, detail, comparison,
  action and explanation prototype data with active `PUBLISHED` PostgreSQL
  serving data. The recommendation API now exposes server-owned highest,
  low-compatibility and needs-review partitions with deterministic ordering;

- **US-09.T071:** Added browser-local saved loans, editable profile fields and About page; PR #85 also introduced profile API and the user_profiles migration. Scoring and published loan data were unchanged.


Sidebar owner clarification: show the server profile name; use «کاربر» for a phone-only profile without a name. Refresh the owned profile when opening the menu with a valid capability. Personal-info uses the confirmed server response. Browser regression verifies named and unnamed profiles.

## US-09.T073 — Local OTP request repair (2026-10-09)

Owner reported failures in both login and personal-info on local Docker. Reproduced local API 503 with the new mock flag absent (old-container environment). Local/test now default to fake OTP 123456; explicit false still disables it, and staging/production remain fail-closed. This supersedes T072's opt-in-only local default without enabling real SMS or production authentication. The profile client honors VITE_SHAHAB_API_BASE_URL for every request. Existing schema, design, icons, About text, D-005 and published source data remain unchanged. New CI browser integration runs against real FastAPI/PostgreSQL through Vite, not API route fixtures. See Docker runbook for non-destructive container recreation.
