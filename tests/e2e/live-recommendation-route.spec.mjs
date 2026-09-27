import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
const questionnaire = JSON.parse(readFileSync(new URL("../../data/contracts/questionnaire-configuration.v1.json", import.meta.url), "utf8"));

const sessionId = "opaque-live-flow-test";
const response = {
  dataVersion: "official-source-v1", configVersion: "1.1.0",
  rankedRecommendations: [{ loanId: "published-loan", lenderName: "بانک آزمون", loanName: "وام منتشرشده", compatibilityScore: 0.91, compatibilityReason: "سازگاری دسته‌بندی شرایط وام با پاسخ‌های ثبت‌شدهٔ شما" }],
  lowCompatibilityRecommendations: [{ loanId: "low-loan", lenderName: "بانک کم‌تطابق", loanName: "وام زیر آستانه", compatibilityScore: 0.2, compatibilityReason: "تطابق پایین؛ پیشنهاد اصلی نیست" }],
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
    loanId: "published-loan", lenderName: "بانک آزمون", loanName: "وام منتشرشده", bankLogoReference: "https://cdn.example.test/published-bank.svg",
    maxAmountTomans: 500000000, monthlyInstallmentTomans: 12000000, maxRepaymentMonths: 48,
    interestRatePercent: 18, depositRequired: "خیر", depositHoldingMonths: null,
    loanToDepositRatioPercent: null, guaranteeType: "ضامن رسمی", requiredDepositAccount: null,
    conditions: ["مدارک هویتی", "ضامن معتبر"],
  } }));
  await page.route("**/api/v1/loans/low-loan", (route) => route.fulfill({ json: {
    loanId: "low-loan", lenderName: "بانک کم‌تطابق", loanName: "وام زیر آستانه", bankLogoReference: "https://cdn.example.test/low-bank.svg",
    maxAmountTomans: 200000000, monthlyInstallmentTomans: 9000000, maxRepaymentMonths: 24,
    interestRatePercent: 23, depositRequired: "بله", depositHoldingMonths: 3,
    loanToDepositRatioPercent: 80, guaranteeType: "چک", requiredDepositAccount: "قرض‌الحسنه",
    conditions: ["افتتاح حساب تأییدشده"],
  } }));
  await page.route("**/api/v1/loans/unknown-loan", (route) => route.fulfill({ json: {
    loanId: "unknown-loan", lenderName: "بانک دیگر", loanName: "وام نیازمند بررسی", bankLogoReference: "https://cdn.example.test/review-bank.svg",
    maxAmountTomans: 100000000, monthlyInstallmentTomans: null, maxRepaymentMonths: 12,
    interestRatePercent: null, depositRequired: null, depositHoldingMonths: null,
    loanToDepositRatioPercent: null, guaranteeType: null, requiredDepositAccount: null,
    conditions: [],
  } }));
  await page.goto("/question/3");
  for (const question of questionnaire.questions) {
    await page.getByRole("radio").first().click();
    await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  }
  await expect(page).toHaveURL(/\/loan-results$/);
  await expect(page.getByText("وام منتشرشده")).toBeVisible();
  await expect(page.locator(".hp-loan-result-head img").first()).toHaveAttribute("src", "https://cdn.example.test/published-bank.svg");
  const resultPartition = page.locator(".hp-loan-result-filters select").first();
  await resultPartition.selectOption("lowest");
  await expect(page.getByText("وام زیر آستانه")).toBeVisible();
  await resultPartition.selectOption("variable");
  await expect(page.getByText("وام نیازمند بررسی")).toBeVisible();
  await expect(page.locator(".hp-serving-loan-card")).toContainText("تطابق با وضعیت مشتری: نامشخص");
  expect(writes).toHaveLength(10);
  expect(writes.map(({ body }) => body.answerId)).toEqual(questionnaire.questions.map((q) => q.answerOptions[0].answerId));
  expect(posts.length).toBeGreaterThanOrEqual(1);
  expect(posts.every((request) => request.method === "POST" && Object.keys(request.body).length === 1 && request.body.sessionId === sessionId)).toBe(true);
  expect(page.url()).not.toContain(sessionId);
  await resultPartition.selectOption("highest");
  await page.getByRole("link", { name: "مشاهده شرایط و مدارک مورد نیاز" }).first().click();
  await expect(page.getByRole("heading", { name: "شرایط و مدارک مورد نیاز" })).toBeVisible();
  await expect(page.locator(".hp-loan-details-conditions")).toContainText("مدارک هویتی");
  await page.getByRole("button", { name: /بازگشت/ }).first().click();
  await expect(page.getByText("وام منتشرشده")).toBeVisible();

  await expect(page.getByRole("button", { name: "ثبت درخواست همزمان وام بانکی" })).toBeDisabled();

  await page.getByRole("button", { name: "مقایسه وام" }).click();
  await expect(page).toHaveURL(/\/compare-loans$/);
  await page.getByRole("button", { name: "انتخاب وام منتشرشده" }).click();
  await page.getByRole("button", { name: "انتخاب وام زیر آستانه" }).click();
  await page.getByRole("button", { name: /مقایسه کن/ }).click();
  await expect(page).toHaveURL(/\/compare-result$/);
  await expect(page.locator(".hp-compare-result-card")).toHaveCount(2);
  await expect(page.getByText("۵۰۰/۰۰۰/۰۰۰ تومان")).toBeVisible();

});

test("direct result and action routes fail closed without an active-tab session", async ({ page }) => {
  await page.goto("/loan-results");
  await expect(page.getByText(/ابتدا پرسشنامه را در همین تب کامل کنید/)).toBeVisible();
  await expect(page.getByRole("button", { name: "شروع پرسشنامه" })).toBeVisible();
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });

  await page.goto("/loan-request");
  await expect(page.getByText(/ابتدا پرسشنامه را در همین تب کامل/)).toBeVisible();
});
