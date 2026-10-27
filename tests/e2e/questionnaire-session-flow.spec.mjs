import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";

const sessionId = "opaque-test-session-id";
const questionnaireConfiguration = JSON.parse(
  readFileSync(new URL("../../data/contracts/questionnaire-configuration.v1.json", import.meta.url), "utf8"),
);
const canonicalIdentifiers = JSON.parse(
  readFileSync(new URL("../../data/contracts/canonical-identifiers.v1.json", import.meta.url), "utf8"),
);
const canonicalQuestionRoutes = Object.entries(canonicalIdentifiers.questionnaireRouteMap);

async function mockQuestionnaireSessionApi(page, { failStart = false, existingSession = false } = {}) {
  const answers = {};
  const flowAnswers = existingSession ? { loan_type: "shahab", entity_type: "person" } : {};
  let sessionExists = existingSession;
  const requests = [];

  if (existingSession) {
    await page.addInitScript((id) => {
      window.history.replaceState({ shahabRecommendation: { sessionId: id } }, "", window.location.href);
    }, sessionId);
  }

  await page.route("**/api/v1/questionnaire/sessions**", async (route) => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;
    requests.push({ method: request.method(), pathname });

    if (request.method() === "GET" && pathname.endsWith("/sessions/current")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(sessionExists
          ? { sessionId, expiresAt: "2026-10-27T12:30:00Z", answers, flowAnswers }
          : null),
      });
      return;
    }

    if (request.method() === "POST") {
      if (failStart) {
        await route.fulfill({
          status: 503,
          contentType: "application/json",
          body: JSON.stringify({ error: { code: "service_unavailable", message: "temporarily unavailable" } }),
        });
        return;
      }
      sessionExists = true;
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ sessionId, expiresAt: "2026-10-27T12:30:00Z", answers, flowAnswers }),
      });
      return;
    }

    if (request.method() === "PUT") {
      const parts = pathname.split("/");
      const flowIndex = parts.indexOf("flow-answers");
      const answerIndex = parts.indexOf("answers");
      if (flowIndex >= 0) flowAnswers[parts[flowIndex + 1]] = request.postDataJSON().answerId;
      if (answerIndex >= 0) answers[parts[answerIndex + 1]] = request.postDataJSON().answerId;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ sessionId, expiresAt: "2026-10-27T12:30:00Z", answers, flowAnswers }),
    });
  });

  return { answers, flowAnswers, requests };
}

test("direct later-question URL fails closed before the first entry answer", async ({ page }) => {
  const { requests } = await mockQuestionnaireSessionApi(page);
  await page.goto("/question/8");
  await expect(page).toHaveURL(/\/question\/1$/);
  await expect(page.locator(".hp-questionnaire-page h1")).toContainText("مایل به دریافت چه نوع وامی");
  await expect(page.getByRole("button", { name: "پاسخ به سوال بعد" })).toBeDisabled();
  expect(requests.filter(({ pathname }) => pathname === "/api/v1/questionnaire/sessions/current").length).toBeGreaterThan(0);
});

test("full URL navigation restores answers and redirects question six to the first unanswered question", async ({ page }) => {
  const { answers } = await mockQuestionnaireSessionApi(page);
  const firstFourRoutes = ["/question/1", "/question/2", "/question/3", "/question/4"];

  await page.goto(firstFourRoutes[0]);
  for (let index = 0; index < firstFourRoutes.length; index += 1) {
    await expect(page).toHaveURL(new RegExp(`${firstFourRoutes[index].replaceAll("/", "\\/")}$`));
    await page.getByRole("radio").nth(index === 1 ? 1 : 0).click();
    await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  }

  expect(answers).toEqual({ Q1: "Q1.incomeInvestment", Q2: "Q2.highCostBorrowing" });
  await page.goto("/question/6");
  await expect(page).toHaveURL(/\/question\/5$/);
  await expect(page.getByRole("radio").first()).toHaveAttribute("aria-checked", "false");

  await page.getByRole("button", { name: "بازگشت به سوال قبل" }).click();
  await expect(page).toHaveURL(/\/question\/4$/);
  await expect(page.getByRole("radio").first()).toHaveAttribute("aria-checked", "true");
  await page.getByRole("button", { name: "بازگشت به سوال قبل" }).click();
  await expect(page).toHaveURL(/\/question\/3$/);
  await expect(page.getByRole("radio").first()).toHaveAttribute("aria-checked", "true");
});

test("restores every visible answer after refresh and blocks jumps between all twelve steps", async ({ page }) => {
  const { answers, flowAnswers, requests } = await mockQuestionnaireSessionApi(page);
  const journey = [
    ["/question/1", "loan_type"],
    ["/question/2", "entity_type"],
    ...canonicalQuestionRoutes,
  ];

  await page.goto(journey[0][0]);
  for (let index = 0; index < journey.length; index += 1) {
    const [route] = journey[index];
    await expect(page).toHaveURL(new RegExp(`${route.replaceAll("/", "\\/")}$`));
    const choice = page.getByRole("radio").nth(index === 1 ? 1 : 0);
    await choice.click();
    await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();

    if (index < journey.length - 1) {
      await expect(page).toHaveURL(new RegExp(`${journey[index + 1][0].replaceAll("/", "\\/")}$`));
      await page.goto(journey[Math.min(index + 3, journey.length - 1)][0]);
      await expect(page).toHaveURL(new RegExp(`${journey[index + 1][0].replaceAll("/", "\\/")}$`));
    } else {
      await expect(page).toHaveURL(/\/personal-info$/);
    }

    await page.reload();
    if (index < journey.length - 1) {
      await expect(page).toHaveURL(new RegExp(`${journey[index + 1][0].replaceAll("/", "\\/")}$`));
    } else {
      await expect(page).toHaveURL(/\/personal-info$/);
    }

    const backName = index < journey.length - 1 ? "بازگشت به سوال قبل" : "بازگشت به مرحله قبل";
    await page.getByRole("button", { name: backName }).click();
    await expect(page).toHaveURL(new RegExp(`${route.replaceAll("/", "\\/")}$`));
    await expect(page.getByRole("radio").nth(index === 1 ? 1 : 0)).toHaveAttribute("aria-checked", "true");

    if (index < journey.length - 1) {
      await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
      await expect(page).toHaveURL(new RegExp(`${journey[index + 1][0].replaceAll("/", "\\/")}$`));
    }
  }

  expect(flowAnswers).toEqual({ loan_type: "shahab", entity_type: "person" });
  expect(Object.keys(answers)).toEqual(canonicalQuestionRoutes.map(([, questionId]) => questionId));
  expect(requests.filter(({ method }) => method === "POST")).toHaveLength(1);
  expect(page.url()).not.toContain(sessionId);
  for (const question of questionnaireConfiguration.questions) {
    expect(answers[question.questionId]).toBe(question.answerOptions[0].answerId);
  }
});

test("keeps the user on the current entry step and announces retryable API failure", async ({ page }) => {
  const { requests } = await mockQuestionnaireSessionApi(page, { failStart: true });
  await page.goto("/question/1");
  await page.getByRole("radio").first().click();
  await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();

  await expect(page).toHaveURL(/\/question\/1$/);
  await expect(page.getByRole("alert")).toHaveText(
    "ذخیره پاسخ انجام نشد. لطفاً اتصال را بررسی کنید و دوباره تلاش کنید.",
  );
  expect(requests).toContainEqual({ method: "POST", pathname: "/api/v1/questionnaire/sessions" });
  expect(requests.filter(({ pathname }) => pathname === "/api/v1/questionnaire/sessions/current").length)
    .toBeGreaterThan(0);
});

test("only commits supersession after an explicit fresh attempt saves its first answer", async ({ page }) => {
  const writes = [];
  const session = { sessionId: "fresh-test-session", expiresAt: "2026-10-27T12:30:00Z", answers: {}, flowAnswers: {} };
  await page.addInitScript(() => {
    window.history.replaceState({ shahabStartFreshQuestionnaire: true }, "", window.location.href);
  });
  await page.route("**/api/v1/questionnaire/sessions**", async (route) => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;
    if (request.method() === "GET" && pathname.endsWith("/sessions/current")) {
      await route.fulfill({ json: null });
      return;
    }
    if (request.method() === "POST") {
      await route.fulfill({ status: 201, json: session });
      return;
    }
    if (request.method() === "PUT") {
      writes.push({ pathname, body: request.postDataJSON() });
      const flowStep = pathname.split("/flow-answers/")[1];
      if (flowStep) session.flowAnswers[flowStep] = request.postDataJSON().answerId;
      await route.fulfill({ json: session });
      return;
    }
    await route.fulfill({ json: session });
  });

  await page.goto("/question/1");
  await page.getByRole("radio").first().click();
  expect(writes).toHaveLength(0);

  await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  await expect(page).toHaveURL(/\/question\/2$/);
  expect(writes[0].pathname).toContain("/flow-answers/loan_type");
  expect(writes[0].body).toEqual({ answerId: "shahab", supersedePrevious: true });

  await page.getByRole("radio").nth(1).click();
  await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  await expect(page).toHaveURL(/\/question\/3$/);
  expect(writes[1].pathname).toContain("/flow-answers/entity_type");
  expect(writes[1].body).toEqual({ answerId: "person" });
});

test("restores an answered canonical step from server state after refresh", async ({ page }) => {
  const { answers } = await mockQuestionnaireSessionApi(page, { existingSession: true });
  const question = questionnaireConfiguration.questions[0];
  answers[question.questionId] = question.answerOptions[1].answerId;
  await page.goto("/question/4");
  await expect(page).toHaveURL(/\/question\/4$/);
  await page.reload();
  await expect(page).toHaveURL(/\/question\/4$/);
  await page.getByRole("button", { name: "بازگشت به سوال قبل" }).click();
  await expect(page).toHaveURL(/\/question\/3$/);
  await expect(page.getByRole("radio").nth(1)).toHaveAttribute("aria-checked", "true");
});
