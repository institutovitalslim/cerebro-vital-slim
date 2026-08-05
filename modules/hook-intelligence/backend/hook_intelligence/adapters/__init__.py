"""Adaptadores de IA opcionais; desabilitados por padrão."""

from __future__ import annotations

import os
from collections.abc import Mapping

from hook_intelligence.adapters.base import AdapterError, HookAdapter
from hook_intelligence.adapters.disabled import DisabledAdapter
from hook_intelligence.adapters.openai_compatible import (
    DEFAULT_ENDPOINT,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT_SECONDS,
    OpenAICompatible,
)

_FALSE_VALUES = frozenset({"", "0", "false", "no", "off"})
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def adapter_from_env(
    env: Mapping[str, str] | None = None, *, transport: object | None = None
) -> HookAdapter:
    """Constrói o adaptador somente após opt-in explícito.

    O endpoint padrão é ``https://api.openai.com/v1/chat/completions``.
    """

    values = os.environ if env is None else env
    raw_enabled = values.get("HOOK_AI_ENABLED", "")
    if not isinstance(raw_enabled, str):
        raise AdapterError("configuração HOOK_AI_ENABLED deve ser string")
    enabled = raw_enabled.strip().casefold()
    if enabled in _FALSE_VALUES:
        return DisabledAdapter()
    if enabled not in _TRUE_VALUES:
        raise AdapterError(
            "configuração HOOK_AI_ENABLED inválida; use true/false, 1/0, yes/no ou on/off"
        )

    api_key = values.get("HOOK_AI_API_KEY", "")
    model = values.get("HOOK_AI_MODEL", "")
    if not isinstance(api_key, str) or not api_key.strip():
        raise AdapterError("configuração HOOK_AI_API_KEY é obrigatória quando IA está habilitada")
    if not isinstance(model, str) or not model.strip():
        raise AdapterError("configuração HOOK_AI_MODEL é obrigatória quando IA está habilitada")
    try:
        return OpenAICompatible(
            api_key=api_key,
            model=model,
            endpoint=values.get("HOOK_AI_ENDPOINT", DEFAULT_ENDPOINT),
            timeout_seconds=values.get("HOOK_AI_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)),
            max_tokens=values.get("HOOK_AI_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)),
            transport=transport,
        )
    except AdapterError:
        raise
    except Exception:  # noqa: BLE001 -- Mapping externo pode executar código arbitrário.
        raise AdapterError("configuração do adaptador OpenAI-compatible inválida") from None


def ai_runtime_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Valida readiness de configuração sem criar cliente nem executar transporte."""

    try:
        configured = adapter_from_env(env, transport=object())
    except AdapterError:
        return False
    return isinstance(configured, OpenAICompatible)


__all__ = [
    "AdapterError",
    "DisabledAdapter",
    "HookAdapter",
    "OpenAICompatible",
    "adapter_from_env",
    "ai_runtime_enabled",
]
