import assert from "node:assert/strict";
import test from "node:test";

import {
  readCurrentQuestionnaireSession,
  saveQuestionnaireAnswer,
  saveQuestionnaireFlowAnswer,
  startQuestionnaireSession,
} from "../../src/features/questionnaire/questionnaireSessionClient.mjs";

test("starts a body-only questionnaire session", async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, options });
    return { ok: true, json: async () => ({ sessionId: "opaque-session" }) };
  };

  assert.deepEqual(await startQuestionnaireSession(fetchImpl), { sessionId: "opaque-session" });
  assert.deepEqual(calls, [{ url: "/api/v1/questionnaire/sessions", options: { method: "POST" } }]);
});

test("recovers the current session from the same-origin HttpOnly cookie without putting an id in the URL", async () => {
  const calls = [];
  const session = { sessionId: "opaque-session", answers: { Q1: "Q1.answer" }, flowAnswers: {} };
  const fetchImpl = async (url, options) => {
    calls.push({ url, options });
    return { ok: true, json: async () => session };
  };

  assert.deepEqual(await readCurrentQuestionnaireSession(fetchImpl), session);
  assert.deepEqual(calls, [{
    url: "/api/v1/questionnaire/sessions/current",
    options: { cache: "no-store" },
  }]);
});

test("writes an entry-step answer through the protected JSON endpoint", async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, options });
    return { ok: true, json: async () => ({ flowAnswers: { loan_type: "bank" } }) };
  };

  await saveQuestionnaireFlowAnswer("opaque session", "loan_type", "bank", fetchImpl);

  assert.equal(calls[0].url,
    "/api/v1/questionnaire/sessions/opaque%20session/flow-answers/loan_type");
  assert.equal(calls[0].options.method, "PUT");
  assert.equal(calls[0].options.body, JSON.stringify({ answerId: "bank" }));
  assert.equal(calls[0].url.includes("?"), false);
});

test("writes a canonical answer in JSON rather than a query string", async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, options });
    return { ok: true, json: async () => ({ answers: { Q1: "Q1.incomeInvestment" } }) };
  };

  await saveQuestionnaireAnswer("opaque session", "Q1", "Q1.incomeInvestment", fetchImpl);

  assert.equal(calls[0].url, "/api/v1/questionnaire/sessions/opaque%20session/answers/Q1");
  assert.equal(calls[0].options.method, "PUT");
  assert.equal(calls[0].options.body, JSON.stringify({ answerId: "Q1.incomeInvestment" }));
  assert.equal(calls[0].url.includes("?"), false);
});
