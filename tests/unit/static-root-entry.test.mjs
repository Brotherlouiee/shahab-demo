import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("index root has no legacy fallback UI before React starts", async () => {
  const html = await readFile(new URL("../../index.html", import.meta.url), "utf8");
  const root = html.match(/<div\b(?=[^>]*\bid=["']root["'])[^>]*>([\s\S]*?)<\/div>/i);

  assert.ok(root, "index.html must define the React root");
  assert.equal(root[1].trim(), "", "the React root must not contain static fallback markup");
  for (const legacyText of ["محاسبه وام شهاب", "طرح نیک وام", "ثبت درخواست وام بانکی"]) {
    assert.equal(html.includes(legacyText), false, "legacy mock text must not remain in index.html: " + legacyText);
  }
});
