import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock

import pytest
from fastapi.testclient import TestClient

from hook_intelligence.api import dependencies
from hook_intelligence.api.dependencies import ServiceProvider
from hook_intelligence.api.main import create_app
from hook_intelligence.domain.models import GenerationRequest
from hook_intelligence.engine.library import HookLibrary
from hook_intelligence.engine.pipeline import generate_deterministic, validate_generation_request


def _payload(**updates):
    value = {
        "topic": "qualidade do sono",
        "channel": "reel",
        "objective": "retention",
        "audience": "mulheres acima de 40",
        "library": "universal",
        "count": 1,
    }
    value.update(updates)
    return value


def test_overlapping_lifespans_keep_history_and_favorites_until_last_exit():
    app = create_app()

    with TestClient(app) as outer:
        generated = outer.post("/v1/hooks/generate", json=_payload())
        assert generated.status_code == 200, generated.text
        hook_id = generated.json()["hooks"][0]["id"]
        assert outer.post(f"/v1/hooks/{hook_id}/favorite").status_code == 200
        assert outer.get("/v1/history").json()["total"] == 1
        assert outer.get("/v1/favorites").json()["total"] == 1

        with TestClient(app) as inner:
            assert inner.get("/v1/history").json()["total"] == 1
            assert inner.get("/v1/favorites").json()["total"] == 1

        assert outer.get("/v1/history").json()["total"] == 1
        assert outer.get("/v1/favorites").json()["total"] == 1

    with TestClient(app) as fresh:
        assert fresh.get("/v1/history").json()["total"] == 0
        assert fresh.get("/v1/favorites").json()["total"] == 0


class _SpyEngine:
    def __init__(self):
        self.dispose_calls = 0
        self._lock = Lock()

    def dispose(self):
        with self._lock:
            self.dispose_calls += 1


class _Repository:
    pass


def test_provider_owned_engine_closes_only_on_last_release(monkeypatch):
    engine = _SpyEngine()
    monkeypatch.setattr(dependencies, "create_database", lambda _url: engine)
    monkeypatch.setattr(dependencies, "HookRepository", lambda _engine: _Repository())
    provider = ServiceProvider(library=HookLibrary.load_default())

    first = provider.acquire()
    second = provider.acquire()
    assert first is second
    provider.release()
    assert engine.dispose_calls == 0
    provider.release()
    assert engine.dispose_calls == 1
    provider.release()
    assert engine.dispose_calls == 1


def test_nested_app_lifespans_close_owned_engine_only_after_outer_exit(monkeypatch):
    engine = _SpyEngine()
    monkeypatch.setattr(dependencies, "create_database", lambda _url: engine)
    monkeypatch.setattr(dependencies, "HookRepository", lambda _engine: _Repository())
    app = create_app(library=HookLibrary.load_default())

    with TestClient(app):
        with TestClient(app):
            pass
        assert engine.dispose_calls == 0
    assert engine.dispose_calls == 1


def test_provider_never_closes_injected_engine():
    engine = _SpyEngine()
    provider = ServiceProvider(
        library=HookLibrary.load_default(), repository=_Repository(), engine=engine
    )
    provider.acquire()
    provider.acquire()
    provider.release()
    provider.release()
    provider.close()
    assert engine.dispose_calls == 0


def test_provider_ten_concurrent_overlapping_leases_close_exactly_once(monkeypatch):
    engine = _SpyEngine()
    monkeypatch.setattr(dependencies, "create_database", lambda _url: engine)
    monkeypatch.setattr(dependencies, "HookRepository", lambda _engine: _Repository())
    provider = ServiceProvider(library=HookLibrary.load_default())
    entered = Barrier(10)
    leaving = Barrier(10)

    def worker():
        services = provider.acquire()
        entered.wait(timeout=5)
        leaving.wait(timeout=5)
        provider.release()
        return services

    with ThreadPoolExecutor(max_workers=10) as executor:
        services = list(executor.map(lambda _index: worker(), range(10)))

    assert all(item is services[0] for item in services)
    assert engine.dispose_calls == 1


def test_sequential_lifespans_create_and_close_distinct_owned_engines(monkeypatch):
    engines = []

    def create(_url):
        engine = _SpyEngine()
        engines.append(engine)
        return engine

    monkeypatch.setattr(dependencies, "create_database", create)
    monkeypatch.setattr(dependencies, "HookRepository", lambda engine: {"engine": engine})
    provider = ServiceProvider(library=HookLibrary.load_default())

    first = provider.acquire()
    provider.release()
    second = provider.acquire()
    provider.release()

    assert first is not second
    assert first.engine is engines[0]
    assert second.engine is engines[1]
    assert [engine.dispose_calls for engine in engines] == [1, 1]


def test_failed_acquire_releases_lease_and_allows_clean_retry(monkeypatch):
    engines = []
    repository_attempts = 0

    def create(_url):
        engine = _SpyEngine()
        engines.append(engine)
        return engine

    def repository(_engine):
        nonlocal repository_attempts
        repository_attempts += 1
        if repository_attempts == 1:
            raise RuntimeError("initialization failed")
        return _Repository()

    monkeypatch.setattr(dependencies, "create_database", create)
    monkeypatch.setattr(dependencies, "HookRepository", repository)
    provider = ServiceProvider(library=HookLibrary.load_default())

    with pytest.raises(RuntimeError, match="initialization failed"):
        provider.acquire()
    assert engines[0].dispose_calls == 1

    services = provider.acquire()
    assert services.engine is engines[1]
    provider.release()
    assert [engine.dispose_calls for engine in engines] == [1, 1]


@pytest.mark.parametrize("control", ["\x00", "\u202e", "\u200b", "\ufeff", "\ud800"])
@pytest.mark.parametrize(
    "field",
    ["topic", "audience", "context", "mechanism", "required_words", "forbidden_words"],
)
def test_generation_rejects_unicode_category_c_before_generator(field, control):
    calls = 0
    writes = []

    class Repository:
        def save_generation(self, hooks):
            writes.append(hooks)
            raise AssertionError("must not write")

    def generator(_request, _library):
        nonlocal calls
        calls += 1
        return ()

    value = f"seguro{control}texto"
    update = {field: [value] if field.endswith("_words") else value}
    app = create_app(
        library=HookLibrary.load_default(), repository=Repository(), generator=generator
    )
    response = TestClient(app, raise_server_exceptions=False).post(
        "/v1/hooks/generate",
        content=json.dumps(_payload(**update), ensure_ascii=True),
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "request failed"}
    assert control not in response.text
    assert calls == 0
    assert writes == []


def test_generation_accepts_legitimate_unicode_and_editorial_whitespace():
    app = create_app(library=HookLibrary.load_default(), repository=_MemoryRepository())
    response = TestClient(app).post(
        "/v1/hooks/generate",
        json=_payload(
            topic="  saúde\t cardiovascular ❤️  ",
            audience="pessoas\n acima de 40 anos 😊",
            context="conteúdo\r\n editorial em português",
            required_words=[" saúde ", "SAÚDE"],
        ),
    )
    assert response.status_code == 200, response.text


class _MemoryRepository:
    def save_generation(self, _hooks):
        return "00000000-0000-0000-0000-000000000001"


@pytest.mark.parametrize(
    "field,value",
    [
        ("topic", "tema\x00oculto"),
        ("audience", "público\u202eoculto"),
        ("context", "contexto\u200boculto"),
        ("mechanism", "authority\ufeff"),
        ("required_words", ["termo\ud800"]),
        ("forbidden_words", ["termo\x00"]),
    ],
)
def test_direct_pipeline_rejects_category_c_from_unvalidated_models(field, value):
    valid = GenerationRequest.model_validate(_payload())
    raw = valid.model_dump(mode="python")
    raw[field] = value
    request = GenerationRequest.model_construct(**raw)
    with pytest.raises(ValueError, match="request inválida"):
        validate_generation_request(request)
    with pytest.raises(ValueError, match="request inválida"):
        generate_deterministic(request)
