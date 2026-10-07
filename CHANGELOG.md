# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows Semantic Versioning when production releases begin.

## [Unreleased]

### Fixed

- **Local development:** Compose now publishes Vite on `5173`, avoiding the
  Windows-reserved `4173` range. FastAPI mounts the local source and reloads
  changes under `backend/`, so normal backend edits no longer require an image
  rebuild. No production runtime, API contract, data, or recommendation logic
  changed.

- **US-09.T06S:** endpoint توصیه یک snapshot تأییدشده را فقط یک‌بار می‌خواند و چهار fact واقعیِ کارت را از همان serving catalogue در پاسخ برمی‌گرداند. کارت نتیجه با این خلاصهٔ server-owned دیگر پس از spinner برای هر وام درخواست جزئیات جداگانه نمی‌فرستد؛ شروط کامل فقط در صفحهٔ جزئیات خوانده می‌شوند. داده، score، ضرایب D-005، threshold، session و استقرار تغییر نکرده‌اند.

### Security

- **US-09.T06R:** زنجیرهٔ توسعهٔ Vite به نسخهٔ pin‌شدهٔ امن `8.3.3` ارتقا یافت؛ lockfile نسخه‌های امن PostCSS، nanoid و source-map-js را ثبت می‌کند. `npm audit` نهایی صفر آسیب‌پذیری گزارش می‌دهد. UI، API، داده و استقرار تغییری نکرده‌اند.

### Added

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
  direct result refresh fails safely, and unavailable provider/payment/OTP/AI
  behavior is stated rather than simulated. Added route/API documentation and
  unit, PostgreSQL integration, browser journey and responsive visual evidence.

- **US-09.T06:** Connected the ten canonical session answers to approved source conversion and one-to-one category scoring in the server, added the session-only recommendation API, and mounted live ranked/review/loading/error results with published loan detail links. Staging deployment and real-URL verification remain US-09.T07.

- **US-09.T05B:** Added one-statement approved PostgreSQL recommendation snapshot read, active-only loan details with official conditions/facts, and a source-checked idempotent backfill for already published T05A rows. The pure engine now has a real repository adapter, without a public recommendation endpoint or deployed database. Added `US-09.T07` as the separate mandatory persistent-staging/Netlify/real-URL delivery gate; CI success alone does not satisfy it.


- **US-09.T05A:** Verified deterministic official-source extraction and D-005 weight precedence; source audits cover 102 loans, 30 weight groups and 720 compatibility cells. Added a reversible PostgreSQL migration and transactional, approval-gated materialization for versioned categories, conditions, configuration and serving catalogue, with idempotency and source-content checks. Database publication remains an explicit operator action after inspecting the actual database; T05B/T06 consume these records later.

### Changed

- **US-09.T05B (planned):** Added a separate post-T05A server adapter task for an approved PostgreSQL recommendation snapshot, real published loan conditions/details, and durable publication when the database audit proves it missing. Canonical session-to-engine adaptation and the live API/UI journey remain T06; this entry defines work, not completed runtime functionality.

- **US-09.T05A (planned):** Inserted an ordered data and configuration materialization gate before the unchanged T06 live integration. The task consumes the six official sources and approved D-001–D-004 decisions, persists PUBLISHED categories/conditions for existing server use cases, requires audit, provenance and PostgreSQL verification, and introduces no new matching formula or product behavior in this documentation change.


- **US-09.T06 (checkpoint):** documented the missing approved mapping, durable published snapshot and conditions projection that block a truthful live recommendation result. No endpoint, scoring, schema, migration or deployment behavior changed. See the `feature/us-09-live-integration` PR.

### Added

- **US-09.T05**: Added a browser-level recommendation journey contract that exercises the result client, RTL/a11y result surface, manual display controls, typed retry error, and the safe handoff to approved loan-detail conditions through controlled HTTP responses. The live questionnaire/session/API/engine connection remains T06.

- **US-09.T04**: Added server-result presentation controls: lender-only filtering, stable display sorting by lender name, responsive RTL/a11y result markup and typed loading/error states. Score formatting remains display-only; no browser scoring, API/session wiring or static recommendation results were added.

### Changed

- **US-09.T06 (planned)**: Made live end-to-end recommendation delivery a required completion task: the canonical questionnaire session must reach the real recommendation endpoint and server engine, show published loans with server-calculated compatibility percentages, keep `needsReview` score-free, and let the user open safe loan conditions/rules on a testable preview URL. `US-09` is not Done without browser E2E and product-owner manual verification.


- **US-09.T03**: Added a validated display-state contract that distinguishes ranked options, score-free needs-review options, no-candidate results and zero results after later manual filters. It preserves server order and rejects reordered or invented filtered items; no filter/sort computation or result-page wiring is added.

- **US-09.T02**: Added a narrow recommendation-result API client that posts only the opaque active-tab session ID in the JSON body, validates the server read model through the US-09.T01 view model, and turns transport/malformed-response failures into safe typed client errors. No browser scoring, reordering, filtering, persistence or result-page rendering is added.

- **US-09.T01**: Added a presentation-only, validated recommendation result view model and contract for server-calculated results. It preserves server rank/order and score, keeps needs-review entries score-free with a generic uncertainty warning, and builds encoded same-origin detail routes. No API request, React result page, client-side scoring, filtering, persistence or session lookup is added.

- **US-08.T05**: Added bounded golden and property-style regression coverage for deterministic ranking, neutral deposit exclusion, non-classified core review exclusion, score bounds, terminal output completeness and redacted trace determinism.

- **US-08.T04**: Added a framework-free `RecommendLoans` use case that reads one approved immutable recommendation snapshot, returns deterministic ranked and needs-review outputs, and keeps one redacted trace per candidate aligned to the same data/config versions. No FastAPI, React, ORM, database write, session lookup or public result behavior is added.

- **US-08.T03**: Added a pure, versioned and redacted `RecommendationTrace` with deterministic SHA-256 evidence. It records canonical category decisions, effective weight, neutral reasons and core ranking exclusions without session IDs, user identity, free-text answers, API, UI or persistence behavior.

- **US-08.T02**: Added the approved neutral/needs-review policy to the pure engine. Unknown, variable or blank deposit attributes are excluded from the score denominator; unknown core attributes receive no score and are deterministically returned in `needsReview` with typed reasons. No trace/API/UI behavior is added.

- **US-08.T01**: Added a framework-free, deterministic weighted category-matching engine. It validates complete unique positive-weight preferences, rejects missing candidate variables and orders tied results by stable loan ID. It has no database, API, UI, cache, trace, neutral or needs-review policy; those remain later US-08 tasks.

- **US-07.T06**: PostgreSQL now persists anonymous questionnaire sessions and canonical answers as the source of truth; Redis is a hashed-key, best-effort active-session cache with PostgreSQL fallback. A 30-minute expiry cleanup use case removes session-owned answers. No identity, cross-device resume, recommendation result or production deployment is introduced.

- **US-07.T05**: Added browser and API completion-boundary coverage for the behavioural questionnaire: incomplete answers are blocked, canonical body-only answers are persisted through the active-tab session, back navigation preserves the answer, and retryable save failures are announced without progressing. The tests assert no answer/session data appears in the browser URL. No durable PostgreSQL or Redis runtime is introduced; that remains US-07.T06.

- **US-07.T06 (planned)**: Added the required PostgreSQL source-of-truth and Redis cache architecture for anonymous questionnaire sessions, including a 30-minute expiry/cleanup contract, normalized ERD/schema requirements, cache-fallback semantics and mandatory documentation synchronization. No runtime persistence behavior is implemented by this documentation change.

- **US-07.T04**: Connected the behavioural-questionnaire UI to source-traceable canonical questions and a body-only anonymous-session API. The approved retention contract is 30 minutes in the current browser tab; opaque session IDs and answers are not written to browser URLs or web storage. No recommendation score, result, identity or cross-device resume behaviour was added.

- **US-07.T03**: Added anonymous questionnaire session contracts, canonical server-side answer validation, 3NF session/answer migration and an explicit retention-policy boundary. No HTTP answer route, URL answer transport, browser persistence, identity, scoring or automatic deletion policy was introduced.

- **US-01.T01**: Reproducible baseline record and current-state checkpoint; the existing frontend dependency install and production build are verified without changing product behavior.
- **US-01.T02**: Repository, route, dependency, mock, asset, and prototype-risk inventory without changing product behavior.
- **US-01.T03**: Canonical-source inventory with Git/original hash comparison; a source-integrity mismatch is recorded as a blocker for data implementation.
- **US-01.T03a**: Restored all six canonical `.unitext` files using byte-safe Git blobs and verified exact SHA-256/byte-count equality with the original UTF-16 LE sources.
- **US-01.T04**: Added project-document skeletons and an ADR template; no product behavior or data logic changed.
- **US-01.T05**: Added the initial risk and ambiguity register with owners, affected stories, and explicit future gates; no product logic changed.
- **US-02.T01**: Added a versioned canonical identifier contract and static validation for questionnaire IDs, answers, routes, loan variables, categories, and future loan identity.
- **US-02.T02**: Added pure typed schemas and conservative Persian scalar parsers with unit tests; unknown, range, and prose values are never silently inferred.
- **US-02.T03**: Added a read-only canonical-source audit, provenance report, structural evidence, and explicit blocking data issues; no source data changed.
- **US-02.T04**: Added approved, versioned decisions for Q5 interest weight, neutral deposit attributes, core-ranking exclusions, and display-only loan metadata.
- **US-02.T05**: Added versioned golden contract fixtures for canonical answers and complete, neutral, and core-unknown loan-policy boundaries.
- **US-03.T01**: Added staged frontend/backend architecture boundaries, module map, ADR and scaffold validation without moving the active prototype.
- **US-03.T02**: Added a typed FastAPI composition root, safe environment settings, recursive sensitive-field log redaction, dependency providers, focused core tests and local bootstrap runbook.
- **US-03.T03**: Added framework-free domain references, small application ports and AST-based reverse-import/cycle validation without introducing adapters or business behavior.
- **US-03.T04**: Added API v1 composition, typed safe error responses, generated correlation IDs, public minimal liveness and token-gated readiness.
- **US-03.T05**: Added reproducible Ruff/Mypy/test/secret-scan quality gates and a GitHub Actions workflow with no product behavior change.
- **US-04.T01**: Added versioned conceptual ERD, data dictionary, design ADR and documentation validator before physical schema work.
- **US-04.T02**: Added PostgreSQL 3NF physical-schema/constraint specification, migration and rollback operations runbook, ADR and contract validator.
- **US-04.T03**: Added SQLAlchemy 2.x core metadata, explicit database constraints/state enums, transaction boundary port and metadata tests before migrations.
- **US-04.T04**: Added Alembic initial schema migration, bounded SQLAlchemy engine/session composition, Docker Compose local PostgreSQL/API runtime, and real PostgreSQL CI verification of upgrade, fixture write and downgrade.
- **US-04.T05**: Added measured index/query strategy, reversible index migration and PostgreSQL `EXPLAIN (ANALYZE, BUFFERS)` plan-shape verification for selective catalogue lookup.
- **US-05.T01**: Added immutable, content-addressable raw-source capture with SHA-256 integrity, metadata record, size gate and local/test storage adapter; no parsing or serving publication occurs.
- **US-05.T02**: Added strict non-destructive staging validation for encoding, header contract, row width and duplicate source evidence.
- **US-05.T03**: Added conservative normalization and category mapping for all approved loan variables, including typed unmapped outcomes for source-matrix gaps and out-of-range values; no scoring or publication behavior was added.
- **US-05.T04**: Added immutable canonical-row construction, typed rejection evidence, reviewed catalogue diffs, explicit approval records and atomic serving-version publication boundary; no public publication API or scoring behavior was added.
- **US-05.T05**: Added a non-publishing canonical-import preparation command, typed manifest evidence and an operations runbook; no database, approval or serving-pointer mutation can be initiated by the command.
- **US-05.T06**: Added deterministic repeated-import, ambiguous-input and atomic-publication-failure tests; a failed publication demonstrably preserves the prior serving version.
- **US-06.T01**: Added framework-free ListLoans and GetLoanDetails use cases over a serving-only catalogue port; drafts, raw/staging data and provenance internals cannot reach public loan models.
- **US-06.T02**: Added limited, camel-case FastAPI response schemas that allowlist approved public loan facts and reject provenance, raw conditions, internal asset references and extra fields.
- **US-06.T03**: Added a pure plain-text conditions-to-bullets parser; it strips list formatting without generating HTML or interpreting source text as markup.
- **Corrective US-06 dependency**: Added PostgreSQL/SQLAlchemy serving-catalogue adapter with an explicit published-state filter and integration coverage.
- **US-06.T04**: Added the approved-serving loan-detail API endpoint and active RTL API view with loading, absent-detail, safe-error and retry states. Conditions are transported only as parsed plain-text bullets; no migration, recommendation score, raw provenance or internal asset data is exposed.
- **US-06.T05**: Added pinned Playwright Chromium coverage and CI verification for approved-detail RTL rendering, loading, absent-detail, safe retry, hostile condition text and ignored invalid asset/link fields; the public API boundary now also asserts JSON-only, allowlisted behavior.
- **US-07.T01**: Added approved, source-traceable questionnaire configuration for ten canonical questions and fifty stable answers, with a read-only source/identifier validation gate; no route, session, UI, scoring or recommendation behavior changed.
- **US-07.T02**: Added the tested, bidirectional route adapter that maps the immutable `/question/3..12` paths to canonical behavioural question IDs while preserving the prototype's public navigation; no answer/session/API/scoring behavior changed.
