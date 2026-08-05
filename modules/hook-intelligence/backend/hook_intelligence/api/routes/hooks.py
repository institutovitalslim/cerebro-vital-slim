"""Generation, scoring, compliance, and favorite endpoints."""

from time import perf_counter
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from hook_intelligence import ENGINE_VERSION
from hook_intelligence.api.schemas import (
    ComplianceRequest,
    ComplianceResponse,
    ErrorResponse,
    FavoriteResponse,
    GenerateRequest,
    GenerateResponse,
    ScoreRequest,
    ScoreResponse,
)
from hook_intelligence.domain.models import ComplianceStatus, Source
from hook_intelligence.engine.compliance import evaluate_compliance
from hook_intelligence.engine.scorer import score_text

router = APIRouter(prefix="/v1/hooks", tags=["hooks"])
_ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Invalid domain input"},
    404: {"model": ErrorResponse, "description": "Resource not found"},
    500: {"model": ErrorResponse, "description": "Internal service error"},
}


@router.post("/generate", response_model=GenerateResponse, responses=_ERROR_RESPONSES)
def generate(payload: GenerateRequest, request: Request) -> GenerateResponse:
    started = perf_counter()
    services = request.app.state.services.get()
    try:
        generated = services.generator(payload, services.library)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400, detail="generation request cannot be fulfilled"
        ) from None
    approved = tuple(
        hook for hook in generated if hook.compliance.status is not ComplianceStatus.BLOCK
    )
    if not approved:
        raise HTTPException(status_code=400, detail="generation produced no exportable hooks")
    try:
        session_id = services.repository.save_generation(approved)
    except Exception:  # noqa: BLE001 - storage details must never cross the API boundary
        raise HTTPException(status_code=500, detail="internal service error") from None
    warnings: list[str] = []
    if payload.use_ai and all(hook.source is not Source.AI_ADAPTED for hook in approved):
        warnings.append("AI unavailable; deterministic fallback used.")
    return GenerateResponse(
        request_id=UUID(session_id),
        hooks=list(approved),
        warnings=warnings,
        engine_version=ENGINE_VERSION,
        duration_ms=max(0.0, (perf_counter() - started) * 1000),
    )


@router.post("/score", response_model=ScoreResponse, responses={400: _ERROR_RESPONSES[400]})
def score(payload: ScoreRequest) -> ScoreResponse:
    try:
        evaluation = score_text(payload.text, payload.channel, payload.topic)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="score request cannot be evaluated") from None
    return ScoreResponse.model_validate(evaluation.to_hook_scores().model_dump())


@router.post(
    "/compliance", response_model=ComplianceResponse, responses={400: _ERROR_RESPONSES[400]}
)
def compliance(payload: ComplianceRequest, request: Request) -> ComplianceResponse:
    library = request.app.state.services.get().library
    try:
        result = evaluate_compliance(payload.text, payload.library, library)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400, detail="compliance request cannot be evaluated"
        ) from None
    return ComplianceResponse.model_validate(result.model_dump())


@router.post("/{id}/favorite", response_model=FavoriteResponse, responses=_ERROR_RESPONSES)
def favorite(id: UUID, request: Request) -> FavoriteResponse:
    repository = request.app.state.services.get().repository
    try:
        repository.favorite(id)
    except LookupError:
        raise HTTPException(status_code=404, detail="hook not found") from None
    except Exception:  # noqa: BLE001 - storage details are private
        raise HTTPException(status_code=500, detail="internal service error") from None
    return FavoriteResponse(id=id, favorite=True)
