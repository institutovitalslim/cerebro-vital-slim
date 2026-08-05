"""Catalog endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query, Request

from hook_intelligence.api.schemas import ErrorResponse, PatternsResponse, TaxonomiesResponse
from hook_intelligence.domain.models import Library

router = APIRouter(prefix="/v1", tags=["catalog"])


@router.get("/taxonomies", response_model=TaxonomiesResponse)
def taxonomies(request: Request) -> TaxonomiesResponse:
    library = request.app.state.services.get().library
    return TaxonomiesResponse(
        taxonomies={name: list(values) for name, values in library.taxonomies.items()},
        mechanisms=list(library.mechanisms),
    )


@router.get(
    "/patterns",
    response_model=PatternsResponse,
    responses={422: {"model": ErrorResponse, "description": "Request validation failed"}},
)
def patterns(
    request: Request,
    library: Annotated[Library | None, Query(description="Optional library filter")] = None,
) -> PatternsResponse:
    active = request.app.state.services.get().library
    values = [
        {
            "id": item.id,
            "library": item.library,
            "mechanism": item.mechanism,
            "objectives": list(item.objectives),
            "channels": list(item.channels),
            "awareness_stages": list(item.awareness_stages),
            "tones": list(item.tones),
            "template": item.template,
            "slots": list(item.slots),
            "explanation": item.explanation,
            "intensity": item.intensity,
        }
        for item in active.all_patterns
        if library is None or item.library == library.value
    ]
    return PatternsResponse(items=values, total=len(values))
