"""Exercise the VM topology in CI, with already-built candidates and synthetic DB.

This never deploys, rebuilds, publishes source data, sends SMS, or touches an owner
project/volume. The override is test-only; the VM file retains published digests.
"""

import argparse
import json
import os
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from http.cookies import SimpleCookie
from pathlib import Path

from publish import NoRedirect
from test_vm_compose import ROOT, compose_binary, synthetic_environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-image", required=True)
    parser.add_argument("--web-image", required=True)
    args = parser.parse_args()
    project = "shahab-vm-test-" + uuid.uuid4().hex[:12]
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix=project) as directory:
        folder = Path(directory)
        folder.chmod(0o755)
        tls = folder / "tls"
        tls.mkdir(mode=0o755)
        env = synthetic_environment(tls)
        env.update({"SHAHAB_HTTP_PORT": "0", "SHAHAB_HTTPS_PORT": "0"})
        envfile = folder / "test.env"
        envfile.write_text("".join(f"{key}={value}\n" for key, value in env.items()))
        envfile.chmod(0o600)
        override = folder / "override.json"
        override.write_text(
            json.dumps(
                {
                    "services": {
                        "api": {"image": args.api_image, "pull_policy": "never"},
                        "migrate": {"image": args.api_image, "pull_policy": "never"},
                        "frontend": {"image": args.web_image, "pull_policy": "never"},
                    }
                }
            )
        )
        base = [
            *compose_binary(),
            "--project-name",
            project,
            "--env-file",
            str(envfile),
            "-f",
            str(ROOT / "docker-compose.prod.yml"),
            "-f",
            str(override),
        ]

        def run(*command, data=None, check=True):
            result = subprocess.run(
                command,
                cwd=ROOT,
                env={**os.environ, **env},
                input=data,
                text=True,
                capture_output=True,
                timeout=180,
                check=False,
            )
            if check and result.returncode:
                # Inputs here are synthetic, but never expose environment or SQL
                # bodies through generic exception dumps in a public job.
                detail = result.stderr[-3000:]
                for secret in (
                    env["POSTGRES_PASSWORD"],
                    "synthetic-vm-api",
                    env["SHAHAB_READINESS_TOKEN"],
                    env["SHAHAB_DATABASE_URL"],
                    env["SHAHAB_MIGRATION_DATABASE_URL"],
                ):
                    detail = detail.replace(secret, "[redacted]")
                raise ValueError("VM fixture command failed: " + " ".join(command[-6:]) + "\n" + detail)
            return result.stdout

        def compose(*command, data=None):
            return run(*base, *command, data=data)

        run(
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-days",
            "1",
            "-keyout",
            str(tls / "privkey.pem"),
            "-out",
            str(tls / "fullchain.pem"),
            "-subj",
            "/CN=vm.example.invalid",
            "-addext",
            "subjectAltName=DNS:vm.example.invalid,IP:127.0.0.1",
        )
        # ONLY the disposable synthetic certificate fixture uses world-readable
        # files. Real host keys require restricted UID/GID101 access per runbook.
        (tls / "privkey.pem").chmod(0o644)
        try:
            compose("pull", "postgres", "redis")
            compose("up", "-d", "--no-build", "--wait", "--wait-timeout", "60", "postgres", "redis")
            compose("--profile", "maintenance", "run", "--rm", "migrate")
            compose(
                "exec",
                "-T",
                "postgres",
                "psql",
                "-U",
                "shahab_migrator",
                "-d",
                "shahab",
                "-v",
                "ON_ERROR_STOP=1",
                data=(
                    "CREATE ROLE shahab_api LOGIN PASSWORD 'synthetic-vm-api' NOSUPERUSER "
                    "NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;\n"
                    + (ROOT / "deploy/vm/api-grants.sql").read_text()
                ),
            )
            denied = compose(
                "exec",
                "-T",
                "postgres",
                "psql",
                "-U",
                "shahab_migrator",
                "-d",
                "shahab",
                "-Atc",
                "SELECT has_table_privilege('shahab_api','operations_imports','SELECT'), "
                "has_table_privilege('shahab_api','loan_products','UPDATE'), "
                "has_schema_privilege('shahab_api','public','CREATE')",
            )
            assert denied.strip() == "f|f|f", "API role must not be operator/catalogue writer/schema owner"
            compose("up", "-d", "--no-build", "--wait", "--wait-timeout", "60", "api", "frontend")
            address = compose("port", "frontend", "8443").strip()
            assert address.startswith("127.0.0.1:"), "Fixture must bind loopback only"
            port = address.rsplit(":", 1)[1]
            context = ssl.create_default_context(cafile=str(tls / "fullchain.pem"))
            opener = urllib.request.build_opener(
                NoRedirect, urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=context)
            )
            host = "vm.example.invalid:" + port
            origin = "https://" + host

            def request(path, *, data=None, extra=None, method=None):
                headers = {"Host": host, **(extra or {})}
                req = urllib.request.Request("https://" + address + path, data=data, headers=headers, method=method)
                try:
                    response = opener.open(req, timeout=5)
                except urllib.error.HTTPError as error:
                    response = error
                with response:
                    return response.status, response.headers, response.read()

            root = request("/")
            assert root[0] == 200 and b"<!doctype html>" in root[2].lower()
            assert request("/question/3")[2] == root[2]
            assert request("/assets/missing.js")[0] == 404
            assert request("/api/v1/health/live")[0] == 200
            assert request("/api/v1/profiles/me")[0] == 401
            assert request("/api/v1/openapi.json")[0] == 404, "Production schema must not be exposed"
            status, headers, raw = request(
                "/api/v1/questionnaire/sessions", data=b"", extra={"Origin": origin, "X-Forwarded-Proto": "http"}
            )
            assert status == 201, "HTTPS same-origin mutation must survive proxy with spoofed headers discarded"
            assert headers["Cache-Control"] == "no-store"
            cookie = headers["Set-Cookie"]
            assert all(flag in cookie for flag in ("Secure", "HttpOnly", "SameSite=lax"))
            parsed = SimpleCookie()
            parsed.load(cookie)
            cookie_header = "; ".join(f"{key}={value.value}" for key, value in parsed.items())
            session_id = json.loads(raw)["sessionId"]
            path = "/api/v1/questionnaire/sessions/" + session_id
            assert request(path, extra={"Cookie": cookie_header})[0] == 200
            assert request(path)[0] == 403
            assert (
                request("/api/v1/questionnaire/sessions", data=b"", extra={"Origin": "https://other.example.invalid"})[
                    0
                ]
                == 403
            )
            assert (
                request(
                    "/api/v1/account-access/request",
                    data=b'{"phone":"09012340931"}',
                    extra={"Content-Type": "application/json", "Origin": origin},
                )[0]
                == 503
            )
            # A real API restart uses the same named database volume and restores
            # the synthetic session; no source import, snapshot or DB reset.
            compose("restart", "api")
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                try:
                    if request("/api/v1/health/live")[0] == 200:
                        break
                except (OSError, urllib.error.URLError):
                    pass
                time.sleep(0.25)
            assert request(path, extra={"Cookie": cookie_header})[0] == 200
            result = {
                "status": "passed",
                "sourceSha": run("git", "rev-parse", "HEAD").strip(),
                "images": [args.api_image, args.web_image],
                "buildOnVm": False,
                "deployed": False,
                "candidateImagesInCI": True,
                "runtimeRole": "non-owner-limited",
                "tlsVerified": True,
                "sameOriginMutation": "passed",
                "forgedForwardingIgnored": True,
                "secureProofCookie": True,
                "wrongOriginDenied": True,
                "restartPersistence": "passed",
                "realSms": False,
                "elapsedSeconds": round(time.monotonic() - started, 3),
            }
            output = ROOT / "test-results/vm-compose.json"
            output.parent.mkdir(exist_ok=True)
            output.write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result))
        except Exception:
            logs = run(*base, "logs", "--no-color", "--tail", "25", "api", "frontend", check=False)
            for secret in (
                env["POSTGRES_PASSWORD"],
                "synthetic-vm-api",
                env["SHAHAB_READINESS_TOKEN"],
                env["SHAHAB_DATABASE_URL"],
                env["SHAHAB_MIGRATION_DATABASE_URL"],
            ):
                logs = logs.replace(secret, "[redacted]")
            print(logs[-6000:])  # Only synthetic CI services, bounded and no real credentials.
            raise
        finally:
            # Only this randomly named CI project. No down -v or volume reset.
            compose("down", "--remove-orphans")


if __name__ == "__main__":
    main()
