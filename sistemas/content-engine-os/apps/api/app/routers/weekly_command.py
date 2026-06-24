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
    """Pilares estratégicos derivados do Avatar Mestre IVS.

    Avatar central: mulher que não se reconhece mais no espelho; sente perda de
    controle do corpo, baixa autoestima, compulsão, cansaço, libido baixa e medo
    de tentar de novo. Os pilares viram teses semanais para produção por família.
    """
    return [
        {
            "pillar": "reconexao_identidade_feminina",
            "label": "Reconexão com identidade feminina",
            "thesis": "O Vital Slim não fala só de peso; fala da mulher que quer voltar a se reconhecer no espelho.",
            "objection": "não me reconheço mais",
            "promise_safe": "mostrar caminho médico para recuperar controle, autoestima e direção",
        },
        {
            "pillar": "corpo_nao_responde",
            "label": "Corpo não responde",
            "thesis": "Quando o corpo para de responder, insistir na mesma dieta pode aumentar culpa em vez de resolver o mecanismo.",
            "objection": "meu corpo não responde",
            "promise_safe": "investigar o que está travando antes de culpar força de vontade",
        },
        {
            "pillar": "ja_tentei_de_tudo",
            "label": "Já tentei de tudo",
            "thesis": "Quem já tentou de tudo não precisa de mais uma promessa; precisa de uma avaliação que explique por que não sustentou resultado.",
            "objection": "já tentei e não funcionou",
            "promise_safe": "trocar tentativa no escuro por acompanhamento e leitura individual",
        },
        {
            "pillar": "pos_filhos_corpo_mudou",
            "label": "Depois dos filhos tudo mudou",
            "thesis": "Depois dos filhos, o corpo pode mudar por sono, hormônios, rotina e metabolismo — não por falta de amor-próprio.",
            "objection": "não tenho tempo e sinto culpa por investir em mim",
            "promise_safe": "validar a rotina materna e mostrar cuidado possível, individual e sem julgamento",
        },
        {
            "pillar": "compulsao_acucar_controle",
            "label": "Compulsão por açúcar e controle",
            "thesis": "A vontade incontrolável por doce pode ser sinal de desregulação metabólica e emocional, não falta de caráter.",
            "objection": "não consigo parar de comer doce",
            "promise_safe": "educar sobre controle alimentar com abordagem médica e acolhedora",
        },
        {
            "pillar": "gordura_abdominal_metabolismo",
            "label": "Gordura abdominal e metabolismo",
            "thesis": "A gordura abdominal pode ser um sinal de resistência insulínica, sono ruim e inflamação leve acontecendo juntos.",
            "objection": "faço esforço e a barriga não muda",
            "promise_safe": "explicar mecanismo metabólico com clareza, sem promessa de resultado rápido",
        },
        {
            "pillar": "energia_cansaco_rotina",
            "label": "Energia, cansaço e rotina",
            "thesis": "Cansaço constante, sono ruim e peso travado costumam andar juntos; tratar só a balança deixa parte do problema invisível.",
            "objection": "estou sempre cansada e sem energia",
            "promise_safe": "reposicionar energia como indicador clínico e não como preguiça",
        },
        {
            "pillar": "libido_autoestima_hormonal",
            "label": "Libido, autoestima e hormônios",
            "thesis": "Baixa libido, autoestima baixa e mudança corporal podem fazer parte da mesma história hormonal e emocional.",
            "objection": "tenho baixo desejo sexual e vergonha de falar disso",
            "promise_safe": "abrir conversa médica segura, elegante e sem exposição",
        },
        {
            "pillar": "menopausa_metabolismo",
            "label": "Menopausa e metabolismo",
            "thesis": "Na menopausa, o metabolismo não morreu; ele mudou, e precisa ser lido com outro mapa clínico.",
            "objection": "depois da menopausa nada funciona",
            "promise_safe": "educar sobre hormônios, massa muscular e risco metabólico com segurança",
        },
        {
            "pillar": "medo_efeito_sanfona",
            "label": "Medo do efeito sanfona",
            "thesis": "O medo de voltar a engordar geralmente nasce de planos que emagrecem sem ensinar manutenção e acompanhamento.",
            "objection": "vou emagrecer e engordar tudo de novo",
            "promise_safe": "mostrar valor de acompanhamento, ajuste e manutenção realista",
        },
        {
            "pillar": "executiva_sobrecarregada",
            "label": "Executiva sobrecarregada",
            "thesis": "A mulher que trabalha, cuida da casa e se cobra o tempo todo não precisa de dieta maluca; precisa de estratégia possível.",
            "objection": "não tenho tempo para dietas malucas",
            "promise_safe": "mostrar plano médico adaptado à rotina e não uma rotina idealizada",
        },
        {
            "pillar": "seguranca_medica_valor",
            "label": "Segurança médica e valor",
            "thesis": "Preço só vira objeção quando o valor clínico ainda não ficou claro; segurança, método e acompanhamento precisam aparecer antes.",
            "objection": "tenho medo de gastar e não funcionar",
            "promise_safe": "construir percepção de valor com método, avaliação e autoridade médica",
        },
    ]


def _fallback_reel_hooks(thesis: str) -> list[str]:
    clean = thesis.strip().rstrip('.')
    return [
        f"Se {clean[:92].lower()}, presta atenção nisso.",
        f"Opinião impopular: {clean[:96].lower()}.",
        f"O que ninguém te explicou sobre: {clean[:88].lower()}.",
        f"Antes de tentar de novo, entenda isso: {clean[:86].lower()}.",
        f"Você sabe por que isso acontece? {clean[:86]}",
    ]


def _fetch_reel_hooks(conn, tenant_id: str, thesis: str) -> list[str]:
    kws = [w for w in thesis.lower().replace(';', ' ').replace(',', ' ').split() if len(w) >= 5][:8]
    blob = "lower(coalesce(hook_base,'')||' '||coalesce(tese_central,'')||' '||coalesce(adaptacao_ivs,''))"
    if kws:
        score = " + ".join([f"(case when {blob} like %s then 1 else 0 end)" for _ in kws])
        # Ordem dos parâmetros segue a ordem dos placeholders no SQL:
        # primeiro os LIKEs do score no SELECT, depois o tenant_id do WHERE.
        params = [f"%{k}%" for k in kws] + [tenant_id]
        sql = f"""
            select hook_base, ({score}) as score
            from viral_scripts
            where (tenant_id=%s or tenant_id is null)
              and hook_base is not null
              and (codigo like 'HOOK-%%' or classe_ivs like 'hook_%%' or origem like '%%biblioteca-hooks%%')
            order by score desc, codigo asc
            limit 12
        """
    else:
        params = [tenant_id]
        sql = """
            select hook_base, 0 as score
            from viral_scripts
            where (tenant_id=%s or tenant_id is null)
              and hook_base is not null
              and (codigo like 'HOOK-%%' or classe_ivs like 'hook_%%' or origem like '%%biblioteca-hooks%%')
            order by codigo asc
            limit 12
        """
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    hooks: list[str] = []
    for r in rows:
        h = (r.get("hook_base") or "").strip().strip('"')
        if h and h not in hooks:
            hooks.append(h)
        if len(hooks) >= 5:
            break
    for h in _fallback_reel_hooks(thesis):
        if len(hooks) >= 5:
            break
        if h not in hooks:
            hooks.append(h)
    return hooks[:5]


def _family_from(thesis: str, pillar: str, objective: str, stage: str, hook_variations: list[str] | None = None) -> list[dict]:
    base_tag = pillar.replace("_", "-")
    reel_hooks = (hook_variations or _fallback_reel_hooks(thesis))[:5]
    return [
        {
            "format": "reels",
            "role": "alcance e identificação",
            "hook": reel_hooks[0],
            "hook_variations": reel_hooks,
            "hook_test_minimum": 5,
            "output": "roteiro de 30–45s com 5 hooks alternativos para teste no Reels Trial do Instagram, mecanismo simples e CTA de salvar/compartilhar",
            "cta": "salvar e enviar para alguém que precisa entender isso",
            "metric": "retenção por hook + compartilhamentos",
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
        performance_seed = None
        with conn.cursor() as cur:
            cur.execute(
                """
                select e.sprint_thesis, e.sprint_hook, e.origin_tag, e.format,
                       c.objecao_alvo, c.visual_tipo, c.cta_tipo,
                       coalesce((e.metrics->>'reach')::numeric, 0) as reach,
                       coalesce((e.metrics->>'saves')::numeric, 0) as saves,
                       coalesce((e.metrics->>'shares')::numeric, 0) as shares,
                       coalesce((e.metrics->>'whatsapp_leads')::numeric, (e.metrics->>'leads')::numeric, 0) as leads,
                       coalesce((e.metrics->>'appointments')::numeric, 0) as appointments
                from calendar_entries e
                left join creatives c on c.id=e.creative_id
                where e.tenant_id=%s and e.metrics_recorded_at is not null
                order by (
                    coalesce((e.metrics->>'saves')::numeric, 0) * 4 +
                    coalesce((e.metrics->>'shares')::numeric, 0) * 3 +
                    coalesce((e.metrics->>'whatsapp_leads')::numeric, (e.metrics->>'leads')::numeric, 0) * 12 +
                    coalesce((e.metrics->>'appointments')::numeric, 0) * 25 +
                    coalesce((e.metrics->>'reach')::numeric, 0) / 1000
                ) desc
                limit 1
                """,
                (tenant_id,),
            )
            performance_seed = cur.fetchone()
        seed_thesis = (performance_seed or {}).get("sprint_thesis") or pillars[0]["thesis"]
        seed_origin = (performance_seed or {}).get("origin_tag") or ""
        seed_pillar = seed_origin.split(":")[1].replace("-", "_") if ":" in seed_origin else pillars[0]["pillar"]
        default_hooks = _fetch_reel_hooks(conn, tenant_id, seed_thesis)
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
            "thesis": seed_thesis,
            "pillar": seed_pillar,
            "objective": "autoridade_e_conversa",
            "audience_stage": "consciente_da_dor",
            "family": _family_from(seed_thesis, seed_pillar, "autoridade_e_conversa", "consciente_da_dor", default_hooks),
            "seed_source": "performance_winner" if performance_seed else "pillar_default",
            "winner_variables": performance_seed or {},
        },
        "governance": {
            "mode": "plan_only",
            "blocked": ["auto_publish", "auto_dm", "zapi_write", "medical_promise", "diagnosis"],
            "requires_human_approval": ["publicar", "enviar_mensagem", "impulsionar", "aprovar_criativo"],
        },
    }


@router.post("/family-plan")
def family_plan(payload: FamilyPlanRequest) -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        hook_variations = _fetch_reel_hooks(conn, tenant_id, payload.thesis)
    family = _family_from(payload.thesis, payload.pillar, payload.objective, payload.audience_stage, hook_variations)
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
