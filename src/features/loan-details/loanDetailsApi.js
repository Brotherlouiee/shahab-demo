/** Public, narrow client for the approved serving-loan detail endpoint. */

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export class LoanDetailsApiError extends Error {
  constructor(status) {
    super("Loan details could not be loaded.");
    this.name = "LoanDetailsApiError";
    this.status = status;
  }
}

function assertDetailPayload(payload) {
  if (!payload || typeof payload !== "object" || typeof payload.loanId !== "string") {
    throw new LoanDetailsApiError(502);
  }
  if (payload.bankLogoReference !== null && payload.bankLogoReference !== undefined && typeof payload.bankLogoReference !== "string") {
    throw new LoanDetailsApiError(502);
  }
  if (!Array.isArray(payload.conditions) || !payload.conditions.every((item) => typeof item === "string")) {
    throw new LoanDetailsApiError(502);
  }
  return payload;
}

export async function fetchLoanDetails(loanId, { signal } = {}) {
  if (!loanId || !loanId.trim()) {
    throw new LoanDetailsApiError(400);
  }
  const response = await fetch(`${apiBaseUrl}/loans/${encodeURIComponent(loanId)}`, {
    headers: { Accept: "application/json" },
    signal,
  });
  if (response.status === 404) return null;
  if (!response.ok) throw new LoanDetailsApiError(response.status);
  return assertDetailPayload(await response.json());
}
