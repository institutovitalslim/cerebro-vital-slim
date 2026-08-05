"""Persisted history and favorites endpoints."""

from fastapi import APIRouter, HTTPException, Query, Request

from hook_intelligence.api.schemas import ErrorResponse, FavoritesPage, HistoryPage

router = APIRouter(prefix="/v1", tags=["history"])
_INTERNAL_ERROR = {500: {"model": ErrorResponse, "description": "Internal service error"}}
_RESPONSES = {
    **_INTERNAL_ERROR,
    422: {"model": ErrorResponse, "description": "Request validation failed"},
}


@router.get("/history", response_model=HistoryPage, responses=_RESPONSES)
def history(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> HistoryPage:
    repository = request.app.state.services.get().repository
    try:
        result = repository.list_sessions(page=page, page_size=page_size)
    except Exception:  # noqa: BLE001 - storage details are private
        raise HTTPException(status_code=500, detail="internal service error") from None
    items = [
        {
            "request_id": item["session_id"],
            "created_at": item["created_at"],
            "hook_count": item["hook_count"],
        }
        for item in result["items"]
    ]
    return HistoryPage(
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/favorites", response_model=FavoritesPage, responses=_RESPONSES)
def favorites(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> FavoritesPage:
    repository = request.app.state.services.get().repository
    try:
        result = repository.list_favorites(page=page, page_size=page_size)
    except Exception:  # noqa: BLE001 - storage details are private
        raise HTTPException(status_code=500, detail="internal service error") from None
    return FavoritesPage(**result)
