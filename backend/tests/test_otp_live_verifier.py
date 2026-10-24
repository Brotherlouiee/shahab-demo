"""Offline safety checks for the owner-operated live tool; never send SMS."""

import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import Mock, patch

from scripts import verify_otp_live as live


class LiveVerifierTests(unittest.TestCase):
    def test_acceptance_checks_reuse_old_token_and_keep_secrets_out_of_output(self):
        token = "synthetic-session-credential"
        phone = "09000000001"
        client = Mock()
        client.sms_requests = 2
        client.cookies = [
            SimpleNamespace(
                name="shahab_account_access", secure=True, has_nonstandard_attr=lambda name: name == "HttpOnly"
            )
        ]
        client.call.side_effect = [
            (401, {}),
            (200, {"challengeId": "synthetic-first", "expiresIn": 120}),
            (401, {}),
            (200, {"accessToken": token, "expiresIn": 3600}),
            (200, {}),
            (200, {}),
            (204, {}),
            (401, {}),
            (401, {}),
            (200, {"challengeId": "synthetic-second", "expiresIn": 120}),
            (401, {}),
        ]
        replay = Mock()
        replay.call.return_value = (401, {})
        output = io.StringIO()
        with (
            patch.object(live, "Client", return_value=replay),
            patch.object(live.getpass, "getpass", side_effect=[phone, "654321", "765432"]),
            patch.object(live.time, "monotonic", side_effect=[0, 10, 11]),
            patch.object(live.time, "sleep") as sleep,
            redirect_stdout(output),
        ):
            live.run(client)
        sleep.assert_called_once_with(122)
        self.assertEqual(client.call.call_args_list[2].args[2]["code"], "654322")
        self.assertEqual(client.call.call_args_list[7].args[-1], token)
        self.assertEqual(client.call.call_args_list[8].args[-1], token)
        replay.call.assert_called_once()
        for secret in (phone, token, "654321", "765432", "synthetic-first", "synthetic-second"):
            self.assertNotIn(secret, output.getvalue())
        self.assertIn("live_checks_passed", output.getvalue())

    def test_no_third_sms_or_unknown_endpoint_or_redirect(self):
        client = live.Client()
        client.opener = Mock()
        client.sms_requests = 2
        with self.assertRaisesRegex(live.CheckFailed, "sms_budget_exceeded"):
            client.call("POST", live.PREFIX + "/request", {"phone": "09000000001"})
        with self.assertRaisesRegex(live.CheckFailed, "unexpected_endpoint"):
            client.call("GET", "https://unrelated.example/")
        client.opener.open.assert_not_called()
        with self.assertRaisesRegex(live.CheckFailed, "redirect_blocked"):
            live.NoRedirect().redirect_request(None, None, 302, "", {}, "https://unrelated.example/")

    def test_unexpected_success_revokes_test_session_and_fails(self):
        client = Mock()
        client.call.side_effect = [(200, {}), (204, {})]
        with self.assertRaisesRegex(live.CheckFailed, "expected_http_401, received_http_200"):
            live.expect(client, "replay", "POST", live.PREFIX + "/verify", 401, {})
        self.assertEqual(client.call.call_args_list[-1].args, ("POST", live.PREFIX + "/logout"))

    def test_transport_failure_prints_no_exception_or_secret(self):
        with (
            patch.object(live.sys.stdin, "isatty", return_value=True),
            patch.object(live, "run", side_effect=RuntimeError("secret-in-upstream-exception")),
            patch.object(live.sys, "stderr", new_callable=io.StringIO) as output,
        ):
            self.assertEqual(live.main(), 1)
        self.assertNotIn("secret-in-upstream-exception", output.getvalue())


if __name__ == "__main__":
    unittest.main()
