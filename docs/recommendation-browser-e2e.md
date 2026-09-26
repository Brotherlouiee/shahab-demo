# Browser E2E contract for recommendation results

## Scope — US-09.T05

This task runs the existing recommendation transport client and RTL/a11y result screen in Chromium, with controlled HTTP responses at the API boundary. It then follows the same encoded loan-details route used by a ranked result and verifies approved conditions in the detail screen.

The browser fixture is under `tests/e2e/fixtures/`; it is not imported by the production entrypoint and creates no product route or static recommendation data.

## Assertions

- the opaque same-tab session ID is sent only in the POST JSON body;
- the client validates the server read model before rendering it;
- server score is displayed but never calculated in the browser;
- `needsReview` is visually separate and score-free;
- manual lender filtering and display sort are usable in RTL;
- typed result error is safe and retryable;
- the result link reaches the detail UI, which renders conditions as text.

## Boundary

The responses are controlled test fixtures, not a live recommendation service. `US-09.T06` remains responsible for connecting the real questionnaire session, recommendation endpoint, server engine, published-serving data, and a product-owner-testable preview URL. Therefore this task is browser E2E coverage of the client-to-detail contract, not evidence of live recommendation delivery.
