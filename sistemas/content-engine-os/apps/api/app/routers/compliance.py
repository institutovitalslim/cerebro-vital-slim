from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn
from app.services.compliance import assess_creative, assess_text, ensure_compliance_schema

router = APIRouter(prefix="/compliance", tags=["compliance"])


class TextReviewIn(BaseModel):
    tenant_slug: str = Field(default="demo")
    content_body: str
    content_type: str = Field(default="post")


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug=%s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, f"tenant '{tenant_slug}' not found")
    return row["id"]


@router.post("/review-text")
def review_text(payload: TextReviewIn) -> dict:
    result = assess_text(payload.content_body)
    return {"phase": "fase_5_scientific_compliance", "content_type": payload.content_type, **result}


@router.post("/creatives/{creative_id}/assess")
def assess_creative_endpoint(creative_id: str) -> dict:
    with get_conn() as conn:
        result = assess_creative(conn, creative_id)
    if not result:
        raise HTTPException(404, "creative não encontrado")
    return {"phase": "fase_5_scientific_compliance", **result}


@router.get("/overview")
def overview(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        ensure_compliance_schema(conn)
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select
                  count(*)::int as assessments,
                  coalesce(sum(case when risk_level='high' then 1 else 0 end),0)::int as high_risk,
                  coalesce(sum(case when risk_level='medium' then 1 else 0 end),0)::int as medium_risk,
                  coalesce(sum(case when risk_level='low' then 1 else 0 end),0)::int as low_risk,
                  coalesce(avg(score),0)::numeric(8,2) as avg_score
                from compliance_assessments
                where tenant_id=%s
                """,
                (tenant_id,),
            )
            summary = cur.fetchone()
            cur.execute(
                """
                select ca.id::text as id, ca.creative_id::text as creative_id, c.title, c.format,
                       ca.status, ca.risk_level, ca.score, ca.claims, ca.red_flags, ca.evidence,
                       ca.missing_sources, ca.fixes, ca.created_at
                from compliance_assessments ca
                left join creatives c on c.id=ca.creative_id
                where ca.tenant_id=%s
                order by ca.created_at desc
                limit 30
                """,
                (tenant_id,),
            )
            recent = cur.fetchall()
            cur.execute(
                """
                select topic, title, authors, year, evidence_level, main_claim, link
                from scientific_sources
                where tenant_id=%s or tenant_id is null
                order by coalesce(year,0) desc, created_at desc
                limit 30
                """,
                (tenant_id,),
            )
            sources = cur.fetchall()
            cur.execute(
                """
                select id::text as id, title, format, status, quality_score, created_at
                from creatives c
                where tenant_id=%s and status in ('renderizado','gerado','ajustes_solicitados')
                  and not exists (select 1 from compliance_assessments ca where ca.creative_id=c.id)
                order by created_at desc
                limit 20
                """,
                (tenant_id,),
            )
            pending = cur.fetchall()
    return {
        "phase": "fase_5_scientific_compliance",
        "mode": "pre_publication_risk_gate",
        "summary": summary,
        "recent_assessments": recent,
        "pending_creatives": pending,
        "scientific_sources": sources,
        "governance": {
            "auto_publish": False,
            "auto_dm": False,
            "zapi_write": False,
            "blocks_high_risk_publication": True,
            "clinical_claims_need_source": True,
            "required_footer": "Dra Daniely Freitas / CRM-BA 27.588 / conteúdo educativo",
        },
    }
