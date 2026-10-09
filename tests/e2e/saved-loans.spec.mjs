import { expect, test } from "@playwright/test";

const savedLoan = {
  loanId: "saved-loan-1",
  lenderName: "بانک آزمون",
  loanName: "وام آزمون",
  compatibilityScore: 0.85,
  loanSummary: {
    maxAmountTomans: 100000000,
    monthlyInstallmentTomans: 10000000,
    maxRepaymentMonths: 12,
    interestRatePercent: 18,
  },
};

test("shows the supplied empty artwork and no filters when no saved loan exists", async ({ page }) => {
  await page.addInitScript(() => window.localStorage.removeItem("shahab.savedLoans"));
  await page.goto("/saved-loans");

  await expect(page).toHaveURL(/\/saved-loans$/);
  await expect(page.locator(".hp-saved-loans-empty-state img")).toHaveAttribute("src", "/saved-loans-empty.png");
  await expect(page.locator(".hp-loan-result-filters")).toHaveCount(0);
});

test("keeps a saved loan detail return path and hides filters for one loan", async ({ page }) => {
  await page.addInitScript((loan) => window.localStorage.setItem("shahab.savedLoans", JSON.stringify([loan])), savedLoan);
  await page.route("**/api/v1/loans/saved-loan-1", (route) => route.fulfill({ json: {
    loanId: "saved-loan-1",
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
  await page.goto("/saved-loans");

  await expect(page.locator(".hp-loan-result-filters")).toHaveCount(0);
  await expect(page.locator(".hp-loan-docs-link .hp-loan-docs-icon")).toHaveCount(1);
  await page.locator(".hp-loan-docs-link").click();
  await expect(page).toHaveURL(/\/loan-details\?loanId=saved-loan-1&from=saved-loans$/);
  await page.getByRole("button", { name: "بازگشت" }).click();
  await expect(page).toHaveURL(/\/saved-loans$/);
});
