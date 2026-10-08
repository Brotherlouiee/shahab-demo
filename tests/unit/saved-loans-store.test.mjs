import assert from "node:assert/strict";
import test from "node:test";

import { readSavedLoans, toggleSavedLoan } from "../../src/features/account/savedLoansStore.mjs";

function installBrowserStorage() {
  const values = new Map();
  const listeners = new Map();
  global.window = {
    localStorage: {
      getItem: (key) => values.get(key) ?? null,
      setItem: (key, value) => values.set(key, value),
    },
    addEventListener: (name, handler) => listeners.set(name, handler),
    removeEventListener: (name) => listeners.delete(name),
    dispatchEvent: (event) => listeners.get(event.type)?.(event),
  };
  return values;
}

test("saved loans retain only the actual selected recommendation reference", () => {
  const values = installBrowserStorage();
  const card = { loanId: "published-loan-42", loanName: "طرح نمونهٔ API", lenderName: "بانک نمونه" };

  assert.equal(toggleSavedLoan(card), true);
  assert.deepEqual(readSavedLoans(), [card]);
  assert.equal(JSON.parse(values.get("shahab.savedLoans"))[0].loanId, "published-loan-42");

  assert.equal(toggleSavedLoan(card), false);
  assert.deepEqual(readSavedLoans(), []);
});
