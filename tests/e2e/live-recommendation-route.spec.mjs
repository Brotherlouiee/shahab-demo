import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
const questionnaire = JSON.parse(readFileSync(new URL("../../data/contracts/questionnaire-configuration.v1.json", import.meta.url), "utf8"));

const sessionId = "opaque-live-flow-test";
const response = {
  dataVersion: "official-source-v1", configVersion: "1.1.0",
  rankedRecommendations: [{ loanId: "published-loan", lenderName: "بانک آزمون", loanName: "وام منتشرشده", compatibilityScore: 0.91, compatibilityReason: "سازگاری دسته‌بندی شرایط وام با پاسخ‌های ثبت‌شدهٔ شما" }],
  needsReview: [{ loanId: "unknown-loan", lenderName: "بانک دیگر", loanName: "وام نیازمند بررسی", rankingExcludedReasons: ["interestRate:unknown"] }],
};

test("canonical questionnaire reaches the active real-result route and published detail", async ({ page }) => {
  const writes = [];
  const posts = [];
  await page.route("**/api/v1/questionnaire/sessions", (route) => route.fulfill({ status: 201, json: { sessionId, expiresAt: "2027-01-01T00:00:00Z", answers: {} } }));
  await page.route("**/api/v1/questionnaire/sessions/*/answers/*", (route) => {
    writes.push({ url: route.request().url(), body: route.request().postDataJSON() });
    return route.fulfill({ json: { sessionId, expiresAt: "2027-01-01T00:00:00Z", answers: {} } });
  });
  await page.route("**/api/v1/recommendations", (route) => {
    posts.push({ method: route.request().method(), body: route.request().postDataJSON() });
    return route.fulfill({ json: response });
  });
  await page.route("**/api/v1/loans/published-loan", (route) => route.fulfill({ json: {
    loanId: "published-loan", lenderName: "بانک آزمون", loanName: "وام منتشرشده",
    maxAmountTomans: null, monthlyInstallmentTomans: null, maxRepaymentMonths: null,
    interestRatePercent: null, depositRequired: null, depositHoldingMonths: null,
    loanToDepositRatioPercent: null, guaranteeType: null, requiredDepositAccount: null,
    conditions: ["مدارک هویتی", "ضامن معتبر"],
  } }));
  await page.goto("/question/3");
  for (const question of questionnaire.questions) {
    await page.getByRole("radio").first().click();
    await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  }
  await expect(page).toHaveURL(/\/loan-results$/);
  await expect(page.getByText("وام منتشرشده")).toBeVisible();
  await expect(page.locator(".hp-recommendation-needs-review")).toContainText("وام نیازمند بررسی");
  await expect(page.locator(".hp-recommendation-needs-review")).not.toContainText("٪");
  expect(writes).toHaveLength(10);
  expect(writes.map(({ body }) => body.answerId)).toEqual(questionnaire.questions.map((q) => q.answerOptions[0].answerId));
  expect(posts).toEqual([{ method: "POST", body: { sessionId } }]);
  expect(page.url()).not.toContain(sessionId);
  await page.getByRole("link", { name: "مشاهدهٔ جزئیات، شرایط و مدارک" }).first().click();
  await expect(page.getByRole("heading", { name: "شرایط و مدارک مورد نیاز" })).toBeVisible();
  await expect(page.locator(".hp-loan-details-conditions")).toContainText("مدارک هویتی");
  await page.getByRole("button", { name: /بازگشت/ }).first().click();
  await expect(page.getByText("وام منتشرشده")).toBeVisible();
});
