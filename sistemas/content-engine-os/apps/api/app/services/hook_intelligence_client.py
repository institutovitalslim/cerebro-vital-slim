from __future__ import annotations

import hashlib
import hmac
import time
from urllib.parse import urlparse

import httpx


class HookIntelligenceClient:
    """Internal-only client for the isolated Hook Intelligence service."""

    _ALLOWED_HTTP_HOSTS = {
        "127.0.0.1",
        "localhost",
        "hook-intelligence-api",
    }

    def __init__(
        self,
        *,
        base_url: str,
        integration_secret: str,
        timeout_seconds: float = 20.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = self._validated_base_url(base_url)
        if not integration_secret:
            raise ValueError("integration secret is required")
        self.integration_secret = integration_secret
        self._client = httpx.AsyncClient(
            base_url=self.base_url.rstrip("/") + "/",
            timeout=timeout_seconds,
            follow_redirects=False,
            transport=transport,
        )

    @classmethod
    def _validated_base_url(cls, base_url: str) -> str:
        parsed = urlparse(base_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
            or parsed.hostname not in cls._ALLOWED_HTTP_HOSTS
        ):
            raise ValueError(
                "HOOK_INTELLIGENCE_URL must use an approved internal endpoint"
            )
        return base_url.rstrip("/")

    async def forward(
        self,
        method: str,
        path: str,
        *,
        query: str,
        body: bytes,
        tenant_id: str,
        user_id: str,
    ) -> httpx.Response:
        timestamp = str(int(time.time()))
        canonical_path = "/" + path.lstrip("/")
        body_digest = hashlib.sha256(body).hexdigest()
        message = (
            f"{tenant_id}\n{user_id}\n{timestamp}\n{method.upper()}\n"
            f"{canonical_path}\n{query}\n{body_digest}"
        ).encode()
        signature = hmac.new(
            self.integration_secret.encode(),
            message,
            hashlib.sha256,
        ).hexdigest()
        suffix = f"?{query}" if query else ""
        return await self._client.request(
            method,
            path + suffix,
            content=body or None,
            headers={
                "content-type": "application/json",
                "x-content-os-tenant": tenant_id,
                "x-content-os-user": user_id,
                "x-content-os-timestamp": timestamp,
                "x-content-os-signature": signature,
            },
        )

    async def close(self) -> None:
        await self._client.aclose()
