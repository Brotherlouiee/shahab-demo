"""Contract tests for the opt-in, read-only external security smoke boundary."""

import io
import json
import unittest
from email.message import Message
from unittest.mock import Mock, patch

from scripts.authorized_staging_security_smoke import checked_base, exposure_checks, main, verify


class Response(io.BytesIO):
    def __init__(self, status, body=b"", content_type="text/html"):
        super().__init__(body)
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = content_type
        self.headers["Cache-Control"] = "no-store"
        self.headers["X-Content-Type-Options"] = "nosniff"
        self.headers["Strict-Transport-Security"] = "max-age=31536000"


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

    def test_absent_artifacts_and_spa_fallback_are_not_secret_leaks(self):
        for statuses in ((403, 404), (200, 200)):
            opener = Mock()
            opener.open.side_effect = [
                Response(status, b"<!doctype html><html><body>App</body></html>") for status in statuses
            ]
            self.assertEqual(exposure_checks(opener, "https://example.test"), [])
            self.assertEqual(opener.open.call_count, 2)
            urls = [call.args[0].full_url for call in opener.open.call_args_list]
            self.assertEqual(urls, ["https://example.test/.env", "https://example.test/.git/config"])

    def test_secret_git_key_unknown_and_oversized_responses_fail_without_body(self):
        for body, content_type in (
            (b"DATABASE_URL=synthetic-private-marker", "text/plain"),
            (b"[core]\nrepositoryformatversion = 0", "text/plain"),
            (b"-----BEGIN PRIVATE KEY-----", "text/plain"),
            (b"unrecognized response", "text/plain"),
            (b"x" * 16385, "text/html"),
        ):
            opener = Mock()
            opener.open.side_effect = [Response(200, body, content_type), Response(404)]
            findings = exposure_checks(opener, "https://example.test")
            self.assertTrue(findings)
            self.assertNotIn("synthetic-private-marker", json.dumps(findings))

    def test_original_four_gets_remain_and_opt_in_adds_only_two_gets(self):
        for include in (False, True):
            responses = [Response(status) for status in (200, 401, 401, 404, 404, 404)]
            opener = Mock()
            opener.open.side_effect = responses
            with patch("urllib.request.build_opener", return_value=opener):
                self.assertEqual(verify("https://example.test", include), [])
            self.assertEqual(opener.open.call_count, 6 if include else 4)
            for call in opener.open.call_args_list:
                req = call.args[0]
                self.assertEqual(req.method, "GET")
                self.assertIsNone(req.data)
                self.assertIsNone(req.get_header("Authorization"))
                self.assertIsNone(req.get_header("Cookie"))

    def test_transport_failure_is_sanitized_without_traceback(self):
        with (
            patch("sys.argv", ["smoke", "--authorized-test-origin", "https://example.test"]),
            patch("scripts.authorized_staging_security_smoke.verify", side_effect=OSError("private-upstream-marker")),
            patch("sys.stdout", new_callable=io.StringIO) as output,
            self.assertRaises(SystemExit) as error,
        ):
            main()
        self.assertEqual(error.exception.code, 1)
        self.assertNotIn("private-upstream-marker", output.getvalue())
