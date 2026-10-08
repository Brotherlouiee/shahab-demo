import { expect, test } from "@playwright/test";

test("shows the document fallback only after a delayed first paint", async ({ page }) => {
  await page.route("**/src/main.jsx", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 90));
    await route.continue();
  });

  const navigation = page.goto("/", { waitUntil: "commit" });
  await expect(page.locator("#initial-page-skeleton")).toBeVisible();
  await expect(page.locator("#initial-page-skeleton .initial-home")).toBeVisible();
  await expect(page.locator("#initial-page-skeleton .initial-questionnaire")).toBeHidden();
  await expect(page.locator("#root")).toBeEmpty();
  await navigation;
  await expect(page.getByRole("button", { name: "ورود" })).toHaveCount(0);
  await page.getByRole("button", { name: "menu" }).click();
  await expect(page.getByRole("button", { name: "ورود کاربر" })).toBeVisible();
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
  await expect(skeleton.locator(".hp-skeleton-questionnaire")).toBeVisible();
  await expect(skeleton.locator(".hp-skeleton-option")).toHaveCount(2);
  await releaseSession();
  await expect(page).toHaveURL(/\/question\/4$/);
});

test("renders the one-loan comparison action as visibly disabled", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => {
    const button = document.createElement("button");
    button.className = "hp-simple-compare-submit";
    button.disabled = true;
    button.textContent = "مقایسه کن (۱ وام)";
    document.body.append(button);
  });
  const button = page.getByRole("button", { name: /مقایسه کن/ });
  await expect(button).toBeDisabled();
  await expect(button).toHaveCSS("cursor", "not-allowed");
  await expect(button).toHaveCSS("background-color", "rgb(140, 140, 140)");
});


test("uses a detail-shaped document fallback for a delayed loan-details route", async ({ page }) => {
  await page.route("**/src/main.jsx", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 90));
    await route.continue();
  });

  const navigation = page.goto("/loan-details?loanId=example", { waitUntil: "commit" });
  await expect(page.locator("#initial-page-skeleton[data-variant=\"detail\"]")).toBeVisible();
  await expect(page.locator("#initial-page-skeleton .initial-detail")).toBeVisible();
  await expect(page.locator("#initial-page-skeleton .initial-home")).toBeHidden();
  await navigation;
});
