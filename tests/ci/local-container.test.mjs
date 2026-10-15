import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

function run({ database = "", missing = false, exitCode = 0, unhealthy = false } = {}) {
  const dir = mkdtempSync(path.join(tmpdir(), "shahab-ci-test-"));
  for (const name of ["bin", "temp", "cache", "workspace"]) mkdirSync(path.join(dir, name));
  const log = path.join(dir, "docker.jsonl");
  writeFileSync(path.join(dir, "bin/docker"), `#!/usr/bin/env node
const fs = require("node:fs");
const args = process.argv.slice(2);
fs.appendFileSync(process.env.MOCK_DOCKER_LOG, JSON.stringify(args) + "\\n");
if (args[0] === "image" && process.env.MOCK_MISSING === "true") process.exit(1);
if (args[0] === "inspect") console.log(process.env.MOCK_UNHEALTHY === "true" ? "unhealthy" : "healthy");
if (args[0] === "run" && args.includes("shahab-ci:local-v1")) process.exit(Number(process.env.MOCK_CHECK_EXIT));
`, { mode: 0o755 });
  const result = spawnSync("bash", ["scripts/ci/run-local-container.sh"], {
    encoding: "utf8",
    env: {
      ...process.env, PATH: path.join(dir, "bin") + path.delimiter + process.env.PATH,
      GITHUB_WORKSPACE: path.join(dir, "workspace"), RUNNER_TEMP: path.join(dir, "temp"),
      RUNNER_TOOL_CACHE: path.join(dir, "cache"), SHAHAB_CI_COMMANDS: "echo verification",
      SHAHAB_CI_DATABASE: database, MOCK_DOCKER_LOG: log,
      MOCK_MISSING: String(missing), MOCK_UNHEALTHY: String(unhealthy), MOCK_CHECK_EXIT: String(exitCode),
    },
  });
  let calls = [];
  try { calls = readFileSync(log, "utf8").trim().split("\n").filter(Boolean).map(JSON.parse); }
  catch (error) { if (error.code !== "ENOENT") throw error; }
  rmSync(dir, { recursive: true, force: true });
  return { result, calls };
}

test("missing prepared image fails before creating resources or pulling", () => {
  const { result, calls } = run({ missing: true });
  assert.equal(result.status, 1);
  assert.deepEqual(calls, [["image", "inspect", "shahab-ci:local-v1"]]);
});

test("only the two disposable database names are accepted", () => {
  const { result, calls } = run({ database: "production" });
  assert.equal(result.status, 2);
  assert.deepEqual(calls, []);
});

test("database and job have no published ports; cleanup targets only this invocation", () => {
  const { result, calls } = run({ database: "shahab_test" });
  assert.equal(result.status, 0, result.stderr);
  const runs = calls.filter(args => args[0] === "run");
  assert.equal(runs.length, 2);
  for (const args of runs) {
    assert.ok(args.includes("--pull=never"));
    assert.ok(!args.some(arg => ["-p", "--publish", "-P", "--privileged"].includes(arg)));
    assert.ok(!args.join(" ").includes("docker.sock"));
    assert.ok(!args.join(" ").includes("shahab-demo_postgres_data"));
  }
  const job = runs.find(args => args.includes("shahab-ci:local-v1"));
  assert.ok(job.includes("--user"));
  const names = runs.map(args => args[args.indexOf("--name") + 1]);
  const removed = calls.filter(args => args[0] === "rm").map(args => args.at(-1));
  assert.deepEqual(new Set(removed), new Set(names));
  assert.ok(calls.some(args => args[0] === "network" && args[1] === "rm"));
  assert.ok(!calls.some(args => args.includes("prune")));
});

test("verification failure stays failed and cleans its container and network", () => {
  const { result, calls } = run({ exitCode: 23 });
  assert.equal(result.status, 23);
  assert.equal(calls.filter(args => args[0] === "rm").length, 1);
  assert.ok(calls.some(args => args[0] === "network" && args[1] === "rm"));
});

test("unhealthy database prevents verification and cleans its own resources", () => {
  const { result, calls } = run({ database: "shahab_profile_test", unhealthy: true });
  assert.equal(result.status, 1);
  assert.ok(!calls.some(args => args[0] === "run" && args.includes("shahab-ci:local-v1")));
  assert.equal(calls.filter(args => args[0] === "rm").length, 2);
});
