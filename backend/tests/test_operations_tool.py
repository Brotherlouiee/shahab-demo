"""Real local HTTPS introspection and strict command boundary, not production IdP proof."""

import time
import unittest
from unittest.mock import Mock

from pydantic import SecretStr, ValidationError

from backend.app.operations.authorization import (
    IdentityKind,
    OperationsAccessDenied,
    OperationsAuthorityUnavailable,
    OperationsAuthorizer,
)
from backend.app.operations.infrastructure.introspection import IntrospectionAuthority
from backend.app.operations.policy import Permission
from backend.tests.operations_authority_fixture import TLSAuthorityFixture
from scripts.operations_tool import OperationsCommand, execute


class OperationsToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provider = TLSAuthorityFixture()
        cls.original = dict(cls.provider.claims)

    @classmethod
    def tearDownClass(cls):
        cls.provider.close()

    def setUp(self):
        self.provider.claims = dict(self.original)
        self.provider.status, self.provider.redirect = 200, False

    def test_mfa_and_current_grants_reach_policy_and_revocation_is_immediate(self):
        authority = self.provider.authority()
        identity = authority.authenticate()
        self.assertEqual(identity.kind, IdentityKind.OPERATOR_MFA)
        authorizer = OperationsAuthorizer(authority)
        self.assertEqual(authorizer.require(identity, Permission.PUBLISH), "test-operator")
        self.provider.claims["active"] = False
        with self.assertRaises(OperationsAuthorityUnavailable):
            authorizer.require(identity, Permission.PUBLISH)

    def test_bad_claims_wrong_issuer_audience_expiry_mfa_and_roles_deny(self):
        now = int(time.time())
        cases = [
            {"active": False},
            {"active": "true"},
            {"iss": "https://other.example.invalid"},
            {"aud": "customer-api"},
            {"exp": now - 1},
            {"iat": now + 60},
            {"exp": now + 3600},
            {"amr": ["sms"]},
            {"auth_time": now - 600},
            {"roles": ["super-admin"]},
            {"sub": ""},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                self.provider.claims = {**self.original, **changes}
                with self.assertRaises(OperationsAccessDenied):
                    self.provider.authority().authenticate()

    def test_service_identity_cannot_borrow_human_approval(self):
        self.provider.claims.update(client_id="service-import", amr=[], auth_time=None, roles=["service", "admin"])
        authority = self.provider.authority()
        identity = authority.authenticate()
        self.assertEqual(identity.kind, IdentityKind.SERVICE_CREDENTIAL)
        authorizer = OperationsAuthorizer(authority)
        authorizer.require(identity, Permission.IMPORT)
        with self.assertRaises(OperationsAccessDenied):
            authorizer.require(identity, Permission.APPROVE)

    def test_role_change_subject_swap_and_authority_errors_fail_closed(self):
        authority = self.provider.authority()
        identity = authority.authenticate()
        self.provider.claims["roles"] = ["user"]
        with self.assertRaises(OperationsAccessDenied):
            OperationsAuthorizer(authority).require(identity, Permission.PUBLISH)
        self.provider.claims["sub"] = "other"
        with self.assertRaises(OperationsAccessDenied):
            OperationsAuthorizer(authority).require(identity, Permission.IMPORT)
        self.provider.status = 503
        with self.assertRaises(OperationsAccessDenied):
            authority.authenticate()
        self.provider.status, self.provider.redirect = 200, True
        with self.assertRaises(OperationsAccessDenied):
            authority.authenticate()

    def test_tls_verification_and_endpoint_credential_safety(self):
        for url in (
            "http://localhost/introspect",
            "https://user:password@localhost/introspect",
            "https://localhost/introspect?token=bad",
        ):
            with self.assertRaises(OperationsAccessDenied):
                IntrospectionAuthority(
                    self.provider.configuration.model_copy(update={"endpoint": url}), SecretStr(self.provider.token)
                )
        with self.assertRaises(OperationsAccessDenied):
            IntrospectionAuthority(self.provider.configuration, SecretStr("123456"))
        untrusted = self.provider.configuration.model_copy(update={"ca_file": None})
        with self.assertRaises(OperationsAccessDenied):
            IntrospectionAuthority(untrusted, SecretStr(self.provider.token)).authenticate()

    def test_strict_command_fields_and_denied_command_never_open_database(self):
        for extra in ({"actor_reference": "admin"}, {"role": "admin"}, {"source_hash": "a" * 64}):
            with self.assertRaises(ValidationError):
                OperationsCommand.model_validate({"operation": "review", "import_id": "i1", **extra})
        with self.assertRaises(ValidationError):
            OperationsCommand(operation="rollback", version_id="v1", reason="test")
        self.provider.claims["roles"] = ["user"]
        sessions = Mock()
        with self.assertRaises(OperationsAccessDenied):
            execute(OperationsCommand(operation="review", import_id="i1"), self.provider.authority(), sessions, Mock())
        sessions.assert_not_called()

    def test_command_output_errors_do_not_include_secret_or_configuration(self):
        import io
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        from scripts.operations_tool import main

        with tempfile.TemporaryDirectory() as directory:
            command = Path(directory) / "command.json"
            command.write_text('{"operation":"review","import_id":"test","role":"admin"}')
            stderr = io.StringIO()
            with patch("sys.argv", ["operations_tool", "--command", str(command)]), patch("sys.stderr", stderr):
                self.assertEqual(main(), 1)
            self.assertNotIn(self.provider.token, stderr.getvalue())
            self.assertNotIn(self.provider.secret, stderr.getvalue())
