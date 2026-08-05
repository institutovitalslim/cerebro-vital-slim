from __future__ import annotations

import asyncio
import hashlib
import hmac

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import settings
from app.routers.hook_intelligence import get_hook_client, router
from app.services.hook_intelligence_client import HookIntelligenceClient


class StubHookClient:
    async def forward(
        self,
        method: str,
        path: str,
        *,
        query: str,
        body: bytes,
        tenant_id: str,
        user_id: str,
    ) -> httpx.Response:
        assert method == "POST"
        assert path == "v1/hooks/generate"
        assert query == "mode=deterministic"
        assert body == b'{"topic":"sono"}'
        assert tenant_id == "tenant-123"
        assert user_id == "user-456"
        return httpx.Response(
            200,
            headers={"content-type": "application/json", "x-private": "drop"},
            content=b'{"request_id":"req-1"}',
        )


class FailingHookClient:
    async def forward(self, *args, **kwargs) -> httpx.Response:
        raise httpx.ConnectError("internal host must not leak")


def build_client(dependency, *, enabled: bool = True) -> TestClient:
    settings.hook_intelligence_enabled = enabled
    app = FastAPI()

    @app.middleware("http")
    async def attach_test_session(request, call_next):
        request.state.session = {"tid": "tenant-123", "uid": "user-456"}
        return await call_next(request)

    app.include_router(router)
    app.dependency_overrides[get_hook_client] = lambda: dependency
    return TestClient(app)


def test_gateway_forwards_allowlisted_path_and_tenant_context() -> None:
    response = build_client(StubHookClient()).post(
        "/hook-intelligence/v1/hooks/generate?mode=deterministic",
        content=b'{"topic":"sono"}',
        headers={"x-content-os-tenant": "tenant-123"},
    )

    assert response.status_code == 200
    assert response.json() == {"request_id": "req-1"}
    assert "x-private" not in response.headers


def test_gateway_rejects_unknown_paths_before_upstream() -> None:
    response = build_client(StubHookClient()).get(
        "/hook-intelligence/admin/secrets",
        headers={"x-content-os-tenant": "tenant-123"},
    )
    assert response.status_code == 404


def test_gateway_sanitizes_upstream_failures() -> None:
    response = build_client(FailingHookClient()).get(
        "/hook-intelligence/v1/taxonomies",
        headers={"x-content-os-tenant": "tenant-123"},
    )
    assert response.status_code == 503
    assert response.json() == {"detail": "Hook Intelligence temporariamente indisponível"}
    assert "internal host" not in response.text


def test_gateway_is_closed_when_feature_flag_is_off() -> None:
    response = build_client(StubHookClient(), enabled=False).get(
        "/hook-intelligence/v1/taxonomies",
    )
    assert response.status_code == 503
    assert response.json() == {"detail": "Hook Intelligence desativado"}


def test_gateway_rejects_oversized_payload() -> None:
    response = build_client(StubHookClient()).post(
        "/hook-intelligence/v1/hooks/generate",
        content=b"x" * (256 * 1024 + 1),
    )
    assert response.status_code == 413


def test_gateway_closes_client_when_request_is_rejected_early(monkeypatch) -> None:
    import app.routers.hook_intelligence as gateway_module

    closed = 0

    class TrackingClient:
        def __init__(self, **_kwargs) -> None:
            pass

        async def close(self) -> None:
            nonlocal closed
            closed += 1

    monkeypatch.setattr(settings, "hook_intelligence_enabled", True)
    monkeypatch.setattr(settings, "hook_integration_secret", "test-secret")
    monkeypatch.setattr(settings, "hook_intelligence_url", "http://hook-intelligence-api:8000")
    monkeypatch.setattr(gateway_module, "HookIntelligenceClient", TrackingClient)

    app = FastAPI()

    @app.middleware("http")
    async def attach_test_session(request, call_next):
        request.state.session = {"tid": "tenant-123", "uid": "user-456"}
        return await call_next(request)

    app.include_router(router)
    with TestClient(app) as client:
        assert client.get("/hook-intelligence/admin/secrets").status_code == 404
    assert closed == 1


def test_main_app_requires_signed_session_for_gateway() -> None:
    from app.main import app as content_engine_app

    response = TestClient(content_engine_app).get(
        "/hook-intelligence/v1/taxonomies",
    )
    assert response.status_code == 401


def test_client_signs_tenant_and_user_context() -> None:
    secret = "integration-test-secret"
    observed: dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        observed.update(request.headers)
        return httpx.Response(200, json={"ok": True})

    async def exercise() -> None:
        client = HookIntelligenceClient(
            base_url="http://hook-intelligence-api:8000",
            integration_secret=secret,
            transport=httpx.MockTransport(handler),
        )
        try:
            await client.forward(
                "GET",
                "v1/history",
                query="",
                body=b"",
                tenant_id="tenant-123",
                user_id="user-456",
            )
        finally:
            await client.close()

    asyncio.run(exercise())
    timestamp = observed["x-content-os-timestamp"]
    body_digest = hashlib.sha256(b"").hexdigest()
    message = "\n".join(
        (
            "tenant-123",
            "user-456",
            timestamp,
            "GET",
            "/v1/history",
            "",
            body_digest,
        )
    ).encode()
    expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    assert observed["x-content-os-tenant"] == "tenant-123"
    assert observed["x-content-os-user"] == "user-456"
    assert hmac.compare_digest(observed["x-content-os-signature"], expected)


def test_client_rejects_unsafe_base_url() -> None:
    for unsafe_url in (
        "http://example.com:18082",
        "https://example.com",
        "http://user:password@localhost:18082",
    ):
        with pytest.raises(ValueError, match="approved internal endpoint"):
            HookIntelligenceClient(
                base_url=unsafe_url,
                integration_secret="test-secret",
            )
