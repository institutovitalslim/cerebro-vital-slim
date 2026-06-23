import json
import re
from typing import Any
from urllib.parse import quote_plus

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
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


def _payload_sequence(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    sequence = payload.get("sequence")
    return sequence if isinstance(sequence, dict) else {}


def _story_items_from_payload(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    sequence = _payload_sequence(payload)
    stories = sequence.get("stories")
    if not isinstance(stories, list):
        return []
    items: list[dict[str, Any]] = []
    for idx, story in enumerate(stories, start=1):
        if not isinstance(story, dict):
            continue
        copy = str(story.get("texto") or story.get("copy") or "").strip()
        if not copy:
            continue
        items.append(
            {
                "story_order": int(story.get("n") or idx),
                "story_type": str(story.get("funcao") or story.get("story_type") or "story"),
                "hook": str(story.get("hook") or ""),
                "copy": copy,
                "visual_direction": str(story.get("visual") or story.get("visual_direction") or ""),
                "sticker_type": str(story.get("sticker") or story.get("sticker_type") or ""),
                "cta_type": str(story.get("dm") or story.get("cta_type") or sequence.get("palavraChave") or ""),
                "expected_metric": str(story.get("dm") or story.get("expected_metric") or "DM útil"),
                "compliance_status": "safe_draft" if story.get("risco") == "baixo" else "pending_review",
                "quality_score": 82 if story.get("risco") == "baixo" else 70,
            }
        )
    return items


def _insert_story_items(cur, tenant_id: str, sequence_id: str, payload: dict[str, Any] | None) -> int:
    items = _story_items_from_payload(payload)
    for item in items:
        cur.execute(
            """
            insert into story_items
              (tenant_id, sequence_id, story_order, story_type, hook, copy, visual_direction,
               sticker_type, cta_type, expected_metric, compliance_status, quality_score)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on conflict (sequence_id, story_order) do update set
              story_type=excluded.story_type,
              hook=excluded.hook,
              copy=excluded.copy,
              visual_direction=excluded.visual_direction,
              sticker_type=excluded.sticker_type,
              cta_type=excluded.cta_type,
              expected_metric=excluded.expected_metric,
              compliance_status=excluded.compliance_status,
              quality_score=excluded.quality_score
            """,
            (
                tenant_id,
                sequence_id,
                item["story_order"],
                item["story_type"],
                item["hook"],
                item["copy"],
                item["visual_direction"],
                item["sticker_type"],
                item["cta_type"],
                item["expected_metric"],
                item["compliance_status"],
                item["quality_score"],
            ),
        )
    return len(items)


def _html_escape(value: Any) -> str:
    return (
        str(value or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
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


class StoryConversionCreate(BaseModel):
    tenant_slug: str = Field(default="demo")
    sequence_id: str
    origin_tag: str | None = None
    conversion_type: str = Field(pattern="^(lead|appointment|sale|qualified_dm)$")
    source: str = Field(default="manual")
    value: float | None = Field(default=None, ge=0)
    notes: str | None = None


class StoryBlockMetricCreate(BaseModel):
    tenant_slug: str = Field(default="demo")
    sequence_id: str
    block_name: str
    story_start: int | None = Field(default=None, ge=1)
    story_end: int | None = Field(default=None, ge=1)
    views_start: int | None = Field(default=None, ge=0)
    views_end: int | None = Field(default=None, ge=0)
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
            items_count = _insert_story_items(cur, tenant_id, row["id"], payload.payload)
    return {"status": "created", "id": row["id"], "title": title, "created_at": row["created_at"], "story_items": items_count}


@router.get("/sequences/{sequence_id}/items")
def list_sequence_items(sequence_id: str, tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id::text as id, sequence_id::text as sequence_id, story_order,
                       story_type, hook, copy, visual_direction, sticker_type, cta_type,
                       expected_metric, compliance_status, quality_score, created_at
                from story_items
                where tenant_id = %s and sequence_id = %s
                order by story_order asc
                """,
                (tenant_id, sequence_id),
            )
            rows = cur.fetchall()
    return {"items": rows}


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
    tracking_url = f"/api/stories/track/{row['id']}?tenant_slug=demo"
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
        "tracking_url": tracking_url,
        "expected_objections": expected_objections,
        "clara_script": _clara_script(row["title"], keyword, row["main_objection"]),
        "governance": {
            "send_to_patient": False,
            "zapi_write": False,
            "requires_review_before_campaign": True,
            "note": "Handoff pronto para Clara, mas sem envio real automático nesta fase.",
        },
    }


@router.get("/track/{sequence_id}")
def track_sequence_click(
    sequence_id: str,
    tenant_slug: str = "demo",
    user_agent: str | None = Header(default=None),
):
    """Registra clique interno e redireciona para WhatsApp.

    Não envia mensagem, não chama Z-API e não identifica lead. Salva apenas evento agregado.
    """
    handoff = get_sequence_handoff(sequence_id, tenant_slug)
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into story_click_events
                  (tenant_id, sequence_id, origin_tag, utm_campaign, utm_content, user_agent)
                values (%s, %s, %s, %s, %s, %s)
                """,
                (
                    tenant_id,
                    sequence_id,
                    handoff["origin_tag"],
                    handoff["utm"]["utm_campaign"],
                    handoff["utm"]["utm_content"],
                    (user_agent or "")[:240],
                ),
            )
    return RedirectResponse(handoff["whatsapp_url"], status_code=302)


@router.get("/sequences/{sequence_id}/clicks")
def list_sequence_clicks(sequence_id: str, tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select count(*)::int as total_clicks, max(created_at) as last_click_at
                from story_click_events
                where tenant_id = %s and sequence_id = %s
                """,
                (tenant_id, sequence_id),
            )
            summary = cur.fetchone()
            cur.execute(
                """
                select id::text as id, origin_tag, utm_campaign, utm_content, created_at
                from story_click_events
                where tenant_id = %s and sequence_id = %s
                order by created_at desc
                limit 20
                """,
                (tenant_id, sequence_id),
            )
            rows = cur.fetchall()
    return {"summary": summary, "items": rows}


def _sequence_export_payload(sequence_id: str, tenant_slug: str) -> dict[str, Any]:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id::text as id, title, sequence_type, objective, main_objection,
                       patient_moment, support_asset, story_count, payload, created_at
                from story_sequences
                where id = %s and tenant_id = %s
                """,
                (sequence_id, tenant_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "sequence not found")
            cur.execute(
                """
                select story_order, story_type, hook, copy, visual_direction, sticker_type,
                       cta_type, expected_metric, compliance_status, quality_score
                from story_items
                where tenant_id = %s and sequence_id = %s
                order by story_order asc
                """,
                (tenant_id, sequence_id),
            )
            items = cur.fetchall()
    return {"sequence": row, "items": items, "handoff": get_sequence_handoff(sequence_id, tenant_slug)}


@router.get("/sequences/{sequence_id}/export")
def export_sequence(sequence_id: str, tenant_slug: str = "demo", format: str = "telegram") -> Response:
    data = _sequence_export_payload(sequence_id, tenant_slug)
    seq = data["sequence"]
    items = data["items"]
    handoff = data["handoff"]
    if format == "html":
        rows = "".join(
            f"<tr><td>{item['story_order']}</td><td>{_html_escape(item['story_type'])}</td>"
            f"<td>{_html_escape(item['copy'])}</td><td>{_html_escape(item['sticker_type'])}</td>"
            f"<td>{_html_escape(item['compliance_status'])}</td></tr>"
            for item in items
        )
        html = f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>{_html_escape(seq['title'])}</title>
        <body style="font-family:Inter,Arial,sans-serif;max-width:980px;margin:32px auto;line-height:1.5">
        <h1>{_html_escape(seq['title'])}</h1>
        <p><strong>Tipo:</strong> {_html_escape(seq['sequence_type'])} · <strong>Objetivo:</strong> {_html_escape(seq['objective'])}</p>
        <p><strong>Handoff:</strong> {_html_escape(handoff['origin_tag'])}</p>
        <p><strong>Texto WhatsApp:</strong> {_html_escape(handoff['prefilled_text'])}</p>
        <h2>Stories</h2><table border="1" cellspacing="0" cellpadding="8"><thead><tr><th>#</th><th>Função</th><th>Copy</th><th>CTA/Sticker</th><th>Compliance</th></tr></thead><tbody>{rows}</tbody></table>
        <h2>Script Clara</h2><p>{_html_escape(handoff['clara_script'])}</p>
        </body></html>"""
        return HTMLResponse(html)

    lines = [
        f"## Sequência: {seq['title']}",
        f"Tipo: {seq['sequence_type']} | Objetivo: {seq['objective']}",
        f"Objeção principal: {seq['main_objection']}",
        "",
        "### Stories",
    ]
    for item in items:
        lines.extend([
            f"{item['story_order']}. {item['story_type']}",
            f"Copy: {item['copy']}",
            f"Visual: {item['visual_direction'] or 'N/D'}",
            f"CTA/Sticker: {item['sticker_type'] or item['cta_type'] or 'N/D'}",
            f"Métrica esperada: {item['expected_metric'] or 'DM útil'}",
            "",
        ])
    lines.extend([
        "### Handoff Clara",
        f"Tag: {handoff['origin_tag']}",
        f"UTM: {handoff['utm']['utm_campaign']} / {handoff['utm']['utm_content']}",
        f"Texto WhatsApp: {handoff['prefilled_text']}",
        f"Script: {handoff['clara_script']}",
        f"Tracking: {handoff['tracking_url']}",
    ])
    return Response("\n".join(lines), media_type="text/plain; charset=utf-8")



@router.post("/conversions")
def create_conversion(payload: StoryConversionCreate) -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute("select id from story_sequences where id = %s and tenant_id = %s", (payload.sequence_id, tenant_id))
            if not cur.fetchone():
                raise HTTPException(404, "sequence not found")
            cur.execute(
                """
                insert into story_conversions
                  (tenant_id, sequence_id, origin_tag, conversion_type, source, value, notes)
                values (%s, %s, %s, %s, %s, %s, %s)
                returning id::text as id, created_at
                """,
                (
                    tenant_id,
                    payload.sequence_id,
                    payload.origin_tag,
                    payload.conversion_type,
                    payload.source[:80],
                    payload.value,
                    payload.notes,
                ),
            )
            row = cur.fetchone()
    return {"status": "created", "id": row["id"], "created_at": row["created_at"]}


@router.post("/block-metrics")
def create_block_metric(payload: StoryBlockMetricCreate) -> dict:
    retention_pct = None
    drop_pct = None
    if payload.views_start and payload.views_start > 0 and payload.views_end is not None:
        retention_pct = round((payload.views_end / payload.views_start) * 100, 2)
        drop_pct = round(100 - retention_pct, 2)
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute("select id from story_sequences where id = %s and tenant_id = %s", (payload.sequence_id, tenant_id))
            if not cur.fetchone():
                raise HTTPException(404, "sequence not found")
            cur.execute(
                """
                insert into story_block_metrics
                  (tenant_id, sequence_id, block_name, story_start, story_end, views_start, views_end,
                   retention_pct, drop_pct, notes)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                returning id::text as id, retention_pct, drop_pct, created_at
                """,
                (
                    tenant_id,
                    payload.sequence_id,
                    payload.block_name[:120],
                    payload.story_start,
                    payload.story_end,
                    payload.views_start,
                    payload.views_end,
                    retention_pct,
                    drop_pct,
                    payload.notes,
                ),
            )
            row = cur.fetchone()
    return {"status": "created", "id": row["id"], "retention_pct": row["retention_pct"], "drop_pct": row["drop_pct"], "created_at": row["created_at"]}


@router.get("/sequences/{sequence_id}/analytics")
def get_sequence_analytics(sequence_id: str, tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id::text as id, title, sequence_type, objective, main_objection, story_count, created_at
                from story_sequences where id = %s and tenant_id = %s
                """,
                (sequence_id, tenant_id),
            )
            sequence = cur.fetchone()
            if not sequence:
                raise HTTPException(404, "sequence not found")
            cur.execute(
                """
                select count(*)::int as clicks from story_click_events
                where tenant_id = %s and sequence_id = %s
                """,
                (tenant_id, sequence_id),
            )
            clicks = cur.fetchone()["clicks"]
            cur.execute(
                """
                select
                  coalesce(sum(case when conversion_type='qualified_dm' then 1 else 0 end),0)::int as qualified_dms,
                  coalesce(sum(case when conversion_type='lead' then 1 else 0 end),0)::int as leads,
                  coalesce(sum(case when conversion_type='appointment' then 1 else 0 end),0)::int as appointments,
                  coalesce(sum(case when conversion_type='sale' then 1 else 0 end),0)::int as sales,
                  coalesce(sum(value),0)::numeric as conversion_value
                from story_conversions
                where tenant_id = %s and sequence_id = %s
                """,
                (tenant_id, sequence_id),
            )
            conversions = cur.fetchone()
            cur.execute(
                """
                select block_name, story_start, story_end, views_start, views_end,
                       retention_pct, drop_pct, notes, created_at
                from story_block_metrics
                where tenant_id = %s and sequence_id = %s
                order by created_at desc
                limit 20
                """,
                (tenant_id, sequence_id),
            )
            blocks = cur.fetchall()
            cur.execute(
                """
                select coalesce(sum(views),0)::int as views,
                       coalesce(sum(replies),0)::int as replies,
                       coalesce(sum(useful_dms),0)::int as useful_dms,
                       coalesce(sum(leads),0)::int as leads_manual,
                       round(avg(retention_initial_pct),2) as avg_retention_initial_pct
                from story_sequence_performance
                where tenant_id = %s and sequence_id = %s
                """,
                (tenant_id, sequence_id),
            )
            performance = cur.fetchone()
    appointments = conversions["appointments"] or 0
    leads = (conversions["leads"] or 0) + (performance["leads_manual"] or 0)
    conversion_score = round((appointments * 25) + (leads * 10) + ((conversions["qualified_dms"] or 0) * 4) + (clicks * 0.5), 2)
    return {
        "sequence": sequence,
        "clicks": clicks,
        "performance": performance,
        "conversions": conversions,
        "blocks": blocks,
        "score": conversion_score,
        "recommended_next_action": "repetir_com_variacao" if appointments or leads >= 2 else "adaptar_hook_cta",
    }


@router.get("/origin-tags/{origin_tag}/clara-contract")
def get_clara_contract_by_origin(origin_tag: str, tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id::text as id, title, sequence_type, objective, main_objection, payload
                from story_sequences
                where tenant_id = %s and %s like ('stories:stories_ivs_' || regexp_replace(lower(title), '[^a-z0-9áàâãéêíóôõúçñ]+', '-', 'g') || '%%')
                order by created_at desc
                limit 1
                """,
                (tenant_id, origin_tag),
            )
            row = cur.fetchone()
    if not row:
        raise HTTPException(404, "origin_tag not mapped")
    sequence = _payload_sequence(row.get("payload") or {})
    keyword = str(sequence.get("palavraChave") or "quero entender")
    return {
        "origin_tag": origin_tag,
        "sequence_id": row["id"],
        "title": row["title"],
        "keyword": keyword,
        "main_objection": row["main_objection"],
        "clara_instruction": _clara_script(row["title"], keyword, row["main_objection"]),
        "allowed_actions": ["acolher", "perguntar_contexto", "qualificar_spin", "encaminhar_para_agendamento_somente_apos_contexto"],
        "blocked_actions": ["oferecer_horario_na_primeira_resposta", "prometer_resultado", "dar_preco_sem_contexto", "diagnosticar"],
        "pii_policy": "não registrar nome, telefone ou conteúdo sensível neste contrato",
    }


@router.get("/weekly-report")
def weekly_report(tenant_slug: str = "demo", limit: int = 10) -> HTMLResponse:
    limit = max(1, min(limit, 30))
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select s.id::text as id, s.title, s.sequence_type, s.objective, s.main_objection,
                       count(distinct c.id)::int as clicks,
                       coalesce(sum(case when v.conversion_type='qualified_dm' then 1 else 0 end),0)::int as qualified_dms,
                       coalesce(sum(case when v.conversion_type='lead' then 1 else 0 end),0)::int as leads,
                       coalesce(sum(case when v.conversion_type='appointment' then 1 else 0 end),0)::int as appointments,
                       coalesce(sum(case when v.conversion_type='sale' then 1 else 0 end),0)::int as sales,
                       coalesce(sum(p.useful_dms),0)::int as manual_useful_dms,
                       coalesce(sum(p.leads),0)::int as manual_leads,
                       round(coalesce(avg(b.retention_pct),0),2) as avg_block_retention
                from story_sequences s
                left join story_click_events c on c.sequence_id=s.id
                left join story_conversions v on v.sequence_id=s.id
                left join story_sequence_performance p on p.sequence_id=s.id
                left join story_block_metrics b on b.sequence_id=s.id
                where s.tenant_id=%s
                group by s.id
                order by appointments desc, leads desc, qualified_dms desc, clicks desc, s.created_at desc
                limit %s
                """,
                (tenant_id, limit),
            )
            rows = cur.fetchall()
    trs = "".join(
        f"<tr><td>{_html_escape(r['title'])}</td><td>{_html_escape(r['sequence_type'])}</td>"
        f"<td>{r['clicks']}</td><td>{r['qualified_dms'] + r['manual_useful_dms']}</td>"
        f"<td>{r['leads'] + r['manual_leads']}</td><td>{r['appointments']}</td>"
        f"<td>{r['avg_block_retention']}%</td><td>{_html_escape(r['main_objection'])}</td></tr>"
        for r in rows
    )
    html = f"""<!doctype html><html lang=\"pt-BR\"><meta charset=\"utf-8\"><title>Stories Engine IVS — Relatório semanal</title>
    <body style=\"font-family:Inter,Arial,sans-serif;max-width:1100px;margin:32px auto;line-height:1.45;color:#17201d\">
    <h1>Stories Engine IVS — Relatório semanal</h1>
    <p>Ranking operacional por clique, DM qualificada, lead, agendamento e retenção média por bloco. Dados agregados, sem PII.</p>
    <table border=\"1\" cellspacing=\"0\" cellpadding=\"8\"><thead><tr><th>Sequência</th><th>Tipo</th><th>Cliques</th><th>DMs úteis</th><th>Leads</th><th>Agendamentos</th><th>Retenção bloco</th><th>Objeção</th></tr></thead><tbody>{trs}</tbody></table>
    <h2>Próxima ação</h2><p>Repetir sequências com agendamento/lead; adaptar hook+CTA nas sequências com clique sem conversão; descartar temas sem clique e sem retenção.</p>
    </body></html>"""
    return HTMLResponse(html)



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
