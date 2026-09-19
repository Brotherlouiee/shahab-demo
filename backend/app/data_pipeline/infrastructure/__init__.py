"""Replaceable adapters for raw evidence and local/test pipeline persistence."""

from .filesystem_raw_store import FileSystemImmutableRawStore
from .in_memory_serving_versions import InMemoryServingVersionRepository

__all__ = ["FileSystemImmutableRawStore", "InMemoryServingVersionRepository"]
