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
        self._active_leases = 0
        self._lock = threading.Lock()

    def get(self) -> Services:
        active_engine: Engine | None = None
        owns_engine = False
        try:
            with self._lock:
                if self._services is not None:
                    return self._services
                active_library = self._library or HookLibrary.load_default()
                active_engine = self._engine
                if self._repository is None:
                    if active_engine is None:
                        active_engine = create_database(self._database_url)
                        owns_engine = True
                    repository = HookRepository(active_engine)
                else:
                    repository = self._repository
                self._services = Services(
                    library=active_library,
                    repository=repository,
                    engine=active_engine,
                    generator=self._generator,
                    owns_engine=owns_engine,
                )
                return self._services
        except BaseException:
            # Disposal callbacks may re-enter the provider, so never invoke one under its lock.
            if owns_engine and active_engine is not None:
                active_engine.dispose()
            raise

    def acquire(self) -> Services:
        """Register a lifespan lease and return its shared service snapshot."""

        with self._lock:
            self._active_leases += 1
        try:
            return self.get()
        except BaseException:
            self.release()
            raise

    def release(self) -> None:
        """Release one lease, disposing owned resources only after the final lease."""

        with self._lock:
            if self._active_leases == 0:
                return
            self._active_leases -= 1
            if self._active_leases != 0:
                return
            services = self._services
            self._services = None
        self._dispose(services)

    def close(self) -> None:
        """Force-close the current snapshot, independently of lifespan leases."""

        with self._lock:
            services = self._services
            self._services = None
            self._active_leases = 0
        self._dispose(services)

    @staticmethod
    def _dispose(services: Services | None) -> None:
        if services is not None and services.owns_engine and services.engine is not None:
            services.engine.dispose()
