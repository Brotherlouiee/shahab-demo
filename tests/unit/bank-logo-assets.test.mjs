import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { test } from "node:test";
import assert from "node:assert/strict";

const root = resolve(import.meta.dirname, "../..");
const manifest = JSON.parse(readFileSync(resolve(root, "data/contracts/bank-logo-assets.v1.json"), "utf8"));

test("every verified bank logo has an ASCII versioned path and matching SHA-256", () => {
  const calculated = Object.entries(manifest.assets).map(([filename, asset]) => {
    assert.match(asset.assetKey, /^bank-logos\/v1\/[a-f0-9]{64}\.svg$/);
    const bytes = readFileSync(resolve(root, "public", asset.assetKey));
    assert.match(bytes.toString("utf8", 0, 256), /^(?:<\?xml[^>]*>\s*)?<svg\b/);
    assert.doesNotMatch(bytes.toString("utf8", 0, 32), /^(?:PHN2Zy|PD94bWw)/);
    return [filename, createHash("sha256").update(bytes).digest("hex")];
  });
  for (const [filename, actualSha256] of calculated) {
    assert.equal(actualSha256, manifest.assets[filename].sha256);
    assert.equal(actualSha256, manifest.assets[filename].assetKey.match(/\/([a-f0-9]{64})\.svg$/)[1]);
  }
});

test("every canonical lender resolves to a verified controlled asset", () => {
  for (const asset of Object.values(manifest.byLender)) {
    assert.ok(Object.values(manifest.assets).some(
      (candidate) => candidate.assetKey === asset.assetKey && candidate.sha256 === asset.sha256,
    ));
  }
});

test("the manifest covers representative published lender names", () => {
  for (const lenderName of ["بانک ملت", "بانک مسکن", "بانک شهر", "بانک ملی"]) {
    assert.match(manifest.byLender[lenderName].assetKey, /^bank-logos\/v1\/[a-f0-9]{64}\.svg$/);
  }
});
