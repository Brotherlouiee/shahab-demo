"""Validate the resolved production Compose contract using the actual Compose CLI."""

import ipaddress
import json
import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def compose_binary():
    return shlex.split(os.environ.get("SHAHAB_TEST_COMPOSE_BINARY", "docker compose"))


def synthetic_environment(tls):
    return {
        "POSTGRES_PASSWORD": "synthetic-vm-owner",
        "SHAHAB_DATABASE_URL": "postgresql+psycopg://shahab_api:synthetic-vm-api@postgres:5432/shahab",
        "SHAHAB_MIGRATION_DATABASE_URL": (
            "postgresql+psycopg://shahab_migrator:synthetic-vm-owner@postgres:5432/shahab"
        ),
        "SHAHAB_READINESS_TOKEN": "synthetic-vm-readiness",
        "SHAHAB_PUBLIC_HOST": "vm.example.invalid",
        "SHAHAB_TLS_DIRECTORY": str(tls),
    }


class VMComposeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as directory:
            cls.environment = synthetic_environment(directory)
            cls.args = [
                *compose_binary(),
                "--env-file",
                "/dev/null",
                "--profile",
                "maintenance",
                "-f",
                str(ROOT / "docker-compose.prod.yml"),
                "config",
                "--format",
                "json",
            ]
            result = subprocess.run(
                cls.args, capture_output=True, text=True, env={**os.environ, **cls.environment}, timeout=30, check=True
            )
            cls.config = json.loads(result.stdout)

    def test_only_prebuilt_release_pair_and_pinned_infrastructure(self):
        services = self.config["services"]
        manifest = json.loads((ROOT / "docs/release/images/v0.1.0.json").read_text())
        for name, item in zip(("api", "frontend"), manifest["images"], strict=True):
            self.assertEqual(services[name]["image"], "docker.io/" + item["repository"] + "@" + item["digest"])
        for service in services.values():
            self.assertNotIn("build", service)
            self.assertIn("@sha256:", service["image"])
            self.assertEqual(service["platform"], "linux/amd64")

    def test_no_source_mount_dev_server_or_public_database(self):
        for name, service in self.config["services"].items():
            if name != "frontend":
                self.assertFalse(service.get("ports"))
            self.assertNotIn("--reload", (service.get("command") or []))
            for mount in service.get("volumes", []):
                self.assertNotEqual(mount["target"], "/app")
                if mount["type"] == "bind":
                    self.assertTrue(mount["read_only"])
                    self.assertFalse(mount["bind"]["create_host_path"])
        self.assertTrue(self.config["networks"]["data"]["internal"])
        for port in self.config["services"]["frontend"]["ports"]:
            self.assertEqual(port["host_ip"], "127.0.0.1")
        self.assertEqual(self.config["services"]["postgres"]["volumes"][0]["type"], "volume")

    def test_runtime_separated_from_migration_and_no_mock_login(self):
        api = self.config["services"]["api"]
        migration = self.config["services"]["migrate"]
        self.assertEqual(migration["profiles"], ["maintenance"])
        self.assertEqual(migration["command"], ["alembic", "upgrade", "head"])
        self.assertNotIn("migrate", api["depends_on"])
        self.assertNotEqual(api["environment"]["SHAHAB_DATABASE_URL"], migration["environment"]["SHAHAB_DATABASE_URL"])
        for key in ("SHAHAB_PROFILE_MOCK_OTP_ENABLED", "SHAHAB_DEBUG", "SHAHAB_KAVENEGAR_OTP_ENABLED"):
            self.assertEqual(api["environment"][key], "false")
        self.assertEqual(api["environment"]["SHAHAB_ENVIRONMENT"], "production")
        self.assertTrue(api["read_only"])
        self.assertNotIn("POSTGRES_PASSWORD", api["environment"])
        self.assertEqual(api["depends_on"]["postgres"]["condition"], "service_healthy")

    def test_only_frontend_peer_can_supply_forwarded_headers(self):
        frontend = self.config["services"]["frontend"]
        address = frontend["networks"]["app"]["ipv4_address"]
        api = self.config["services"]["api"]
        command = api["command"]
        self.assertEqual(command[command.index("--forwarded-allow-ips") + 1], address)
        subnet = self.config["networks"]["app"]["ipam"]["config"][0]["subnet"]
        self.assertIn(ipaddress.ip_address(address), ipaddress.ip_network(subnet))
        self.assertNotIn("data", frontend["networks"])

    def test_missing_required_secret_fails_closed(self):
        environment = {**os.environ, **self.environment}
        environment.pop("POSTGRES_PASSWORD", None)
        result = subprocess.run(self.args, env=environment, text=True, capture_output=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("POSTGRES_PASSWORD", result.stderr)


if __name__ == "__main__":
    unittest.main()
