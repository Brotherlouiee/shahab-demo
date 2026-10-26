/**
 * Canonical navigation boundary for the behavioural questionnaire.
 *
 * Browser paths are retained for compatibility with the prototype, but are
 * deliberately not used as recommendation identifiers.  This adapter is the
 * only place where a public path is translated to (or from) the stable
 * question IDs approved in the questionnaire contract.
 */
const routeEntries = Object.freeze([
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

const questionIdByRoute = new Map(routeEntries);
const routeByQuestionId = new Map(routeEntries.map(([route, questionId]) => [questionId, route]));
const prototypeQuestionIndexByQuestionId = new Map(
  routeEntries.map(([, questionId], offset) => [questionId, offset + 2]),
);

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
  const questionId = routeEntries[questionIndex - 2]?.[1];
  return questionId ? getQuestionnaireRouteForCanonicalQuestionId(questionId) : null;
}

/**
 * Keep direct links and browser history from skipping required questions.
 * A route at the first unanswered question is allowed; later routes are not.
 */
export function guardQuestionnaireRoute(pathname, answeredQuestionIds = []) {
  const requestedIndex = routeEntries.findIndex(([route]) => route === pathname);
  if (requestedIndex < 0) return pathname;

  const answered = new Set(answeredQuestionIds);
  const firstUnansweredIndex = routeEntries.findIndex(([, questionId]) => !answered.has(questionId));
  if (firstUnansweredIndex < 0 || requestedIndex <= firstUnansweredIndex) return pathname;
  return routeEntries[firstUnansweredIndex][0];
}

export const canonicalQuestionnaireRouteEntries = routeEntries;
