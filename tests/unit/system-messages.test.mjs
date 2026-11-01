import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createSystemMessage } from "../../src/shared/systemMessages.mjs";

test("system messages accept the three requested types and preserve their text", () => {
  for (const type of ["success", "warning", "error"]) {
    assert.deepEqual(createSystemMessage(type, "متن نمونه"), {
      type,
      message: "متن نمونه",
    });
  }
});

test("system messages reject unknown types and empty text", () => {
  assert.throws(() => createSystemMessage("info", "متن"), TypeError);
  assert.throws(() => createSystemMessage("success", "  "), TypeError);
});

test("system feedback and button palette use the approved brand colors", () => {
  const css = readFileSync(new URL("../../src/shared/system-messages.css", import.meta.url), "utf8");
  assert.match(css, /--shahab-success:\s*#059C7B/i);
  assert.match(css, /--shahab-warning:\s*#FFF600/i);
  assert.match(css, /--shahab-error:\s*#FF0000/i);
  assert.match(css, /--shahab-charcoal:\s*#303335/i);
  assert.match(css, /\.hp-next-question[\s\S]*?background-color:\s*var\(--shahab-success\)/);
  assert.match(css, /button\.submit-button[\s\S]*?background-color:\s*var\(--shahab-charcoal\)/);
});

test("all inline warning and field-error messages use their typed palette", () => {
  const css = readFileSync(new URL("../../src/shared/system-messages.css", import.meta.url), "utf8");
  for (const selector of [".hp-loan-otp-error", ".hp-personal-field-error"]) {
    assert.match(css, new RegExp(selector.replaceAll(".", "\\\\.") + "[\\s\\S]*?color:\\s*var\\(--shahab-error\\)"));
  }
  for (const selector of [".hp-question-warning", ".hp-compare-warning", ".hp-compare-info"]) {
    assert.match(css, new RegExp(selector.replaceAll(".", "\\\\.") + "[\\s\\S]*?color:\\s*var\\(--shahab-warning\\)"));
  }
});
