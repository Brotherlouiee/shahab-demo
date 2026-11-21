import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

function ids(file) {
  const result = [];
  function visit(suite) {
    for (const spec of suite.specs || []) {
      assert.equal(typeof spec.id, "string", "discovery must include stable test IDs");
      assert.ok(spec.id.length > 0, "test ID must not be empty");
      result.push(spec.id);
    }
    for (const child of suite.suites || []) visit(child);
  }
  visit(JSON.parse(readFileSync(file, "utf8")));
  assert.ok(result.length > 0, "test discovery must not be empty");
  assert.equal(new Set(result).size, result.length, "duplicate discovered test");
  return result;
}

assert.equal(process.argv.length, 5, "requires original, built, and development discovery reports");
const [original, built, development] = process.argv.slice(2).map(ids);
const partition = [...built, ...development];
assert.equal(new Set(partition).size, partition.length, "a test would run in both phases");
assert.deepEqual([...partition].sort(), [...original].sort(), "every original test must run in exactly one phase");
console.log(
  "E2E_DISCOVERY original=" + original.length + " built=" + built.length + " dev=" + development.length,
);
