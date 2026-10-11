"""T02 application behavior; repositories are explicit local/test doubles.

These tests prove use-case policy and transition contracts, not durable writes
or operator authentication. The existing real PostgreSQL/browser gates stay in CI.
"""

import unittest
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

from backend.app.data_pipeline.application.operations import InternalDataOperations
from backend.app.data_pipeline.application.prepare_import import ImportManifestRow
from backend.app.data_pipeline.application.publish_serving_version import ServingPublicationService
from backend.app.data_pipeline.domain.publication import ServingVersionState
from backend.app.data_pipeline.infrastructure.in_memory_import_reviews import InMemoryImportReviewRepository
from backend.app.data_pipeline.infrastructure.in_memory_serving_versions import InMemoryServingVersionRepository
from backend.app.operations.authorization import (
    IdentityKind,
    OperationsAccessDenied,
    OperationsAuthorizer,
    OperationsIdentity,
    RoleGrant,
)
from backend.app.operations.policy import Role

NOW = datetime(2026, 10, 11, tzinfo=UTC)
VALUES = {
    "maxAmount": "100 میلیون تومان",
    "monthlyInstallment": "10 میلیون تومان",
    "maxRepaymentMonths": "12 ماه",
    "interestRate": "18 درصد",
    "depositRequired": "دارد",
    "depositHoldingMonths": "3 ماه",
    "loanToDepositRatio": "100 درصد",
    "guaranteeType": "تعهد فردی",
}


def manifest(name: str = "طرح نمونه", **values: str) -> tuple[ImportManifestRow, ...]:
    return (ImportManifestRow(1, "بانک نمونه", name, {**VALUES, **values}),)


class InternalDataOperationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grants = Mock()
        self.grants.read_current.side_effect = self.grant
        self.roles = {
            "editor": frozenset({Role.DATA_EDITOR}),
            "admin": frozenset({Role.ADMIN}),
            "service": frozenset({Role.SERVICE}),
            "customer": frozenset({Role.USER}),
        }
        self.reviews = InMemoryImportReviewRepository()
        self.versions = InMemoryServingVersionRepository()
        self.publication = ServingPublicationService(self.versions)
        self.ops = InternalDataOperations(
            OperationsAuthorizer(self.grants, lambda: NOW), self.reviews, self.publication, lambda: NOW
        )
        self.editor = self.identity("editor")
        self.admin = self.identity("admin")

    def grant(self, subject: str) -> RoleGrant | None:
        roles = self.roles.get(subject)
        return None if roles is None else RoleGrant(subject, roles, NOW + timedelta(hours=1))

    @staticmethod
    def identity(subject: str, kind: IdentityKind = IdentityKind.OPERATOR_MFA) -> OperationsIdentity:
        return OperationsIdentity(subject, kind, NOW + timedelta(hours=1))

    def import_plan(self, import_id: str = "i1", rows=None, *, source_hash="a" * 64):
        return self.ops.import_data(
            self.editor,
            import_id=import_id,
            source_file_sha256=source_hash,
            parser_version="normalizer-v1",
            rows=manifest() if rows is None else rows,
            reason="Review source",
        )

    def publish(self, number: int):
        import_id, version_id = f"i{number}", f"v{number}"
        self.import_plan(import_id, manifest(f"طرح {number}"), source_hash=str(number) * 64)
        draft = self.ops.prepare_version(
            self.editor, import_id=import_id, version_id=version_id, reason="Prepare reviewed import"
        )
        self.ops.approve_version(self.admin, version_id=version_id, reason="Reviewed diff")
        published = self.ops.publish_version(self.admin, version_id=version_id, reason="Publish reviewed version")
        self.assertEqual(draft.state, ServingVersionState.DRAFT)
        return published

    def test_authorized_lifecycle_and_rollback_preserve_original_evidence(self) -> None:
        first = self.publish(1)
        second = self.publish(2)
        restored = self.ops.rollback_version(
            self.admin, version_id="v1", expected_current_version_id="v2", reason="Restore reviewed source"
        )
        self.assertEqual(restored.rows, first.rows)
        self.assertEqual(restored.approval, first.approval)
        self.assertEqual(self.versions.get_current_published(), restored)
        self.assertEqual(self.versions.get_by_id("v2"), replace(second, state=ServingVersionState.SUPERSEDED))
        origin, target, decision = self.versions.rollback_decisions[0]
        self.assertEqual((origin, target, decision.actor_reference), ("v2", "v1", "admin"))
        self.assertEqual(decision.reason, "Restore reviewed source")
        record = self.ops.review_import(self.editor, import_id="i1")
        self.assertEqual(record.actor_reference, "editor")
        self.assertEqual(self.versions.preparation_decisions["v1"].actor_reference, "editor")
        self.assertEqual(self.versions.publication_decisions[0][1].actor_reference, "admin")

    def test_every_denied_operation_performs_zero_resource_access(self) -> None:
        reviews, publication = Mock(), Mock()
        ops = InternalDataOperations(OperationsAuthorizer(self.grants, lambda: NOW), reviews, publication)
        identities = [None, self.identity("customer"), self.identity("admin", IdentityKind.MOCK_OTP)]
        for identity in identities:
            calls = [
                lambda identity=identity: ops.import_data(
                    identity,
                    import_id="missing",
                    source_file_sha256="a" * 64,
                    parser_version="v1",
                    rows=manifest(),
                    reason="review",
                ),
                lambda identity=identity: ops.review_import(identity, import_id="missing"),
                lambda identity=identity: ops.prepare_version(
                    identity, import_id="missing", version_id="missing", reason="Prepare reviewed import"
                ),
                lambda identity=identity: ops.approve_version(identity, version_id="missing", reason="approve"),
                lambda identity=identity: ops.publish_version(
                    identity, version_id="missing", reason="Publish reviewed version"
                ),
                lambda identity=identity: ops.rollback_version(
                    identity, version_id="missing", expected_current_version_id="other", reason="rollback"
                ),
            ]
            for call in calls:
                with self.assertRaises(OperationsAccessDenied):
                    call()
        self.assertEqual(reviews.mock_calls, [])
        self.assertEqual(publication.mock_calls, [])

    def test_editor_cannot_approve_publish_or_rollback(self) -> None:
        self.import_plan()
        self.ops.prepare_version(self.editor, import_id="i1", version_id="v1", reason="Prepare reviewed import")
        for call in [
            lambda: self.ops.approve_version(self.editor, version_id="v1", reason="approve"),
            lambda: self.ops.publish_version(self.editor, version_id="v1", reason="Publish reviewed version"),
            lambda: self.ops.rollback_version(
                self.editor, version_id="v1", expected_current_version_id="v2", reason="rollback"
            ),
        ]:
            with self.assertRaises(OperationsAccessDenied):
                call()
        self.assertIsNone(self.versions.get_current_published())

    def test_admin_cannot_import_or_review(self) -> None:
        with self.assertRaises(OperationsAccessDenied):
            self.ops.import_data(
                self.admin,
                import_id="i1",
                source_file_sha256="a" * 64,
                parser_version="v1",
                rows=manifest(),
                reason="review",
            )
        with self.assertRaises(OperationsAccessDenied):
            self.ops.review_import(self.admin, import_id="i1")

    def test_service_can_import_but_cannot_review_or_approve(self) -> None:
        service = self.identity("service", IdentityKind.SERVICE_CREDENTIAL)
        self.ops.import_data(
            service,
            import_id="i1",
            source_file_sha256="a" * 64,
            parser_version="v1",
            rows=manifest(),
            reason="Import job",
        )
        for call in [
            lambda: self.ops.review_import(service, import_id="i1"),
            lambda: self.ops.approve_version(service, version_id="v1", reason="approve"),
        ]:
            with self.assertRaises(OperationsAccessDenied):
                call()

    def test_revoke_between_import_and_review_is_effective(self) -> None:
        self.import_plan()
        del self.roles["editor"]
        with self.assertRaises(OperationsAccessDenied):
            self.ops.review_import(self.editor, import_id="i1")

    def test_duplicate_import_is_idempotent_but_conflicting_input_cannot_overwrite(self) -> None:
        first = self.import_plan()
        self.assertIs(self.import_plan(), first)
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.import_plan(rows=manifest("different"))
        self.assertIs(self.reviews.get_by_id("i1"), first)

    def test_dirty_import_is_reviewable_but_cannot_prepare_or_borrow_partial_rows(self) -> None:
        dirty = self.import_plan(rows=(*manifest(), *manifest()))
        self.assertTrue(self.ops.review_import(self.editor, import_id="i1").preparation.issues)
        with self.assertRaisesRegex(ValueError, "blocking"):
            self.ops.prepare_version(self.editor, import_id="i1", version_id="v1", reason="Prepare reviewed import")
        self.publication.prepare(
            version_id="v1",
            import_id="i1",
            source_file_sha256="a" * 64,
            parser_version="normalizer-v1",
            rows=dirty.preparation.accepted_rows,
        )
        with self.assertRaisesRegex(ValueError, "blocking"):
            self.ops.approve_version(self.admin, version_id="v1", reason="reviewed")

    def test_version_cannot_use_other_import_hash_parser_or_rows(self) -> None:
        plan = self.import_plan().preparation
        self.ops.prepare_version(self.editor, import_id="i1", version_id="v1", reason="Prepare reviewed import")
        version = self.versions.get_by_id("v1")
        assert version is not None
        for altered in [
            replace(version, source_file_sha256="b" * 64),
            replace(version, parser_version="other"),
            replace(version, rows=()),
        ]:
            self.versions.replace_version(altered)  # hostile/incorrect adapter resource
            with self.assertRaisesRegex(ValueError, "does not match"):
                self.ops.approve_version(self.admin, version_id="v1", reason="approve")
        self.assertTrue(plan.accepted_rows)

    def test_missing_import_and_version_are_controlled_failures(self) -> None:
        with self.assertRaises(LookupError):
            self.ops.review_import(self.editor, import_id="missing")
        with self.assertRaises(LookupError):
            self.ops.approve_version(self.admin, version_id="missing", reason="approve")

    def test_unapproved_publication_and_draft_rollback_are_rejected(self) -> None:
        self.import_plan()
        self.ops.prepare_version(self.editor, import_id="i1", version_id="v1", reason="Prepare reviewed import")
        with self.assertRaisesRegex(ValueError, "approved"):
            self.ops.publish_version(self.admin, version_id="v1", reason="Publish reviewed version")
        with self.assertRaisesRegex(ValueError, "superseded"):
            self.ops.rollback_version(self.admin, version_id="v1", expected_current_version_id="v2", reason="undo")

    def test_stale_rollback_and_injected_failure_preserve_pointer_and_evidence(self) -> None:
        first, second = self.publish(1), self.publish(2)
        with self.assertRaisesRegex(ValueError, "current version changed"):
            self.ops.rollback_version(
                self.admin, version_id="v1", expected_current_version_id="obsolete", reason="undo"
            )
        self.versions.fail_next_publish_for_test()
        with self.assertRaisesRegex(RuntimeError, "simulated"):
            self.ops.rollback_version(self.admin, version_id="v1", expected_current_version_id="v2", reason="undo")
        self.assertEqual(self.versions.get_current_published(), second)
        self.assertEqual(self.versions.get_by_id("v1"), replace(first, state=ServingVersionState.SUPERSEDED))
        self.assertEqual(self.versions.rollback_decisions, ())
        self.ops.rollback_version(self.admin, version_id="v1", expected_current_version_id="v2", reason="undo")
        self.assertEqual(len(self.versions.rollback_decisions), 1)

    def test_reason_and_aware_time_are_required_before_mutations(self) -> None:
        with self.assertRaisesRegex(ValueError, "reason"):
            self.ops.import_data(
                self.editor,
                import_id="i1",
                source_file_sha256="a" * 64,
                parser_version="v1",
                rows=manifest(),
                reason=" ",
            )
        self.ops._clock = lambda: NOW.replace(tzinfo=None)
        with self.assertRaisesRegex(ValueError, "timezone aware"):
            self.import_plan()
        self.assertIsNone(self.reviews.get_by_id("i1"))

    def test_publication_between_rollback_read_and_switch_cannot_be_lost(self) -> None:
        self.publish(1)
        self.publish(2)
        original = self.versions.rollback_atomically

        def concurrent_publish(target, **kwargs):
            self.publish(3)  # deterministic interleaving at the transaction port
            return original(target, **kwargs)

        with patch.object(self.versions, "rollback_atomically", side_effect=concurrent_publish):
            with self.assertRaisesRegex(ValueError, "current version changed"):
                self.ops.rollback_version(self.admin, version_id="v1", expected_current_version_id="v2", reason="undo")
        self.assertEqual(self.versions.get_current_published().version_id, "v3")
        self.assertEqual(self.versions.rollback_decisions, ())

    def test_unknown_core_keeps_needs_review_without_changing_normalization(self) -> None:
        record = self.import_plan(rows=manifest(interestRate="نامشخص"))
        self.assertTrue(record.preparation.is_publishable_candidate)
        draft = self.ops.prepare_version(self.editor, import_id="i1", version_id="v1", reason="Prepare reviewed import")
        self.assertEqual(draft.rows[0].ranking_excluded_variable_ids, ("interestRate",))


if __name__ == "__main__":
    unittest.main()
