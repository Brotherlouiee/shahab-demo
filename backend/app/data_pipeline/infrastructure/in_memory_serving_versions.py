"""Deterministic test/local adapter for the serving-version port.

This adapter models the transaction invariant in memory only. Production
PostgreSQL persistence and operational authorization remain separate tasks; no
application code may use it as a production publication mechanism.
"""

from __future__ import annotations

from dataclasses import replace

from backend.app.data_pipeline.application.publish_serving_version import ServingVersionRepository
from backend.app.data_pipeline.domain.publication import ServingDataVersion, ServingVersionState


class InMemoryServingVersionRepository(ServingVersionRepository):
    """A copy-on-write repository that proves active-pointer atomicity."""

    def __init__(self, *, fail_publish: bool = False) -> None:
        self._versions: dict[str, ServingDataVersion] = {}
        self._current_version_id: str | None = None
        self._fail_publish = fail_publish
        self._fail_next_publish = False

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

    def save_draft(self, version: ServingDataVersion) -> None:
        if version.version_id in self._versions:
            raise ValueError("serving version already exists")
        self._versions[version.version_id] = version

    def replace_version(self, version: ServingDataVersion) -> None:
        if version.version_id not in self._versions:
            raise LookupError("serving version was not found")
        self._versions[version.version_id] = version

    def publish_atomically(self, approved_version: ServingDataVersion) -> ServingDataVersion:
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
        return published
