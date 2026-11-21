# Testing documentation

برنامه و evidence تست‌های unit، integration، API، E2E، data-audit، security و release gate در این پوشه ثبت می‌شوند. هر تسک فقط با تست مرتبطِ سبز قابل عبور است.

## US-06.T04 evidence

`backend.tests.test_loan_detail_api` uses an approved-serving repository override
to verify the versioned detail response, parsed plain-text bullets, omitted
internal fields, typed absent-detail response and typed unavailable-catalogue
response. `npm run build` compiles the active RTL React integration. Browser/E2E
coverage for loading, error, empty, invalid logo/link and XSS rendering remains
the explicit scope of `US-06.T05`.

## US-06.T05 browser and API verification

`npm run test:e2e` runs four Chromium tests in `tests/e2e/loan-details.spec.mjs`.
They use deterministic HTTP route interception rather than a prototype-data
fallback, and cover: RTL approved-detail rendering, a pending loading response,
typed 404/absent detail, and typed 503/safe retry. The approved-detail test
deliberately supplies an HTML-looking condition plus `javascript:` logo/link
fields: the condition must remain escaped text, no script may execute, and the
unallowlisted asset/link fields must not reach the DOM.

`backend.tests.test_loan_detail_api` additionally protects the HTTP boundary:
the response is JSON, omits internal fields, returns typed unavailable/not-found
responses, and is intentionally public because it exposes only approved
catalogue facts. No user credential, session, source-version selector or
authorization bypass is accepted by the route.

CI installs the pinned Chromium revision and executes the browser command in
the separate `Loan details browser verification` job. Local execution requires
`npx playwright install chromium`; a browser-download failure is environmental,
not a reason to remove or skip the CI gate.

GitHub Actions run #37 completed the browser job successfully, alongside the
repository quality and PostgreSQL migration jobs.

## US-07.T02 route-contract verification

`npm run test:questionnaire-route-map` runs the framework-free route-adapter
tests. They cover all ten immutable behavioural paths in both directions,
legacy prototype-index bridging, and rejection of unmapped/non-behavioural
paths. `tests/e2e/questionnaire-route-map.spec.mjs` visits all ten public
routes and verifies their screen heading. The route-unit command is part of
`npm run quality`; neither test submits answers, creates a session, or
calculates a recommendation.
