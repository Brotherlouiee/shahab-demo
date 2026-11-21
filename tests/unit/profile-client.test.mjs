import { test } from "node:test";
import assert from "node:assert/strict";
import { clearAccountAccess, displayProfilePhone, hasProfileAccess, normalizeProfilePhone, persistPersonalInfo, persistProfile, readPersonalInfoProfile, requestProfileCode, restoreAccountAccess, verifyProfileCode } from "../../src/features/account/profileClient.mjs";

test("complete phone identities are not truncated", () => {
  for (const value of ["09000000001", "۰۹۰۰۰۰۰۰۰۰۱", "٠٩٠٠٠٠٠٠٠٠١", "000000001"]) {
    assert.equal(normalizeProfilePhone(value), "09000000001");
    assert.equal(displayProfilePhone(value), "۰۹۰۰۰۰۰۰۰۰۱");
  }
  assert.throws(() => normalizeProfilePhone("0900000000"));
});

test("verification authorizes persistence; storage failure stays an error and preserves retry", async () => {
  clearAccountAccess();
  const requests = [];
  let failWrite = true;
  const original = globalThis.fetch;
  globalThis.fetch = async (url, options) => {
    requests.push({ url, options });
    if (url.endsWith("/request")) return Response.json({ challengeId: "test-challenge" });
    if (url.endsWith("/verify")) return Response.json({ accessToken: "fixture", phone: "09000000001", expiresIn: 1800 });
    if (url.endsWith("/me")) return Response.json({ gender: "female", avatar: null });
    if (failWrite) return Response.json({}, { status: 503 });
    return Response.json(JSON.parse(options.body));
  };
  try {
    await assert.rejects(persistProfile({ phone: "09000000001" }), { status: 401 });
    assert.equal(requests.length, 1);
    assert.ok(requests[0].url.endsWith("/account-access/session"));
    await requestProfileCode("۰۹۰۰۰۰۰۰۰۰۱");
    await verifyProfileCode("test-challenge", "۱۲۳۴۵۶");
    await assert.rejects(persistPersonalInfo({ phone: "000000001", job: "manager" }), { status: 503 });
    assert.equal(hasProfileAccess("000000001"), true);
    failWrite = false;
    const stored = await persistPersonalInfo({ phone: "000000001", job: "manager" });
    assert.equal(stored.phone, "09000000001");
    assert.equal(stored.gender, "female");
    const write = requests.at(-1);
    assert.equal(write.options.headers.Authorization, "Bearer fixture");
    assert.equal(requests.filter((r) => r.url.endsWith("/verify")).length, 1);
    assert.ok(requests.every((r) => !r.url.includes("09000000001")));
  } finally { globalThis.fetch = original; clearAccountAccess(); }
});

test("a valid HttpOnly access cookie restores authorization without browser token storage", async () => {
  clearAccountAccess();
  const original = globalThis.fetch;
  globalThis.fetch = async (url) => {
    assert.ok(url.endsWith("/account-access/session"));
    return Response.json({ phone: "09000000001", expiresIn: 1800 });
  };
  try {
    assert.equal(await restoreAccountAccess(), "09000000001");
    assert.equal(hasProfileAccess("09000000001"), true);
  } finally { globalThis.fetch = original; clearAccountAccess(); }
});

test("an earlier anonymous session probe cannot erase a later OTP verification", async () => {
  clearAccountAccess();
  const original = globalThis.fetch;
  let resolveProbe;
  globalThis.fetch = (url) => {
    if (url.endsWith("/account-access/session")) return new Promise((resolve) => { resolveProbe = resolve; });
    if (url.endsWith("/verify")) return Promise.resolve(Response.json({ accessToken: "fixture", phone: "09000000001", expiresIn: 1800 }));
    return Promise.resolve(Response.json({}));
  };
  try {
    const probe = restoreAccountAccess();
    await verifyProfileCode("fixture", "123456");
    resolveProbe(new Response(null, { status: 401 }));
    await probe;
    assert.equal(hasProfileAccess("09000000001"), true);
  } finally { globalThis.fetch = original; clearAccountAccess(); }
});

test("personal-info restores the server actor and persists with its cookie without OTP", async () => {
  clearAccountAccess();
  const original = globalThis.fetch;
  const paths = [];
  globalThis.fetch = async (url, options) => {
    paths.push(url);
    if (url.endsWith("/session")) return Response.json({ phone: "09000000001", expiresIn: 17 });
    assert.equal(options.headers.Authorization, undefined);
    assert.equal(options.credentials, "same-origin");
    if (url.endsWith("/me")) return Response.json({ phone: "09000000001", firstName: "آزمون", gender: "female" });
    return Response.json(JSON.parse(options.body));
  };
  try {
    const profile = await readPersonalInfoProfile();
    const stored = await persistPersonalInfo({ ...profile, job: "manager" });
    assert.equal(stored.gender, "female");
    assert.ok(paths.every(path => !/\/(request|verify)$/.test(path)));
  } finally { globalThis.fetch = original; clearAccountAccess(); }
});

test("personal-info treats only 401 as guest; infrastructure errors never imply login", async () => {
  clearAccountAccess();
  const original = globalThis.fetch;
  try {
    for (const status of [403, 429, 503]) {
      globalThis.fetch = async () => new Response(null, { status });
      await assert.rejects(readPersonalInfoProfile(), { status });
    }
    globalThis.fetch = async () => { throw new TypeError("offline"); };
    await assert.rejects(readPersonalInfoProfile(), { status: 0 });
    globalThis.fetch = async () => new Response(null, { status: 401 });
    assert.equal(await readPersonalInfoProfile(), null);
  } finally { globalThis.fetch = original; clearAccountAccess(); }
});

test("a successful cookie probe started before logout cannot resurrect the old actor", async () => {
  clearAccountAccess();
  const original = globalThis.fetch;
  let resolveProbe;
  globalThis.fetch = () => new Promise(resolve => { resolveProbe = resolve; });
  try {
    const probe = restoreAccountAccess({ strict: true });
    clearAccountAccess();
    resolveProbe(Response.json({ phone: "09000000001", expiresIn: 3600 }));
    assert.equal(await probe, null);
    assert.equal(hasProfileAccess("09000000001"), false);
  } finally { globalThis.fetch = original; clearAccountAccess(); }
});


test("configured API base is used by OTP, profile and logout requests", async () => {
  const { createServer } = await import("vite");
  const originalBase = process.env.VITE_SHAHAB_API_BASE_URL;
  const originalFetch = globalThis.fetch;
  process.env.VITE_SHAHAB_API_BASE_URL = "https://api.example.test/api/v1/";
  const server = await createServer({ configFile: false, server: { middlewareMode: true }, appType: "custom" });
  const urls = [];
  globalThis.fetch = async (url) => {
    urls.push(url);
    if (url.endsWith("/verify")) return Response.json({ accessToken: "fixture", phone: "09000000001", expiresIn: 1800 });
    if (url.endsWith("/logout")) return new Response(null, { status: 204 });
    return Response.json({ challengeId: "fixture", phone: "09000000001" });
  };
  try {
    const client = await server.ssrLoadModule("/src/features/account/profileClient.mjs");
    await client.requestProfileCode("09000000001");
    await client.verifyProfileCode("fixture", "123456");
    await client.readOwnProfile();
    await client.persistProfile({ phone: "09000000001" });
    await client.logoutProfile();
    assert.deepEqual(urls, ["account-access/request", "account-access/verify", "profiles/me", "profiles", "account-access/logout"].map(path => `https://api.example.test/api/v1/${path}`));
  } finally {
    globalThis.fetch = originalFetch;
    if (originalBase === undefined) delete process.env.VITE_SHAHAB_API_BASE_URL;
    else process.env.VITE_SHAHAB_API_BASE_URL = originalBase;
    await server.close();
  }
});
