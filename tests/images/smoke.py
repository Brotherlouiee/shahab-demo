"""Build/run contract for A.1/A.2; disposable resources only, never push or deploy.

Requires Docker, OpenSSL and an independently built dist/ from this same checkout.
No database, owner volume, registry credential, source publication or SMS is used.
"""

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def command(*args, capture=True):
    return subprocess.run(args, cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE if capture else None).stdout


def request(origin, path="/", data=None, headers=None):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(origin + path, data=data, headers=headers or {})
    try:
        response = opener.open(req, timeout=5)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, response.headers, response.read(8 * 1024 * 1024)


def wait_ready(origin, path="/"):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            if request(origin, path)[0] == 200:
                return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(0.2)
    raise AssertionError("Container did not become ready within 30 seconds")


def fingerprints(directory):
    return {
        p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in directory.rglob("*")
        if p.is_file()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-image")
    parser.add_argument("--web-image")
    args = parser.parse_args()
    if bool(args.api_image) != bool(args.web_image):
        parser.error("Supply both externally built image references or neither")
    external = bool(args.api_image)
    identifier = "shahab-image-" + uuid.uuid4().hex[:12]
    network = identifier + "-network"
    images = [args.api_image, args.web_image] if external else [identifier + "-api", identifier + "-web"]
    containers = []
    network_created = False
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix=identifier) as temporary:
        folder = Path(temporary)
        folder.chmod(0o755)

        def start(suffix, image, port, *options, arguments=()):
            name = identifier + "-" + suffix
            containers.append(name)  # Also clean up a partially created container.
            command(
                "docker",
                "run",
                "-d",
                "--name",
                name,
                "--network",
                network,
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "-p",
                f"127.0.0.1::{port}",
                *options,
                image,
                *arguments,
            )
            address = command("docker", "port", name, f"{port}/tcp").strip()
            assert address.startswith("127.0.0.1:"), "Smoke port must be loopback-only"
            return name, "http://" + address

        try:
            assert (ROOT / "dist/index.html").is_file(), "Build independent dist reference first"
            for dockerfile, image in zip(("Dockerfile", "frontend/Dockerfile"), images, strict=True):
                if not external:
                    command("docker", "build", "-f", dockerfile, "-t", image, ".", capture=False)
                user = command("docker", "image", "inspect", "--format", "{{.Config.User}}", image).strip()
                assert user and user.split(":")[0] not in {"0", "root"}, "Image must declare non-root"
                assert (
                    command("docker", "run", "--rm", "--network", "none", "--entrypoint", "id", image, "-u").strip()
                    != "0"
                )
            # A dedicated bridge permits loopback-only host probes. Docker's
            # --internal network deliberately does not publish those host ports.
            command("docker", "network", "create", network)
            network_created = True
            api_name, api = start(
                "api",
                images[0],
                8000,
                "-e",
                "SHAHAB_ENVIRONMENT=staging",
                "-e",
                "SHAHAB_PROFILE_MOCK_OTP_ENABLED=false",
                "-e",
                "CI=true",
            )
            wait_ready(api, "/api/v1/health/live")
            assert json.loads(request(api, "/api/v1/health/live")[2]) == {"status": "ok"}
            assert request(api, "/api/v1/loans/not-a-real-loan")[0] == 503
            assert request(api, "/api/v1/profiles/me")[0] == 401
            assert (
                request(
                    api,
                    "/api/v1/account-access/request",
                    b'{"phone":"09012340931"}',
                    {"Content-Type": "application/json"},
                )[0]
                == 503
            )
            command(
                "docker",
                "exec",
                api_name,
                "sh",
                "-c",
                "test ! -e /app/.env && test ! -d /app/.agents && test ! -d /app/backend/tests",
            )

            web_name, web = start("web", images[1], 8080)
            wait_ready(web)
            expected = (ROOT / "dist/index.html").read_bytes()
            for route in ("/", "/question/3", "/personal-info", "/loan-details?loanId=synthetic"):
                status, headers, body = request(web, route)
                assert status == 200, f"SPA route {route} returned HTTP {status}"
                assert "text/html" in headers.get("Content-Type", ""), (
                    f"SPA route {route} returned Content-Type {headers.get('Content-Type')!r}"
                )
                assert body == expected, (
                    f"SPA route {route} did not serve the built index.html "
                    f"(response_bytes={len(body)}, expected_bytes={len(expected)}, "
                    f"response_sha256={hashlib.sha256(body).hexdigest()}, "
                    f"expected_sha256={hashlib.sha256(expected).hexdigest()})"
                )
            for suffix in ("/api/v1/health/live", "/api/v1/not-found"):
                status, headers, body = request(web, suffix)
                assert status == 503 and headers["Cache-Control"] == "no-store"
                assert (
                    "application/json" in headers["Content-Type"] and json.loads(body)["error"] == "api_not_configured"
                )
            assert request(web, "/assets/missing.js")[0] == 404
            asset = next((ROOT / "dist/assets").glob("*.js"))
            status, headers, body = request(web, "/assets/" + urllib.parse.quote(asset.name))
            assert status == 200 and body == asset.read_bytes() and "javascript" in headers["Content-Type"]
            copied = folder / "static"
            copied.mkdir()
            command("docker", "cp", web_name + ":/srv/shahab/.", str(copied))
            assert fingerprints(copied) == fingerprints(ROOT / "dist"), (
                "Image static files differ from independent build"
            )

            # Self-signed fixture CA/key live only in this temporary directory.
            command(
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-days",
                "1",
                "-keyout",
                str(folder / "key.pem"),
                "-out",
                str(folder / "cert.pem"),
                "-subj",
                "/CN=upstream",
                "-addext",
                "subjectAltName=DNS:upstream",
            )
            (folder / "key.pem").chmod(0o644)  # Ephemeral synthetic key for this disposable non-root fixture.
            (folder / "tls_fixture.py").write_bytes((ROOT / "tests/images/tls_fixture.py").read_bytes())
            fixture, _ = start(
                "upstream",
                images[0],
                8443,
                "--network-alias",
                "upstream",
                "-v",
                f"{folder}:/fixture:ro",
                "--entrypoint",
                "python",
                arguments=("/fixture/tls_fixture.py",),
            )
            template = (ROOT / "frontend/nginx/api-https.conf.example").read_text()
            proxy = template.replace("https://api.example.invalid", "https://upstream:8443").replace(
                "proxy_ssl_name api.example.invalid", "proxy_ssl_name upstream"
            )
            trusted = folder / "trusted.conf"
            trusted.write_text(proxy.replace("/etc/ssl/certs/ca-certificates.crt", "/etc/nginx/test-ca.pem"))
            _, proxied = start(
                "proxy",
                images[1],
                8080,
                "-v",
                f"{trusted}:/etc/nginx/shahab-api.conf:ro",
                "-v",
                f"{folder / 'cert.pem'}:/etc/nginx/test-ca.pem:ro",
            )
            wait_ready(proxied)
            # Retry only readiness of the isolated TLS fixture, not a product request.
            wait_ready(proxied, "/api/v1/fixture")
            status, headers, body = request(
                proxied,
                "/api/v1/fixture?synthetic=1",
                b"synthetic-body",
                {
                    "Origin": proxied,
                    "Cookie": "fixture=synthetic",
                    "X-Forwarded-Proto": "forged",
                    "X-Forwarded-For": "forged",
                    "Content-Type": "text/plain",
                },
            )
            value = json.loads(body)
            assert status == 200 and value["method"] == "POST" and value["path"] == "/api/v1/fixture?synthetic=1"
            assert value["host"] == proxied.removeprefix("http://") and value["origin"] == proxied
            assert value["scheme"] == "http" and value["forwarded"] != "forged"
            assert value["body"] == "synthetic-body" and value["cookie"] == "fixture=synthetic"
            assert headers["Set-Cookie"] == "fixture=synthetic; Secure; HttpOnly; SameSite=Lax; Path=/api/v1"
            assert headers["Cache-Control"] == "no-store"
            untrusted = folder / "untrusted.conf"
            untrusted.write_text(proxy)
            _, denied = start("untrusted", images[1], 8080, "-v", f"{untrusted}:/etc/nginx/shahab-api.conf:ro")
            wait_ready(denied)
            assert request(denied, "/api/v1/fixture")[0] == 502, "Untrusted TLS upstream must be rejected"

            evidence = {
                "status": "passed",
                "sourceSha": command("git", "rev-parse", "HEAD").strip(),
                "imageIds": [command("docker", "image", "inspect", "--format", "{{.Id}}", i).strip() for i in images],
                "staticFileCount": len(fingerprints(copied)),
                "nonRootImages": 2,
                "httpsProxyFixture": "passed",
                "untrustedTlsRejected": True,
                "elapsedSeconds": round(time.monotonic() - started, 3),
                "published": False,
                "deployed": False,
            }
            output = ROOT / "test-results/image-smoke.json"
            output.parent.mkdir(exist_ok=True)
            output.write_text(json.dumps(evidence, indent=2) + "\n")
            print(json.dumps(evidence))
        finally:
            for name in reversed(containers):
                subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if network_created:
                command("docker", "network", "rm", network)
            for image in [] if external else images:
                subprocess.run(["docker", "image", "rm", image], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
