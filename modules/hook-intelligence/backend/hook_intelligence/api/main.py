"""FastAPI application factory for the autonomous local-first service."""

from __future__ import annotations

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
from hook_intelligence.domain.models import HealthResponse
from hook_intelligence.engine.library import HookLibrary


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
        try:
            yield
        finally:
            services.close()

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
    async def reject_duplicate_query_scalars(request: Request, call_next: Any) -> Any:
        if any(len(request.query_params.getlist(key)) != 1 for key in request.query_params):
            return JSONResponse(status_code=422, content={"detail": "request validation failed"})
        return await call_next(request)

    @application.exception_handler(RequestValidationError)
    async def request_validation_error(
        _request: Request, _exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": "request validation failed"})

    @application.exception_handler(StarletteHTTPException)
    async def http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail if type(exc.detail) is str else "request failed"
        return JSONResponse(
            status_code=exc.status_code, content={"detail": detail}, headers=exc.headers
        )

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
