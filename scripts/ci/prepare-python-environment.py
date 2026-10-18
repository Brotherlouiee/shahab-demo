"""Cache a dependency snapshot, then restore a private venv at its original path.

Only trusted local CI uses this cache. Never execute tests in the stored snapshot.
The fixed /workspace editable source and /tmp venv paths are part of the contract.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

ENVIRONMENT = Path(tempfile.gettempdir()) / "shahab-job-python"
MAX_AGE_SECONDS = 24 * 60 * 60
PROFILES = {
    "project": ("pip",),
    "security": ("pip>=26.2", "bandit==1.8.6", "pip-audit==2.9.0"),
}


def cache_key(root: Path, profile: str, image_id: str) -> str:
    if profile not in PROFILES:
        raise ValueError("Unsupported Python dependency profile")
    if not image_id:
        raise ValueError("Missing immutable CI image identity")
    parts = [
        Path(__file__).read_bytes(),
        (root / "pyproject.toml").read_bytes(),
        json.dumps([profile, image_id, sys.version, sys.platform, platform.machine()]).encode(),
    ]
    return hashlib.sha256(b"\0".join(parts)).hexdigest()


def run(arguments: list[str]) -> None:
    started = time.monotonic()
    subprocess.run(arguments, check=True)
    print(f"PYTHON_CACHE command={arguments[1:]} seconds={time.monotonic() - started:.3f}", flush=True)


def prepare(root: Path, cache: Path, environment: Path, profile: str, image_id: str) -> str:
    key = cache_key(root, profile, image_id)
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / f"{key}.tar"
    # Lock only preparation/restoration, never hold this lock while tests execute.
    with (cache / f"{key}.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        started = time.monotonic()
        if environment.exists():
            shutil.rmtree(environment)
        environment.mkdir(parents=True)
        if archive.exists() and 0 <= time.time() - archive.stat().st_mtime < MAX_AGE_SECONDS:
            try:
                with tarfile.open(archive) as snapshot:
                    snapshot.extractall(environment, filter="data")
                run([str(environment / "bin/python"), "-m", "pip", "check"])
            except (OSError, tarfile.TarError, subprocess.CalledProcessError):
                print("PYTHON_CACHE invalid snapshot; rebuilding", flush=True)
                archive.unlink(missing_ok=True)
                shutil.rmtree(environment)
                environment.mkdir()
            else:
                print(f"PYTHON_CACHE hit key={key} seconds={time.monotonic() - started:.3f}", flush=True)
                return "hit"

        print(f"PYTHON_CACHE miss key={key}", flush=True)
        run([sys.executable, "-m", "venv", str(environment)])
        python = str(environment / "bin/python")
        run([python, "-m", "pip", "install", "--upgrade", PROFILES[profile][0]])
        run([python, "-m", "pip", "install", "-e", ".[test,quality]"])
        if profile == "security":
            run([python, "-m", "pip", "install", *PROFILES[profile][1:]])
        run([python, "-m", "pip", "check"])

        descriptor, temporary = tempfile.mkstemp(prefix=f"{key}.", suffix=".partial", dir=cache)
        os.close(descriptor)
        try:
            # Dereference venv interpreter symlinks: data-filter extraction must not
            # need absolute links to the base image's Python installation.
            with tarfile.open(temporary, "w", dereference=True) as snapshot:
                for entry in environment.iterdir():
                    # Keep relative links such as lib64 -> lib without duplicating
                    # the entire dependency tree in the snapshot.
                    snapshot.dereference = not (entry.is_symlink() and not entry.readlink().is_absolute())
                    snapshot.add(entry, arcname=entry.name)
            os.replace(temporary, archive)
        finally:
            Path(temporary).unlink(missing_ok=True)
        print(f"PYTHON_CACHE stored key={key} seconds={time.monotonic() - started:.3f}", flush=True)
        return "miss"


if __name__ == "__main__":
    prepare(
        Path.cwd(),
        Path("/ci-cache/python-environments"),
        ENVIRONMENT,
        sys.argv[1],
        os.environ["SHAHAB_CI_IMAGE_ID"],
    )
