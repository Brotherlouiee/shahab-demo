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
  assert.match(css, /\.hp-loan-otp-error,[\s\S]*?\.hp-personal-field-error[\s\S]*?color:\s*var\(--shahab-error\)/);
  assert.match(css, /\.hp-question-warning p,[\s\S]*?\.hp-compare-warning p,[\s\S]*?\.hp-compare-info p[\s\S]*?color:\s*var\(--shahab-warning\)/);
});
