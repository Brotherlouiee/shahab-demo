// Presentation caches live only in memory. Legacy storage is never identity or
// bookmark authority; it remains quarantined until an explicit logout clears it.
let profile = null;
let fields = {};
const recommendations = new Map();
const allowedFields = new Set(["firstName", "lastName", "phone", "income", "job"]);

export function readAccountProfileCache() { return profile; }
export function writeAccountProfileCache(value) { profile = value; }
export function readPersonalInfoCache(field) { return fields[field] || ""; }
export function writePersonalInfoCache(field, value) {
  if (allowedFields.has(field)) fields[field] = value || "";
}
export function readRecommendationCache(sessionId) { return recommendations.get(sessionId) || null; }
export function writeRecommendationCache(sessionId, result) { if (result) recommendations.set(sessionId, result); }
export function resetAccountPresentation() { profile = null; fields = {}; recommendations.clear(); }

export function clearAccountBrowserData({ notify = true } = {}) {
  resetAccountPresentation();
  if (typeof window === "undefined") return;
  for (const name of ["localStorage", "sessionStorage"]) {
    try {
      const storage = window[name];
      const ownKeys = [];
      for (let index = 0; index < storage.length; index += 1) {
        const key = storage.key(index);
        if (key?.startsWith("shahab.")) ownKeys.push(key);
      }
      for (const key of ownKeys) storage.removeItem(key);
    } catch { /* Restricted storage must not block in-memory cleanup. */ }
  }
  if (window.history?.state?.shahabRecommendation) {
    const { shahabRecommendation: _removed, ...state } = window.history.state;
    window.history.replaceState(state, "", window.location.pathname + window.location.search);
  }
  if (notify) window.dispatchEvent(new Event("shahab:account-cleared"));
}

// Only a non-personal control flag persists during a failed logout. It prevents
// refreshing from silently restoring a still-live HttpOnly cookie while offline.
const pendingKey = "shahab.logoutPending";
let pendingLogout = false;
export function markLogoutPending(value) {
  pendingLogout = value;
  if (typeof window === "undefined") return;
  try {
    if (value) window.sessionStorage.setItem(pendingKey, "1");
    else window.sessionStorage.removeItem(pendingKey);
  } catch { /* The active tab still fails closed if storage is blocked. */ }
}
export function isLogoutPending() {
  if (typeof window !== "undefined") {
    try { pendingLogout ||= window.sessionStorage.getItem(pendingKey) === "1"; } catch { /* memory fallback */ }
  }
  return pendingLogout;
}

export function synchronizeAccountTabs() {
  if (typeof window === "undefined" || typeof BroadcastChannel === "undefined") return () => {};
  const channel = new BroadcastChannel("shahab-account-lifecycle");
  const receive = ({ data }) => {
    if (data?.type === "logout") { clearAccountBrowserData(); markLogoutPending(true); }
    if (data?.type === "logout-completed") markLogoutPending(false);
  };
  const send = () => channel.postMessage({ type: "logout" });
  channel.addEventListener("message", receive);
  const complete = () => channel.postMessage({ type: "logout-completed" });
  window.addEventListener("shahab:logout-intent", send);
  window.addEventListener("shahab:logout-completed", complete);
  return () => { window.removeEventListener("shahab:logout-intent", send); window.removeEventListener("shahab:logout-completed", complete); channel.close(); };
}
