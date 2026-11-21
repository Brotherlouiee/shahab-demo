const SAVED_LOANS_RETURN_TARGET = "saved-loans";

export function shouldShowSavedLoanFilters(savedItems) {
  return !Array.isArray(savedItems) || savedItems.length > 1;
}

export function savedLoanDetailsPath(loanId) {
  return `/loan-details?loanId=${encodeURIComponent(loanId)}&from=${SAVED_LOANS_RETURN_TARGET}`;
}

export function isSavedLoanDetailsPath(search) {
  return new URLSearchParams(search).get("from") === SAVED_LOANS_RETURN_TARGET;
}
