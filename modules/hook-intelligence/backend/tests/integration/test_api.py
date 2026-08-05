from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from hook_intelligence import ENGINE_VERSION
from hook_intelligence.api.main import create_app
from hook_intelligence.engine.library import HookLibrary
from hook_intelligence.storage import HookRepository, create_database


@pytest.fixture
def client():
    engine = create_database("sqlite:///:memory:")
    app = create_app(
        library=HookLibrary.load_default(),
        repository=HookRepository(engine),
        engine=engine,
    )
    with TestClient(app) as value:
        yield value
    engine.dispose()


def generation_payload(**overrides):
    value = {
        "topic": "qualidade do sono",
        "channel": "reel",
        "objective": "retention",
        "audience": "mulheres acima de 40",
        "library": "universal",
        "count": 5,
    }
    value.update(overrides)
    return value


def test_health_catalog_and_exact_public_routes(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {
        "status": "ready",
        "service": "hook-intelligence",
        "version": ENGINE_VERSION,
        "ai_enabled": False,
    }
    taxonomies = client.get("/v1/taxonomies")
    patterns = client.get("/v1/patterns")
    assert taxonomies.status_code == patterns.status_code == 200
    assert "channels" in taxonomies.json()["taxonomies"]
    assert patterns.json()["items"]
    assert client.get("/v1/not-found").status_code == 404
    assert client.get("/v1/hooks/generate").status_code == 405

    schema = client.get("/openapi.json").json()
    expected = {
        "/health",
        "/v1/taxonomies",
        "/v1/patterns",
        "/v1/hooks/generate",
        "/v1/hooks/score",
        "/v1/hooks/compliance",
        "/v1/hooks/{id}/favorite",
        "/v1/hooks/{id}",
        "/v1/history",
        "/v1/favorites",
        "/v1/exports/content-os",
    }
    assert set(schema["paths"]) == expected
    assert schema["paths"]["/v1/hooks/generate"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    for path, method in (
        ("/v1/hooks/generate", "post"),
        ("/v1/hooks/score", "post"),
        ("/v1/hooks/compliance", "post"),
        ("/v1/hooks/{id}/favorite", "post"),
        ("/v1/history", "get"),
        ("/v1/favorites", "get"),
        ("/v1/patterns", "get"),
        ("/v1/exports/content-os", "post"),
    ):
        response_schema = schema["paths"][path][method]["responses"]["422"]["content"][
            "application/json"
        ]["schema"]
        assert response_schema == {"$ref": "#/components/schemas/ErrorResponse"}


def test_generate_boundaries_order_metadata_and_persisted_history(client):
    response = client.post("/v1/hooks/generate", json=generation_payload())
    assert response.status_code == 200, response.text
    body = response.json()
    UUID(body["request_id"])
    assert body["engine_version"] == ENGINE_VERSION
    assert body["duration_ms"] >= 0
    assert all(isinstance(item, str) for item in body["warnings"])
    assert len(body["hooks"]) == 5
    scores = [hook["scores"]["overall"] for hook in body["hooks"]]
    assert scores == sorted(scores, reverse=True)
    assert any(score > 0 for score in scores)
    assert all(0 <= value <= 100 for hook in body["hooks"] for value in hook["scores"].values())
    assert all(
        "{" not in hook["explanation"] and "}" not in hook["explanation"] for hook in body["hooks"]
    )
    assert client.post("/v1/hooks/generate", json=generation_payload(count=1)).status_code == 200
    assert client.post("/v1/hooks/generate", json=generation_payload(count=50)).status_code == 200
    assert client.post("/v1/hooks/generate", json=generation_payload(count=51)).status_code == 422
    history = client.get("/v1/history", params={"page": 1, "page_size": 2}).json()
    assert history["total"] == 3
    assert history["items"][0]["request_id"]


def test_ivs_generation_score_and_compliance_real_results(client):
    generated = client.post(
        "/v1/hooks/generate", json=generation_payload(library="ivs-health", count=2)
    )
    assert generated.status_code == 200, generated.text
    score = client.post(
        "/v1/hooks/score",
        json={"text": "3 sinais sobre qualidade do sono", "channel": "reel", "topic": "sono"},
    )
    assert score.status_code == 200
    assert 0 <= score.json()["overall"] <= 100

    cases = {
        "Cuide da sua rotina com acompanhamento profissional.": "pass",
        "Este método reduz 73% do colesterol.": "review",
        "Este método cura a obesidade.": "block",
    }
    for text, status in cases.items():
        result = client.post("/v1/hooks/compliance", json={"text": text, "library": "ivs-health"})
        assert result.status_code == 200
        assert result.json()["status"] == status


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/v1/hooks/generate", generation_payload(channel="invalid")),
        ("/v1/hooks/generate", {**generation_payload(), "surprise": True}),
        ("/v1/hooks/generate", {"topic": "missing"}),
        ("/v1/hooks/score", {"text": "x" * 5000, "channel": "reel", "topic": "sono"}),
        ("/v1/hooks/score", {"text": "texto", "channel": "reel", "topic": "sono", "x": 1}),
        ("/v1/hooks/compliance", {"text": "texto", "library": "bad"}),
    ],
)
def test_strict_validation(client, path, payload):
    assert client.post(path, json=payload).status_code == 422


def test_favorite_pagination_and_export(client):
    generated = client.post("/v1/hooks/generate", json=generation_payload(count=2)).json()
    hook_id = generated["hooks"][0]["id"]
    for _ in range(2):
        response = client.post(f"/v1/hooks/{hook_id}/favorite")
        assert response.status_code == 200
        assert response.json() == {"id": hook_id, "favorite": True}
    favorites = client.get("/v1/favorites", params={"page": 1, "page_size": 1}).json()
    assert favorites["total"] == 1
    assert favorites["items"][0]["id"] == hook_id
    assert client.post("/v1/hooks/not-a-uuid/favorite").status_code == 422
    assert client.post(f"/v1/hooks/{uuid4()}/favorite").status_code == 404
    assert client.get("/v1/favorites", params={"page": 0}).status_code == 422

    exported = client.post(
        "/v1/exports/content-os",
        json={"session_id": generated["request_id"], "workspace_ref": "ivs-internal"},
    )
    assert exported.status_code == 200, exported.text
    assert exported.json()["hooks"][0]["favorite"] is True
    assert all(hook["compliance"]["status"] != "block" for hook in exported.json()["hooks"])
    assert (
        client.post(
            "/v1/exports/content-os",
            json={"session_id": str(uuid4()), "workspace_ref": "ivs-internal"},
        ).status_code
        == 404
    )
    assert client.post(
        "/v1/exports/content-os",
        json={"session_id": generated["request_id"], "workspace_ref": " "},
    ).status_code in {400, 422}


def test_concurrent_generation_history_and_favorite(client):
    def generate(index):
        return client.post(
            "/v1/hooks/generate", json=generation_payload(topic=f"sono reparador {index}", count=1)
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(generate, range(8)))
    assert all(response.status_code == 200 for response in responses)
    ids = [response.json()["hooks"][0]["id"] for response in responses]
    with ThreadPoolExecutor(max_workers=4) as pool:
        favored = list(pool.map(lambda value: client.post(f"/v1/hooks/{value}/favorite"), ids))
    assert all(response.status_code == 200 for response in favored)
    assert client.get("/v1/history", params={"page_size": 100}).json()["total"] == 8
    assert client.get("/v1/favorites", params={"page_size": 100}).json()["total"] == 8


def test_storage_error_is_sanitized_and_import_does_not_create_sqlite_file(tmp_path, monkeypatch):
    class BrokenRepository:
        def save_generation(self, _hooks):
            raise RuntimeError("sqlite:///secret/path.db token=super-secret")

    app = create_app(library=HookLibrary.load_default(), repository=BrokenRepository())
    with TestClient(app, raise_server_exceptions=False) as broken:
        response = broken.post("/v1/hooks/generate", json=generation_payload(count=1))
    assert response.status_code == 500
    assert response.json() == {"detail": "internal service error"}
    assert "secret" not in response.text
    assert list(Path(tmp_path).iterdir()) == []


def test_ai_disabled_falls_back_without_network(client, monkeypatch):
    monkeypatch.setenv("HOOK_AI_ENABLED", "false")
    response = client.post("/v1/hooks/generate", json=generation_payload(count=1, use_ai=True))
    assert response.status_code == 200
    assert response.json()["hooks"][0]["source"] == "deterministic"
    assert response.json()["hooks"][0]["scores"]["overall"] > 0
    assert "{" not in response.json()["hooks"][0]["explanation"]
    assert response.json()["warnings"]
