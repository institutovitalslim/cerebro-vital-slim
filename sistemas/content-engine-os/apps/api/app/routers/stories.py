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
