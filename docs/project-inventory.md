# Project inventory — US-01.T02

## Scope and evidence

This inventory documents the existing prototype without changing its behavior. It is based on the `main` baseline commit `6f406146b9020bf20ea0ba786ee8f959400c307d` and the `US-01.T01` baseline record.

## Runtime and entry points

| Area | Current state | Migration implication |
| --- | --- | --- |
| Application entry | `src/main.jsx` renders `src/home page.jsx` in `React.StrictMode`. | `home page.jsx` is the active product composition root and must be decomposed gradually, not rewritten in one step. |
| Routing | Custom `window.history.pushState`, `popstate`, and pathname parsing; no router dependency. | Preserve public paths with a route adapter before replacing routing internals. |
| Styling | One `src/App.css` file with 5,218 lines. | Extract styles only with a dedicated characterization/UI task; no opportunistic reformatting. |
| Legacy JSX | `src/App.jsx` and `src/Section1 & Q1.jsx` are present but are not imported by `src/main.jsx`. | Treat them as unused prototype artifacts until a later inventory/cleanup decision; do not delete them now. |
| Hosting | Netlify static build: `npm run build`, publish `dist`, SPA fallback to `index.html`. | Current frontend deploy is static-only; no API/server runtime exists. |

## Current dependencies and quality tooling

| Category | Installed/observed state |
| --- | --- |
| Runtime packages | `react@19.2.6`, `react-dom@19.2.6`, `vite@8.0.14`, `@vitejs/plugin-react@6.0.2` from the committed lockfile. |
| Scripts | Only `dev`, `build`, and `preview`. |
| Missing controls | No lint, formatter, typecheck, unit test, E2E test, CI workflow, backend package, migration, Docker, or Compose configuration. |
| Build status | `npm ci` and `npm run build` passed in `US-01.T01`; rerun for this documentation-only task is required before closure. |

## Route inventory

| Path or pattern | Current view/behavior | Product status |
| --- | --- | --- |
| `/` | Marketing home; can start questionnaire or open demo login. | UI prototype. |
| `/login`, `/login/otp` | Client-only phone/OTP screens. | Mock; no server identity or verification. |
| `/question/1`, `/question/2` | Preliminary loan-type and applicant-type choices. | UI-only; not part of canonical recommendation mapping. |
| `/question/3` … `/question/8` | Six behavioral questions. | Must later map to canonical `Q1` … `Q6`. |
| `/question/9`, `/question/10`, `/question/11`, `/question/12` | Four scenario questions, with `/question/12` rendered as personal information. | Must later map to `S7`, `S8`, `S10`, `S13`; current screen order is not a domain contract. |
| `/personal-info`, `/verify-code`, `/analysis` | Profile entry, mock OTP, and timed analysis transition. | Client-only temporary flow. |
| `/loan-results`, `/loan-details`, `/loan-request`, `/compare-loans`, `/compare-result`, `/ai-analysis` | Hard-coded result, details, request, comparison, and analysis views. | Replace only through later API/presentation tasks. |

## Mock and hard-coded behavior

| Area | Observed implementation | Required future handling |
| --- | --- | --- |
| Loan recommendations | `loanResultPlans` is a four-record in-memory list with repeated entries and fixed match percentages. | Replace in `US-08`/`US-09` with server-calculated, traceable recommendation data. |
| Loan details | Conditions and displayed values are in JSX. | `US-06` must use the approved serving data and parse the database conditions field. |
| Questionnaire | Twelve screen objects and options live in `QuestionnaireScreen`; answers are keyed by screen index. | `US-07` must create canonical `questionId`/`answerId` adapters and preserve public routes. |
| OTP | Login is UI-only; questionnaire OTP accepts the hard-coded Persian code `۱۲۳۴۵۶`. | Keep mock OTP behind the provider port; remove client-side acceptance before production auth. |
| Analysis | An eight-second client timer transitions to loan results. | Replace only after the recommendation use case/API exists. |
| Persistence | Personal first name, last name, phone, and account profile are written to `localStorage`. | `US-07`/security work must remove or redesign this handling under the privacy/retention policy. |
| Network calls | No `fetch`, Axios, Firebase, Supabase, or other application API client is present. | The future frontend must call a versioned API contract rather than databases or source documents. |

## Assets and external dependencies

- Local logo, UI icon, and Iranian bank-logo assets are used through normal Vite imports and `import.meta.glob`.
- Two marketing cards use remote Unsplash URLs. This is an external rendering dependency and needs a fallback/allowlist decision in the security/UI hardening tasks.
- `design/icons.zip` exists as a supplied design asset; the application currently uses individual assets instead of reading the ZIP at runtime.

## Risks and decisions for later tasks

1. The active entry module is approximately 2,935 lines and the stylesheet approximately 5,218 lines. Do not perform a broad cleanup before architecture boundaries and characterization tests exist.
2. Public routes and the current visual flow are compatibility constraints; a future router/API migration needs route-level regression tests.
3. The local-storage use of personal data and the client-side OTP are known prototype-only behavior, not production security controls.
4. `package.json` uses `latest` ranges. The lockfile currently resolves the tested versions, but package policy, pinning, scanning, and CI belong to `US-03.T05`.
5. There is no backend or database in the current repository; FastAPI/PostgreSQL/Docker must be introduced in their assigned tasks, not hidden inside this inventory task.

## Golden-rule attestation

1. This task is documentation-only and incremental; no deploy occurred.
2. The complete canonical guide was reread before execution.
3. Closure requires this inventory, current-state/CHANGELOG updates, a successful baseline build, and a dedicated commit.
