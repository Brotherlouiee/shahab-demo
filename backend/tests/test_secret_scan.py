"""Tests for the conservative repository secret scanner."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.scan_repository_secrets import find_secret_assignments


class SecretScanTests(unittest.TestCase):
    def test_detects_credential_shaped_assignment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            assignment = "api_" + "key" + ' = "not-a-real-secret-value"\n'
            (root / "settings.py").write_text(assignment, encoding="utf-8")
            self.assertEqual(find_secret_assignments(root), ["settings.py:1"])

    def test_allows_documented_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "settings.py").write_text('client_secret = "replace-with-a-local-secret"\n', encoding="utf-8")
            self.assertEqual(find_secret_assignments(root), [])
