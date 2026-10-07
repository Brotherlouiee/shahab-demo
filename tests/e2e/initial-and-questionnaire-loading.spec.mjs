import { expect, test } from "@playwright/test";

test("shows the document fallback only after a delayed first paint", async ({ page }) => {
  await page.route("**/src/main.jsx", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 90));
    await route.continue();
  });

  await page.goto("/");
  await expect(page.locator("#initial-page-skeleton")).toBeVisible();
  await expect(page.locator("#root")).toBeEmpty();
  await expect(page.getByRole("button", { name: "ورود" })).toBeVisible();
  await expect(page.locator("#initial-page-skeleton")).toHaveCount(0);
});

test("shows a delayed skeleton while a canonical questionnaire answer is saved", async ({ page }) => {
  let releaseSession;
  await page.route("**/api/v1/questionnaire/sessions", (route) => new Promise((resolve) => {
    releaseSession = async () => {
      await route.fulfill({ status: 201, json: { sessionId: "test-session", expiresAt: "2027-01-01T00:00:00Z", answers: {} } });
      resolve();
    };
  }));
  await page.route("**/api/v1/questionnaire/sessions/*/answers/*", (route) => route.fulfill({
    json: { sessionId: "test-session", expiresAt: "2027-01-01T00:00:00Z", answers: {} },
  }));

  await page.goto("/question/3");
  await page.getByRole("radio").first().click();
  await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();

  const skeleton = page.getByRole("status", { name: "در حال بارگذاری" });
  await expect(skeleton).toBeVisible();
  await releaseSession();
  await expect(page).toHaveURL(/\/question\/4$/);
});

test("renders the one-loan comparison action as visibly disabled", async ({ page }) => {
  await page.setContent(`
    <button class="hp-simple-compare-submit" disabled>مقایسه کن (۱ وام)</button>
  `);
  await expect(page.getByRole("button", { name: /مقایسه کن/ })).toBeDisabled();
  await expect(page.getByRole("button", { name: /مقایسه کن/ })).toHaveCSS("cursor", "not-allowed");
  await expect(page.getByRole("button", { name: /مقایسه کن/ })).toHaveCSS("background-color", "rgb(140, 140, 140)");
});
