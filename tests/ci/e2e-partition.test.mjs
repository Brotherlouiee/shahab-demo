import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

function verify(original, built, development) {
  const dir = mkdtempSync(path.join(tmpdir(), "shahab-e2e-partition-"));
  try {
    const reports = [original, built, development].map((ids, index) => {
      const file = path.join(dir, index + ".json");
      writeFileSync(file, JSON.stringify({ suites: [{ suites: [{ specs: ids.map(id => ({ id })) }] }] }));
      return file;
    });
    return spawnSync(process.execPath, ["scripts/ci/verify_e2e_partition.mjs", ...reports], { encoding: "utf8" });
  } finally { rmSync(dir, { recursive: true, force: true }); }
}

test("built and dev phases together cover every discovered original test exactly once", () => {
  const result = verify(["home", "loading", "api"], ["home", "api"], ["loading"]);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /original=3 built=2 dev=1/);
});

test("a silently omitted original test fails the gate", () => {
  assert.notEqual(verify(["home", "loading", "api"], ["home"], ["loading"]).status, 0);
});

test("duplicate execution and malformed discovery fail the gate", () => {
  assert.notEqual(verify(["home", "loading"], ["home", "loading"], ["loading"]).status, 0);
  assert.notEqual(verify(["home"], ["home"], []).status, 0);
  assert.notEqual(verify([null], [null], [null]).status, 0);
});
