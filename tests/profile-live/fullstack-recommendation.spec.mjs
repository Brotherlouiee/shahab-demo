import { expect, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import questionnaire from "../../data/contracts/questionnaire-configuration.v1.json" with { type: "json" };

// This fixture mutates security metadata only in CI's named disposable database.
// It never resets business rows, volumes or an owner's local database.
function database(code) {
  return execFileSync("python", ["-c", `
import os, json
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
url = os.environ.get("SHAHAB_DATABASE_URL", "")
assert os.environ.get("SHAHAB_ENVIRONMENT") == "local"
assert make_url(url).database == "shahab_profile_test", "requires disposable profile CI database"
engine = create_engine(url)
${code}
engine.dispose()
`], { encoding: "utf8" }).trim();
}

test.beforeAll(() => {
  database(`from sqlalchemy.orm import Session
from pathlib import Path
from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config
with Session(engine) as session, session.begin():
    materialize_official_sources(session, loan_manifest=build_manifest(), config_manifest=build_config(),
        questionnaire=json.loads(Path("data/contracts/questionnaire-configuration.v1.json").read_text()),
        identifiers=json.loads(Path("data/contracts/canonical-identifiers.v1.json").read_text()),
        actor_reference="CI-US12-T02-journey", approval_reason="source-backed release-gate fixture")`);
});

test.beforeEach(() => {
  // Test isolation of the 120-second global quota, not a production bypass.
  database(`with engine.begin() as connection:
    connection.execute(text("DELETE FROM account_otp_quota_events"))`);
});


const persian = value => value.replace(/[0-9]/g, digit => "۰۱۲۳۴۵۶۷۸۹"[Number(digit)]);

test("full questionnaire, OTP, server partitions, published details and comparison", async ({ page }, testInfo) => {
  // Retain the original journey's budget, including the approved five-second spinner.
  test.setTimeout(60_000);
  const answerWrites = [];
  const recommendationPosts = [];
  const detailRequests = [];
  page.on("request", request => {
    const path = new URL(request.url()).pathname;
    if (/\/answers\/[^/]+$/.test(path) && request.method() === "PUT") answerWrites.push(request);
    if (path === "/api/v1/recommendations" && request.method() === "POST") recommendationPosts.push(request);
    if (path.startsWith("/api/v1/loans/")) detailRequests.push(request);
  });

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/question/3");
  for (const question of questionnaire.questions) {
    await expect(page.getByRole("heading", { name: persian(question.prompt).replace(/\s+/g, " ").trim() })).toBeVisible();
    const answer = page.getByRole("radio").first();
    await answer.click();
    await expect(answer).toBeChecked();
    const next = page.getByRole("button", { name: "پاسخ به سوال بعد" });
    await expect(next).toBeEnabled();
    await next.click();
  }

  // This form and server-backed mock verification supersede the old pre-OTP flow.
  await expect(page).toHaveURL(/\/personal-info$/);
  const inputs = page.locator(".hp-personal-info-form input");
  await inputs.nth(0).fill("آزمون");
  await inputs.nth(1).fill("کاربر");
  const phone = "09012340931"; // Synthetic local-only fixture; never sent to an SMS provider.
  await inputs.nth(2).fill(phone.slice(2));
  await expect(inputs.nth(2)).toHaveValue(persian(phone.slice(2)));
  await page.locator(".hp-personal-dropdown-trigger").nth(0).click();
  await page.getByRole("option", { name: "تا ۲۲ میلیون تومان" }).click();
  await page.locator(".hp-personal-dropdown-trigger").nth(1).click();
  await page.getByRole("option", { name: "کارمند (شرکت یا اداره)" }).click();
  await expect(page.getByRole("button", { name: "تایید و جستجوی وام", exact: true })).toBeEnabled();
  await page.getByRole("button", { name: "تایید و جستجوی وام", exact: true }).click();
  await expect(page).toHaveURL(/\/verify-code$/);
  for (const [index, digit] of [..."123456"].entries()) {
    await page.locator(".hp-loan-otp-row input").nth(index).fill(digit);
  }
  const recommended = page.waitForResponse(response =>
    new URL(response.url()).pathname === "/api/v1/recommendations" && response.request().method() === "POST");
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  const response = await recommended;
  expect(response.status()).toBe(200);
  const payload = await response.json();
  expect(payload.rankedRecommendations.length).toBeGreaterThan(1);
  expect(payload.lowCompatibilityRecommendations.length).toBeGreaterThan(0);
  expect(payload.needsReview.length).toBeGreaterThan(0);
  expect(Object.keys(response.request().postDataJSON())).toEqual(["sessionId"]);
  expect(recommendationPosts).toHaveLength(1);
  expect(answerWrites.map(request => new URL(request.url()).pathname.split("/").at(-1)))
    .toEqual(questionnaire.questions.map(question => question.questionId));
  expect(answerWrites.map(request => request.postDataJSON()))
    .toEqual(questionnaire.questions.map(question => ({ answerId: question.answerOptions[0].answerId })));

  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 7000 });
  const cards = page.locator(".hp-serving-loan-card");
  await expect(cards).toHaveCount(payload.rankedRecommendations.length);
  expect(detailRequests).toHaveLength(0); // All card summaries come from the one server snapshot.
  await testInfo.attach("desktop-results", { body: await page.screenshot(), contentType: "image/png" });

  async function mode(label) {
    await page.getByRole("button", { name: "نمایش نتایج", exact: true }).click();
    await page.getByRole("option", { name: label, exact: true }).click();
  }
  await mode("کمترین تطابق");
  await expect(cards).toHaveCount(payload.lowCompatibilityRecommendations.length);
  const low = [...payload.lowCompatibilityRecommendations].sort((a, b) => b.compatibilityScore - a.compatibilityScore);
  await expect(cards.locator(".hp-loan-result-head > strong")).toHaveText(low.map(item => persian(item.loanName)));
  await page.setViewportSize({ width: 390, height: 844 });
  await mode("وضعیت متغیر");
  await expect(cards).toHaveCount(payload.needsReview.length);
  await expect(cards.locator(".hp-loan-match .hp-loan-percent")).toHaveCount(0);
  await expect(cards.first().locator(".hp-loan-match")).toContainText("نامشخص");
  await testInfo.attach("mobile-needs-review", { body: await page.screenshot(), contentType: "image/png" });

  await mode("بیشترین تطابق");
  const loan = payload.rankedRecommendations[0];
  const details = page.waitForResponse(reply => new URL(reply.url()).pathname === "/api/v1/loans/" + loan.loanId);
  await cards.first().locator(".hp-loan-docs-link").click();
  const detailResponse = await details;
  expect(detailResponse.status()).toBe(200);
  const detail = await detailResponse.json();
  expect(detail.loanId).toBe(loan.loanId);
  await expect(page.locator(".hp-loan-details-conditions")).toBeVisible();
  await expect(page.locator(".hp-loan-details-conditions li")).toHaveText(detail.conditions.map(persian));
  await page.getByRole("button", { name: "بازگشت", exact: true }).first().click();
  await expect(page).toHaveURL(/\/loan-results$/);
  expect(recommendationPosts).toHaveLength(1); // Back reuses the result; no rescoring.

  await page.getByRole("button", { name: "مقایسه وام", exact: true }).click();
  await expect(page.getByRole("button", { name: /مقایسه کن/ })).toBeDisabled();
  await page.locator(".hp-loan-compare-check").nth(0).click();
  await page.locator(".hp-loan-compare-check").nth(1).click();
  await page.getByRole("button", { name: /مقایسه کن/ }).click();
  await expect(page.locator(".hp-compare-result-card")).toHaveCount(2);
  await page.getByRole("button", { name: "تحلیل با هوش مصنوعی", exact: true }).click();
  await expect(page.locator(".hp-ai-analysis-message")).toContainText("provider خارجی فعال نیست؛ تحلیل ساختگی نمایش داده نمی‌شود.");
  await expect(page.getByRole("button", { name: "ارسال", exact: true })).toBeDisabled();
});
