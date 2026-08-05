"""FastAPI application factory for the autonomous local-first service."""

from __future__ import annotations

import json
import unicodedata
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.engine import Engine
from starlette.exceptions import HTTPException as StarletteHTTPException

from hook_intelligence import ENGINE_VERSION
from hook_intelligence.adapters import ai_runtime_enabled
from hook_intelligence.api.dependencies import Generator, ServiceProvider
from hook_intelligence.api.routes import catalog, exports, history, hooks
from hook_intelligence.api.security import resolve_ownership
from hook_intelligence.domain.models import HealthResponse
from hook_intelligence.engine.library import HookLibrary

_PUBLIC_HTTP_DETAILS = {
    400: "request failed",
    404: "resource not found",
    405: "method not allowed",
    422: "request validation failed",
    500: "internal service error",
}


async def _generation_body_has_lone_surrogate(request: Request) -> bool:
    """Bridge JSON parsers that reject escaped surrogates before model validation."""

    if request.method != "POST" or request.url.path != "/v1/hooks/generate":
        return False
    try:
        payload = json.loads(await request.body())
    except (TypeError, ValueError):
        return False
    if not isinstance(payload, dict):
        return False
    values = [payload.get(field) for field in ("topic", "audience", "context", "mechanism")]
    for field in ("required_words", "forbidden_words"):
        expressions = payload.get(field)
        if isinstance(expressions, list):
            values.extend(expressions)
    return any(
        isinstance(value, str)
        and any(unicodedata.category(character) == "Cs" for character in value)
        for value in values
    )


def create_app(
    *,
    library: HookLibrary | None = None,
    repository: Any | None = None,
    engine: Engine | None = None,
    generator: Generator | None = None,
    database_url: str = "sqlite:///:memory:",
) -> FastAPI:
    """Build an isolated app; caller-owned engines are never disposed by the app."""

    services = ServiceProvider(
        library=library,
        repository=repository,
        engine=engine,
        generator=generator,
        database_url=database_url,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        lease = services.acquire_lease()
        try:
            yield
        finally:
            services.release(lease)

    application = FastAPI(
        title="Hook Intelligence Engine",
        description=(
            "Local-first hook generation API. REVIEW is not publication approval, and no "
            "content is approved or published automatically."
        ),
        version=ENGINE_VERSION,
        lifespan=lifespan,
    )
    application.state.services = services

    @application.middleware("http")
    async def authenticate_integration_context(request: Request, call_next: Any) -> Any:
        if request.method == "GET" and request.url.path == "/health":
            return await call_next(request)
        ownership = await resolve_ownership(request)
        if ownership is None:
            return JSONResponse(status_code=401, content={"detail": "authentication failed"})
        request.state.hook_ownership = ownership
        return await call_next(request)

    @application.middleware("http")
    async def reject_duplicate_query_scalars(request: Request, call_next: Any) -> Any:
        if any(len(request.query_params.getlist(key)) != 1 for key in request.query_params):
            return JSONResponse(status_code=422, content={"detail": "request validation failed"})
        return await call_next(request)

    @application.exception_handler(RequestValidationError)
    async def request_validation_error(
        request: Request, _exc: RequestValidationError
    ) -> JSONResponse:
        if await _generation_body_has_lone_surrogate(request):
            return JSONResponse(status_code=400, content={"detail": "request failed"})
        return JSONResponse(status_code=422, content={"detail": "request validation failed"})

    @application.exception_handler(StarletteHTTPException)
    async def http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Detail e headers podem vir de rotas/componentes injetados e são sempre não confiáveis.
        detail = _PUBLIC_HTTP_DETAILS.get(exc.status_code, "request failed")
        return JSONResponse(status_code=exc.status_code, content={"detail": detail})

    @application.exception_handler(Exception)
    async def internal_error(_request: Request, _exc: Exception) -> JSONResponse:
        # Never serialize or log exception strings: they may contain SQL, paths, URLs, or secrets.
        return JSONResponse(status_code=500, content={"detail": "internal service error"})

    @application.get(
        "/health",
        response_model=HealthResponse,
        responses={
            200: {
                "content": {
                    "application/json": {
                        "example": {
                            "status": "ready",
                            "service": "hook-intelligence",
                            "version": ENGINE_VERSION,
                            "ai_enabled": False,
                        }
                    }
                }
            }
        },
        tags=["system"],
        summary="Service readiness",
    )
    def health() -> HealthResponse:
        return HealthResponse(ai_enabled=ai_runtime_enabled())

    application.include_router(catalog.router)
    application.include_router(hooks.router)
    application.include_router(history.router)
    application.include_router(exports.router)
    return application


# Importing this module performs no library load and creates no SQLite database or file.
app = create_app()

__all__ = ["app", "create_app"]
