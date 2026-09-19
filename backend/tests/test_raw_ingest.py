"""Unit tests for immutable raw capture; no parser, database or serving behavior is involved."""

from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from backend.app.data_pipeline.application.ingest_raw import RawIngestService
from backend.app.data_pipeline.infrastructure.filesystem_raw_store import FileSystemImmutableRawStore


class RawIngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.service = RawIngestService(FileSystemImmutableRawStore(self.root), max_bytes=64)
        self.received_at = datetime(2026, 9, 19, tzinfo=UTC)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_same_bytes_are_deduplicated_without_overwrite(self) -> None:
        first = self._ingest(b"verified source")
        second = self._ingest(b"verified source")
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first.byte_count, 15)
        self.assertEqual((self.root / first.sha256).read_bytes(), b"verified source")
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_changed_bytes_create_a_new_immutable_object(self) -> None:
        first = self._ingest(b"version one")
        second = self._ingest(b"version two")
        self.assertNotEqual(first.sha256, second.sha256)
        self.assertEqual((self.root / first.sha256).read_bytes(), b"version one")
        self.assertEqual((self.root / second.sha256).read_bytes(), b"version two")

    def test_oversized_source_is_rejected_before_storage(self) -> None:
        with self.assertRaisesRegex(ValueError, "maximum size"):
            self._ingest(b"x" * 65)
        self.assertEqual(list(self.root.iterdir()), [])

    def _ingest(self, content: bytes):
        return self.service.ingest_bytes(
            content,
            original_filename="source.unitext",
            source_reference="canonical-upload-2026-09",
            source_version="2026.09.19",
            owner_reference="data-owner",
            received_at=self.received_at,
        )
