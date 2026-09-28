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
  rankedRecommendations: [{ loanId: "published-loan", lenderName: "بانک ملت", loanName: "وام منتشرشده", bankLogoReference: "https://cdn.example.test/published-bank.svg", compatibilityScore: 0.91, compatibilityReason: "سازگاری دسته‌بندی شرایط وام با پاسخ‌های ثبت‌شدهٔ شما" }, ...additionalRankedRecommendations],
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
    loanId: "published-loan", lenderName: "بانک ملت", loanName: "وام منتشرشده", bankLogoReference: "https://cdn.example.test/published-bank.svg",
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
  await expect(page).toHaveURL(/\/loan-results$/);
  await expect(page.getByText("وام منتشرشده")).toBeVisible();
  await expect(page.locator(".hp-loan-result-head img").first()).toHaveAttribute("src", /bank-logos/);
  const resultLogo = page.locator(".hp-loan-result-head img").first();
  await expect(resultLogo).toBeVisible();
  await expect(resultLogo).toHaveJSProperty("complete", true);
  expect(await resultLogo.evaluate((image) => image.naturalWidth > 0 && image.naturalHeight > 0)).toBe(true);
  const shortNameLogoOffset = await logoOffsetFromCard(page.locator(".hp-serving-loan-card").first());
  const resultTitleOffset = await titleOffsetFromCard(page.locator(".hp-serving-loan-card").first(), ".hp-loan-result-head strong");
  await expect(page.locator(".hp-serving-loan-card .hp-loan-percent").first()).toHaveAttribute("dir", "ltr");
  await expect(page.locator(".hp-serving-loan-card .hp-loan-percent").first()).toHaveText("٪۹۱");
  const resultPercentParts = await page.locator(".hp-serving-loan-card .hp-loan-percent").first().locator("span").evaluateAll((parts) => parts.map((part) => part.getBoundingClientRect().x));
  expect(resultPercentParts[0]).toBeLessThan(resultPercentParts[1]);
  await expectCompatibilityPercentScale(page.locator(".hp-serving-loan-card").first());
  const assetResponse = await page.request.get(await resultLogo.getAttribute("src"));
  expect(assetResponse.ok()).toBe(true);
  expect(assetResponse.headers()["content-type"]).toContain("image/svg+xml");
  await page.getByRole("button", { name: "نمایش نتایج" }).click();
  await page.getByRole("option", { name: "کمترین تطابق" }).click();
  await expect(page.getByText("وام زیر آستانه")).toBeVisible();
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
  await expectLogoOffsets(page.locator(".hp-loan-detail-card"), shortNameLogoOffset);
  const declaredInterestParts = await page.locator(".hp-loan-detail-card .hp-loan-percent").locator("span").evaluateAll((parts) => parts.map((part) => part.getBoundingClientRect().x));
  expect(declaredInterestParts[0]).toBeLessThan(declaredInterestParts[1]);
  await page.getByRole("button", { name: /بازگشت/ }).first().click();
  await expect(page.getByText("وام منتشرشده")).toBeVisible();

  await expect(page.getByRole("button", { name: "ثبت درخواست همزمان وام بانکی" })).toBeDisabled();

  await page.getByRole("button", { name: "مقایسه وام" }).click();
  await expect(page).toHaveURL(/\/compare-loans$/);
  await expect(page.locator(".hp-loan-compare-card .hp-loan-result-head img").first()).toHaveAttribute("src", /bank-logos/);
  expect(await page.locator(".hp-loan-compare-card .hp-loan-result-head img").first().evaluate((image) => image.naturalWidth > 0)).toBe(true);
  await expectLogoOffsets(page.locator(".hp-loan-compare-card"), shortNameLogoOffset);
  await expectCompatibilityPercentScale(page.locator(".hp-loan-compare-card").first());
  await expectVerticalShift(page.locator(".hp-loan-compare-card .hp-loan-match").first(), 0.2);
  await page.screenshot({ path: "docs/evidence/us-09-t06h/desktop-bank-logo-anchor.png", fullPage: true });
  await page.setViewportSize({ width: 360, height: 800 });
  await expectLogoOffsets(page.locator(".hp-loan-compare-card"), shortNameLogoOffset);
  await page.screenshot({ path: "docs/evidence/us-09-t06h/mobile-bank-logo-anchor.png", fullPage: true });
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.getByRole("button", { name: "انتخاب وام منتشرشده" }).click();
  await page.getByRole("button", { name: "انتخاب وام زیر آستانه" }).click();
  await page.getByRole("button", { name: /مقایسه کن/ }).click();
  await expect(page).toHaveURL(/\/compare-result$/);
  await expect(page.locator(".hp-compare-result-card")).toHaveCount(2);
  await expectVerticalShift(page.locator(".hp-compare-result-card > strong").first(), -0.2);
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
  await expect(page.getByRole("button", { name: "انتخاب وام منتشرشده" })).toHaveClass(/is-selected/);
  await expect(page.getByRole("button", { name: "انتخاب وام زیر آستانه" })).toHaveClass(/is-selected/);

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
    await expectVerticalShift(compareCards.first().locator(".hp-loan-match"), 0.2);

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
  await expect(page).toHaveURL(/\/loan-results$/);
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
  await expectVerticalShift(loanTitle, -0.2);
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

async function expectVerticalShift(locator, expectedRatio) {
  const metrics = await locator.evaluate((element) => {
    const rect = element.getBoundingClientRect();
    const matrix = new DOMMatrixReadOnly(getComputedStyle(element).transform);
    return { height: rect.height, translateY: matrix.m42 };
  });
  expect(metrics.translateY).toBeCloseTo(metrics.height * expectedRatio, 1);
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
  await expect(page.getByText("وام منتشرشده")).toBeVisible();
  await expect(page.locator(".hp-serving-loan-card img").first()).toHaveJSProperty("complete", true);
}
