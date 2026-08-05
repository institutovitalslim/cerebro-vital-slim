"""Content OS integration endpoint."""

from fastapi import APIRouter, HTTPException, Request

from hook_intelligence.api.schemas import ErrorResponse, ExportRequest, ExportResponse
from hook_intelligence.domain.models import ComplianceStatus
from hook_intelligence.engine.exporter import validate_export_payload

router = APIRouter(prefix="/v1/exports", tags=["exports"])


@router.post(
    "/content-os",
    response_model=ExportResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid workspace"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        422: {"model": ErrorResponse, "description": "Request validation failed"},
        500: {"model": ErrorResponse, "description": "Internal service error"},
    },
)
def export_content_os(payload: ExportRequest, request: Request) -> ExportResponse:
    repository = request.app.state.services.get().repository
    try:
        exported = repository.export_session(payload.session_id, payload.workspace_ref)
    except LookupError:
        raise HTTPException(status_code=404, detail="generation session not found") from None
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="invalid export request") from None
    except Exception:  # noqa: BLE001 - storage details are private
        raise HTTPException(status_code=500, detail="internal service error") from None
    try:
        validate_export_payload(exported)
        response = ExportResponse.model_validate(exported)
        if any(hook.compliance.status is ComplianceStatus.BLOCK for hook in response.hooks):
            raise ValueError("blocked hook")
    except Exception:  # noqa: BLE001 - invalid persisted exports are internal failures
        raise HTTPException(status_code=500, detail="internal service error") from None
    return response
