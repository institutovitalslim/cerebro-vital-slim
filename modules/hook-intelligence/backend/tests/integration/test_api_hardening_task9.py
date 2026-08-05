import copy
import math
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from hook_intelligence.api.main import create_app
from hook_intelligence.domain.models import ComplianceResult, ComplianceStatus, Hook, HookScores
from hook_intelligence.engine.library import HookLibrary
from hook_intelligence.engine.pipeline import generate_deterministic


def payload(**updates):
    value = {
        "topic": "qualidade do sono",
        "channel": "reel",
        "objective": "retention",
        "audience": "mulheres acima de 40",
        "library": "universal",
        "count": 2,
    }
    value.update(updates)
    return value


class MemoryRepository:
    def __init__(self):
        self.saved = []

    def save_generation(self, hooks):
        self.saved.append(tuple(hooks))
        return str(uuid4())

    def list_sessions(self, page=1, page_size=20):
        return {"items": [], "total": len(self.saved), "page": page, "page_size": page_size}

    def list_favorites(self, page=1, page_size=20):
        return {"items": [], "total": 0, "page": page, "page_size": page_size}


def make_client(generator):
    repository = MemoryRepository()
    app = create_app(library=HookLibrary.load_default(), repository=repository, generator=generator)
    return TestClient(app, raise_server_exceptions=False), repository


def valid_hooks(request, library):
    return generate_deterministic(request, library)


def test_validation_errors_never_reflect_secret_or_input(caplog):
    client, _ = make_client(valid_hooks)
    probes = [
        client.post(
            "/v1/hooks/score",
            json={"text": "TOP-SECRET" * 1000, "channel": "reel", "topic": "sono"},
        ),
        client.post(
            "/v1/hooks/compliance", json={"text": "ok", "library": "universal", "TOP-SECRET": True}
        ),
        client.post("/v1/hooks/TOP-SECRET/favorite"),
        client.get("/v1/history?page=TOP-SECRET"),
        client.post(
            "/v1/hooks/generate",
            content='{"topic":"TOP-SECRET"',
            headers={"content-type": "application/json"},
        ),
    ]
    for response in probes:
        assert response.status_code == 422
        assert response.json() == {"detail": "request validation failed"}
        assert len(response.content) < 100
    assert "TOP-SECRET" not in caplog.text


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("count", True),
        ("count", "2"),
        ("intensity", True),
        ("intensity", "2"),
        ("max_length", True),
        ("max_length", "180"),
        ("use_ai", "false"),
    ],
)
def test_generate_public_numeric_and_boolean_types_are_strict(field, value):
    client, _ = make_client(valid_hooks)
    assert client.post("/v1/hooks/generate", json=payload(**{field: value})).status_code == 422


def test_generator_output_is_sorted_and_same_snapshot_is_persisted():
    def ascending(request, library):
        hooks = list(generate_deterministic(request, library))
        hooks[0] = hooks[0].model_copy(
            update={"scores": hooks[0].scores.model_copy(update={"overall": 10})}
        )
        hooks[1] = hooks[1].model_copy(
            update={"scores": hooks[1].scores.model_copy(update={"overall": 90})}
        )
        return tuple(hooks)

    client, repository = make_client(ascending)
    response = client.post("/v1/hooks/generate", json=payload())
    assert response.status_code == 200, response.text
    assert [h["scores"]["overall"] for h in response.json()["hooks"]] == [90, 10]
    assert [h.scores.overall for h in repository.saved[0]] == [90, 10]


@pytest.mark.parametrize(
    "corruption", ["short", "required", "forbidden", "metadata", "duplicate", "block", "nan"]
)
def test_invalid_generator_batch_is_internal_failure_and_never_persisted(corruption):
    def generator(request, library):
        hooks = list(generate_deterministic(request, library))
        if corruption == "short":
            hooks.pop()
        elif corruption == "required":
            hooks[0] = hooks[0].model_copy(
                update={"text": hooks[0].text.replace("obrigatória", "ignorada")}
            )
        elif corruption == "forbidden":
            hooks[0] = hooks[0].model_copy(update={"text": hooks[0].text + " proibida"})
        elif corruption == "metadata":
            hooks[0] = hooks[0].model_copy(update={"audience": "outra"})
        elif corruption == "duplicate":
            hooks[1] = hooks[1].model_copy(update={"id": hooks[0].id})
        elif corruption == "block":
            hooks[0] = hooks[0].model_copy(
                update={"compliance": ComplianceResult(status=ComplianceStatus.BLOCK)}
            )
        elif corruption == "nan":
            scores = hooks[0].scores.model_copy(update={"overall": math.nan})
            hooks[0] = hooks[0].model_copy(update={"scores": scores})
        return tuple(hooks)

    request = payload()
    if corruption == "required":
        request["required_words"] = ["obrigatória"]
    if corruption == "forbidden":
        request["forbidden_words"] = ["proibida"]
    client, repository = make_client(generator)
    response = client.post("/v1/hooks/generate", json=request)
    assert response.status_code == 500
    assert response.json() == {"detail": "internal service error"}
    assert repository.saved == []


@pytest.mark.parametrize(
    "kind", ["list", "tuple_subclass", "iterator", "mapping", "hook_subclass", "constructed"]
)
def test_adversarial_generator_container_and_models_are_rejected(kind):
    class EvilTuple(tuple):
        pass

    class EvilHook(Hook):
        pass

    def generator(request, library):
        hooks = generate_deterministic(request, library)
        if kind == "list":
            return list(hooks)
        if kind == "tuple_subclass":
            return EvilTuple(hooks)
        if kind == "iterator":
            return iter(hooks)
        if kind == "mapping":
            return {index: hook for index, hook in enumerate(hooks)}
        if kind == "hook_subclass":
            return (EvilHook.model_validate(hooks[0].model_dump()), hooks[1])
        raw = hooks[0].model_dump()
        raw["scores"]["overall"] = math.inf
        return (Hook.model_construct(**raw), hooks[1])

    client, repository = make_client(generator)
    response = client.post("/v1/hooks/generate", json=payload())
    assert response.status_code == 500
    assert response.json() == {"detail": "internal service error"}
    assert repository.saved == []


def test_generator_type_and_value_errors_are_internal_failures():
    for error in (TypeError("TOP-SECRET"), ValueError("TOP-SECRET")):

        def broken(_request, _library, failure=error):
            raise failure

        client, repository = make_client(broken)
        response = client.post("/v1/hooks/generate", json=payload())
        assert response.status_code == 500
        assert response.json() == {"detail": "internal service error"}
        assert "TOP-SECRET" not in response.text
        assert repository.saved == []


def test_request_domain_error_is_400_before_generator():
    called = False

    def generator(_request, _library):
        nonlocal called
        called = True
        return ()

    client, repository = make_client(generator)
    response = client.post(
        "/v1/hooks/generate",
        json=payload(required_words=["mesma"], forbidden_words=["MESMA"]),
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "generation request cannot be fulfilled"}
    assert called is False
    assert repository.saved == []


def test_request_and_generator_hooks_are_not_mutated():
    original_request = payload()
    before = copy.deepcopy(original_request)
    returned = []
    snapshots = []

    def generator(request, library):
        hooks = generate_deterministic(request, library)
        returned.extend(hooks)
        snapshots.extend(hook.model_dump() for hook in hooks)
        return hooks

    client, _ = make_client(generator)
    assert client.post("/v1/hooks/generate", json=original_request).status_code == 200
    assert original_request == before
    assert [hook.model_dump() for hook in returned] == snapshots


@pytest.mark.parametrize(
    "path",
    [
        "/v1/history?page=1&page=2",
        "/v1/favorites?page_size=1&page_size=2",
        "/v1/patterns?library=universal&library=ivs-health",
    ],
)
def test_duplicate_scalar_queries_are_rejected(path):
    client, _ = make_client(valid_hooks)
    response = client.get(path)
    assert response.status_code == 422
    assert response.json() == {"detail": "request validation failed"}


def test_health_reports_effective_dynamic_ai_configuration(monkeypatch):
    client, _ = make_client(valid_hooks)
    monkeypatch.setenv("HOOK_AI_ENABLED", "false")
    assert client.get("/health").json()["ai_enabled"] is False
    monkeypatch.setenv("HOOK_AI_ENABLED", "true")
    monkeypatch.setenv("HOOK_AI_API_KEY", "safe-key")
    monkeypatch.setenv("HOOK_AI_MODEL", "safe-model")
    assert client.get("/health").json()["ai_enabled"] is True
    monkeypatch.setenv("HOOK_AI_ENDPOINT", "not-a-url")
    assert client.get("/health").json()["ai_enabled"] is False


def test_non_finite_score_and_duration_contracts_rejected():
    base = {
        "clarity": 1,
        "specificity": 1,
        "novelty": 1,
        "retention": 1,
        "channel_fit": 1,
        "overall": 1,
    }
    for value in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValidationError):
            HookScores(**{**base, "overall": value})
