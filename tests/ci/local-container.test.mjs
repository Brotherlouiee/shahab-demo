import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

function run({ database = "", missing = false, exitCode = 0, unhealthy = false, profile = "" } = {}) {
  const dir = mkdtempSync(path.join(tmpdir(), "shahab-ci-test-"));
  for (const name of ["bin", "temp", "cache", "workspace"]) mkdirSync(path.join(dir, name));
  const log = path.join(dir, "docker.jsonl");
  writeFileSync(path.join(dir, "bin/docker"), `#!/usr/bin/env node
const fs = require("node:fs");
const args = process.argv.slice(2);
fs.appendFileSync(process.env.MOCK_DOCKER_LOG, JSON.stringify(args) + "\\n");
if (args[0] === "image" && process.env.MOCK_MISSING === "true") process.exit(1);
if (args[0] === "image") console.log("sha256:fixture");
if (args[0] === "inspect") console.log(process.env.MOCK_UNHEALTHY === "true" ? "unhealthy" : "healthy");
if (args[0] === "run" && args.includes("shahab-ci:local-v1")) process.exit(Number(process.env.MOCK_CHECK_EXIT));
`, { mode: 0o755 });
  const result = spawnSync("bash", ["scripts/ci/run-local-container.sh"], {
    encoding: "utf8",
    env: {
      ...process.env, PATH: path.join(dir, "bin") + path.delimiter + process.env.PATH,
      GITHUB_WORKSPACE: path.join(dir, "workspace"), RUNNER_TEMP: path.join(dir, "temp"),
      RUNNER_TOOL_CACHE: path.join(dir, "cache"), SHAHAB_CI_COMMANDS: "echo verification",
      SHAHAB_CI_DATABASE: database, SHAHAB_CI_PYTHON_PROFILE: profile, MOCK_DOCKER_LOG: log,
      GITHUB_RUN_ID: "123", GITHUB_RUN_ATTEMPT: "2", GITHUB_JOB: "verification",
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
  assert.deepEqual(calls, [["image", "inspect", "--format", "{{.Id}}", "shahab-ci:local-v1"]]);
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
  assert.ok(job.includes("SHAHAB_CI_DATABASE"), "owned database identity must reach the isolated scheduler");
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

test("TERM interrupts a running check and triggers cleanup before it finishes", { timeout: 10000 }, async () => {
  const dir = mkdtempSync(path.join(tmpdir(), "shahab-ci-cancel-"));
  for (const name of ["bin", "temp", "cache", "workspace"]) mkdirSync(path.join(dir, name));
  const log = path.join(dir, "docker.jsonl");
  const pidFile = path.join(dir, "check.pid");
  writeFileSync(path.join(dir, "bin/docker"), `#!/usr/bin/env node
const fs = require("node:fs");
const args = process.argv.slice(2);
fs.appendFileSync(process.env.MOCK_DOCKER_LOG, JSON.stringify(args) + "\\n");
if (args[0] === "run") {
  fs.writeFileSync(process.env.MOCK_CHILD_PID, String(process.pid));
  setInterval(() => {}, 1000);
}
if (args[0] === "rm" && args.at(-1).endsWith("-checks")) {
  try { process.kill(Number(fs.readFileSync(process.env.MOCK_CHILD_PID, "utf8")), "SIGTERM"); } catch {}
}
`, { mode: 0o755 });
  const child = spawn("bash", ["scripts/ci/run-local-container.sh"], {
    stdio: "ignore",
    env: { ...process.env, PATH: path.join(dir, "bin") + path.delimiter + process.env.PATH,
      GITHUB_WORKSPACE: path.join(dir, "workspace"), RUNNER_TEMP: path.join(dir, "temp"),
      RUNNER_TOOL_CACHE: path.join(dir, "cache"), SHAHAB_CI_COMMANDS: "echo verification", SHAHAB_CI_DATABASE: "",
      GITHUB_RUN_ID: "123", GITHUB_RUN_ATTEMPT: "2", GITHUB_JOB: "verification",
      MOCK_DOCKER_LOG: log, MOCK_CHILD_PID: pidFile },
  });
  const exited = new Promise(resolve => child.on("exit", (code, signal) => resolve({ code, signal })));
  let pid;
  try {
    for (let attempt = 0; attempt < 100; attempt++) {
      try { pid = Number(readFileSync(pidFile, "utf8")); break; } catch {}
      await new Promise(resolve => setTimeout(resolve, 20));
    }
    assert.ok(pid, "verification process must be running before cancellation");
    child.kill("SIGTERM");
    const result = await Promise.race([exited, new Promise((_, reject) => {
      const timer = setTimeout(() => reject(new Error("cancellation did not clean up promptly")), 3000);
      timer.unref();
    })]);
    assert.equal(result.code, 143);
    const calls = readFileSync(log, "utf8").trim().split("\n").map(JSON.parse);
    assert.ok(calls.some(args => args[0] === "rm" && args.at(-1).endsWith("-checks")));
    assert.ok(calls.some(args => args[0] === "network" && args[1] === "rm"));
  } finally {
    child.kill("SIGKILL");
    if (pid) { try { process.kill(pid, "SIGKILL"); } catch {} }
    rmSync(dir, { recursive: true, force: true });
  }
});

test("fallback cleanup selects only the exact workflow attempt and job label", () => {
  const dir = mkdtempSync(path.join(tmpdir(), "shahab-ci-recovery-"));
  const log = path.join(dir, "docker.jsonl");
  writeFileSync(path.join(dir, "docker"), `#!/usr/bin/env node
const fs = require("node:fs");
const args = process.argv.slice(2);
fs.appendFileSync(process.env.MOCK_DOCKER_LOG, JSON.stringify(args) + "\\n");
if (args[0] === "ps") console.log("111111111111\\n222222222222");
if (args[0] === "network" && args[1] === "ls") console.log("333333333333");
`, { mode: 0o755 });
  try {
    const result = spawnSync("bash", ["scripts/ci/cleanup-local-container.sh"], { encoding: "utf8",
      env: { ...process.env, PATH: dir + path.delimiter + process.env.PATH, MOCK_DOCKER_LOG: log,
        GITHUB_RUN_ID: "123", GITHUB_RUN_ATTEMPT: "2", GITHUB_JOB: "verification" } });
    assert.equal(result.status, 0, result.stderr);
    const calls = readFileSync(log, "utf8").trim().split("\n").map(JSON.parse);
    for (const args of calls.filter(args => args.includes("--filter"))) {
      assert.equal(args[args.indexOf("--filter") + 1], "label=shahab.ci.owner=123-2-verification");
    }
    assert.deepEqual(calls.find(args => args[0] === "rm"), ["rm", "-f", "-v", "111111111111", "222222222222"]);
    assert.deepEqual(calls.at(-1), ["network", "rm", "333333333333"]);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});


test("Python profile and immutable image identity reach the job container", () => {
  const { result, calls } = run({ profile: "security" });
  assert.equal(result.status, 0, result.stderr);
  const job = calls.find(args => args[0] === "run" && args.includes("shahab-ci:local-v1"));
  assert.ok(job.includes("SHAHAB_CI_PYTHON_PROFILE"));
  assert.ok(job.includes("SHAHAB_CI_IMAGE_ID=sha256:fixture"));
});

test("unsupported Python profile is rejected before Docker resources are created", () => {
  const { result, calls } = run({ profile: "unknown" });
  assert.equal(result.status, 2);
  assert.deepEqual(calls, []);
});

test("cache diagnostic separates fill from a warm single-test database probe", () => {
  const dir = mkdtempSync(path.join(tmpdir(), "shahab-ci-probe-"));
  const log = path.join(dir, "timeouts.jsonl");
  for (const name of ["bin", ".git", "scripts/ci"]) mkdirSync(path.join(dir, name), { recursive: true });
  writeFileSync(path.join(dir, "scripts/ci/cleanup-local-container.sh"),
    readFileSync("scripts/ci/cleanup-local-container.sh", "utf8"));
  writeFileSync(path.join(dir, "bin/git"), "#!/bin/sh\nprintf '%s\\n' \"$MOCK_ROOT\"\n", { mode: 0o755 });
  writeFileSync(path.join(dir, "bin/docker"), "#!/bin/sh\nexit 0\n", { mode: 0o755 });
  writeFileSync(path.join(dir, "bin/timeout"), `#!/usr/bin/env node
const fs = require("node:fs");
fs.appendFileSync(process.env.MOCK_LOG, JSON.stringify({
  args: process.argv.slice(2), job: process.env.GITHUB_JOB,
  profile: process.env.SHAHAB_CI_PYTHON_PROFILE, database: process.env.SHAHAB_CI_DATABASE,
  commands: process.env.SHAHAB_CI_COMMANDS
}) + "\\n");
if (process.env.GITHUB_JOB === "cancel-probe") {
  console.log("DIAGNOSTIC_CANCEL_READY");
  process.exit(124);
}
`, { mode: 0o755 });
  try {
    const result = spawnSync("bash", [path.resolve("scripts/ci/diagnose-local-postgres.sh"), "--cache"], {
      encoding: "utf8", env: { ...process.env, PATH: path.join(dir, "bin") + path.delimiter + process.env.PATH,
        MOCK_ROOT: dir, MOCK_LOG: log, SHAHAB_DIAGNOSTIC_CACHE: path.join(dir, "cache") },
    });
    assert.equal(result.status, 0, result.stderr);
    const calls = readFileSync(log, "utf8").trim().split("\n").map(JSON.parse);
    assert.equal(calls.length, 3);
    assert.deepEqual(calls.map(call => call.job), ["cancel-probe", "python-cache-fill", "postgres-cached-probe"]);
    assert.deepEqual(calls.map(call => call.profile), ["", "project", "project"]);
    assert.deepEqual(calls.map(call => call.database), ["", "", "shahab_test"]);
    assert.equal(calls[1].commands, "python -m pip check");
    assert.equal(calls[2].commands, "PYTHONPATH=. python -u scripts/ci/profile-postgres-test.py");
    assert.ok(calls[1].args.includes("180s"));
    assert.ok(calls[2].args.includes("120s"));
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test("private checkout preserves source bytes and exports evidence even when verification fails", () => {
  const dir = mkdtempSync(path.join(tmpdir(), "shahab-ci-storage-"));
  const source = path.join(dir, "input");
  const workspace = path.join(dir, "workspace");
  const evidence = path.join(dir, "evidence");
  for (const name of [source, workspace, evidence, path.join(source, "node_modules"), path.join(source, "test-results")]) {
    mkdirSync(name, { recursive: true });
  }
  assert.equal(spawnSync("git", ["init", "--quiet", source]).status, 0);
  writeFileSync(path.join(source, "source.txt"), "exact source bytes\n");
  writeFileSync(path.join(source, "node_modules/stale"), "do not reuse dependencies");
  writeFileSync(path.join(source, "test-results/stale"), "do not reuse results");
  const script = readFileSync("scripts/ci/run-local-container.sh", "utf8");
  const bootstrap = script.match(/<<'BOOTSTRAP'\n([\s\S]*?)\nBOOTSTRAP/)[1].split('if [[ -n "${SHAHAB_CI_PYTHON_PROFILE:-}" ]]')[0]
    .replaceAll("/ci-source", source).replaceAll("/workspace", workspace).replaceAll("/ci-evidence", evidence);
  try {
    const result = spawnSync("bash", ["-c", bootstrap + '\nmkdir -p test-results\nprintf synthetic-evidence > test-results/result.txt\nexit 23\n'], {
      cwd: workspace, encoding: "utf8", env: { ...process.env, HOME: path.join(dir, "home"), GITHUB_WORKSPACE: workspace },
    });
    assert.equal(result.status, 23, result.stderr);
    assert.equal(readFileSync(path.join(workspace, "source.txt"), "utf8"), "exact source bytes\n");
    assert.equal(readFileSync(path.join(evidence, "result.txt"), "utf8"), "synthetic-evidence");
    assert.equal(readFileSync(path.join(source, "test-results/stale"), "utf8"), "do not reuse results");
    assert.ok(!existsSync(path.join(workspace, "node_modules/stale")));
    assert.ok(!existsSync(path.join(workspace, "test-results/stale")));
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test("in-memory filesystems belong only to disposable job and database containers", () => {
  const { result, calls } = run({ database: "shahab_test" });
  assert.equal(result.status, 0, result.stderr);
  const runs = calls.filter(args => args[0] === "run");
  const job = runs.find(args => args.includes("shahab-ci:local-v1"));
  const database = runs.find(args => args.includes("postgres:16-alpine"));
  assert.ok(job.some(arg => arg.startsWith("/workspace:rw,exec,nosuid,nodev,size=512m,uid=")));
  assert.ok(job.includes("/tmp:rw,exec,nosuid,nodev,size=1g,mode=1777"));
  assert.ok(job.some(arg => arg.endsWith("target=/ci-source,readonly")));
  assert.ok(job.some(arg => arg.endsWith("/test-results,target=/ci-evidence")));
  assert.ok(database.includes("/var/lib/postgresql/data:rw,nosuid,nodev,size=512m"));
  assert.ok(!database.includes("-c"));
});
