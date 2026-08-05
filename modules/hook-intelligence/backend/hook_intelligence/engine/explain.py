"""Explicações editoriais curtas baseadas somente no resultado público do score."""

from __future__ import annotations

import re
import unicodedata

from hook_intelligence.engine.scorer import ScoreEvaluation

MAX_PUBLIC_EXPLANATION_CHARS = 500

_COMPONENT_LABELS = {
    "clarity": "clareza",
    "specificity": "especificidade",
    "novelty": "novidade",
    "retention": "retenção",
    "channel_fit": "adequação ao canal",
}
_PENALTY_LABELS = {
    "generic_cliche": "abertura genérica",
    "excessive_uppercase": "caixa alta excessiva",
    "exaggerated_punctuation": "pontuação exagerada",
    "topic_absent": "tópico ausente",
    "bad_length": "comprimento inadequado ao canal",
}
_FORBIDDEN_INTERNAL_LANGUAGE = (
    "chain-of-thought",
    "chain of thought",
    "meu raciocínio",
    "system prompt",
    "prompt do sistema",
    "instruções internas",
    "raciocínio interno",
)
_UNSAFE_CLAIM_PATTERNS = (
    re.compile(r"\b(?:cura|curar|cure|curado|curada)\b"),
    re.compile(r"\bgarant(?:e|ido|ida|idos|idas)\b(?:\s+\w+){0,3}\s+resultados?\b"),
    re.compile(r"\bresultados?\s+garantid[oa]s?\b"),
    re.compile(r"\bfunciona\s+para\s+todos\b"),
    re.compile(r"\bperder\s+\d+(?:[.,]\d+)?\s*kg\s+em\s+\d+\s+dias?\b"),
)
_SENTENCE_ENDINGS = frozenset(".!?。！？")


def _public_text(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} deve ser str")
    normalized = " ".join(unicodedata.normalize("NFKC", value).split())
    if not normalized:
        raise ValueError(f"{field} não pode ser vazio")
    for character in normalized:
        if unicodedata.category(character).startswith("C"):
            raise ValueError(f"{field} contém caractere Unicode não publicável")
    folded = normalized.casefold()
    if any(term in folded for term in _FORBIDDEN_INTERNAL_LANGUAGE):
        raise ValueError(f"{field} contém linguagem interna não publicável")
    if any(pattern.search(folded) for pattern in _UNSAFE_CLAIM_PATTERNS):
        raise ValueError(f"{field} contém claim não publicável")
    return normalized


def _truncate_words(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    prefix = value[: limit - 1].rstrip()
    if " " in prefix:
        prefix = prefix.rsplit(" ", 1)[0].rstrip()
    return f"{prefix}…"


def _first_sentence(value: str, limit: int = 160) -> str:
    for index, character in enumerate(value):
        if character in _SENTENCE_ENDINGS:
            sentence = value[: index + 1]
            return sentence if len(sentence) <= limit else _truncate_words(sentence, limit)
    return _truncate_words(value, limit)


def explain_score(mechanism: str, curated_explanation: str, evaluation: ScoreEvaluation) -> str:
    """Produz resumo determinístico sem expor raciocínio interno ou criar claims."""

    if not isinstance(evaluation, ScoreEvaluation):
        raise TypeError("evaluation deve ser ScoreEvaluation")
    mechanism = _public_text(mechanism, "mechanism")
    curated_explanation = _public_text(curated_explanation, "curated_explanation")
    recommendations = tuple(
        _public_text(recommendation, f"recommendations[{index}]")
        for index, recommendation in enumerate(evaluation.recommendations)
    )

    components = (
        ("clarity", evaluation.clarity),
        ("specificity", evaluation.specificity),
        ("novelty", evaluation.novelty),
        ("retention", evaluation.retention),
        ("channel_fit", evaluation.channel_fit),
    )
    strongest = sorted(components, key=lambda item: (-item[1], item[0]))[:2]
    strengths = ", ".join(f"{_COMPONENT_LABELS[name]} ({value:.2f})" for name, value in strongest)
    if evaluation.penalties:
        public_penalties = (
            _PENALTY_LABELS.get(code, "outra penalidade editorial") for code in evaluation.penalties
        )
        penalties = _truncate_words(", ".join(public_penalties), 70)
    else:
        penalties = "nenhuma penalidade registrada"
    recommendation = (
        _truncate_words(recommendations[0], 80)
        if recommendations
        else "Preserve a formulação e valide-a no contexto editorial."
    )
    explanation = (
        f"Mecanismo: {_truncate_words(mechanism, 60)}. "
        f"Resumo: {_first_sentence(curated_explanation)} "
        f"Score: {evaluation.overall:.2f}/100. Forças: {strengths}. "
        f"Penalidades: {penalties}. Recomendação: {recommendation}"
    )
    return _truncate_words(explanation, MAX_PUBLIC_EXPLANATION_CHARS)
