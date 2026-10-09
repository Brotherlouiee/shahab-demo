// Profile authorization lives only in this tab's active module instance.
// Browser caches are presentation data and never authorize server requests.
let accessToken = "";
let actorPhone = "";
let expiresAt = 0;

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
  if (authorize && (!accessToken || Date.now() >= expiresAt)) throw new ProfileApiError(401);
  let response;
  try {
    response = await fetch(`/api/v1/${path}`, {
      method, cache: "no-store",
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
}

export function hasProfileAccess(phone) {
  return Boolean(accessToken && Date.now() < expiresAt && actorPhone === normalizeProfilePhone(phone));
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

export function clearAccountAccess() { accessToken = ""; actorPhone = ""; expiresAt = 0; }

export async function logoutProfile() {
  // Clear the local capability even if the network is unavailable; server TTL still bounds it.
  const token = accessToken;
  clearAccountAccess();
  if (token) await fetch("/api/v1/account-access/logout", { method: "POST", headers: { Authorization: `Bearer ${token}` } });
}
