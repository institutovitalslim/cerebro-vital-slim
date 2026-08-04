import asyncio

from starlette.requests import Request
from starlette.responses import JSONResponse

from app import main
from app.auth_core import make_token
from app.config import settings


def make_request(path: str, cookie: str | None = None) -> Request:
    headers = []
    if cookie:
        headers.append((b"cookie", f"cos_session={cookie}".encode()))
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"tenant_slug=demo",
            "headers": headers,
            "client": ("127.0.0.1", 1234),
            "server": ("test", 80),
        }
    )


def test_auth_gate_attaches_signed_tenant_identity(monkeypatch) -> None:
    monkeypatch.setattr(settings, "content_os_secret", "x" * 32)
    token = make_token("user", "tenant-123", "user@example.com", ttl=60)
    request = make_request("/protected", token)

    async def next_handler(req: Request) -> JSONResponse:
        return JSONResponse({"tenant": req.state.session["tid"]})

    response = asyncio.run(main.auth_gate(request, next_handler))
    assert response.status_code == 200
    assert response.body == b'{"tenant":"tenant-123"}'


def test_tenant_lookup_error_fails_closed(monkeypatch) -> None:
    request = make_request(
        "/generation/creatives/3fa85f64-5717-4562-b3fc-2c963f66afa6/edit"
    )
    request.state.session = {"tid": "tenant-123"}

    def broken_connection():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(main, "_get_conn", broken_connection)

    async def next_handler(_req: Request) -> JSONResponse:
        return JSONResponse({"unsafe": True})

    response = asyncio.run(main.tenant_isolation(request, next_handler))
    assert response.status_code == 404
    assert b"unsafe" not in response.body
