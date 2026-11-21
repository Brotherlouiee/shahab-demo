import { accountAccessEpoch, authorizedRequest, restoreAccountAccess } from "./profileClient.mjs";

// Server-confirmed tab presentation only; legacy JSON has no account provenance.
let items = [];
let loading = null;
let revision = 0;
const pendingLoans = new Set();
function announce() {
  if (typeof window !== "undefined") window.dispatchEvent(new Event("shahab:saved-loans"));
}
export function readSavedLoans() { return items; }
export function clearSavedLoansCache() { items = []; loading = null; revision += 1; pendingLoans.clear(); announce(); }

export async function refreshSavedLoans() {
  if (loading) return loading;
  const operation = (async () => {
    if (!(await restoreAccountAccess({ strict: true }))) { items = []; announce(); return []; }
    const epoch = accountAccessEpoch();
    const currentRevision = revision;
    const next = [];
    const cursors = new Set();
    let cursor = null;
    do {
      const page = await authorizedRequest(`bookmarks?limit=50${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`);
      if (!Array.isArray(page?.items) || !page.items.every(item => typeof item.loanId === "string" && typeof item.loanName === "string")) throw new Error("Invalid bookmark response");
      next.push(...page.items);
      cursor = page.nextCursor ?? null;
      if (cursor !== null && (typeof cursor !== "string" || cursors.has(cursor))) throw new Error("Invalid bookmark cursor");
      cursors.add(cursor);
    } while (cursor !== null);
    if (epoch !== accountAccessEpoch() || currentRevision !== revision) return items;
    items = next; announce(); return items;
  })();
  loading = operation;
  try { return await operation; } finally { if (loading === operation) loading = null; }
}

export async function toggleSavedLoan(recommendation, { historyId = null } = {}) {
  const id = recommendation.loanId;
  if (pendingLoans.has(id)) return null;
  pendingLoans.add(id);
  try {
    const epoch = accountAccessEpoch();
    const saved = items.some(item => item.loanId === id);
    await authorizedRequest(`bookmarks/${encodeURIComponent(id)}`, {
      method: saved ? "DELETE" : "PUT", ...(saved ? {} : { body: historyId ? { historyId } : {} }),
    });
    if (epoch !== accountAccessEpoch()) return null;
    revision += 1; loading = null;
    items = saved ? items.filter(item => item.loanId !== id) : [...items, recommendation];
    announce(); return !saved;
  } finally { pendingLoans.delete(id); }
}

if (typeof window !== "undefined") {
  window.addEventListener("shahab:account-changed", clearSavedLoansCache);
  window.addEventListener("shahab:account-cleared", clearSavedLoansCache);
}
