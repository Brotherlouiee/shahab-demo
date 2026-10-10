# Project Continuity Document

> **Document version:** 12.0

> **Project:** Shahab Finance Demo / `shahab-demo`  
> **Prepared:** 2026-10-10  
> **Repository state represented:** `main` at `6d31bde1bc27ecdf1fabe3f423b660b3930f1b78`, after PR #93; section 0B is the current authoritative handoff. US-09.T07 real deployment remains unverified.
> **Purpose:** This is the hand-off document for a new chat or engineer with no access to prior conversation history. It distinguishes implemented reality from the target architecture and from proposals not yet approved.

## 0B. Owner-directed continuity reconciliation — authoritative update (2026-10-10)

The owner explicitly requested this refresh after the recent changes were described as nearly complete. This authorization permits a mid-story documentation update; it does **not** declare US-09, production authentication, deployment or the project complete. The normal story-end continuity rule remains binding for future work.

**Precedence:** this section and the refreshed sections 17–19 and 22 supersede older implementation/status/next-task statements. Sections 0A and 0 preserve dated checkpoints; older task tables and quality counts are historical evidence, not a current work queue. Permanent source, product, security and Golden Rules remain binding. Repository code, migrations and fresh CI must be reconciled before further work.

### Repository and verification

- Latest merged feature: [PR #93 — recommendation history](https://github.com/Brotherlouiee/shahab-demo/pull/93), merged 2026-10-10 at 21:22 Tehran (17:52 UTC), with 11 commits and 31 changed files.
- Feature head: `69a0abf7b8deef4b26a8abbd7484bd4fe9ef9858`; merge/main: `6d31bde1bc27ecdf1fabe3f423b660b3930f1b78`.
- [Feature-head CI](https://github.com/Brotherlouiee/shahab-demo/actions/runs/38073092052) succeeded.
- [Merged-main CI](https://github.com/Brotherlouiee/shahab-demo/actions/runs/38073493793) succeeded in all four jobs: Quality gates, PostgreSQL migration verification, Loan details browser verification, and Profile OTP real API browser verification.
- These runs verify their checked test scopes. They are not evidence of deployment, the owner's local database contents, or independent visual acceptance of every page. This documentation refresh does not rerun runtime tests or change application code.

### Implemented capability map

| Capability | Current contract / evidence boundary |
|---|---|
| Questionnaire and recommendation | Canonical questionnaire answers are server validated; anonymous retention remains 30 minutes. The deterministic server engine reads approved configuration and active PUBLISHED data. Results/detail/comparison are API connected. No client-owned score or fabricated catalogue data. |
| Profile creation | Successful local/test OTP verification creates/reuses `user_profiles` before issuing access. Requesting OTP alone does not create a profile. Repeat login preserves saved fields. |
| Personal information | Name, family name, income and job update the same owned database profile before analysis; existing gender/avatar are preserved. Failed persistence remains visible/retryable. |
| Sidebar identity | Read the owned server profile; show the stored name, or «کاربر» for a phone-only profile. Browser display cache alone does not authorize access. |
| Account session | PR #93 adds an HttpOnly, SameSite=Lax same-origin account cookie and `GET /api/v1/account-access/session` restoration. A valid refresh/session should reach history without unnecessary OTP. Bearer credentials are not saved in localStorage. |
| Recommendation history | Successful authenticated results are stored atomically once per questionnaire session, with all three partitions, order, scores/reasons, data/config versions and immutable card display facts. Anonymous results remain transient. |
| Ownership | The creator browser receives a per-questionnaire HttpOnly proof cookie. First history write requires that proof and atomically binds the session owner. Session ID alone is not ownership; reads and mutations constrain the authenticated actor. |
| History list | Menu item «سوابق وام‌های توصیه شده» follows «سوابق درخواست وام». Cards show server creation date/time in Tehran, ranked-section count, and result navigation. Newest-first keyset pagination replaces offset pagination. |
| Historical display | Reuses LoanResultsScreen and normal result controls with stored output; no rescoring. Result-to-detail and return paths belong to the selected historical entry. Preserve list position/pagination and original source/back behavior according to the approved flow. |
| Empty states | A successful empty history reuses the existing saved-loans artwork. Loading, valid empty output and request/authentication failure are distinct. Zero ranked count does not mean the entire historical result is empty. |
| Hidden histories | Owner-scoped DELETE hides a card after confirmation by setting `hidden_at`. Immutable run/items/reasons remain in the database. Hidden runs are excluded from user list/detail reads; this is not physical deletion. |
| Bookmarked loans | Still browser-local under `/saved-loans`; recommendation history is a separate, database-backed feature. Do not conflate the two or claim bookmarks are per-account PostgreSQL records. |
| Unavailable external actions | Real SMS, external AI analysis/readiness and bank application/provider success are not delivered by this update. Preserve approved disabled controls and do not simulate success. |

### Database and API handoff

Use the existing profile identity and normalized relations; do not create duplicate user/bank/loan tables. The history design deliberately snapshots the minimum card facts to protect historical display while retaining a loan-product-version foreign key. It is not permission to duplicate all API payloads or raw questionnaire answers.

| Migration | Change |
|---|---|
| `d1a9e71b4c3f` | Existing user_profiles foundation (PR #85). |
| `e4c7b9a1d2f3` | recommendation_history_runs, recommendation_history_items and recommendation_history_item_reasons; unique questionnaire-session run and owner/time index. |
| `f1a2b3c4d5e6` | Nullable questionnaire session owner relation/index for atomic owner binding. |
| `a3b7c9d1e2f4` | History hidden_at; retained data rather than physical deletion. |

- Owned APIs: `GET /api/v1/profiles/me`, `PUT /api/v1/profiles`, `GET /api/v1/recommendation-history`, `GET /api/v1/recommendation-history/{historyId}`, and `DELETE /api/v1/recommendation-history/{historyId}`.
- Missing/other-owner/hidden history is not readable; hide returns 204 only for an eligible owned visible record.
- Database access for authorized operators follows the run/item/reason foreign keys and existing owner identity. Hidden data remains accessible to authorized database administration; no public admin/export endpoint is implied.
- Never copy raw answers or credentials into history, URLs or logs. Questionnaire expiry is not permission to erase retained history. Review retention/cleanup against foreign keys before changing that policy.
- Apply forward migrations according to the Docker/operations runbook. Never reset a volume, truncate data, run `docker compose down -v`, or treat destructive downgrade as routine rollback.

### Authentication and operational limits

- Local/test fake OTP remains `123456`, enabled by default in these environments; an explicit false setting disables it. Staging/production reject this mock. It proves development flow, not real phone ownership.
- Challenges are bounded and expire; account capabilities expire/revoke and are stored process-locally. The restoration cookie does not make access survive API restart or provide shared multi-worker production sessions. Do not claim durable production authentication.
- The present frontend uses same-origin credentials and a local Vite API proxy. A separately hosted API requires an approved cookie/CORS/HTTPS/CSRF arrangement; do not assume same-origin development settings automatically work across hosts.
- ADR 0010's earlier “refresh requires login” statement is superseded by PR #93 session restoration while the server session remains valid. ADR 0011 describes the base history decision; the canonical guide's T079 follow-ups and current migrations describe later ownership/cursor/hide additions.
- The currently observed Netlify project URL is `https://shahabfintech-ir.netlify.app/`; older `shahab-finance-demo.netlify.app` references are historical and must not be used without rechecking. No current real-URL full-stack acceptance is established by this refresh.

### Recent merged work to preserve

PRs #85–#87 introduced/repaired database profiles and local/test OTP; #88 restricted home to the approved hero composition; #89 delivered saved-loans empty/navigation states; #90 refined questionnaire geometry/disabled controls; #91 installed the supplied global SVG logo; #92 reduced only question-2 card height; #93 delivered history and corrective follow-ups.

No unsolicited design changes are authorized. Preserve supplied icons/assets, exact page geometry, colors, text and existing controls. Reuse shared pages/components. Historical results must match the existing result page for the same data and viewport.

### Next action and unresolved delivery gate

1. Reconcile the owner's IDE with merged main safely: inspect local status before pull/switch; preserve uncommitted edits. Work on a new scoped branch for any further correction because PR #93 is already merged.
2. Confirm the owner's final acceptance of the three previously reported issues: unnecessary history login, successful-empty artwork, and history-card geometry. The owner says changes are nearly complete; no unresolved failure is asserted here, but no independent visual acceptance is invented.
3. The remaining ordered operational delivery gate is **US-09.T07**: persistent staging PostgreSQL, approved publication/import, deployed HTTPS API, Netlify integration, actual-URL questionnaire/result/detail/comparison verification, restart and rollback evidence. Select infrastructure/access/configuration with the owner rather than guessing.
4. Do not advance to US-10 or mark US-09 complete until its full gate is evidenced. US-11 hardening and US-12 production release remain later gates.

References: canonical guide T071–T079 and corrective follow-ups; CHANGELOG; ADR 0010/0011; docs/operations/docker-runbook.md; docs/runbook/production-deployment.md; docs/evidence/ and current GitHub CI. Older short-term checkpoint entries must be read as dated history, not as instructions to restart completed tasks.

---

## 0A. Owner-directed continuity reconciliation — authoritative update (2026-09-28)

> This is an explicit product-owner-directed mid-story refresh. It **does not** mark `US-09` complete and does not weaken the normal rule that the continuity document is updated at a completed user-story gate. All earlier statements in this document about current implementation, the next task, local/full-stack readiness, results UI or `US-09` status are superseded by this section.

### Repository position

- **Repository truth:** `main` after merge of PR [#60](https://github.com/Brotherlouiee/shahab-demo/pull/60), merge commit `a3f9680ebb7c5e60e410f210f0b8d7e2c18894b7`.
- **Completed story base:** US-01 through US-08 are merged. The anonymous questionnaire uses PostgreSQL as its durable source of truth when configured, with Redis only as an optional, rebuildable cache and a database fallback.
- **US-09 completed work:** the result view model/API client, canonical session-to-recommendation integration, real published-loan result/detail routes and follow-up UI work through `US-09.T06H` are merged. The relevant delivery PRs include [#39](https://github.com/Brotherlouiee/shahab-demo/pull/39), [#40](https://github.com/Brotherlouiee/shahab-demo/pull/40), [#51](https://github.com/Brotherlouiee/shahab-demo/pull/51), [#53](https://github.com/Brotherlouiee/shahab-demo/pull/53), [#54](https://github.com/Brotherlouiee/shahab-demo/pull/54), [#55](https://github.com/Brotherlouiee/shahab-demo/pull/55), [#56](https://github.com/Brotherlouiee/shahab-demo/pull/56), [#57](https://github.com/Brotherlouiee/shahab-demo/pull/57), [#58](https://github.com/Brotherlouiee/shahab-demo/pull/58), [#59](https://github.com/Brotherlouiee/shahab-demo/pull/59) and [#60](https://github.com/Brotherlouiee/shahab-demo/pull/60).
- **Not complete:** `US-09.T07` is the separate, mandatory real-deployment task. CI, Docker-local integration and a merge to `main` are not evidence of deployment.

### What is now available in code and locally verified browser flows

1. The user completes the canonical questionnaire; the browser sends only the opaque session identifier to `POST /api/v1/recommendations`. No client-side score, threshold, weight, category, rank or fabricated loan fact is calculated.
2. FastAPI reads the complete questionnaire session plus the approved configuration and the active `PUBLISHED` PostgreSQL catalogue. Results are returned in three server-owned partitions: highest compatibility, low compatibility and variable/needs-review. The latter has no score or rank.
3. Results, loan details, comparison selection and comparison result routes use server-owned published loan facts. Direct result-route entry without a usable session fails closed rather than showing invented rows.
4. Conditions/required documents are displayed from approved serving data; no provider, payment, OTP, loan-application or external-analysis success is simulated when no approved provider contract exists.
5. The local catalogue publication verification recorded 102 loans: 88 rankable and 14 needing review. These figures describe the checked local catalogue, not a deployed production database.
6. The UI is modularised around feature-owned result, card, detail and percentage components. Current card behavior includes fixed internal bank-logo placement, right-aligned single-line bank identity, centered single-line loan title with ellipsis, real result filters, comparison selection/result flow and reserved scroll space so a selected tenth loan is not hidden by the fixed comparison action.
7. Bank logos are not fetched from `rade.ir` at render time. Twenty-nine approved SVG assets are stored under project control; the serving data preserves provenance while also storing a controlled asset key and recorded file hash. Results, details and comparison surfaces use those internal assets.
8. Loan percentage displays use the tested visual RTL form `٪۱۸`, including the declared-interest display. The browser does not alter the underlying numeric data.

### Rules that remain binding

- **D-005:** only coefficients from the approved answer-conversion table are valid. Numeric coefficients from the questionnaire-to-loan mapping matrix must not be used.
- The product remains decision support, not credit scoring, approval prediction or a guarantee of receiving a loan.
- Only `PUBLISHED` serving records may cross the public API boundary. Unknown/variable core fields remain unscored and unranked in needs-review; the three deposit fields follow the approved neutral policy.
- No credential, database URL or provider secret belongs in Git, Vite/React or browser storage.

### Verification currently evidenced

- PR #60: `PYTHONUTF8=1 npm run quality` passed (120 backend tests passed; 4 environment-dependent tests skipped) and `npx playwright test tests/e2e/live-recommendation-route.spec.mjs` passed 4 desktop/mobile checks, including card geometry and the two-/ten-loan comparison-return flows.
- PR #59 additionally verified controlled SVG rendering/hash checks, the questionnaire-to-results/detail/comparison browser route, and visual percentage geometry. These are code/local/CI checks, not public deployment checks.
- Fresh desktop and mobile visual evidence is versioned under `docs/evidence/us-09-t06h/`.

### The one next delivery gate — US-09.T07

Before calling the product operational, complete and document all of the following on real infrastructure:

1. persistent PostgreSQL on the selected server, reachable only through the intended protected network path;
2. migrations and the approved 102-loan publication/import on that persistent database;
3. FastAPI connected to that database and exposed through HTTPS;
4. Netlify configured to call that deployed API without a browser-visible credential;
5. an end-to-end test on the actual public URL: questionnaire → API → engine → results/detail/comparison;
6. a restart check proving API health, data access and recommendation flow recover correctly.

Required user/product-owner inputs for T07 remain the server/domain/access and secret-management decisions. Do not guess them. Until T07 succeeds, the Netlify frontend must not be represented as a deployed full-stack product.

---
## 0. Current reconciliation — authoritative update (2026-09-24)

This section supersedes any older status statement below that says the questionnaire work stops at `US-07.T02`.

### Version history

- **v10.0 — 2026-09-25:** `US-08.T05` is complete in mergeable PR #38. It adds bounded golden and property-style regression checks for ranking, neutral policy, core exclusions, terminal completeness and redacted trace determinism. GitHub Actions #123 is green; it adds no API, UI, ORM, database-write or session behaviour. Library and Git `docs/` copies are synchronized.
- **v9.0 — 2026-09-25:** `US-08.T04` is complete in mergeable PR #37. The pure `RecommendLoans` use case reads one approved immutable snapshot and returns aligned ranked/needs-review outputs with one redacted trace per candidate. GitHub Actions #116 is green; Library and Git `docs/` copies are synchronized.
- **v8.0 — 2026-09-25:** `US-08.T03` is complete in mergeable PR #36. GitHub Actions #112 passed quality, PostgreSQL migration verification and Chromium E2E. Library and Git `docs/` copies are synchronized.
- **v7.0 — 2026-09-24:** `US-08.T03` is implemented in PR #36: a pure, deterministic and redacted `RecommendationTrace` records canonical category evidence, neutral/exclusion reasons, effective weight, score when rankable and a stable SHA-256 hash. No session, identity, raw answer, API, UI or persistence data is included; CI evidence is pending final PR gate.
- **v6.0 — 2026-09-24:** `US-08.T02` is complete in mergeable PR #35 with GitHub Actions #106 green. Library and Git `docs/` copies are synchronized.
- **v5.0 — 2026-09-24:** Recorded the `US-08.T02` neutral/needs-review policy checkpoint.
- **v4.0 — 2026-09-24:** `US-08.T01` is complete in mergeable PR #34 with GitHub Actions #101 green. The Git `docs/` copy and the Library document are synchronized.
- **v3.0 — 2026-09-24:** `US-07.T06` was merged in PR #33. Added the `US-08.T01` pure recommendation-engine checkpoint and synchronized copy requirement for `docs/PROJECT_CONTINUITY_DOCUMENT_SHAHAB_FINANCE_DEMO.md`.
- **v2.0 — 2026-09-24:** Added the `US-07.T06` durable-session implementation checkpoint and the explicit document-versioning convention. Future updates must increment this number.
- **v1.0 — 2026-09-24:** Reconciled the document through merged `US-07.T05`.

- `US-07.T03` was merged in PR #29: an anonymous-session domain/application boundary, canonical answer validation and a 30-minute retention policy were introduced. The current server adapter is process-local in-memory only.
- `US-07.T04` was merged in PR #30: behavioural questionnaire screens use the approved canonical prompts/answer IDs and call the body-only session API. The opaque session ID is held only in the current React instance; no answer or session value is put in browser URLs, `localStorage` or `sessionStorage`. Refresh, another tab, a new browser or another device start a new session.
- PR #31 was merged: `US-07.T06` is now an ordered, mandatory task after `US-07.T05`. It will make PostgreSQL the normalized source of truth and Redis an optional cache with database fallback; it must implement the 30-minute expiry/cleanup policy and keep the ERD, physical schema, data dictionary, migrations and tests synchronized.
- `US-07.T05` is implemented in PR #32, `test: complete US-07.T05 questionnaire flow verification`: browser/API tests cover incomplete-answer blocking, canonical JSON-body answer save, same-tab back navigation, URL non-leakage, RTL/accessibility roles and retryable save failure. GitHub Actions run #85 is green for quality, PostgreSQL migration verification and Chromium E2E; PR #32 is mergeable and awaits only normal review/merge.
- No durable questionnaire answer storage, Redis runtime, recommendation score/result, identity, OTP integration, cross-device resume or production deployment exists yet. Do not represent an answer as durably saved until `US-07.T06` is merged and deployed.
- The next permitted product task after a green/merged `US-07.T05` is `US-07.T06`; `US-08` cannot start first.
- `US-07.T06` is now implemented in PR #33: PostgreSQL is composed as the durable source of truth when configured, Redis uses only SHA-256-derived opaque cache keys and a cache miss/outage falls back to PostgreSQL. The 30-minute cleanup use case deletes expired sessions and their answers idempotently. At this checkpoint, PR CI is still the mandatory final merge gate; no production deployment is claimed.
- `US-08.T01` is complete in PR #34. It adds immutable recommendation inputs plus a pure deterministic weighted category-match score and stable ordering. GitHub Actions #101 is green for quality, PostgreSQL migration verification and Chromium E2E; PR #34 is mergeable. It has no database, FastAPI, React, trace, neutral/unknown, needs-review or recommendation endpoint behavior; those are later ordered tasks.
- `US-08.T02` is complete in PR #35. Unknown/variable/blank deposit attributes are neutral and excluded from the score denominator. Unknown core ranking attributes are returned deterministically in `needsReview` with typed reasons and receive no score or rank. GitHub Actions #106 is green; PR #35 is mergeable. Trace output, API, UI and use-case composition remain later tasks.
- `US-08.T03` is complete in PR #36. Its framework-free trace contract is versioned and redact-by-design: it records only canonical category IDs and calculation evidence, never questionnaire session IDs, user identity, free-text answers or raw source values. GitHub Actions #112 is green for quality, PostgreSQL migration verification and Chromium E2E; PR #36 is mergeable. `US-08.T04` remains the next task for use-case composition.
- `US-08.T04` is merged in PR #37. `US-08.T05` is complete in PR #38: bounded golden/property-style coverage now protects deterministic ranking, neutral handling, non-classified core exclusion, terminal completeness and trace determinism. GitHub Actions #123 is green; no API, UI, ORM, database-write or session-lookup behaviour is included. The next ordered work is `US-09.T01`.

## 1. Project Identity

| Item | Record |
|---|---|
| Name | Shahab Finance Demo / Shahab loan recommender |
| Repository | Private GitHub repository: `https://github.com/Brotherlouiee/shahab-demo` (`Brotherlouiee/shahab-demo`) |
| Domain | Iranian retail-loan discovery, comparison and recommendation |
| Primary problem | People often lack an accurate, usable understanding of loan terms and may choose loans that are financially or operationally unsuitable. Loan terminology and a simplistic idea of “cheap/good loan” lead to bad decisions. |
| Final product objective | Replace prototype/mock outputs with a testable, explainable, data-driven recommendation engine that matches approved available loans to a user’s needs, payment capacity, operational constraints and behavioural preferences. |
| Explicit non-objective | Not credit scoring; not credit approval prediction; not a guarantee that a user will receive a loan. Bank/lender makes approval decisions and user makes the final choice. |
| Target users | Iranian individuals assessing available loans/credit facilities; future operations users who import, review and approve loan data/configuration. |
| Value proposition | Explainable comparison: show compatible loan options, important terms, trade-offs and uncertainty rather than claim a universally “best” loan or approval probability. |
| Current delivery stage | Data/backend foundations, published-loan detail API/UI and canonical questionnaire navigation are implemented and tested. Personalised recommendation, response persistence, public backend deployment and live full-stack integration are **not yet implemented**. |

---

## 2. Project Vision & Strategic Context

### Why the project exists

The initial product problem is decision support, not risk assessment. Users can often answer what they need or prefer, but cannot safely translate that into interest-rate, instalment, term, deposit, guarantee and other loan trade-offs. Shahab must make those trade-offs visible and produce a reproducible match against approved loan data.

### Strategic positioning

- **Confirmed:** Shahab starts with loan comparison/recommendation.
- **Under discussion / future product direction:** It may later expand beyond the current loan tool. The user has considered a parent brand “Shahab” with products such as Shahab Bank, Credit, Wealth, Insurance or Invest; “Bank” was considered a possible suffix broad enough for future financial areas.
- **Consequence:** Keep domain boundaries extensible, but do not prematurely build a broad fintech/neo-bank platform. The current bounded context is loan recommendation.

### What makes it different

1. Recommendations are derived from versioned source data and an explicit rule/configuration model, not static percentages in a React screen.
2. Every recommendation must be explainable through a `RecommendationTrace`.
3. Unknown information is handled honestly: some non-core unknowns are neutral; unknown core terms exclude a loan from scored ranking and place it in `needsReview`.
4. Loan terms displayed to users must originate from approved serving data, never inferred text or UI hard-coding.

### Definition of success

Success is **not** a visually polished prototype alone. A successful release has all of the following:

- approved, traceable loan/configuration data;
- deterministic, tested recommendations with clear uncertainty;
- a user can complete the canonical questionnaire and receive real server-calculated results;
- public UI and API are safely deployed, observable and rollback-capable;
- all US-01 through US-12 acceptance gates are complete, including security, migration, preview and post-deploy verification.

---

## 3. User / Stakeholder Context

### Product owner and primary stakeholder

The user is the product owner and decision maker. Their background is product/business and venture development, with strong familiarity with platform/product thinking, business models, research and statistics. They do not want the product to be reduced to a conventional credit-scoring questionnaire.

### Product intent that must be preserved

- Ask enough questions to clarify the user’s own financial decision; questions do **not** assess credit history at this stage.
- Do not optimise for a simplistic “lowest interest” answer. Balance practical affordability, loan amount, repayment burden, operational requirements and preferences.
- Avoid artificial certainty and misleading claims such as “best loan” or “you will be approved.”
- Use clear Persian, RTL-friendly UI and explanations appropriate for Iranian users.

### Collaboration preferences and constraints

- Work sequentially through the approved user stories and tasks. Do not skip ahead or mix future-task scope into the current PR.
- The user expects a complete, mergeable result per task: implementation, relevant tests, quality/security checks, documentation, CHANGELOG, checkpoint and PR. Do not stop after partial coding.
- The project uses three governing “Golden Rules” (see section 4); they are mandatory.
- Be direct and evidence-based. Distinguish a code-level integration from a live public deployment.
- Never expose passwords, tokens or credentials in chat, Git or logs.
- Remaining model/token capacity is relevant: if insufficient to close a full task cycle, split before implementation or create only a documented checkpoint. Do not leave untested, undocumented partial changes.

---

## 4. Core Principles & Permanent Rules

### 4.1 The Three Golden Rules — **Confirmed and overriding**

1. **Staged development and capacity-aware execution.** Development, test, migration and deploy are never a single big-bang action. Use the smallest compatible, reviewable task; minimise repeated exploration; run nearby tests; finish with a complete commit. If capacity is inadequate to close the cycle, split the task or make only a checkpoint.
2. **Read the complete canonical guide every stage.** Before starting, resuming or returning to **any** user story, task, subtask, bug fix, refactor, migration, test or deploy: reread the complete canonical guide, then read the related ADR/data decision and relevant official `.unitext` sources. Token economy never permits skipping this review.
3. **No unproven partial completion.** A task is Done only after its acceptance criteria, required tests, security/quality review, documentation, CHANGELOG, checkpoint and commit/PR are complete. A later story starts only after the previous gate is green. Project completion requires `US-12.T05`, a full release gate, preview/post-deploy verification and tested rollback.

### 4.2 Source-of-truth hierarchy — **Confirmed**

1. The current repository `main` and its versioned documentation/ADRs/checkpoints are operational truth.
2. `docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md` is the permanent development contract. A Library copy named `SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md` also exists, but repository `main` must be checked before work.
3. Six `.agents/documents/*.unitext` files are the current official business/data source documents. For engine/data/questionnaire/result/database changes, reread all six and verify against `docs/source-inventory.md`.
4. If sources conflict, do not silently choose one. Record the precise conflict, source location, impact and proposed resolution in `docs/recommendation-data-decisions.md`. A versioned configuration may be `approved: false` for build/testing, but production is blocked until the owner approves it.

### 4.3 Official source documents — **Confirmed**

1. `.agents/documents/پرسشنامه سنجش متغیرهای رفتاری.unitext` — questionnaire text, questions and options.
2. `.agents/documents/ماتریس گزینه های متغیرهای وام.unitext` — standard categories for eight loan variables.
3. `.agents/documents/ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام.unitext` — each question’s contribution to each loan variable.
4. `.agents/documents/تبدیل پاسخ‌ها به وزن‌های عددی.unitext` — answer weights.
5. `.agents/documents/ضرایب تناسب یک به یک گزینه‌های هر یک از سئوالاتسناریوها با هریک از دسته بندی‌ها متغیرهای وام.unitext` — answer × loan-category compatibility coefficients.
6. `.agents/documents/دیتابیس وام های بانکی.unitext` — raw loan data and display conditions.

All source hashes/inventory must be preserved and checked. Raw data must never be hard-coded into the UI or browser-side engine.

### 4.4 Product and data rules — **Confirmed**

- Stable Latin IDs are canonical; Persian strings are display labels only.
- Question/answer identity is never a URL number, screen index or visual option position. Each option requires a stable `answerId`.
- Incomplete answers must be detectable and rejected; never silently convert them to zero weight.
- No parser may use free-form display text for direct numerical/business comparison without a tested normalisation layer.
- Numeric Persian formats, spacing, `تومان`, percentages, `متغیر` and `نامشخص` require tested parsers.
- Only a **published/approved serving version** may reach public loan listing/detail/recommendation use cases. Draft/raw/staging/superseded records and provenance internals must not cross the public boundary.
- Every business claim must be traceable to project data.

### 4.5 Engineering and Git rules — **Confirmed**

- Inspect the real repository and active `main` before changes.
- Create a feature branch from `main`; never push directly to `main`.
- One small reviewable task/commit/PR at a time. Do not bundle data rules, algorithms and unrelated UI changes.
- The change allowlist in the user-story task matrix is binding; unrelated changes need an explicit ADR/PR rationale.
- Update relevant docs, module map/API/ERD/runbook, `CHANGELOG.md` and `docs/project-current-state.md` in the same PR.
- No secrets, credentials, personal data or sensitive raw data in Git, client bundles or public logs.

---

## 5. Product Definition

### Problem Statement

An Iranian loan seeker needs help comparing loan facilities according to their own financial needs and constraints. Existing intuitive heuristics are often insufficient because terms, deposits, guarantees, repayment and costs are difficult to compare. The product translates stated preferences into an explainable comparison of available loan offerings.

### Target Users

| User | Need | Product boundary |
|---|---|---|
| Loan seeker | Understand options and see compatible loans/terms | Not a creditworthiness or approval decision |
| Data/operations owner | Import, review, approve and roll back trusted loan/config data | Internal-only operations, later US-10 |
| Product/admin owner | Review audit/trace, source/version and release state | No direct database editing |

### Primary user journey — target state

1. User enters the questionnaire.
2. Each behavioural page maps to a canonical question and a valid canonical answer.
3. Server validates and retains a short-lived anonymous questionnaire session; no answer data in URL/public logs.
4. User submits complete answers.
5. Backend uses an approved data/configuration snapshot to produce `rankedRecommendations`, `needsReview` and a redacted `RecommendationTrace`.
6. Frontend presents scores, reasons, warnings, conditions and action links with clear uncertainty language.
7. User can return/back/resume without corrupting answers; can open loan detail; final decision remains theirs.

### Product capability map and current state

| Capability | Goal/business logic | Status as of 2026-09-20 | Dependencies / note |
|---|---|---|---|
| Source inventory and audit | Establish traceable official inputs and identify data quality problems | **Implemented** | Six official `.unitext` sources, audit/provenance decisions and fixtures exist. |
| Loan-data normalisation/import | Turn raw data into typed, approved serving data with provenance | **Implemented foundation** | Ingest, staging, normalisation, approval/publish and tests completed in US-05. Live production dataset/deploy still pending. |
| Published-loan catalogue | Expose only approved public loan versions | **Implemented** | SQLAlchemy adapter explicitly filters `PUBLISHED`. |
| Loan list/detail API | Safely expose allowlisted public loan facts | **Implemented at code/API level** | `GET /api/v1/loans/{loanId}` is implemented. Public live hosting is not. |
| Safe conditions display | Convert approved conditions text into safe plain-text bullets | **Implemented** | No HTML generation/interpreting; XSS/browser tests added. Persistence mapping currently may return an empty list until conditions field is hydrated. |
| Loan details UI | Show API detail with RTL, loading, absent, error/retry states | **Implemented at code level** | Connected in code and covered by Chromium E2E; current public Netlify deployment has no live FastAPI. |
| Canonical questionnaire configuration | Stable ten questions / fifty canonical answer IDs, source-validated | **Implemented** | US-07.T01 / PR #27. |
| Questionnaire route mapping | Preserve current public routes while mapping to canonical IDs | **Implemented** | US-07.T02 / PR #28; no persistence or scoring. |
| Anonymous session and answer validation | Server-side start/save/validate/resume/retention | **Not implemented; next** | US-07.T03. |
| Questionnaire UI integration | Submit canonical answers; next/back/resume/no incomplete submit | **Not implemented** | US-07.T04. |
| Personalised recommendation engine | Score, tree traversal, neutral/exclusion and trace | **Not implemented** | US-08. |
| Results UI/API | Replace static result cards/percentages with server results | **Not implemented** | US-09. |
| Operations authorization/audit | Safely control imports/approvals/config | **Not implemented** | US-10. |
| Production hardening/release | Security, deployment, monitoring, rollback | **Not implemented** | US-11 / US-12. |

---

## 6. Functional Requirements

| ID | Requirement | Description | Status |
|---|---|---|---|
| FR-01 | Canonical questionnaire | Ten required canonical questions and fifty stable answers must match official source text/order. | Implemented |
| FR-02 | Immutable route contract | `/question/3..12` map exactly to `Q1..Q6`, `S7`, `S8`, `S10`, `S13`; first two pages are independent. | Implemented |
| FR-03 | Valid answer capture | Each required question must have exactly one canonical answer; incomplete/unknown input is rejected. | Pending (session/UI work) |
| FR-04 | Published catalogue only | User-facing loan data only comes from `PUBLISHED` versions. | Implemented |
| FR-05 | Safe loan details | API is allowlisted; conditions are plain-text bullets; no raw HTML/XSS/internal provenance leakage. | Implemented at code level |
| FR-06 | Ranking eligibility | Four core unknown values exclude loans from scored ranking; three deposit unknowns are neutral. | Decision confirmed; engine pending |
| FR-07 | Explainable scoring | Build deterministic scores and a trace using source/config/data version. | Pending (US-08) |
| FR-08 | Separate outcomes | Return/show `rankedRecommendations` and `needsReview` separately; no score/rank for needs-review loans. | Pending (US-08/09) |
| FR-09 | Transparent UI | Show reasons, warnings, terms, uncertainty and action method; do not claim approval or “best loan.” | Partially implemented for details; results pending |
| FR-10 | Secure operations | Only authorised internal roles can import/approve/roll back loan/config data; append-only audit. | Pending (US-10) |
| FR-11 | Deployable service | A versioned API, database and frontend can be deployed with health checks, migration, observability and rollback. | Pending (US-11/12) |

---

## 7. User Stories & Execution Status

### Overall implementation sequence — **Confirmed; do not reorder**

| ID | Title | Status | Notes |
|---|---|---|---|
| US-01 | Baseline, source inventory, docs and risk register | Done | Repository baseline/skeleton and source traceability completed. |
| US-02 | Data audit and business decisions | Done | Includes canonical IDs, parsers/audit/provenance, Q5 fix, unknown policy and golden fixtures. |
| US-03 | Backend foundation | Done | FastAPI, settings/logging, domain/application ports, API v1/health and CI quality gates. |
| US-04 | Database and ORM | Done | Conceptual model, 3NF physical schema, SQLAlchemy models/constraints/ports, migrations and query strategy. |
| US-05 | Ingestion/publish pipeline | Done | Raw/staging/core/serving, validations, approval/publish, runbook and idempotency/failure tests. |
| US-06 | Published loan list/details | Done | Corrective persistent catalogue adapter plus API/UI/E2E delivered in PRs #21–#26. |
| US-07 | Questionnaire correctness/persistence | **In progress** | T01 and T02 done/merged; T03 is next. |
| US-08 | Recommendation engine | Pending | Starts only after all US-07 tasks are Done. |
| US-09 | Results and explainability UI | Pending | Starts only after US-08. |
| US-10 | Internal operations/authorization | Pending | Starts only after US-09. |
| US-11 | Security/operability hardening | Pending | Starts only after US-10. |
| US-12 | Release/production | Pending | Last story; starts only after US-11. |

### Completed stories/tasks in detail

#### US-01 — baseline and sources — Done

Completed work includes repository skeleton/baseline, source inventory/hash documentation, initial architecture/doc skeleton and risk documentation. These established the `.unitext` source files as official inputs and the rule that data must be traceable.

#### US-02 — data audit and decisions — Done

- Canonical identifiers/schema/parsers and data audit/provenance were built.
- `interestRate.Q5` was corrected in versioned decision/configuration to `0.10`, making the interest-rate weights total exactly `1.00`.
- Unknown/variable/blank handling was established for three deposit variables and four core variables (see section 10).
- Versioned golden fixtures were added.

#### US-03 — backend foundation — Done

- FastAPI settings, logging/dependency structure, application/domain ports and import-boundary checks were established.
- Typed API v1 errors and health/readiness endpoints exist.
- Formatting, lint, typecheck, test and CI quality-gate foundation exists.

#### US-04 — database/ORM — Done

- Conceptual model/ERD and documented 3NF physical schema exist.
- SQLAlchemy models, constraints, repository ports and Alembic migration verification are present.
- PostgreSQL migration verification is a CI gate. SQLite is not the sole authority for database correctness.

#### US-05 — ingestion and published serving data — Done

- Ingestion baseline, staging validation, typed normalisation/categories, approval/publish, import runbook and failure/idempotency coverage were completed.
- Core/serving changes happen only after approved import; provenance is retained.

#### US-06 — loan catalogue/detail — Done

| Task | State | Important result |
|---|---|---|
| T01 | Done | Framework-free `ListLoans`/`GetLoanDetails` use cases over serving-only catalogue port. |
| T02 | Done | Tight camel-case FastAPI allowlist schemas; raw conditions/provenance/internal asset references excluded. |
| T03 | Done | Pure conditions-to-bullets parser; plain text only, no HTML interpretation. |
| R01 corrective | Done, PR #24 | `SqlAlchemyServingLoanCatalogueRepository` filters `PublicationState.PUBLISHED`; draft/raw/staging/superseded data cannot become public. |
| T04 | Done, PR #25 | `GET /api/v1/loans/{loanId}` and RTL loan-details UI integration; loading/error/not-found/retry and no hard-coded details. |
| T05 | Done, PR #26 | Chromium E2E and CI gates for loading, 404, safe error/retry, RTL, XSS and invalid asset/link handling. |

**Known US-06 data limitation:** The persisted physical catalogue mapping did not yet carry the display-conditions source column through the durable adapter. Until approved import/persistence mapping supplies `LoanDetail.conditions_source_text`, the endpoint intentionally returns `conditions: []`; it must not invent conditions or fall back to prototype text.

#### US-07 — questionnaire — In progress

| Task | State | Important result |
|---|---|---|
| T01: versioned questionnaire config | Done, PR #27 | Approved source-traceable configuration with 10 canonical questions and 50 semantic/stable answers; loader rejects missing/reordered/duplicate/noncanonical answers. |
| T02: route adapter | Done, PR #28 merged 2026-09-19 | Sole bidirectional mapping between `/question/3..12` and `Q1..Q6,S7,S8,S10,S13`; legacy screen indexes are navigation-only. Fixed `/question/12` off-by-one redirect and now renders `S13`. |
| T03: session use case/retention | **Next; not started** | Start/save/validate short-lived anonymous server-side session, retention policy and no sensitive answer leakage. |
| T04: UI flow | Pending | Use canonical config and session API; next/back/resume and incomplete-answer state. |
| T05: route/API/E2E/accessibility | Pending | Complete story-level integration/E2E/RTL/accessibility gates. |

### Remaining stories/task decomposition — **Confirmed backlog**

| Story | Ordered tasks | Required outcome before next story |
|---|---|---|
| US-08 | T01 pure engine → T02 neutral/`needsReview` → T03 trace → T04 `RecommendLoans` use case → T05 unit/property/golden | Deterministic engine independent of FastAPI/React; unknown policy and redacted trace proven by tests. |
| US-09 | T01 result view model → T02 API integration → T03 distinct states → T04 manual filters/sort/a11y → T05 full E2E | No client-side score computation; ranked/needs-review/empty separated; RTL mobile/desktop E2E. |
| US-10 | T01 RBAC → T02 import/review/approve/rollback use case → T03 audit event → T04 protected internal endpoint/tool → T05 operations runbook | Ordinary client cannot change data/config/score; role/ownership/audit/rollback tested. |
| US-11 | T01 threat/privacy review → T02 app/transport hardening → T03 SAST/SCA/secret/DAST → T04 logs/metrics/alerts → T05 load/backup/restore | No critical/high findings or secret leaks; restore and rate/headers tests recorded. |
| US-12 | T01 docs review → T02 full CI → T03 preview/smoke → T04 release/rollback note → T05 reviewed production/post-deploy | All prior stories done, green full gate, preview/post-deploy smoke and tested rollback. |

---

## 8. Technical Architecture

### Architecture overview — **Confirmed target and partly implemented**

```text
React/Vite frontend (RTL user interface)
        │
        ├── questionnaire route adapter / future session + result clients
        │
FastAPI API v1
        │
application use cases / ports
        │
domain and pure recommendation engine
        │
SQLAlchemy infrastructure adapters
        │
PostgreSQL 3NF + Alembic migrations
        │
raw/staging/core/serving import and approval pipeline
```

Dependency direction is mandatory: `presentation → application → domain`; infrastructure implements ports and must not reverse-import presentation. React components call use cases/API clients, but never parse Excel, implement scoring formulas, or own data rules.

### Technology stack

| Layer | Technology / approach | State |
|---|---|---|
| Frontend | React + Vite; current prototype pages under `src/`; RTL UI | Existing and incrementally integrated |
| Backend | Python 3.12+, FastAPI | Implemented foundation/API |
| Database | PostgreSQL, SQLAlchemy, Alembic | Implemented local/CI architecture |
| Tests | Python unit/integration, Node tests, Playwright Chromium E2E, PostgreSQL migration verification | Implemented CI gates |
| Dev packaging | Docker/Docker Compose target architecture, non-root containers, local env docs/runbook | Foundation/docs expected; production deploy not complete |
| Hosting currently | Netlify frontend project `shahab-finance-demo` | Live frontend only; no live FastAPI/PostgreSQL |

### Backend structure/responsibilities

- `backend/app/.../domain`: entities, value objects, invariants and business rules.
- `backend/app/.../application`: use cases and ports; depends on abstractions, not database/UI.
- `backend/app/.../infrastructure`: SQLAlchemy repositories, importers, parsers and adapters.
- Loan catalogue: serving-only use cases and a durable SQLAlchemy read adapter with an explicit `PUBLISHED` predicate.
- Questionnaire: canonical configuration exists; session/use case is next.
- Recommendation: must be a pure engine/domain module, still pending.
- API: typed errors, health/readiness, public allowlisted loan detail responses are implemented.

### Frontend

Current operational code is in `src/`, principally the existing prototype screen and `src/App.css`; assets are in `assets/`. More focused modules added during delivery include:

- `src/features/loan-details/`: API client and RTL detail states; no hard-coded detail fallback.
- `src/features/questionnaire/questionnaireRouteMap.mjs`: the sole route ↔ canonical question ID adapter.

Current route requirements:

| Browser route | Canonical behavioural ID |
|---|---|
| `/question/3` | `Q1` |
| `/question/4` | `Q2` |
| `/question/5` | `Q3` |
| `/question/6` | `Q4` |
| `/question/7` | `Q5` |
| `/question/8` | `Q6` |
| `/question/9` | `S7` |
| `/question/10` | `S8` |
| `/question/11` | `S10` |
| `/question/12` | `S13` |

`/question/1` and `/question/2` are intentionally outside this behavioural canonical map. Legacy screen indexes are compatibility-only and must never be stored as answer IDs.

### Database

The target data model is normalized 3NF and versioned. Major domains include lender, loan product, loan product version, loan terms, questionnaire/configuration, import/audit/provenance and recommendation/session result data. Publication state separates draft/raw/staging/superseded from `PUBLISHED` serving data. Constraints, enums, foreign keys, uniqueness and migrations must be verified against PostgreSQL.

### AI/ML components

There is **no ML model currently planned or implemented**. The recommender is a data/configuration-driven deterministic decision engine. It may later evolve, but the current approved approach is transparent rules, weights, compatibility factors, candidate-tree traversal and reproducible traces.

### Infrastructure/deployment status

- Netlify site currently exists: `https://shahab-finance-demo.netlify.app/`.
- It is a frontend deployment; the public site is **not** backed by live FastAPI/PostgreSQL at present.
- Docker/Compose, health/readiness, migrations and CI are architectural preparation; production/staging service hosting, secrets, database, observability and rollback are still pending.

---

## 9. Architecture Decisions Record (ADR)

### ADR-01: Clean Architecture / ports and adapters

- **Status:** Confirmed.
- **Context:** Prototype concentrated interaction and static data in a large frontend implementation. Future data sources, admin workflow and recommendation rules require change isolation.
- **Alternatives considered:** Keep scoring/data parsing in React; build a monolithic route/component; tightly couple use cases to SQLAlchemy.
- **Final choice:** Feature/domain/application/infrastructure/presentation boundaries; inward dependencies; injected ports.
- **Reason:** Allows source, database, formula or UI changes without rewriting the engine or leaking business logic into UI.
- **Consequences:** More modules and tests are required; imports are validated; React/FastAPI cannot be dependencies of pure engine code.

### ADR-02: PostgreSQL 3NF with migration-tested schema

- **Status:** Confirmed.
- **Context:** Loan terms/configuration are versioned, auditable data, not transient screen JSON.
- **Alternatives considered:** Browser JSON only; direct Excel runtime reads; SQLite-only validation.
- **Final choice:** PostgreSQL + SQLAlchemy + Alembic, migration/constraint/rollback tests on real PostgreSQL.
- **Consequences:** A durable host/database is needed before public full-stack operation. SQLite can support narrow tests but is not the only oracle.

### ADR-03: Serving boundary for public loan data

- **Status:** Confirmed and implemented (corrective PR #24).
- **Context:** UI/API must not expose draft, raw, staging, superseded data or internal provenance.
- **Final choice:** Serving catalogue port/use cases plus `SqlAlchemyServingLoanCatalogueRepository` querying only `PublicationState.PUBLISHED`.
- **Consequences:** Any source/import data must be approved/published before public visibility. Absence of a mapping must produce empty/unknown state, not prototype fallback.

### ADR-04: Canonical IDs and route adapter

- **Status:** Confirmed and implemented (PR #28).
- **Context:** Existing public paths and prototype indexes do not equal stable questionnaire identity; `/question/12` previously redirected incorrectly.
- **Final choice:** One immutable route adapter maps the ten behavioural paths to canonical IDs and back. A separate bridge maps canonical IDs to legacy screen indexes.
- **Consequences:** Routes remain backward compatible, but only canonical `questionId`/`answerId` may be persisted/scored. No guessed mapping for malformed/nonbehavioural routes.

### ADR-05: Data-quality policy for unknown loan attributes

- **Status:** Confirmed.
- **Context:** The audited source has incomplete/variable values. Treating every unknown as a failing score would punish uncertainty; treating core unknowns as neutral would create false recommendation confidence.
- **Final choice:** Three deposit variables are neutral; four core variables exclude the loan from scored ranking. See section 10.
- **Consequences:** Engine must produce separate `rankedRecommendations` and `needsReview`; UI must distinguish insufficient data from no matching loan.

### ADR-06: Safe conditions rendering

- **Status:** Confirmed and implemented (US-06.T03–T05).
- **Context:** Conditions come from source text and may include bullets/newlines/untrusted markup.
- **Final choice:** Normalise into plain-text bullet strings; React renders text; no `innerHTML`, HTML generation or interpretation.
- **Consequences:** Empty conditions are a distinct “additional information unavailable” state, not loan absence.

### ADR-07: Recommendation engine is deterministic, explainable and server-side

- **Status:** Confirmed; implementation pending US-08/09.
- **Context:** Static client-side percentages are wrong and easily manipulable; user needs explanations.
- **Final choice:** Pure backend/domain engine with versioned configuration; server calculates score/rank and emits redacted trace. Client displays a view model and does not calculate score.
- **Consequences:** Requires completed questionnaire session API and approved data snapshot before live results.

### ADR-08: Public API protection approach

- **Status:** Under discussion; not yet an approved/implemented deployment ADR.
- **Context:** Product owner asked how to make backend public for frontend while preventing direct resource abuse with an API key.
- **Important security fact:** A key shipped in React/Vite/browser code cannot be secret and cannot secure the backend.
- **Proposed direction (not yet implemented):** Browser → same-origin Netlify Function/BFF → FastAPI, with service token only in server-side environment variables. Add rate limiting, short-lived anonymous sessions, input validation, HTTPS, narrow CORS, logging and later user auth/session.
- **Consequence:** A BFF prevents direct backend access without a service credential, but cannot stop an anonymous public visitor from using the public product flow. Real per-user control requires authentication/authorisation; anti-abuse requires rate limits/CAPTCHA/WAF as appropriate.

---

## 10. Data Model & Business Logic

### Canonical loan variables — **Confirmed order**

`maxAmount`, `monthlyInstallment`, `maxRepaymentMonths`, `interestRate`, `depositRequired`, `depositHoldingMonths`, `loanToDepositRatio`, `guaranteeType`.

Category counts from the official matrix:

| Variable | Category count / notes |
|---|---|
| `maxAmount` | 8 |
| `monthlyInstallment` | 6 |
| `maxRepaymentMonths` | 6 |
| `interestRate` | 5 |
| `depositRequired` | 2 |
| `depositHoldingMonths` | 5 |
| `loanToDepositRatio` | 4 |
| `guaranteeType` | 3: `hardCollateral`, `thirdPartyUndertaking`, `personalUndertaking` |

Boundary contracts must be single, documented and tested (for example: lower range includes its start; next range owns its own lower boundary).

### Confirmed data decisions

#### D-01: `interestRate.Q5` correction

| Field | Record |
|---|---|
| Earlier problem | Interest-rate matrix weights summed to approximately `1.05`. |
| Confirmed decision | `Q5` (repayment flexibility) weight for `interestRate` is `0.10`. |
| Effect | Total interest-rate question weight is exactly `1.00`. |
| Implementation rule | Record as a versioned data decision/configuration; do **not** silently mutate the raw official source. |

#### D-02: Neutral deposit variables

For `depositRequired`, `depositHoldingMonths`, and `loanToDepositRatio`, values `متغیر`, `نامشخص`, blank or unclassifiable are **neutral**:

- no positive or negative score contribution;
- removed from that loan’s effective-weight denominator;
- trace records `neutral: true` and the reason;
- not equivalent to incompatibility score zero.

#### D-03: Core-variable ranking exclusion

For `maxAmount`, `monthlyInstallment`, `maxRepaymentMonths`, and `interestRate`, values `متغیر`, `نامشخص`, blank or unclassifiable are **not neutral**:

- loan is excluded from `rankedRecommendations`;
- it enters `needsReview` with `rankingExcludedReasons`;
- it must never get a match score, rank or “compatible recommendation” label.

For a core `متغیر` value, importer may extract an explicit structured range/options only through versioned, tested rules. If ambiguous or inferred from free text, retain unknown; free-text guesswork is forbidden.

#### D-04: Display-only unknowns

`requiredDepositAccount` and other non-core/display fields may show `نامشخص`; this alone does not remove a loan from ranking.

### Known audit observations — do not hard-code

Audit of the 102-loan source observed, at the time of audit: 66 `دارد`, 34 `نامشخص`, 2 blank for deposit requirement; 37 unknown deposit-holding values; 54 unknown loan-to-deposit values. Example core cases included one unknown interest rate, 9 variable maximum amounts, 12 variable instalments and 4 variable repayment terms. These figures are evidence for the policy, not constants; recompute them on each audit.

### Target recommendation algorithm — **Confirmed specification, not yet implemented**

1. Validate answers: exactly one known `answerId` for each required canonical question.
2. Normalise loan data and classify all eight variables.
3. For each variable/category, derive compatibility from the one-to-one matrix and versioned question/answer weights.

```text
normalizedQuestionWeight = questionWeight × answerWeight
categoryScore(variable, category) = Σ(normalizedQuestionWeight × impactFactor)
```

4. Sort categories descending by score with deterministic `categoryId` tie-break.
5. Traverse a candidate tree in the eight-variable order; prune empty branches immediately.

```text
pathScore = Π(categoryWeight in path)
rawLoanScore = Σ(pathScore for all valid paths for that loan)
normalizedScore = rawLoanScore / max(rawLoanScore among candidates) × 100
```

6. Final ranking sort is only `normalizedScore DESC, stableLoanId ASC`. Traversal order must not determine rank. Do not introduce commercial secondary ranking.
7. `minimumMatchScore` is a versioned setting with initial value `50`; below-threshold loans remain in diagnostic trace but are not user results.
8. Return two separate collections: `rankedRecommendations` and `needsReview`.

### RecommendationTrace requirements — **Confirmed target**

Each recommendation run must produce a reproducible/redacted `RecommendationTrace` including:

- data and configuration versions;
- canonical input question/answer IDs;
- category scores and source references;
- valid paths and pruned/excluded reasons;
- neutral variables and effective weight;
- raw and normalized score;
- stable trace hash.

Never put identifying user data in public logs or a public trace.

### Required behaviour for edge cases

- Zero candidate: no error; offer review/expand answers and a return path.
- `rankedRecommendations` empty but `needsReview` nonempty: say data is insufficient for precise ranking; do not say no loan exists.
- Zero after manual UI filters: distinguish from zero compatible loans.
- Many results: do not silently truncate valid candidates merely to shorten a list.
- Conflicting preferences: do not “solve” them secretly; show nearest options/explanation.
- Every loan source needs `sourceUrl`, `sourceCheckedAt`, and `dataVersion`; newer official bank source outranks stale data.

---

## 11. Repository & Development Status

### Repository

| Item | Record |
|---|---|
| Platform | GitHub, private |
| URL | `https://github.com/Brotherlouiee/shahab-demo` |
| Default branch | `main` |
| Latest verified hand-off merge | PR #28, `feat(US-07.T02): add canonical questionnaire route adapter`, merged 2026-09-19; head commit `c0c1fd90b6616b873cb52996164532a08ab84176` |
| Important docs | `docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md`, `docs/project-current-state.md`, `docs/recommendation-data-decisions.md`, `docs/source-inventory.md`, `CHANGELOG.md`, database/data-pipeline/API/operations docs |
| Official sources | `.agents/documents/*.unitext` |

### Important delivered PRs

| PR | Purpose | State |
|---|---|---|
| #24 | Corrective durable PostgreSQL serving catalogue adapter, `PUBLISHED` filter | Merged |
| #25 | Loan details API/UI RTL integration | Merged |
| #26 | Loan detail browser E2E/CI coverage | Merged |
| #27 | Versioned canonical questionnaire configuration | Merged |
| #28 | Canonical questionnaire route adapter / route-12 correction | Merged |

### Quality evidence current at PR #28

- `npm run quality`: passed with 76 backend tests (two PostgreSQL integration tests may be skipped locally if service unavailable), 3 route-adapter tests, format, lint, typecheck, validators including source integrity, secret scan and production build.
- Chromium binary was unavailable in one local environment, but GitHub Actions run #46 installed pinned Chromium and passed quality gates, PostgreSQL migration verification and browser E2E including the all-routes case.
- CI is authoritative when local scratch is missing `.agents/documents/*.unitext` or browser/Python dependencies after a runtime reset; do not weaken/skip the corresponding gate to make local execution green.

### Known issues/limitations

1. **No live public backend/database.** Netlify is frontend only. API/UI integration exists in code/CI, not as a live internet full-stack service.
2. **Conditions hydration gap.** Durable SQLAlchemy catalogue adapter currently does not persist/display the source conditions field; it must return empty conditions rather than fabricate content.
3. **Questionnaire answers are still not persisted/server-submitted.** Current T02 solved navigation identity only. Existing UI local state/static behaviour must not be described as recommender integration.
4. **Static recommendation results/prototype artefacts remain.** They are not backed by the recommendation engine and must be replaced only in ordered US-08/US-09 work.
5. **SMS/OTP via Kavenegar is deferred** until legal registration; do not introduce fake live SMS integration.
6. **Current local environment may be incomplete.** Re-check actual dependencies and source files; use CI findings truthfully instead of bypassing validation.

---

## 12. Code Quality Standards

### Mandatory practices — **Confirmed**

- Clean Architecture and SOLID; feature-first organisation and narrow responsibility modules.
- Schema validation at all input boundaries.
- Pure engine/domain functions: no React/FastAPI/database imports.
- Repository/config/data dependencies injected through ports/interfaces.
- No raw source Excel/unitext parsing in browser runtime.
- All formulas, category boundaries, normalisation and tie-breaking documented and tested.
- Deterministic test fixtures; golden tests updated whenever configuration/model weights change.
- Add/change docs and `CHANGELOG.md` in every relevant PR. Keep a Changelog categories: Added, Changed, Fixed, Security, Deprecated, Removed.
- Typed, safe error responses; avoid hidden fallbacks.
- Code review before completion: security, performance, duplication, boundaries, comment/docstring quality.

### Testing requirements

| Area | Mandatory coverage |
|---|---|
| Data/import | schema, parser, source hash/integrity, audit, provenance, idempotency, atomic failure |
| Domain/engine | Persian parsing, category boundaries, scoring, pruning, path aggregation, normalization, threshold, ties, neutral, trace |
| Application | fake repository, incomplete answers, incomplete loan, snapshot/transaction behaviour |
| API | allowlist schemas, typed errors, validation, access controls when added |
| UI | canonical route map, safe conditions bullets, RTL, loading/error/empty/return states, accessibility |
| E2E/release | questionnaire completion/back/resume, results/detail/no-result/filter states, mobile/desktop, security text |
| Security | secret scan plus later SAST/SCA/DAST and threat/privacy review |

### Completion standard

No task can be marked Done merely because code compiles. It needs the task-specific tests, broad quality gate, documentation/checkpoint/CHANGELOG, commit, PR and green CI evidence appropriate to the task.

---

## 13. Security & Compliance Requirements

### Current confirmed requirements

- No secrets, API keys, credentials or personal data in repository/client code/logs.
- Public API returns only allowlisted loan facts; no raw provenance, draft data, serving version internals or unsafe asset references.
- Conditions text never executes as HTML.
- Questionnaire session data must not be placed in URL or public logs.
- Validation at every API/input boundary; typed error handling; least privilege for future internal functions.
- TLS, narrow CORS, secure headers, CSRF assessment, rate limiting, secret management and input limits are required in US-11.
- Admin/import/config/approval operations will require RBAC, ownership checks and append-only audit in US-10.
- Logs/traces must redact personal identifiers; retention/privacy policy is a US-11 deliverable.
- Database backups must be encrypted and restore rehearsed before production release.

### Public API-key clarification — **Confirmed security conclusion**

A static SPA cannot keep an API key secret. Any key inserted into a React/Vite browser bundle can be inspected and reused. Do not represent a browser API key or CORS as access control.

For a future deployment, use a server-side BFF/API proxy token kept only in server/hosting secrets for service-to-service authentication, combined with anonymous short-lived session controls, rate limits and later user authentication. This direction remains pending implementation/ADR approval (ADR-08).

---

## 14. Deployment & Operations

### Environments

| Environment | Current state | Requirement |
|---|---|---|
| Local | Intended Docker Compose with frontend, FastAPI and PostgreSQL | Must validate health/readiness, migrations, seed/import and smoke tests; do not delete volumes casually. |
| CI | Active GitHub Actions quality, PostgreSQL migration and Chromium E2E gates | Remains mandatory; do not disable gate due to local missing dependencies. |
| Preview/staging | Not established as full stack | Required before production; approved config/data version, smoke, monitoring and rollback. |
| Production | Not deployed for API/database | Only after US-12 release gate. |

### Existing hosting

- Netlify project: `shahab-finance-demo`.
- Current public site: `https://shahab-finance-demo.netlify.app/`.
- It serves frontend assets. It does not constitute a live FastAPI/PostgreSQL production deployment.

### Required future deployment foundation

Beyond server/domain, production readiness requires:

1. immutable Docker image build and registry/deployment pipeline;
2. managed or securely operated PostgreSQL;
3. migration sequencing and rollback/runbook;
4. server-side secret/configuration management;
5. frontend API endpoint configuration and CORS/HTTPS;
6. health/readiness checks and post-deploy smoke;
7. structured logs, metrics, alerts and incident runbook;
8. encrypted backups plus recorded restore rehearsal;
9. version rollback that can restore application and data/migration compatibility;
10. staging and production separation.

### Operational rules

- Production Compose/config is not the same as local development Compose.
- Never reset/delete a database volume without explicit target/environment confirmation and the documented runbook.
- Every changes to stack, ports, env, migration, dependency or command updates local-development docs, Docker runbook and CHANGELOG in the same PR.
- Final release is not valid until preview and post-deploy verification plus rollback exercise succeed.

---

## 15. Decisions Log

| Date/phase | Decision | Reason | Impact |
|---|---|---|---|
| US-01 | Six `.unitext` files are official source documents and must be hash-inventoried | Prevent undocumented source drift | All data/questionnaire/engine changes require source verification. |
| US-02 | `interestRate.Q5 = 0.10` | Original interest weights summed to ~1.05 | Interest variable total is 1.00 in versioned config/golden tests. |
| US-02 | Unknown deposit fields are neutral | Do not punish data absence as incompatibility | Exclude contribution from effective denominator and trace it. |
| US-02 | Unknown core loan fields exclude from ranking | Avoid false confidence in scored results | Separate `needsReview`; no score/rank. |
| US-03/04 | FastAPI + PostgreSQL 3NF + SQLAlchemy/Alembic + ports | Need traceable, maintainable, versioned service | Backend/database foundation and migration CI. |
| US-05 | Only approved/published versions can serve user-facing data | Raw/staging data must not reach users | Serving publication state and provenance pipeline. |
| US-06.R01 / PR #24 | Add durable SQLAlchemy catalogue adapter with `PUBLISHED` filter | T04 required a real serving boundary, not memory-only source | Draft/raw/staging/superseded blocked from loan use cases. |
| US-06 | Conditions are parsed/rendered as plain text, never HTML | Prevent XSS and source-text interpretation | Safe bullet UI and tests. |
| US-06 | Do not infer missing persisted conditions | Avoid fabricated loan terms | Return empty conditions until import/persistence mapping is complete. |
| US-07.T01 / PR #27 | Versioned canonical config: 10 questions, 50 answers | Stable questionnaire identity independent of UI | Later routes/session/engine use canonical IDs. |
| US-07.T02 / PR #28 | Exact route adapter; `/question/12 → S13` | Existing prototype index caused redirect/off-by-one defect | Public routes retained; indexes cannot become answer IDs. |
| Deployment discussion | Netlify currently frontend-only; backend needs separate real hosting/database | Static frontend cannot host full FastAPI/PostgreSQL architecture | Do not claim public full-stack integration yet. |
| API protection discussion | Browser API key is not a secret; use server-side BFF token + abuse controls | Keys in client bundle are extractable | Pending deployment ADR/implementation. |

---

## 16. Rejected Approaches

| Item | Reason rejected |
|---|---|
| Treat project as credit scoring/approval prediction | Product is decision support only; would change purpose and make misleading claims. |
| Hard-code loan data/conditions/recommendation percentages in JSX | Not traceable, cannot be safely updated and contradicts published-data rules. |
| Use raw/staging/draft/superseded records in public API | Violates serving boundary and provenance/approval policy. |
| Give neutral score to unknown core attributes | Would falsely elevate loans with missing amount/instalment/term/interest information. |
| Treat unknown deposit variables as zero incompatibility | Incorrectly punishes data uncertainty; policy is neutral exclusion from effective weight. |
| Guess structured terms from ambiguous free-form text | Creates unverifiable financial claims; only versioned/tested structured extraction is allowed. |
| Use URL numbers, screen indexes or option position as canonical answer IDs | Breaks when UI/order changes; canonical IDs are required. |
| Render conditions via `innerHTML` or sanitise/interpret HTML at display time | Plain-text only is the security contract. |
| Build recommendation scoring in React/client | Formula must be server/domain controlled, deterministic and traceable. |
| Start US-08/US-09 before completing US-07 | Violates enforced dependency order. |
| Fake full-stack deploy using hard-coded/API-mocked data | Would misrepresent operational status and violate data/serving rules. |
| Store a “secret” API key in React/Vite frontend | Any browser-delivered key is public. |
| Enable real Kavenegar SMS before legal registration | Explicitly deferred. |
| Skip CI source/browser gates because scratch lacks files/browsers | CI has full checkout and is authoritative; bypassing would weaken verification. |

---

## 17. Current Project State

- **Merged foundation:** US-01 through US-08, canonical questionnaire sessions, approved catalogue/configuration, deterministic engine and live result/detail/comparison code.
- **Merged US-09 work:** frontend refinements through PR #92; database-backed profile/mock-OTP access and authenticated recommendation history through PR #93 and its corrective commits.
- **Verified repository gate:** merged main `6d31bde` has all four CI jobs successful (see section 0B). Do not reuse old test totals as current suite counts.
- **Acceptance boundary:** the owner's current statement is “changes nearly complete”; final visual/local acceptance and actual hosted database state are not independently established by this document.
- **Remaining story gate:** US-09.T07 actual deployment and real-URL/restart verification. US-09 is not declared complete; real SMS, production auth, US-10–US-12 and production release remain outside this completion claim.

---

## 18. Immediate Next Actions

| Priority | Action | Boundary |
|---|---|---|
| P0 | Safely synchronize the owner's local IDE with merged main and verify required migrations | Inspect local edits; no discard, forced push or database reset. |
| P0 | Record final owner acceptance of history access, empty state and card geometry | Correct only observed defects in a new scoped PR; preserve exact approved design. |
| P1 | Complete US-09.T07 on explicitly selected real infrastructure | Persistent database/publication, API HTTPS, Netlify, real URL and restart evidence. |
| P1 | Record staging/rollback and relevant security/session decisions | Local mock and process-local account store are not production authentication. |
| P2 | Close US-09 only after the complete story gate; then select US-10 work | Do not restart completed US-07/08 tasks from old checkpoints. |

---

## 19. Open Questions

| Question | Current state |
|---|---|
| Has the owner accepted the final history UI/flow in the updated local stack? | Nearly complete per owner; explicit final acceptance remains to be recorded. |
| Which server/domain/access and secret management will support T07? | Not established by this documentation refresh. |
| Does the actual Netlify URL reach the selected persistent API/database? | Requires fresh real-URL acceptance; CI success is insufficient. |
| When will real SMS/provider credentials and production authentication be enabled? | Deferred; no API key or production activation supplied/claimed here. |
| How will production sessions, cross-host cookie/CSRF and multi-worker/restart behavior be handled? | Must be resolved before production; current account state is process-local. |
| What retention/erasure policy applies to persistent recommendation history? | Raw answers keep their 30-minute policy; hide preserves records. Formal durable-history privacy/retention and authorized erasure require explicit decisions. |
| What operational cadence updates/approves catalogue data? | Existing versioned publication rules remain; operational cadence needs release planning. |

---

## 20. Knowledge Transfer Notes

### Critical distinctions a new chat must keep

1. **“Connected in code” is not “deployed live.”** Loan details are connected to API in code and CI; public Netlify has no live FastAPI/PostgreSQL.
2. **Questionnaire route mapping is not answer persistence.** PR #28 was navigation-only; later US-07/08/09 work implements server answer persistence and recommendation. Do not infer current status from PR #28 alone.
3. **Published data boundary is real.** Do not repair an empty detail field by returning raw/staging/prototype data.
4. **Neutral is not zero.** Neutral removes a non-core unknown variable from both contribution and denominator; it does not penalise or reward the loan.
5. **Core unknown is exclusion, not neutral.** No score or rank for those loans.
6. **Source conflict requires a documented decision, not an implementation guess.** Production is blocked when relevant data decisions are unapproved.
7. **The project already has an exact task order.** New work must not use a “faster” UI shortcut that effectively implements later stories early.

### Past pitfalls and lessons

- A prior `US-06.T04` attempt was correctly blocked because serving data persistence did not exist; a corrective PR (#24) was created first. This is the expected behaviour: resolve true dependency, then continue, rather than ship a hard-coded workaround.
- `/question/12` exposed an off-by-one prototype screen-index defect. Canonical route map tests and browser tests now protect it. Do not reintroduce raw index arithmetic.
- Local environment failures (missing Chromium, reset Python dependencies, missing raw sources in scratch) are environmental, not permission to erase/skip gates. Report them, use CI evidence and restore proper local environment when needed.
- Conditions are deliberately strict: strings that resemble HTML remain text. Security is preferred over rich formatting.

### Required per-task handoff/checkpoint record

`docs/project-current-state.md` must accurately state: active task ID, base/current commit, branch, full guide/source read attestation, completed scope, test results, CI evidence, blocker/open decision and the one next task. This is the operational source of short-term continuity; this broader document is the new-chat handoff.

---

## 21. Glossary

| Term | Meaning |
|---|---|
| Canonical ID | Stable internal identifier (for example `Q1`, `S13`, `answerId`) independent of screen order or Persian label. |
| `.unitext` | Versioned project source-document format in `.agents/documents/`; current official business/data sources. |
| Serving data/version | Approved, user-facing loan data. Only `PUBLISHED` records may cross public catalogue boundary. |
| Raw/staging/core | Earlier data-pipeline layers: raw capture, validation staging and normalised internal core; not public output. |
| `needsReview` | Loans lacking a classifiable core attribute; shown with reason but never ranked/scored. |
| Neutral | Unknown/variable value for one of three deposit variables; excluded from score contribution and effective denominator. |
| Core variables | `maxAmount`, `monthlyInstallment`, `maxRepaymentMonths`, `interestRate`; unknowns exclude from ranking. |
| RecommendationTrace | Redacted, versioned explanation of scoring inputs, category/path decisions, exclusions and score. |
| BFF | Backend for Frontend: server-side proxy/function that can hold service credentials unavailable to browser code. |
| PR | Pull Request: small reviewable unit of change, with tests/docs/checkpoint and CI. |
| Golden test/fixture | Fixed scenario/assertion that protects important business behaviour from regression. |
| Quality gate | Mandatory collection of formatting, lint, typecheck, validators, tests, secret scan/build and/or CI checks. |

---

## 22. Instructions For New Chat

1. Read this document, especially authoritative section 0B, and inspect fresh main/PR/CI state. This handoff represents PR #93, not the older PR #28 or #60 snapshots.
2. Read the complete canonical guide and preserve the Three Golden Rules. For engine/data/questionnaire/result/database changes, read required official sources and related ADR/data decisions.
3. Preserve confirmed product/data/security decisions, particularly D-005, PUBLISHED-only serving, unknown-core exclusions and deposit neutral policy.
4. Do not restart completed US-07 or US-08 work. Resolve any confirmed owner acceptance defects, then pursue the remaining US-09.T07 gate unless the owner explicitly changes priority.
5. Use a fresh scoped branch from current main; protect local IDE edits. PR #93 is merged, so further implementation needs a new PR.
6. Separate database-backed recommendation history from browser-local bookmarks; preserve owner proof, atomic idempotency, immutable output and hidden-run retention.
7. Keep loading, valid empty response and request/authentication error separate; reuse supplied empty-state assets and existing result components without unsolicited design changes.
8. Update relevant docs, CHANGELOG and current checkpoint with evidence, then verify required CI on the final commit. Continuity normally updates at story completion; this v12 refresh was explicitly requested by the owner.
9. Do not claim CI/local code equals deployment. Require real infrastructure, URL, restart and rollback evidence for the deployment/story gate.
10. Keep credentials out of code, URLs, logs and browser storage. Fake OTP and process-local account access are development-only; real SMS/production security remain deferred.

---

## Audit of This Continuity Document

- Version 12 reconciles main after PR #93, records both feature and merge CI evidence, and removes the obsolete US-07.T03 next-action queue from current sections.
- Historical checkpoints are retained with explicit precedence; their old status, host names and test counts do not define current reality.
- Profile creation/persistence, session restoration, questionnaire ownership proof, history snapshot/cursor/hide behavior, migrations and bookmark separation are documented.
- No full US-09 completion, production authentication, deployed database or final independent visual acceptance is asserted.
- Next work is evidence-based owner acceptance and US-09.T07 real deployment; no runtime, schema, data, scoring or design changes are made by this document.
