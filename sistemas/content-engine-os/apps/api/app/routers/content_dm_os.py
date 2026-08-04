from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException

from app.services.content_dm_os_client import (
    ContentDmCampaignAcceptance,
    ContentDmCampaignDraft,
    ContentDmOsClient,
    ContentDmOsConfigurationError,
)

router = APIRouter(prefix="/content-dm-os", tags=["content-dm-os"])


def get_content_dm_os_client() -> Iterator[ContentDmOsClient]:
    base_url = os.getenv("CONTENT_DM_OS_BASE_URL", "")
    integration_secret = os.getenv("CONTENT_DM_OS_INTEGRATION_SECRET", "")
    allowed_insecure_origin = os.getenv(
        "CONTENT_DM_OS_ALLOWED_INSECURE_ORIGIN", ""
    )
    try:
        client = ContentDmOsClient(
            base_url=base_url,
            integration_secret=integration_secret,
            allowed_insecure_origin=allowed_insecure_origin or None,
        )
    except ContentDmOsConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail="IVS Content DM OS não configurado",
        ) from exc

    try:
        yield client
    finally:
        client.close()


@router.get("/status")
def content_dm_os_status(
    client: Annotated[
        ContentDmOsClient,
        Depends(get_content_dm_os_client),
    ],
) -> dict:
    try:
        capabilities = client.get_capabilities()
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=503,
            detail="IVS Content DM OS indisponível",
        ) from exc

    return {
        "connected": True,
        **capabilities.model_dump(mode="json"),
    }


@router.post(
    "/campaigns/dry-run",
    response_model=ContentDmCampaignAcceptance,
    status_code=202,
)
def submit_content_dm_campaign_dry_run(
    draft: ContentDmCampaignDraft,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    client: Annotated[
        ContentDmOsClient,
        Depends(get_content_dm_os_client),
    ],
) -> ContentDmCampaignAcceptance:
    try:
        normalized_key = str(UUID(idempotency_key))
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="Idempotency-Key deve ser UUID",
        ) from exc

    try:
        return client.submit_campaign_dry_run(
            draft,
            idempotency_key=normalized_key,
        )
    except httpx.HTTPStatusError as exc:
        upstream_status = exc.response.status_code
        status_code = 422 if upstream_status == 422 else 503
        raise HTTPException(
            status_code=status_code,
            detail="IVS Content DM OS rejeitou o dry_run"
            if status_code == 422
            else "IVS Content DM OS indisponível",
        ) from exc
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=503,
            detail="IVS Content DM OS indisponível",
        ) from exc
