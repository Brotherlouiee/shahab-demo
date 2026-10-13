"""Small opt-in security smoke against an explicitly authorized HTTPS test deployment.

Read-only negative checks only. Never follow redirects, send credentials,
enumerate, stress, or scan any host without the owner-provided allowlisted URL.
This script is not a substitute for full staging DAST.
"""

from __future__ import annotations

import argparse
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request


def checked_base(url: str) -> str:
    value = urllib.parse.urlsplit(url)
    if (
        value.scheme != "https"
        or not value.hostname
        or value.username is not None
        or value.password is not None
        or value.query
        or value.fragment
        or value.path not in {"", "/"}
        or value.port == 0
    ):
        raise ValueError("Only an explicit HTTPS origin without credentials, path or query is allowed")
    return url.rstrip("/")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def verify(base: str) -> list[str]:
    origin = checked_base(base)
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        NoRedirect(),
    )
    findings: list[str] = []
    for suffix, expected in (
        ("/api/v1/health/live", 200),
        ("/api/v1/profiles/me", 401),
        ("/api/v1/bookmarks", 401),
        ("/api/v1/does-not-exist", 404),
    ):
        req = urllib.request.Request(origin + suffix, method="GET")
        try:
            response = opener.open(req, timeout=5)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            if response.status != expected:
                findings.append(f"{suffix}: expected {expected}, got {response.status}")
            if response.headers.get("Cache-Control") != "no-store":
                findings.append(f"{suffix}: missing no-store")
            if response.headers.get("X-Content-Type-Options") != "nosniff":
                findings.append(f"{suffix}: missing nosniff")
            if not response.headers.get("Strict-Transport-Security"):
                findings.append(f"{suffix}: missing HSTS")
            if response.headers.get("Access-Control-Allow-Origin") == "*":
                findings.append(f"{suffix}: wildcard CORS")
            response.read(2048)
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Authorized HTTPS-only Shahab read-only DAST smoke")
    parser.add_argument("--authorized-test-origin", required=True, help="Owner-approved HTTPS test origin")
    args = parser.parse_args()
    findings = verify(args.authorized_test_origin)
    print(json.dumps({"status": "failed" if findings else "passed", "findings": findings}))
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
