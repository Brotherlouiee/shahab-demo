import assert from "node:assert/strict";
import test from "node:test";

import { fetchLoanDetails } from "../../src/features/loan-details/loanDetailsApi.js";

test("deduplicates concurrent detail requests and reuses the same-tab response", async () => {
  const originalFetch = globalThis.fetch;
  let calls = 0;
  let release;
  const pending = new Promise((resolve) => { release = resolve; });
  globalThis.fetch = async () => {
    calls += 1;
    await pending;
    return new Response(JSON.stringify({
      loanId: "cached-loan", conditions: [], bankLogoReference: null,
    }), { status: 200, headers: { "Content-Type": "application/json" } });
  };
  try {
    const first = fetchLoanDetails("cached-loan");
    const second = fetchLoanDetails("cached-loan");
    assert.equal(calls, 1);
    release();
    assert.deepEqual(await first, await second);
    await fetchLoanDetails("cached-loan");
    assert.equal(calls, 1);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
