"""Gate heurístico e determinístico de claims para a biblioteca IVS Health.

As regras são conservadoras e servem para triagem editorial. O resultado não é uma
avaliação jurídica ou médica definitiva.
"""

import re
import unicodedata

from hook_intelligence.domain.models import (
    ComplianceResult,
    ComplianceStatus,
    Library,
)
from hook_intelligence.engine.library import CLAIM_SCAN_MAX_CHARS, HookLibrary

_CATEGORY_REASON = {
    "guarantee": "GUARANTEED_RESULT",
    "cure": "CURE_CLAIM",
    "diagnosis": "DIRECT_DIAGNOSIS",
    "prescription": "DIRECT_PRESCRIPTION",
    "false_urgency": "FALSE_URGENCY",
    "stigma": "STIGMATIZING_LANGUAGE",
    "unsourced_number": "UNSOURCED_CLINICAL_NUMBER",
    "absolute_superiority": "ABSOLUTE_SUPERIORITY",
}
_REVIEW_CATEGORIES = frozenset({"unsourced_number"})
_NEGATED_CLAUSE_RE = re.compile(
    r"(^|[,.;:!?])(\s{0,20}(?:não|nunca|jamais)\b[^,.;:!?]{0,500})",
    re.IGNORECASE,
)
_METALINGUISTIC_CLAUSE_RE = re.compile(
    r"(^|[,.;:!?])(\s{0,20}(?:a frase|o texto|a expressão|o exemplo)\s{1,4}"
    r"[^,.;:!?]{0,300}\s{1,4}(?:é|seria)\s{1,4}[^,.;:!?]{0,80}"
    r"(?:proibid[oa]|inadequad[oa]|exemplo\s{1,4}do\s{1,4}que\s{1,4}evitar)\b)",
    re.IGNORECASE,
)


def _normalize_claim_text(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("text deve ser str")  # noqa: TRY004

    normalized = unicodedata.normalize("NFKC", text)
    # Whitespace editorial é aceito e canonizado antes da rejeição de controles.
    normalized = " ".join(normalized.split())
    controls = [character for character in normalized if unicodedata.category(character)[0] == "C"]
    if controls:
        raise ValueError("text contém Unicode remanescente de categoria C")
    if not any(character.isalnum() for character in normalized):
        raise ValueError("text deve conter ao menos um caractere alfanumérico")
    if len(normalized) > CLAIM_SCAN_MAX_CHARS:
        raise ValueError(f"text excede CLAIM_SCAN_MAX_CHARS={CLAIM_SCAN_MAX_CHARS}")
    return normalized


def _coerce_library(library: Library | str) -> Library:
    if isinstance(library, Library):
        return library
    if not isinstance(library, str):
        raise ValueError("library deve ser Library ou string válida")  # noqa: TRY004
    try:
        return Library(library)
    except ValueError as error:
        raise ValueError(f"library inválida: {library!r}") from error


def _mask_editorial_context(text: str) -> str:
    """Mascara heurísticas editoriais bounded sem alterar o texto recebido."""

    def mask_clause(match: re.Match[str]) -> str:
        return match.group(1) + (" " * len(match.group(2)))

    masked = _METALINGUISTIC_CLAUSE_RE.sub(mask_clause, text)
    return _NEGATED_CLAUSE_RE.sub(mask_clause, masked)


def evaluate_compliance(
    text: str,
    library: Library | str,
    rules_library: HookLibrary | None = None,
) -> ComplianceResult:
    """Classifica texto com regras locais já validadas, sem compilar entrada do usuário."""

    normalized = _normalize_claim_text(text)
    active_library = _coerce_library(library)
    if rules_library is not None and not isinstance(rules_library, HookLibrary):
        raise ValueError("rules_library deve ser uma HookLibrary validada")
    if active_library is Library.UNIVERSAL:
        return ComplianceResult(status=ComplianceStatus.PASS, reasons=[])
    rules = HookLibrary.load_default() if rules_library is None else rules_library
    try:
        matches = rules.scan_forbidden_claims(_mask_editorial_context(normalized))
    except (ValueError, TypeError):
        # Não publique expressão nem detalhe do motor de regex.
        raise ValueError("falha contextual ao avaliar regras médicas IVS") from None

    categories = {category for category, _expression in matches}
    reasons = [
        _CATEGORY_REASON[category["id"]]
        for category in rules.forbidden_claims["categories"]
        if category["id"] in categories
    ]
    if not reasons:
        status = ComplianceStatus.PASS
    elif categories - _REVIEW_CATEGORIES:
        status = ComplianceStatus.BLOCK
    else:
        status = ComplianceStatus.REVIEW
    return ComplianceResult(status=status, reasons=reasons)


__all__ = ["CLAIM_SCAN_MAX_CHARS", "evaluate_compliance"]
