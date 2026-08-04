from fastapi import APIRouter, HTTPException

from app.db import get_conn
from app.services.codex_client import CodexClient

router = APIRouter(tags=["workspaces"])


def _tenant_by_slug(conn, tenant_slug: str):
    with conn.cursor() as cur:
        cur.execute("select id, slug, name, niche, created_at from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row


def _dashboard_counts(cur, tenant_id: str):
    cur.execute(
        """
        select
          (select count(*) from sources where tenant_id = %(tenant_id)s) as sources,
          (select count(*) from manual_themes where tenant_id = %(tenant_id)s) as themes,
          (select count(*) from opportunities where tenant_id = %(tenant_id)s) as opportunities,
          (select count(*) from briefings where tenant_id = %(tenant_id)s) as briefings,
          (select count(*) from creative_jobs where tenant_id = %(tenant_id)s) as creative_jobs,
          (select count(*) from strategy_intakes where tenant_id = %(tenant_id)s) as strategy_intakes,
          (select count(*) from content_assets where tenant_id = %(tenant_id)s) as assets,
          (select count(*) from calendar_entries where tenant_id = %(tenant_id)s) as calendar_entries
        """,
        {"tenant_id": tenant_id},
    )
    return cur.fetchone()


def _workflow_state(counts: dict) -> dict:
    stages = [
        {
            "key": "strategy",
            "title": "Definir estratégia",
            "description": "Clínica, oferta, dor, objeção e objetivo de conteúdo.",
            "done": counts["strategy_intakes"] > 0,
            "target": "/onboarding",
        },
        {
            "key": "sources",
            "title": "Abastecer repertório",
            "description": "Subir fontes e temas para o sistema parar de trabalhar no vazio.",
            "done": counts["sources"] > 0 and counts["themes"] > 0,
            "target": "/fontes",
        },
        {
            "key": "assets",
            "title": "Subir materiais brutos",
            "description": "Vídeos, imagens, PDFs e provas para virar conteúdo real.",
            "done": counts["assets"] > 0,
            "target": "/biblioteca",
        },
        {
            "key": "production",
            "title": "Gerar peças com direção",
            "description": "Transformar tema e asset em peça com quality gate.",
            "done": counts["creative_jobs"] > 0,
            "target": "/studio",
        },
        {
            "key": "calendar",
            "title": "Virar rotina editorial",
            "description": "Empurrar peças para o calendário com data e status.",
            "done": counts["calendar_entries"] > 0,
            "target": "/calendario",
        },
    ]
    next_stage = next((stage for stage in stages if not stage["done"]), stages[-1])
    completed = sum(1 for stage in stages if stage["done"])
    return {
        "completion_ratio": round(completed / len(stages), 2),
        "completed_steps": completed,
        "total_steps": len(stages),
        "next_stage": next_stage,
        "stages": stages,
    }


@router.get("/workspaces")
def list_workspaces() -> dict:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select id, slug, name, niche, created_at from tenants order by created_at asc")
            rows = cur.fetchall()
    return {"items": rows}


@router.get("/dashboard/summary")
def dashboard_summary(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant = _tenant_by_slug(conn, tenant_slug)
        with conn.cursor() as cur:
            counts = _dashboard_counts(cur, tenant["id"])
    return {"workspace": tenant, "counts": counts}


@router.get("/dashboard/recent")
def dashboard_recent(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant = _tenant_by_slug(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select label, network, created_at
                from sources
                where tenant_id = %s
                order by created_at desc
                limit 4
                """,
                (tenant["id"],),
            )
            sources = cur.fetchall()

            cur.execute(
                """
                select theme, objective, created_at
                from manual_themes
                where tenant_id = %s
                order by created_at desc
                limit 4
                """,
                (tenant["id"],),
            )
            themes = cur.fetchall()

            cur.execute(
                """
                select title, asset_kind, created_at
                from content_assets
                where tenant_id = %s
                order by created_at desc
                limit 4
                """,
                (tenant["id"],),
            )
            assets = cur.fetchall()

            cur.execute(
                """
                select title, format, status, scheduled_for, created_at
                from calendar_entries
                where tenant_id = %s
                order by coalesce(scheduled_for, created_at) asc
                limit 6
                """,
                (tenant["id"],),
            )
            calendar = cur.fetchall()

            cur.execute(
                """
                select format, status, output_payload, created_at
                from creative_jobs
                where tenant_id = %s
                order by created_at desc
                limit 4
                """,
                (tenant["id"],),
            )
            jobs = cur.fetchall()

    return {
        "workspace": tenant,
        "sources": sources,
        "themes": themes,
        "assets": assets,
        "calendar": calendar,
        "jobs": jobs,
    }


@router.get("/workflow/state")
def workflow_state(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant = _tenant_by_slug(conn, tenant_slug)
        with conn.cursor() as cur:
            counts = _dashboard_counts(cur, tenant["id"])
    return {
        "workspace": tenant,
        "counts": counts,
        "workflow": _workflow_state(counts),
    }


@router.get("/dashboard/advisor")
async def dashboard_advisor(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant = _tenant_by_slug(conn, tenant_slug)
        with conn.cursor() as cur:
            counts = _dashboard_counts(cur, tenant["id"])
            cur.execute(
                """
                select theme, objective
                from manual_themes
                where tenant_id = %s
                order by created_at desc
                limit 3
                """,
                (tenant["id"],),
            )
            themes = cur.fetchall()
            cur.execute(
                """
                select title, asset_kind
                from content_assets
                where tenant_id = %s
                order by created_at desc
                limit 3
                """,
                (tenant["id"],),
            )
            assets = cur.fetchall()
            cur.execute(
                """
                select title, status, format
                from calendar_entries
                where tenant_id = %s
                order by coalesce(scheduled_for, created_at) asc
                limit 3
                """,
                (tenant["id"],),
            )
            calendar = cur.fetchall()

    client = CodexClient()
    system = (
        "Você é um operador sênior de marketing para clínicas. "
        "Leia o estado de uma operação de conteúdo e devolva direção prática, curta, clara e priorizada. "
        "Nada de buzzword. Nada de aula. Foco em gargalo, próxima ação e quick wins."
    )
    prompt = f"""
Workspace: {tenant['name']}
Nicho: {tenant['niche']}

Contagens:
- fontes: {counts['sources']}
- temas: {counts['themes']}
- oportunidades: {counts['opportunities']}
- briefings: {counts['briefings']}
- jobs criativos: {counts['creative_jobs']}
- intakes estratégicos: {counts['strategy_intakes']}
- assets: {counts['assets']}
- calendário: {counts['calendar_entries']}

Temas recentes: {themes}
Assets recentes: {assets}
Calendário recente: {calendar}

Responda SOMENTE em JSON com:
- status_label
- diagnosis
- priority
- next_actions (lista com 3 itens)
- quick_wins (lista com 3 itens)
- warning
""".strip()

    result = await client.generate_json(prompt=prompt, system=system)
    data = result.get("json") or {
        "status_label": "Operação em estruturação",
        "diagnosis": "A base do sistema existe, mas ainda precisa amarrar repertório, asset e calendário com mais consistência.",
        "priority": "Transformar material bruto e temas em uma fila editorial viva.",
        "next_actions": [
            "Subir mais assets reais para o sistema parar de trabalhar com amostra pequena.",
            "Criar temas conectados a dor e objeção real da paciente.",
            "Empurrar toda peça relevante para o calendário com status claro.",
        ],
        "quick_wins": [
            "Pegar um asset cru e gerar 3 ângulos diferentes.",
            "Criar um briefing com foco em objeção financeira.",
            "Separar uma semana de publicações por formato e objetivo.",
        ],
        "warning": "Sem auth real e sem Supabase, ainda é operação forte mas não é SaaS completo.",
    }

    return {
        "workspace": tenant,
        "counts": counts,
        "workflow": _workflow_state(counts),
        "advisor": data,
        "engine": {"mode": result.get("mode"), "model": result.get("model")},
    }
