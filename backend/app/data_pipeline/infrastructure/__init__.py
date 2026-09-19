"""Replaceable adapters for raw pipeline storage."""

from .filesystem_raw_store import FileSystemImmutableRawStore

__all__ = ["FileSystemImmutableRawStore"]
