import assert from "node:assert/strict";
import test from "node:test";

import {
  fetchRecommendationResult,
  RecommendationResultApiError,
} from "../../src/features/recommendation/presentation/recommendationResultClient.mjs";

const responsePayload = {
  dataVersion: "serving.v1",
  configVersion: "recommendation.v1",
  rankedRecommendations: [
    {
      loanId: "loan/a",
      lenderName: "بانک نمونه",
      loanName: "طرح نمونه",
      compatibilityScore: 0.75,
      compatibilityReason: "سقف وام و نرخ سود با ترجیح شما هماهنگ است.",
    },
  ],
  needsReview: [],
};

test("posts only the active-tab session ID and returns the validated server result view model", async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, options });
    return { ok: true, json: async () => responsePayload };
  };

  const result = await fetchRecommendationResult("opaque session", { fetchImpl });

  assert.equal(result.rankedRecommendations[0].compatibilityScore, 0.75);
  assert.deepEqual(calls, [
    {
      url: "/api/v1/recommendations",
      options: {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId: "opaque session" }),
        signal: undefined,
      },
    },
  ]);
  assert.equal(calls[0].url.includes("?"), false);
  assert.equal(calls[0].url.includes("opaque session"), false);
});

test("does not expose a malformed response or server failure as a recommendation", async () => {
  await assert.rejects(
    () => fetchRecommendationResult("opaque", { fetchImpl: async () => ({ ok: false, status: 503 }) }),
    (error) => error instanceof RecommendationResultApiError && error.status === 503,
  );
  await assert.rejects(
    () =>
      fetchRecommendationResult("opaque", {
        fetchImpl: async () => ({
          ok: true,
          json: async () => ({ ...responsePayload, dataVersion: "" }),
        }),
      }),
    (error) => error instanceof RecommendationResultApiError && error.status === 502,
  );
  await assert.rejects(
    () => fetchRecommendationResult("", { fetchImpl: async () => ({ ok: true, json: async () => responsePayload }) }),
    (error) => error instanceof RecommendationResultApiError && error.status === 400,
  );
});
