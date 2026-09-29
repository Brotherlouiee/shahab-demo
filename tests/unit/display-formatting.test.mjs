import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { test } from "node:test";

import { toPersianDigits } from "../../src/features/loan-details/toPersianDigits.mjs";
import { compatibilityBandForScore } from "../../src/features/recommendation/ui/compatibilityDisplay.mjs";

test("visible loan text converts ASCII and Arabic-Indic digits to Persian digits", () => {
  assert.equal(toPersianDigits("میثاق 2 / ٣"), "میثاق ۲ / ۳");
  assert.equal(toPersianDigits("بازپرداخت 24 ماهه"), "بازپرداخت ۲۴ ماهه");
});

test("compatibility bands use the displayed rounded percentage at every boundary", () => {
  for (const [percent, expected] of [
    [100, "blue"], [80, "blue"], [79, "lime"], [60, "lime"],
    [59, "orange"], [40, "orange"], [39, "deep-orange"], [20, "deep-orange"],
    [19, "red"], [0, "red"],
  ]) {
    assert.equal(compatibilityBandForScore(percent / 100), expected, String(percent));
  }
  assert.equal(compatibilityBandForScore(null), null);
  assert.equal(compatibilityBandForScore(Number.NaN), null);
});

test("compatibility CSS keeps the requested card and percent color scale", () => {
  const css = readFileSync(resolve(import.meta.dirname, "../../src/App.css"), "utf8");
  for (const [band, color] of [
    ["blue", "#0067ff"], ["lime", "#CFD238"], ["orange", "#F28943"],
    ["deep-orange", "#FF2F00"], ["red", "#FF0004"],
  ]) {
    assert.match(css, new RegExp(`data-compatibility-band="${band}"[^}]*--loan-accent: ${color};[^}]*border-color: ${color};`));
  }
});
