import json
import re
from typing import Any
from urllib.parse import quote_plus

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn

router = APIRouter(prefix="/stories", tags=["stories"])


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9áàâãéêíóôõúçñ]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:80] or "stories-ivs"


def _clara_script(title: str, keyword: str, objection: str) -> str:
    return (
        f"Origem: sequência de stories '{title}'. Se a pessoa chegar com a palavra-chave '{keyword}', "
        "não pular direto para agenda. Começar com SPIN curto: acolher, perguntar o que mais incomodou "
        "na sequência e entender contexto antes de falar de avaliação. Objeção provável: "
        f"{objection}. Uma pergunta por vez."
    )


class StorySequenceCreate(BaseModel):
    tenant_slug: str = Field(default="demo")
    title: str
    sequence_type: str
    objective: str
    main_objection: str
    patient_moment: str | None = None
    support_asset: str | None = None
    story_count: int = Field(default=10, ge=1, le=30)
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="draft")


class StoryPerformanceCreate(BaseModel):
    tenant_slug: str = Field(default="demo")
    sequence_id: str
    posted_at: str | None = None
    views: int | None = Field(default=None, ge=0)
    replies: int | None = Field(default=None, ge=0)
    useful_dms: int | None = Field(default=None, ge=0)
    leads: int | None = Field(default=None, ge=0)
    prints: int | None = Field(default=None, ge=0)
    sticker_taps: int | None = Field(default=None, ge=0)
    shares: int | None = Field(default=None, ge=0)
    saves: int | None = Field(default=None, ge=0)
    retention_initial_pct: float | None = Field(default=None, ge=0, le=100)
    avg_watch_time_sec: float | None = Field(default=None, ge=0)
    intent_signal: str | None = None
    quality_metric: str | None = None
    send_save_reason: str | None = None
    dominant_objection: str | None = None
    best_story: int | None = Field(default=None, ge=1)
    worst_story: int | None = Field(default=None, ge=1)
    decision: str = Field(default="adaptar")
    notes: str | None = None


@router.get("/themes")
def list_themes(tenant_slug: str = "demo", limit: int = 50) -> dict:
    limit = max(1, min(limit, 100))
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id::text as id, title, category, pain, desire, objection,
                       awareness_level, source, confidence, created_at
                from story_themes
                where tenant_id = %s
                order by confidence desc, created_at desc
                limit %s
                """,
                (tenant_id, limit),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.get("/products")
def list_products(tenant_slug: str = "demo", limit: int = 50) -> dict:
    limit = max(1, min(limit, 100))
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id::text as id, name, product_type, offer, cta_link,
                       tracking_url, lead_destination, owner, created_at
                from story_products
                where tenant_id = %s
                order by created_at desc
                limit %s
                """,
                (tenant_id, limit),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.get("/sequences")
def list_sequences(tenant_slug: str = "demo", limit: int = 20) -> dict:
    limit = max(1, min(limit, 100))
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select
                  s.id::text as id,
                  s.title,
                  s.sequence_type,
                  s.objective,
                  s.main_objection,
                  s.patient_moment,
                  s.support_asset,
                  s.story_count,
                  s.payload,
                  s.status,
                  s.created_at,
                  coalesce(count(p.id), 0) as performance_entries,
                  coalesce(sum(p.useful_dms), 0) as total_useful_dms,
                  coalesce(sum(p.leads), 0) as total_leads
                from story_sequences s
                left join story_sequence_performance p on p.sequence_id = s.id
                where s.tenant_id = %s
                group by s.id
                order by s.created_at desc
                limit %s
                """,
                (tenant_id, limit),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.post("/sequences")
def create_sequence(payload: StorySequenceCreate) -> dict:
    title = payload.title.strip()
    if not title:
        raise HTTPException(400, "title obrigatório")
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into story_sequences
                  (tenant_id, title, sequence_type, objective, main_objection, patient_moment, support_asset, story_count, payload, status)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                returning id::text as id, created_at
                """,
                (
                    tenant_id,
                    title,
                    payload.sequence_type,
                    payload.objective,
                    payload.main_objection,
                    payload.patient_moment,
                    payload.support_asset,
                    payload.story_count,
                    json.dumps(payload.payload, ensure_ascii=False),
                    payload.status,
                ),
            )
            row = cur.fetchone()
    return {"status": "created", "id": row["id"], "title": title, "created_at": row["created_at"]}


@router.get("/sequences/{sequence_id}/performance")
def list_performance(sequence_id: str, tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id::text as id, sequence_id::text as sequence_id, posted_at, views, replies,
                       useful_dms, leads, prints, sticker_taps, shares, saves,
                       retention_initial_pct, avg_watch_time_sec, intent_signal,
                       quality_metric, send_save_reason, dominant_objection,
                       best_story, worst_story, decision, notes, created_at
                from story_sequence_performance
                where tenant_id = %s and sequence_id = %s
                order by created_at desc
                """,
                (tenant_id, sequence_id),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.post("/performance")
def create_performance(payload: StoryPerformanceCreate) -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                "select id from story_sequences where id = %s and tenant_id = %s",
                (payload.sequence_id, tenant_id),
            )
            if not cur.fetchone():
                raise HTTPException(404, "sequence not found")
            cur.execute(
                """
                insert into story_sequence_performance
                  (tenant_id, sequence_id, posted_at, views, replies, useful_dms, leads, prints,
                   sticker_taps, shares, saves, retention_initial_pct, avg_watch_time_sec,
                   intent_signal, quality_metric, send_save_reason, dominant_objection,
                   best_story, worst_story, decision, notes)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                returning id::text as id, created_at
                """,
                (
                    tenant_id,
                    payload.sequence_id,
                    payload.posted_at,
                    payload.views,
                    payload.replies,
                    payload.useful_dms,
                    payload.leads,
                    payload.prints,
                    payload.sticker_taps,
                    payload.shares,
                    payload.saves,
                    payload.retention_initial_pct,
                    payload.avg_watch_time_sec,
                    payload.intent_signal,
                    payload.quality_metric,
                    payload.send_save_reason,
                    payload.dominant_objection,
                    payload.best_story,
                    payload.worst_story,
                    payload.decision,
                    payload.notes,
                ),
            )
            row = cur.fetchone()
    return {"status": "created", "id": row["id"], "created_at": row["created_at"]}


@router.get("/winners")
def list_winners(tenant_slug: str = "demo", limit: int = 10) -> dict:
    """Ranking operacional de sequências vencedoras.

    Score prioriza conversa útil, não vaidade:
    - lead tem peso 10
    - DM útil peso 4
    - reply peso 1
    - print peso 1.5
    - sticker tap peso 0.5
    Views entram apenas para taxa, nunca como ranking principal.
    """
    limit = max(1, min(limit, 50))
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select
                  s.id::text as id,
                  s.title,
                  s.sequence_type,
                  s.objective,
                  s.main_objection,
                  s.patient_moment,
                  s.support_asset,
                  s.story_count,
                  s.payload,
                  s.created_at,
                  coalesce(count(p.id), 0)::int as performance_entries,
                  coalesce(sum(p.views), 0)::int as total_views,
                  coalesce(sum(p.replies), 0)::int as total_replies,
                  coalesce(sum(p.useful_dms), 0)::int as total_useful_dms,
                  coalesce(sum(p.leads), 0)::int as total_leads,
                  coalesce(sum(p.prints), 0)::int as total_prints,
                  coalesce(sum(p.sticker_taps), 0)::int as total_sticker_taps,
                  coalesce(sum(p.shares), 0)::int as total_shares,
                  coalesce(sum(p.saves), 0)::int as total_saves,
                  round(avg(p.retention_initial_pct), 2) as avg_retention_initial_pct,
                  mode() within group (order by p.intent_signal) filter (where p.intent_signal is not null and p.intent_signal <> '') as learned_intent_signal,
                  round((
                    coalesce(sum(p.leads), 0) * 10
                    + coalesce(sum(p.useful_dms), 0) * 4
                    + coalesce(sum(p.shares), 0) * 2
                    + coalesce(sum(p.saves), 0) * 2
                    + coalesce(sum(p.replies), 0) * 1
                    + coalesce(sum(p.prints), 0) * 1.5
                    + coalesce(sum(p.sticker_taps), 0) * 0.5
                    + coalesce(avg(p.retention_initial_pct), 0) * 0.05
                  )::numeric, 2) as winner_score,
                  case when coalesce(sum(p.views), 0) > 0
                    then round((coalesce(sum(p.useful_dms), 0)::numeric / nullif(sum(p.views), 0)) * 100, 2)
                    else null
                  end as useful_dm_rate,
                  case when coalesce(sum(p.views), 0) > 0
                    then round((coalesce(sum(p.leads), 0)::numeric / nullif(sum(p.views), 0)) * 100, 2)
                    else null
                  end as lead_rate,
                  mode() within group (order by p.dominant_objection) filter (where p.dominant_objection is not null and p.dominant_objection <> '') as dominant_objection_learned
                from story_sequences s
                join story_sequence_performance p on p.sequence_id = s.id
                where s.tenant_id = %s
                group by s.id
                order by winner_score desc, total_leads desc, total_useful_dms desc, s.created_at desc
                limit %s
                """,
                (tenant_id, limit),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.get("/sequences/{sequence_id}/handoff")
def get_sequence_handoff(sequence_id: str, tenant_slug: str = "demo") -> dict:
    """Handoff determinístico para fechar story → WhatsApp/Clara sem envio real.

    Não chama Z-API e não escreve em produção; apenas devolve campanha, UTM,
    texto pré-preenchido, tag de origem e orientação SPIN para Clara.
    """
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id::text as id, title, sequence_type, objective, main_objection,
                       patient_moment, support_asset, story_count, payload
                from story_sequences
                where id = %s and tenant_id = %s
                """,
                (sequence_id, tenant_id),
            )
            row = cur.fetchone()
    if not row:
        raise HTTPException(404, "sequence not found")

    payload = row.get("payload") or {}
    sequence = payload.get("sequence") if isinstance(payload, dict) else {}
    keyword = sequence.get("palavraChave") if isinstance(sequence, dict) else None
    keyword = str(keyword or "quero entender").strip()
    campaign = f"stories_ivs_{_slugify(row['title'])}"
    content = f"{_slugify(row['sequence_type'])}_{_slugify(keyword)}"
    origin_tag = f"stories:{campaign}:{content}"
    prefilled = (
        f"Vim dos stories do IVS e quero entender sobre {row['title']}. "
        f"Palavra-chave: {keyword}."
    )
    whatsapp_url = (
        "https://api.whatsapp.com/send/?phone=557138388708"
        f"&text={quote_plus(prefilled)}"
        "&type=phone_number&app_absent=0"
    )
    expected_objections = [
        row["main_objection"],
        "preço/valor antes de contexto",
        "medo de julgamento",
        "já tentei de tudo",
    ]
    return {
        "sequence_id": row["id"],
        "title": row["title"],
        "utm": {
            "utm_source": "instagram",
            "utm_medium": "stories",
            "utm_campaign": campaign,
            "utm_content": content,
        },
        "origin_tag": origin_tag,
        "prefilled_text": prefilled,
        "whatsapp_url": whatsapp_url,
        "expected_objections": expected_objections,
        "clara_script": _clara_script(row["title"], keyword, row["main_objection"]),
        "governance": {
            "send_to_patient": False,
            "zapi_write": False,
            "requires_review_before_campaign": True,
            "note": "Handoff pronto para Clara, mas sem envio real automático nesta fase.",
        },
    }


@router.post("/sequences/{sequence_id}/ab-variations")
def create_ab_variations(sequence_id: str, tenant_slug: str = "demo") -> dict:
    """Gera variações A/B determinísticas a partir de uma sequência salva.

    Não salva no banco automaticamente: devolve variações para revisão humana.
    """
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id::text as id, title, sequence_type, objective, main_objection,
                       patient_moment, support_asset, story_count, payload
                from story_sequences
                where id = %s and tenant_id = %s
                """,
                (sequence_id, tenant_id),
            )
            row = cur.fetchone()
    if not row:
        raise HTTPException(404, "sequence not found")

    payload = row.get("payload") or {}
    sequence = payload.get("sequence") if isinstance(payload, dict) else {}
    stories = sequence.get("stories") if isinstance(sequence, dict) else []
    first_text = stories[0].get("texto") if stories else row["title"]
    cta = sequence.get("ctaPrincipal") if isinstance(sequence, dict) else "Me responde no direct."
    objection = row["main_objection"]

    variations = [
        {
            "variant": "A",
            "focus": "Hook mais íntimo",
            "hook": f"Você também sente que {row['title'].strip().lower()} aparece justamente quando ninguém está vendo?",
            "cta": cta,
            "sticker": "Enquete: sim, muito / nunca falei disso",
            "why": "Aumenta identificação silenciosa e reduz vergonha de responder.",
        },
        {
            "variant": "B",
            "focus": "Hook de objeção",
            "hook": f"Antes de se culpar de novo, olha isso: talvez o problema não seja você.",
            "cta": "Me manda “faz sentido” se essa frase pegou em você.",
            "sticker": "Slider: quanto isso te representa?",
            "why": "Quebra culpa antes de pedir interação; útil para públicos frios.",
        },
        {
            "variant": "C",
            "focus": "Hook de método",
            "hook": f"No IVS, a gente não começa perguntando quanto você quer perder. Começa entendendo por que ficou tão difícil.",
            "cta": "Me manda “entender” se você quer ver como avaliamos isso.",
            "sticker": "Caixinha: o que mais trava hoje?",
            "why": "Puxa conversa mais qualificada e aproxima do método sem promessa clínica.",
        },
    ]

    return {
        "sequence_id": row["id"],
        "source_title": row["title"],
        "source_first_story": first_text,
        "main_objection": objection,
        "variations": variations,
        "usage_note": "Teste uma variável por vez: hook OU CTA OU sticker. Compare por DM útil e lead, não por views.",
    }
