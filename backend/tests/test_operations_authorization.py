"""Least-privilege matrix and authority failures; no production DB/credentials."""

import unittest
from datetime import UTC, datetime, timedelta
from typing import cast
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.app.core.config import AppEnvironment, Settings
from backend.app.core.dependencies import get_request_database_session
from backend.app.infrastructure.db.models import UserProfile
from backend.app.main import create_app
from backend.app.operations.authorization import (
    IdentityKind,
    OperationsAccessDenied,
    OperationsAuthorityUnavailable,
    OperationsAuthorizer,
    OperationsIdentity,
    RoleGrant,
)
from backend.app.operations.policy import Permission, Role, permits

NOW = datetime(2026, 10, 11, tzinfo=UTC)
LATER = NOW + timedelta(minutes=5)


class OperationsAuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = MagicMock()
        self.identity = OperationsIdentity("operator-test", IdentityKind.OPERATOR_MFA, LATER)
        self.repository.read_current.return_value = RoleGrant(
            self.identity.subject, frozenset({Role.DATA_EDITOR}), LATER
        )
        self.authorizer = OperationsAuthorizer(self.repository, lambda: NOW)

    def test_complete_role_permission_matrix(self) -> None:
        # Explicit product expectations, independent of the implementation map.
        expected = {
            Role.ANONYMOUS: set(),
            Role.USER: set(),
            Role.SUPPORT: set(),
            Role.DATA_EDITOR: {"data.import", "data.review", "config.edit"},
            Role.ADMIN: {"data.approve", "data.publish", "data.rollback", "config.approve"},
            Role.SERVICE: {"data.import"},
        }
        for role in Role:
            kind = IdentityKind.SERVICE_CREDENTIAL if role is Role.SERVICE else IdentityKind.OPERATOR_MFA
            identity = OperationsIdentity("operator-test", kind, LATER)
            self.repository.read_current.return_value = RoleGrant(identity.subject, frozenset({role}), LATER)
            for permission in Permission:
                with self.subTest(role=role, permission=permission):
                    if permission.value in expected[role]:
                        self.assertEqual(self.authorizer.require(identity, permission), identity.subject)
                    else:
                        with self.assertRaises(OperationsAccessDenied):
                            self.authorizer.require(identity, permission)

    def test_admin_has_no_implicit_editor_permission_but_explicit_combination_works(self) -> None:
        self.repository.read_current.return_value = RoleGrant(self.identity.subject, frozenset({Role.ADMIN}), LATER)
        with self.assertRaises(OperationsAccessDenied):
            self.authorizer.require(self.identity, Permission.IMPORT)
        self.repository.read_current.return_value = RoleGrant(
            self.identity.subject, frozenset({Role.ADMIN, Role.DATA_EDITOR}), LATER
        )
        for permission in Permission:
            self.assertEqual(self.authorizer.require(self.identity, permission), self.identity.subject)

    def test_anonymous_customer_and_mock_otp_cannot_use_even_an_admin_grant(self) -> None:
        self.repository.read_current.return_value = RoleGrant(self.identity.subject, frozenset({Role.ADMIN}), LATER)
        identities = [None] + [
            OperationsIdentity("operator-test", kind, LATER) for kind in (IdentityKind.CUSTOMER, IdentityKind.MOCK_OTP)
        ]
        for identity in identities:
            for permission in Permission:
                with self.subTest(identity=identity, permission=permission):
                    with self.assertRaises(OperationsAccessDenied):
                        self.authorizer.require(identity, permission)
        self.repository.read_current.assert_not_called()

    def test_missing_revoked_expired_and_wrong_subject_grants_are_denied(self) -> None:
        for grant in (
            None,
            RoleGrant("operator-test", frozenset(), LATER),
            RoleGrant("operator-test", frozenset({Role.ADMIN}), NOW),
            RoleGrant("other-operator", frozenset({Role.ADMIN}), LATER),
            RoleGrant("operator-test", frozenset({Role.ADMIN}), NOW.replace(tzinfo=None)),
        ):
            with self.subTest(grant=grant):
                self.repository.read_current.return_value = grant
                with self.assertRaises(OperationsAccessDenied):
                    self.authorizer.require(self.identity, Permission.APPROVE)

    def test_grants_are_reread_so_revocation_is_immediate(self) -> None:
        self.authorizer.require(self.identity, Permission.IMPORT)
        self.repository.read_current.return_value = None
        with self.assertRaises(OperationsAccessDenied):
            self.authorizer.require(self.identity, Permission.IMPORT)
        self.assertEqual(self.repository.read_current.call_count, 2)

    def test_invalid_identity_and_expiry_are_rejected_before_lookup(self) -> None:
        for identity in (
            OperationsIdentity("", IdentityKind.OPERATOR_MFA, LATER),
            OperationsIdentity("operator-test", IdentityKind.OPERATOR_MFA, NOW),
            OperationsIdentity("operator-test", IdentityKind.OPERATOR_MFA, NOW.replace(tzinfo=None)),
            OperationsIdentity("operator-test", cast(IdentityKind, "operator-mfa"), LATER),
            OperationsIdentity("operator-test", cast(IdentityKind, "future-admin"), LATER),
        ):
            with self.subTest(identity=identity):
                with self.assertRaises(OperationsAccessDenied):
                    self.authorizer.require(identity, Permission.IMPORT)
        self.repository.read_current.assert_not_called()

    def test_unknown_role_permission_and_client_strings_fail_closed(self) -> None:
        for role in ("admin", "future-admin"):
            self.repository.read_current.return_value = RoleGrant(
                "operator-test", frozenset({Role.DATA_EDITOR, cast(Role, role)}), LATER
            )
            with self.assertRaises(OperationsAccessDenied):
                self.authorizer.require(self.identity, Permission.IMPORT)
        for permission in ("data.import", "*", "future-operation"):
            self.assertFalse(permits(frozenset({Role.ADMIN}), cast(Permission, permission)))
            with self.assertRaises(OperationsAccessDenied):
                self.authorizer.require(self.identity, cast(Permission, permission))

    def test_authority_failure_does_not_leak_or_fall_back(self) -> None:
        self.repository.read_current.side_effect = RuntimeError("private grant-store credential")
        with self.assertRaises(OperationsAuthorityUnavailable) as raised:
            self.authorizer.require(self.identity, Permission.IMPORT)
        self.assertNotIn("credential", str(raised.exception))
        self.assertNotIn("operator-test", str(raised.exception))

    def test_service_credentials_cannot_borrow_human_approval_roles(self) -> None:
        identity = OperationsIdentity("service-test", IdentityKind.SERVICE_CREDENTIAL, LATER)
        self.repository.read_current.return_value = RoleGrant(
            identity.subject, frozenset({Role.SERVICE, Role.ADMIN, Role.DATA_EDITOR}), LATER
        )
        self.assertEqual(self.authorizer.require(identity, Permission.IMPORT), identity.subject)
        for permission in set(Permission) - {Permission.IMPORT}:
            with self.assertRaises(OperationsAccessDenied):
                self.authorizer.require(identity, permission)

    def test_humans_cannot_borrow_a_service_grant(self) -> None:
        self.repository.read_current.return_value = RoleGrant(self.identity.subject, frozenset({Role.SERVICE}), LATER)
        with self.assertRaises(OperationsAccessDenied):
            self.authorizer.require(self.identity, Permission.IMPORT)

    def test_default_authority_denies_all_operations(self) -> None:
        for permission in Permission:
            with self.assertRaises(OperationsAccessDenied):
                OperationsAuthorizer(clock=lambda: NOW).require(self.identity, permission)


class OperationsPublicBoundaryTests(unittest.TestCase):
    def test_default_app_denies_operator_actions_and_public_payload_cannot_elevate(self) -> None:
        app = create_app(Settings(environment=AppEnvironment.TEST))
        identity = OperationsIdentity(
            "operator-test", IdentityKind.OPERATOR_MFA, datetime.now(UTC) + timedelta(minutes=5)
        )
        for permission in Permission:
            with self.assertRaises(OperationsAccessDenied):
                app.state.operations_authorizer.require(identity, permission)

        database = MagicMock()
        database.get.return_value = UserProfile(phone="09000000001")
        app.dependency_overrides[get_request_database_session] = lambda: database
        client = TestClient(app)
        # Existing real HTTP handlers with a contract-only DB double.
        challenge = client.post("/api/v1/account-access/request", json={"phone": "09000000001"})
        self.assertEqual(challenge.status_code, 200)
        verified = client.post(
            "/api/v1/account-access/verify",
            json={"challengeId": challenge.json()["challengeId"], "code": "123456"},
        )
        self.assertEqual(verified.status_code, 200)
        headers = {"Authorization": "Bearer " + verified.json()["accessToken"], "X-Role": "admin"}
        for extra in ({"role": "admin"}, {"roles": ["admin"]}, {"permissions": ["data.publish"]}):
            response = client.put("/api/v1/profiles", headers=headers, json={"phone": "09000000001", **extra})
            self.assertEqual(response.status_code, 422)
        database.commit.assert_not_called()
        # OTP's server-owned phone remains a customer, even with a spoofed role header.
        response = client.get("/api/v1/account-access/session", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("roles", response.json())
        for path in ("/api/v1/operations", "/api/v1/operations/publish", "/api/v1/operations/roles"):
            self.assertEqual(client.post(path, headers=headers, json={"role": "admin"}).status_code, 404)
