"""Run protected-tool positive HTTP regression in a fresh laptop-only PostgreSQL.

Every invocation gets a new Compose project/volume. The runner stops its own
container, retaining the volume for inspection; it never touches prior projects.
"""

from __future__ import annotations

import os
import secrets
import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "tests/t081-fixture.compose.yml"
ENV_FILE = ROOT / ".env"
PORT = 55432


def local_settings() -> dict[str, str]:
    if not ENV_FILE.is_file():
        raise RuntimeError("local .env is required")
    values = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key] = value
    if values.get("SHAHAB_ENVIRONMENT") != "local":
        raise RuntimeError("only the local environment is allowed")
    if any(not values.get(key) for key in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD")):
        raise RuntimeError("local PostgreSQL configuration is incomplete")
    return values


def run() -> None:
    values = local_settings()
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", PORT))
    project = "shahab-t081-fixture-" + secrets.token_hex(4)
    compose = ["docker", "compose", "-p", project, "-f", str(COMPOSE), "--env-file", str(ENV_FILE)]
    env = os.environ.copy()
    env["SHAHAB_T081_DISPOSABLE_FIXTURE"] = "1"
    env["SHAHAB_TEST_DATABASE_URL"] = "postgresql+psycopg://{}:{}@127.0.0.1:{}/{}".format(
        quote(values["POSTGRES_USER"], safe=""),
        quote(values["POSTGRES_PASSWORD"], safe=""),
        PORT,
        quote(values["POSTGRES_DB"], safe=""),
    )
    if os.name == "nt":
        openssl = Path("C:/Program Files/Git/usr/bin")
        if not (openssl / "openssl.exe").is_file():
            raise RuntimeError("Git for Windows OpenSSL is required for the TLS test fixture")
        env["PATH"] = str(openssl) + os.pathsep + env.get("PATH", "")
    print(f"isolated fixture project: {project}", flush=True)
    attempted_start = False
    try:
        attempted_start = True
        subprocess.run([*compose, "up", "-d", "--wait"], cwd=ROOT, check=True, capture_output=True)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "backend.tests.test_operations_tool_postgresql.OperationsToolPostgreSQLTests."
                "test_protected_fixture_publication_supports_owned_http_journey",
            ],
            cwd=ROOT,
            env=env,
            check=False,
        )
        if result.returncode:
            raise RuntimeError("protected fixture HTTP regression failed")
        print("protected fixture HTTP regression passed; operational MFA and online acceptance remain unverified")
    finally:
        env.pop("SHAHAB_TEST_DATABASE_URL", None)
        if attempted_start:
            subprocess.run([*compose, "stop"], cwd=ROOT, check=False, capture_output=True)
        print(f"only {project} was stopped; its volume was retained for inspection", flush=True)


if __name__ == "__main__":
    try:
        run()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        # Never emit DSNs, command output, tokens, or responses on setup failure.
        print(f"fixture verification stopped: {type(error).__name__}")
        raise SystemExit(1) from None
