import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";

class Storage {
  values = new Map();
  get length() { return this.values.size; }
  key(index) { return [...this.values.keys()][index] ?? null; }
  getItem(key) { return this.values.get(key) ?? null; }
  setItem(key, value) { this.values.set(key, value); }
  removeItem(key) { this.values.delete(key); }
}
const browser = new EventTarget();
browser.localStorage = new Storage(); browser.sessionStorage = new Storage();
browser.location = { pathname: "/", search: "" };
browser.history = { state: null, replaceState(value) { this.state = value; } };
globalThis.window = browser;
const profile = await import("../../src/features/account/profileClient.mjs");
const state = await import("../../src/features/account/accountBrowserState.mjs");
const saved = await import("../../src/features/account/savedLoans.mjs");
const loan = { loanId: "fixture-loan", loanName: "fixture", lenderName: "fixture", compatibilityScore: .85 };
const response = (value, status = 200) => Response.json(value, { status });

beforeEach(() => {
  state.markLogoutPending(false); profile.clearAccountAccess(); saved.clearSavedLoansCache();
  browser.localStorage.values.clear(); browser.sessionStorage.values.clear(); browser.history.state = null;
});

test("legacy browser bookmarks are neither display authority nor an upload source", async () => {
  browser.localStorage.setItem("shahab.savedLoans", JSON.stringify([loan]));
  const requests = [];
  globalThis.fetch = async (url, options) => {
    requests.push([url, options?.method]);
    return url.includes("/session") ? response({ phone: "09000000001", accountId: "account-A", expiresIn: 3600 }) : response({ items: [], nextCursor: null });
  };
  assert.deepEqual(saved.readSavedLoans(), []);
  assert.deepEqual(await saved.refreshSavedLoans(), []);
  assert.equal(browser.localStorage.getItem("shahab.savedLoans"), JSON.stringify([loan]));
  assert.ok(requests.every(([, method]) => method === undefined || method === "GET"));
});

test("save waits for committed desired state; errors show no optimistic saved value", async () => {
  let fail = true;
  const mutations = [];
  globalThis.fetch = async (url, options) => {
    if (url.includes("/session")) return response({ phone: "09000000001", accountId: "account-A", expiresIn: 3600 });
    if (url.includes("bookmarks?")) return response({ items: [], nextCursor: null });
    mutations.push(options);
    return fail ? response({}, 503) : new Response(null, { status: 204 });
  };
  await saved.refreshSavedLoans();
  await assert.rejects(saved.toggleSavedLoan(loan), { status: 503 });
  assert.deepEqual(saved.readSavedLoans(), []);
  fail = false;
  assert.equal(await saved.toggleSavedLoan(loan), true);
  assert.deepEqual(JSON.parse(mutations.at(-1).body), {});
  assert.equal(mutations.at(-1).method, "PUT");
  assert.equal(await saved.toggleSavedLoan(loan), false);
  assert.equal(mutations.at(-1).method, "DELETE");
});

test("duplicate click has one mutation; late result cannot repopulate a logged-out account", async () => {
  let resolveSave;
  globalThis.fetch = async url => {
    if (url.includes("/session")) return response({ phone: "09000000001", accountId: "account-A", expiresIn: 3600 });
    if (url.includes("bookmarks?")) return response({ items: [], nextCursor: null });
    return new Promise(resolve => { resolveSave = resolve; });
  };
  await saved.refreshSavedLoans();
  const operation = saved.toggleSavedLoan(loan);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(await saved.toggleSavedLoan(loan), null);
  profile.clearAccountAccess();
  resolveSave(new Response(null, { status: 204 }));
  await assert.rejects(operation, { status: 401 });
  assert.deepEqual(saved.readSavedLoans(), []);
});

test("pagination loads all confirmed pages and detects a non-progressing cursor", async () => {
  const paths = [];
  let repeat = false;
  globalThis.fetch = async url => {
    if (url.includes("/session")) return response({ phone: "09000000001", accountId: "account-A", expiresIn: 3600 });
    paths.push(url);
    return url.includes("cursor=") ? response({ items: [{ ...loan, loanId: "second" }], nextCursor: repeat ? "next" : null }) : response({ items: [loan], nextCursor: "next" });
  };
  assert.equal((await saved.refreshSavedLoans()).length, 2);
  assert.equal(paths.length, 2);
  repeat = true;
  await assert.rejects(saved.refreshSavedLoans(), /cursor/);
});

test("logout clears only Shahab storage, presentation and navigation while DB reads remain independent", async () => {
  browser.localStorage.setItem("another-app", "keep"); browser.sessionStorage.setItem("another-app", "keep");
  browser.localStorage.setItem("shahab.accountProfile", "private");
  browser.sessionStorage.setItem("shahab.form", "private");
  browser.history.state = { otherApp: "keep", shahabRecommendation: { result: "private" } };
  state.writeAccountProfileCache({ firstName: "private" }); state.writePersonalInfoCache("phone", "private");
  globalThis.fetch = async () => new Response(null, { status: 204 });
  await profile.logoutProfile();
  assert.equal(browser.localStorage.getItem("another-app"), "keep");
  assert.equal(browser.sessionStorage.getItem("another-app"), "keep");
  assert.equal(browser.localStorage.getItem("shahab.accountProfile"), null);
  assert.equal(browser.sessionStorage.getItem("shahab.form"), null);
  assert.deepEqual(browser.history.state, { otherApp: "keep" });
  assert.equal(state.readAccountProfileCache(), null);
  assert.equal(state.readPersonalInfoCache("phone"), "");
  assert.equal(state.isLogoutPending(), false);
});

test("failed logout survives refresh as a non-personal pending flag, never a restored session", async () => {
  const paths = [];
  globalThis.fetch = async url => { paths.push(url); throw new Error("network fixture"); };
  await assert.rejects(profile.logoutProfile(), { status: 0 });
  assert.equal(browser.sessionStorage.getItem("shahab.logoutPending"), "1");
  assert.equal(await profile.restoreAccountAccess(), null);
  assert.ok(paths.every(url => url.endsWith("/logout")));
  globalThis.fetch = async url => { assert.ok(url.endsWith("/logout")); return new Response(null, { status: 204 }); };
  assert.equal(await profile.restoreAccountAccess(), null);
  assert.equal(browser.sessionStorage.getItem("shahab.logoutPending"), null);
});

test("same phone in a new server account generation never inherits an old bookmark cache", async () => {
  let id = "generation-A";
  globalThis.fetch = async url => url.includes("/session") ? response({ phone: "09000000001", accountId: id, expiresIn: 3600 }) : response({ items: id === "generation-A" ? [loan] : [], nextCursor: null });
  assert.equal((await saved.refreshSavedLoans()).length, 1);
  id = "generation-B";
  assert.equal((await saved.refreshSavedLoans()).length, 0);
  assert.deepEqual(saved.readSavedLoans(), []);
});
