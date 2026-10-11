"""Deterministic test/local adapter for the serving-version port.

This adapter models the transaction invariant in memory only. Production
PostgreSQL persistence and operational authorization remain separate tasks; no
application code may use it as a production publication mechanism.
"""

from __future__ import annotations

from dataclasses import replace

from backend.app.data_pipeline.application.publish_serving_version import ServingVersionRepository
from backend.app.data_pipeline.domain.publication import ApprovalRecord, ServingDataVersion, ServingVersionState


class InMemoryServingVersionRepository(ServingVersionRepository):
    """A copy-on-write repository that proves active-pointer atomicity."""

    def __init__(self, *, fail_publish: bool = False) -> None:
        self._versions: dict[str, ServingDataVersion] = {}
        self._current_version_id: str | None = None
        self._fail_publish = fail_publish
        self._fail_next_publish = False
        self.preparation_decisions: dict[str, ApprovalRecord] = {}
        self.publication_decisions: tuple[tuple[str, ApprovalRecord], ...] = ()
        self.rollback_decisions: tuple[tuple[str, str, ApprovalRecord], ...] = ()

    def fail_next_publish_for_test(self) -> None:
        """Inject one pre-commit failure in this local/test adapter.

        The hook lets the pipeline prove that a failed future publish retains the
        already serving version. It is deliberately unavailable from production
        composition and performs no state mutation beyond this test adapter.
        """
        self._fail_next_publish = True

    def get_current_published(self) -> ServingDataVersion | None:
        return None if self._current_version_id is None else self._versions[self._current_version_id]

    def get_by_id(self, version_id: str) -> ServingDataVersion | None:
        return self._versions.get(version_id)

    def save_draft(self, version: ServingDataVersion, *, decision: ApprovalRecord | None = None) -> None:
        if version.version_id in self._versions:
            raise ValueError("serving version already exists")
        self._versions[version.version_id] = version
        if decision is not None:
            self.preparation_decisions[version.version_id] = decision

    def replace_version(self, version: ServingDataVersion) -> None:
        if version.version_id not in self._versions:
            raise LookupError("serving version was not found")
        self._versions[version.version_id] = version

    def publish_atomically(
        self, approved_version: ServingDataVersion, *, decision: ApprovalRecord | None = None
    ) -> ServingDataVersion:
        if self._fail_publish or self._fail_next_publish:
            self._fail_next_publish = False
            raise RuntimeError("simulated publication failure")
        if approved_version.version_id not in self._versions:
            raise LookupError("serving version was not found")
        next_versions = dict(self._versions)
        if self._current_version_id is not None:
            previous = next_versions[self._current_version_id]
            next_versions[previous.version_id] = replace(previous, state=ServingVersionState.SUPERSEDED)
        published = replace(approved_version, state=ServingVersionState.PUBLISHED)
        next_versions[published.version_id] = published
        self._versions = next_versions
        self._current_version_id = published.version_id
        if decision is not None:
            self.publication_decisions = (*self.publication_decisions, (published.version_id, decision))
        return published

    def rollback_atomically(
        self,
        target: ServingDataVersion,
        *,
        expected_current_version_id: str,
        decision: ApprovalRecord,
    ) -> ServingDataVersion:
        """Test-only copy-on-write model of CAS and decision atomicity."""
        if self._current_version_id != expected_current_version_id:
            raise ValueError("current version changed; review again")
        stored = self._versions.get(target.version_id)
        if stored != target or target.state is not ServingVersionState.SUPERSEDED or target.approval is None:
            raise ValueError("rollback target changed or is not approved")
        if self._fail_publish or self._fail_next_publish:
            self._fail_next_publish = False
            raise RuntimeError("simulated publication failure")
        next_versions = dict(self._versions)
        current = next_versions[expected_current_version_id]
        next_versions[current.version_id] = replace(current, state=ServingVersionState.SUPERSEDED)
        restored = replace(target, state=ServingVersionState.PUBLISHED)
        next_versions[target.version_id] = restored
        decisions = (*self.rollback_decisions, (current.version_id, target.version_id, decision))
        self._versions = next_versions
        self._current_version_id = target.version_id
        self.rollback_decisions = decisions
        return restored
