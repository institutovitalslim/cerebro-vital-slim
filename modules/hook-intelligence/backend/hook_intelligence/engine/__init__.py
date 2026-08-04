"""Carregamento, seleção e composição determinística de hooks."""

from hook_intelligence.engine.composer import (
    CandidateConstraintError,
    PatternCompositionError,
    compose_pattern,
    contains_forbidden,
)
from hook_intelligence.engine.deduplicator import deduplicate, similarity
from hook_intelligence.engine.explain import explain_score
from hook_intelligence.engine.library import HookLibrary, Pattern
from hook_intelligence.engine.pipeline import generate_deterministic
from hook_intelligence.engine.scorer import (
    PENALTY_POINTS,
    SCORE_WEIGHTS,
    RankedText,
    ScoreEvaluation,
    rank_texts,
    score_text,
)
from hook_intelligence.engine.selector import select_patterns, stable_rank

__all__ = [
    "PENALTY_POINTS",
    "SCORE_WEIGHTS",
    "CandidateConstraintError",
    "HookLibrary",
    "Pattern",
    "PatternCompositionError",
    "RankedText",
    "ScoreEvaluation",
    "compose_pattern",
    "contains_forbidden",
    "deduplicate",
    "explain_score",
    "generate_deterministic",
    "rank_texts",
    "score_text",
    "select_patterns",
    "similarity",
    "stable_rank",
]
