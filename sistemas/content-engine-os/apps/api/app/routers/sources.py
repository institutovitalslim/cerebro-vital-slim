import json

from fastapi import APIRouter, HTTPException
from app.schemas import SourceCreate, ThemeCreate
from app.db import get_conn

router = APIRouter(tags=["sources"])


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


@router.get("/sources")
def list_sources(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, network, label, handle_or_url, active, finalidade, objetivo, created_at
                from sources
                where tenant_id = %s
                order by created_at desc
                limit 50
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.post("/sources")
def create_source(payload: SourceCreate) -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into sources (tenant_id, network, label, handle_or_url, active, finalidade, objetivo)
                values (%s, %s, %s, %s, %s, %s, %s)
                returning id, created_at
                """,
                (tenant_id, payload.network, payload.label, payload.handle_or_url, payload.active, payload.finalidade, payload.objetivo),
            )
            row = cur.fetchone()
    return {
        "status": "created",
        "module": "sources",
        "id": row["id"],
        "tenant_slug": payload.tenant_slug,
        "network": payload.network,
        "label": payload.label,
        "created_at": row["created_at"],
    }


@router.get("/themes")
def list_themes(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, theme, objective, format_targets, notes, created_at
                from manual_themes
                where tenant_id = %s
                order by created_at desc
                limit 50
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.post("/themes")
def create_theme(payload: ThemeCreate) -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into manual_themes (tenant_id, theme, objective, format_targets, notes)
                values (%s, %s, %s, %s::jsonb, %s)
                returning id, created_at
                """,
                (
                    tenant_id,
                    payload.theme,
                    payload.objective,
                    json.dumps(payload.format_targets),
                    payload.notes,
                ),
            )
            row = cur.fetchone()
    return {
        "status": "created",
        "module": "manual_themes",
        "id": row["id"],
        "tenant_slug": payload.tenant_slug,
        "theme": payload.theme,
        "objective": payload.objective,
        "formats": payload.format_targets,
        "created_at": row["created_at"],
    }


@router.get("/sources/purposes")
def list_purposes(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute("select chave, label, descricao from source_purposes "
                        "where tenant_id is null or tenant_id=%s order by created_at", (tid,))
            rows = cur.fetchall()
    return {"items": rows}


@router.post("/sources/purposes")
def create_purpose(payload: dict) -> dict:
    import re as _re
    label = (payload.get("label") or "").strip()
    if not label:
        raise HTTPException(400, "label obrigatório")
    chave = _re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")[:40] or "termo"
    with get_conn() as conn:
        tid = _tenant_id(conn, payload.get("tenant_slug", "demo"))
        with conn.cursor() as cur:
            cur.execute("insert into source_purposes (tenant_id, chave, label, descricao) "
                        "values (%s,%s,%s,%s) returning chave", (tid, chave, label, payload.get("descricao")))
            r = cur.fetchone()
    return {"status": "created", "chave": r["chave"], "label": label}


@router.get("/sources/signals")
def list_signals(tenant_slug: str = "demo", classificacao: str = "", limit: int = 60) -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            extra = " and ss.classificacao=%s" if classificacao else ""
            params = [tid] + ([classificacao] if classificacao else []) + [limit]
            cur.execute(
                "select ss.id::text as id, ss.classificacao, ss.likes, ss.comments, ss.engagement, "
                "ss.caption, ss.url, ss.external_code, ss.taken_at, src.label as fonte "
                "from source_signals ss join sources src on src.id=ss.source_id "
                f"where ss.tenant_id=%s{extra} order by ss.engagement desc limit %s", params)
            rows = cur.fetchall()
    return {"items": rows}
