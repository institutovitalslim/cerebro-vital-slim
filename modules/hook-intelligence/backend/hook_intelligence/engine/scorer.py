"""Score editorial local, transparente e determinístico para hooks."""

from __future__ import annotations

import math
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from hook_intelligence.domain.models import Channel, HookScores

SCORE_WEIGHTS: Mapping[str, float] = MappingProxyType(
    {
        "clarity": 0.25,
        "specificity": 0.25,
        "novelty": 0.15,
        "retention": 0.20,
        "channel_fit": 0.15,
    }
)
PENALTY_POINTS: Mapping[str, float] = MappingProxyType(
    {
        "generic_cliche": 12.0,
        "excessive_uppercase": 8.0,
        "exaggerated_punctuation": 8.0,
        "topic_absent": 10.0,
        "bad_length": 7.0,
    }
)

_CHANNEL_LENGTHS: Mapping[Channel, tuple[int, int]] = MappingProxyType(
    {
        Channel.REEL: (20, 90),
        Channel.AD: (15, 90),
        Channel.CAROUSEL: (20, 110),
        Channel.STORY: (12, 80),
        Channel.LANDING_PAGE: (25, 130),
        Channel.EMAIL: (20, 100),
        Channel.BLOG: (45, 150),
        Channel.YOUTUBE: (25, 110),
    }
)
_GENERIC_CLICHES = (
    "você precisa saber disso",
    "voce precisa saber disso",
    "segredo que ninguém conta",
    "segredo que ninguem conta",
    "isso vai mudar sua vida",
)
_RETENTION_SIGNALS = frozenset({"como", "por", "erro", "sinais", "hábitos", "habitos"})
_DETAIL_SIGNALS = frozenset(
    {"após", "apos", "antes", "durante", "minutos", "horas", "h", "passos", "sinais"}
)
_WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)


@dataclass(frozen=True, slots=True)
class ScoreEvaluation:
    """Componentes heurísticos públicos; não representa medição científica."""

    clarity: float
    specificity: float
    novelty: float
    retention: float
    channel_fit: float
    overall: float
    penalties: tuple[str, ...]
    recommendations: tuple[str, ...]

    def __post_init__(self) -> None:
        for field in (
            "clarity",
            "specificity",
            "novelty",
            "retention",
            "channel_fit",
            "overall",
        ):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{field} deve ser numérico")
            if not math.isfinite(value) or not 0 <= value <= 100:
                raise ValueError(f"{field} deve estar entre 0 e 100")
        if not isinstance(self.penalties, tuple):
            raise TypeError("penalties deve ser tuple")
        if not isinstance(self.recommendations, tuple):
            raise TypeError("recommendations deve ser tuple")

    def to_hook_scores(self) -> HookScores:
        return HookScores(
            clarity=self.clarity,
            specificity=self.specificity,
            novelty=self.novelty,
            retention=self.retention,
            channel_fit=self.channel_fit,
            overall=self.overall,
        )


@dataclass(frozen=True, slots=True)
class RankedText:
    index: int
    text: str
    evaluation: ScoreEvaluation


def _normalize(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} deve ser str")
    normalized = " ".join(unicodedata.normalize("NFKC", value).split())
    if not normalized:
        raise ValueError(f"{field} não pode ser vazio")
    if not any(character.isalnum() for character in normalized):
        raise ValueError(f"{field} deve conter ao menos um caractere alfanumérico")
    return normalized


def _has_exaggerated_punctuation(value: str) -> bool:
    """Detecta três pontuações Unicode consecutivas após normalização NFKC."""

    run_length = 0
    for character in unicodedata.normalize("NFKC", value):
        if unicodedata.category(character).startswith("P"):
            run_length += 1
            if run_length >= 3:
                return True
        else:
            run_length = 0
    return False


def _channel(value: object) -> Channel:
    if isinstance(value, Channel):
        return value
    if not isinstance(value, str):
        raise TypeError("channel deve ser Channel ou str válido")
    try:
        return Channel(value)
    except ValueError as error:
        raise ValueError(f"channel inválido: {value!r}") from error


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def _topic_present(text_tokens: set[str], topic: str) -> bool:
    topic_tokens = set(_WORD_RE.findall(topic.casefold()))
    return bool(topic_tokens) and topic_tokens.issubset(text_tokens)


def _component_scores(text: str, channel: Channel, topic: str) -> tuple[float, ...]:
    folded = text.casefold()
    words = _WORD_RE.findall(folded)
    tokens = set(words)
    length = len(text)
    minimum, maximum = _CHANNEL_LENGTHS[channel]
    exaggerated_punctuation = _has_exaggerated_punctuation(text)

    clarity = 78.0
    if 4 <= len(words) <= 18:
        clarity += 12
    if len(words) > 24 or exaggerated_punctuation:
        clarity -= 25
    if len(words) < 3:
        clarity -= 30

    topic_present = _topic_present(tokens, topic)
    specificity = 25.0 + (35 if topic_present else 0)
    if re.search(r"\d", text):
        specificity += 25
    if tokens & _DETAIL_SIGNALS:
        specificity += 15

    generic = any(cliche in folded for cliche in _GENERIC_CLICHES)
    novelty = 68.0 - (38 if generic else 0)
    if re.search(r"\d", text) and tokens & _DETAIL_SIGNALS:
        novelty += 10

    retention = 42.0
    if "?" in text:
        retention += 20
    if re.search(r"\d", text):
        retention += 18
    if tokens & _RETENTION_SIGNALS:
        retention += 15
    if generic:
        retention -= 10

    channel_fit = 82.0 if minimum <= length <= maximum else 45.0
    if channel in {Channel.REEL, Channel.STORY, Channel.AD} and len(words) <= 14:
        channel_fit += 8
    if channel in {Channel.BLOG, Channel.EMAIL, Channel.YOUTUBE} and len(words) >= 7:
        channel_fit += 8
    if exaggerated_punctuation:
        channel_fit -= 35

    return tuple(
        round(_clamp(value), 2)
        for value in (
            clarity,
            specificity,
            novelty,
            retention,
            channel_fit,
        )
    )


def score_text(text: str, channel: Channel | str, topic: str) -> ScoreEvaluation:
    """Avalia um texto com heurísticas editoriais explícitas e pesos fixos."""

    normalized_text = _normalize(text, "text")
    normalized_topic = _normalize(topic, "topic")
    normalized_channel = _channel(channel)
    clarity, specificity, novelty, retention, channel_fit = _component_scores(
        normalized_text, normalized_channel, normalized_topic
    )

    folded = normalized_text.casefold()
    letters = [character for character in normalized_text if character.isalpha()]
    uppercase_ratio = (
        sum(character.isupper() for character in letters) / len(letters) if letters else 0.0
    )
    text_tokens = set(_WORD_RE.findall(folded))
    minimum, maximum = _CHANNEL_LENGTHS[normalized_channel]
    penalties: list[str] = []
    if any(cliche in folded for cliche in _GENERIC_CLICHES):
        penalties.append("generic_cliche")
    if len(letters) >= 8 and uppercase_ratio >= 0.75:
        penalties.append("excessive_uppercase")
    if _has_exaggerated_punctuation(normalized_text):
        penalties.append("exaggerated_punctuation")
    if not _topic_present(text_tokens, normalized_topic):
        penalties.append("topic_absent")
    if not minimum <= len(normalized_text) <= maximum:
        penalties.append("bad_length")

    components = {
        "clarity": clarity,
        "specificity": specificity,
        "novelty": novelty,
        "retention": retention,
        "channel_fit": channel_fit,
    }
    weighted = sum(components[name] * weight for name, weight in SCORE_WEIGHTS.items())
    overall = round(_clamp(weighted - sum(PENALTY_POINTS[code] for code in penalties)), 2)
    recommendation_by_code = {
        "generic_cliche": "Troque o clichê por uma abertura específica.",
        "excessive_uppercase": "Use caixa alta apenas quando necessária.",
        "exaggerated_punctuation": "Reduza a pontuação enfática.",
        "topic_absent": "Inclua o tópico de forma explícita.",
        "bad_length": "Ajuste o comprimento ao canal.",
    }
    recommendations = tuple(recommendation_by_code[code] for code in penalties)
    return ScoreEvaluation(
        clarity,
        specificity,
        novelty,
        retention,
        channel_fit,
        overall,
        tuple(penalties),
        recommendations,
    )


def rank_texts(texts: Iterable[str], channel: Channel | str, topic: str) -> tuple[RankedText, ...]:
    """Ordena por overall decrescente e usa o índice original como desempate."""

    if isinstance(texts, (str, bytes)) or not isinstance(texts, Iterable):
        raise TypeError("texts deve ser um iterável de strings")
    # Valida parâmetros comuns mesmo para uma coleção vazia.
    normalized_channel = _channel(channel)
    normalized_topic = _normalize(topic, "topic")
    ranked: list[RankedText] = []
    for index, text in enumerate(texts):
        if not isinstance(text, str):
            raise TypeError(f"texts[{index}] deve ser str")
        ranked.append(
            RankedText(index, text, score_text(text, normalized_channel, normalized_topic))
        )
    return tuple(sorted(ranked, key=lambda item: (-item.evaluation.overall, item.index)))
