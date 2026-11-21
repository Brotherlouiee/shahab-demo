"""Content-addressable local raw store; production object-storage adaptation is deferred deliberately."""

from __future__ import annotations

import os
from pathlib import Path


class FileSystemImmutableRawStore:
    """Persist opaque source bytes exactly once under a validated SHA-256 filename.

    The exclusive create flag gives the local adapter immutable semantics even with concurrent
    writers: the first writer wins and later identical writes leave the existing object intact.
    This adapter is not a production backup/retention solution; deployment storage and access
    controls are selected in the operations story rather than hidden here.
    """

    def __init__(self, root: Path) -> None:
        self._root = root

    def put_if_absent(self, *, sha256: str, content: bytes) -> bool:
        if len(sha256) != 64 or any(character not in "0123456789abcdef" for character in sha256):
            raise ValueError("sha256 must be a lowercase 64-character hexadecimal digest")
        self._root.mkdir(parents=True, exist_ok=True)
        target = self._root / sha256
        try:
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return False
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        return True
