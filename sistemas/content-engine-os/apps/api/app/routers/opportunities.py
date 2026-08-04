from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


class OpportunityCreate(BaseModel):
    tenant_slug: str = Field(default="demo")
    title: str
    angle: str
    score: float = 50.0
    source_type: str = "manual"


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


@router.get("")
def list_opportunities(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, title, angle, score, source_type, status, created_at
                from opportunities
                where tenant_id = %s
                order by created_at desc
                limit 50
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.post("")
def create_opportunity(payload: OpportunityCreate) -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into opportunities (tenant_id, title, angle, score, source_type)
                values (%s, %s, %s, %s, %s)
                returning id, created_at
                """,
                (tenant_id, payload.title, payload.angle, payload.score, payload.source_type),
            )
            row = cur.fetchone()
    return {
        "status": "created",
        "module": "opportunities",
        "id": row["id"],
        "tenant_slug": payload.tenant_slug,
        "title": payload.title,
        "angle": payload.angle,
        "score": payload.score,
        "source_type": payload.source_type,
        "created_at": row["created_at"],
    }
