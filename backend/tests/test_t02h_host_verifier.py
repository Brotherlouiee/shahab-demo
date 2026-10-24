"""Offline tests for deployment audit; no Docker, production HTTP or SMS calls."""

import io
import json
import unittest
from contextlib import redirect_stdout
from email.message import Message
from pathlib import Path
from unittest.mock import patch

from scripts import verify_t02h_host as audit

ROOT = Path(__file__).resolve().parents[2]


class HostVerifierTests(unittest.TestCase):
    def test_actual_proxy_template_and_spoofed_header_regression(self):
        config = (ROOT / "deploy/vm/nginx.conf.template").read_text()
        with redirect_stdout(io.StringIO()):
            audit.inspect_proxy(config)
        for old, new in (
            ("$remote_addr;", "$http_x_forwarded_for;"),
            ("proxy_read_timeout 30s;", "proxy_read_timeout 300s;"),
            ("limit_req zone=api_requests", "limit_req zone=undefined"),
        ):
            with self.subTest(change=new), redirect_stdout(io.StringIO()), self.assertRaises(audit.AuditFailed):
                audit.inspect_proxy(config.replace(old, new))

    def test_unrelated_location_cannot_supply_missing_api_directive(self):
        config = (ROOT / "deploy/vm/nginx.conf.template").read_text()
        config = config.replace("proxy_set_header X-Forwarded-For $remote_addr;", "")
        config += "\nserver { location /unrelated { proxy_set_header X-Forwarded-For $remote_addr; } }"
        with redirect_stdout(io.StringIO()), self.assertRaises(audit.AuditFailed):
            audit.inspect_proxy(config)
        with self.assertRaises(audit.AuditFailed):
            audit.api_block("location /api/v1/ { } location /api/v1/ { }")

    def test_ports_and_api_trust_match_actual_frontend_peer(self):
        rows = []
        for name in ("api", "frontend", "postgres", "redis"):
            rows.append(
                {
                    "name": "/shahab-prod-" + name + "-1",
                    "ports": {},
                    "networks": {"app": {"IPAddress": "172.30.50.10"}},
                    "cmd": ["uvicorn", "--forwarded-allow-ips", "172.30.50.10"],
                    "image": "synthetic",
                }
            )
        rows[1]["ports"] = {"8443/tcp": [{"HostIp": "127.0.0.1", "HostPort": "8443"}]}
        config = (ROOT / "deploy/vm/nginx.conf.template").read_text()

        def run():
            with (
                patch.object(audit, "command", side_effect=["\n".join(map(json.dumps, rows)), config, ""]),
                redirect_stdout(io.StringIO()),
            ):
                audit.inspect_containers()

        run()
        rows[2]["ports"] = {"5432/tcp": [{"HostIp": "0.0.0.0", "HostPort": "5432"}]}
        with self.assertRaisesRegex(audit.AuditFailed, "postgres_has_no_host_port"):
            run()
        rows[2]["ports"] = {}
        rows[0]["cmd"][-1] = "*"
        with self.assertRaisesRegex(audit.AuditFailed, "api_trusts_only_frontend_peer"):
            run()

    def test_six_bounded_http_requests_without_credentials_or_sms(self):
        def headers(**values):
            result = Message()
            for key, value in values.items():
                result[key.replace("_", "-")] = value
            return result

        secure = headers(
            Strict_Transport_Security="max-age=31536000",
            X_Content_Type_Options="nosniff",
            Cache_Control="no-store",
            X_Frame_Options="DENY",
        )
        answers = [
            (308, headers(Location=audit.ORIGIN + "/api/v1/health/live")),
            (200, secure),
            (200, secure),
            (401, headers(Cache_Control="no-store")),
            (405, headers()),
            (403, headers()),
        ]
        with patch.object(audit, "request", side_effect=answers) as request, redirect_stdout(io.StringIO()):
            audit.inspect_https()
        self.assertEqual(request.call_count, 6)
        self.assertTrue(all("/account-access/request" not in call.args[2] for call in request.call_args_list))
        self.assertTrue(
            all("Authorization" not in (call.args[3] if len(call.args) > 3 else {}) for call in request.call_args_list)
        )
        answers[-2] = (405, headers(Access_Control_Allow_Origin="*"))
        with (
            patch.object(audit, "request", side_effect=answers),
            redirect_stdout(io.StringIO()),
            self.assertRaisesRegex(audit.AuditFailed, "untrusted_cors"),
        ):
            audit.inspect_https()

    def test_failures_do_not_dump_configuration_or_exception(self):
        with (
            patch.object(audit, "inspect_containers", side_effect=RuntimeError("private-config-value")),
            patch.object(audit.sys, "stderr", new_callable=io.StringIO) as output,
        ):
            self.assertEqual(audit.main(), 1)
        self.assertNotIn("private-config-value", output.getvalue())


if __name__ == "__main__":
    unittest.main()
