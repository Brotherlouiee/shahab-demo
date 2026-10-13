"""Contract tests for the opt-in, read-only external security smoke boundary."""

import unittest

from scripts.authorized_staging_security_smoke import checked_base


class AuthorizedStagingSecuritySmokeTests(unittest.TestCase):
    def test_only_explicit_https_origin_is_accepted(self):
        self.assertEqual(checked_base("https://example.test/"), "https://example.test")
        for url in (
            "http://example.test",
            "https://example.test/unsafe",
            "https://example.test/?token=secret",
            "https://example.test/#fragment",
            "https://name:secret@example.test",
            "https://example.test:0",
            "ftp://example.test",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                checked_base(url)
