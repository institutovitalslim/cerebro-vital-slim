"""Carregamento, seleção e composição determinística de hooks."""

from hook_intelligence.engine.composer import compose_pattern, contains_forbidden
from hook_intelligence.engine.library import HookLibrary, Pattern
from hook_intelligence.engine.pipeline import generate_deterministic
from hook_intelligence.engine.selector import select_patterns, stable_rank

__all__ = [
    "HookLibrary",
    "Pattern",
    "compose_pattern",
    "contains_forbidden",
    "generate_deterministic",
    "select_patterns",
    "stable_rank",
]
