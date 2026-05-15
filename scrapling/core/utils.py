"""Utility functions and helpers for Scrapling."""

import re
import logging
import hashlib
from typing import Optional, Union, Dict, Any
from urllib.parse import urlparse, urljoin, urlencode

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO, fmt: Optional[str] = None) -> logging.Logger:
    """Configure and return a logger for Scrapling.

    Args:
        level: Logging level (default: INFO)
        fmt: Optional custom format string

    Returns:
        Configured logger instance
    """
    if fmt is None:
        fmt = "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S"))

    _logger = logging.getLogger("scrapling")
    _logger.setLevel(level)
    if not _logger.handlers:
        _logger.addHandler(handler)

    return _logger


def is_valid_url(url: str) -> bool:
    """Check whether a given string is a valid HTTP/HTTPS URL.

    Args:
        url: The URL string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def normalize_url(url: str, base: Optional[str] = None) -> str:
    """Normalize a URL, optionally resolving it against a base URL.

    Args:
        url: The URL to normalize
        base: Optional base URL for resolving relative paths

    Returns:
        Normalized absolute URL string

    Raises:
        ValueError: If the resulting URL is invalid
    """
    if base:
        url = urljoin(base, url)

    url = url.strip()

    if not is_valid_url(url):
        raise ValueError(f"Invalid URL after normalization: {url!r}")

    return url


def build_url(base: str, path: str = "", params: Optional[Dict[str, Any]] = None) -> str:
    """Construct a full URL from components.

    Args:
        base: Base URL (scheme + host)
        path: URL path to append
        params: Optional query parameters as a dict

    Returns:
        Complete URL string
    """
    url = urljoin(base, path)
    if params:
        query_string = urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{url}?{query_string}"
    return url


def hash_url(url: str) -> str:
    """Return a short SHA-256 hex digest for a URL (useful for caching keys).

    Args:
        url: The URL to hash

    Returns:
        16-character hex digest string
    """
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def clean_text(text: str) -> str:
    """Strip and collapse whitespace in a text string.

    Args:
        text: Raw text content

    Returns:
        Cleaned, single-spaced text
    """
    return re.sub(r"\s+", " ", text).strip()


def merge_headers(
    default: Dict[str, str],
    override: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Merge two header dicts, with *override* taking precedence.

    Args:
        default: Base headers
        override: Headers that should overwrite defaults

    Returns:
        Merged header dictionary
    """
    merged = dict(default)
    if override:
        merged.update(override)
    return merged
