from __future__ import annotations

import re
from collections.abc import AsyncIterator

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.config import settings
from app.services.hook_intelligence_client import HookIntelligenceClient

router = APIRouter(
    prefix="/hook-intelligence",
    tags=["hook-intelligence"],
)

_ALLOWED = (
    re.compile(r"^v1/taxonomies$"),
    re.compile(r"^v1/patterns$"),
    re.compile(r"^v1/hooks/generate$"),
    re.compile(r"^v1/hooks/[0-9a-fA-F-]{36}$"),
    re.compile(r"^v1/hooks/[0-9a-fA-F-]{36}/favorite$"),
    re.compile(r"^v1/history$"),
    re.compile(r"^v1/favorites$"),
    re.compile(r"^v1/exports/content-os$"),
)
_ALLOWED_RESPONSE_HEADERS = {"content-type", "content-disposition"}
_MAX_BODY_BYTES = 256 * 1024


async def get_hook_client() -> AsyncIterator[HookIntelligenceClient]:
    if not settings.hook_intelligence_enabled:
        raise HTTPException(status_code=503, detail="Hook Intelligence desativado")
    if not settings.hook_integration_secret:
        raise HTTPException(
            status_code=503,
            detail="Hook Intelligence temporariamente indisponível",
        )
    client = HookIntelligenceClient(
        base_url=settings.hook_intelligence_url,
        timeout_seconds=settings.hook_intelligence_timeout_seconds,
        integration_secret=settings.hook_integration_secret,
    )
    try:
        yield client
    finally:
        await client.close()


async def _forward_request(
    path: str,
    request: Request,
    client: HookIntelligenceClient,
) -> Response:
    if not settings.hook_intelligence_enabled:
        raise HTTPException(
            status_code=503,
            detail="Hook Intelligence desativado",
        )
    if not any(pattern.fullmatch(path) for pattern in _ALLOWED):
        raise HTTPException(status_code=404, detail="rota não encontrada")

    session = getattr(request.state, "session", None)
    tenant_id = session.get("tid") if isinstance(session, dict) else None
    user_id = session.get("uid") if isinstance(session, dict) else None
    if not tenant_id or not user_id:
        raise HTTPException(status_code=401, detail="não autenticado")

    body = await request.body()
    if len(body) > _MAX_BODY_BYTES:
        raise HTTPException(status_code=413, detail="payload excede o limite permitido")

    try:
        upstream = await client.forward(
            request.method,
            path,
            query=request.url.query,
            body=body,
            tenant_id=str(tenant_id),
            user_id=str(user_id),
        )
    except (httpx.HTTPError, TimeoutError):
        raise HTTPException(
            status_code=503,
            detail="Hook Intelligence temporariamente indisponível",
        ) from None
    headers = {
        key: value
        for key, value in upstream.headers.items()
        if key.lower() in _ALLOWED_RESPONSE_HEADERS
    }
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=headers,
        media_type=None,
    )


@router.get("/{path:path}", operation_id="hook_intelligence_gateway_get")
async def hook_intelligence_gateway_get(
    path: str,
    request: Request,
    client: HookIntelligenceClient = Depends(get_hook_client),
) -> Response:
    return await _forward_request(path, request, client)


@router.post("/{path:path}", operation_id="hook_intelligence_gateway_post")
async def hook_intelligence_gateway_post(
    path: str,
    request: Request,
    client: HookIntelligenceClient = Depends(get_hook_client),
) -> Response:
    return await _forward_request(path, request, client)
