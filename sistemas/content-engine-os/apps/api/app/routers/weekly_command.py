from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn

router = APIRouter(prefix="/weekly-command", tags=["weekly-command"])


class FamilyPlanRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    thesis: str = Field(min_length=6, max_length=220)
    pillar: str = Field(default="emagrecimento_metabolico")
    objective: str = Field(default="autoridade_e_conversa")
    audience_stage: str = Field(default="consciente_da_dor")


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug=%s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


def _pillar_cards() -> list[dict]:
    return [
        {
            "pillar": "emagrecimento_metabolico",
            "label": "Emagrecimento metabólico",
            "thesis": "O corpo travado não é falta de força de vontade; é sinal de mecanismo metabólico não investigado.",
            "objection": "já tentei de tudo",
            "promise_safe": "entender o mecanismo antes de insistir em outra dieta",
        },
        {
            "pillar": "hormonios_mulher_35_plus",
            "label": "Hormônios 35+",
            "thesis": "Depois dos 35, sintomas soltos podem ser sinais conectados de desregulação hormonal.",
            "objection": "meus exames sempre dão normais",
            "promise_safe": "olhar sintomas, rotina e exames com contexto clínico",
        },
        {
            "pillar": "tricologia_clinica",
            "label": "Tricologia clínica",
            "thesis": "Queda de cabelo não é só estética; pode ser sintoma-sentinela de desequilíbrio interno.",
            "objection": "já usei shampoo e vitamina",
            "promise_safe": "investigar causa antes de empilhar soluções superficiais",
        },
        {
            "pillar": "metodo_ivs",
            "label": "Método IVS",
            "thesis": "A diferença não está em prometer resultado rápido, mas em acompanhar, medir e ajustar com método.",
            "objection": "vai ser só mais uma consulta",
            "promise_safe": "mostrar o valor do acompanhamento e da avaliação individual",
        },
    ]


def _family_from(thesis: str, pillar: str, objective: str, stage: str) -> list[dict]:
    base_tag = pillar.replace("_", "-")
    return [
        {
            "format": "reels",
            "role": "alcance e identificação",
            "hook": f"Se você sente que '{thesis[:72]}...', talvez o problema não seja esforço.",
            "output": "roteiro de 30–45s com hook, mecanismo simples e CTA de salvar/compartilhar",
            "cta": "salvar e enviar para alguém que precisa entender isso",
            "metric": "retenção + compartilhamentos",
            "production_url": "/producao/reels",
            "origin_tag": f"weekly:{base_tag}:reels",
        },
        {
            "format": "carrossel",
            "role": "autoridade e salvamento",
            "hook": thesis,
            "output": "6–8 slides: capa, rehook, mecanismo, 2 provas/contextos, objeção e CTA",
            "cta": "salvar para revisar antes da próxima tentativa",
            "metric": "salvamentos + compartilhamentos",
            "production_url": "/producao/carrosseis",
            "origin_tag": f"weekly:{base_tag}:carousel",
        },
        {
            "format": "stories",
            "role": "conversa e qualificação",
            "hook": "Enquete/caixinha para mapear quem vive esse problema hoje",
            "output": "sequência com pergunta, bastidor, micro-explicação e CTA para WhatsApp/Clara",
            "cta": "responder palavra-chave ou clicar no link rastreado",
            "metric": "respostas úteis + cliques WhatsApp",
            "production_url": "/stories-engine",
            "origin_tag": f"weekly:{base_tag}:stories",
        },
        {
            "format": "estatico",
            "role": "tese visual e anúncio",
            "hook": thesis,
            "output": "peça única premium com tese, reframe e CTA seguro",
            "cta": "entender se faz sentido para o seu caso",
            "metric": "CTR + comentários qualificados",
            "production_url": "/producao/estaticos",
            "origin_tag": f"weekly:{base_tag}:static",
        },
    ]


@router.get("/overview")
def weekly_overview(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select
                  count(*)::int as total_creatives,
                  coalesce(sum(case when status='renderizado' then 1 else 0 end),0)::int as ready_review,
                  coalesce(sum(case when status='aprovado' then 1 else 0 end),0)::int as approved,
                  coalesce(sum(case when status='ajustes_solicitados' then 1 else 0 end),0)::int as changes_requested
                from creatives where tenant_id=%s
                """,
                (tenant_id,),
            )
            creatives = cur.fetchone()
            cur.execute(
                """
                select count(*)::int as stories,
                       coalesce(sum(case when status='approved' then 1 else 0 end),0)::int as stories_approved
                from story_sequences where tenant_id=%s
                """,
                (tenant_id,),
            )
            stories = cur.fetchone()
            cur.execute(
                """
                select coalesce(sum(case when conversion_type='appointment' then 1 else 0 end),0)::int as appointments,
                       coalesce(sum(case when conversion_type='lead' then 1 else 0 end),0)::int as leads,
                       coalesce(sum(case when conversion_type='qualified_dm' then 1 else 0 end),0)::int as qualified_dms
                from story_conversions where tenant_id=%s and created_at >= now() - interval '30 days'
                """,
                (tenant_id,),
            )
            funnel = cur.fetchone()
    pillars = _pillar_cards()
    priority = "Escolha uma tese semanal, gere uma família completa e só depois aprove/publica."
    if creatives.get("ready_review", 0) > 0:
        priority = "Há peças prontas para revisão; aprove ou peça ajuste antes de criar volume novo."
    if funnel.get("appointments", 0) > 0:
        priority = "Use os temas que já geraram agendamento como base da próxima tese semanal."
    return {
        "mode": "weekly_positioning_sprint",
        "priority": priority,
        "creatives": creatives,
        "stories": stories,
        "funnel": funnel,
        "pillars": pillars,
        "default_plan": {
            "thesis": pillars[0]["thesis"],
            "pillar": pillars[0]["pillar"],
            "objective": "autoridade_e_conversa",
            "audience_stage": "consciente_da_dor",
            "family": _family_from(pillars[0]["thesis"], pillars[0]["pillar"], "autoridade_e_conversa", "consciente_da_dor"),
        },
        "governance": {
            "mode": "plan_only",
            "blocked": ["auto_publish", "auto_dm", "zapi_write", "medical_promise", "diagnosis"],
            "requires_human_approval": ["publicar", "enviar_mensagem", "impulsionar", "aprovar_criativo"],
        },
    }


@router.post("/family-plan")
def family_plan(payload: FamilyPlanRequest) -> dict:
    family = _family_from(payload.thesis, payload.pillar, payload.objective, payload.audience_stage)
    return {
        "thesis": payload.thesis,
        "pillar": payload.pillar,
        "objective": payload.objective,
        "audience_stage": payload.audience_stage,
        "family": family,
        "approval_flow": [
            "Gerar peças nos módulos por formato",
            "Revisar visual/copy/compliance no Banco de Criativos",
            "Aprovar ou solicitar alterações por slide/peça",
            "Planejar no calendário",
            "Registrar performance no BI e Criativos Campeões",
        ],
        "governance": {
            "external_actions": "blocked_by_default",
            "notes": "Plano não publica, não envia DM e não escreve em WhatsApp/Quark/Omie.",
        },
    }
