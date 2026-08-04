"""Explicações editoriais curtas baseadas somente no resultado público do score."""

from __future__ import annotations

import unicodedata

from hook_intelligence.engine.scorer import ScoreEvaluation

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
_FORBIDDEN_INTERNAL_LANGUAGE = ("chain-of-thought", "meu raciocínio", "prompt")


def _public_text(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} deve ser str")
    normalized = " ".join(unicodedata.normalize("NFKC", value).split())
    if not normalized:
        raise ValueError(f"{field} não pode ser vazio")
    if any(term in normalized.casefold() for term in _FORBIDDEN_INTERNAL_LANGUAGE):
        raise ValueError(f"{field} contém linguagem interna não publicável")
    return normalized


def explain_score(mechanism: str, curated_explanation: str, evaluation: ScoreEvaluation) -> str:
    """Produz resumo determinístico sem expor raciocínio interno ou criar claims."""

    mechanism = _public_text(mechanism, "mechanism")
    curated_explanation = _public_text(curated_explanation, "curated_explanation")
    if not isinstance(evaluation, ScoreEvaluation):
        raise TypeError("evaluation deve ser ScoreEvaluation")

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
        penalties = ", ".join(_PENALTY_LABELS.get(code, code) for code in evaluation.penalties)
    else:
        penalties = "nenhuma penalidade registrada"
    recommendation = (
        evaluation.recommendations[0]
        if evaluation.recommendations
        else "Preserve a formulação e valide-a no contexto editorial."
    )
    return (
        f"Mecanismo: {mechanism}. {curated_explanation} "
        f"Score: {evaluation.overall:.2f}/100. Forças: {strengths}. "
        f"Penalidades: {penalties}. Recomendação: {recommendation}"
    )
