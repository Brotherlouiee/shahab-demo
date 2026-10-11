"""HTTPS OAuth token introspection; no local password or MFA simulator.

Only the administrator-configured authority can assert roles/MFA. A fresh
introspection is made at authentication and again by the T01 grant boundary.
Transport/validation failures deny access without leaking credentials or URL.
"""

import base64
import json
import ssl
from collections.abc import Callable
from datetime import UTC, datetime
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener

from pydantic import BaseModel, Field, SecretStr, StrictBool, StrictInt

from backend.app.operations.authorization import (
    IdentityKind,
    OperationsAccessDenied,
    OperationsIdentity,
    RoleGrant,
    utc_now,
)
from backend.app.operations.policy import Role


class AuthorityConfiguration(BaseModel):
    endpoint: str
    issuer: str
    audience: str = Field(min_length=1)
    client_id: str = Field(min_length=1)
    client_secret: SecretStr
    service_client_ids: frozenset[str] = frozenset()
    ca_file: str | None = None


class AuthorityClaims(BaseModel):
    active: StrictBool
    sub: str = Field(min_length=1, max_length=200)
    iss: str
    aud: str | tuple[str, ...]
    exp: StrictInt
    iat: StrictInt
    client_id: str
    amr: tuple[str, ...] = ()
    auth_time: StrictInt | None = None
    roles: frozenset[Role]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise OperationsAccessDenied()


class IntrospectionAuthority:
    """Bound to one opaque credential; no credential/role is accepted in commands."""

    def __init__(
        self, configuration: AuthorityConfiguration, token: SecretStr, clock: Callable[[], datetime] = utc_now
    ) -> None:
        url = urlsplit(configuration.endpoint)
        if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise OperationsAccessDenied()
        credential = token.get_secret_value()
        if not 32 <= len(credential) <= 4096 or any(not 33 <= ord(c) <= 126 for c in credential):
            raise OperationsAccessDenied()
        if not configuration.client_secret.get_secret_value():
            raise OperationsAccessDenied()
        self._configuration, self._token, self._clock = configuration, token, clock
        context = ssl.create_default_context(cafile=configuration.ca_file)
        self._opener = build_opener(ProxyHandler({}), HTTPSHandler(context=context), NoRedirect())

    def _claims(self) -> AuthorityClaims:
        config = self._configuration
        basic = base64.b64encode((config.client_id + ":" + config.client_secret.get_secret_value()).encode()).decode()
        request = Request(
            config.endpoint,
            data=urlencode({"token": self._token.get_secret_value(), "token_type_hint": "access_token"}).encode(),
            headers={
                "Authorization": "Basic " + basic,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with self._opener.open(request, timeout=3) as response:
                if response.status != 200 or response.headers.get_content_type() != "application/json":
                    raise OperationsAccessDenied()
                payload = response.read(16385)
                if len(payload) > 16384:
                    raise OperationsAccessDenied()
            claims = AuthorityClaims.model_validate(json.loads(payload))
            now = int(self._clock().timestamp())
            audience = (claims.aud,) if isinstance(claims.aud, str) else claims.aud
            if (
                not claims.active
                or claims.iss != config.issuer
                or config.audience not in audience
                or not (claims.iat <= now < claims.exp <= claims.iat + 900)
            ):
                raise OperationsAccessDenied()
            if claims.client_id not in config.service_client_ids and (
                "mfa" not in claims.amr or claims.auth_time is None or not now - 300 <= claims.auth_time <= now
            ):
                raise OperationsAccessDenied()
            return claims
        except Exception:
            raise OperationsAccessDenied() from None

    def authenticate(self) -> OperationsIdentity:
        claims = self._claims()
        kind = (
            IdentityKind.SERVICE_CREDENTIAL
            if claims.client_id in self._configuration.service_client_ids
            else (IdentityKind.OPERATOR_MFA)
        )
        return OperationsIdentity(claims.sub, kind, datetime.fromtimestamp(claims.exp, UTC))

    def read_current(self, subject: str) -> RoleGrant | None:
        claims = self._claims()
        if claims.sub != subject:
            return None
        return RoleGrant(subject, claims.roles, datetime.fromtimestamp(claims.exp, UTC))
