import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  canonicalQuestionnaireRouteEntries,
  guardQuestionnaireRoute,
  getCanonicalQuestionIdForRoute,
  getPrototypeQuestionIndexForCanonicalQuestionId,
  getQuestionnaireRouteForCanonicalQuestionId,
  getQuestionnaireRouteForPrototypeQuestionIndex,
} from "../../src/features/questionnaire/questionnaireRouteMap.mjs";

const canonicalIdentifiers = JSON.parse(
  readFileSync(new URL("../../data/contracts/canonical-identifiers.v1.json", import.meta.url), "utf8"),
);
const approvedRoutes = Object.entries(canonicalIdentifiers.questionnaireRouteMap);

test("maps every immutable behavioural route to its canonical ID and back", () => {
  assert.deepEqual(canonicalQuestionnaireRouteEntries, approvedRoutes);

  for (const [route, questionId] of approvedRoutes) {
    assert.equal(getCanonicalQuestionIdForRoute(route), questionId);
    assert.equal(getQuestionnaireRouteForCanonicalQuestionId(questionId), route);
  }
});

test("uses the adapter for the prototype index without making an index canonical", () => {
  for (const [offset, [route, questionId]] of approvedRoutes.entries()) {
    const prototypeQuestionIndex = offset + 2;
    assert.equal(getPrototypeQuestionIndexForCanonicalQuestionId(questionId), prototypeQuestionIndex);
    assert.equal(getQuestionnaireRouteForPrototypeQuestionIndex(prototypeQuestionIndex), route);
  }
});

test("rejects non-behavioural and malformed paths rather than guessing an ID", () => {
  assert.equal(getCanonicalQuestionIdForRoute("/question/1"), null);
  assert.equal(getCanonicalQuestionIdForRoute("/question/13"), null);
  assert.equal(getCanonicalQuestionIdForRoute("/question/03"), null);
  assert.equal(getQuestionnaireRouteForCanonicalQuestionId("Q7"), null);
  assert.equal(getPrototypeQuestionIndexForCanonicalQuestionId("Q7"), null);
  assert.equal(getQuestionnaireRouteForPrototypeQuestionIndex(1), null);
});

test("guards direct and history navigation at the first unanswered required question", () => {
  assert.equal(guardQuestionnaireRoute("/question/4"), "/question/3");
  assert.equal(guardQuestionnaireRoute("/question/5", ["Q1"]), "/question/4");
  assert.equal(guardQuestionnaireRoute("/question/4", ["Q1"]), "/question/4");
  assert.equal(guardQuestionnaireRoute("/question/12", approvedRoutes.map(([, id]) => id)), "/question/12");
  assert.equal(guardQuestionnaireRoute("/loan-results", []), "/loan-results");
});
