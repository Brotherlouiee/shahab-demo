
import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";

const sessionId = "route-guard-test-session";
const canonicalIdentifiers = JSON.parse(
  readFileSync(new URL("../../data/contracts/canonical-identifiers.v1.json", import.meta.url), "utf8"),
);
const questionnaireConfiguration = JSON.parse(
  readFileSync(new URL("../../data/contracts/questionnaire-configuration.v1.json", import.meta.url), "utf8"),
);
const canonicalRoutes = Object.entries(canonicalIdentifiers.questionnaireRouteMap);

function answeredPrefix(answeredCount) {
  return Object.fromEntries(canonicalRoutes.slice(0, answeredCount).map(([, questionId]) => {
    const question = questionnaireConfiguration.questions.find((item) => item.questionId === questionId);
    return [questionId, question.answerOptions[0].answerId];
  }));
}

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
      flowAnswers: { loan_type: "shahab", entity_type: "person" },
    }),
  }));
  await page.goto(route);
}

test("redirects a direct later-question URL to the first visible step without a saved session", async ({ page }) => {
  await page.goto("/question/4");

  await expect(page).toHaveURL(/\/question\/1$/);
  await expect(page.locator(".hp-questionnaire-page h1")).toContainText("مایل به دریافت چه نوع وامی");
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

test("blocks a later in-app history route at the first unanswered canonical question", async ({ page }) => {
  await restoreSessionAt(page, "/question/4", { Q1: "Q1.incomeInvestment" });

  await expect(page).toHaveURL(/\/question\/4$/);
  await page.evaluate(() => {
    window.history.pushState(window.history.state, "", "/question/6");
    window.dispatchEvent(new PopStateEvent("popstate", { state: window.history.state }));
  });

  await expect(page).toHaveURL(/\/question\/4$/);
  await expect(page.locator(".hp-questionnaire-page h1")).toContainText("اگر دریافت این وام لغو شود");
});

for (let answeredCount = 0; answeredCount < canonicalRoutes.length; answeredCount += 1) {
  test(`blocks direct, refreshed, and history jumps with ${answeredCount} answers`, async ({ page }) => {
    const expectedRoute = canonicalRoutes[answeredCount][0];
    const lastRoute = canonicalRoutes.at(-1)[0];
    await restoreSessionAt(page, lastRoute, answeredPrefix(answeredCount));

    await expect(page).toHaveURL(new RegExp(`${expectedRoute.replaceAll("/", "\\/")}$`));
    await expect(page.locator(".hp-questionnaire-page")).toBeVisible();
    await expect(page.getByRole("radio").first()).toBeVisible();

    await page.evaluate((targetRoute) => {
      window.history.pushState(window.history.state, "", targetRoute);
      window.dispatchEvent(new PopStateEvent("popstate", { state: window.history.state }));
    }, lastRoute);
    await expect(page).toHaveURL(new RegExp(`${expectedRoute.replaceAll("/", "\\/")}$`));

    await page.reload();
    await expect(page).toHaveURL(new RegExp(`${expectedRoute.replaceAll("/", "\\/")}$`));
  });
}
