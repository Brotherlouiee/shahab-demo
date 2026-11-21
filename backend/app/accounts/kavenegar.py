"""Kavenegar Lookup delivery and challenge-bound proof, with no raw OTP storage.

The random opaque challenge is a nonce. HMAC-SHA256 with a separate, stable
server secret derives its six-digit code. Only the existing challenge digest is
stored; reading that database or knowing a challenge does not enable offline
six-digit guessing without the server secret. Workers share the configured key,
not Python memory. Expiry, attempts and consumption remain in account access.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections.abc import Callable
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from backend.app.accounts.access import AccessFailure

LookupTransport = Callable[[str, dict[str, str], float], object]
MAX_RESPONSE_BYTES = 65536


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        # API keys occur in the path; never forward them or the body elsewhere.
        raise AccessFailure(503)


def post_lookup(key: str, parameters: dict[str, str], timeout: float) -> object:
    """One bounded HTTPS POST; no retries, redirects, ambient proxies or logging."""
    request = Request(
        f"https://api.kavenegar.com/v1/{key}/verify/lookup.json",
        data=urlencode(parameters).encode("ascii"),
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        method="POST",
    )
    # Default HTTPSHandler validates certificates. Fixed host/path and disabled
    # proxies prevent an environment-supplied endpoint from receiving secrets.
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    with opener.open(request, timeout=timeout) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
        if response.status != 200 or len(body) > MAX_RESPONSE_BYTES:
            raise AccessFailure(503)
    return json.loads(body)


class KavenegarOtpProvider:
    """Deliver the locally derived token; provider acceptance is not delivery proof."""

    challenge_prefix = "sms1."
    requires_persistence = True

    def __init__(
        self,
        api_key: str,
        template: str,
        code_secret: str,
        timeout: float = 5.0,
        transport: LookupTransport = post_lookup,
    ) -> None:
        # URL path cannot be influenced by malformed environment credentials.
        if (
            re.fullmatch(r"[A-Za-z0-9]{16,256}", api_key) is None
            or re.fullmatch(r"[A-Za-z0-9]{1,100}", template) is None
            or len(code_secret) < 32
            or not 0 < timeout <= 10
        ):
            raise ValueError("Invalid OTP provider configuration.")
        self._api_key = api_key
        self._template = template
        self._code_secret = code_secret.encode()
        self._timeout = timeout
        self._transport = transport

    def _code(self, challenge_id: str) -> str:
        proof = hmac.new(self._code_secret, ("shahab-otp-v1:" + challenge_id).encode(), hashlib.sha256).digest()
        return f"{int.from_bytes(proof, 'big') % 1000000:06d}"

    def send(self, phone: str, challenge_id: str) -> None:
        """Raise only a safe unavailable error; never expose upstream text/URL."""
        try:
            if not self._valid_challenge(challenge_id) or re.fullmatch(r"09[0-9]{9}", phone) is None:
                raise AccessFailure(503)
            payload = self._transport(
                self._api_key,
                {"receptor": phone, "token": self._code(challenge_id), "template": self._template, "type": "sms"},
                self._timeout,
            )
            if not isinstance(payload, dict):
                raise AccessFailure(503)
            result, entries = payload.get("return"), payload.get("entries")
            if not isinstance(result, dict) or type(result.get("status")) is not int or result["status"] != 200:
                raise AccessFailure(503)
            if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
                raise AccessFailure(503)
            entry = entries[0]
            if (
                type(entry.get("messageid")) is not int
                or entry["messageid"] <= 0
                or type(entry.get("status")) is not int
                or entry["status"] not in {1, 2, 4, 5, 10}
            ):
                raise AccessFailure(503)
        except Exception:
            # Even network exception messages can contain the key-bearing URL.
            # No raw response/message/receptor is retained or returned.
            raise AccessFailure(503) from None

    def _valid_challenge(self, challenge_id: str) -> bool:
        return re.fullmatch(r"sms1\.[A-Za-z0-9_-]{43}", challenge_id) is not None

    def verify(self, code: str, challenge_id: str) -> bool:
        if not self._valid_challenge(challenge_id):
            return False
        normalized = code.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
        return hmac.compare_digest(normalized.encode(), self._code(challenge_id).encode())
