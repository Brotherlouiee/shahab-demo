
import { expect, test } from "@playwright/test";

const sessionId = "route-guard-test-session";

async function restoreSessionAt(page, route, answers) {
  await page.addInitScript((id) => {
    window.history.replaceState({ shahabRecommendation: { sessionId: id } }, "", window.location.href);
  }, sessionId);
  await page.route(`**/api/v1/questionnaire/sessions/${sessionId}`, (request) => request.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({
      sessionId,
      expiresAt: "2026-10-27T12:30:00Z",
      answers,
    }),
  }));
  await page.goto(route);
}

test("redirects a direct later-question URL to Q1 when there is no saved session", async ({ page }) => {
  await page.goto("/question/4");

  await expect(page).toHaveURL(/\/question\/3$/);
  await expect(page.locator(".hp-questionnaire-page h1")).toContainText("پولی که از این وام یا اعتبار");
});

test("restores the first unanswered question when a later URL is opened with a saved session", async ({ page }) => {
  await restoreSessionAt(page, "/question/5", { Q1: "Q1.incomeInvestment" });

  await expect(page).toHaveURL(/\/question\/4$/);
  await expect(page.locator(".hp-questionnaire-page h1")).toContainText("اگر دریافت این وام لغو شود");
  await page.reload();
  await expect(page).toHaveURL(/\/question\/4$/);
  await expect(page.locator(".hp-questionnaire-page h1")).toContainText("اگر دریافت این وام لغو شود");
});

test("allows refresh of the current question when all preceding answers were saved", async ({ page }) => {
  await restoreSessionAt(page, "/question/4", { Q1: "Q1.incomeInvestment" });

  await expect(page).toHaveURL(/\/question\/4$/);
  await expect(page.locator(".hp-questionnaire-page h1")).toContainText("اگر دریافت این وام لغو شود");
});
