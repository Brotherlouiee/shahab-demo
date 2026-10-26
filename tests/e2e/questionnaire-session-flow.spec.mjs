import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";

const sessionId = "opaque-test-session-id";
const firstAnswerId = "Q1.incomeInvestment";
const questionnaireConfiguration = JSON.parse(
  readFileSync(new URL("../../data/contracts/questionnaire-configuration.v1.json", import.meta.url), "utf8"),
);
const canonicalIdentifiers = JSON.parse(
  readFileSync(new URL("../../data/contracts/canonical-identifiers.v1.json", import.meta.url), "utf8"),
);
const canonicalQuestionRoutes = Object.entries(canonicalIdentifiers.questionnaireRouteMap);

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

test("restores the saved selection after refresh before allowing back navigation", async ({ page }) => {
  const answers = {};
  await page.route("**/api/v1/questionnaire/sessions**", async (route) => {
    const request = route.request();
    if (request.method() === "POST") {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ sessionId, expiresAt: "2026-09-24T12:30:00Z", answers }),
      });
      return;
    }

    if (request.method() === "PUT") {
      const questionId = new URL(request.url()).pathname.split("/").at(-1);
      answers[questionId] = request.postDataJSON().answerId;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ sessionId, expiresAt: "2026-09-24T12:30:00Z", answers }),
    });
  });

  await page.goto("/question/3");
  const firstChoice = page.getByRole("radio", {
    name: "مستقیماً برای کار، تولید یا خرید تجهیزاتی که درآمدم را بیشتر می‌کند سرمایه‌گذاری می‌کنم.",
  });
  await firstChoice.click();
  await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  await expect(page).toHaveURL(/\/question\/4$/);
  await expect.poll(() => page.evaluate(
    () => window.history.state?.shahabRecommendation?.sessionId,
  )).toBe(sessionId);

  await page.reload();
  await expect(page).toHaveURL(/\/question\/4$/);
  await expect(page.locator(".hp-questionnaire-page")).toHaveAttribute("aria-busy", "false");
  await page.getByRole("button", { name: "بازگشت به سوال قبل" }).click();
  await expect(page).toHaveURL(/\/question\/3$/);
  await expect(page.getByRole("radio", {
    name: "مستقیماً برای کار، تولید یا خرید تجهیزاتی که درآمدم را بیشتر می‌کند سرمایه‌گذاری می‌کنم.",
  })).toHaveAttribute("aria-checked", "true");
});

test("restores every canonical answer as selected after next, refresh, and back", async ({ page }) => {
  const answers = {};
  const answerByQuestionId = new Map();
  const requestCounts = { starts: 0, reads: 0, writes: 0 };

  await page.route("**/api/v1/account-access/session", (route) => route.fulfill({
    status: 401,
    contentType: "application/json",
    body: JSON.stringify({ error: { code: "unauthorized", message: "unauthorized" } }),
  }));
  await page.route("**/api/v1/profiles/me", (route) => route.fulfill({
    status: 401,
    contentType: "application/json",
    body: JSON.stringify({ error: { code: "unauthorized", message: "unauthorized" } }),
  }));

  await page.route("**/api/v1/questionnaire/sessions**", async (route) => {
    const request = route.request();
    if (request.method() === "POST") requestCounts.starts += 1;
    if (request.method() === "GET") requestCounts.reads += 1;
    if (request.method() === "PUT") {
      requestCounts.writes += 1;
      const questionId = new URL(request.url()).pathname.split("/").at(-1);
      answers[questionId] = request.postDataJSON().answerId;
      answerByQuestionId.set(questionId, answers[questionId]);
    }
    await route.fulfill({
      status: request.method() === "POST" ? 201 : 200,
      contentType: "application/json",
      body: JSON.stringify({
        sessionId,
        expiresAt: "2026-10-27T12:30:00Z",
        answers,
      }),
    });
  });

  await page.goto(canonicalQuestionRoutes[0][0]);

  for (let index = 0; index < canonicalQuestionRoutes.length; index += 1) {
    const [route, questionId] = canonicalQuestionRoutes[index];
    const question = questionnaireConfiguration.questions.find((item) => item.questionId === questionId);
    const chosenOption = question.answerOptions[0];

    await expect(page).toHaveURL(new RegExp(`${route.replaceAll("/", "\\/")}$`));
    const selected = page.getByRole("radio", { name: chosenOption.label });
    await selected.click();
    await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();

    if (index < canonicalQuestionRoutes.length - 1) {
      const nextRoute = canonicalQuestionRoutes[index + 1][0];
      await expect(page).toHaveURL(new RegExp(`${nextRoute.replaceAll("/", "\\/")}$`));
    } else {
      await expect(page).toHaveURL(/\/personal-info$/);
    }

    await page.reload();
    if (index < canonicalQuestionRoutes.length - 1) {
      await expect(page).toHaveURL(new RegExp(`${canonicalQuestionRoutes[index + 1][0].replaceAll("/", "\\/")}$`));
      await expect(page.locator(".hp-questionnaire-page")).toHaveAttribute("aria-busy", "false");
    } else {
      await expect(page).toHaveURL(/\/personal-info$/);
      await expect(page.getByRole("button", { name: "بازگشت به مرحله قبل" })).toBeVisible();
      await expect.poll(() => requestCounts.reads).toBeGreaterThan(0);
    }

    await page.getByRole("button", {
      name: index < canonicalQuestionRoutes.length - 1 ? "بازگشت به سوال قبل" : "بازگشت به مرحله قبل",
    }).click();
    await expect(page).toHaveURL(new RegExp(`${route.replaceAll("/", "\\/")}$`));
    await expect(page.getByRole("radio", { name: chosenOption.label })).toHaveAttribute("aria-checked", "true");

    if (index < canonicalQuestionRoutes.length - 1) {
      await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
    }
  }

  expect(requestCounts.starts).toBe(1);
  expect(requestCounts.writes).toBe((canonicalQuestionRoutes.length * 2) - 1);
  expect(Object.keys(answers)).toEqual(canonicalQuestionRoutes.map(([, questionId]) => questionId));
  expect(answerByQuestionId.size).toBe(canonicalQuestionRoutes.length);
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
