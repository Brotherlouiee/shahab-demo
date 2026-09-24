import { expect, test } from "@playwright/test";

const sessionId = "opaque-test-session-id";
const firstAnswerId = "Q1.incomeInvestment";

async function mockQuestionnaireSessionApi(page, { failStart = false } = {}) {
  const requests = [];

  await page.route("**/api/v1/questionnaire/sessions", async (route) => {
    requests.push({ method: route.request().method(), url: route.request().url() });

    if (failStart) {
      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({ error: { code: "service_unavailable", message: "temporarily unavailable" } }),
      });
      return;
    }

    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({
        sessionId,
        expiresAt: "2026-09-24T12:30:00Z",
        answers: {},
      }),
    });
  });

  await page.route(`**/api/v1/questionnaire/sessions/${sessionId}/answers/Q1`, async (route) => {
    requests.push({
      method: route.request().method(),
      url: route.request().url(),
      body: route.request().postDataJSON(),
    });
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        sessionId,
        expiresAt: "2026-09-24T12:30:00Z",
        answers: { Q1: firstAnswerId },
      }),
    });
  });

  return requests;
}

test("blocks an incomplete canonical answer without creating a session", async ({ page }) => {
  const requests = await mockQuestionnaireSessionApi(page);

  await page.goto("/question/3");

  const next = page.getByRole("button", { name: "پاسخ به سوال بعد" });
  await expect(next).toBeDisabled();
  await expect(page.getByRole("radiogroup", { name: "نوع وام" })).toBeVisible();
  await expect(page.locator(".hp-questionnaire-page")).toHaveAttribute("dir", "rtl");
  expect(requests).toEqual([]);
});

test("saves only a canonical body answer, advances, and keeps the answer on same-tab back navigation", async ({ page }) => {
  const requests = await mockQuestionnaireSessionApi(page);

  await page.goto("/question/3");
  await page.getByRole("radio", {
    name: "مستقیماً برای کار، تولید یا خرید تجهیزاتی که درآمدم را بیشتر می‌کند سرمایه‌گذاری می‌کنم.",
  }).click();
  await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();

  await expect(page).toHaveURL(/\/question\/4$/);
  await expect(page.getByRole("heading")).toContainText("اگر دریافت این وام لغو شود");
  expect(requests).toEqual([
    { method: "POST", url: expect.stringMatching(/\/api\/v1\/questionnaire\/sessions$/) },
    {
      method: "PUT",
      url: expect.stringMatching(new RegExp(`/sessions/${sessionId}/answers/Q1$`)),
      body: { answerId: firstAnswerId },
    },
  ]);
  expect(requests[1].url).not.toContain(firstAnswerId);
  expect(page.url()).not.toContain(sessionId);
  expect(page.url()).not.toContain(firstAnswerId);

  await page.getByRole("button", { name: "بازگشت به سوال قبل" }).click();
  await expect(page).toHaveURL(/\/question\/3$/);
  await expect(page.getByRole("radio", {
    name: "مستقیماً برای کار، تولید یا خرید تجهیزاتی که درآمدم را بیشتر می‌کند سرمایه‌گذاری می‌کنم.",
  })).toHaveAttribute("aria-checked", "true");
  expect(requests).toHaveLength(2);
});

test("keeps the user on the question and announces a retryable save failure", async ({ page }) => {
  const requests = await mockQuestionnaireSessionApi(page, { failStart: true });

  await page.goto("/question/3");
  await page.getByRole("radio", {
    name: "مستقیماً برای کار، تولید یا خرید تجهیزاتی که درآمدم را بیشتر می‌کند سرمایه‌گذاری می‌کنم.",
  }).click();
  await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();

  await expect(page).toHaveURL(/\/question\/3$/);
  await expect(page.getByRole("alert")).toHaveText(
    "ذخیره پاسخ انجام نشد. لطفاً اتصال را بررسی کنید و دوباره تلاش کنید.",
  );
  expect(requests).toHaveLength(1);
});
