import { test, expect } from "@playwright/test";

// Every test uses the real FastAPI/PostgreSQL service and unmodified Swagger assets.
// Independent operations have independent existing test budgets; no API fixtures.
// Preserve action/network/screenshot traces; avoid repeated full Swagger DOM copies.
// Playwright still writes the final error-context DOM when an assertion fails.
test.use({ trace: { mode: "retain-on-failure", snapshots: false, screenshots: true, sources: true } });

test.beforeEach(async ({ page }) => {
  await page.goto("http://127.0.0.1:8000/docs", { waitUntil: "domcontentloaded" });
});

test("Swagger lists all operations and preserves account security declarations", async ({ page }) => {
  const schemaResponse = await page.request.get("http://127.0.0.1:8000/api/v1/openapi.json");
  expect(schemaResponse.ok()).toBe(true);
  const schema = await schemaResponse.json();
  const methods = new Set(["get", "post", "put", "delete", "patch", "head", "options"]);
  const count = Object.values(schema.paths).flatMap(path => Object.keys(path).filter(method => methods.has(method))).length;
  expect(count).toBe(19);
  for (const method of ["get", "put", "delete"]) expect(schema.paths[method === "get" ? "/api/v1/bookmarks" : "/api/v1/bookmarks/{loan_id}"][method].security).toEqual([{ AccountBearer: [] }, { AccountCookie: [] }]);
  await expect(page.locator(".opblock")).toHaveCount(count);
});

test("Swagger executes a real public health request", async ({ page }) => {
  const live = page.locator(".opblock").filter({ has: page.locator('.opblock-summary-path[data-path="/api/v1/health/live"]') });
  await live.locator(".opblock-summary").click();
  await live.getByRole("button", { name: "Try it out", exact: true }).click();
  const [response] = await Promise.all([
    page.waitForResponse(reply => new URL(reply.url()).pathname === "/api/v1/health/live" && reply.request().method() === "GET"),
    live.getByRole("button", { name: "Execute", exact: true }).click(),
  ]);
  await response.finished();
  expect(response.status()).toBe(200);
  await expect(live.locator(".live-responses-table tbody .response-col_status")).toHaveText(/^200(?:\s|$)/);
  await expect(live.locator(".live-responses-table")).toContainText('"ok"');
});

test("Swagger rejects an unauthorized real profile request", async ({ page }) => {
  const profile = page.locator(".opblock").filter({ has: page.locator('.opblock-summary-path[data-path="/api/v1/profiles/me"]') });
  await profile.locator(".opblock-summary").click();
  await profile.getByRole("button", { name: "Try it out", exact: true }).click();
  const [response] = await Promise.all([
    page.waitForResponse(reply => new URL(reply.url()).pathname === "/api/v1/profiles/me" && reply.request().method() === "GET"),
    profile.getByRole("button", { name: "Execute", exact: true }).click(),
  ]);
  await response.finished();
  expect(response.status()).toBe(401);
  await expect(profile.locator(".live-responses-table tbody .response-col_status")).toHaveText(/^401(?:\s|$)/);
  await expect(profile.locator(".live-responses-table")).toContainText("correlationId");
});

