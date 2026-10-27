import { expect, test } from "@playwright/test";

const questionnaireFixture = {
  sessionId: "t076-layout-session",
  expiresAt: "2027-01-01T00:00:00Z",
  answers: {},
  flowAnswers: { loan_type: "shahab", entity_type: "person" },
};

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/questionnaire/sessions/current", route => route.fulfill({ json: questionnaireFixture }));
  await page.route(`**/api/v1/questionnaire/sessions/${questionnaireFixture.sessionId}`, route => route.fulfill({ json: questionnaireFixture }));
});

for (const route of [
  "/question/3", "/question/4", "/question/5", "/question/6", "/question/7",
  "/question/8", "/question/9", "/question/10", "/question/11", "/question/12",
]) {
  test(`keeps 28px above and below the options inside ${route}`, async ({ page }) => {
    await page.goto(route);
    const { topGap, bottomGap } = await page.locator(".hp-question-card").evaluate((card) => {
      const options = card.querySelectorAll(".hp-question-option");
      const firstOption = options[0];
      const lastOption = options[options.length - 1];
      const cardBounds = card.getBoundingClientRect();
      return {
        topGap: Math.round(firstOption.getBoundingClientRect().top - cardBounds.top),
        bottomGap: Math.round(cardBounds.bottom - lastOption.getBoundingClientRect().bottom),
      };
    });

    expect(topGap).toBe(28);
    expect(bottomGap).toBe(28);
  });
}

for (const route of [
  "/question/3", "/question/4", "/question/5", "/question/6", "/question/7",
  "/question/8", "/question/9", "/question/10", "/question/11", "/question/12",
]) {
  test(`keeps the questionnaire actions 28px below the card on ${route}`, async ({ page }) => {
    await page.goto(route);

    const { cardToActionsGap, actionsToPageGap } = await page.locator(".hp-question-actions").evaluate((actions) => {
      const card = actions.previousElementSibling;
      const questionnairePage = actions.closest(".hp-questionnaire-page");
      return {
        cardToActionsGap: Math.round(actions.getBoundingClientRect().top - card.getBoundingClientRect().bottom),
        actionsToPageGap: Math.round(questionnairePage.getBoundingClientRect().bottom - actions.getBoundingClientRect().bottom),
      };
    });

    expect(cardToActionsGap).toBe(28);
    expect(actionsToPageGap).toBe(28);
  });
}

test("uses the application chevron dimensions on the home amount selector", async ({ page }) => {
  await page.goto("/");
  const chevron = await page.locator(".hp-select-wrap > span").evaluate((element) => {
    const style = getComputedStyle(element);
    return { width: style.width, height: style.height };
  });

  expect(chevron).toEqual({ width: "8px", height: "8px" });
});

test("disables the loan-detail AI analysis action", async ({ page }) => {
  await page.route("**/api/v1/loans/t076-disabled-analysis", (route) => route.fulfill({ json: {
    loanId: "t076-disabled-analysis",
    lenderName: "بانک آزمون",
    loanName: "وام آزمون",
    maxAmountTomans: 100000000,
    monthlyInstallmentTomans: 10000000,
    maxRepaymentMonths: 12,
    interestRatePercent: 18,
    depositRequired: "ندارد",
    depositHoldingMonths: 0,
    loanToDepositRatioPercent: 0,
    guaranteeType: "ضامن",
    requiredDepositAccount: "ندارد",
    conditions: ["کارت ملی"],
    bankLogoReference: null,
    applicationLink: null,
  } }));
  await page.goto("/loan-details?loanId=t076-disabled-analysis");

  const action = page.getByRole("button", { name: "تحلیل با هوش مصنوعی" });
  await expect(action).toBeDisabled();
  await expect(action).toHaveCSS("background-color", "rgb(140, 140, 140)");
});
