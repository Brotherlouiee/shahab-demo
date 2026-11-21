import questionnaireConfiguration from "../../../data/contracts/questionnaire-configuration.v1.json";
import { getCanonicalQuestionIdForRoute } from "./questionnaireRouteMap.mjs";

/**
 * Returns the approved behavioural question for an existing prototype screen.
 *
 * The screen index is used only to preserve the legacy layout. The returned
 * question and every answer identity are source-traceable canonical values.
 */
export function getCanonicalQuestionForPrototypeIndex(prototypeQuestionIndex) {
  const pathname = `/question/${prototypeQuestionIndex + 1}`;
  const questionId = getCanonicalQuestionIdForRoute(pathname);
  if (!questionId) return null;

  const question = questionnaireConfiguration.questions.find(
    (candidate) => candidate.questionId === questionId,
  );
  if (!question) {
    throw new Error(`canonical question is missing for ${questionId}`);
  }
  return question;
}
