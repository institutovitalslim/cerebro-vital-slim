from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.config import settings
from app.content_radar import BaselineObservation, build_baseline, observation_window, select_metric
from app.content_radar_schemas import RadarIngestBatch, RadarIngestItem
from app.db import get_conn

router = APIRouter(prefix="/external-learning", tags=["external-learning"])
logger = logging.getLogger(__name__)

_ALGORITHM_VERSION = "content-radar-v1.0"
_BASELINE_SOURCE_KINDS = ("approved", "candidate", "own_account")


class ExternalIngestRequest(RadarIngestBatch):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    tenant_slug: str = Field(default="demo", min_length=1, max_length=120)


class SourceDecisionIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_kind: Literal["approved", "candidate", "excluded", "own_account", "thematic_search"]
    reason: str = Field(min_length=3, max_length=1_000)


AVATAR_TERMS = {
    "corpo_nao_responde": ["corpo", "não responde", "emagrecer", "peso", "balança", "travado"],
    "hormonios_35": ["hormônio", "menopausa", "libido", "sono", "cansaço", "calor"],
    "compulsao_acucar": ["doce", "compulsão", "ansiedade", "fome", "beliscar"],
    "gordura_abdominal": ["barriga", "abdominal", "insulina", "metabolismo"],
    "autoestima_identidade": ["espelho", "autoestima", "vergonha", "roupa", "mulher"],
    "queda_cabelo": ["cabelo", "queda", "fio", "tricologia"],
    "metodo_comunicacao": ["visualizar", "verificar", "concreto", "comunicação", "anúncio"],
}

HOOK_PATTERNS = [
    ("concretude_exclusiva", ["possível visualizar", "possível verificar", "só eu posso falar", "concretude"]),
    ("contrarian", ["ninguém", "errado", "mentira", "pare de", "não é"]),
    ("identificacao", ["você", "já sentiu", "se identifica", "acontece com você"]),
    ("mecanismo", ["por que", "motivo", "mecanismo", "explica"]),
    ("lista", ["3 ", "5 ", "passos", "sinais", "erros"]),
    ("historia", ["quando", "história", "caso", "antes"]),
]


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug=%s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, f"tenant '{tenant_slug}' not found")
    return row["id"]


def require_session_tenant(session: dict | None, tenant_id: str) -> str:
    session_tenant_id = session.get("tid") if isinstance(session, dict) else None
    if not session_tenant_id or str(session_tenant_id) != str(tenant_id):
        raise HTTPException(404, "tenant não encontrado")
    return str(tenant_id)


def _tenant_id_for_request(conn, tenant_slug: str, request: Request) -> str:
    tenant_id = _tenant_id(conn, tenant_slug)
    return require_session_tenant(getattr(request.state, "session", None), tenant_id)


def effective_new_source_kind(requested_kind: str) -> str:
    return "thematic_search" if requested_kind == "thematic_search" else "candidate"


def validate_source_transition(from_kind: str, to_kind: str, *, actor_role: str) -> None:
    if actor_role != "owner":
        raise HTTPException(403, "decisão de fonte exige papel owner")
    if from_kind == "thematic_search" and to_kind in {"approved", "own_account"}:
        raise HTTPException(409, "busca temática deve ser resolvida para uma fonte real antes da aprovação")


def _authenticated_actor(conn, request: Request, tenant_id: str) -> dict[str, str]:
    session = getattr(request.state, "session", None)
    uid = session.get("uid") if isinstance(session, dict) else None
    if not uid:
        raise HTTPException(401, "sessão sem identidade de usuário")
    with conn.cursor() as cur:
        cur.execute(
            "select id::text, email, role from users where id=%s and tenant_id=%s",
            (uid, tenant_id),
        )
        actor = cur.fetchone()
    if not actor:
        raise HTTPException(403, "usuário não pertence ao tenant")
    return dict(actor)


def _assert_radar_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            select to_regclass('public.external_metric_snapshots') as snapshots,
                   to_regclass('public.external_ingest_batches') as ingest_batches,
                   to_regclass('public.external_ingest_ledger') as ingest_ledger
            """
        )
        row = cur.fetchone()
    if not row or not all(row[name] for name in ("snapshots", "ingest_batches", "ingest_ledger")):
        raise HTTPException(
            503,
            "Content Radar v1 indisponível: migrations 022 e 023 não aplicadas",
        )


def _detect_pattern(caption: str) -> str:
    low = caption.lower()
    for label, terms in HOOK_PATTERNS:
        if any(term in low for term in terms):
            return label
    return "observacao"


def _detect_avatar_pillar(caption: str) -> str:
    low = caption.lower()
    scores = {pillar: sum(1 for term in terms if term in low) for pillar, terms in AVATAR_TERMS.items()}
    best = max(scores.items(), key=lambda pair: pair[1])
    return best[0] if best[1] else "avatar_geral"


def _reverse_engineer(item: RadarIngestItem) -> dict[str, Any]:
    caption = item.caption or ""
    pattern = _detect_pattern(caption)
    pillar = _detect_avatar_pillar(caption)
    first_line = caption.strip().split("\n", 1)[0][:140] if caption.strip() else None
    return {
        "status": "hypothesis_only",
        "why_it_may_have_worked": {
            "concretude_exclusiva": "Concretude pode facilitar compreensão e retenção.",
            "contrarian": "Contraste pode criar tensão cognitiva no início.",
            "identificacao": "Dor reconhecível pode aumentar identificação.",
            "mecanismo": "Explicação causal pode elevar utilidade percebida.",
            "lista": "Estrutura enumerada pode facilitar consumo e salvamento.",
            "historia": "Narrativa pode sustentar atenção.",
            "observacao": "Sinal bruto; requer curadoria antes de virar padrão.",
        }[pattern],
        "pattern": pattern,
        "avatar_pillar": pillar,
        "adaptation_to_instituto_vital_slim": (
            f"Testar uma tese original sobre {pillar.replace('_', ' ')} sem copiar a referência."
        ),
        "suggested_hook": first_line,
        "compliance_notes": [
            "Não copiar texto externo literalmente",
            "Não prometer resultado clínico",
            "Validar afirmações médicas antes de publicar",
        ],
    }


def _external_id(item: RadarIngestItem) -> str:
    if item.external_id:
        return item.external_id
    return hashlib.sha256(str(item.url).encode("utf-8")).hexdigest()[:32]


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _ingest_identity(item: RadarIngestItem, *, external_id: str | None = None) -> str:
    """Identidade estável usada no ledger, independente de snapshots de métrica."""

    return f"{item.source_network}:{external_id or _external_id(item)}"


def _batch_fingerprint(payload: ExternalIngestRequest) -> str:
    """Fingerprint da requisição original.

    ``observed_at`` permanece ``null`` quando foi omitido pelo coletor. Assim o
    relógio do servidor não transforma um replay idêntico em um batch diferente.
    A ordem dos itens também não altera a identidade do batch.
    """

    items = []
    for item in payload.items:
        dumped = item.model_dump(mode="json")
        items.append(
            {
                "identity": _ingest_identity(item),
                "payload": dumped,
            }
        )
    items.sort(key=lambda entry: entry["identity"])
    return _sha256_json(
        {
            "source_kind": payload.source_kind,
            "source_display_name": payload.source_display_name,
            "provider": payload.provider,
            "collector_run_id": payload.collector_run_id,
            "observed_at": payload.observed_at.isoformat() if payload.observed_at else None,
            "items": items,
        }
    )


def _reserve_ingest_batch(
    conn,
    *,
    tenant_id: str,
    payload: ExternalIngestRequest,
    server_now: datetime | None = None,
) -> datetime:
    """Reserva o run id e reutiliza seu timestamp efetivo em replays."""

    request_fingerprint = _batch_fingerprint(payload)
    proposed_observed_at = payload.observed_at or server_now or datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into external_ingest_batches (
                tenant_id, provider, collector_run_id, request_fingerprint,
                identity_count, effective_observed_at
            ) values (%s,%s,%s,%s,%s,%s)
            on conflict (tenant_id, provider, collector_run_id) do nothing
            returning request_fingerprint, identity_count, effective_observed_at
            """,
            (
                tenant_id,
                payload.provider,
                payload.collector_run_id,
                request_fingerprint,
                len(payload.items),
                proposed_observed_at,
            ),
        )
        stored = cur.fetchone()
        if not stored:
            cur.execute(
                """
                select request_fingerprint, identity_count, effective_observed_at
                from external_ingest_batches
                where tenant_id=%s and provider=%s and collector_run_id=%s
                """,
                (tenant_id, payload.provider, payload.collector_run_id),
            )
            stored = cur.fetchone()
    if (
        not stored
        or stored["request_fingerprint"] != request_fingerprint
        or stored["identity_count"] != len(payload.items)
    ):
        raise HTTPException(409, "collector_run_id já foi usado por batch ou identidades diferentes")
    return stored["effective_observed_at"]


def _register_ingest_identity(
    conn,
    *,
    tenant_id: str,
    payload: ExternalIngestRequest,
    item: RadarIngestItem,
    external_id: str,
    payload_fingerprint: str,
    effective_observed_at: datetime,
) -> bool:
    """Registra todo item, inclusive sem métricas; devolve ``True`` em replay."""

    identity = _ingest_identity(item, external_id=external_id)
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into external_ingest_ledger (
                tenant_id, provider, collector_run_id, source_network,
                external_identity, payload_fingerprint, effective_observed_at
            ) values (%s,%s,%s,%s,%s,%s,%s)
            on conflict (
                tenant_id, provider, collector_run_id, source_network, external_identity
            ) do nothing
            returning payload_fingerprint, effective_observed_at
            """,
            (
                tenant_id,
                payload.provider,
                payload.collector_run_id,
                item.source_network,
                external_id,
                payload_fingerprint,
                effective_observed_at,
            ),
        )
        stored = cur.fetchone()
        replay = stored is None
        if replay:
            cur.execute(
                """
                select payload_fingerprint, effective_observed_at
                from external_ingest_ledger
                where tenant_id=%s and provider=%s and collector_run_id=%s
                  and source_network=%s and external_identity=%s
                """,
                (
                    tenant_id,
                    payload.provider,
                    payload.collector_run_id,
                    item.source_network,
                    external_id,
                ),
            )
            stored = cur.fetchone()
    if (
        not stored
        or stored["payload_fingerprint"] != payload_fingerprint
        or stored["effective_observed_at"] != effective_observed_at
    ):
        raise HTTPException(409, "collector_run_id já foi persistido com identidade ou payload diferente")
    return replay


def _payload_fingerprint(
    payload: ExternalIngestRequest,
    item: RadarIngestItem,
    *,
    external_id: str,
    actual_profile: str,
) -> str:
    observed_at = item.observed_at or payload.observed_at
    canonical = {
        "source_network": item.source_network,
        "source_profile": item.source_profile.strip().lstrip("@").lower(),
        "actual_source_profile": actual_profile,
        "external_id": external_id,
        "url": str(item.url) if item.url else None,
        "format": item.format,
        "canonical_format": item.canonical_format,
        "caption": item.caption,
        "published_at": item.published_at.isoformat() if item.published_at else None,
        "observed_at": observed_at.isoformat() if observed_at else None,
        "metrics": item.metrics.model_dump(exclude_none=True),
        "raw_payload": item.raw_payload,
        "provider": payload.provider,
        "collector_run_id": payload.collector_run_id,
    }
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _upsert_source(conn, tenant_id: str, payload: ExternalIngestRequest, item: RadarIngestItem) -> dict:
    canonical_key = item.source_profile.strip().lstrip("@").lower()
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into external_radar_sources (
                tenant_id, network, canonical_key, display_name, handle_or_url,
                source_kind, decision_reason
            ) values (%s,%s,%s,%s,%s,%s,%s)
            on conflict (tenant_id, network, canonical_key) do update set
                display_name=coalesce(external_radar_sources.display_name, excluded.display_name),
                handle_or_url=coalesce(external_radar_sources.handle_or_url, excluded.handle_or_url),
                updated_at=now()
            returning id::text, source_kind, canonical_key, active
            """,
            (
                tenant_id,
                item.source_network,
                canonical_key,
                payload.source_display_name or item.source_profile,
                f"@{canonical_key}",
                effective_new_source_kind(payload.source_kind),
                "Criada pela ingestão governada; mudanças posteriores exigem decisão explícita",
            ),
        )
        return dict(cur.fetchone())


def _snapshot_values(item: RadarIngestItem) -> list[tuple[str, float]]:
    metrics = item.metrics.model_dump(exclude_none=True)
    out: list[tuple[str, float]] = []
    for basis in ("views", "plays", "reach"):
        if basis in metrics:
            out.append((basis, float(metrics[basis])))
    if "likes" in metrics or "comments" in metrics:
        out.append(("public_interactions", float(metrics.get("likes", 0) + metrics.get("comments", 0))))
    return out


def _load_baseline_observations(
    conn,
    *,
    tenant_id: str,
    candidate_id: str,
    source_network: str,
    source_profile: str,
    canonical_format: str,
    metric_basis: str,
    cutoff_at: datetime,
) -> tuple[list[BaselineObservation], dict[str, str]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select * from (
              select distinct on (s.content_item_id)
                     s.id::text as snapshot_id,
                     e.id::text as content_item_id,
                     e.external_id,
                     e.source_network,
                     e.source_profile,
                     e.canonical_format,
                     rs.source_kind,
                     rs.active as source_active,
                     e.url,
                     e.published_at,
                     s.metric_basis,
                     s.metric_value,
                     s.observed_at
              from external_metric_snapshots s
              join external_content_items e on e.id=s.content_item_id
              join external_radar_sources rs on rs.id=e.radar_source_id
              where s.tenant_id=%s
                and e.id<>%s::uuid
                and e.source_network=%s
                and e.source_profile=%s
                and e.canonical_format=%s
                and s.metric_basis=%s
                and s.observed_at<=%s
                and rs.source_kind=any(%s)
                and rs.active=true
              order by s.content_item_id, s.observed_at desc, s.created_at desc,
                       s.provider, s.collector_run_id, s.id desc
            ) latest
            order by observed_at desc, snapshot_id desc
            limit 120
            """,
            (
                tenant_id,
                candidate_id,
                source_network,
                source_profile,
                canonical_format,
                metric_basis,
                cutoff_at,
                list(_BASELINE_SOURCE_KINDS),
            ),
        )
        rows = cur.fetchall()
    observations = [
        BaselineObservation(
            content_item_id=row["content_item_id"],
            external_id=row["external_id"],
            source_network=row["source_network"],
            source_profile=row["source_profile"],
            canonical_format=row["canonical_format"],
            metric_basis=row["metric_basis"],
            metric_value=float(row["metric_value"]),
            observed_at=row["observed_at"],
            published_at=row["published_at"],
            source_kind=row["source_kind"],
            source_active=bool(row["source_active"]),
            url=row["url"],
        )
        for row in rows
    ]
    snapshot_ids = {row["content_item_id"]: row["snapshot_id"] for row in rows}
    return observations, snapshot_ids


def _persist_baseline(
    conn,
    *,
    tenant_id: str,
    candidate: BaselineObservation,
    candidate_snapshot_id: str,
    observations: list[BaselineObservation],
    snapshot_ids: dict[str, str],
) -> dict:
    result = build_baseline(candidate, observations)
    if observation_window(candidate.published_at, candidate.observed_at) is None:
        return {
            "algorithm_version": _ALGORITHM_VERSION,
            "metric_basis": candidate.metric_basis,
            "metric_value": candidate.metric_value,
            "maturity": result.maturity,
            "sample_count": result.sample_count,
            "median_value": result.median_value,
            "performance_ratio": result.performance_ratio,
            "signal_state": result.signal_state,
            "reason": result.reason,
            "comparison_posts": [],
        }
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into external_content_baselines (
                tenant_id, candidate_content_item_id, candidate_metric_snapshot_id,
                source_network, source_profile, canonical_format, metric_basis,
                observation_window, cutoff_at, algorithm_version,
                sample_count, median_value, maturity, performance_ratio, signal_state, reason
            ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on conflict (
                tenant_id, candidate_content_item_id, candidate_metric_snapshot_id,
                metric_basis, algorithm_version, cutoff_at
            )
            do nothing
            returning id::text
            """,
            (
                tenant_id,
                candidate.content_item_id,
                candidate_snapshot_id,
                candidate.source_network,
                candidate.source_profile,
                candidate.canonical_format,
                candidate.metric_basis,
                observation_window(candidate.published_at, candidate.observed_at),
                candidate.observed_at,
                _ALGORITHM_VERSION,
                result.sample_count,
                result.median_value,
                result.maturity,
                result.performance_ratio,
                result.signal_state,
                result.reason,
            ),
        )
        inserted = cur.fetchone()
        if inserted:
            baseline_id = inserted["id"]
            for member in result.members:
                cur.execute(
                    """
                    insert into external_baseline_members (
                        tenant_id, baseline_id, metric_snapshot_id, content_item_id, metric_value
                    ) values (%s,%s,%s,%s,%s)
                    on conflict do nothing
                    """,
                    (
                        tenant_id,
                        baseline_id,
                        snapshot_ids[member.content_item_id],
                        member.content_item_id,
                        member.metric_value,
                    ),
                )

        cur.execute(
            """
            select id::text, algorithm_version, metric_basis, sample_count, median_value,
                   maturity, performance_ratio, signal_state, reason
            from external_content_baselines
            where tenant_id=%s and candidate_content_item_id=%s
              and candidate_metric_snapshot_id=%s and metric_basis=%s
              and algorithm_version=%s and cutoff_at=%s
            """,
            (
                tenant_id,
                candidate.content_item_id,
                candidate_snapshot_id,
                candidate.metric_basis,
                _ALGORITHM_VERSION,
                candidate.observed_at,
            ),
        )
        stored = dict(cur.fetchone())
        comparison_posts: list[dict] = []
        if stored["median_value"] is not None:
            cur.execute(
                """
                select m.content_item_id::text, e.external_id, m.metric_value, e.url
                from external_baseline_members m
                join external_content_items e on e.id=m.content_item_id
                join external_metric_snapshots s on s.id=m.metric_snapshot_id
                where m.baseline_id=%s
                order by abs(m.metric_value-%s), s.observed_at desc, m.content_item_id
                limit 3
                """,
                (stored["id"], stored["median_value"]),
            )
            comparison_posts = [
                {
                    "content_item_id": member["content_item_id"],
                    "external_id": member["external_id"],
                    "metric_value": _as_float(member["metric_value"]),
                    "url": member["url"],
                }
                for member in cur.fetchall()
            ]

    return {
        "algorithm_version": stored["algorithm_version"],
        "metric_basis": stored["metric_basis"],
        "metric_value": candidate.metric_value,
        "maturity": stored["maturity"],
        "sample_count": stored["sample_count"],
        "median_value": _as_float(stored["median_value"]),
        "performance_ratio": _as_float(stored["performance_ratio"]),
        "signal_state": stored["signal_state"],
        "reason": stored["reason"],
        "comparison_posts": comparison_posts,
    }


def _ingest_item(
    conn,
    *,
    tenant_id: str,
    payload: ExternalIngestRequest,
    item: RadarIngestItem,
    calculate_baseline: bool = True,
) -> dict:
    source = _upsert_source(conn, tenant_id, payload, item)
    external_id = _external_id(item)
    observed_at = item.observed_at or payload.observed_at or datetime.now(timezone.utc)
    metrics = item.metrics.model_dump(exclude_none=True)
    reverse = _reverse_engineer(item)
    actual_profile = (
        item.actual_source_profile.strip().lstrip("@").lower()
        if source["source_kind"] == "thematic_search" and item.actual_source_profile
        else source["canonical_key"]
    )
    payload_fingerprint = _payload_fingerprint(
        payload,
        item,
        external_id=external_id,
        actual_profile=actual_profile,
    )
    _register_ingest_identity(
        conn,
        tenant_id=tenant_id,
        payload=payload,
        item=item,
        external_id=external_id,
        payload_fingerprint=payload_fingerprint,
        effective_observed_at=observed_at,
    )

    with conn.cursor() as cur:
        cur.execute(
            """
            select s.payload_fingerprint
            from external_content_items e
            join external_metric_snapshots s on s.content_item_id=e.id
            where e.tenant_id=%s and e.source_network=%s and e.external_id=%s
              and s.provider=%s and s.collector_run_id=%s
            limit 1
            """,
            (tenant_id, item.source_network, external_id, payload.provider, payload.collector_run_id),
        )
        prior_run = cur.fetchone()
        if prior_run and prior_run["payload_fingerprint"] != payload_fingerprint:
            raise HTTPException(409, "collector_run_id já foi persistido com payload diferente")
        cur.execute(
            """
            insert into external_content_items (
                tenant_id, source_network, source_profile, external_id, url, format,
                canonical_format, actual_source_profile, caption, published_at, metric_date,
                metrics, raw_payload, reverse_engineering, opportunity_score, source, status,
                radar_source_id, first_seen_at, last_seen_at
            ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,0,%s,'new',%s,%s,%s)
            on conflict (tenant_id, source_network, external_id) do update set
                url=excluded.url,
                format=excluded.format,
                canonical_format=excluded.canonical_format,
                actual_source_profile=excluded.actual_source_profile,
                caption=excluded.caption,
                published_at=coalesce(excluded.published_at, external_content_items.published_at),
                metric_date=excluded.metric_date,
                metrics=excluded.metrics,
                raw_payload=excluded.raw_payload,
                reverse_engineering=excluded.reverse_engineering,
                opportunity_score=0,
                source=excluded.source,
                radar_source_id=excluded.radar_source_id,
                first_seen_at=coalesce(external_content_items.first_seen_at, excluded.first_seen_at),
                last_seen_at=greatest(coalesce(external_content_items.last_seen_at, excluded.last_seen_at), excluded.last_seen_at),
                updated_at=now()
            returning id::text as id, external_id
            """,
            (
                tenant_id,
                item.source_network,
                actual_profile,
                external_id,
                str(item.url) if item.url else None,
                item.format,
                item.canonical_format,
                actual_profile,
                item.caption or "",
                item.published_at,
                observed_at.date(),
                _json(metrics),
                _json(item.raw_payload),
                _json(reverse),
                payload.provider,
                source["id"],
                observed_at,
                observed_at,
            ),
        )
        row = dict(cur.fetchone())

        candidate_snapshot_ids: dict[str, str] = {}
        candidate_snapshot_times: dict[str, datetime] = {}
        for basis, value in _snapshot_values(item):
            cur.execute(
                """
                insert into external_metric_snapshots (
                    tenant_id, content_item_id, observed_at, metric_basis, metric_value,
                    provider, collector_run_id, raw_metrics, payload_fingerprint
                ) values (%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)
                on conflict (tenant_id, content_item_id, metric_basis, provider, collector_run_id)
                do nothing
                returning id::text, observed_at
                """,
                (
                    tenant_id,
                    row["id"],
                    observed_at,
                    basis,
                    value,
                    payload.provider,
                    payload.collector_run_id,
                    _json(metrics),
                    payload_fingerprint,
                ),
            )
            inserted_snapshot = cur.fetchone()
            if inserted_snapshot:
                candidate_snapshot_ids[basis] = inserted_snapshot["id"]
                candidate_snapshot_times[basis] = inserted_snapshot["observed_at"]
            else:
                cur.execute(
                    """
                    select id::text, observed_at, metric_value, raw_metrics, payload_fingerprint
                    from external_metric_snapshots
                    where tenant_id=%s and content_item_id=%s and metric_basis=%s
                      and provider=%s and collector_run_id=%s
                    """,
                    (tenant_id, row["id"], basis, payload.provider, payload.collector_run_id),
                )
                stored_snapshot = cur.fetchone()
                if (
                    Decimal(str(stored_snapshot["metric_value"])) != Decimal(str(value))
                    or stored_snapshot["raw_metrics"] != metrics
                    or stored_snapshot["payload_fingerprint"] != payload_fingerprint
                ):
                    raise HTTPException(
                        409,
                        "collector_run_id já foi persistido com métricas diferentes",
                    )
                candidate_snapshot_ids[basis] = stored_snapshot["id"]
                candidate_snapshot_times[basis] = stored_snapshot["observed_at"]

    selected = select_metric(metrics)
    baseline = None
    if calculate_baseline and selected is not None:
        candidate = BaselineObservation(
            content_item_id=row["id"],
            external_id=external_id,
            source_network=item.source_network,
            source_profile=actual_profile,
            canonical_format=item.canonical_format,
            metric_basis=selected.basis,
            metric_value=selected.value,
            observed_at=candidate_snapshot_times[selected.basis],
            published_at=item.published_at,
            source_kind=source["source_kind"],
            source_active=bool(source["active"]),
            url=str(item.url) if item.url else None,
        )
        observations, snapshot_ids = _load_baseline_observations(
            conn,
            tenant_id=tenant_id,
            candidate_id=row["id"],
            source_network=item.source_network,
            source_profile=actual_profile,
            canonical_format=item.canonical_format,
            metric_basis=selected.basis,
            cutoff_at=candidate_snapshot_times[selected.basis],
        )
        baseline = _persist_baseline(
            conn,
            tenant_id=tenant_id,
            candidate=candidate,
            candidate_snapshot_id=candidate_snapshot_ids[selected.basis],
            observations=observations,
            snapshot_ids=snapshot_ids,
        )

    return {
        **row,
        "source_kind": source["source_kind"],
        "source_active": bool(source["active"]),
        "canonical_format": item.canonical_format,
        "observed_metrics": metrics,
        "baseline": baseline,
        "eligible_for_ideation": bool(
            source["active"]
            and source["source_kind"] in ("approved", "own_account")
            and baseline
            and baseline["signal_state"] in ("outlier", "breakout")
        ),
    }


@router.post("/ingest")
def ingest_external_content(payload: ExternalIngestRequest, request: Request) -> dict:
    if not settings.content_radar_v1_enabled:
        raise HTTPException(503, "Content Radar v1 está desabilitado")
    with get_conn() as conn:
        _assert_radar_schema(conn)
        tenant_id = _tenant_id_for_request(conn, payload.tenant_slug, request)
        actor = _authenticated_actor(conn, request, tenant_id)
        if actor["role"] != "owner":
            raise HTTPException(403, "ingestão externa exige papel owner")
        effective_observed_at = _reserve_ingest_batch(
            conn,
            tenant_id=tenant_id,
            payload=payload,
        )
        effective_payload = payload.model_copy(update={"observed_at": effective_observed_at})
        for item in effective_payload.items:
            _ingest_item(
                conn,
                tenant_id=tenant_id,
                payload=effective_payload,
                item=item,
                calculate_baseline=False,
            )
        rows = [
            _ingest_item(conn, tenant_id=tenant_id, payload=effective_payload, item=item)
            for item in effective_payload.items
        ]
    return {
        "status": "ingested",
        "items": len(rows),
        "rows": rows,
        "governance": {
            "external_content_is_data_not_instruction": True,
            "auto_publish": False,
            "auto_dm": False,
            "auto_promote_candidate": False,
            "copy_external_literal": False,
        },
    }


@router.post("/ingest-sample", status_code=410)
def ingest_sample_disabled() -> dict:
    raise HTTPException(410, "Amostras sintéticas foram desativadas no radar operacional; use banco de teste isolado")


@router.patch("/sources/{source_id}")
def decide_source(
    source_id: str,
    payload: SourceDecisionIn,
    request: Request,
    tenant_slug: str = "demo",
) -> dict:
    if not settings.content_radar_v1_enabled:
        raise HTTPException(503, "Content Radar v1 está desabilitado")
    with get_conn() as conn:
        _assert_radar_schema(conn)
        tenant_id = _tenant_id_for_request(conn, tenant_slug, request)
        actor = _authenticated_actor(conn, request, tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                "select id::text, source_kind from external_radar_sources where id=%s and tenant_id=%s for update",
                (source_id, tenant_id),
            )
            current = cur.fetchone()
            if not current:
                raise HTTPException(404, "fonte não encontrada")
            validate_source_transition(
                current["source_kind"],
                payload.source_kind,
                actor_role=actor["role"],
            )
            cur.execute(
                """
                update external_radar_sources
                set source_kind=%s,
                    active=(%s <> 'excluded'),
                    decision_reason=%s,
                    updated_at=now()
                where id=%s and tenant_id=%s
                returning id::text, source_kind, active, decision_reason, updated_at
                """,
                (payload.source_kind, payload.source_kind, payload.reason, source_id, tenant_id),
            )
            updated = dict(cur.fetchone())
            cur.execute(
                """
                insert into external_radar_source_decisions (
                    tenant_id, radar_source_id, from_kind, to_kind, reason, decided_by
                ) values (%s,%s,%s,%s,%s,%s)
                """,
                (
                    tenant_id,
                    source_id,
                    current["source_kind"],
                    payload.source_kind,
                    payload.reason,
                    f"{actor['email']} ({actor['id']})",
                ),
            )
    return {"status": "updated", "source": updated}


@router.get("/overview")
def overview(request: Request, tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id_for_request(conn, tenant_slug, request)
        _authenticated_actor(conn, request, tenant_id)
        if not settings.content_radar_v1_enabled:
            return {
                "feature_enabled": False,
                "version": _ALGORITHM_VERSION,
                "mode": "observed_metrics_only",
                "summary": {
                    "total_items": 0,
                    "candidate_items": 0,
                    "governed_items": 0,
                    "eligible_items": 0,
                    "last_ingest_at": None,
                },
                "top_items": [],
                "sources": [],
                "thresholds": {"outlier": 3, "breakout": 10, "minimum_sample": 10, "target_sample": 20},
                "governance": {"feature_disabled": True, "auto_publish": False, "auto_dm": False},
            }
        _assert_radar_schema(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                select
                  count(*) filter (where rs.source_kind <> 'excluded')::int as total_items,
                  count(*) filter (where rs.source_kind = 'candidate')::int as candidate_items,
                  count(*) filter (where rs.source_kind in ('approved','own_account'))::int as governed_items,
                  count(*) filter (where b.signal_state in ('outlier','breakout')
                                      and rs.source_kind in ('approved','own_account')
                                      and rs.active=true)::int as eligible_items,
                  max(e.last_seen_at) as last_ingest_at
                from external_content_items e
                join external_radar_sources rs on rs.id=e.radar_source_id
                left join lateral (
                  select signal_state from external_content_baselines b
                  where b.candidate_content_item_id=e.id
                  order by b.computed_at desc limit 1
                ) b on true
                where e.tenant_id=%s
                """,
                (tenant_id,),
            )
            summary = dict(cur.fetchone())
            cur.execute(
                """
                select e.id::text, e.source_network, e.source_profile, e.actual_source_profile,
                       e.external_id, e.url, e.canonical_format, left(e.caption,220) as caption_excerpt,
                       e.metrics, e.reverse_engineering, e.last_seen_at,
                       rs.id::text as radar_source_id, rs.source_kind,
                       rs.active as source_active, rs.display_name,
                       b.id::text as baseline_id, b.algorithm_version, b.cutoff_at,
                       cs.id::text as candidate_snapshot_id, b.metric_basis,
                       cs.metric_value as candidate_metric_value, b.observation_window,
                       b.sample_count, b.median_value, b.maturity,
                       b.performance_ratio, b.signal_state, b.reason, b.computed_at,
                       coalesce(cmp.comparison_posts, '[]'::jsonb) as comparison_posts
                from external_content_items e
                join external_radar_sources rs on rs.id=e.radar_source_id
                left join lateral (
                  select * from external_content_baselines b
                  where b.candidate_content_item_id=e.id
                  order by b.computed_at desc limit 1
                ) b on true
                left join external_metric_snapshots cs on cs.id=b.candidate_metric_snapshot_id
                left join lateral (
                  select jsonb_agg(
                           jsonb_build_object(
                             'content_item_id', ranked.content_item_id,
                             'external_id', ranked.external_id,
                             'url', ranked.url,
                             'metric_value', ranked.metric_value
                           ) order by ranked.distance, ranked.content_item_id
                         ) as comparison_posts
                  from (
                    select m.content_item_id::text,
                           compared.external_id,
                           compared.url,
                           m.metric_value,
                           abs(m.metric_value-b.median_value) as distance
                    from external_baseline_members m
                    join external_content_items compared on compared.id=m.content_item_id
                    where m.baseline_id=b.id
                    order by abs(m.metric_value-b.median_value), m.content_item_id
                    limit 3
                  ) ranked
                ) cmp on b.id is not null
                where e.tenant_id=%s and rs.source_kind <> 'excluded'
                order by
                  case b.signal_state when 'breakout' then 1 when 'outlier' then 2 when 'signal' then 3 else 4 end,
                  b.performance_ratio desc nulls last,
                  e.last_seen_at desc
                limit 50
                """,
                (tenant_id,),
            )
            top_items = [dict(row) for row in cur.fetchall()]
            cur.execute(
                """
                select id::text, network, canonical_key, display_name, handle_or_url,
                       source_kind, active, decision_reason, updated_at
                from external_radar_sources
                where tenant_id=%s
                order by case source_kind
                  when 'approved' then 1 when 'own_account' then 2 when 'candidate' then 3
                  when 'thematic_search' then 4 else 5 end,
                  canonical_key
                """,
                (tenant_id,),
            )
            sources = [dict(row) for row in cur.fetchall()]

    for item in top_items:
        item["median_value"] = _as_float(item.get("median_value"))
        item["performance_ratio"] = _as_float(item.get("performance_ratio"))
        item["metric_value"] = _as_float(item.pop("candidate_metric_value", None))
        item["eligible_for_ideation"] = bool(
            item.get("source_active")
            and item["source_kind"] in ("approved", "own_account")
            and item.get("signal_state") in ("outlier", "breakout")
        )

    return {
        "feature_enabled": settings.content_radar_v1_enabled,
        "version": _ALGORITHM_VERSION,
        "mode": "observed_metrics_only",
        "summary": summary,
        "top_items": top_items,
        "sources": sources,
        "thresholds": {"outlier": 3, "breakout": 10, "minimum_sample": 10, "target_sample": 20},
        "governance": {
            "auto_publish": False,
            "auto_dm": False,
            "candidate_mode": "preview_only",
            "excluded_never_enters_baseline": True,
            "source_change_requires_audit_reason": True,
        },
    }
