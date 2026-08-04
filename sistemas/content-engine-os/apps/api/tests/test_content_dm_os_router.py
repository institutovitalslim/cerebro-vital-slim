from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.content_dm_os import get_content_dm_os_client, router
from app.services.content_dm_os_client import (
    ContentDmCampaignAcceptance,
    ContentDmCampaignDraft,
    ContentDmCapabilities,
)


class FakeContentDmOsClient:
    def __init__(self) -> None:
        self.submitted: tuple[ContentDmCampaignDraft, str] | None = None

    def get_capabilities(self) -> ContentDmCapabilities:
        return ContentDmCapabilities(
            schema_version="content-dm-os/v1",
            phase="foundation",
            campaign_intake="dry_run_only",
            live_meta_delivery=False,
            pii_in_events=False,
            event_types=["comment_matched", "dm_sent"],
        )

    def submit_campaign_dry_run(
        self,
        draft: ContentDmCampaignDraft,
        *,
        idempotency_key: str,
    ) -> ContentDmCampaignAcceptance:
        self.submitted = (draft, idempotency_key)
        return ContentDmCampaignAcceptance(
            success=True,
            accepted=True,
            mode="dry_run",
            persisted=False,
            dispatched=False,
            idempotency_key=UUID(idempotency_key),
            campaign={
                "tenant_id": draft.tenant_id,
                "content_id": draft.content_id,
                "campaign_id": draft.campaign_id,
            },
        )


def test_status_exposes_safe_dm_os_capabilities() -> None:
    app = FastAPI()
    app.include_router(router)
    fake = FakeContentDmOsClient()
    app.dependency_overrides[get_content_dm_os_client] = lambda: fake
    client = TestClient(app)

    response = client.get("/content-dm-os/status")

    assert response.status_code == 200
    assert response.json() == {
        "connected": True,
        "schema_version": "content-dm-os/v1",
        "phase": "foundation",
        "campaign_intake": "dry_run_only",
        "live_meta_delivery": False,
        "pii_in_events": False,
        "event_types": ["comment_matched", "dm_sent"],
    }


def test_campaign_endpoint_accepts_only_governed_dry_run() -> None:
    app = FastAPI()
    app.include_router(router)
    fake = FakeContentDmOsClient()
    app.dependency_overrides[get_content_dm_os_client] = lambda: fake
    client = TestClient(app)
    idempotency_key = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

    response = client.post(
        "/content-dm-os/campaigns/dry-run",
        headers={"Idempotency-Key": idempotency_key},
        json={
            "tenant_id": "ivs",
            "content_id": "content_123",
            "campaign_id": "campaign_123",
            "origin_tag": "reel",
            "keywords": ["GUIA"],
            "dm_template": "Envio o guia por aqui.",
            "destination_url": "https://institutovitalslim.com.br/guia",
        },
    )

    assert response.status_code == 202
    assert response.json()["mode"] == "dry_run"
    assert response.json()["persisted"] is False
    assert response.json()["dispatched"] is False
    assert fake.submitted is not None
    draft, submitted_key = fake.submitted
    assert draft.tenant_id == "ivs"
    assert submitted_key == idempotency_key


def test_content_engine_main_registers_dm_os_routes() -> None:
    from app.main import app as content_engine_app

    paths = set(content_engine_app.openapi()["paths"])

    assert "/content-dm-os/status" in paths
    assert "/content-dm-os/campaigns/dry-run" in paths


def test_campaign_endpoint_rejects_extra_pii_fields() -> None:
    app = FastAPI()
    app.include_router(router)
    fake = FakeContentDmOsClient()
    app.dependency_overrides[get_content_dm_os_client] = lambda: fake
    client = TestClient(app)

    response = client.post(
        "/content-dm-os/campaigns/dry-run",
        headers={
            "Idempotency-Key": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        },
        json={
            "tenant_id": "ivs",
            "content_id": "content_123",
            "campaign_id": "campaign_123",
            "origin_tag": "reel",
            "keywords": ["GUIA"],
            "dm_template": "Envio o guia por aqui.",
            "destination_url": "https://institutovitalslim.com.br/guia",
            "instagram_username": "person",
        },
    )

    assert response.status_code == 422
    assert fake.submitted is None


def test_campaign_endpoint_rejects_invalid_idempotency_key() -> None:
    app = FastAPI()
    app.include_router(router)
    fake = FakeContentDmOsClient()
    app.dependency_overrides[get_content_dm_os_client] = lambda: fake
    client = TestClient(app)

    response = client.post(
        "/content-dm-os/campaigns/dry-run",
        headers={"Idempotency-Key": "not-a-uuid"},
        json={
            "tenant_id": "ivs",
            "content_id": "content_123",
            "campaign_id": "campaign_123",
            "origin_tag": "reel",
            "keywords": ["GUIA"],
            "dm_template": "Envio o guia por aqui.",
            "destination_url": "https://institutovitalslim.com.br/guia",
        },
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Idempotency-Key deve ser UUID"}
    assert fake.submitted is None

