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


@dataclass(eq=False, slots=True)
class ServiceLease:
    """Opaque, single-use lease bound to one service snapshot generation."""

    services: Services
    generation: int
    _provider: ServiceProvider
    _lease_id: int
    _released: bool = False


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
        self._generation = 0
        self._next_lease_id = 0
        self._leases: dict[int, ServiceLease] = {}
        # Keep invalidated compatibility acquisitions until their delayed release. This
        # prevents an anonymous old release from consuming a newer generation's lease.
        self._legacy_leases: list[ServiceLease] = []
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
                self._generation += 1
                return self._services
        except BaseException:
            # Disposal callbacks may re-enter the provider, so never invoke one under its lock.
            if owns_engine and active_engine is not None:
                active_engine.dispose()
            raise

    def acquire(self) -> Services:
        """Compatibility API; new lifecycle code should retain ``acquire_lease()``."""

        lease = self.acquire_lease()
        with self._lock:
            self._legacy_leases.append(lease)
        return lease.services

    def acquire_lease(self) -> ServiceLease:
        """Acquire a unique lease bound to the current service generation."""

        while True:
            services = self.get()
            with self._lock:
                # close() may detach the snapshot between get() and this lock.
                if self._services is not services:
                    continue
                self._next_lease_id += 1
                lease = ServiceLease(
                    services=services,
                    generation=self._generation,
                    _provider=self,
                    _lease_id=self._next_lease_id,
                )
                self._leases[lease._lease_id] = lease
                return lease

    def release(self, lease: ServiceLease | Services | None = None) -> None:
        """Release one acquisition without affecting any later generation."""

        with self._lock:
            token = self._resolve_lease_locked(lease)
            if token is None or token._released:
                return
            token._released = True
            active = self._leases.pop(token._lease_id, None)
            if active is not token:
                return
            if self._services is not token.services or self._leases:
                return
            services = self._services
            self._services = None
        self._dispose(services)

    def close(self) -> None:
        """Force-close the current snapshot and invalidate only its leases."""

        with self._lock:
            services = self._services
            self._services = None
            for lease in self._leases.values():
                lease._released = True
            self._leases.clear()
        self._dispose(services)

    def _resolve_lease_locked(self, lease: ServiceLease | Services | None) -> ServiceLease | None:
        if isinstance(lease, ServiceLease):
            if lease._provider is not self:
                return None
            for index, legacy in enumerate(self._legacy_leases):
                if legacy is lease:
                    self._legacy_leases.pop(index)
                    break
            return lease

        for index, legacy in enumerate(self._legacy_leases):
            if lease is None or legacy.services is lease:
                return self._legacy_leases.pop(index)
        return None

    @staticmethod
    def _dispose(services: Services | None) -> None:
        if services is not None and services.owns_engine and services.engine is not None:
            services.engine.dispose()
