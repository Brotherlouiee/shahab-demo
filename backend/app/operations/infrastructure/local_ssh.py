"""Local SSH operator authority for the private CLI only.

A root-owned policy binds numeric UIDs to explicit roles and is re-read for every
grant check. Single-owner root mode is opt-in and does not claim dual control.
No role, actor or policy path comes from a command or environment.
"""

import json
import os
import stat
from datetime import datetime, timedelta
from pathlib import Path

from backend.app.operations.authorization import (
    IdentityKind,
    OperationsAccessDenied,
    OperationsIdentity,
    RoleGrant,
    unexpired,
    utc_now,
)
from backend.app.operations.policy import Role

POLICY_PATH = Path("/etc/shahab/operations-operators.json")


class LocalSshAuthority:
    def __init__(self, policy_path: Path = POLICY_PATH, *, allow_root_owner: bool = False) -> None:
        self._path = policy_path
        self._allow_root_owner = allow_root_owner

    def _uid(self) -> int:
        if os.name != "posix" or os.getuid() != os.geteuid():
            raise OperationsAccessDenied()
        if os.getuid() == 0:
            if self._allow_root_owner and not os.environ.get("SUDO_UID"):
                return 0
            # A sudo wrapper retains the invoking unprivileged SSH UID.
            original = os.environ.get("SUDO_UID", "")
            if not original.isdecimal() or int(original) <= 0 or not os.environ.get("SUDO_USER"):
                raise OperationsAccessDenied()
            return int(original)
        return os.getuid()

    def _document(self) -> dict:
        try:
            path = self._path.absolute()
            for parent in path.parents:
                info = parent.lstat()
                if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
                    raise OperationsAccessDenied()
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
                    raise OperationsAccessDenied()
                with os.fdopen(fd, "rb", closefd=False) as source:
                    raw = source.read(4097)
                if len(raw) > 4096:
                    raise OperationsAccessDenied()
            finally:
                os.close(fd)
            return json.loads(raw)
        except Exception:
            raise OperationsAccessDenied() from None

    def _binding(self) -> tuple[str, RoleGrant]:
        uid = self._uid()
        try:
            document = self._document()
            if set(document) != {"schemaVersion", "operators", "singleOwner"} or document["schemaVersion"] != 1:
                raise OperationsAccessDenied()
            if type(document["singleOwner"]) is not bool:
                raise OperationsAccessDenied()
            operators = document["operators"]
            if not isinstance(operators, list) or not 1 <= len(operators) <= 16:
                raise OperationsAccessDenied()
            matches = []
            seen = set()
            seen_actors = set()
            for entry in operators:
                if not isinstance(entry, dict) or set(entry) != {"uid", "actor", "roles", "expiresAt"}:
                    raise OperationsAccessDenied()
                operator_uid = entry["uid"]
                if type(operator_uid) is not int or operator_uid < 0 or operator_uid in seen:
                    raise OperationsAccessDenied()
                seen.add(operator_uid)
                actor = entry["actor"]
                if (
                    not isinstance(actor, str)
                    or not 1 <= len(actor) <= 100
                    or not actor.isascii()
                    or not actor.isprintable()
                    or actor in seen_actors
                ):
                    raise OperationsAccessDenied()
                seen_actors.add(actor)
                raw_roles = entry["roles"]
                if not isinstance(raw_roles, list) or not raw_roles or len(raw_roles) > 2:
                    raise OperationsAccessDenied()
                roles = frozenset(Role(item) for item in raw_roles)
                if len(roles) != len(raw_roles) or not roles <= {Role.DATA_EDITOR, Role.ADMIN}:
                    raise OperationsAccessDenied()
                if operator_uid == 0 and (
                    not self._allow_root_owner
                    or not document["singleOwner"]
                    or len(operators) != 1
                    or roles != {Role.DATA_EDITOR, Role.ADMIN}
                ):
                    raise OperationsAccessDenied()
                if operator_uid != 0 and document["singleOwner"]:
                    raise OperationsAccessDenied()
                expiry = datetime.fromisoformat(entry["expiresAt"])
                if operator_uid == uid:
                    matches.append((actor, RoleGrant(actor, roles, expiry)))
            now = utc_now()
            if (
                len(matches) != 1
                or not unexpired(matches[0][1].expires_at, now)
                or matches[0][1].expires_at > now + timedelta(hours=24)
            ):
                raise OperationsAccessDenied()
            return matches[0]
        except Exception:
            raise OperationsAccessDenied() from None

    def authenticate(self) -> OperationsIdentity:
        actor, grant = self._binding()
        return OperationsIdentity(actor, IdentityKind.LOCAL_SSH_OPERATOR, grant.expires_at)

    def read_current(self, subject: str) -> RoleGrant | None:
        actor, grant = self._binding()
        return grant if actor == subject else None
