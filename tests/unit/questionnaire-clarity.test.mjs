import test from "node:test";
import assert from "node:assert/strict";
import { trackQuestionnaireClarity } from "../../src/features/questionnaire/questionnaireClarity.mjs";

test("emits a fixed action and step number without answer data", () => {
  const originalWindow = globalThis.window;
  const events = [];
  globalThis.window = { clarity: (...args) => events.push(args) };

  try {
    assert.equal(trackQuestionnaireClarity("answer_saved", 3), true);
    assert.deepEqual(events, [["event", "questionnaire_answer_saved_step_03"]]);
  } finally {
    if (originalWindow === undefined) delete globalThis.window;
    else globalThis.window = originalWindow;
  }
});

test("rejects unknown actions and invalid step numbers", () => {
  const originalWindow = globalThis.window;
  const events = [];
  globalThis.window = { clarity: (...args) => events.push(args) };

  try {
    assert.equal(trackQuestionnaireClarity("answer_value", 3), false);
    assert.equal(trackQuestionnaireClarity("answer_saved", 0), false);
    assert.equal(trackQuestionnaireClarity("answer_saved", 21), false);
    assert.deepEqual(events, []);
  } finally {
    if (originalWindow === undefined) delete globalThis.window;
    else globalThis.window = originalWindow;
  }
});

test("does nothing when Clarity is not loaded", () => {
  const originalWindow = globalThis.window;
  globalThis.window = {};

  try {
    assert.equal(trackQuestionnaireClarity("step_viewed", 1), false);
  } finally {
    if (originalWindow === undefined) delete globalThis.window;
    else globalThis.window = originalWindow;
  }
});
