"""Contrato público dos adaptadores opcionais de IA."""

from __future__ import annotations

from typing import Protocol


class AdapterError(RuntimeError):
    """Falha pública sanitizada de configuração, transporte ou resposta."""


class HookAdapter(Protocol):
    def adapt(self, topic: str, candidates: list[str]) -> list[str]:
        """Adapta candidatos sem alterar a coleção recebida."""
        ...
