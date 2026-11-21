import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  canonicalQuestionnaireRouteEntries,
  questionnaireJourneyRouteEntries,
  guardQuestionnaireRoute,
  getCanonicalQuestionIdForRoute,
  getPrototypeQuestionIndexForCanonicalQuestionId,
  getQuestionnaireRouteForCanonicalQuestionId,
  getQuestionnaireRouteForPrototypeQuestionIndex,
  getQuestionnaireStepIdForPrototypeQuestionIndex,
} from "../../src/features/questionnaire/questionnaireRouteMap.mjs";

const canonicalIdentifiers = JSON.parse(
  readFileSync(new URL("../../data/contracts/canonical-identifiers.v1.json", import.meta.url), "utf8"),
);
const approvedRoutes = Object.entries(canonicalIdentifiers.questionnaireRouteMap);

test("keeps the ten scoring routes mapped to the approved canonical IDs", () => {
  assert.deepEqual(canonicalQuestionnaireRouteEntries, approvedRoutes);
  for (const [route, questionId] of approvedRoutes) {
    assert.equal(getCanonicalQuestionIdForRoute(route), questionId);
    assert.equal(getQuestionnaireRouteForCanonicalQuestionId(questionId), route);
  }
});

test("maps all twelve visible steps to stable server-side step IDs", () => {
  assert.equal(questionnaireJourneyRouteEntries.length, 12);
  assert.deepEqual(questionnaireJourneyRouteEntries.slice(0, 2), [
    ["/question/1", "loan_type"], ["/question/2", "entity_type"],
  ]);
  for (const [index, [route, stepId]] of questionnaireJourneyRouteEntries.entries()) {
    assert.equal(getQuestionnaireRouteForPrototypeQuestionIndex(index), route);
    assert.equal(getQuestionnaireStepIdForPrototypeQuestionIndex(index), stepId);
  }
});

test("blocks direct, refreshed, and history navigation beyond the first unanswered step", () => {
  for (let answeredCount = 0; answeredCount <= questionnaireJourneyRouteEntries.length; answeredCount += 1) {
    const answered = questionnaireJourneyRouteEntries.slice(0, answeredCount).map(([, id]) => id);
    const flowAnswers = answered.filter((id) => id === "loan_type" || id === "entity_type");
    const canonicalAnswers = answered.filter((id) => id !== "loan_type" && id !== "entity_type");
    const firstUnansweredRoute = questionnaireJourneyRouteEntries[answeredCount]?.[0];

    for (let requestedIndex = 0; requestedIndex < questionnaireJourneyRouteEntries.length; requestedIndex += 1) {
      const [requestedRoute] = questionnaireJourneyRouteEntries[requestedIndex];
      const expected = requestedIndex <= answeredCount
        ? requestedRoute
        : firstUnansweredRoute;
      assert.equal(
        guardQuestionnaireRoute(requestedRoute, canonicalAnswers, flowAnswers),
        expected,
        `answered=${answeredCount}, requested=${requestedRoute}`,
      );
    }
  }
});

test("fails closed for malformed and unknown numbered questionnaire paths", () => {
  assert.equal(guardQuestionnaireRoute("/question/13"), "/question/1");
  assert.equal(guardQuestionnaireRoute("/question/03"), "/question/1");
  assert.equal(guardQuestionnaireRoute("/question/not-a-number"), "/question/not-a-number");
  assert.equal(guardQuestionnaireRoute("/loan-results"), "/loan-results");
});
