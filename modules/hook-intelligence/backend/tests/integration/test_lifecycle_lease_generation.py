from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock

from hook_intelligence.api import dependencies
from hook_intelligence.api.dependencies import ServiceProvider
from hook_intelligence.engine.library import HookLibrary


class _SpyEngine:
    def __init__(self):
        self.dispose_calls = 0
        self._lock = Lock()

    def dispose(self):
        with self._lock:
            self.dispose_calls += 1


class _Repository:
    pass


def _provider(monkeypatch):
    engines = []

    def create(_url):
        engine = _SpyEngine()
        engines.append(engine)
        return engine

    monkeypatch.setattr(dependencies, "create_database", create)
    monkeypatch.setattr(dependencies, "HookRepository", lambda _engine: _Repository())
    return ServiceProvider(library=HookLibrary.load_default()), engines


def test_late_old_release_cannot_dispose_new_snapshot(monkeypatch):
    provider, engines = _provider(monkeypatch)
    old = provider.acquire_lease()
    provider.close()
    new = provider.acquire_lease()

    provider.release(old)

    assert [engine.dispose_calls for engine in engines] == [1, 0]
    assert provider.get() is new.services
    provider.release(new)
    assert [engine.dispose_calls for engine in engines] == [1, 1]


def test_legacy_services_release_is_also_bound_to_old_snapshot(monkeypatch):
    provider, engines = _provider(monkeypatch)
    old_services = provider.acquire()
    provider.close()
    new_services = provider.acquire()

    provider.release(old_services)

    assert [engine.dispose_calls for engine in engines] == [1, 0]
    assert provider.get() is new_services
    provider.release(new_services)
    assert [engine.dispose_calls for engine in engines] == [1, 1]


def test_duplicate_token_release_is_idempotent(monkeypatch):
    provider, engines = _provider(monkeypatch)
    lease = provider.acquire_lease()

    provider.release(lease)
    provider.release(lease)

    assert engines[0].dispose_calls == 1


def test_close_and_release_same_generation_dispose_exactly_once(monkeypatch):
    provider, engines = _provider(monkeypatch)
    lease = provider.acquire_lease()

    with ThreadPoolExecutor(max_workers=2) as executor:
        list(
            executor.map(lambda action: action(), (provider.close, lambda: provider.release(lease)))
        )

    assert engines[0].dispose_calls == 1


def test_repeated_threaded_aba_never_releases_new_generation(monkeypatch):
    provider, engines = _provider(monkeypatch)

    for iteration in range(100):
        old = provider.acquire_lease()
        provider.close()
        new = provider.acquire_lease()
        barrier = Barrier(2)

        def release_old(old_lease=old, sync=barrier):
            sync.wait(timeout=5)
            provider.release(old_lease)

        def observe_new(new_lease=new, sync=barrier):
            sync.wait(timeout=5)
            assert provider.get() is new_lease.services

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(release_old), executor.submit(observe_new)]
            for future in futures:
                future.result(timeout=5)

        assert engines[iteration * 2 + 1].dispose_calls == 0
        assert provider.get() is new.services
        provider.release(new)

    assert all(engine.dispose_calls == 1 for engine in engines)
