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
test.beforeEach(() => database(`with engine.begin() as c:
    c.execute(text("DELETE FROM account_otp_quota_events"))`));

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
  return { loan: result.rankedRecommendations[0], historyId: (await history.json()).items[0].historyId };
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
    await expect(card).toBeVisible();
    const save = card.locator(".hp-loan-save-button");
    const committed = page.waitForResponse(response => response.url().includes(`/bookmarks/${loan.loanId}`) && response.request().method() === "PUT");
    await save.click(); expect((await committed).status()).toBe(204);
    await expect(save).toHaveAttribute("aria-pressed", "true");
    await expect(page.locator(".hp-loan-save-toast")).toBeVisible();
    const firstList = await (await a.request.get("/api/v1/bookmarks")).json();
    expect((await (await second.request.get("/api/v1/bookmarks")).json()).items).toEqual(firstList.items);
    expect((await (await b.request.get("/api/v1/bookmarks")).json()).items).toEqual([]);
    const other = await second.newPage();
    await other.goto("/saved-loans");
    await expect(other.locator(".hp-serving-loan-card")).toHaveCount(1);
    await other.reload(); await expect(other.locator(".hp-serving-loan-card")).toHaveCount(1);
    await other.locator(".hp-loan-docs-link").click();
    await expect(other).toHaveURL(/from=saved-loans/);
    await other.getByRole("button", { name: "بازگشت" }).click();
    await expect(other).toHaveURL(/\/saved-loans$/);

    await page.evaluate(() => {
      localStorage.setItem("another-app", "preserve"); sessionStorage.setItem("another-app", "preserve");
      localStorage.setItem("shahab.savedLoans", "legacy fixture");
      localStorage.setItem("shahab.personalInfo.phone", "synthetic fixture");
      sessionStorage.setItem("shahab.testDraft", "synthetic fixture");
    });
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
  } finally { await a.close(); await second.close(); await b.close(); }
});
