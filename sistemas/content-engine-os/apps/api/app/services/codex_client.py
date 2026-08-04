from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import settings


class CodexClient:
    """Cliente do motor de geração via Codex CLI (GPT-5.5, OAuth) através do gateway no host.

    Suporta texto e VISÃO: passe `images` (lista de data-URLs base64) para o gateway
    anexar ao prompt (codex exec -i). `output_schema` força JSON estruturado.
    """

    def __init__(self) -> None:
        self.url = settings.codex_gateway_url
        self.token = settings.codex_gateway_token

    @property
    def available(self) -> bool:
        return bool(self.url)

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        timeout: int = 180,
        images: list[str] | None = None,
        output_schema: dict | None = None,
    ) -> dict[str, Any]:
        if not self.url:
            raise RuntimeError("codex_gateway_url não configurado")
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        payload: dict[str, Any] = {"prompt": prompt, "system": system, "timeout": timeout}
        if images:
            payload["images"] = images
        if output_schema:
            payload["output_schema"] = output_schema
        async with httpx.AsyncClient(timeout=timeout + 40) as client:
            resp = await client.post(
                f"{self.url.rstrip('/')}/generate",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        if not data.get("ok"):
            raise RuntimeError(f"codex gateway: {data.get('error')}")
        return {"mode": "codex", "model": data.get("model"), "content": data.get("content", "")}

    async def generate_json(
        self,
        prompt: str,
        system: str | None = None,
        timeout: int = 180,
    ) -> dict[str, Any]:
        """Drop-in do OpenRouterClient.generate_json: retorna {mode, model, content, json}.
        json=None se o conteúdo não for JSON parseável ou o motor falhar (chamador usa seu fallback).
        NUNCA lança — preserva o contrato do antigo OpenRouterClient.generate_json."""
        try:
            res = await self.generate(prompt, system=system, timeout=timeout)
        except Exception as e:
            return {"mode": "error", "model": None, "content": "", "json": None, "error": str(e)}
        content = res.get("content", "") or ""
        parsed: Any = None
        try:
            parsed = json.loads(content)
        except Exception:
            m = re.search(r"\{.*\}", content, re.S)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except Exception:
                    parsed = None
        return {"mode": res.get("mode"), "model": res.get("model"), "content": content, "json": parsed}
