import { expect, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import questionnaire from "../../data/contracts/questionnaire-configuration.v1.json" with { type: "json" };

function database(code) {
  return execFileSync("python", ["-c", `
import os,json
from pathlib import Path
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
assert os.environ.get("SHAHAB_ENVIRONMENT") == "local"
url=os.environ["SHAHAB_DATABASE_URL"]
assert make_url(url).database == "shahab_profile_test", "requires disposable CI database"
engine=create_engine(url)
${code}
engine.dispose()
`], { encoding: "utf8" }).trim();
}

test.beforeAll(() => {
  database(`from sqlalchemy.orm import Session
from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config
with Session(engine) as db, db.begin():
    materialize_official_sources(db,loan_manifest=build_manifest(),config_manifest=build_config(),
        questionnaire=json.loads(Path("data/contracts/questionnaire-configuration.v1.json").read_text()),
        identifiers=json.loads(Path("data/contracts/canonical-identifiers.v1.json").read_text()),
        actor_reference="CI-bookmark-fixture",approval_reason="source-backed account bookmark regression")`);
});
const clearFixtureQuota = () => database(`with engine.begin() as c:
    c.execute(text("DELETE FROM account_otp_quota_events"))`);
test.beforeEach(clearFixtureQuota);
test.afterEach(clearFixtureQuota);

async function login(context, phone) {
  const requested = await context.request.post("/api/v1/account-access/request", { data: { phone } });
  expect(requested.status()).toBe(200);
  const verified = await context.request.post("/api/v1/account-access/verify", { data: { challengeId: (await requested.json()).challengeId, code: "123456" } });
  expect(verified.status()).toBe(200);
  return verified.json();
}

async function recommendation(context) {
  const started = await context.request.post("/api/v1/questionnaire/sessions");
  expect(started.status()).toBe(201);
  const sid = (await started.json()).sessionId;
  for (const [stepId, answerId] of [["loan_type", "shahab"], ["entity_type", "person"]]) {
    const flow = await context.request.put(`/api/v1/questionnaire/sessions/${sid}/flow-answers/${stepId}`, { data: { answerId } });
    expect(flow.status()).toBe(200);
  }
  for (const question of questionnaire.questions) {
    const answer = await context.request.put(`/api/v1/questionnaire/sessions/${sid}/answers/${question.questionId}`, { data: { answerId: question.answerOptions[0].answerId } });
    expect(answer.status()).toBe(200);
  }
  const response = await context.request.post("/api/v1/recommendations", { data: { sessionId: sid } });
  expect(response.status()).toBe(200);
  const result = await response.json();
  expect(result.rankedRecommendations.length).toBeGreaterThan(0);
  const history = await context.request.get("/api/v1/recommendation-history");
  expect(history.status()).toBe(200);
  return { loan: result.rankedRecommendations[0], result, sessionId: sid, historyId: result.historyId };
}

test("two devices share database bookmarks, another account cannot inherit them, logout clears only Shahab", async ({ browser, baseURL }) => {
  const a = await browser.newContext({ baseURL });
  const second = await browser.newContext({ baseURL });
  const b = await browser.newContext({ baseURL });
  try {
    const phone = "09000000821";
    const actor = await login(a, phone); await login(second, phone); await login(b, "09000000822");
    const { loan, historyId } = await recommendation(a);
    const page = await a.newPage();
    await page.goto(`/recommendation-history/${historyId}`);
    const card = page.locator(".hp-serving-loan-card").filter({ has: page.getByRole("button", { name: `ذخیره وام ${loan.loanName.replace(/[0-9]/g, digit => "۰۱۲۳۴۵۶۷۸۹"[Number(digit)])}` }) });
    console.log("F browser: historical card", loan.loanId, loan.loanName);
    await expect(card).toBeVisible();
    const save = card.locator(".hp-loan-save-button");
    const committed = page.waitForResponse(response => response.url().includes(`/bookmarks/${loan.loanId}`) && response.request().method() === "PUT");
    console.log("F browser: save");
    await save.click(); expect((await committed).status()).toBe(204);
    await expect(save).toHaveAttribute("aria-pressed", "true");
    await expect(page.locator(".hp-loan-save-toast")).toBeVisible();
    const firstList = await (await a.request.get("/api/v1/bookmarks")).json();
    expect((await (await second.request.get("/api/v1/bookmarks")).json()).items).toEqual(firstList.items);
    expect((await (await b.request.get("/api/v1/bookmarks")).json()).items).toEqual([]);
    const other = await second.newPage();
    console.log("F browser: second device");
    await other.goto("/saved-loans");
    await expect(other.locator(".hp-serving-loan-card")).toHaveCount(1);
    await other.reload(); await expect(other.locator(".hp-serving-loan-card")).toHaveCount(1);
    await other.locator(".hp-loan-docs-link").click();
    await expect(other).toHaveURL(/from=saved-loans/);
    await other.getByRole("button", { name: "بازگشت" }).click();
    await expect(other).toHaveURL(/\/saved-loans$/);

    // Historical results have the approved account header, not a hamburger menu.
    await page.locator("a.hp-questionnaire-brand").click();
    await expect(page).toHaveURL(/\/$/);
    await page.evaluate(() => {
      localStorage.setItem("another-app", "preserve"); sessionStorage.setItem("another-app", "preserve");
      localStorage.setItem("shahab.savedLoans", "legacy fixture");
      localStorage.setItem("shahab.personalInfo.phone", "synthetic fixture");
      sessionStorage.setItem("shahab.testDraft", "synthetic fixture");
    });
    console.log("F browser: logout");
    await page.locator("button.hp-menu-button").click();
    await page.getByRole("button", { name: "خروج از حساب کاربری" }).click();
    await page.getByRole("alertdialog").getByRole("button", { name: "خیر" }).click();
    expect((await a.request.get("/api/v1/bookmarks")).status()).toBe(200);
    await page.getByRole("button", { name: "خروج از حساب کاربری" }).click();
    const revoked = page.waitForResponse(response => response.url().endsWith("/account-access/logout"));
    await page.getByRole("alertdialog").getByRole("button", { name: "بله" }).click();
    expect((await revoked).status()).toBe(204);
    await expect(page).toHaveURL(/\/$/);
    const storage = await page.evaluate(() => ({ local: [...Object.keys(localStorage)], session: [...Object.keys(sessionStorage)], history: history.state }));
    expect(storage.local).toEqual(["another-app"]); expect(storage.session).toEqual(["another-app"]);
    expect(storage.history?.shahabRecommendation).toBeUndefined();
    const cookies = await a.cookies();
    expect(cookies.some(cookie => cookie.name === "shahab_account_access" || cookie.name.startsWith("shahab_questionnaire_proof_"))).toBe(false);
    expect((await a.request.get("/api/v1/bookmarks", { headers: { Authorization: `Bearer ${actor.accessToken}` } })).status()).toBe(401);
    await page.reload(); await page.locator("button.hp-menu-button").click();
    await expect(page.getByRole("button", { name: "ورود کاربر" })).toBeVisible();
    await login(a, "09000000822"); await page.goto("/saved-loans");
    await expect(page.locator(".hp-saved-loans-empty-state img")).toBeVisible();
    await login(a, phone); await page.reload();
    await expect(page.locator(".hp-serving-loan-card")).toHaveCount(1);
    const removed = page.waitForResponse(response => response.url().includes(`/bookmarks/${loan.loanId}`) && response.request().method() === "DELETE");
    await page.locator(".hp-loan-save-button").click(); expect((await removed).status()).toBe(204);
    await expect(page.locator(".hp-saved-loans-empty-state img")).toBeVisible();
    await other.reload(); await expect(other.locator(".hp-saved-loans-empty-state img")).toBeVisible();
    expect(Number(database(`with engine.connect() as c:
    print(c.scalar(text("SELECT count(*) FROM account_bookmarks WHERE removed_at IS NOT NULL")))`))).toBeGreaterThan(0);
  } finally { await Promise.allSettled([a.close(), second.close(), b.close()]); }
});

// A refreshed current result resolves its immutable snapshot, without rescoring or PII storage.
test("current result refresh and detail Back use only an owned historical reference", async ({ browser, baseURL }) => {
  const context = await browser.newContext({ baseURL });
  try {
    await login(context, "09000000823");
    const { loan, sessionId, historyId } = await recommendation(context);
    expect(historyId).toMatch(/^[a-f0-9-]{36}$/i);
    const page = await context.newPage();
    await page.addInitScript(({ sessionId, historyId }) => {
      if (location.pathname === "/loan-results" && !history.state?.shahabRecommendation)
        history.replaceState({ shahabRecommendation: { sessionId, historyId } }, "", location.href);
    }, { sessionId, historyId });
    let scoringRequests = 0;
    page.on("request", request => {
      if (request.method() === "POST" && new URL(request.url()).pathname === "/api/v1/recommendations") scoringRequests += 1;
    });
    await page.goto("/loan-results");
    await expect(page.locator(".hp-serving-loan-card").first()).toBeVisible();
    await page.reload();
    await expect(page.locator(".hp-serving-loan-card").first()).toBeVisible();
    expect(await page.evaluate(() => history.state.shahabRecommendation)).toEqual({ sessionId, historyId });
    await page.locator(".hp-loan-docs-link").first().click();
    await page.reload();
    await page.getByRole("button", { name: "بازگشت" }).click();
    await expect(page).toHaveURL(/\/loan-results$/);
    await expect(page.locator(".hp-serving-loan-card").first()).toBeVisible();
    expect(scoringRequests).toBe(0);
    expect(await page.evaluate(() => [...Object.keys(localStorage), ...Object.keys(sessionStorage)].filter(k => k.startsWith("shahab.")))).toEqual([]);
    expect((await context.request.get(`/api/v1/recommendation-history/${historyId}`)).status()).toBe(200);
  } finally { await context.close(); }
});

test("refresh restores persisted questionnaire answers on the same step from the real API", async ({ page }) => {
  const started = await page.request.post("/api/v1/questionnaire/sessions");
  expect(started.status()).toBe(201);
  const sessionId = (await started.json()).sessionId;
  for (const [stepId, answerId] of [["loan_type", "shahab"], ["entity_type", "person"]]) {
    const flow = await page.request.put(`/api/v1/questionnaire/sessions/${sessionId}/flow-answers/${stepId}`, { data: { answerId } });
    expect(flow.status()).toBe(200);
  }
  const firstQuestion = questionnaire.questions[0];
  const saved = await page.request.put(`/api/v1/questionnaire/sessions/${sessionId}/answers/${firstQuestion.questionId}`, {
    data: { answerId: firstQuestion.answerOptions[0].answerId },
  });
  expect(saved.status()).toBe(200);
  await page.addInitScript((id) => {
    window.history.replaceState({ ...(window.history.state || {}), shahabRecommendation: { sessionId: id } }, "", window.location.href);
  }, sessionId);

  const restoredBeforeReload = page.waitForResponse(response => response.url().endsWith(`/questionnaire/sessions/${sessionId}`) && response.request().method() === "GET");
  await page.goto("/question/4");
  expect((await restoredBeforeReload).status()).toBe(200);
  await expect(page).toHaveURL(/\/question\/4$/);
  await expect(page.getByRole("heading").first()).toBeVisible();

  const restoredAfterReload = page.waitForResponse(response => response.url().endsWith(`/questionnaire/sessions/${sessionId}`) && response.request().method() === "GET");
  await page.reload();
  expect((await restoredAfterReload).status()).toBe(200);
  await expect(page).toHaveURL(/\/question\/4$/);
  await page.getByRole("button", { name: "بازگشت به سوال قبل" }).click();
  await expect(page).toHaveURL(/\/question\/3$/);
  await expect(page.getByRole("radio").first()).toBeChecked();
  expect(await page.evaluate(() => [...Object.keys(localStorage), ...Object.keys(sessionStorage)].filter(key => key.startsWith("shahab.")))).toEqual([]);
});

test("historical recommendation comparison works and its route and selection survive refresh", async ({ browser, baseURL }) => {
  const context = await browser.newContext({ baseURL });
  try {
    await login(context, "09000000824");
    const { result, historyId } = await recommendation(context);
    expect(result.rankedRecommendations.length).toBeGreaterThanOrEqual(2);
    const page = await context.newPage();
    let scoringRequests = 0;
    page.on("request", request => {
      if (request.method() === "POST" && new URL(request.url()).pathname === "/api/v1/recommendations") scoringRequests += 1;
    });
    await page.goto(`/recommendation-history/${historyId}`);
    await expect(page.locator(".hp-serving-loan-card").first()).toBeVisible();
    await page.getByRole("button", { name: "مقایسه وام" }).click();
    await expect(page).toHaveURL(new RegExp(`/compare-loans\\?historyId=${historyId}`));
    await expect(page.locator(".hp-loan-compare-card").first()).toBeVisible();
    await page.locator(".hp-loan-compare-check").nth(0).click();
    await page.locator(".hp-loan-compare-check").nth(1).click();
    await page.getByRole("button", { name: /مقایسه کن/ }).click();
    await expect(page).toHaveURL(new RegExp(`/compare-result\\?historyId=${historyId}`));
    await expect(page.locator(".hp-compare-result-card")).toHaveCount(2);
    await page.reload();
    await expect(page).toHaveURL(new RegExp(`/compare-result\\?historyId=${historyId}`));
    await expect(page.locator(".hp-recommendation-result-state")).toHaveCount(0);
    await expect(page.locator(".hp-compare-result-card")).toHaveCount(2);
    expect(await page.evaluate(() => history.state.shahabRecommendation.selectedComparisonPlanIds)).toHaveLength(2);
    expect(scoringRequests).toBe(0);

    await page.getByRole("button", { name: "بازگشت" }).click();
    await expect(page).toHaveURL(new RegExp(`/compare-loans\\?historyId=${historyId}`));
    await expect(page.locator(".hp-recommendation-result-state")).toHaveCount(0);
    await expect(page.locator(".hp-loan-compare-check[aria-pressed=true]")).toHaveCount(2);
    await page.reload();
    await expect(page.locator(".hp-loan-compare-check[aria-pressed=true]")).toHaveCount(2);
    expect(scoringRequests).toBe(0);
  } finally {
    await context.close();
  }
});
