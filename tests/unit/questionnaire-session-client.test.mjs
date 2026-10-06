import assert from "node:assert/strict";
import test from "node:test";

import {
  QuestionnaireSessionApiError,
  saveQuestionnaireAnswer,
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


test("preserves HTTP expiry and transient failure status without exposing response bodies", async () => {
  for (const status of [410, 503]) {
    const fetchImpl = async () => ({ ok: false, status, json: async () => { throw Error("must not read error body"); } });
    await assert.rejects(saveQuestionnaireAnswer("opaque", "Q1", "canonical", fetchImpl), error => error instanceof QuestionnaireSessionApiError && error.status === status);
    await assert.rejects(startQuestionnaireSession(fetchImpl), error => error instanceof QuestionnaireSessionApiError && error.status === status);
  }
});
