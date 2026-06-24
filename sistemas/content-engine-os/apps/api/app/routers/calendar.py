from datetime import datetime
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn

router = APIRouter(prefix="/calendar", tags=["calendar"])


class CalendarEntryCreate(BaseModel):
    tenant_slug: str = Field(default="demo")
    title: str
    format: str
    channel: str = "instagram"
    objective: str | None = None
    status: str = "planned"
    scheduled_for: datetime | None = None
    notes: str | None = None
    asset_id: str | None = None
    creative_id: str | None = None
    origin_tag: str | None = None
    sprint_thesis: str | None = None
    sprint_hook: str | None = None


class CalendarStatusUpdate(BaseModel):
    status: str
    published_at: datetime | None = None
    notes: str | None = None


class CalendarMetricsIn(BaseModel):
    reach: int | None = None
    views: int | None = None
    retention_rate: float | None = None
    likes: int | None = None
    comments: int | None = None
    replies: int | None = None
    shares: int | None = None
    saves: int | None = None
    profile_clicks: int | None = None
    whatsapp_clicks: int | None = None
    whatsapp_leads: int | None = None
    leads: int | None = None
    appointments: int | None = None
    notes: str | None = None


class PublicationRegisterIn(BaseModel):
    platform: str = Field(default="instagram")
    published_at: datetime | None = None
    platform_post_id: str | None = None
    published_url: str | None = None
    campaign_name: str | None = None
    notes: str | None = None


VALID_STATUSES = {
    "planned",
    "in_review",
    "approved",
    "aprovado_para_publicar",
    "published",
    "publicado",
    "metrics_pending",
    "medido",
}


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


def ensure_phase1_schema(conn) -> None:
    """Evolução idempotente da Fase 1: criativo aprovado vira calendário e medição."""
    with conn.cursor() as cur:
        cur.execute("alter table calendar_entries add column if not exists creative_id uuid references creatives(id) on delete set null")
        cur.execute("alter table calendar_entries add column if not exists origin_tag text")
        cur.execute("alter table calendar_entries add column if not exists sprint_thesis text")
        cur.execute("alter table calendar_entries add column if not exists sprint_hook text")
        cur.execute("alter table calendar_entries add column if not exists published_at timestamptz")
        cur.execute("alter table calendar_entries add column if not exists metrics jsonb not null default '{}'::jsonb")
        cur.execute("alter table calendar_entries add column if not exists metrics_recorded_at timestamptz")
        cur.execute("create unique index if not exists idx_calendar_entries_creative_id on calendar_entries(creative_id) where creative_id is not null")
        cur.execute("create index if not exists idx_calendar_entries_status on calendar_entries(tenant_id, status)")
        cur.execute("alter table publications add column if not exists platform text")
        cur.execute("alter table publications add column if not exists platform_post_id text")
        cur.execute("alter table publications add column if not exists published_url text")
        cur.execute("alter table publications add column if not exists campaign_name text")
        cur.execute("alter table publications add column if not exists notes text")
        cur.execute("create unique index if not exists idx_publications_creative_id_once on publications(creative_id) where creative_id is not null")


@router.get("/entries")
def list_entries(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select e.id::text as id, e.title, e.format, e.channel, e.objective, e.status,
                       e.scheduled_for, e.notes, e.asset_id::text as asset_id, e.created_at,
                       e.creative_id::text as creative_id, e.origin_tag, e.sprint_thesis, e.sprint_hook,
                       e.published_at, e.metrics, e.metrics_recorded_at,
                       c.quality_score, c.status as creative_status, c.asset_url,
                       case when e.metrics_recorded_at is null and e.status in ('published','publicado','metrics_pending') then true else false end as metrics_pending
                from calendar_entries e
                left join creatives c on c.id = e.creative_id
                where e.tenant_id = %s
                order by coalesce(e.scheduled_for, e.created_at) asc
                limit 100
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.post("/entries")
def create_entry(payload: CalendarEntryCreate) -> dict:
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into calendar_entries (
                    tenant_id, title, format, channel, objective, status, scheduled_for, notes, asset_id,
                    creative_id, origin_tag, sprint_thesis, sprint_hook
                ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                returning id::text as id, created_at
                """,
                (
                    tenant_id,
                    payload.title,
                    payload.format,
                    payload.channel,
                    payload.objective,
                    payload.status,
                    payload.scheduled_for,
                    payload.notes,
                    payload.asset_id,
                    payload.creative_id,
                    payload.origin_tag,
                    payload.sprint_thesis,
                    payload.sprint_hook,
                ),
            )
            row = cur.fetchone()
    return {
        "status": "created",
        "id": row["id"],
        "created_at": row["created_at"],
        "title": payload.title,
    }


@router.patch("/entries/{entry_id}/status")
def update_entry_status(entry_id: str, payload: CalendarStatusUpdate) -> dict:
    if payload.status not in VALID_STATUSES:
        raise HTTPException(400, f"status inválido: {payload.status}")
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        with conn.cursor() as cur:
            published_at = payload.published_at if payload.status in ("published", "publicado", "metrics_pending") else None
            if payload.status in ("published", "publicado") and published_at is None:
                cur.execute("select now() as now")
                published_at = cur.fetchone()["now"]
            cur.execute(
                """
                update calendar_entries
                set status=%s,
                    published_at=coalesce(%s, published_at),
                    notes=coalesce(%s, notes)
                where id=%s
                returning id::text as id, creative_id::text as creative_id, status, published_at
                """,
                (payload.status, published_at, payload.notes, entry_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "entrada de calendário não encontrada")
            if row.get("creative_id") and payload.status in ("published", "publicado", "metrics_pending"):
                cur.execute("update creatives set status='publicado' where id=%s", (row["creative_id"],))
                cur.execute(
                    """
                    insert into publications (tenant_id, creative_id, format, published_at, platform, notes)
                    select tenant_id, creative_id, format, coalesce(%s, published_at, now()), channel, %s
                    from calendar_entries where id=%s
                    on conflict (creative_id) where creative_id is not null do update set
                        published_at=coalesce(excluded.published_at, publications.published_at),
                        platform=coalesce(excluded.platform, publications.platform),
                        notes=coalesce(excluded.notes, publications.notes)
                    """,
                    (published_at, payload.notes, entry_id),
                )
            if row.get("creative_id") and payload.status in ("approved", "aprovado_para_publicar"):
                cur.execute("update creatives set status='aprovado' where id=%s", (row["creative_id"],))
    return dict(row)


@router.post("/entries/{entry_id}/publication")
def register_publication(entry_id: str, payload: PublicationRegisterIn) -> dict:
    """Fase 3: registra publicação real vinculada ao criativo, sem publicar nada externamente."""
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                update calendar_entries
                set status='published',
                    published_at=coalesce(%s, published_at, now()),
                    notes=coalesce(%s, notes)
                where id=%s
                returning id::text as id, tenant_id, creative_id::text as creative_id, format, channel, published_at
                """,
                (payload.published_at, payload.notes, entry_id),
            )
            entry = cur.fetchone()
            if not entry:
                raise HTTPException(404, "entrada de calendário não encontrada")
            if entry.get("creative_id"):
                cur.execute("update creatives set status='publicado' where id=%s", (entry["creative_id"],))
            cur.execute(
                """
                insert into publications (
                    tenant_id, creative_id, format, published_at, platform, platform_post_id,
                    published_url, campaign_name, notes, metrics
                ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,'{}'::jsonb)
                on conflict (creative_id) where creative_id is not null do update set
                    published_at=coalesce(excluded.published_at, publications.published_at),
                    platform=excluded.platform,
                    platform_post_id=coalesce(excluded.platform_post_id, publications.platform_post_id),
                    published_url=coalesce(excluded.published_url, publications.published_url),
                    campaign_name=coalesce(excluded.campaign_name, publications.campaign_name),
                    notes=coalesce(excluded.notes, publications.notes)
                returning id::text as id, platform, platform_post_id, published_url, campaign_name, published_at
                """,
                (entry["tenant_id"], entry.get("creative_id"), entry.get("format"), entry.get("published_at"), payload.platform, payload.platform_post_id, payload.published_url, payload.campaign_name, payload.notes),
            )
            pub = cur.fetchone()
    return {"calendar_entry_id": entry["id"], "creative_id": entry.get("creative_id"), "status": "published", "publication": pub}


@router.post("/entries/{entry_id}/metrics")
def save_entry_metrics(entry_id: str, payload: CalendarMetricsIn) -> dict:
    metrics = {k: v for k, v in payload.model_dump().items() if v is not None}
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                update calendar_entries
                set metrics=%s::jsonb,
                    metrics_recorded_at=now(),
                    status='medido'
                where id=%s
                returning id::text as id, creative_id::text as creative_id, metrics, metrics_recorded_at
                """,
                (json.dumps(metrics, ensure_ascii=False), entry_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "entrada de calendário não encontrada")
            if row.get("creative_id"):
                cur.execute(
                    """
                    insert into publications (tenant_id, creative_id, format, published_at, metrics, platform)
                    select tenant_id, creative_id, format, coalesce(published_at, now()), %s::jsonb, channel
                    from calendar_entries where id=%s
                    on conflict (creative_id) where creative_id is not null do update set
                        metrics=excluded.metrics,
                        published_at=coalesce(publications.published_at, excluded.published_at),
                        platform=coalesce(publications.platform, excluded.platform)
                    returning id::text as id
                    """,
                    (json.dumps(metrics, ensure_ascii=False), entry_id),
                )
                pub = cur.fetchone()
            else:
                pub = None
    return {"id": row["id"], "creative_id": row.get("creative_id"), "metrics_recorded_at": row["metrics_recorded_at"], "publication_id": pub.get("id") if pub else None}
