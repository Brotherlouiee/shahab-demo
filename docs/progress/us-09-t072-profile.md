# US-09.T072 — Profile access and persistence repair

## Start checkpoint — 2026-10-09

- Codex-owned branch from main `5fb92c1db7109132f9bd883d2ac0bad45dc698bd`; remote operations use the authenticated GitHub API because shell Git transport has no credentials. Local files are a review/test snapshot, not the user's IDE checkout.
- Full canonical guide read: blob `e949af5add0058c1f9cd66e9f55cb5e254759183`. Three golden rules confirmed: limited staged development, full-guide review, evidence before Done.
- estimatedWorkScope: repair profile ownership and local/test OTP verification, personal-info persistence, failure feedback, phone normalization and inconsistent documentation.
- completionBudget: one coherent repair PR with API/security tests, client tests, E2E, quality and migration checks; no production deployment or SMS provider work.
- acceptance: anonymous/cross-account access denied; mock disabled outside explicit local/test; OTP expiry/attempts/revocation tested; personal-info persisted only after verification; failed storage blocks progression and remains retryable; full 11-digit phone preserved; docs match schema/API.
- baseline: import-boundary check passed. Existing profile API uses phone as authorization and catches storage failures silently. The existing `user_profiles` migration will be reused without destructive changes.
- test plan: targeted Python API tests; Node phone/client tests; browser personal-info/profile retry and login tests; CI quality, real PostgreSQL migration verification and browser suite.
- raw recommendation sources, D-005, score, published catalogue, questionnaire TTL and story continuity document remain unchanged.

## End checkpoint

Implementation and acceptance checks passed on PR #86 head `b3b14fb3cda237f30787bd17a0a5a0d916ff03ac`. GitHub Actions run [37924268911](https://github.com/Brotherlouiee/shahab-demo/actions/runs/37924268911) passed all three required jobs: Quality gates, browser verification, and real PostgreSQL migration/persistence verification. This documentation-only checkpoint commit must also pass the final PR checks before merge. No merge or deployment performed.

## Validation checkpoint

- Backend: 136 tests passed, 5 PostgreSQL-dependent skips without a local DB; targeted ownership/session tests and two client tests passed. Build passed; mypy, targeted Ruff, boundaries and secret scan passed.
- Full local quality is not claimed: one large existing logo asset is absent from the partial test snapshot. Browser download was blocked/truncated; required browser and real PostgreSQL checks run in GitHub Actions.
- Scope closed for implementation and acceptance validation. Final merge readiness requires green CI on the latest documentation checkpoint head. No deployment or local user DB mutation.

## Official source inventory (all six Git blob hashes verified; no source edits)

- `.agents/documents/تبدیل پاسخ‌ها به وزن‌های عددی.unitext`: `f14d0d82a13708e87eea93c1d96ff14f4797c10b`
- `.agents/documents/دیتابیس وام های بانکی.unitext`: `0854a5c3ad6b7640ddb7d6d9ae24ae0b2a4733fc`
- `.agents/documents/ضرایب تناسب یک به یک گزینه‌های هر یک از سئوالاتسناریوها با هریک از دسته بندی‌ها متغیرهای وام.unitext`: `7eeed38450067f7fe3ba6be4846999d768ed697c`
- `.agents/documents/ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام.unitext`: `2721940cdc5ae17fc952d20f947d949a61317fcd`
- `.agents/documents/ماتریس گزینه های متغیرهای وام.unitext`: `f2121e0e7f109d03cce432e4119978ba51ebb915`
- `.agents/documents/پرسشنامه سنجش متغیرهای رفتاری.unitext`: `26c70261829442e0676b85ac552bd6f7255f5faf`

## Verified first-login profile creation — 2026-10-09

Owner clarification: after entering a phone and successfully verifying mock OTP `123456`, the API creates the actor's `user_profiles` record before issuing access. Requesting a code or submitting an invalid code does not create a profile. Repeated login reuses the record without erasing name, income, job, gender or avatar. Personal-info then updates that same database profile before analysis. Creation failure returns 503 without issuing access; resend a code to retry. Existing migration is reused. Real SMS provider remains deferred until the owner supplies its API key; mock remains explicitly local/test. API tests and a real PostgreSQL HTTP integration test cover creation, persistence and repeat login. Follow-up CI must pass before merge.

Sidebar owner clarification: show the server profile name; use «کاربر» for a phone-only profile without a name. Refresh the owned profile when opening the menu with a valid capability. Personal-info uses the confirmed server response. Browser regression verifies named and unnamed profiles.
