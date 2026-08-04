from __future__ import annotations

from typing import Literal
from urllib.parse import unquote, urlparse
from uuid import UUID

import httpx
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


class ContentDmOsConfigurationError(ValueError):
    """Raised when the service boundary is configured unsafely."""


def _is_safe_service_path(path: str) -> bool:
    decoded = unquote(path or "/")
    return (
        decoded.startswith("/")
        and "\\" not in decoded
        and "//" not in decoded
        and all(segment not in {".", ".."} for segment in decoded.split("/"))
    )


class ContentDmCapabilities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["content-dm-os/v1"]
    phase: str = Field(min_length=1, max_length=64)
    campaign_intake: Literal["dry_run_only"]
    live_meta_delivery: bool
    pii_in_events: bool
    event_types: list[str]


class ContentDmCampaignDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
    content_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
    campaign_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
    origin_tag: Literal["reel", "post", "carousel", "story"]
    keywords: list[str] = Field(min_length=1, max_length=20)
    dm_template: str = Field(min_length=1, max_length=1000)
    destination_url: AnyHttpUrl

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, value: list[str]) -> list[str]:
        normalized = [keyword.strip() for keyword in value]
        if any(not keyword or len(keyword) > 64 for keyword in normalized):
            raise ValueError("keywords must contain 1 to 64 visible characters")
        return normalized

    @field_validator("destination_url")
    @classmethod
    def require_https_destination(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        if value.scheme != "https":
            raise ValueError("destination_url must use HTTPS")
        return value


class ContentDmCampaignIdentifiers(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: str = Field(min_length=1, max_length=128)
    content_id: str = Field(min_length=1, max_length=128)
    campaign_id: str = Field(min_length=1, max_length=128)


class ContentDmCampaignAcceptance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: Literal[True]
    accepted: Literal[True]
    mode: Literal["dry_run"]
    persisted: Literal[False]
    dispatched: Literal[False]
    idempotency_key: UUID
    campaign: ContentDmCampaignIdentifiers


class ContentDmOsClient:
    def __init__(
        self,
        *,
        base_url: str,
        integration_secret: str,
        timeout_seconds: float = 3.0,
        allowed_insecure_origin: str | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        parsed = urlparse(base_url)
        is_loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        normalized_base_url = base_url.rstrip("/")
        private_http_allowed = False
        if allowed_insecure_origin:
            allowed = urlparse(allowed_insecure_origin)
            if (
                allowed.scheme != "http"
                or not allowed.hostname
                or allowed.username is not None
                or allowed.password is not None
                or not _is_safe_service_path(allowed.path)
                or allowed.query
                or allowed.fragment
                or allowed.params
            ):
                raise ContentDmOsConfigurationError(
                    "CONTENT_DM_OS_ALLOWED_INSECURE_ORIGIN must be an exact HTTP service endpoint"
                )
            private_http_allowed = (
                parsed.scheme == "http"
                and normalized_base_url == allowed_insecure_origin.rstrip("/")
            )
        if (
            not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or not _is_safe_service_path(parsed.path)
            or parsed.query
            or parsed.fragment
            or parsed.params
        ):
            raise ContentDmOsConfigurationError(
                "CONTENT_DM_OS_BASE_URL must be an unambiguous service endpoint"
            )
        if parsed.scheme != "https" and not (
            parsed.scheme == "http" and (is_loopback or private_http_allowed)
        ):
            raise ContentDmOsConfigurationError(
                "CONTENT_DM_OS_BASE_URL must use HTTPS outside loopback"
            )
        if (
            integration_secret != integration_secret.strip()
            or len(integration_secret) < 32
        ):
            raise ContentDmOsConfigurationError(
                "CONTENT_DM_OS_INTEGRATION_SECRET must contain at least 32 characters"
            )

        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            headers={"Authorization": f"Bearer {integration_secret}"},
            timeout=timeout_seconds,
            transport=transport,
        )

    def get_capabilities(self) -> ContentDmCapabilities:
        response = self._client.get(
            "api/integrations/content-os/v1/capabilities"
        )
        response.raise_for_status()
        payload = response.json()
        capabilities = payload["capabilities"]
        return ContentDmCapabilities.model_validate(
            {
                "schema_version": payload["schema_version"],
                "phase": payload["phase"],
                "campaign_intake": capabilities["campaign_intake"],
                "live_meta_delivery": capabilities["live_meta_delivery"],
                "pii_in_events": capabilities["pii_in_events"],
                "event_types": capabilities["event_types"],
            }
        )

    def submit_campaign_dry_run(
        self,
        draft: ContentDmCampaignDraft,
        *,
        idempotency_key: str,
    ) -> ContentDmCampaignAcceptance:
        parsed_key = UUID(idempotency_key)
        response = self._client.post(
            "api/integrations/content-os/v1/campaigns",
            headers={"Idempotency-Key": str(parsed_key)},
            json={
                "schema_version": "content-dm-os/v1",
                **draft.model_dump(mode="json"),
                "mode": "dry_run",
            },
        )
        response.raise_for_status()
        acceptance = ContentDmCampaignAcceptance.model_validate(response.json())
        expected_campaign = ContentDmCampaignIdentifiers(
            tenant_id=draft.tenant_id,
            content_id=draft.content_id,
            campaign_id=draft.campaign_id,
        )
        if acceptance.campaign != expected_campaign:
            raise ValueError("Content DM OS returned a mismatched campaign identity")
        if acceptance.idempotency_key != parsed_key:
            raise ValueError("Content DM OS returned a mismatched idempotency key")
        return acceptance

    def close(self) -> None:
        self._client.close()
