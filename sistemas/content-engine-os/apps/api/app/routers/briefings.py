from datetime import datetime
import json

from fastapi import APIRouter, HTTPException
from app.schemas import BriefRequest, BriefResponse
from app.db import get_conn

router = APIRouter(prefix="/briefings", tags=["briefings"])


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


@router.get("")
def list_briefings(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, title, thesis, mechanism, objections, hook_ideas, cta, created_at
                from briefings
                where tenant_id = %s
                order by created_at desc
                limit 50
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.post("/generate", response_model=BriefResponse)
def generate_brief(payload: BriefRequest) -> BriefResponse:
    title = payload.title.strip()
    audience = payload.audience.strip()
    objective = payload.objective.strip()

    thesis = f"Criativo orientado para {audience}, com foco em {objective.lower()}."
    mechanism = "Transformar dor percebida em mecanismo explicável, com ponte comercial segura e CTA claro."
    objections = [
        "já tentei de tudo",
        "isso é só mais uma promessa",
        "não sei se serve para mim",
    ]
    hook_ideas = [
        f"Se você é {audience.lower()} e sente que o conteúdo está sempre igual, veja isso.",
        f"Talvez o problema não seja falta de esforço, e sim falta de direção para {objective.lower()}.",
        f"Antes de criar mais do mesmo, vale entender o mecanismo por trás de {title.lower()}.",
    ]
    cta = "Avance para roteiro, variações e fila de produção."
    created_at = datetime.utcnow()

    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into briefings (tenant_id, title, thesis, mechanism, objections, hook_ideas, cta)
                values (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s)
                returning created_at
                """,
                (
                    tenant_id,
                    title,
                    thesis,
                    mechanism,
                    json.dumps(objections),
                    json.dumps(hook_ideas),
                    cta,
                ),
            )
            row = cur.fetchone()
            if row and row.get("created_at"):
                created_at = row["created_at"]

    return BriefResponse(
        title=title,
        thesis=thesis,
        mechanism=mechanism,
        objections=objections,
        hook_ideas=hook_ideas,
        cta=cta,
        created_at=created_at,
    )
