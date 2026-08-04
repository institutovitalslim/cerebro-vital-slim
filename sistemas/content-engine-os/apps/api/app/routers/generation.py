import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn
from app.services.codex_client import CodexClient

router = APIRouter(prefix="/generation", tags=["generation"])


class CreativeGenerateRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    title: str
    audience: str
    objective: str
    format: str
    mechanism: str | None = None
    objections: list[str] = Field(default_factory=list)
    cta: str | None = None


class AdvancedCreativeRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    core_theme: str
    audience: str
    objective: str
    angle: str
    format: str
    hook_style: str = "mecanismo"
    cta: str | None = None


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


@router.get("/creative-jobs")
def list_creative_jobs(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, format, status, output_payload, created_at
                from creative_jobs
                where tenant_id = %s
                order by created_at desc
                limit 50
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.post("/creative")
def generate_creative(payload: CreativeGenerateRequest) -> dict:
    base = {
        "post_estatico": {
            "headline": f"{payload.title}: um novo ângulo para {payload.audience.lower()}",
            "body": f"Explique o mecanismo de {payload.objective.lower()} com clareza, prova e CTA.",
        },
        "carrossel": {
            "slides": [
                "Capa com dor principal",
                "Reframe do problema",
                "Explicação do mecanismo",
                "Quebra de objeção",
                "CTA final",
            ]
        },
        "reel": {
            "hook": f"Se você é {payload.audience.lower()}, talvez o erro não seja falta de esforço.",
            "development": "Explique o mecanismo em linguagem simples, sem promessa agressiva.",
            "cta": payload.cta or "Comente uma palavra-chave para receber o próximo passo.",
        },
        "stories": {
            "frames": [
                "Pergunta de identificação",
                "Micro explicação",
                "Prova/autoridade",
                "CTA",
            ]
        },
    }

    output = base.get(payload.format, base["reel"])
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into creative_jobs (tenant_id, format, status, output_payload)
                values (%s, %s, %s, %s::jsonb)
                returning id, created_at
                """,
                (tenant_id, payload.format, "generated", json.dumps(output)),
            )
            row = cur.fetchone()

    return {
        "status": "generated",
        "id": row["id"],
        "created_at": row["created_at"],
        "tenant_slug": payload.tenant_slug,
        "format": payload.format,
        "payload": output,
    }


@router.post("/advanced")
async def generate_advanced_creative(payload: AdvancedCreativeRequest) -> dict:
    client = CodexClient()
    system = (
        "Você é um estrategista de conteúdo premium para médicos. "
        "Crie saída objetiva, elegante, intuitiva e orientada a resultado. "
        "Sempre pense em reaproveitamento, ângulos, hooks e públicos distintos. "
        "Nunca use promessa médica agressiva."
    )
    prompt = f"""
Tema central: {payload.core_theme}
Público: {payload.audience}
Objetivo: {payload.objective}
Ângulo: {payload.angle}
Formato: {payload.format}
Estilo de hook: {payload.hook_style}
CTA: {payload.cta or 'Defina um CTA filtrando público qualificado'}

Entregue SOMENTE JSON com:
- title
- hook
- development
- cta
- repurposing_angles (lista com 3 ângulos)
- alternate_hooks (lista com 4 hooks)
- audience_splits (lista com 3 variações de público)
- compliance_note
""".strip()

    result = await client.generate_json(prompt=prompt, system=system)
    structured = result.get("json") or {
        "title": payload.core_theme,
        "hook": f"Se você fala com {payload.audience.lower()}, talvez o problema não seja falta de conteúdo, e sim falta de direção.",
        "development": f"Use o ângulo {payload.angle} para mostrar mecanismo, dor e próximo passo com clareza.",
        "cta": payload.cta or "Comente uma palavra-chave para receber o próximo passo.",
        "repurposing_angles": [
            payload.angle,
            "quebra_de_mito",
            "prova_clinica",
        ],
        "alternate_hooks": [
            "O erro que faz seu conteúdo parecer igual ao de toda agência.",
            "Como transformar um tema simples em vários criativos sem virar repetição.",
            "Por que médicos bons continuam invisíveis nas redes.",
            "O problema não é postar pouco. É postar sem função.",
        ],
        "audience_splits": [
            payload.audience,
            f"{payload.audience} com rotina intensa",
            f"{payload.audience} que já tentou terceirizar marketing e se frustrou",
        ],
        "compliance_note": "Manter linguagem educativa, sem garantia ou promessa temporal rígida.",
    }
    output = {
        "engine_mode": result["mode"],
        "engine_model": result["model"],
        "structured": structured,
        "raw_content": result["content"],
    }

    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into creative_jobs (tenant_id, format, status, output_payload)
                values (%s, %s, %s, %s::jsonb)
                returning id, created_at
                """,
                (tenant_id, payload.format, "generated_advanced", json.dumps(output)),
            )
            row = cur.fetchone()

    return {
        "status": "generated",
        "id": row["id"],
        "created_at": row["created_at"],
        "tenant_slug": payload.tenant_slug,
        "format": payload.format,
        "payload": output,
    }
