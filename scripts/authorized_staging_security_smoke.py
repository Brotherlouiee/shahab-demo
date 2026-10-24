"""Small opt-in security smoke against an explicitly authorized HTTPS test deployment.

Read-only negative checks only. Never follow redirects, send credentials,
enumerate, stress, or scan any host without the owner-provided allowlisted URL.
This script is not a substitute for full staging DAST.
"""

from __future__ import annotations

import argparse
import json
import re
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


def exposure_checks(opener, origin: str) -> list[str]:
    """Two fixed deployment-artifact paths, not a crawler or credential search.

    A Vite SPA can legitimately return its HTML shell for an absent dotfile.
    Recognize that case without printing response bodies or accepting arbitrary
    200 responses. Bounded/inconclusive responses remain findings, never passes.
    """
    findings: list[str] = []
    for suffix in ("/.env", "/.git/config"):
        request = urllib.request.Request(origin + suffix, method="GET")
        try:
            response = opener.open(request, timeout=5)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body = response.read(16385)
            if len(body) > 16384:
                findings.append(f"{suffix}: bounded inspection inconclusive")
                continue
            text = body.decode("utf-8", errors="replace")
            sensitive = re.search(
                r"(?mi)^\s*(?:export\s+)?(?:SHAHAB_[A-Z0-9_]+|POSTGRES_PASSWORD|DATABASE_URL)\s*=",
                text,
            ) or re.search(r'(?mi)^\s*\[(?:core|remote\s+"[^\"]+")\]\s*$', text)
            sensitive = sensitive or re.search(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----", text)
            if sensitive:
                findings.append(f"{suffix}: sensitive artifact signature exposed; body withheld")
            elif response.status in {403, 404}:
                continue
            elif (
                response.status == 200
                and "text/html" in response.headers.get("Content-Type", "").lower()
                and re.search(r"(?i)^\s*(?:<!doctype html[^>]*>\s*)?<html\b", text)
            ):
                continue
            else:
                findings.append(f"{suffix}: unexpected response {response.status}; body withheld")
    return findings


def verify(base: str, include_exposure_checks: bool = False) -> list[str]:
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
    if include_exposure_checks:
        findings.extend(exposure_checks(opener, origin))
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Authorized HTTPS-only Shahab read-only DAST smoke")
    parser.add_argument("--authorized-test-origin", required=True, help="Owner-approved HTTPS test origin")
    parser.add_argument("--include-exposure-checks", action="store_true", help="Also inspect two fixed artifact paths")
    args = parser.parse_args()
    try:
        findings = verify(args.authorized_test_origin, args.include_exposure_checks)
    except (OSError, ValueError, urllib.error.URLError):
        print(json.dumps({"status": "failed", "findings": ["transport_or_input_error; no automatic retry"]}))
        raise SystemExit(1) from None
    print(
        json.dumps(
            {
                "status": "failed" if findings else "passed",
                "findings": findings,
                "requests": 6 if args.include_exposure_checks else 4,
            }
        )
    )
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
