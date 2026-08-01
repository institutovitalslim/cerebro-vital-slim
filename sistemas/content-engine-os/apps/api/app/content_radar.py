"""Núcleo determinístico do Content Radar IVS.

Este módulo não acessa banco nem rede. Ele concentra invariantes que não podem
ser alterados por UI, coletor ou fornecedor:

- ausência de métrica continua ausente;
- views nunca são estimadas;
- interações públicas têm base própria;
- baseline compara somente itens equivalentes;
- candidato nunca participa da própria mediana.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import median
from typing import Any, Literal, Mapping, Sequence


MetricBasis = Literal["views", "plays", "reach", "public_interactions"]
Maturity = Literal["insufficient", "provisional", "target"]
SignalState = Literal["insufficient", "signal", "outlier", "breakout"]
SourceKind = Literal["approved", "candidate", "excluded", "own_account", "thematic_search"]

_ALLOWED_BASELINE_SOURCE_KINDS = {"approved", "candidate", "own_account"}


@dataclass(frozen=True, slots=True)
class MetricSelection:
    basis: MetricBasis
    value: float
    components: dict[str, float]


@dataclass(frozen=True, slots=True)
class BaselineObservation:
    content_item_id: str
    external_id: str
    source_network: str
    source_profile: str
    canonical_format: str
    metric_basis: str
    metric_value: float
    observed_at: datetime
    published_at: datetime | None = None
    source_kind: str = "candidate"
    source_active: bool = True
    url: str | None = None


@dataclass(frozen=True, slots=True)
class BaselineResult:
    maturity: Maturity
    sample_count: int
    median_value: float | None
    performance_ratio: float | None
    signal_state: SignalState
    reason: str | None = None
    members: tuple[BaselineObservation, ...] = field(default_factory=tuple)
    comparison_posts: tuple[BaselineObservation, ...] = field(default_factory=tuple)


def _observed_number(metrics: Mapping[str, Any], key: str) -> float | None:
    if key not in metrics or metrics[key] is None:
        return None
    value = metrics[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"métrica {key!r} deve ser número não negativo ou null")
    if value < 0:
        raise ValueError(f"métrica {key!r} não pode ser negativa")
    return value


def select_metric(metrics: Mapping[str, Any]) -> MetricSelection | None:
    """Seleciona uma base observada sem inferir alcance ou views.

    A prioridade preserva a unidade entregue pelo provedor. Quando nenhuma
    métrica de distribuição existe, likes + comentários podem formar apenas o
    proxy explícito ``public_interactions``.
    """

    for basis in ("views", "plays", "reach"):
        value = _observed_number(metrics, basis)
        if value is not None:
            return MetricSelection(basis=basis, value=value, components={basis: value})

    likes = _observed_number(metrics, "likes")
    comments = _observed_number(metrics, "comments")
    if likes is None and comments is None:
        return None

    components: dict[str, float] = {}
    if likes is not None:
        components["likes"] = likes
    if comments is not None:
        components["comments"] = comments
    return MetricSelection(
        basis="public_interactions",
        value=(likes or 0) + (comments or 0),
        components=components,
    )


def normalize_format(raw_format: str | None) -> str:
    value = (raw_format or "").strip().lower()
    aliases = {
        "clips": "reel",
        "reels": "reel",
        "reel": "reel",
        "short": "reel",
        "shorts": "reel",
        "carousel_container": "carousel",
        "carousel": "carousel",
        "carrossel": "carousel",
        "feed": "post",
        "post": "post",
        "static": "post",
        "estatico": "post",
        "estático": "post",
        "story": "story",
        "stories": "story",
    }
    return aliases.get(value, "other")


def observation_window(published_at: datetime | None, observed_at: datetime) -> str | None:
    """Agrupa a idade observada para evitar comparações em maturidades diferentes."""

    if published_at is None:
        return None
    age = observed_at - published_at
    if age < timedelta(0):
        return None
    if age < timedelta(hours=24):
        return "0_24h"
    if age <= timedelta(hours=72):
        return "24_72h"
    if age <= timedelta(days=7):
        return "72h_7d"
    return "7d_plus"


def classify_signal(performance_ratio: float | None) -> SignalState:
    if performance_ratio is None:
        return "insufficient"
    if performance_ratio >= 10:
        return "breakout"
    if performance_ratio >= 3:
        return "outlier"
    return "signal"


def _same_baseline_group(candidate: BaselineObservation, item: BaselineObservation) -> bool:
    candidate_window = observation_window(candidate.published_at, candidate.observed_at)
    item_window = observation_window(item.published_at, item.observed_at)
    return (
        item.content_item_id != candidate.content_item_id
        and item.source_kind in _ALLOWED_BASELINE_SOURCE_KINDS
        and item.source_active
        and item.source_network == candidate.source_network
        and item.source_profile == candidate.source_profile
        and item.canonical_format == candidate.canonical_format
        and item.metric_basis == candidate.metric_basis
        and candidate_window is not None
        and item_window == candidate_window
    )


def build_baseline(
    candidate: BaselineObservation,
    observations: Sequence[BaselineObservation],
    *,
    min_sample: int = 10,
    target_sample: int = 20,
    max_sample: int = 30,
) -> BaselineResult:
    """Calcula mediana comparável e devolve evidência auditável.

    A função recebe apenas a última observação elegível de cada conteúdo. A
    seleção de snapshots é responsabilidade da camada de persistência.
    """

    if not candidate.source_active:
        return BaselineResult(
            maturity="insufficient",
            sample_count=0,
            median_value=None,
            performance_ratio=None,
            signal_state="insufficient",
            reason="source_not_active",
        )

    if candidate.source_kind not in _ALLOWED_BASELINE_SOURCE_KINDS:
        return BaselineResult(
            maturity="insufficient",
            sample_count=0,
            median_value=None,
            performance_ratio=None,
            signal_state="insufficient",
            reason="source_not_eligible",
        )

    if observation_window(candidate.published_at, candidate.observed_at) is None:
        return BaselineResult(
            maturity="insufficient",
            sample_count=0,
            median_value=None,
            performance_ratio=None,
            signal_state="insufficient",
            reason="unknown_observation_window",
        )

    eligible = [item for item in observations if _same_baseline_group(candidate, item)]
    eligible.sort(key=lambda item: item.observed_at, reverse=True)
    members = tuple(eligible[:max_sample])
    count = len(members)

    if count < min_sample:
        return BaselineResult(
            maturity="insufficient",
            sample_count=count,
            median_value=None,
            performance_ratio=None,
            signal_state="insufficient",
            reason="insufficient_sample",
            members=members,
        )

    median_value = float(median(item.metric_value for item in members))
    maturity: Maturity = "target" if count >= target_sample else "provisional"
    comparison_posts = tuple(
        sorted(members, key=lambda item: abs(item.metric_value - median_value))[:3]
    )

    if median_value <= 0:
        return BaselineResult(
            maturity=maturity,
            sample_count=count,
            median_value=median_value,
            performance_ratio=None,
            signal_state="insufficient",
            reason="zero_baseline",
            members=members,
            comparison_posts=comparison_posts,
        )

    ratio = candidate.metric_value / median_value
    return BaselineResult(
        maturity=maturity,
        sample_count=count,
        median_value=median_value,
        performance_ratio=ratio,
        signal_state=classify_signal(ratio),
        members=members,
        comparison_posts=comparison_posts,
    )
