import httpx
import pytest

from app.services.content_dm_os_client import (
    ContentDmCampaignDraft,
    ContentDmOsClient,
    ContentDmOsConfigurationError,
)


def campaign_draft() -> ContentDmCampaignDraft:
    return ContentDmCampaignDraft(
        tenant_id="ivs",
        content_id="content_123",
        campaign_id="campaign_123",
        origin_tag="carousel",
        keywords=["GUIA"],
        dm_template="Envio o guia por aqui.",
        destination_url="https://institutovitalslim.com.br/guia",
    )


def test_capabilities_uses_service_auth_and_parses_contract() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url == httpx.URL(
            "https://dm-os.internal/api/integrations/content-os/v1/capabilities"
        )
        assert request.headers["Authorization"] == "Bearer " + ("s" * 32)
        return httpx.Response(
            200,
            json={
                "service": "ivs-content-dm-os",
                "schema_version": "content-dm-os/v1",
                "phase": "foundation",
                "capabilities": {
                    "campaign_intake": "dry_run_only",
                    "live_meta_delivery": False,
                    "pii_in_events": False,
                    "event_types": ["comment_matched", "dm_sent"],
                },
            },
        )

    client = ContentDmOsClient(
        base_url="https://dm-os.internal",
        integration_secret="s" * 32,
        transport=httpx.MockTransport(handler),
    )

    result = client.get_capabilities()

    assert result.schema_version == "content-dm-os/v1"
    assert result.live_meta_delivery is False
    assert result.pii_in_events is False
    assert result.event_types == ["comment_matched", "dm_sent"]


def test_capabilities_preserves_a_governed_service_base_path() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL(
            "http://ivs-content-dm-web:3020/dm/api/integrations/content-os/v1/capabilities"
        )
        return httpx.Response(
            200,
            json={
                "service": "ivs-content-dm-os",
                "schema_version": "content-dm-os/v1",
                "phase": "foundation",
                "capabilities": {
                    "campaign_intake": "dry_run_only",
                    "live_meta_delivery": False,
                    "pii_in_events": False,
                    "event_types": ["comment_matched", "dm_sent"],
                },
            },
        )

    client = ContentDmOsClient(
        base_url="http://ivs-content-dm-web:3020/dm",
        integration_secret="s" * 32,
        allowed_insecure_origin="http://ivs-content-dm-web:3020/dm",
        transport=httpx.MockTransport(handler),
    )

    assert client.get_capabilities().live_meta_delivery is False


def test_submit_campaign_forces_dry_run_and_idempotency() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url == httpx.URL(
            "https://dm-os.internal/api/integrations/content-os/v1/campaigns"
        )
        assert request.headers["Idempotency-Key"] == (
            "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        )
        payload = __import__("json").loads(request.content)
        assert payload["mode"] == "dry_run"
        assert "instagram_username" not in payload
        return httpx.Response(
            202,
            json={
                "success": True,
                "accepted": True,
                "mode": "dry_run",
                "persisted": False,
                "dispatched": False,
                "idempotency_key": request.headers["Idempotency-Key"],
                "campaign": {
                    "tenant_id": payload["tenant_id"],
                    "content_id": payload["content_id"],
                    "campaign_id": payload["campaign_id"],
                },
            },
        )

    client = ContentDmOsClient(
        base_url="https://dm-os.internal",
        integration_secret="s" * 32,
        transport=httpx.MockTransport(handler),
    )
    draft = campaign_draft()

    result = client.submit_campaign_dry_run(
        draft,
        idempotency_key="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    )

    assert result.accepted is True
    assert result.mode == "dry_run"
    assert result.persisted is False
    assert result.dispatched is False


@pytest.mark.parametrize(
    "base_url",
    [
        "https://user:password@dm-os.internal",
        "https://dm-os.internal/../path",
        "https://dm-os.internal?token=unsafe",
        "https://dm-os.internal#fragment",
    ],
)
def test_configuration_rejects_ambiguous_or_credentialed_base_urls(
    base_url: str,
) -> None:
    with pytest.raises(ContentDmOsConfigurationError):
        ContentDmOsClient(
            base_url=base_url,
            integration_secret="s" * 32,
        )


def test_configuration_rejects_blank_integration_secret() -> None:
    with pytest.raises(ContentDmOsConfigurationError):
        ContentDmOsClient(
            base_url="https://dm-os.internal",
            integration_secret=" " * 32,
        )


def test_configuration_rejects_private_http_without_exact_opt_in() -> None:
    with pytest.raises(ContentDmOsConfigurationError):
        ContentDmOsClient(
            base_url="http://ivs-content-dm-web:3020",
            integration_secret="s" * 32,
        )


def test_configuration_accepts_only_exact_opted_in_private_http_origin() -> None:
    client = ContentDmOsClient(
        base_url="http://ivs-content-dm-web:3020",
        integration_secret="s" * 32,
        allowed_insecure_origin="http://ivs-content-dm-web:3020",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={})
        ),
    )
    client.close()

    with pytest.raises(ContentDmOsConfigurationError):
        ContentDmOsClient(
            base_url="http://other-service:3020",
            integration_secret="s" * 32,
            allowed_insecure_origin="http://ivs-content-dm-web:3020",
        )


@pytest.mark.parametrize(
    "campaign_override",
    [
        {"tenant_id": "other-tenant"},
        {"phone": "not-allowed"},
    ],
)
def test_submit_rejects_cross_tenant_or_pii_in_upstream_response(
    campaign_override: dict[str, str],
) -> None:
    draft = campaign_draft()

    def handler(request: httpx.Request) -> httpx.Response:
        campaign = {
            "tenant_id": draft.tenant_id,
            "content_id": draft.content_id,
            "campaign_id": draft.campaign_id,
            **campaign_override,
        }
        return httpx.Response(
            202,
            json={
                "success": True,
                "accepted": True,
                "mode": "dry_run",
                "persisted": False,
                "dispatched": False,
                "idempotency_key": request.headers["Idempotency-Key"],
                "campaign": campaign,
            },
        )

    client = ContentDmOsClient(
        base_url="https://dm-os.internal",
        integration_secret="s" * 32,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ValueError):
        client.submit_campaign_dry_run(
            draft,
            idempotency_key="3fa85f64-5717-4562-b3fc-2c963f66afa6",
        )

