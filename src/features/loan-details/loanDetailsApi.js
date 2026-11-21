/** Public, narrow client for the approved serving-loan detail endpoint. */

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export class LoanDetailsApiError extends Error {
  constructor(status) {
    super("Loan details could not be loaded.");
    this.name = "LoanDetailsApiError";
    this.status = status;
  }
}

function normalizeBankLogoReference(value) {
  if (typeof value !== "string") return null;
  const reference = value.trim();
  // The API owns which logo URL is approved. Accept its HTTPS/HTTP URL or a
  // same-origin SVG path; reject protocol-relative and executable schemes.
  if (/^https?:\/\//i.test(reference)) return reference;
  if (/^\/(?!\/)/.test(reference)) return reference;
  return null;
}

function assertDetailPayload(payload) {
  if (!payload || typeof payload !== "object" || typeof payload.loanId !== "string") {
    throw new LoanDetailsApiError(502);
  }
  if (!Array.isArray(payload.conditions) || !payload.conditions.every((item) => typeof item === "string")) {
    throw new LoanDetailsApiError(502);
  }
  return { ...payload, bankLogoReference: normalizeBankLogoReference(payload.bankLogoReference) };
}

const detailCache = new Map();
const detailsInFlight = new Map();

function waitForDetail(promise, signal) {
  if (!signal) return promise;
  if (signal.aborted) return Promise.reject(new DOMException("Aborted", "AbortError"));
  return new Promise((resolve, reject) => {
    const abort = () => reject(new DOMException("Aborted", "AbortError"));
    signal.addEventListener("abort", abort, { once: true });
    promise.then(resolve, reject).finally(() => signal.removeEventListener("abort", abort));
  });
}

export async function fetchLoanDetails(loanId, { signal } = {}) {
  if (!loanId || !loanId.trim()) throw new LoanDetailsApiError(400);
  const cacheKey = loanId.trim();
  if (detailCache.has(cacheKey)) return waitForDetail(Promise.resolve(detailCache.get(cacheKey)), signal);

  let request = detailsInFlight.get(cacheKey);
  if (!request) {
    request = fetch(`${apiBaseUrl}/loans/${encodeURIComponent(cacheKey)}`, {
      headers: { Accept: "application/json" },
    }).then(async (response) => {
      if (response.status === 404) return null;
      if (!response.ok) throw new LoanDetailsApiError(response.status);
      const detail = assertDetailPayload(await response.json());
      detailCache.set(cacheKey, detail);
      return detail;
    }).finally(() => detailsInFlight.delete(cacheKey));
    detailsInFlight.set(cacheKey, request);
  }
  return waitForDetail(request, signal);
}
