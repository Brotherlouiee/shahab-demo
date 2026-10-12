import { expect, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import questionnaire from "../../data/contracts/questionnaire-configuration.v1.json" with { type: "json" };

// Two complete questionnaire journeys include two existing five-second analysis timers.
test.setTimeout(90000);

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
        actor_reference="CI-reviewed-personal-info-fixture", approval_reason="source-backed login-flow regression")`);
});

test.beforeEach(() => {
  // Test isolation of the 120-second global quota, not a production bypass.
  database(`with engine.begin() as connection:
    connection.execute(text("DELETE FROM account_otp_quota_events"))`);
});

async function completeQuestionnaire(page) {
  await page.goto("/question/3");
  for (let number = 3; number <= 12; number += 1) {
    await expect(page).toHaveURL(new RegExp(`/question/${number}$`));
    await page.getByRole("radio").first().click();
    await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  }
  await expect(page).toHaveURL(/\/personal-info$/);
}

async function fillInfo(page, phone) {
  const inputs = page.locator(".hp-personal-info-form input");
  await expect(inputs.nth(2)).toBeEditable();
  await inputs.nth(0).fill("آزمون");
  await inputs.nth(1).fill("کاربر");
  await inputs.nth(2).fill(phone.slice(2));
  await page.locator(".hp-personal-dropdown-trigger").nth(0).click();
  await page.getByRole("option", { name: "تا ۲۲ میلیون تومان" }).click();
  await page.locator(".hp-personal-dropdown-trigger").nth(1).click();
  await page.getByRole("option", { name: "کارمند (شرکت یا اداره)" }).click();
}

async function verify(page) {
  await expect(page).toHaveURL(/\/verify-code$/);
  for (const [index, digit] of [..."123456"].entries()) await page.locator(".hp-loan-otp-row input").nth(index).fill(digit);
  const result = page.waitForResponse(r => r.url().endsWith("/recommendations") && r.request().method() === "POST");
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  expect((await result).status()).toBe(200);
  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 10000 });
}

async function seedLogin(page, phone) {
  const requested = await page.request.post("/api/v1/account-access/request", { data: { phone } });
  expect(requested.status()).toBe(200);
  const verified = await page.request.post("/api/v1/account-access/verify", { data: { challengeId: (await requested.json()).challengeId, code: "123456" } });
  expect(verified.status()).toBe(200);
  const profile = await page.request.put("/api/v1/profiles", { data: { phone, firstName: "آزمون", lastName: "کاربر", income: "up-to-22", job: "employee", gender: "female", avatar: null } });
  expect(profile.status()).toBe(200);
}

async function formGeometry(page) {
  return page.locator(".hp-personal-info-form").evaluate(form => [...form.querySelectorAll("input, .hp-personal-dropdown-trigger")].map(element => {
    const bounds = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return { width: bounds.width, height: bounds.height, color: style.color, background: style.backgroundColor,
      fontSize: style.fontSize, padding: style.padding, border: style.border, margin: style.margin };
  }));
}

test("first OTP creates the account; a refreshed second questionnaire saves the same profile without OTP and retains the old snapshot", async ({ page }) => {
  const phone = "09011112222";
  const otp = [];
  page.on("request", request => { if (/\/account-access\/(request|verify)$/.test(request.url())) otp.push(request.url()); });
  await completeQuestionnaire(page);
  await fillInfo(page, phone);
  const geometry = await formGeometry(page);
  await page.getByRole("button", { name: "تایید" }).click();
  await verify(page);
  expect(otp).toHaveLength(2);
  const list = await page.request.get("/api/v1/recommendation-history");
  expect(list.status()).toBe(200);
  const historyId = (await list.json()).items[0].historyId;
  const old = await (await page.request.get(`/api/v1/recommendation-history/${historyId}`)).json();
  await completeQuestionnaire(page);
  await page.reload();
  const inputs = page.locator(".hp-personal-info-form input");
  await expect(inputs.nth(0)).toHaveValue("آزمون");
  await expect(inputs.nth(2)).toHaveValue("۰۱۱۱۱۲۲۲۲");
  await expect(inputs.nth(2)).toBeEditable();
  expect(await formGeometry(page)).toEqual(geometry);
  await inputs.nth(0).fill("مریم");
  const recommended = page.waitForResponse(r => r.url().endsWith("/recommendations"));
  await page.getByRole("button", { name: "تایید" }).click();
  expect((await recommended).status()).toBe(200);
  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 10000 });
  expect(otp).toHaveLength(2);
  expect(await (await page.request.get("/api/v1/profiles/me")).json()).toMatchObject({ phone, firstName: "مریم", income: "up-to-22", job: "employee" });
  expect((await (await page.request.get("/api/v1/recommendation-history")).json()).items).toHaveLength(2);
  expect(await (await page.request.get(`/api/v1/recommendation-history/${historyId}`)).json()).toEqual(old);
  const accountCounts = JSON.parse(database(`with engine.connect() as connection:
    row = connection.execute(text("SELECT a.account_id::text, (SELECT count(*) FROM recommendation_history_runs h WHERE h.owner_account_id=a.account_id) AS runs FROM accounts a WHERE a.phone='09011112222' AND a.status='active'")).one()
    print(json.dumps({"accountId": row[0], "runs": row[1]}))`));
  expect(accountCounts.runs).toBe(2);
});

test("session and storage failures preserve the edited draft and retry without OTP", async ({ page }) => {
  await seedLogin(page, "09011113333");
  await completeQuestionnaire(page);
  const firstName = page.locator(".hp-personal-info-form input").nth(0);
  await expect(firstName).toHaveValue("آزمون");
  await firstName.fill("مریم");
  const otp = [];
  page.on("request", request => { if (/\/account-access\/(request|verify)$/.test(request.url())) otp.push(request.url()); });
  let failSession = true;
  let failWrite = true;
  await page.route("**/api/v1/account-access/session", route => failSession ? route.fulfill({ status: 503, json: {} }) : route.continue());
  await page.route("**/api/v1/profiles", route => failWrite ? route.fulfill({ status: 503, json: {} }) : route.continue());
  await page.getByRole("button", { name: "تایید" }).click();
  await expect(page.getByRole("alert")).toContainText("انجام نشد");
  await expect(firstName).toHaveValue("مریم");
  failSession = false;
  await page.getByRole("button", { name: "تایید" }).click();
  await expect(page.getByRole("alert")).toContainText("انجام نشد");
  await expect(page).toHaveURL(/\/personal-info$/);
  await expect(firstName).toHaveValue("مریم");
  expect(await (await page.request.get("/api/v1/profiles/me")).json()).toMatchObject({ firstName: "آزمون" });
  failWrite = false;
  const result = page.waitForResponse(r => r.url().endsWith("/recommendations"));
  await page.getByRole("button", { name: "تایید" }).click();
  expect((await result).status()).toBe(200);
  expect(otp).toHaveLength(0);
  expect(await (await page.request.get("/api/v1/profiles/me")).json()).toMatchObject({ firstName: "مریم", gender: "female" });
});

test("absolute account expiry during the form uses existing OTP and preserves the draft; logout requires login again", async ({ page, context }) => {
  const phone = "09011114444";
  await seedLogin(page, phone);
  await completeQuestionnaire(page);
  await expect(page.locator(".hp-personal-info-form input").first()).toHaveValue("آزمون");
  await page.locator(".hp-personal-info-form input").first().fill("مریم");
  // Insert a validly shaped, already-expired credential; never weaken immutable expiry triggers.
  database(`import hashlib
with engine.begin() as connection:
    connection.execute(text("INSERT INTO account_access_sessions (token_digest, account_id, issued_at, expires_at) SELECT :digest, account_id, now()-interval '2 hours', now()-interval '1 hour' FROM accounts WHERE phone=:phone AND status='active'"), {"digest": hashlib.sha256(b"d-browser-expired-credential").hexdigest(), "phone": "${phone}"})`);
  await context.addCookies([{ name: "shahab_account_access", value: "d-browser-expired-credential", domain: "127.0.0.1", path: "/api/v1", httpOnly: true, sameSite: "Lax" }]);
  const requested = page.waitForResponse(r => r.url().endsWith("/account-access/request"));
  await page.getByRole("button", { name: "تایید" }).click();
  expect((await requested).status()).toBe(200);
  await verify(page);
  expect(await (await page.request.get("/api/v1/profiles/me")).json()).toMatchObject({ phone, firstName: "مریم" });
  expect((await page.request.post("/api/v1/account-access/logout")).status()).toBe(204);
  await page.goto("/personal-info");
  await expect(page.locator(".hp-personal-info-form input").nth(2)).toBeEditable();
  expect((await page.request.get("/api/v1/account-access/session")).status()).toBe(401);
});

test("expired raw answers cannot be replayed into a fresh session or bypassed by OTP", async ({ page }) => {
  await seedLogin(page, "09011115555");
  await completeQuestionnaire(page);
  await expect(page.locator(".hp-personal-info-form input").first()).toHaveValue("آزمون");
  const sid = await page.evaluate(() => history.state.shahabRecommendation.sessionId);
  database(`with engine.begin() as connection:
    connection.execute(text("UPDATE questionnaire_sessions SET created_at=now()-interval '31 minutes', expires_at=now()-interval '1 minute' WHERE questionnaire_session_id=:sid"), {"sid": "${sid}"})`);
  const afterExpiry = [];
  page.on("request", request => { if (request.method() === "POST") afterExpiry.push(request.url()); });
  await page.getByRole("button", { name: "تایید" }).click();
  await expect(page.getByRole("alert")).toContainText("مهلت پرسشنامه تمام شده");
  await expect(page).toHaveURL(/\/personal-info$/);
  expect(afterExpiry).toEqual([]);
  expect((await page.request.get(`/api/v1/questionnaire/sessions/${sid}`)).status()).toBe(410);
  expect(questionnaire.questions).toHaveLength(10);
});

test("changing the prefilled phone requires its OTP and creates an independent account without transferring the old profile or history", async ({ page }) => {
  const firstPhone = "09011116666";
  const nextPhone = "09011117777";
  const requested = await page.request.post("/api/v1/account-access/request", { data: { phone: firstPhone } });
  expect(requested.status()).toBe(200);
  const verified = await page.request.post("/api/v1/account-access/verify", { data: { challengeId: (await requested.json()).challengeId, code: "123456" } });
  expect(verified.status()).toBe(200);
  const firstToken = (await verified.json()).accessToken;
  const original = { phone: firstPhone, firstName: "مریم", lastName: "کاربر", income: "up-to-22", job: "employee", gender: "female", avatar: null };
  expect((await page.request.put("/api/v1/profiles", { data: original })).status()).toBe(200);
  async function fillQuestionnaire() {
    await completeQuestionnaire(page);
    await expect(page.locator(".hp-personal-info-form input").first()).toHaveValue("مریم");
  }
  await fillQuestionnaire();
  const firstResult = page.waitForResponse(r => r.url().endsWith("/recommendations"));
  await page.getByRole("button", { name: "تایید" }).click();
  expect((await firstResult).status()).toBe(200);
  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 10000 });
  const historyBefore = await (await page.request.get("/api/v1/recommendation-history")).json();
  expect(historyBefore.items).toHaveLength(1);
  const originalHistoryId = historyBefore.items[0].historyId;
  const originalSnapshot = await (await page.request.get(`/api/v1/recommendation-history/${originalHistoryId}`)).json();
  // A fresh questionnaire remains unbound until its first successful result.
  await fillQuestionnaire();
  await expect(page).toHaveURL(/\/personal-info$/);
  const inputs = page.locator(".hp-personal-info-form input");
  await expect(inputs.first()).toHaveValue("مریم");
  await expect(inputs.nth(2)).toHaveValue("۰۱۱۱۱۶۶۶۶");
  await expect(inputs.nth(2)).toBeEditable();
  await inputs.nth(2).fill(nextPhone.slice(2));
  await inputs.first().fill("آزمون");
  const challengeResponse = page.waitForResponse(r => r.url().endsWith("/account-access/request"));
  await page.getByRole("button", { name: "تایید" }).click();
  const challenge = await challengeResponse;
  expect(challenge.status()).toBe(200);
  expect(challenge.request().postDataJSON()).toEqual({ phone: nextPhone });
  await expect(page).toHaveURL(/\/verify-code$/);
  // The old account remains unchanged before verification of the new number.
  expect(await (await page.request.get("/api/v1/profiles/me")).json()).toMatchObject(original);
  await page.getByRole("button", { name: "تغییر شماره تلفن" }).click();
  await expect(inputs.nth(2)).toHaveValue(nextPhone.slice(2).replace(/[0-9]/g, digit => "۰۱۲۳۴۵۶۷۸۹"[Number(digit)]));
  await expect(inputs.first()).toHaveValue("آزمون");
  await page.getByRole("button", { name: "تایید" }).click();
  await expect(page).toHaveURL(/\/verify-code$/);
  for (const [index, digit] of [..."123450"].entries()) await page.locator(".hp-loan-otp-row input").nth(index).fill(digit);
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  await expect(page.locator(".hp-loan-otp-error")).toContainText("اشتباه");
  await expect(page).toHaveURL(/\/verify-code$/);
  expect(await (await page.request.get("/api/v1/profiles/me")).json()).toMatchObject(original);
  for (const [index, digit] of [..."123456"].entries()) await page.locator(".hp-loan-otp-row input").nth(index).fill(digit);
  const result = page.waitForResponse(r => r.url().endsWith("/recommendations"));
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  expect((await result).status()).toBe(200);
  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 10000 });
  expect(await (await page.request.get("/api/v1/profiles/me")).json()).toMatchObject({ phone: nextPhone, firstName: "آزمون", gender: "" });
  expect((await (await page.request.get("/api/v1/recommendation-history")).json()).items).toHaveLength(1);
  const oldHeaders = { Authorization: `Bearer ${firstToken}` };
  expect(await (await page.request.get("/api/v1/profiles/me", { headers: oldHeaders })).json()).toMatchObject(original);
  expect(await (await page.request.get("/api/v1/recommendation-history", { headers: oldHeaders })).json()).toEqual(historyBefore);
  expect(await (await page.request.get(`/api/v1/recommendation-history/${originalHistoryId}`, { headers: oldHeaders })).json()).toEqual(originalSnapshot);
  expect((await page.request.get(`/api/v1/recommendation-history/${originalHistoryId}`)).status()).toBe(404);
});
