import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
const questionnaire = JSON.parse(readFileSync(new URL("../../data/contracts/questionnaire-configuration.v1.json", import.meta.url), "utf8"));

const sessionId = "opaque-live-flow-test";
const additionalRankedRecommendations = [
  ["published-loan-2", "بانک توسعه تعاون", "طرح نیروگاه خورشیدی خانگی", 0.86],
  ["published-loan-3", "بانک دی", "وام دی", 0.82],
  ["published-loan-4", "بانک رفاه کارگران", "طرح رفاه سازمانی", 0.79],
  ["published-loan-5", "بانک صنعت و معدن", "تسهیلات توسعه صنعتی", 0.76],
  ["published-loan-6", "بانک ملی", "وام ملی", 0.73],
  ["published-loan-7", "بانک ایران و ونزوئلا", "طرح تأمین مالی زنجیره‌ای بنگاه‌های کوچک و متوسط", 0.69],
  ["published-loan-8", "بانک سینا", "وام سینا", 0.65],
].map(([loanId, lenderName, loanName, compatibilityScore]) => ({
  loanId,
  lenderName,
  loanName,
  bankLogoReference: `https://cdn.example.test/${loanId}.svg`,
  compatibilityScore,
  compatibilityReason: "سازگاری دسته‌بندی شرایط وام با پاسخ‌های ثبت‌شدهٔ شما",
}));
const response = {
  dataVersion: "official-source-v1", configVersion: "1.1.0",
  rankedRecommendations: [{ loanId: "published-loan", lenderName: "بانک ملت", loanName: "میثاق 2", bankLogoReference: "https://cdn.example.test/published-bank.svg", compatibilityScore: 0.91, compatibilityReason: "سازگاری دسته‌بندی شرایط وام با پاسخ‌های ثبت‌شدهٔ شما" }, ...additionalRankedRecommendations],
  lowCompatibilityRecommendations: [{ loanId: "low-loan", lenderName: "بانک ایران و ونزوئلا", loanName: "وام زیر آستانه", bankLogoReference: "https://cdn.example.test/low-bank.svg", compatibilityScore: 0.2, compatibilityReason: "تطابق پایین؛ پیشنهاد اصلی نیست" }],
  needsReview: [{ loanId: "unknown-loan", lenderName: "بانک شهر", loanName: "وام نیازمند بررسی", bankLogoReference: "https://cdn.example.test/review-bank.svg", rankingExcludedReasons: ["interestRate:unknown"] }],
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
    loanId: "published-loan", lenderName: "بانک ملت", loanName: "میثاق 2", bankLogoReference: "https://cdn.example.test/published-bank.svg",
    maxAmountTomans: 500000000, monthlyInstallmentTomans: 12000000, maxRepaymentMonths: 48,
    interestRatePercent: 18, depositRequired: "خیر", depositHoldingMonths: null,
    loanToDepositRatioPercent: null, guaranteeType: "ضامن رسمی", requiredDepositAccount: null,
    conditions: ["مدارک هویتی", "ضامن معتبر"],
  } }));
  await page.route("**/api/v1/loans/low-loan", (route) => route.fulfill({ json: {
    loanId: "low-loan", lenderName: "بانک ایران و ونزوئلا", loanName: "وام زیر آستانه", bankLogoReference: "https://cdn.example.test/low-bank.svg",
    maxAmountTomans: 200000000, monthlyInstallmentTomans: 9000000, maxRepaymentMonths: 24,
    interestRatePercent: 23, depositRequired: "بله", depositHoldingMonths: 3,
    loanToDepositRatioPercent: 80, guaranteeType: "چک", requiredDepositAccount: "قرض‌الحسنه",
    conditions: ["افتتاح حساب تأییدشده"],
  } }));
  await page.route("**/api/v1/loans/unknown-loan", (route) => route.fulfill({ json: {
    loanId: "unknown-loan", lenderName: "بانک شهر", loanName: "وام نیازمند بررسی", bankLogoReference: "https://cdn.example.test/review-bank.svg",
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

  await expect(page).toHaveURL(/\/personal-info$/);
  const personalInputs = page.locator(".hp-personal-info-form input");
  await personalInputs.nth(0).fill("علی");
  await personalInputs.nth(1).fill("رضایی");
  await personalInputs.nth(2).fill("۹۱۲۳۴۵۶۷۸۹");
  await page.locator(".hp-personal-dropdown-trigger").nth(0).click();
  await page.getByRole("option", { name: "تا ۲۲ میلیون تومان" }).click();
  await page.locator(".hp-personal-dropdown-trigger").nth(1).click();
  await page.getByRole("option", { name: "کارمند (شرکت یا اداره)" }).click();
  await page.getByRole("button", { name: "تایید" }).click();
  await expect(page).toHaveURL(/\/verify-code$/);
  const otpInputs = page.locator(".hp-loan-otp-row input");
  for (const [index, digit] of [..."۱۲۳۴۵۶"].entries()) await otpInputs.nth(index).fill(digit);
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  await expect(page).toHaveURL(/\/analysis$/);
  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 7000 });
  await expect(page).toHaveURL(/\/loan-results$/);
  await expect(page.getByText("میثاق ۲")).toBeVisible();
  await expect(page.getByText("میثاق 2", { exact: true })).toHaveCount(0);
  await expect(page.locator(".hp-loan-result-head img").first()).toHaveAttribute("src", /bank-logos/);
  const resultLogo = page.locator(".hp-loan-result-head img").first();
  await expect(resultLogo).toBeVisible();
  await expect(resultLogo).toHaveJSProperty("complete", true);
  expect(await resultLogo.evaluate((image) => image.naturalWidth > 0 && image.naturalHeight > 0)).toBe(true);
  const shortNameLogoOffset = await logoOffsetFromCard(page.locator(".hp-serving-loan-card").first());
  const resultTitleOffset = await titleOffsetFromCard(page.locator(".hp-serving-loan-card").first(), ".hp-loan-result-head strong");
  expect(resultTitleOffset.top).toBeCloseTo(30, 0);
  await expect(page.locator(".hp-serving-loan-card .hp-loan-percent").first()).toHaveAttribute("dir", "ltr");
  await expect(page.locator(".hp-serving-loan-card .hp-loan-percent").first()).toHaveText("٪۹۱");
  const resultPercentParts = await page.locator(".hp-serving-loan-card .hp-loan-percent").first().locator("span").evaluateAll((parts) => parts.map((part) => part.getBoundingClientRect().x));
  expect(resultPercentParts[0]).toBeLessThan(resultPercentParts[1]);
  await expectCompatibilityPercentScale(page.locator(".hp-serving-loan-card").first());
  const limeCompatibilityCard = page.locator(".hp-serving-loan-card").filter({ hasText: "طرح رفاه سازمانی" });
  await expect(limeCompatibilityCard).toHaveCSS("border-top-color", "rgb(207, 210, 56)");
  const melliLogo = page.getByAltText("بانک ملی").first();
  await expect(melliLogo).toBeVisible();
  await expect(melliLogo).toHaveJSProperty("complete", true);
  expect(await melliLogo.evaluate((image) => image.naturalWidth > 0 && image.naturalHeight > 0)).toBe(true);
  const assetResponse = await page.request.get(await resultLogo.getAttribute("src"));
  expect(assetResponse.ok()).toBe(true);
  expect(assetResponse.headers()["content-type"]).toContain("image/svg+xml");
  await page.getByRole("button", { name: "نمایش نتایج" }).click();
  await page.getByRole("option", { name: "کمترین تطابق" }).click();
  await expect(page.getByText("وام زیر آستانه")).toBeVisible();
  await expect(page.locator(".hp-serving-loan-card").first()).toHaveCSS("border-top-color", "rgb(255, 47, 0)");
  await expect(page.locator(".hp-loan-docs-link").first()).toHaveCSS("color", "rgb(0, 103, 255)");
  await expect(page.locator(".hp-loan-result-head img").first()).toHaveAttribute("src", /bank-logos\/v1\/[a-f0-9]{64}\.svg/);
  const longNameLogoOffset = await logoOffsetFromCard(page.locator(".hp-serving-loan-card").first());
  expect(Math.abs(shortNameLogoOffset.right - longNameLogoOffset.right)).toBeLessThanOrEqual(1);
  expect(Math.abs(shortNameLogoOffset.top - longNameLogoOffset.top)).toBeLessThanOrEqual(1);
  await page.getByRole("button", { name: "نمایش نتایج" }).click();
  await page.getByRole("option", { name: "وضعیت متغیر" }).click();
  await expect(page.getByText("وام نیازمند بررسی")).toBeVisible();
  await expect(page.locator(".hp-loan-docs-link").first()).toHaveCSS("color", "rgb(0, 103, 255)");
  await expect(page.locator(".hp-loan-result-head img").first()).toHaveAttribute("src", /bank-logos\/v1\/[a-f0-9]{64}\.svg/);
  await expect(page.locator(".hp-serving-loan-card")).toContainText("تطابق با وضعیت مشتری: نامشخص");
  expect(writes).toHaveLength(10);
  expect(writes.map(({ body }) => body.answerId)).toEqual(questionnaire.questions.map((q) => q.answerOptions[0].answerId));
  expect(posts.length).toBeGreaterThanOrEqual(1);
  expect(posts.every((request) => request.method === "POST" && Object.keys(request.body).length === 1 && request.body.sessionId === sessionId)).toBe(true);
  expect(page.url()).not.toContain(sessionId);
  await page.getByRole("button", { name: "نمایش نتایج" }).click();
  await page.getByRole("option", { name: "بیشترین تطابق" }).click();
  await page.getByRole("link", { name: "مشاهده شرایط و مدارک مورد نیاز" }).first().click();
  await expect(page.getByRole("heading", { name: "شرایط و مدارک مورد نیاز" })).toBeVisible();
  await expect(page.locator(".hp-loan-details-conditions")).toContainText("مدارک هویتی");
  await expect(page.getByRole("button", { name: "تحلیل با هوش مصنوعی" })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { name: "شرایط و مدارک مورد نیاز" })).toBeVisible();
  await expectLogoOffsets(page.locator(".hp-loan-detail-card"), shortNameLogoOffset);
  const declaredInterestParts = await page.locator(".hp-loan-detail-card .hp-loan-percent").locator("span").evaluateAll((parts) => parts.map((part) => part.getBoundingClientRect().x));
  expect(declaredInterestParts[0]).toBeLessThan(declaredInterestParts[1]);
  await page.getByRole("button", { name: /بازگشت/ }).first().click();
  await expect(page.getByText("میثاق ۲")).toBeVisible();

  await expect(page.getByRole("button", { name: "بررسی آمادگی دریافت وام" })).toBeDisabled();

  await page.getByRole("button", { name: "مقایسه وام" }).click();
  await expect(page).toHaveURL(/\/compare-loans$/);
  await expect(page.locator(".hp-loan-compare-card .hp-loan-result-head img").first()).toHaveAttribute("src", /bank-logos/);
  expect(await page.locator(".hp-loan-compare-card .hp-loan-result-head img").first().evaluate((image) => image.naturalWidth > 0)).toBe(true);
  await expectLogoOffsets(page.locator(".hp-loan-compare-card"), shortNameLogoOffset);
  await expectCompatibilityPercentScale(page.locator(".hp-loan-compare-card").first());
  await expectComparisonMatchTopOffset(page.locator(".hp-loan-compare-card").first());
  await page.screenshot({ path: "docs/evidence/us-09-t06h/desktop-bank-logo-anchor.png", fullPage: true });
  await page.setViewportSize({ width: 360, height: 800 });
  await expectLogoOffsets(page.locator(".hp-loan-compare-card"), shortNameLogoOffset);
  await page.screenshot({ path: "docs/evidence/us-09-t06h/mobile-bank-logo-anchor.png", fullPage: true });
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.getByRole("button", { name: "انتخاب میثاق ۲" }).click();
  await page.getByRole("button", { name: "انتخاب وام زیر آستانه" }).click();
  await page.getByRole("button", { name: /مقایسه کن/ }).click();
  await expect(page).toHaveURL(/\/compare-result$/);
  await expect(page.locator(".hp-compare-result-card")).toHaveCount(2);
  await expect(page.getByRole("button", { name: "تحلیل با هوش مصنوعی" })).toBeVisible();
  const comparisonResultCardHeight = await page.locator(".hp-compare-result-card").first().evaluate((card) => card.getBoundingClientRect().height);
  await expectTitleTopOffset(page.locator(".hp-compare-result-card").first(), ".hp-compare-result-card > strong");
  await expectTitleOffset(page.locator(".hp-compare-result-card").first(), ".hp-compare-result-card > strong", resultTitleOffset);
  await expect(page.locator(".hp-compare-result-card img")).toHaveCount(2);
  expect(await page.locator(".hp-compare-result-card img").evaluateAll((images) => images.every((image) => image.complete && image.naturalWidth > 0))).toBe(true);
  await expectLogoOffsets(page.locator(".hp-compare-result-card"), shortNameLogoOffset);
  await expect(page.getByText("۵۰۰/۰۰۰/۰۰۰ تومان")).toBeVisible();
  await page.getByRole("button", { name: "نرخ بهره" }).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("button", { name: "نرخ بهره" })).toHaveClass(/is-active/);
  await expect(page.locator(".hp-compare-result-card .hp-loan-percent").first()).toHaveAttribute("dir", "ltr");
  await expect(page.locator(".hp-compare-result-card .hp-loan-percent").first()).toHaveText("٪۱۸");
  const comparedPercentParts = await page.locator(".hp-compare-result-card .hp-loan-percent").first().locator("span").evaluateAll((parts) => parts.map((part) => part.getBoundingClientRect().x));
  expect(comparedPercentParts[0]).toBeLessThan(comparedPercentParts[1]);
  await page.getByRole("button", { name: "بازگشت" }).click();
  await expect(page).toHaveURL(/\/compare-loans$/);
  await expect(page.locator(".hp-loan-compare-check[aria-pressed='true']")).toHaveCount(2);
  await expect(page.getByRole("button", { name: "انتخاب میثاق ۲" })).toHaveClass(/is-selected/);
  await expect(page.getByRole("button", { name: "انتخاب وام زیر آستانه" })).toHaveClass(/is-selected/);
  await expectComparisonSelectionGeometry(page.locator(".hp-loan-compare-card").first(), comparisonResultCardHeight);
  await page.getByRole("button", { name: "بازگشت" }).click();
  await expect(page).toHaveURL(/\/loan-results$/);
  await page.getByRole("button", { name: "مقایسه وام" }).click();
  await expect(page).toHaveURL(/\/compare-loans$/);
  await expect(page.locator(".hp-loan-compare-check[aria-pressed='true']")).toHaveCount(0);

});

async function logoOffsetFromCard(card) {
  return card.evaluate((element) => {
    const cardRect = element.getBoundingClientRect();
    const logoRect = element.querySelector(".hp-bank-logo-box img").getBoundingClientRect();
    return { right: cardRect.right - logoRect.right, top: logoRect.top - cardRect.top };
  });
}

async function titleOffsetFromCard(card, selector) {
  return card.evaluate((element, titleSelector) => {
    const cardRect = element.getBoundingClientRect();
    const titleRect = element.querySelector(titleSelector).getBoundingClientRect();
    return { top: titleRect.top - cardRect.top };
  }, selector);
}

async function expectTitleOffset(card, selector, expectedOffset) {
  const offset = await titleOffsetFromCard(card, selector);
  expect(Math.abs(offset.top - expectedOffset.top)).toBeLessThanOrEqual(1);
}

async function expectLogoOffsets(cards, expectedOffset) {
  const offsets = await cards.evaluateAll((elements) => elements.map((element) => {
    const cardRect = element.getBoundingClientRect();
    const logoRect = element.querySelector(".hp-bank-logo-box img").getBoundingClientRect();
    return { right: cardRect.right - logoRect.right, top: logoRect.top - cardRect.top };
  }));
  for (const offset of offsets) {
    expect(Math.abs(offset.right - expectedOffset.right)).toBeLessThanOrEqual(1);
    expect(Math.abs(offset.top - expectedOffset.top)).toBeLessThanOrEqual(1);
  }
}


test("local profile, demonstration OTP and five-second spinner preserve the fail-closed result boundary", async ({ page }) => {
  await page.goto("/personal-info");

  const personalInputs = page.locator(".hp-personal-info-form input");
  await personalInputs.nth(0).fill("علی");
  await personalInputs.nth(1).fill("رضایی");
  await personalInputs.nth(2).fill("۹۱۲۳۴۵۶۷۸۹");
  await page.locator(".hp-personal-dropdown-trigger").nth(0).click();
  await page.getByRole("option", { name: "تا ۲۲ میلیون تومان" }).click();
  await page.locator(".hp-personal-dropdown-trigger").nth(1).click();
  await page.getByRole("option", { name: "کارمند (شرکت یا اداره)" }).click();
  await page.getByRole("button", { name: "تایید" }).click();

  await expect(page).toHaveURL(/\/verify-code$/);
  await expect(page.locator(".hp-loan-otp-row input")).toHaveCount(6);
  await expect(page.getByRole("button", { name: /۰۲:۰۰/ })).toBeDisabled();

  const otpInputs = page.locator(".hp-loan-otp-row input");
  for (const [index, digit] of [..."۱۲۳۴۵۰"].entries()) await otpInputs.nth(index).fill(digit);
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  await expect(page.getByText("کد وارد شده اشتباه است")).toBeVisible();

  for (const [index, digit] of [..."۱۲۳۴۵۶"].entries()) await otpInputs.nth(index).fill(digit);
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  await expect(page).toHaveURL(/\/analysis$/);
  await expect(page.locator(".hp-analysis-spinner > span")).toHaveText("۵");
  await page.waitForTimeout(1100);
  await expect(page.locator(".hp-analysis-spinner > span")).toHaveText("۴");
  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 7000 });
  await expect(page.getByText(/ابتدا پرسشنامه را در همین تب کامل کنید/)).toBeVisible();

  await page.getByRole("button", { name: "منو" }).click();
  await expect(page.locator(".hp-sidebar-name")).toHaveText("علی رضایی");

  await page.goto("/personal-info");
  await personalInputs.nth(0).focus();
  await expect(page.getByRole("button", { name: "علی" })).toBeVisible();
});

for (const viewport of [
  { name: "desktop", width: 1280, height: 720 },
  { name: "mobile", width: 390, height: 834 },
]) {
  test(`${viewport.name} personal-information and OTP use the questionnaire content rail`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto("/question/3");
    const questionnaireRail = await page.locator(".hp-stage-board").evaluate((board) => {
      const rect = board.getBoundingClientRect();
      return { left: rect.left, right: rect.right, width: rect.width };
    });

    await page.goto("/personal-info");
    await expect(page.locator(".hp-questionnaire-header")).toBeVisible();
    await expect(page.locator(".hp-personal-info-form")).toBeVisible();
    await page.waitForTimeout(100);

    const personalGeometry = await page.evaluate(() => {
      const board = document.querySelector(".hp-stage-board");
      const form = document.querySelector(".hp-personal-info-form");
      const fields = [...form.querySelectorAll(":scope > label > input, :scope > label > .hp-personal-phone, :scope > label .hp-personal-dropdown-trigger")];
      const actions = document.querySelector(".hp-personal-info-form + .hp-question-actions");
      const confirm = actions.querySelector(".hp-next-question");
      const previous = actions.querySelector(".hp-previous-question");
      const phoneLabel = [...form.querySelectorAll(":scope > label > span:first-child")].find((label) => label.textContent.trim() === "شماره تلفن همراه");
      const rect = (element) => element.getBoundingClientRect();
      const boardRect = rect(board);
      const formRect = rect(form);
      const actionRect = rect(actions);
      const confirmRect = rect(confirm);
      const previousTextRange = document.createRange();
      previousTextRange.selectNodeContents(previous);
      const previousTextRect = previousTextRange.getBoundingClientRect();
      return {
        board: { left: boardRect.left, right: boardRect.right, width: boardRect.width },
        form: { left: formRect.left, right: formRect.right, width: formRect.width },
        actions: { left: actionRect.left, right: actionRect.right, width: actionRect.width },
        fields: fields.map((field) => {
          const fieldRect = rect(field);
          return { left: fieldRect.left, right: fieldRect.right, width: fieldRect.width };
        }),
        labelRight: rect(form.querySelector("label > span")).right,
        phoneLabel: {
          whiteSpace: getComputedStyle(phoneLabel).whiteSpace,
          width: rect(phoneLabel).width,
          scrollWidth: phoneLabel.scrollWidth,
        },
        dots: [...document.querySelectorAll(".hp-step-dot")].map((dot) => {
          const dotRect = rect(dot);
          return {
            left: dotRect.left,
            top: dotRect.top,
            width: dotRect.width,
            height: dotRect.height,
          };
        }),
        previousRight: rect(previous).right,
        previousText: {
          left: previousTextRect.left,
          right: previousTextRect.right,
          width: previousTextRect.width,
          height: previousTextRect.height,
        },
        previousTextAlign: getComputedStyle(previous).textAlign,
        previousAfterContent: getComputedStyle(previous, "::after").content,
        previousLayout: {
          direction: getComputedStyle(previous).direction,
          display: getComputedStyle(previous).display,
          justifyContent: getComputedStyle(previous).justifyContent,
          afterDirection: getComputedStyle(previous, "::after").direction,
          afterTextAlign: getComputedStyle(previous, "::after").textAlign,
          afterTransform: getComputedStyle(previous, "::after").transform,
        },
        fieldHeights: fields.map((field) => rect(field).height),
        fieldGaps: fields.slice(1).map((field, index) => rect(field).top - rect(fields[index]).bottom),
        confirm: { width: confirmRect.width, height: confirmRect.height },
      };
    });

    expect(personalGeometry.board).toEqual(questionnaireRail);
    expect(personalGeometry.form).toEqual(questionnaireRail);
    expect(personalGeometry.actions).toEqual(questionnaireRail);
    expect(personalGeometry.labelRight).toBeCloseTo(questionnaireRail.right, 1);
    expect(personalGeometry.phoneLabel.whiteSpace).toBe("nowrap");
    expect(personalGeometry.phoneLabel.scrollWidth).toBeLessThanOrEqual(personalGeometry.phoneLabel.width + 1);
    expect(personalGeometry.dots).toHaveLength(2);
    expect(Math.abs(personalGeometry.dots[0].left - personalGeometry.dots[1].left)).toBeCloseTo(53, 0);
    expect(personalGeometry.previousText.height).toBeGreaterThan(0);
    expect(personalGeometry.previousTextAlign).toBe("right");
    expect(personalGeometry.previousAfterContent).toBe("none");
    expect(personalGeometry.previousLayout).toEqual({ direction: "rtl", display: "flex", justifyContent: "flex-end", afterDirection: "rtl", afterTextAlign: "right", afterTransform: "none" });
    for (const field of personalGeometry.fields) {
      expect(field.left).toBeCloseTo(questionnaireRail.left, 1);
      expect(field.right).toBeLessThanOrEqual(questionnaireRail.right + 1);
    }
    expect(personalGeometry.confirm).toEqual({ width: 145, height: 48 });
    if (viewport.name === "mobile") {
      await page.screenshot({ path: "docs/evidence/us-09-t06i/personal-info-mobile-reference.png" });
    }
    for (const height of personalGeometry.fieldHeights) expect(height).toBeCloseTo(36, 0);
    for (const gap of personalGeometry.fieldGaps) expect(gap).toBeCloseTo(8, 0);

    await page.goto("/verify-code");
    await expect(page.locator(".hp-loan-otp-card")).toBeVisible();
    await page.waitForTimeout(100);
    const otpGeometry = await page.evaluate(() => {
      const cardRect = document.querySelector(".hp-loan-otp-card").getBoundingClientRect();
      const actionRect = document.querySelector(".hp-loan-otp-card + .hp-question-actions").getBoundingClientRect();
      const confirmRect = document.querySelector(".hp-loan-otp-card + .hp-question-actions .hp-next-question").getBoundingClientRect();
      return {
        card: { left: cardRect.left, right: cardRect.right, width: cardRect.width },
        actions: { left: actionRect.left, right: actionRect.right, width: actionRect.width },
        confirm: { width: confirmRect.width, height: confirmRect.height },
        dots: [...document.querySelectorAll(".hp-step-dot")].map((dot) => {
          const dotRect = dot.getBoundingClientRect();
          return {
            left: dotRect.left,
            top: dotRect.top,
            width: dotRect.width,
            height: dotRect.height,
          };
        }),
      };
    });
    expect(otpGeometry.card).toEqual(questionnaireRail);
    expect(otpGeometry.actions).toEqual(questionnaireRail);
    expect(otpGeometry.confirm).toEqual({ width: 145, height: 48 });
    expect(otpGeometry.dots).toEqual(personalGeometry.dots);
    if (viewport.name === "mobile") await page.screenshot({ path: "docs/evidence/us-09-t06i/verify-code-mobile-reference.png" });
  });
}

test("direct result and action routes fail closed without an active-tab session", async ({ page }) => {
  await page.goto("/loan-results");
  await expect(page.getByText(/ابتدا پرسشنامه را در همین تب کامل کنید/)).toBeVisible();
  await expect(page.getByRole("button", { name: "شروع پرسشنامه" })).toBeVisible();
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });

  await page.goto("/loan-request");
  await expect(page.getByText(/ابتدا پرسشنامه را در همین تب کامل/)).toBeVisible();
});

for (const viewport of [
  { name: "desktop", width: 1280, height: 720 },
  { name: "mobile", width: 360, height: 800 },
]) {
  test(`${viewport.name} keeps card identity, filters and ten selections usable`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await mockRecommendationJourney(page);
    await completeQuestionnaire(page);
    await page.evaluate(() => window.scrollTo(0, 0));

    const cards = page.locator(".hp-serving-loan-card");
    await expect(cards).toHaveCount(8);
    await expectCardTextRules(cards.first(), { titleShouldFit: true });
    await expectCardTextRules(cards.nth(1), { titleShouldFit: true });
    await expectCardTextRules(cards.nth(6), { titleShouldFit: false });
    await expectStableLogoOffsets(cards.first(), cards.nth(1));
    await expectFilterMenuAboveCards(page);
    await expectScrollableBankFilter(page);
    await expectLoanSaveFeedback(page);
    await page.screenshot({ path: `docs/evidence/us-09-t06h/${viewport.name}-results-card-layout.png`, fullPage: true });

    await page.getByRole("button", { name: "مقایسه وام" }).click();
    await expect(page).toHaveURL(/\/compare-loans$/);
    const compareCards = page.locator(".hp-loan-compare-card");
    await expect(compareCards).toHaveCount(10);
    await expectCardTextRules(compareCards.first(), { titleShouldFit: true });
    await expectCardTextRules(compareCards.nth(1), { titleShouldFit: true });
    await expectCardTextRules(compareCards.nth(6), { titleShouldFit: false });
    await expectStableLogoOffsets(compareCards.first(), compareCards.nth(1));
    await expectStableCheckboxOffsets(compareCards);
    await expectCompatibilityPercentScale(compareCards.first());
    await expectComparisonMatchTopOffset(compareCards.first());

    for (const checkbox of await page.locator(".hp-loan-compare-check").all()) await checkbox.click();
    await expect(page.locator(".hp-loan-compare-check[aria-pressed='true']")).toHaveCount(10);
    await scrollActivePageToBottom(page);
    const lastCard = compareCards.last();
    await expect(lastCard).toBeVisible();
    const clearance = await page.evaluate(() => {
      const card = document.querySelector(".hp-loan-compare-card:last-child").getBoundingClientRect();
      const bar = document.querySelector(".hp-simple-compare-bottom-bar").getBoundingClientRect();
      return { cardBottom: card.bottom, barTop: bar.top };
    });
    expect(clearance.cardBottom).toBeLessThanOrEqual(clearance.barTop + 1);
    await page.screenshot({ path: `docs/evidence/us-09-t06h/${viewport.name}-compare-ten-loans.png`, fullPage: true });

    await page.getByRole("button", { name: /مقایسه کن/ }).click();
    await expect(page).toHaveURL(/\/compare-result$/);
    await expect(page.locator(".hp-compare-result-card")).toHaveCount(10);
    const comparisonResultCardHeight = await page.locator(".hp-compare-result-card").first().evaluate((card) => card.getBoundingClientRect().height);
    await scrollActivePageToBottom(page);
    const resultClearance = await page.evaluate(() => {
      const card = document.querySelector(".hp-compare-result-card:last-child").getBoundingClientRect();
      const button = document.querySelector(".hp-compare-result-bottom-bar button").getBoundingClientRect();
      return button.top - card.bottom;
    });
    expect(resultClearance).toBeGreaterThanOrEqual(20);
    await page.screenshot({ path: `docs/evidence/us-09-t06h/${viewport.name}-compare-result-clearance.png` });
    await page.getByRole("button", { name: "بازگشت" }).click();
    await expect(page).toHaveURL(/\/compare-loans$/);
    await expect(page.locator(".hp-loan-compare-check[aria-pressed='true']")).toHaveCount(10);
    await expectComparisonSelectionGeometry(compareCards.first(), comparisonResultCardHeight);
  });
}

async function mockRecommendationJourney(page) {
  await page.route("**/api/v1/questionnaire/sessions", (route) => route.fulfill({ status: 201, json: { sessionId, expiresAt: "2027-01-01T00:00:00Z", answers: {} } }));
  await page.route("**/api/v1/questionnaire/sessions/*/answers/*", (route) => route.fulfill({ json: { sessionId, expiresAt: "2027-01-01T00:00:00Z", answers: {} } }));
  await page.route("**/api/v1/recommendations", (route) => route.fulfill({ json: response }));
  await page.route("**/api/v1/loans/*", (route) => {
    const loanId = decodeURIComponent(new URL(route.request().url()).pathname.split("/").at(-1));
    const recommendation = [...response.rankedRecommendations, ...response.lowCompatibilityRecommendations, ...response.needsReview].find((item) => item.loanId === loanId);
    return route.fulfill({ json: {
      loanId,
      lenderName: recommendation.lenderName,
      loanName: recommendation.loanName,
      bankLogoReference: recommendation.bankLogoReference,
      maxAmountTomans: 500000000,
      monthlyInstallmentTomans: 12000000,
      maxRepaymentMonths: 48,
      interestRatePercent: 18,
      depositRequired: "خیر",
      depositHoldingMonths: null,
      loanToDepositRatioPercent: null,
      guaranteeType: "ضامن رسمی",
      requiredDepositAccount: null,
      conditions: ["مدارک هویتی"],
    } });
  });
}

async function completeQuestionnaire(page) {
  await page.goto("/question/3");
  for (const _question of questionnaire.questions) {
    await page.getByRole("radio").first().click();
    await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  }
  await expect(page).toHaveURL(/\/personal-info$/);
  const personalInputs = page.locator(".hp-personal-info-form input");
  await personalInputs.nth(0).fill("علی");
  await personalInputs.nth(1).fill("رضایی");
  await personalInputs.nth(2).fill("۹۱۲۳۴۵۶۷۸۹");
  await page.locator(".hp-personal-dropdown-trigger").nth(0).click();
  await page.getByRole("option", { name: "تا ۲۲ میلیون تومان" }).click();
  await page.locator(".hp-personal-dropdown-trigger").nth(1).click();
  await page.getByRole("option", { name: "کارمند (شرکت یا اداره)" }).click();
  await page.getByRole("button", { name: "تایید" }).click();
  await expect(page).toHaveURL(/\/verify-code$/);
  const otpInputs = page.locator(".hp-loan-otp-row input");
  for (const [index, digit] of [..."۱۲۳۴۵۶"].entries()) await otpInputs.nth(index).fill(digit);
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 7000 });
}

async function scrollActivePageToBottom(page) {
  await page.evaluate(() => {
    const shell = document.querySelector(".hp-questionnaire-shell");
    shell.scrollTop = shell.scrollHeight;
  });
}

async function expectCardTextRules(card, { titleShouldFit }) {
  const bankName = card.locator(".hp-bank-name");
  const loanTitle = card.locator(".hp-loan-result-head strong");
  await expect(bankName).toBeVisible();
  await expect(loanTitle).toBeVisible();

  const bankMetrics = await bankName.evaluate((element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    const cardRect = element.closest("article").getBoundingClientRect();
    const logoRect = element.closest(".hp-bank-identity").querySelector(".hp-bank-logo-box").getBoundingClientRect();
    return {
      whiteSpace: style.whiteSpace,
      textOverflow: style.textOverflow,
      scrollWidth: element.scrollWidth,
      clientWidth: element.clientWidth,
      inside: rect.left >= cardRect.left - 1 && rect.right <= cardRect.right + 1,
      bankRight: rect.right,
      logoRight: logoRect.right,
      rightAlignmentDelta: Math.abs(rect.right - logoRect.right),
      title: element.getAttribute("title"),
      text: element.textContent.replace(/[«»]/g, ""),
    };
  });
  expect(bankMetrics.whiteSpace).toBe("nowrap");
  expect(bankMetrics.textOverflow).not.toBe("ellipsis");
  expect(bankMetrics.scrollWidth).toBeLessThanOrEqual(bankMetrics.clientWidth + 1);
  expect(bankMetrics.inside).toBe(true);
  expect(bankMetrics.rightAlignmentDelta, JSON.stringify(bankMetrics)).toBeLessThanOrEqual(1);
  expect(bankMetrics.title).toBe(bankMetrics.text);

  const titleMetrics = await loanTitle.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      whiteSpace: style.whiteSpace,
      overflow: style.overflow,
      textOverflow: style.textOverflow,
      scrollWidth: element.scrollWidth,
      clientWidth: element.clientWidth,
      title: element.getAttribute("title"),
      text: element.textContent,
    };
  });
  expect(titleMetrics.whiteSpace).toBe("nowrap");
  expect(titleMetrics.overflow).toBe("hidden");
  expect(titleMetrics.textOverflow).toBe("ellipsis");
  expect(titleMetrics.title).toBe(titleMetrics.text);
  if (titleShouldFit) expect(titleMetrics.scrollWidth).toBeLessThanOrEqual(titleMetrics.clientWidth + 1);
  else expect(titleMetrics.scrollWidth).toBeGreaterThan(titleMetrics.clientWidth);
  await expectTitleTopOffset(card, ".hp-loan-result-head strong");
}

async function expectCompatibilityPercentScale(card) {
  const match = card.locator(".hp-loan-match");
  const percent = match.locator(".hp-loan-percent");
  const sizes = await match.evaluate((element) => ({
    match: Number.parseFloat(getComputedStyle(element).fontSize),
    percent: Number.parseFloat(getComputedStyle(element.querySelector(".hp-loan-percent")).fontSize),
  }));
  expect(sizes.percent / sizes.match).toBeCloseTo(1.2, 2);
  await expect(percent).toBeVisible();
}

async function expectTitleTopOffset(card, selector) {
  const offset = await titleOffsetFromCard(card, selector);
  expect(offset.top).toBeCloseTo(30, 0);
}

async function expectComparisonMatchTopOffset(card) {
  const offset = await card.evaluate((element) => {
    const cardRect = element.getBoundingClientRect();
    const matchRect = element.querySelector(".hp-loan-match").getBoundingClientRect();
    return matchRect.top - cardRect.top;
  });
  expect(offset).toBeCloseTo(98, 0);
}

async function expectComparisonSelectionGeometry(card, expectedHeight) {
  const metrics = await card.evaluate((element) => {
    const cardRect = element.getBoundingClientRect();
    const matchRect = element.querySelector(".hp-loan-match").getBoundingClientRect();
    const checkboxRect = element.querySelector(".hp-loan-compare-check").getBoundingClientRect();
    return {
      height: cardRect.height,
      matchCenter: matchRect.top - cardRect.top + matchRect.height / 2,
      checkboxCenter: checkboxRect.top - cardRect.top + checkboxRect.height / 2,
    };
  });
  expect(Math.abs(metrics.height - expectedHeight)).toBeLessThanOrEqual(1);
  expect(Math.abs(metrics.matchCenter - metrics.checkboxCenter)).toBeLessThanOrEqual(1);
}

async function expectStableLogoOffsets(firstCard, secondCard) {
  const first = await logoOffsetFromCard(firstCard);
  const second = await logoOffsetFromCard(secondCard);
  expect(Math.abs(first.right - second.right)).toBeLessThanOrEqual(1);
  expect(Math.abs(first.top - second.top)).toBeLessThanOrEqual(1);
}

async function expectStableCheckboxOffsets(cards) {
  const offsets = await cards.evaluateAll((elements) => elements.map((element) => {
    const card = element.getBoundingClientRect();
    const checkbox = element.querySelector(".hp-loan-compare-check").getBoundingClientRect();
    return { right: card.right - checkbox.right };
  }));
  for (const offset of offsets) expect(Math.abs(offset.right - offsets[0].right)).toBeLessThanOrEqual(1);
  expect(offsets[0].right).toBeGreaterThanOrEqual(11);
}

async function expectScrollableBankFilter(page) {
  await page.getByRole("button", { name: "نام بانک" }).click();
  const menu = page.locator(".hp-loan-filter-menu.is-scrollable");
  await expect(menu).toBeVisible();
  expect(await menu.evaluate((element) => element.scrollHeight > element.clientHeight)).toBe(true);
  await menu.evaluate((element) => { element.scrollTop = element.scrollHeight; });
  await page.getByRole("option", { name: "بانک سینا" }).last().click();
  await expect(page.locator(".hp-serving-loan-card")).toHaveCount(1);
  await expect(page.locator(".hp-serving-loan-card")).toContainText("وام سینا");
  await page.getByRole("button", { name: "نام بانک" }).click();
  await page.getByRole("option", { name: "نام بانک" }).click();
  await expect(page.locator(".hp-serving-loan-card")).toHaveCount(8);
}

async function expectLoanSaveFeedback(page) {
  const save = page.getByRole("button", { name: "ذخیره وام میثاق ۲" });
  const card = page.locator(".hp-serving-loan-card").filter({ hasText: "میثاق ۲" }).first();
  await expect(save).toHaveAttribute("aria-pressed", "false");
  await expect(save.locator("img")).toHaveAttribute("src", /save-linear\.png$/);
  await save.click();
  await expect(save).toHaveAttribute("aria-pressed", "true");
  await expect(save.locator("img")).toHaveAttribute("src", /save-bold\.png$/);
  const toast = page.getByText("وام مورد نظر با موفقیت ذخیره شد", { exact: true });
  await expect(toast).toBeVisible();
  await expect(toast).toHaveCSS("background-color", "rgb(191, 255, 233)");
  const geometry = await Promise.all([toast.boundingBox(), card.boundingBox()]);
  expect(geometry[0].y + geometry[0].height).toBeLessThanOrEqual(geometry[1].y);
  await page.waitForTimeout(2100);
  await expect(toast).toHaveCount(0);
  await save.click();
  await expect(save).toHaveAttribute("aria-pressed", "false");
  await expect(save.locator("img")).toHaveAttribute("src", /save-linear\.png$/);
  await expect(toast).toHaveCount(0);
}

async function expectFilterMenuAboveCards(page) {
  await page.getByRole("button", { name: "نمایش نتایج" }).click();
  const option = page.getByRole("option", { name: "کمترین تطابق" });
  await expect(option).toBeVisible();
  expect(await option.evaluate((element) => {
    const rect = element.getBoundingClientRect();
    const hit = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
    return element === hit || element.contains(hit);
  })).toBe(true);
  await option.click();
  await expect(page.getByText("وام زیر آستانه")).toBeVisible();
  await page.getByRole("button", { name: "نمایش نتایج" }).click();
  await page.getByRole("option", { name: "بیشترین تطابق" }).click();
  await expect(page.getByText("میثاق ۲")).toBeVisible();
  await expect(page.locator(".hp-serving-loan-card img").first()).toHaveJSProperty("complete", true);
}
