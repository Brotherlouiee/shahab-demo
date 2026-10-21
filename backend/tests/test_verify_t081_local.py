"""Guard the reusable T081 HTTP verifier against wrong Compose targets."""

import json
import unittest
from unittest.mock import patch

from scripts import verify_t081_local as verifier


class LocalVerifierBoundaryTests(unittest.TestCase):
    def metadata(self, *, project=None, environment="local", host="127.0.0.1"):
        return json.dumps(
            [
                {
                    "Config": {
                        "Labels": {
                            "com.docker.compose.project": project or verifier.PROJECT,
                            "com.docker.compose.service": "api",
                            "com.docker.compose.project.working_dir": str(verifier.ROOT),
                        },
                        "Env": [
                            f"SHAHAB_ENVIRONMENT={environment}",
                            "SHAHAB_PROFILE_MOCK_OTP_ENABLED=true",
                        ],
                    },
                    "NetworkSettings": {"Ports": {"8000/tcp": [{"HostIp": host, "HostPort": "8000"}]}},
                }
            ]
        )

    def verify(self, metadata):
        with patch.object(verifier, "docker", side_effect=["isolated-api-container", metadata]):
            verifier.require_isolated_local_api()

    def test_accepts_exact_isolated_local_loopback_container(self):
        self.verify(self.metadata())

    def test_rejects_wrong_project(self):
        with self.assertRaisesRegex(RuntimeError, "local-only"):
            self.verify(self.metadata(project="shahab-prod"))

    def test_rejects_production_environment(self):
        with self.assertRaisesRegex(RuntimeError, "local-only"):
            self.verify(self.metadata(environment="production"))

    def test_rejects_public_bind(self):
        with self.assertRaisesRegex(RuntimeError, "local-only"):
            self.verify(self.metadata(host="0.0.0.0"))


if __name__ == "__main__":
    unittest.main()
