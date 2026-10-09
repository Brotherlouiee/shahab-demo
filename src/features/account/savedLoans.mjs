const savedLoansKey = "shahab.savedLoans";

export function readSavedLoans() {
  try {
    const value = JSON.parse(window.localStorage.getItem(savedLoansKey) || "[]");
    return Array.isArray(value) ? value : [];
  } catch {
    return [];
  }
}

export function toggleSavedLoan(recommendation) {
  const current = readSavedLoans();
  const exists = current.some((item) => item.loanId === recommendation.loanId);
  const next = exists ? current.filter((item) => item.loanId !== recommendation.loanId) : [...current, recommendation];
  window.localStorage.setItem(savedLoansKey, JSON.stringify(next));
  window.dispatchEvent(new Event("shahab:saved-loans"));
  return !exists;
}
