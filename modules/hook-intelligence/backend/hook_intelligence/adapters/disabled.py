"""Adaptador local usado quando IA não foi habilitada explicitamente."""

from __future__ import annotations


class DisabledAdapter:
    """No-op sem dependências ou I/O externo."""

    def adapt(self, topic: str, candidates: list[str]) -> list[str]:
        del topic
        return list(candidates)

    def adapt_or_fallback(self, topic: str, candidates: list[str]) -> list[str]:
        return self.adapt(topic, candidates)
