"""Scrapling - A powerful, flexible web scraping library.

Scraping made easy with automatic element detection, smart caching,
and anti-bot bypass capabilities.

Personal fork notes:
- Forked for learning/personal use
- See upstream: https://github.com/D4Vinci/Scrapling
"""

from scrapling.core.fetchers import Fetcher, AsyncFetcher
from scrapling.core.page import Page
from scrapling.core.element import Element
from scrapling.core.storage import StorageAdapter, SQLiteStorageAdapter

__version__ = "0.2.9"
__author__ = "Karim Shoair (D4Vinci)"
__license__ = "MIT"

__all__ = [
    "Fetcher",
    "AsyncFetcher",
    "Page",
    "Element",
    "StorageAdapter",
    "SQLiteStorageAdapter",
]
