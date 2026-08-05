"""Deduplicação determinística de textos curtos sem dependências externas."""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable
from itertools import pairwise

_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)

# Artigos, conectivos, possessivos e formas auxiliares frequentes não distinguem a
# ideia editorial de hooks curtos. A lista é deliberadamente pequena e estável.
_FUNCTION_WORDS = frozenset(
    {
        "a",
        "as",
        "de",
        "do",
        "dos",
        "e",
        "em",
        "esta",
        "estao",
        "está",
        "estão",
        "o",
        "os",
        "que",
        "seu",
        "seus",
        "sua",
        "suas",
        "um",
        "uma",
    }
)


def _canonical(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split()).casefold()


def _pt_br_token(token: str) -> str:
    """Converte somente gerúndios regulares longos para forma de presente aproximada."""

    # Não é um stemmer: preserva tokens curtos e só cobre terminações regulares
    # necessárias para equivalências como ``travando`` -> ``trava``.
    if len(token) >= 7 and token.endswith("ando"):
        return token[:-4] + "a"
    if len(token) >= 7 and token.endswith("endo"):
        return token[:-4] + "e"
    if len(token) >= 7 and token.endswith("indo"):
        return token[:-4] + "e"
    return token


def _tokens(canonical: str) -> tuple[str, ...]:
    return tuple(
        normalized
        for raw in _TOKEN_RE.findall(canonical)
        if raw not in _FUNCTION_WORDS
        for normalized in (_pt_br_token(raw),)
        if normalized
    )


def _features(tokens: tuple[str, ...]) -> Counter[tuple[str, ...]]:
    """Retorna multiconjunto estável de unigramas e bigramas adjacentes."""

    features: Counter[tuple[str, ...]] = Counter((token,) for token in tokens)
    features.update(pairwise(tokens))
    return features


def similarity(left: str, right: str) -> float:
    """Calcula Sørensen–Dice sobre unigramas/bigramas após normalização local.

    Equivalência canônica tem valor 1.0. Textos canonicamente distintos sem
    features têm valor 0.0, assim como quando apenas um lado não tem features.
    """

    if not isinstance(left, str):
        raise TypeError("left deve ser str")
    if not isinstance(right, str):
        raise TypeError("right deve ser str")
    canonical_left = _canonical(left)
    canonical_right = _canonical(right)
    if canonical_left == canonical_right:
        return 1.0

    left_features = _features(_tokens(canonical_left))
    right_features = _features(_tokens(canonical_right))
    if not left_features and not right_features:
        return 0.0
    if not left_features or not right_features:
        return 0.0
    intersection = sum((left_features & right_features).values())
    return (2.0 * intersection) / (sum(left_features.values()) + sum(right_features.values()))


def deduplicate(rows: Iterable[str], threshold: float = 0.82) -> list[str]:
    """Mantém a primeira ocorrência de cada grupo similar, preservando a ordem.

    A complexidade O(n²) é intencional para as pequenas listas de candidatos do motor.
    A entrada nunca é alterada e o retorno é sempre uma lista nova.
    """

    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise TypeError("threshold deve ser número entre 0 e 1")
    if not math.isfinite(float(threshold)) or not 0 <= threshold <= 1:
        raise ValueError("threshold deve estar entre 0 e 1")
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Iterable):
        raise TypeError("rows deve ser um iterável de strings")

    result: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, str):
            raise TypeError(f"rows[{index}] deve ser str")
        if all(similarity(row, kept) < threshold for kept in result):
            result.append(row)
    return result
