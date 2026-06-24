from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn

router = APIRouter(prefix="/external-learning", tags=["external-learning"])


class ExternalContentIn(BaseModel):
    source_network: str = Field(default="instagram")
    source_profile: str
    external_id: str | None = None
    url: str | None = None
    format: str = Field(default="reels")
    caption: str = ""
    published_at: datetime | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class ExternalIngestRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    source: str = Field(default="rapidapi_manual")
    items: list[ExternalContentIn]


AVATAR_TERMS = {
    "corpo_nao_responde": ["corpo", "não responde", "emagrecer", "peso", "balança", "travado"],
    "hormonios_35": ["hormônio", "menopausa", "libido", "sono", "cansaço", "calor"],
    "compulsao_acucar": ["doce", "compulsão", "ansiedade", "fome", "beliscar"],
    "gordura_abdominal": ["barriga", "abdominal", "insulina", "metabolismo"],
    "autoestima_identidade": ["espelho", "autoestima", "vergonha", "roupa", "mulher"],
    "queda_cabelo": ["cabelo", "queda", "fio", "tricologia"],
}

HOOK_PATTERNS = [
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


def ensure_phase4_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("alter table sources add column if not exists finalidade text")
        cur.execute("alter table sources add column if not exists objetivo text")
        cur.execute(
            """
            create table if not exists external_content_items (
              id uuid primary key default gen_random_uuid(),
              tenant_id uuid not null references tenants(id) on delete cascade,
              source_network text not null default 'instagram',
              source_profile text not null,
              external_id text not null,
              url text,
              format text,
              caption text,
              published_at timestamptz,
              metric_date date not null default current_date,
              metrics jsonb not null default '{}'::jsonb,
              raw_payload jsonb not null default '{}'::jsonb,
              reverse_engineering jsonb not null default '{}'::jsonb,
              opportunity_score numeric(8,2) not null default 0,
              source text not null default 'rapidapi',
              status text not null default 'new',
              created_at timestamptz not null default now(),
              updated_at timestamptz not null default now(),
              unique (tenant_id, source_network, external_id)
            )
            """
        )
        cur.execute(
            """
            create table if not exists content_pattern_library (
              id uuid primary key default gen_random_uuid(),
              tenant_id uuid not null references tenants(id) on delete cascade,
              pattern_key text not null,
              pattern_type text not null,
              label text not null,
              score numeric(8,2) not null default 0,
              examples jsonb not null default '[]'::jsonb,
              created_at timestamptz not null default now(),
              updated_at timestamptz not null default now(),
              unique (tenant_id, pattern_key)
            )
            """
        )
        cur.execute("create index if not exists idx_external_content_score on external_content_items(tenant_id, opportunity_score desc, updated_at desc)")
        cur.execute("create index if not exists idx_external_content_profile on external_content_items(tenant_id, source_profile, metric_date desc)")
        cur.execute("create index if not exists idx_pattern_library_score on content_pattern_library(tenant_id, score desc)")


def _num(metrics: dict[str, Any], key: str) -> float:
    aliases = {
        "views": ["views", "plays", "visualizacoes"],
        "shares": ["shares", "envios", "compartilhamentos"],
        "comments": ["comments", "comentarios"],
        "saves": ["saves", "salvamentos"],
    }
    for k in aliases.get(key, [key]):
        try:
            value = metrics.get(k)
            if value not in (None, ""):
                return float(value or 0)
        except Exception:
            pass
    return 0.0


def _detect_pattern(caption: str) -> str:
    low = caption.lower()
    for label, terms in HOOK_PATTERNS:
        if any(t in low for t in terms):
            return label
    return "observacao"


def _detect_avatar_pillar(caption: str) -> str:
    low = caption.lower()
    scores = {pillar: sum(1 for t in terms if t in low) for pillar, terms in AVATAR_TERMS.items()}
    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] else "avatar_geral"


def _score(metrics: dict[str, Any], caption: str) -> float:
    observed = _num(metrics, "views") or _num(metrics, "reach")
    if observed <= 0:
        observed = max((_num(metrics, "likes") + _num(metrics, "comments") + _num(metrics, "shares") + _num(metrics, "saves")) * 20, 1000.0)
    views = max(observed, 1000.0)
    engagement = _num(metrics, "likes") + 2 * _num(metrics, "comments") + 3 * _num(metrics, "shares") + 4 * _num(metrics, "saves")
    avatar_bonus = 15 if _detect_avatar_pillar(caption) != "avatar_geral" else 0
    return round(min((engagement / (views / 1000.0)) + avatar_bonus, 999.0), 2)


def _reverse_engineer(item: ExternalContentIn) -> dict[str, Any]:
    caption = item.caption or ""
    pattern = _detect_pattern(caption)
    pillar = _detect_avatar_pillar(caption)
    first_line = caption.strip().split("\n", 1)[0][:140] if caption.strip() else "Conteúdo externo sem legenda disponível"
    reason = {
        "contrarian": "Quebra crença e cria tensão cognitiva nos primeiros segundos.",
        "identificacao": "Começa pela dor vivida e aumenta retenção por reconhecimento.",
        "mecanismo": "Promete explicação causal, útil para autoridade médica e salvamento.",
        "lista": "Organiza promessa em passos/sinais, bom para salvamento e compartilhamento.",
        "historia": "Usa narrativa/caso para reduzir resistência e sustentar atenção.",
        "observacao": "Conteúdo capturado como sinal bruto; precisa curadoria antes de virar padrão.",
    }[pattern]
    return {
        "why_it_worked": reason,
        "pattern": pattern,
        "avatar_pillar": pillar,
        "adaptation_to_ivs": f"Transformar em tese IVS sobre {pillar.replace('_', ' ')} sem copiar a peça original.",
        "suggested_hook": first_line if first_line else f"O que esse sinal revela sobre {pillar.replace('_', ' ')}",
        "suggested_formats": ["reels", "carrossel", "stories"],
        "compliance_notes": ["Não copiar texto externo literalmente", "Não prometer resultado", "Validar claims clínicos antes de publicar"],
    }


def _external_id(item: ExternalContentIn) -> str:
    if item.external_id:
        return item.external_id
    raw = f"{item.source_network}|{item.source_profile}|{item.url or ''}|{item.caption[:120]}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]


def _sample_items() -> list[ExternalContentIn]:
    return [
        ExternalContentIn(
            source_profile="@benchmark.metabolismo",
            external_id="sample-metabolismo-001",
            url="https://instagram.com/p/sample-metabolismo-001",
            format="reels",
            caption="Você faz dieta, treina e mesmo assim o corpo não responde? Talvez o problema não seja força de vontade, mas o mecanismo metabólico por trás.",
            metrics={"views": 18400, "likes": 910, "comments": 74, "saves": 322, "shares": 181},
            raw_payload={"sample": True},
        ),
        ExternalContentIn(
            source_profile="@benchmark.mulher40",
            external_id="sample-hormonios-002",
            url="https://instagram.com/p/sample-hormonios-002",
            format="carrossel",
            caption="5 sinais de que seus hormônios podem estar afetando sono, libido, energia e barriga depois dos 40.",
            metrics={"views": 12100, "likes": 640, "comments": 52, "saves": 410, "shares": 96},
            raw_payload={"sample": True},
        ),
        ExternalContentIn(
            source_profile="@benchmark.compulsao",
            external_id="sample-acucar-003",
            url="https://instagram.com/p/sample-acucar-003",
            format="reels",
            caption="Pare de se culpar pela vontade de doce à noite. Compulsão por açúcar pode ter relação com sono, estresse e regulação glicêmica.",
            metrics={"views": 9900, "likes": 520, "comments": 88, "saves": 290, "shares": 140},
            raw_payload={"sample": True},
        ),
    ]


def _upsert_items(conn, tenant_id: str, items: list[ExternalContentIn], source: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with conn.cursor() as cur:
        for item in items:
            eid = _external_id(item)
            reverse = _reverse_engineer(item)
            score = _score(item.metrics, item.caption)
            cur.execute(
                """
                insert into external_content_items (
                    tenant_id, source_network, source_profile, external_id, url, format, caption,
                    published_at, metrics, raw_payload, reverse_engineering, opportunity_score, source
                ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s,%s)
                on conflict (tenant_id, source_network, external_id) do update set
                    url=excluded.url,
                    format=excluded.format,
                    caption=excluded.caption,
                    metrics=excluded.metrics,
                    raw_payload=excluded.raw_payload,
                    reverse_engineering=excluded.reverse_engineering,
                    opportunity_score=excluded.opportunity_score,
                    source=excluded.source,
                    updated_at=now()
                returning id::text as id, external_id, opportunity_score, reverse_engineering
                """,
                (tenant_id, item.source_network, item.source_profile, eid, item.url, item.format, item.caption,
                 item.published_at, json.dumps(item.metrics, ensure_ascii=False), json.dumps(item.raw_payload, ensure_ascii=False),
                 json.dumps(reverse, ensure_ascii=False), score, source),
            )
            row = cur.fetchone()
            pattern_key = f"{reverse['pattern']}:{reverse['avatar_pillar']}"
            example = {"external_id": eid, "profile": item.source_profile, "score": float(score), "hook": reverse["suggested_hook"]}
            cur.execute(
                """
                insert into content_pattern_library (tenant_id, pattern_key, pattern_type, label, score, examples)
                values (%s,%s,%s,%s,%s,%s::jsonb)
                on conflict (tenant_id, pattern_key) do update set
                    score=greatest(content_pattern_library.score, excluded.score),
                    examples=(select jsonb_agg(distinct x) from jsonb_array_elements(content_pattern_library.examples || excluded.examples) as t(x)),
                    updated_at=now()
                """,
                (tenant_id, pattern_key, reverse["pattern"], reverse["avatar_pillar"], score, json.dumps([example], ensure_ascii=False)),
            )
            if score >= 80:
                title = reverse["suggested_hook"][:120]
                angle = reverse["adaptation_to_ivs"]
                cur.execute(
                    """
                    insert into opportunities (tenant_id, title, thesis, angle, score, source_type, status)
                    select %s,%s,%s,%s,%s,'external_learning','new'
                    where not exists (
                      select 1 from opportunities where tenant_id=%s and source_type='external_learning' and title=%s
                    )
                    """,
                    (tenant_id, title, item.caption[:220], angle, score, tenant_id, title),
                )
            out.append(dict(row))
    return out


@router.post("/ingest")
def ingest_external_content(payload: ExternalIngestRequest) -> dict:
    with get_conn() as conn:
        ensure_phase4_schema(conn)
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        rows = _upsert_items(conn, tenant_id, payload.items, payload.source)
    return {"status": "ingested", "items": len(rows), "rows": rows, "governance": {"read_only_external": True, "auto_publish": False, "auto_dm": False, "copy_external_literal": False}}


@router.post("/ingest-sample")
def ingest_sample(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        ensure_phase4_schema(conn)
        tenant_id = _tenant_id(conn, tenant_slug)
        rows = _upsert_items(conn, tenant_id, _sample_items(), "phase4_sample")
    return {"status": "ingested", "mode": "sample_idempotent", "items": len(rows), "governance": {"read_only_external": True, "auto_publish": False, "auto_dm": False}}


@router.get("/overview")
def overview(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        ensure_phase4_schema(conn)
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select count(*)::int as total_items,
                       count(distinct source_profile)::int as profiles,
                       coalesce(avg(opportunity_score),0)::numeric(8,2) as avg_score,
                       coalesce(max(updated_at), null) as last_ingest_at
                from external_content_items where tenant_id=%s
                """,
                (tenant_id,),
            )
            summary = cur.fetchone()
            cur.execute(
                """
                select id::text, source_network, source_profile, external_id, url, format,
                       left(caption, 220) as caption_excerpt, metrics, reverse_engineering,
                       opportunity_score, source, updated_at
                from external_content_items
                where tenant_id=%s
                order by opportunity_score desc, updated_at desc
                limit 20
                """,
                (tenant_id,),
            )
            top_items = cur.fetchall()
            cur.execute(
                """
                select pattern_key, pattern_type, label, score, examples, updated_at
                from content_pattern_library
                where tenant_id=%s
                order by score desc, updated_at desc
                limit 20
                """,
                (tenant_id,),
            )
            patterns = cur.fetchall()
            cur.execute(
                """
                select title, angle, score, source_type, status, created_at
                from opportunities
                where tenant_id=%s and source_type='external_learning'
                order by score desc, created_at desc
                limit 10
                """,
                (tenant_id,),
            )
            opportunities = cur.fetchall()
    return {
        "phase": "fase_4_external_reverse_engineering",
        "mode": "read_only_learning",
        "summary": summary,
        "top_items": top_items,
        "patterns": patterns,
        "opportunities": opportunities,
        "governance": {
            "external_fetch": "RapidAPI/manual allowed; no scraping bypass",
            "auto_publish": False,
            "auto_dm": False,
            "zapi_write": False,
            "clinical_claims": "must_be_reviewed",
            "copy_policy": "adaptar padrão; nunca copiar texto externo literalmente",
        },
        "next_step": "Usar padrões vencedores para sugerir tese/hook no Sprint Semanal e produzir família IVS original.",
    }
