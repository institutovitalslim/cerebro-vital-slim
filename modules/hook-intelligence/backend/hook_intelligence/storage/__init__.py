"""SQLite storage API for generation history and favorites."""

from hook_intelligence.storage.database import create_database
from hook_intelligence.storage.repositories import HookRepository

__all__ = ["HookRepository", "create_database"]
