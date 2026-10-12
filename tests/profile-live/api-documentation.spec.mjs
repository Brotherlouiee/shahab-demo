import { test, expect } from "@playwright/test";

// This suite already runs FastAPI with PostgreSQL. No HTTP route fixtures:
// Try it out must send to the real API and retain the runtime authorization rules.
test("Swagger lists every operation and executes real authorized-boundary requests", async ({ page }) => {
  await page.goto("http://127.0.0.1:8000/docs");
  const schemaResponse = await page.request.get("http://127.0.0.1:8000/api/v1/openapi.json");
  expect(schemaResponse.ok()).toBe(true);
  const schema = await schemaResponse.json();
  const methods = new Set(["get", "post", "put", "delete", "patch", "head", "options"]);
  const count = Object.values(schema.paths).flatMap(path => Object.keys(path).filter(method => methods.has(method))).length;
  expect(count).toBe(19);
  for (const method of ["get", "put", "delete"]) expect(schema.paths[method === "get" ? "/api/v1/bookmarks" : "/api/v1/bookmarks/{loan_id}"][method].security).toEqual([{ AccountBearer: [] }, { AccountCookie: [] }]);
  await expect(page.locator(".opblock")).toHaveCount(count);
  const live = page.locator(".opblock").filter({ has: page.locator('.opblock-summary-path[data-path="/api/v1/health/live"]') });
  await live.locator(".opblock-summary").click();
  await live.getByRole("button", { name: "Try it out", exact: true }).click();
  await live.getByRole("button", { name: "Execute", exact: true }).click();
  await expect(live.locator(".live-responses-table tbody .response-col_status")).toHaveText(/^200(?:\s|$)/);
  await expect(live.locator(".live-responses-table")).toContainText('"ok"');
  const profile = page.locator(".opblock").filter({ has: page.locator('.opblock-summary-path[data-path="/api/v1/profiles/me"]') });
  await profile.locator(".opblock-summary").click();
  await profile.getByRole("button", { name: "Try it out", exact: true }).click();
  await profile.getByRole("button", { name: "Execute", exact: true }).click();
  await expect(profile.locator(".live-responses-table tbody .response-col_status")).toHaveText(/^401(?:\s|$)/);
  await expect(profile.locator(".live-responses-table")).toContainText("correlationId");
});
