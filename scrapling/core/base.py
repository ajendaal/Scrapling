"""Base classes and core abstractions for Scrapling.

This module provides the foundational building blocks used throughout
the Scrapling library, including base fetcher interfaces and common
utility mixins.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ScraplingException(Exception):
    """Base exception class for all Scrapling-related errors."""
    pass


class FetchError(ScraplingException):
    """Raised when a fetch operation fails."""
    pass


class ParseError(ScraplingException):
    """Raised when parsing of content fails."""
    pass


class BaseFetcher(ABC):
    """Abstract base class for all fetcher implementations.

    All fetchers (sync, async, playwright-based, etc.) should inherit
    from this class and implement the required interface.
    """

    def __init__(
        self,
        timeout: int = 60,  # increased from 30 — 30s was too aggressive for slow sites
        retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the base fetcher.

        Args:
            timeout: Request timeout in seconds.
            retries: Number of retry attempts on failure.
            headers: Optional HTTP headers to include with requests.
            proxy: Optional proxy URL string.
            **kwargs: Additional keyword arguments for subclass use.
        """
        self.timeout = timeout
        self.retries = retries
        self.headers = headers or {}
        self.proxy = proxy
        self._extra = kwargs

    @abstractmethod
    def fetch(self, url: str, **kwargs: Any) -> Any:
        """Fetch the content at the given URL.

        Args:
            url: The URL to fetch.
            **kwargs: Additional options passed to the underlying fetcher.

        Returns:
            A parsed response object.
        """
        raise NotImplementedError

    def _build_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Merge instance headers with any request-specific headers.

        Args:
            extra: Additional headers to merge in for this request.

        Returns:
            Merged header dictionary.
        """
        merged = dict(self.headers)
        if extra:
            merged.update(extra)
        return merged

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"timeout={self.timeout}, "
            f"retries={self.retries})"
        )


class StorageMixin:
    """Mixin that provides simple in-memory caching / storage helpers.

    Intended to be mixed into fetcher or spider classes that need
    lightweight state management between requests.
    """

    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """Store a value under the given key."""
        