"""Transport-independent authorization boundary for future internal use cases.

Identity must come from a trusted internal credential verifier, never from a
request role/header/phone or customer mock OTP. Role grants are freshly resolved
on every check so revocation is effective without restarting a session. This
task deliberately has no operator login endpoint or persistent grant store.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol

from .policy import Permission, Role, permits


class IdentityKind(StrEnum):
    """Only independently verified internal identities qualify for operations."""

    CUSTOMER = "customer"
    MOCK_OTP = "mock-otp"
    OPERATOR_MFA = "operator-mfa"
    SERVICE_CREDENTIAL = "service-credential"


@dataclass(frozen=True)
class OperationsIdentity:
    """Authenticated identity issued by a trusted adapter; deliberately has no roles."""

    subject: str
    kind: IdentityKind
    expires_at: datetime


@dataclass(frozen=True)
class RoleGrant:
    """Current server-owned binding; timestamps are aware UTC instants."""

    subject: str
    roles: frozenset[Role]
    expires_at: datetime


class RoleGrantRepository(Protocol):
    """Trusted source of current grants; revocation is represented by a missing grant."""

    def read_current(self, subject: str) -> RoleGrant | None: ...


class DenyAllRoleGrantRepository:
    """Safe runtime default until a reviewed internal authority is configured."""

    def read_current(self, subject: str) -> RoleGrant | None:
        return None


class OperationsAccessDenied(Exception):
    """Safe denial without actor, credential, grant details or repository state."""

    def __init__(self) -> None:
        super().__init__("Operations access is not allowed.")


class OperationsAuthorityUnavailable(Exception):
    """Distinguish failed authority lookup from a valid but insufficient grant."""

    def __init__(self) -> None:
        super().__init__("Operations authorization is unavailable.")


def utc_now() -> datetime:
    return datetime.now(UTC)


def unexpired(expires_at: datetime, now: datetime) -> bool:
    """Naive/non-date timestamps fail closed instead of inventing a timezone."""
    return isinstance(expires_at, datetime) and expires_at.utcoffset() is not None and expires_at > now


class OperationsAuthorizer:
    """Check authority before a caller starts any operational read or mutation.

    T02 must call require at its use-case boundary. T04 must authenticate the
    incoming credential before constructing OperationsIdentity. Python objects
    themselves are not evidence of authentication or protection of a public API.
    """

    def __init__(
        self,
        grants: RoleGrantRepository | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._grants = grants if grants is not None else DenyAllRoleGrantRepository()
        self._clock = clock

    def require(self, identity: OperationsIdentity | None, permission: Permission) -> str:
        """Return only the verified actor reference; raise safe typed failures."""
        now = self._clock()
        if (
            not isinstance(identity, OperationsIdentity)
            or not identity.subject.strip()
            or not isinstance(identity.kind, IdentityKind)
            or identity.kind not in {IdentityKind.OPERATOR_MFA, IdentityKind.SERVICE_CREDENTIAL}
            or not unexpired(identity.expires_at, now)
            or not isinstance(permission, Permission)
        ):
            raise OperationsAccessDenied()
        try:
            grant = self._grants.read_current(identity.subject)
        except Exception:
            # A broken authority must never fall back to the user's claimed role.
            # Do not propagate repository diagnostics containing credentials.
            raise OperationsAuthorityUnavailable() from None
        if (
            not isinstance(grant, RoleGrant)
            or grant.subject != identity.subject
            or not unexpired(grant.expires_at, now)
            or not isinstance(grant.roles, frozenset)
            or not permits(grant.roles, permission)
        ):
            raise OperationsAccessDenied()
        # Human credentials cannot borrow service grants; service credentials
        # cannot exercise human approval/configuration roles even if misbound.
        if identity.kind is IdentityKind.SERVICE_CREDENTIAL:
            allowed_roles = frozenset({Role.SERVICE}) & grant.roles
        else:
            allowed_roles = grant.roles - {Role.SERVICE}
        if not permits(allowed_roles, permission):
            raise OperationsAccessDenied()
        return identity.subject
