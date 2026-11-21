import assert from "node:assert/strict";
import test from "node:test";

import {
  isSavedLoanDetailsPath,
  savedLoanDetailsPath,
  shouldShowSavedLoanFilters,
} from "../../src/features/account/savedLoansPresentation.mjs";

test("shows saved-loan filters only when two or more saved loans can be filtered", () => {
  assert.equal(shouldShowSavedLoanFilters([]), false);
  assert.equal(shouldShowSavedLoanFilters([{ loanId: "loan-1" }]), false);
  assert.equal(shouldShowSavedLoanFilters([{ loanId: "loan-1" }, { loanId: "loan-2" }]), true);
  assert.equal(shouldShowSavedLoanFilters(null), true);
});

test("keeps the saved-loans return target in the loan-details URL", () => {
  assert.equal(savedLoanDetailsPath("loan / 1"), "/loan-details?loanId=loan%20%2F%201&from=saved-loans");
  assert.equal(isSavedLoanDetailsPath("?loanId=loan-1&from=saved-loans"), true);
  assert.equal(isSavedLoanDetailsPath("?loanId=loan-1"), false);
});
