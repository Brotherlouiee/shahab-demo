"""Exercise real snapshot files without downloading or installing dependencies."""

import importlib.util
import io
import os
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "python_environment_cache", Path(__file__).parents[2] / "scripts/ci/prepare-python-environment.py"
)
cache_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cache_module)


class PythonEnvironmentCacheTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "pyproject.toml").write_text("[project]\nname='fixture'\n")
        self.cache = self.root / "cache"
        self.environment = self.root / "environment"
        self.calls = []

    def command(self, arguments):
        self.calls.append(arguments)
        if arguments[1:3] == ["-m", "venv"]:
            (self.environment / "bin").mkdir()
            (self.environment / "lib").mkdir()
            (self.environment / "bin/python").symlink_to(sys.executable)
            (self.environment / "lib64").symlink_to("lib", target_is_directory=True)
            (self.environment / "lib/package").write_text("fresh dependency")

    def prepare(self, profile="project", image="sha256:fixture"):
        with patch.object(cache_module, "run", side_effect=self.command):
            return cache_module.prepare(self.root, self.cache, self.environment, profile, image)

    def test_hit_restores_private_copy_without_installing(self):
        self.assertEqual(self.prepare(), "miss")
        self.calls.clear()
        (self.environment / "lib/package").write_text("contamination from prior test")
        self.assertEqual(self.prepare(), "hit")
        self.assertEqual((self.environment / "lib/package").read_text(), "fresh dependency")
        self.assertTrue((self.environment / "bin/python").is_file())
        self.assertEqual([call[1:] for call in self.calls], [["-m", "pip", "check"]])

    def test_dependency_file_image_and_security_profile_invalidate(self):
        key = cache_module.cache_key(self.root, "project", "image1")
        self.assertNotEqual(key, cache_module.cache_key(self.root, "project", "image2"))
        self.assertNotEqual(key, cache_module.cache_key(self.root, "security", "image1"))
        (self.root / "pyproject.toml").write_text("changed dependency metadata")
        self.assertNotEqual(key, cache_module.cache_key(self.root, "project", "image1"))

    def test_security_keeps_pip_floor_and_pinned_tools(self):
        self.prepare(profile="security")
        self.assertTrue(any(call[-2:] == ["--upgrade", "pip>=26.2"] for call in self.calls))
        self.assertTrue(any(call[-2:] == ["bandit==1.8.6", "pip-audit==2.9.0"] for call in self.calls))

    def test_expired_snapshot_is_rebuilt(self):
        self.prepare()
        archive = next(self.cache.glob("*.tar"))
        expired = time.time() - cache_module.MAX_AGE_SECONDS - 1
        os.utime(archive, (expired, expired))
        self.calls.clear()
        self.assertEqual(self.prepare(), "miss")
        self.assertTrue(any("install" in call for call in self.calls))

    def test_failed_install_never_publishes_snapshot(self):
        def failing(arguments):
            self.command(arguments)
            if "install" in arguments:
                raise subprocess.CalledProcessError(23, arguments)

        with patch.object(cache_module, "run", side_effect=failing):
            with self.assertRaises(subprocess.CalledProcessError):
                cache_module.prepare(self.root, self.cache, self.environment, "project", "image")
        self.assertEqual(list(self.cache.glob("*.tar")), [])
        self.assertEqual(list(self.cache.glob("*.partial")), [])

    def test_corrupt_snapshot_is_rebuilt(self):
        self.prepare()
        next(self.cache.glob("*.tar")).write_text("incomplete archive")
        self.assertEqual(self.prepare(), "miss")

    def test_unsafe_archive_cannot_escape_private_environment(self):
        self.prepare()
        archive = next(self.cache.glob("*.tar"))
        with tarfile.open(archive, "w") as snapshot:
            member = tarfile.TarInfo("../escape")
            member.size = 1
            snapshot.addfile(member, io.BytesIO(b"x"))
        self.assertEqual(self.prepare(), "miss")
        self.assertFalse((self.root / "escape").exists())

    def test_missing_identity_and_unknown_profile_fail_before_cache_creation(self):
        for profile, image in (("other", "image"), ("project", "")):
            with self.assertRaises(ValueError):
                self.prepare(profile=profile, image=image)
        self.assertFalse(self.cache.exists())

    def test_real_venv_python_and_console_script_work_after_restoration(self):
        # Real ensurepip/venv/tar/interpreter, no package downloads. Dependency
        # install invocations are replaced; pip check and executables are real.
        def offline_commands(arguments):
            if arguments[1:3] == ["-m", "venv"] or arguments[1:] == ["-m", "pip", "check"]:
                subprocess.run(arguments, check=True, capture_output=True)

        with patch.object(cache_module, "run", side_effect=offline_commands):
            self.assertEqual(
                cache_module.prepare(self.root, self.cache, self.environment, "project", "real-venv-image"),
                "miss",
            )
            self.assertEqual(
                cache_module.prepare(self.root, self.cache, self.environment, "project", "real-venv-image"),
                "hit",
            )
        python = self.environment / "bin/python"
        completed = subprocess.run(
            [str(python), "-c", "import sys; print(sys.prefix)"], check=True, capture_output=True, text=True
        )
        self.assertEqual(completed.stdout.strip(), str(self.environment))
        subprocess.run([str(self.environment / "bin/pip"), "check"], check=True, capture_output=True)
        self.assertTrue((self.environment / "lib64").is_symlink())


if __name__ == "__main__":
    unittest.main()
