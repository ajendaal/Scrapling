"""Storage backends for Scrapling's adaptive learning and caching capabilities.

This module provides storage abstractions for persisting element fingerprints
and caching scraped data across sessions.
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

from scrapling.core.utils import setup_logging

logger = setup_logging()


class StorageBackend:
    """Abstract base class for storage backends."""

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        raise NotImplementedError

    def clear(self) -> bool:
        raise NotImplementedError


class FileStorageBackend(StorageBackend):
    """File-based JSON storage backend for persisting fingerprints and cache.

    Stores data as JSON files in a configurable directory. Supports optional
    TTL-based expiration for cached entries.

    Args:
        storage_dir: Directory path where storage files will be written.
                     Defaults to ~/.scrapling/storage.
        filename: Name of the JSON file used for storage.
    """

    def __init__(
        self,
        storage_dir: Optional[Union[str, Path]] = None,
        filename: str = "scrapling_store.json",
    ):
        if storage_dir is None:
            storage_dir = Path.home() / ".scrapling" / "storage"
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = self.storage_dir / filename
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load existing data from the JSON file, returning empty dict on failure."""
        if not self.filepath.exists():
            return {}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load storage file %s: %s", self.filepath, exc)
            return {}

    def _save(self) -> bool:
        """Persist in-memory data to the JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, default=str)
            return True
        except OSError as exc:
            logger.error("Failed to save storage file %s: %s", self.filepath, exc)
            return False

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check whether a stored entry has passed its TTL."""
        expires_at = entry.get("expires_at")
        if expires_at is None:
            return False
        return datetime.utcnow() > datetime.fromisoformat(expires_at)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value by key, respecting TTL expiration."""
        entry = self._data.get(key)
        if entry is None:
            return None
        if self._is_expired(entry):
            self.delete(key)
            return None
        return entry.get("value")

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store a value under the given key with an optional TTL in seconds."""
        entry: Dict[str, Any] = {"value": value, "created_at": datetime.utcnow().isoformat()}
        if ttl is not None:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            entry["expires_at"] = expires_at.isoformat()
        self._data[key] = entry
        return self._save()

    def delete(self, key: str) -> bool:
        """Remove an entry by key."""
        if key in self._data:
            del self._data[key]
            return self._save()
        return False

    def exists(self, key: str) -> bool:
        """Return True if the key exists and has not expired."""
        return self.get(key) is not None

    def clear(self) -> bool:
        """Remove all stored entries."""
        self._data = {}
        return self._save()

    def __repr__(self) -> str:
        return f"FileStorageBackend(path={self.filepath!r}, entries={len(self._data)})"
