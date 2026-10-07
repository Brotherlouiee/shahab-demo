import { expect, test } from "@playwright/test";

const approvedDetail = {
  loanId: "loan-approved",
  lenderName: "بانک نمونه",
  loanName: "طرح نمونه",
  maxAmountTomans: 100000000,
  monthlyInstallmentTomans: 10000000,
  maxRepaymentMonths: 12,
  interestRatePercent: 18,
  depositRequired: "دارد",
  depositHoldingMonths: 3,
  loanToDepositRatioPercent: 100,
  guaranteeType: "ضامن",
  requiredDepositAccount: "قرض الحسنه",
  conditions: ["کارت ملی", "<script>window.__xss = true</script>"],
  bankLogoReference: "javascript:alert(1)",
  applicationLink: "javascript:alert(1)",
};

async function openDetail(page) {
  await page.goto("/loan-details?loanId=loan-approved");
}

test("renders approved detail in RTL and escapes hostile conditions without using invalid assets", async ({ page }) => {
  await page.route("**/api/v1/loans/**", async (route) => {
    expect(route.request().headers().accept).toContain("application/json");
    await route.fulfill({ json: approvedDetail });
  });

  await openDetail(page);
  const pageRoot = page.locator("main.hp-loan-details-page");
  await expect(pageRoot).toHaveAttribute("dir", "rtl");
  await expect(pageRoot).toContainText("طرح نمونه");
  await expect(pageRoot).toContainText("کارت ملی");
  await expect(pageRoot).toContainText("<script>window.__xss = true</script>");
  await expect(page.locator(".hp-loan-details-conditions li")).toHaveCount(2);
  expect(await page.locator(".hp-loan-details-conditions").innerHTML()).toContain("&lt;script&gt;");
  await expect(page.locator('a[href^="javascript:"], img[src^="javascript:"]')).toHaveCount(0);
  expect(await page.evaluate(() => window.__xss)).toBeUndefined();
});

test("keeps a visible loading state until the approved-detail response arrives", async ({ page }) => {
  let releaseResponse;
  await page.route("**/api/v1/loans/**", (route) => new Promise((resolve) => {
    releaseResponse = async () => {
      await route.fulfill({ json: approvedDetail });
      resolve();
    };
  }));

  await openDetail(page);
  const skeleton = page.getByRole("status", { name: "در حال بارگذاری" });
  await expect(skeleton).toBeVisible();
  await expect(skeleton).toHaveClass(/hp-deferred-skeleton/);
  await releaseResponse();
  await expect(page.getByText("طرح نمونه")).toBeVisible();
});

test("renders an absent-detail state for the typed not-found response", async ({ page }) => {
  await page.route("**/api/v1/loans/**", (route) => route.fulfill({ status: 404, contentType: "application/json" }));
  await openDetail(page);
  await expect(page.getByText("جزئیات این وام در فهرست تأییدشده موجود نیست.")).toBeVisible();
});

test("shows a safe error and retries without displaying a server response", async ({ page }) => {
  let calls = 0;
  let recover = false;
  await page.route("**/api/v1/loans/**", (route) => {
    calls += 1;
    return recover
      ? route.fulfill({ json: approvedDetail })
      : route.fulfill({ status: 503, contentType: "application/json", body: '{"error":{"message":"database password leaked"}}' });
  });

  await openDetail(page);
  await expect(page.getByRole("alert")).toContainText("دریافت جزئیات وام در حال حاضر ممکن نیست.");
  await expect(page.getByText("database password leaked")).toHaveCount(0);
  recover = true;
  await page.getByRole("button", { name: "تلاش مجدد" }).click();
  await expect(page.getByText("طرح نمونه")).toBeVisible();
  expect(calls).toBeGreaterThanOrEqual(2);
});
