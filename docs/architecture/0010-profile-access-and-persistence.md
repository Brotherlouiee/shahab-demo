# ADR 0010 — Profile access and persistence repair (US-09.T072)

Status: accepted within the owner's request to repair PR #85, 2026-10-09.

PR #85 exposed personal profiles by phone without ownership checks and silently fell back to browser cache on failed writes. Personal-info did not persist to PostgreSQL and complete phone numbers were truncated.

Reuse the existing user_profiles table/migration. GET /profiles/me selects the server-owned actor; PUT /profiles compares normalized payload phone against that actor. The public GET /profiles/{phone} route is removed. Client phone, localStorage and React login state are not authorization.

Real SMS/Kavenegar remains out of scope under the canonical guide. Under the T073 owner-authorized local repair, local/test demo OTP is enabled by default; SHAHAB_PROFILE_MOCK_OTP_ENABLED=false explicitly disables it. Staging/production reject the mock even with the flag enabled. This is development verification, not real phone ownership or production authentication.

Challenges expire after 120 seconds, permit five attempts and are single-use. Request quota is five per phone/client in 120 seconds. A bounded, locked process-local store retains token digests, expires capabilities after 30 minutes and revokes them on logout. API restart invalidates access. Shared production/multiple-worker sessions require a separate adapter and real authentication gate.

Bearer capability is held only in the active tab's module memory, never URLs, browser storage or logs. Refresh requires development login again. Existing browser caches remain display/draft conveniences, not authentication; anonymous questionnaire session policy is unchanged.

Personal-info requires server verification plus confirmed persistence before analysis. Failed storage stays on verification and can retry using the still-valid capability. Existing gender/avatar survive personal-info updates. Profile writes preserve the draft on error and update confirmed caches only after server success. Full eleven-digit Latin/Persian/Arabic phone numbers retain their identity.

API tests cover anonymous/forged access, ownership, expiry, attempts, single use, quota, logout, production denial, schema and storage errors. A PostgreSQL migration test verifies persistence through a new connection. Browser tests cover both forms' retry paths.

No new migration/dependency, design, About copy, loan data, D-005 or questionnaire TTL changes. Disable the local mock flag and restart to close access without deleting profiles. Do not restore the vulnerable unauthenticated endpoints as rollback. Production remains blocked pending real authentication/security release work.

## Current precedence — US-12.T01 documentation audit, 2026-10-18

The process-local 30-minute capability and refresh/restart-login descriptions above record T072, not current runtime. US-11.T02A.2 replaces phone ownership with account UUID; T02C supplies PostgreSQL-shared challenges, quotas, absolute one-hour sessions and durable revocation. T02F restores account state without browser credential storage and adds account-owned bookmarks. See the [session contract](../security/account-session-lifecycle.md), [bookmark contract](../security/account-bookmarks.md) and [current API matrix](../api/coverage.md). Questionnaire TTL remains 30 minutes. Main still uses local/test mock OTP; the Kavenegar proposal in PR #133 is unmerged at the audit baseline.

## Verified first-login profile creation — 2026-10-09

Owner clarification: after entering a phone and successfully verifying mock OTP `123456`, the API creates the actor's `user_profiles` record before issuing access. Requesting a code or submitting an invalid code does not create a profile. Repeated login reuses the record without erasing name, income, job, gender or avatar. Personal-info then updates that same database profile before analysis. Creation failure returns 503 without issuing access; resend a code to retry. Existing migration is reused. Real SMS provider remains deferred until the owner supplies its API key; mock remains explicitly local/test. API tests and a real PostgreSQL HTTP integration test cover creation, persistence and repeat login. Follow-up CI must pass before merge.

## US-11.T02A.2 — انتقال اجرایی هویت

قرارداد phone-PK اولیه بالا تاریخی است؛ identity اکنون AccountActor.account_id و profile PK/FK accounts است. payload phone فقط برابر phone actor بررسی می‌شود؛ GET/PUT با ID همان generation و active DB انجام می‌شوند. atomic creation، read lock در برابر archive، partial unique race و یک ورود مجدد بعد از cutover؛ TTL/store/OTP provider همان قبلی.
