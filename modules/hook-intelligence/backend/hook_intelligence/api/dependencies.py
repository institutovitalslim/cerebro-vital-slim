"""Application-owned dependencies, initialized lazily and reused."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy.engine import Engine

from hook_intelligence.domain.models import GenerationRequest, Hook
from hook_intelligence.engine.library import HookLibrary
from hook_intelligence.engine.pipeline import generate_with_optional_ai
from hook_intelligence.storage import HookRepository, create_database

Generator = Callable[[GenerationRequest, HookLibrary], tuple[Hook, ...]]


@dataclass(slots=True)
class Services:
    library: HookLibrary
    repository: Any
    engine: Engine | None
    generator: Generator
    owns_engine: bool


class ServiceProvider:
    """Thread-safe lazy provider that avoids database work during module import."""

    def __init__(
        self,
        *,
        library: HookLibrary | None = None,
        repository: Any | None = None,
        engine: Engine | None = None,
        generator: Generator | None = None,
        database_url: str = "sqlite:///:memory:",
    ) -> None:
        self._library = library
        self._repository = repository
        self._engine = engine
        self._generator = generator or generate_with_optional_ai
        self._database_url = database_url
        self._services: Services | None = None
        self._lock = threading.Lock()

    def get(self) -> Services:
        existing = self._services
        if existing is not None:
            return existing
        with self._lock:
            if self._services is not None:
                return self._services
            active_library = self._library or HookLibrary.load_default()
            active_engine = self._engine
            owns_engine = False
            try:
                if self._repository is None:
                    if active_engine is None:
                        active_engine = create_database(self._database_url)
                        owns_engine = True
                    repository = HookRepository(active_engine)
                else:
                    repository = self._repository
            except Exception:
                if owns_engine and active_engine is not None:
                    active_engine.dispose()
                raise
            self._services = Services(
                library=active_library,
                repository=repository,
                engine=active_engine,
                generator=self._generator,
                owns_engine=owns_engine,
            )
            return self._services

    def close(self) -> None:
        with self._lock:
            services = self._services
            self._services = None
        if services is not None and services.owns_engine and services.engine is not None:
            services.engine.dispose()
