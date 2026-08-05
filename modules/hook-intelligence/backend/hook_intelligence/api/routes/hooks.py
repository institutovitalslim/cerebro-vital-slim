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
from hook_intelligence.domain.models import ComplianceStatus, GenerationRequest, Hook, Source
from hook_intelligence.engine.compliance import evaluate_compliance
from hook_intelligence.engine.composer import (
    canonical_key,
    contains_expression,
    contains_forbidden,
    normalize_text,
)
from hook_intelligence.engine.pipeline import validate_generation_request
from hook_intelligence.engine.scorer import score_text

router = APIRouter(prefix="/v1/hooks", tags=["hooks"])
_ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Invalid domain input"},
    404: {"model": ErrorResponse, "description": "Resource not found"},
    500: {"model": ErrorResponse, "description": "Internal service error"},
}
_VALIDATION_ERROR = {"model": ErrorResponse, "description": "Request validation failed"}


def _validated_generated_hooks(generated: object, payload: GenerationRequest) -> tuple[Hook, ...]:
    """Snapshot e valida integralmente a fronteira injetável antes de qualquer escrita."""

    if type(generated) is not tuple or len(generated) != payload.count:
        raise ValueError("invalid generated batch")

    validated: list[tuple[int, Hook]] = []
    identifiers = set()
    for index, candidate in enumerate(generated):
        if type(candidate) is not Hook:
            raise TypeError("invalid generated hook")
        hook = Hook.model_validate(
            Hook.model_dump(candidate, mode="python", warnings="none"), strict=True
        )
        if hook.id in identifiers:
            raise ValueError("duplicate generated hook")
        identifiers.add(hook.id)
        if (
            hook.library is not payload.library
            or hook.channel is not payload.channel
            or hook.objective is not payload.objective
            or hook.awareness_stage is not payload.awareness_stage
            or hook.tone is not payload.tone
            or normalize_text(hook.audience) != payload.audience
            or normalize_text(hook.topic) != payload.topic
            or hook.compliance.status is ComplianceStatus.BLOCK
            or not 3 <= len(hook.text) <= payload.max_length
            or not all(contains_expression(hook.text, word) for word in payload.required_words)
            or contains_forbidden(hook.text, payload.forbidden_words)
            or (
                payload.mechanism is not None
                and canonical_key(payload.mechanism)
                not in {canonical_key(value) for value in hook.mechanisms}
            )
        ):
            raise ValueError("incoherent generated hook")
        validated.append((index, hook))

    validated.sort(key=lambda item: (-item[1].scores.overall, item[0]))
    return tuple(hook for _, hook in validated)


@router.post(
    "/generate",
    response_model=GenerateResponse,
    responses={**_ERROR_RESPONSES, 422: _VALIDATION_ERROR},
)
def generate(payload: GenerateRequest, request: Request) -> GenerateResponse:
    started = perf_counter()
    services = request.app.state.services.get()
    try:
        validated_payload = validate_generation_request(payload)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400, detail="generation request cannot be fulfilled"
        ) from None
    try:
        generated = services.generator(validated_payload.model_copy(deep=True), services.library)
        approved = _validated_generated_hooks(generated, validated_payload)
    except Exception:  # noqa: BLE001 - componente injetável é uma fronteira interna.
        raise HTTPException(status_code=500, detail="internal service error") from None
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


@router.post(
    "/score",
    response_model=ScoreResponse,
    responses={400: _ERROR_RESPONSES[400], 422: _VALIDATION_ERROR},
)
def score(payload: ScoreRequest) -> ScoreResponse:
    try:
        evaluation = score_text(payload.text, payload.channel, payload.topic)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="score request cannot be evaluated") from None
    return ScoreResponse.model_validate(evaluation.to_hook_scores().model_dump())


@router.post(
    "/compliance",
    response_model=ComplianceResponse,
    responses={400: _ERROR_RESPONSES[400], 422: _VALIDATION_ERROR},
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


@router.post(
    "/{id}/favorite",
    response_model=FavoriteResponse,
    responses={**_ERROR_RESPONSES, 422: _VALIDATION_ERROR},
)
def favorite(id: UUID, request: Request) -> FavoriteResponse:
    repository = request.app.state.services.get().repository
    try:
        repository.favorite(id)
    except LookupError:
        raise HTTPException(status_code=404, detail="hook not found") from None
    except Exception:  # noqa: BLE001 - storage details are private
        raise HTTPException(status_code=500, detail="internal service error") from None
    return FavoriteResponse(id=id, favorite=True)
