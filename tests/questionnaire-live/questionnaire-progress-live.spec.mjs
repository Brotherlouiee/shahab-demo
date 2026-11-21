import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";

const canonicalIdentifiers = JSON.parse(
  readFileSync(new URL("../../data/contracts/canonical-identifiers.v1.json", import.meta.url), "utf8"),
);
const canonicalRoutes = Object.entries(canonicalIdentifiers.questionnaireRouteMap);
const journeyRoutes = ["/question/1", "/question/2", ...canonicalRoutes.map(([route]) => route)];

test("persists every visible answer and blocks URL jumps against the real API and database", async ({ page }) => {
  await page.goto("/question/1");

  for (let index = 0; index < journeyRoutes.length; index += 1) {
    const currentRoute = journeyRoutes[index];
    const nextRoute = journeyRoutes[index + 1] || "/personal-info";
    await expect(page).toHaveURL(new RegExp(`${currentRoute.replaceAll("/", "\\/")}$`));
    const selectedAnswerIndex = index === 1 ? 1 : 0;
    await page.getByRole("radio").nth(selectedAnswerIndex).click();
    await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
    await expect(page).toHaveURL(new RegExp(`${nextRoute.replaceAll("/", "\\/")}$`));

    const nextQuestionNumber = index + 2;
    const jumpQuestionNumber = Math.min(nextQuestionNumber + 2, journeyRoutes.length);
    if (nextRoute.startsWith("/question/") && jumpQuestionNumber > nextQuestionNumber) {
      const requestedQuestionNumber = index === 3 ? 6 : jumpQuestionNumber;
      await page.goto(`/question/${requestedQuestionNumber}`);
      await expect(page).toHaveURL(new RegExp(`${nextRoute.replaceAll("/", "\\/")}$`));
    }

    await page.reload();
    await expect(page).toHaveURL(new RegExp(`${nextRoute.replaceAll("/", "\\/")}$`));
    const backButtonName = nextRoute === "/personal-info" ? "بازگشت به مرحله قبل" : "بازگشت به سوال قبل";
    await page.getByRole("button", { name: backButtonName }).click();
    await expect(page).toHaveURL(new RegExp(`${currentRoute.replaceAll("/", "\\/")}$`));
    await expect(page.getByRole("radio").nth(selectedAnswerIndex)).toHaveAttribute("aria-checked", "true");

    if (index < journeyRoutes.length - 1) {
      await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
      await expect(page).toHaveURL(new RegExp(`${nextRoute.replaceAll("/", "\\/")}$`));
    }
  }

  const sessionId = await page.evaluate(() => window.history.state?.shahabRecommendation?.sessionId);
  expect(sessionId).toBeTruthy();
  expect(page.url()).not.toContain(sessionId);
  const persisted = await page.evaluate(async (id) => {
    const response = await fetch(`/api/v1/questionnaire/sessions/${id}`);
    return response.json();
  }, sessionId);
  expect(Object.keys(persisted.flowAnswers).sort()).toEqual(["entity_type", "loan_type"]);
  expect(Object.keys(persisted.answers).sort()).toEqual(
    Object.values(canonicalIdentifiers.questionnaireRouteMap).sort(),
  );
});

test("a fresh direct URL cannot skip the two entry questions", async ({ page }) => {
  await page.goto("/question/8");
  await expect(page).toHaveURL(/\/question\/1$/);
  await expect(page.locator(".hp-questionnaire-page h1")).toContainText("مایل به دریافت چه نوع وامی");
});
