/**
 * Browser-local storage for bookmarks selected from server-provided recommendation cards.
 * This feature deliberately stores only the displayed public loan reference, never
 * questionnaire answers, a recommendation session id, or a user credential.
 */
export const SAVED_LOANS_CHANGED_EVENT = "shahab:saved-loans";
const savedLoansCacheKey = "shahab.savedLoans";

export function readSavedLoans() {
  if (typeof window === "undefined") return [];
  try {
    const value = JSON.parse(window.localStorage.getItem(savedLoansCacheKey) || "[]");
    return Array.isArray(value)
      ? value.filter((item) => item && typeof item.loanId === "string")
      : [];
  } catch {
    return [];
  }
}

function writeSavedLoans(loans) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(savedLoansCacheKey, JSON.stringify(loans));
    window.dispatchEvent(new Event(SAVED_LOANS_CHANGED_EVENT));
  } catch {
    // Bookmarks remain optional when storage is blocked by the browser.
  }
}

export function toggleSavedLoan(recommendation) {
  if (!recommendation?.loanId) return false;
  const loans = readSavedLoans();
  const alreadySaved = loans.some((item) => item.loanId === recommendation.loanId);
  writeSavedLoans(
    alreadySaved
      ? loans.filter((item) => item.loanId !== recommendation.loanId)
      : [...loans, recommendation],
  );
  return !alreadySaved;
}
