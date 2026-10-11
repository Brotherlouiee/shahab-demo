"""Pure, explicit permission matrix for internal data operations.

No role inherits another role and there is no wildcard administrator. Adding
an operation requires an explicit reviewed entry and denial/allowance tests.
This module reads neither HTTP payloads nor database/customer profile fields.
"""

from enum import StrEnum
from types import MappingProxyType


class Role(StrEnum):
    ANONYMOUS = "anonymous"
    USER = "user"
    SUPPORT = "support"
    DATA_EDITOR = "data-editor"
    ADMIN = "admin"
    SERVICE = "service"


class Permission(StrEnum):
    IMPORT = "data.import"
    REVIEW = "data.review"
    APPROVE = "data.approve"
    PUBLISH = "data.publish"
    ROLLBACK = "data.rollback"
    CONFIG_EDIT = "config.edit"
    CONFIG_APPROVE = "config.approve"


ROLE_PERMISSIONS = MappingProxyType(
    {
        Role.ANONYMOUS: frozenset(),
        Role.USER: frozenset(),
        Role.SUPPORT: frozenset(),
        Role.DATA_EDITOR: frozenset({Permission.IMPORT, Permission.REVIEW, Permission.CONFIG_EDIT}),
        Role.ADMIN: frozenset({Permission.APPROVE, Permission.PUBLISH, Permission.ROLLBACK, Permission.CONFIG_APPROVE}),
        Role.SERVICE: frozenset({Permission.IMPORT}),
    }
)


def permits(roles: frozenset[Role], permission: Permission) -> bool:
    """Fail closed on unknown/raw values, including mixed known and unknown roles."""
    if not isinstance(permission, Permission) or any(not isinstance(role, Role) for role in roles):
        return False
    return any(permission in ROLE_PERMISSIONS[role] for role in roles)
