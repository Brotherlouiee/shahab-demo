/**
 * Canonical navigation boundary for the behavioural questionnaire.
 *
 * Browser paths are retained for compatibility with the prototype, but are
 * deliberately not used as recommendation identifiers.  This adapter is the
 * only place where a public path is translated to (or from) the stable
 * question IDs approved in the questionnaire contract.
 */
const canonicalRouteEntries = Object.freeze([
  ["/question/3", "Q1"],
  ["/question/4", "Q2"],
  ["/question/5", "Q3"],
  ["/question/6", "Q4"],
  ["/question/7", "Q5"],
  ["/question/8", "Q6"],
  ["/question/9", "S7"],
  ["/question/10", "S8"],
  ["/question/11", "S10"],
  ["/question/12", "S13"],
]);

const flowRouteEntries = Object.freeze([
  ["/question/1", "loan_type"],
  ["/question/2", "entity_type"],
]);
const journeyRouteEntries = Object.freeze([
  ...flowRouteEntries,
  ...canonicalRouteEntries,
]);

const questionIdByRoute = new Map(canonicalRouteEntries);
const routeByQuestionId = new Map(canonicalRouteEntries.map(([route, questionId]) => [questionId, route]));
const prototypeQuestionIndexByQuestionId = new Map(
  canonicalRouteEntries.map(([, questionId], offset) => [questionId, offset + 2]),
);
const stepIdByPrototypeQuestionIndex = new Map([
  [0, "loan_type"], [1, "entity_type"],
  ...canonicalRouteEntries.map(([, questionId], offset) => [offset + 2, questionId]),
]);

/** Return a canonical ID for an exact questionnaire path, otherwise null. */
export function getCanonicalQuestionIdForRoute(pathname) {
  return questionIdByRoute.get(pathname) ?? null;
}

/** Return the immutable public path for a canonical behavioural question. */
export function getQuestionnaireRouteForCanonicalQuestionId(questionId) {
  return routeByQuestionId.get(questionId) ?? null;
}

/**
 * Bridge the canonical route contract to the prototype's pre-existing screen
 * index.  This is navigation-only compatibility glue; answer persistence must
 * use the canonical ID and is intentionally deferred to US-07.T03/T04.
 */
export function getPrototypeQuestionIndexForCanonicalQuestionId(questionId) {
  return prototypeQuestionIndexByQuestionId.get(questionId) ?? null;
}

/** Return a canonical route for an existing prototype screen index, if mapped. */
export function getQuestionnaireRouteForPrototypeQuestionIndex(questionIndex) {
  return journeyRouteEntries[questionIndex]?.[0] ?? null;
}

export function getQuestionnaireStepIdForPrototypeQuestionIndex(questionIndex) {
  return stepIdByPrototypeQuestionIndex.get(questionIndex) ?? null;
}

export function getPrototypeQuestionIndexForQuestionnaireStepId(stepId) {
  for (const [index, candidate] of stepIdByPrototypeQuestionIndex) {
    if (candidate === stepId) return index;
  }
  return null;
}

/**
 * Keep direct links and browser history from skipping required questions.
 * A route at the first unanswered question is allowed; later routes are not.
 */
export function guardQuestionnaireRoute(pathname, answeredQuestionIds = [], answeredFlowStepIds = []) {
  const requestedIndex = journeyRouteEntries.findIndex(([route]) => route === pathname);
  if (requestedIndex < 0) {
    if (!/^\/question\/\d+$/.test(pathname)) return pathname;
    const completed = new Set([...answeredFlowStepIds, ...answeredQuestionIds]);
    const firstUnansweredIndex = journeyRouteEntries.findIndex(([, stepId]) => !completed.has(stepId));
    return journeyRouteEntries[Math.max(0, firstUnansweredIndex)][0];
  }

  const completed = new Set([...answeredFlowStepIds, ...answeredQuestionIds]);
  const firstUnansweredIndex = journeyRouteEntries.findIndex(([, stepId]) => !completed.has(stepId));
  if (firstUnansweredIndex < 0 || requestedIndex <= firstUnansweredIndex) return pathname;
  return journeyRouteEntries[firstUnansweredIndex][0];
}

export const canonicalQuestionnaireRouteEntries = canonicalRouteEntries;
export const questionnaireJourneyRouteEntries = journeyRouteEntries;
