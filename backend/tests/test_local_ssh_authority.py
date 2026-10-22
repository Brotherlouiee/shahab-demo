"""Local operator identity and role checks; no production authority is simulated."""

import json
import os
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from backend.app.operations.authorization import (
    OperationsAccessDenied,
    OperationsAuthorityUnavailable,
    OperationsAuthorizer,
)
from backend.app.operations.infrastructure.local_ssh import LocalSshAuthority
from backend.app.operations.policy import Permission


class LocalSshAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.current_uid = 10001
        self.expires = (datetime.now(UTC) + timedelta(minutes=10)).isoformat()
        self.document = {
            "schemaVersion": 1,
            "singleOwner": False,
            "operators": [
                {"uid": 10001, "actor": "ssh-editor-1", "roles": ["data-editor"], "expiresAt": self.expires},
                {"uid": 10002, "actor": "ssh-admin-2", "roles": ["admin"], "expiresAt": self.expires},
            ],
        }
        self.authority = LocalSshAuthority()
        self.authority._uid = lambda: self.current_uid
        self.authority._document = lambda: self.document

    def test_separate_editor_and_admin_permissions(self):
        editor = self.authority.authenticate()
        authorizer = OperationsAuthorizer(self.authority)
        self.assertEqual(authorizer.require(editor, Permission.IMPORT), "ssh-editor-1")
        with self.assertRaises(OperationsAccessDenied):
            authorizer.require(editor, Permission.PUBLISH)
        self.current_uid = 10002
        admin = self.authority.authenticate()
        self.assertEqual(authorizer.require(admin, Permission.PUBLISH), "ssh-admin-2")
        with self.assertRaises(OperationsAccessDenied):
            authorizer.require(admin, Permission.IMPORT)
        with self.assertRaises(OperationsAccessDenied):
            authorizer.require(editor, Permission.IMPORT)

    def test_revocation_and_malformed_policy_fail_closed(self):
        editor = self.authority.authenticate()
        self.document["operators"] = [self.document["operators"][1]]
        with self.assertRaises(OperationsAuthorityUnavailable):
            OperationsAuthorizer(self.authority).require(editor, Permission.IMPORT)
        self.document["operators"].append(
            {"uid": 10001, "actor": "ssh-editor-1", "roles": ["data-editor"], "expiresAt": self.expires}
        )
        self.document["operators"].append(dict(self.document["operators"][-1]))
        with self.assertRaises(OperationsAccessDenied):
            self.authority.authenticate()
        self.document["operators"].pop()
        self.document["operators"][-1]["roles"] = ["service"]
        with self.assertRaises(OperationsAccessDenied):
            self.authority.authenticate()
        self.document["operators"][-1]["roles"] = ["data-editor"]
        self.document["operators"][0]["actor"] = "ssh-editor-1"
        with self.assertRaises(OperationsAccessDenied):
            self.authority.authenticate()
        self.document["operators"][0]["actor"] = "ssh-admin-2"
        self.document["operators"][-1]["expiresAt"] = (datetime.now(UTC) + timedelta(days=2)).isoformat()
        with self.assertRaises(OperationsAccessDenied):
            self.authority.authenticate()

    def test_root_and_impersonated_effective_uid_are_denied(self):
        authority = LocalSshAuthority()
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.getuid", return_value=0, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.geteuid", return_value=0, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.name", "posix"),
        ):
            with self.assertRaises(OperationsAccessDenied):
                authority.authenticate()
        with (
            patch("backend.app.operations.infrastructure.local_ssh.os.getuid", return_value=10001, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.geteuid", return_value=0, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.name", "posix"),
        ):
            with self.assertRaises(OperationsAccessDenied):
                authority.authenticate()

    def test_sudo_root_uses_invoking_uid_not_claimed_actor(self):
        with (
            patch.dict(os.environ, {"SUDO_UID": "10001", "SUDO_USER": "ssh-editor"}),
            patch("backend.app.operations.infrastructure.local_ssh.os.getuid", return_value=0, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.geteuid", return_value=0, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.name", "posix"),
        ):
            self.assertEqual(LocalSshAuthority()._uid(), 10001)
        with (
            patch.dict(os.environ, {"SUDO_UID": "10002", "SUDO_USER": "ssh-admin"}),
            patch("backend.app.operations.infrastructure.local_ssh.os.getuid", return_value=10001, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.geteuid", return_value=10001, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.name", "posix"),
        ):
            self.assertEqual(LocalSshAuthority()._uid(), 10001)

    def test_single_owner_requires_explicit_root_mode_and_both_roles(self):
        self.document = {
            "schemaVersion": 1,
            "singleOwner": True,
            "operators": [
                {"uid": 0, "actor": "ssh-owner-root", "roles": ["data-editor", "admin"], "expiresAt": self.expires}
            ],
        }
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.getuid", return_value=0, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.geteuid", return_value=0, create=True),
            patch("backend.app.operations.infrastructure.local_ssh.os.name", "posix"),
        ):
            owner = LocalSshAuthority(allow_root_owner=True)
            owner._document = lambda: self.document
            identity = owner.authenticate()
            authorizer = OperationsAuthorizer(owner)
            self.assertEqual(authorizer.require(identity, Permission.IMPORT), "ssh-owner-root")
            self.assertEqual(authorizer.require(identity, Permission.PUBLISH), "ssh-owner-root")
            with self.assertRaises(OperationsAccessDenied):
                LocalSshAuthority().authenticate()
            self.document["operators"][0]["roles"] = ["admin"]
            with self.assertRaises(OperationsAccessDenied):
                owner.authenticate()

    @unittest.skipUnless(
        os.name == "posix" and getattr(os, "geteuid", lambda: -1)() == 0,
        "requires isolated Linux root container",
    )
    def test_root_owned_policy_rejects_writable_file_and_symlink(self):
        with tempfile.TemporaryDirectory(dir="/etc") as root:
            directory = Path(root)
            directory.chmod(0o755)
            policy = directory / "operators.json"
            policy.write_text(json.dumps(self.document), encoding="utf-8")
            policy.chmod(0o644)
            authority = LocalSshAuthority(policy)
            authority._uid = lambda: 10001
            self.assertEqual(authority.authenticate().subject, "ssh-editor-1")
            policy.chmod(0o666)
            with self.assertRaises(OperationsAccessDenied):
                authority.authenticate()
            policy.chmod(0o644)
            link = directory / "link.json"
            link.symlink_to(policy)
            with self.assertRaises(OperationsAccessDenied):
                LocalSshAuthority(link)._document()
            directory.chmod(0o777)
            with self.assertRaises(OperationsAccessDenied):
                authority.authenticate()
            directory.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
