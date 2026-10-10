// Profile authorization lives only in this tab's active module instance.
// Browser caches are presentation data and never authorize server requests.
let accessToken = "";
let actorPhone = "";
let expiresAt = 0;
let accessGeneration = 0;
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
  let response;
  try {
    response = await fetch(`${apiBaseUrl}/${path}`, {
      method, cache: "no-store",
      credentials: "same-origin",
      headers: { ...(body ? { "Content-Type": "application/json" } : {}), ...(authorize ? { Authorization: `Bearer ${accessToken}` } : {}) },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
  } catch { throw new ProfileApiError(0); }
  if (!response.ok) {
    if (authorize && response.status === 401) clearAccountAccess();
    throw new ProfileApiError(response.status);
  }
  return response.status === 204 ? null : response.json();
}

export function authorizedRequest(path, options) { return request(path, { ...options, authorize: true }); }

export function authenticatedHeaders() {
  return accessToken && Date.now() < expiresAt ? { Authorization: `Bearer ${accessToken}` } : {};
}

export function optionalAuthenticatedHeaders() {
  return accessToken && Date.now() < expiresAt ? { Authorization: `Bearer ${accessToken}` } : {};
}

export function requestProfileCode(phone) {
  return request("account-access/request", { method: "POST", body: { phone: normalizeProfilePhone(phone) } });
}

export async function verifyProfileCode(challengeId, code) {
  let verified;
  try { verified = await request("account-access/verify", { method: "POST", body: { challengeId, code } }); }
  catch (error) { if (error.status === 401) error.message = "کد وارد شده اشتباه است"; throw error; }
  accessToken = verified.accessToken;
  actorPhone = normalizeProfilePhone(verified.phone);
  expiresAt = Date.now() + verified.expiresIn * 1000;
  accessGeneration += 1;
}

export async function restoreAccountAccess() {
  const generationAtStart = accessGeneration;
  try {
    const response = await fetch(`${apiBaseUrl}/account-access/session`, { cache: "no-store", credentials: "same-origin" });
    if (!response.ok) {
      // An anonymous bootstrap response must never erase a later successful
      // OTP verification that completed while this request was in flight.
      if (generationAtStart === accessGeneration) clearAccountAccess();
      return null;
    }
    const value = await response.json();
    actorPhone = normalizeProfilePhone(value.phone);
    expiresAt = Date.now() + value.expiresIn * 1000;
    accessGeneration += 1;
    return actorPhone;
  } catch { return null; }
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

export function clearAccountAccess() { accessToken = ""; actorPhone = ""; expiresAt = 0; accessGeneration += 1; }

export async function logoutProfile() {
  // Clear the local capability even if the network is unavailable; server TTL still bounds it.
  const token = accessToken;
  clearAccountAccess();
  await fetch(`${apiBaseUrl}/account-access/logout`, { method: "POST", credentials: "same-origin", headers: token ? { Authorization: `Bearer ${token}` } : {} });
}
