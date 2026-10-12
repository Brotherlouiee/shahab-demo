import { clearAccountBrowserData, isLogoutPending, markLogoutPending, resetAccountPresentation } from "./accountBrowserState.mjs";
// Profile authorization lives only in this tab's active module instance.
// Browser caches are presentation data and never authorize server requests.
let accessToken = "";
let actorPhone = "";
let expiresAt = 0;
let accessGeneration = 0;
let accountId = "";
let accountEpoch = 0;
let logoutInFlight = null;
export function accountAccessEpoch() { return accountEpoch; }
function announceAccountChange() {
  accountEpoch += 1;
  resetAccountPresentation();
  if (typeof window !== "undefined") window.dispatchEvent(new Event("shahab:account-changed"));
}
const apiBaseUrl = (import.meta.env?.VITE_SHAHAB_API_BASE_URL || "/api/v1").replace(/\/+$/, "");

export class ProfileApiError extends Error {
  constructor(status) {
    super(status === 401 ? "برای ذخیره اطلاعات، دوباره کد تأیید را دریافت کنید." : status === 429 ? "تعداد تلاش‌ها زیاد است. کمی بعد دوباره تلاش کنید." : "ثبت یا دریافت اطلاعات انجام نشد. دوباره تلاش کنید.");
    this.status = status;
  }
}

export function normalizeProfilePhone(value) {
  const digits = String(value || "").replace(/[۰-۹٠-٩]/g, (digit) => {
    const index = "۰۱۲۳۴۵۶۷۸۹".indexOf(digit);
    return String(index >= 0 ? index : "٠١٢٣٤٥٦٧٨٩".indexOf(digit));
  });
  const full = digits.length === 9 ? `09${digits}` : digits;
  if (!/^09[0-9]{9}$/.test(full)) throw new ProfileApiError(422);
  return full;
}

export function displayProfilePhone(value) {
  if (!value) return "";
  try { return normalizeProfilePhone(value).replace(/[0-9]/g, (digit) => "۰۱۲۳۴۵۶۷۸۹"[Number(digit)]); }
  catch { return ""; }
}

async function request(path, { body, method = "GET", authorize = false } = {}) {
  if (authorize && !(await ensureAccountAccess())) throw new ProfileApiError(401);
  const epochAtStart = accountEpoch;
  let response;
  try {
    response = await fetch(`${apiBaseUrl}/${path}`, {
      method, cache: "no-store",
      credentials: "same-origin",
      headers: { ...(body ? { "Content-Type": "application/json" } : {}), ...(authorize && accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
  } catch { throw new ProfileApiError(0); }
  if (authorize && epochAtStart !== accountEpoch) throw new ProfileApiError(401);
  if (!response.ok) {
    if (authorize && response.status === 401) clearAccountAccess();
    throw new ProfileApiError(response.status);
  }
  const value = response.status === 204 ? null : await response.json();
  if (authorize && epochAtStart !== accountEpoch) throw new ProfileApiError(401);
  return value;
}

export function authorizedRequest(path, options) { return request(path, { ...options, authorize: true }); }

export function authenticatedHeaders() {
  return accessToken && Date.now() < expiresAt ? { Authorization: `Bearer ${accessToken}` } : {};
}

export function optionalAuthenticatedHeaders() {
  return accessToken && Date.now() < expiresAt ? { Authorization: `Bearer ${accessToken}` } : {};
}

export async function requestProfileCode(phone) {
  if (isLogoutPending()) await finishPendingLogout();
  return request("account-access/request", { method: "POST", body: { phone: normalizeProfilePhone(phone) } });
}

export async function verifyProfileCode(challengeId, code) {
  if (isLogoutPending()) await finishPendingLogout();
  const epochAtStart = accountEpoch;
  let verified;
  try { verified = await request("account-access/verify", { method: "POST", body: { challengeId, code } }); }
  catch (error) { if (error.status === 401) error.message = "کد وارد شده اشتباه است"; throw error; }
  if (epochAtStart !== accountEpoch) {
    markLogoutPending(true);
    await finishPendingLogout();
    throw new ProfileApiError(401);
  }
  announceAccountChange();
  accountId = verified.accountId || verified.phone;
  accessToken = verified.accessToken;
  actorPhone = normalizeProfilePhone(verified.phone);
  expiresAt = Date.now() + verified.expiresIn * 1000;
  accessGeneration += 1;
}

export async function restoreAccountAccess({ strict = false } = {}) {
  if (isLogoutPending()) {
    try { await finishPendingLogout(); } catch (error) { if (strict) throw error; }
    return null;
  }
  const generationAtStart = accessGeneration;
  try {
    const response = await fetch(`${apiBaseUrl}/account-access/session`, { cache: "no-store", credentials: "same-origin" });
    if (!response.ok) {
      // An anonymous bootstrap response must never erase a later successful
      // OTP verification that completed while this request was in flight.
      if (response.status === 401) {
        if (generationAtStart === accessGeneration) clearAccountAccess();
        return Date.now() < expiresAt ? actorPhone : null;
      }
      if (strict) throw new ProfileApiError(response.status);
      return null;
    }
    const value = await response.json();
    // A probe started before logout or a newer login cannot resurrect its actor.
    if (generationAtStart !== accessGeneration) return Date.now() < expiresAt ? actorPhone : null;
    const restoredId = value.accountId || value.phone;
    if (accountId !== restoredId) announceAccountChange();
    accountId = restoredId;
    accessToken = "";
    actorPhone = normalizeProfilePhone(value.phone);
    expiresAt = Date.now() + value.expiresIn * 1000;
    accessGeneration += 1;
    return actorPhone;
  } catch (error) {
    if (strict) throw error instanceof ProfileApiError ? error : new ProfileApiError(0);
    return null;
  }
}

export async function readPersonalInfoProfile() {
  if (!(await restoreAccountAccess({ strict: true }))) return null;
  try {
    const profile = await readOwnProfile();
    if (!profile) throw new ProfileApiError(503);
    if (!hasProfileAccess(profile.phone)) return null;
    return profile;
  } catch (error) {
    if (error instanceof ProfileApiError && error.status === 401) return null;
    throw error;
  }
}

async function ensureAccountAccess() {
  if (Date.now() < expiresAt && actorPhone) return true;
  return Boolean(await restoreAccountAccess());
}

export function hasProfileAccess(phone) {
  return Boolean(Date.now() < expiresAt && actorPhone === normalizeProfilePhone(phone));
}

export async function readOwnProfile() {
  try { return await request("profiles/me", { authorize: true }); }
  catch (error) { if (error instanceof ProfileApiError && error.status === 404) return null; throw error; }
}

export function persistProfile(profile) {
  return request("profiles", { method: "PUT", authorize: true, body: {
    phone: normalizeProfilePhone(profile.phone), firstName: profile.firstName || "", lastName: profile.lastName || "",
    income: profile.income || "", job: profile.job || "", gender: profile.gender || "", avatar: profile.avatar || null,
  } });
}

export async function persistPersonalInfo(profile) {
  const previous = await readOwnProfile();
  return persistProfile({ ...previous, ...profile });
}

export function clearAccountAccess() {
  const hadAccess = Boolean(actorPhone);
  accessToken = ""; actorPhone = ""; accountId = ""; expiresAt = 0; accessGeneration += 1;
  if (hadAccess) { announceAccountChange(); clearAccountBrowserData(); }
  else resetAccountPresentation();
}

async function finishPendingLogout(token = "") {
  if (logoutInFlight) return logoutInFlight;
  const operation = (async () => {
    let response;
    try { response = await fetch(`${apiBaseUrl}/account-access/logout`, {
      method: "POST", credentials: "same-origin", cache: "no-store",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }); } catch { throw new ProfileApiError(0); }
    if (!response.ok && response.status !== 401) throw new ProfileApiError(response.status);
    markLogoutPending(false);
    if (typeof window !== "undefined") window.dispatchEvent(new Event("shahab:logout-completed"));
  })();
  logoutInFlight = operation;
  try { await operation; } finally { if (logoutInFlight === operation) logoutInFlight = null; }
}

export async function logoutProfile() {
  const token = accessToken;
  clearAccountAccess();
  clearAccountBrowserData();
  markLogoutPending(true);
  if (typeof window !== "undefined") window.dispatchEvent(new Event("shahab:logout-intent"));
  await finishPendingLogout(token);
}

if (typeof window !== "undefined") {
  // Cleanup from another tab invalidates capabilities as well as presentation.
  window.addEventListener("shahab:account-cleared", () => {
    accessToken = ""; actorPhone = ""; accountId = ""; expiresAt = 0; accessGeneration += 1;
    announceAccountChange();
  });
}
