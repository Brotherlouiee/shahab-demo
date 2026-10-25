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


test("keeps history-detail back and brand controls inside the shared page margins", async ({ page }) => {
  await page.route("**/api/v1/loans/**", (route) => route.fulfill({ json: approvedDetail }));

  for (const viewport of [{ width: 390, height: 844 }, { width: 430, height: 932 }, { width: 1440, height: 900 }]) {
    await page.setViewportSize(viewport);
    await page.goto("/loan-details?from=history&loanId=loan-approved");

    const header = page.locator(".hp-loan-details-page > .hp-account-header");
    await expect(header).toBeVisible();
    await expect(header.locator(".hp-questionnaire-menu")).toHaveCount(0);
    const margins = await page.evaluate(() => {
      const headerRect = document.querySelector(".hp-loan-details-page > .hp-account-header").getBoundingClientRect();
      const backRect = document.querySelector(".hp-loan-details-page > .hp-account-header .hp-questionnaire-icon-button").getBoundingClientRect();
      const brandRect = document.querySelector(".hp-loan-details-page > .hp-account-header .hp-questionnaire-brand").getBoundingClientRect();
      return { back: backRect.left - headerRect.left, brand: headerRect.right - brandRect.right };
    });

    expect(margins.back).toBeGreaterThanOrEqual(19);
    expect(margins.brand).toBeGreaterThanOrEqual(19);
  }
});

test("halves the history-detail header-to-card gap", async ({ page }) => {
  await page.route("**/api/v1/loans/**", (route) => route.fulfill({ json: approvedDetail }));
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/loan-details?from=history&loanId=loan-approved");

  const gap = await page.evaluate(() => {
    const header = document.querySelector(".hp-loan-details-page > .hp-account-header").getBoundingClientRect();
    const card = document.querySelector(".hp-loan-details-page .hp-loan-result-card").getBoundingClientRect();
    return card.top - header.bottom;
  });

  expect(gap).toBe(12);
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
