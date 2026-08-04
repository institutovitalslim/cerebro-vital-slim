"""Router /ads — leitura da performance de mídia paga (Meta Ads via meta_ads_insights_daily)."""
from __future__ import annotations

import json
from statistics import median

from fastapi import APIRouter, HTTPException

from ..db import get_conn
from ..services.codex_client import CodexClient

router = APIRouter(prefix="/ads", tags=["ads"])

# tradução dos tipos de correspondência do Google Ads (p/ instruções sem ambiguidade)
_MATCH_PT = {"EXACT": "exata", "PHRASE": "frase", "BROAD": "ampla"}


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug=%s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="tenant não encontrado")
    return row["id"]


@router.get("/overview")
def ads_overview(tenant_slug: str = "demo", days: int = 30) -> dict:
    days = max(1, min(days, 90))
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select coalesce(sum(spend),0)::numeric(12,2) as spend,
                       coalesce(sum(impressions),0) as impressions,
                       coalesce(sum(reach),0) as reach,
                       coalesce(sum(clicks),0) as clicks,
                       coalesce(sum(link_clicks),0) as link_clicks,
                       coalesce(sum(messaging_starts),0) as messaging_starts,
                       coalesce(sum(leads),0) as leads,
                       min(metric_date) as from_date,
                       max(metric_date) as to_date
                from meta_ads_insights_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                """,
                (tid, days))
            totals = cur.fetchone()

            cur.execute(
                """
                select campaign_id, max(campaign_name) as campaign_name,
                       sum(spend)::numeric(12,2) as spend,
                       sum(impressions) as impressions,
                       sum(clicks) as clicks,
                       sum(messaging_starts) as messaging_starts,
                       sum(leads) as leads,
                       case when sum(messaging_starts) > 0
                            then (sum(spend)/sum(messaging_starts))::numeric(10,2) end as custo_por_conversa,
                       max(metric_date) as last_active
                from meta_ads_insights_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                group by campaign_id
                order by sum(spend) desc
                """,
                (tid, days))
            campaigns = cur.fetchall()

            cur.execute(
                """
                select metric_date, sum(spend)::numeric(12,2) as spend,
                       sum(clicks) as clicks, sum(messaging_starts) as messaging_starts
                from meta_ads_insights_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                group by metric_date order by metric_date
                """,
                (tid, days))
            daily = cur.fetchall()

            google_totals, google_campaigns = None, []
            cur.execute("select to_regclass('google_ads_insights_daily') is not null as ok")
            if cur.fetchone()["ok"]:
                cur.execute(
                    """
                    select coalesce(sum(spend),0)::numeric(12,2) as spend,
                           coalesce(sum(impressions),0) as impressions,
                           coalesce(sum(clicks),0) as clicks,
                           coalesce(sum(conversions),0)::numeric(10,2) as conversions
                    from google_ads_insights_daily
                    where tenant_id=%s and metric_date >= current_date - %s::int
                    """,
                    (tid, days))
                google_totals = cur.fetchone()
                cur.execute(
                    """
                    select campaign_id, max(campaign_name) as campaign_name,
                           max(channel_type) as channel_type,
                           sum(spend)::numeric(12,2) as spend,
                           sum(clicks) as clicks,
                           sum(conversions)::numeric(10,2) as conversions,
                           case when sum(conversions) > 0
                                then (sum(spend)/sum(conversions))::numeric(10,2) end as cpa,
                           max(metric_date) as last_active
                    from google_ads_insights_daily
                    where tenant_id=%s and metric_date >= current_date - %s::int
                    group by campaign_id having sum(spend) > 0
                    order by sum(spend) desc
                    """,
                    (tid, days))
                google_campaigns = cur.fetchall()

    spend = float(totals["spend"] or 0)
    msgs = int(totals["messaging_starts"] or 0)
    return {
        "window_days": days,
        "totals": {
            **totals,
            "custo_por_conversa": round(spend / msgs, 2) if msgs else None,
        },
        "campaigns": campaigns,
        "daily": daily,
        "google": {"totals": google_totals, "campaigns": google_campaigns},
        "readiness": {
            "meta_ads": "ativo (coleta diária 06:50, horário da Bahia — scripts/meta_ads_ingest.py)",
            "google_ads": "ativo (coleta diária 06:55, horário da Bahia — google_ads_fetch.py | google_ads_load.py)",
        },
    }


# ── Decisão de campanhas ─────────────────────────────────────────────────────
# Semáforo determinístico por campanha: janela atual vs anterior, custo por
# resultado vs mediana do canal, tendência, fadiga (frequency) e gasto sem
# retorno. Regras explicáveis — cada veredito carrega os motivos em texto.

_GASTO_MIN_DECISAO = 30.0   # abaixo disso não há volume p/ decidir
_GASTO_SEM_RESULTADO = 50.0  # gasto >= isso com 0 resultados = vermelho
_FADIGA_FREQ = 3.5


def _brl(v: float) -> str:
    return ("R$ %.2f" % v).replace(".", ",")


def _decide(c: dict, mediana_canal: float | None) -> None:
    """Anota semaforo/motivos/acao na campanha (mutação in-place)."""
    gasto, res = c["gasto"], c["resultado"]
    custo, custo_ant = c["custo_res"], c["custo_res_ant"]
    unidade = c["tipo_resultado"]
    motivos: list[str] = []
    nivel = 1  # 0=verde 1=amarelo 2=vermelho

    if gasto < _GASTO_MIN_DECISAO:
        c.update(semaforo="amarelo", acao="Aguardar volume",
                 motivos=[f"Gasto de {_brl(gasto)} na janela ainda é baixo para decidir"])
        return

    if res == 0:
        if gasto >= _GASTO_SEM_RESULTADO:
            c.update(semaforo="vermelho", acao="Pausar ou reestruturar",
                     motivos=[f"{_brl(gasto)} gastos sem nenhum resultado na janela"])
        else:
            c.update(semaforo="amarelo", acao="Observar mais alguns dias",
                     motivos=[f"{_brl(gasto)} gastos e ainda sem resultado"])
        return

    # custo vs mediana do canal
    if mediana_canal and custo is not None:
        razao = custo / mediana_canal
        if razao <= 0.7:
            nivel = 0
            motivos.append(f"Custo/{unidade} de {_brl(custo)} — {round((1-razao)*100)}% abaixo da mediana do canal ({_brl(mediana_canal)})")
        elif razao >= 1.8:
            nivel = 2
            motivos.append(f"Custo/{unidade} de {_brl(custo)} — {round(razao, 1)}x a mediana do canal ({_brl(mediana_canal)})")
        else:
            motivos.append(f"Custo/{unidade} de {_brl(custo)} próximo da mediana do canal ({_brl(mediana_canal)})")

    # tendência vs janela anterior
    if custo is not None and custo_ant:
        var = (custo - custo_ant) / custo_ant
        if var >= 0.4:
            nivel = min(2, nivel + 1)
            motivos.append(f"Custo/{unidade} subiu {round(var*100)}% vs janela anterior ({_brl(custo_ant)} → {_brl(custo)})")
        elif var <= -0.25:
            motivos.append(f"Custo/{unidade} caiu {round(-var*100)}% vs janela anterior — tendência boa")
    elif custo is not None and c["gasto_ant"] < _GASTO_MIN_DECISAO:
        motivos.append("Sem janela anterior comparável (campanha recente)")

    # fadiga de criativo (só Meta tem frequency)
    if c.get("frequency") and c["frequency"] >= _FADIGA_FREQ:
        nivel = max(nivel, 1)
        motivos.append(f"Frequência média {round(c['frequency'], 1)} — público saturando, criativo pede renovação")

    c["semaforo"] = ("verde", "amarelo", "vermelho")[nivel]
    c["acao"] = (
        "Escalar orçamento (+20% e reavaliar em 3–4 dias)",
        "Manter e observar",
        "Revisar criativo/segmentação ou pausar",
    )[nivel]
    c["motivos"] = motivos


@router.get("/decisao")
def ads_decisao(tenant_slug: str = "demo", days: int = 7) -> dict:
    days = max(3, min(days, 30))
    campanhas: list[dict] = []
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select campaign_id, max(campaign_name) as campaign_name,
                       coalesce(sum(spend) filter (where metric_date >= current_date - %(d)s::int), 0)::float as gasto,
                       coalesce(sum(spend) filter (where metric_date <  current_date - %(d)s::int), 0)::float as gasto_ant,
                       coalesce(sum(messaging_starts) filter (where metric_date >= current_date - %(d)s::int), 0)::float as resultado,
                       coalesce(sum(messaging_starts) filter (where metric_date <  current_date - %(d)s::int), 0)::float as resultado_ant,
                       avg(frequency) filter (where metric_date >= current_date - %(d)s::int)::float as frequency,
                       max(metric_date) as last_active
                from meta_ads_insights_daily
                where tenant_id=%(tid)s and metric_date >= current_date - 2*%(d)s::int
                group by campaign_id having sum(spend) > 0
                """,
                {"tid": tid, "d": days})
            for r in cur.fetchall():
                campanhas.append({**dict(r), "canal": "meta", "tipo_resultado": "conversa"})

            cur.execute("select to_regclass('google_ads_insights_daily') is not null as ok")
            if cur.fetchone()["ok"]:
                cur.execute(
                    """
                    select campaign_id, max(campaign_name) as campaign_name,
                           coalesce(sum(spend) filter (where metric_date >= current_date - %(d)s::int), 0)::float as gasto,
                           coalesce(sum(spend) filter (where metric_date <  current_date - %(d)s::int), 0)::float as gasto_ant,
                           coalesce(sum(conversions) filter (where metric_date >= current_date - %(d)s::int), 0)::float as resultado,
                           coalesce(sum(conversions) filter (where metric_date <  current_date - %(d)s::int), 0)::float as resultado_ant,
                           null::float as frequency,
                           max(metric_date) as last_active
                    from google_ads_insights_daily
                    where tenant_id=%(tid)s and metric_date >= current_date - 2*%(d)s::int
                    group by campaign_id having sum(spend) > 0
                    """,
                    {"tid": tid, "d": days})
                for r in cur.fetchall():
                    campanhas.append({**dict(r), "canal": "google", "tipo_resultado": "conversão"})

    for c in campanhas:
        c["custo_res"] = round(c["gasto"] / c["resultado"], 2) if c["resultado"] else None
        c["custo_res_ant"] = round(c["gasto_ant"] / c["resultado_ant"], 2) if c["resultado_ant"] else None

    medianas: dict[str, float | None] = {}
    for canal in ("meta", "google"):
        custos = [c["custo_res"] for c in campanhas if c["canal"] == canal and c["custo_res"]]
        medianas[canal] = round(median(custos), 2) if custos else None

    for c in campanhas:
        _decide(c, medianas[c["canal"]])

    ordem = {"vermelho": 0, "amarelo": 1, "verde": 2}
    campanhas.sort(key=lambda c: (ordem[c["semaforo"]], -c["gasto"]))
    return {
        "janela_dias": days,
        "medianas_canal": medianas,
        "resumo": {s: sum(1 for c in campanhas if c["semaforo"] == s) for s in ("verde", "amarelo", "vermelho")},
        "campanhas": campanhas,
    }


# ── Cockpit de tráfego (detalhe do detalhe) ─────────────────────────────────
# Payload único da página /trafego: fila de ações executáveis priorizada por R$,
# criativos da Meta com leads CTWA qualificados, termos de pesquisa do Google
# (negativação com detecção de conflito por família) e keywords. Regras 100%
# determinísticas — toda recomendação carrega a evidência numérica.

_NEG_GASTO_MIN = 15.0        # termo sem conversão só vira ação com gasto relevante
_KW_PAUSA_GASTO_MIN = 30.0
_CRIATIVO_GASTO_MIN = 50.0
_ENGAJADO_MSGS = 3           # >=3 msgs inbound em 7d = lead engajado (proxy)


def _familia(term: str) -> str:
    """Agrupa termos por 'família' (2 primeiras palavras significativas)."""
    stop = {"em", "de", "da", "do", "para", "no", "na", "o", "a", "que", "com"}
    words = [w for w in (term or "").lower().split() if w not in stop]
    return " ".join(words[:2]) if words else (term or "")


@router.get("/cockpit")
def ads_cockpit(tenant_slug: str = "demo", days: int = 30) -> dict:
    days = max(7, min(days, 90))
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            # ---- Google: termos na granularidade campanha → grupo → termo
            cur.execute(
                """
                select campaign_name, ad_group_name, term,
                       sum(spend)::float as gasto, sum(clicks)::int as cliques,
                       sum(conversions)::float as conv
                from google_ads_search_terms_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                group by campaign_name, ad_group_name, term
                """, (tid, days))
            termos_grao = [dict(r) for r in cur.fetchall()]

    # agregado por termo (p/ regras de família — um termo pode aparecer em 2 grupos)
    _por_termo: dict[str, dict] = {}
    for t in termos_grao:
        agg = _por_termo.setdefault(t["term"], {"term": t["term"], "gasto": 0.0, "cliques": 0,
                                                "conv": 0.0, "campaign_name": t["campaign_name"],
                                                "ad_group_name": t["ad_group_name"]})
        agg["gasto"] += t["gasto"]
        agg["cliques"] += t["cliques"]
        agg["conv"] += t["conv"]
    termos = list(_por_termo.values())
    with get_conn() as conn:
        with conn.cursor() as cur:

            # ---- Google: keywords por campanha → grupo (árvore estilo BM)
            cur.execute(
                """
                select campaign_name, ad_group_name, keyword,
                       match_type, max(kw_status) as kw_status,
                       sum(spend)::float as gasto, sum(clicks)::int as cliques,
                       sum(conversions)::float as conv
                from google_ads_keywords_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                group by campaign_name, ad_group_name, keyword, match_type
                """, (tid, days))
            keywords = [dict(r) for r in cur.fetchall()]

            # ---- Google: anúncios RSA por campanha → grupo
            cur.execute(
                """
                select campaign_name, ad_group_name, ad_id,
                       max(ad_status) as ad_status,
                       (array_agg(headlines order by metric_date desc))[1] as headlines,
                       sum(spend)::float as gasto, sum(clicks)::int as cliques,
                       sum(conversions)::float as conv
                from google_ads_ads_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                group by campaign_name, ad_group_name, ad_id
                having sum(impressions) > 0
                """, (tid, days))
            google_anuncios = [dict(r) for r in cur.fetchall()]

            # ---- Meta: criativos agregados + metadados + leads CTWA
            cur.execute(
                """
                with ins as (
                  select ad_id, max(ad_name) as ad_name, max(campaign_name) as campaign_name,
                         max(adset_name) as adset_name,
                         sum(spend)::float as gasto, sum(impressions)::int as impressoes,
                         sum(clicks)::int as cliques, sum(messaging_starts)::int as conversas,
                         avg(frequency)::float as freq,
                         sum(video_plays)::int as plays, sum(video_thruplays)::int as thruplays
                  from meta_ads_ad_insights_daily
                  where tenant_id=%s and metric_date >= current_date - %s::int
                  group by ad_id
                ), ctwa as (
                  select source_id as ad_id, count(*)::int as leads,
                         count(*) filter (where msgs_7d >= %s)::int as engajados,
                         count(*) filter (where msgs_7d <= 1)::int as frios
                  from whatsapp_ctwa_leads
                  where tenant_id=%s and first_ts >= current_date - %s::int
                  group by source_id
                )
                select i.*, c.title, c.body, c.thumbnail_url, c.object_type, c.status,
                       c.instagram_permalink,
                       coalesce(w.leads, 0) as leads_ctwa,
                       coalesce(w.engajados, 0) as leads_engajados,
                       coalesce(w.frios, 0) as leads_frios
                from ins i
                left join meta_ads_creatives c on c.ad_id = i.ad_id
                left join ctwa w on w.ad_id = i.ad_id
                where i.gasto > 0
                order by i.gasto desc
                """, (tid, days, _ENGAJADO_MSGS, tid, days))
            criativos = [dict(r) for r in cur.fetchall()]

            # selo "roteiros prontos" nos cards
            rot_counts: dict[str, int] = {}
            cur.execute("select to_regclass('ads_roteiros_gerados') is not null as ok")
            if cur.fetchone()["ok"]:
                cur.execute(
                    "select ad_id, count(*)::int as n from ads_roteiros_gerados "
                    "where tenant_id=%s group by ad_id", (tid,))
                rot_counts = {r["ad_id"]: r["n"] for r in cur.fetchall()}
            for c in criativos:
                c["roteiros_count"] = rot_counts.get(c["ad_id"], 0)

            # ---- série diária p/ o gráfico de evolução (gasto × leads bons)
            cur.execute(
                """
                with m as (
                  select metric_date as d, sum(spend)::float as gasto, sum(messaging_starts)::int as conversas
                  from meta_ads_insights_daily
                  where tenant_id=%(tid)s and metric_date >= current_date - %(d)s::int
                  group by metric_date
                ), g as (
                  select metric_date as d, sum(spend)::float as gasto
                  from google_ads_insights_daily
                  where tenant_id=%(tid)s and metric_date >= current_date - %(d)s::int
                  group by metric_date
                ), w as (
                  select first_ts::date as d, count(*)::int as leads,
                         count(*) filter (where msgs_7d >= %(eng)s)::int as engajados
                  from whatsapp_ctwa_leads
                  where tenant_id=%(tid)s and first_ts >= current_date - %(d)s::int
                  group by first_ts::date
                )
                select coalesce(m.d, g.d, w.d) as dia,
                       coalesce(m.gasto, 0) + coalesce(g.gasto, 0) as gasto,
                       coalesce(m.conversas, 0) as conversas,
                       coalesce(w.leads, 0) as leads,
                       coalesce(w.engajados, 0) as engajados
                from m full join g on g.d = m.d full join w on w.d = coalesce(m.d, g.d)
                order by 1
                """, {"tid": tid, "d": days, "eng": _ENGAJADO_MSGS})
            serie_diaria = [dict(r) for r in cur.fetchall()]

            # ---- leads CTWA recentes (tabela de leads com anúncio de origem)
            cur.execute(
                """
                select phone, sender_name, first_ts, source_id, ad_title, media_type,
                       msgs_7d, msgs_total, first_text, conversa_amostra
                from whatsapp_ctwa_leads
                where tenant_id=%s and first_ts >= current_date - %s::int
                order by first_ts desc limit 120
                """, (tid, days))
            leads_recentes = [dict(r) for r in cur.fetchall()]

            # fluxo de conversas: por dia (30d), semana (12) e mês (6)
            fluxo_leads = {"por_dia": [], "por_semana": [], "por_mes": []}
            cur.execute("select to_regclass('whatsapp_fluxo_diario') is not null as ok")
            if cur.fetchone()["ok"]:
                _FONTES = ("fonte_anuncio_ig, fonte_anuncio_fb, fonte_site_google, "
                           "fonte_indicacao, fonte_outros")
                cur.execute(
                    f"""
                    select dia::text as periodo, contatos_ativos, contatos_novos,
                           msgs_inbound, ctwa_leads, {_FONTES}
                    from whatsapp_fluxo_diario
                    where tenant_id=%s and dia >= current_date - 30
                    order by dia
                    """, (tid,))
                fluxo_leads["por_dia"] = [dict(r) for r in cur.fetchall()]
                _FONTES_SUM = ", ".join(f"sum({c})::int as {c}" for c in
                                        ("fonte_anuncio_ig", "fonte_anuncio_fb",
                                         "fonte_site_google", "fonte_indicacao", "fonte_outros"))
                cur.execute(
                    f"""
                    select to_char(date_trunc('week', dia), 'DD/MM') as periodo,
                           sum(contatos_ativos)::int as contatos_ativos,
                           sum(contatos_novos)::int as contatos_novos,
                           sum(msgs_inbound)::int as msgs_inbound,
                           sum(ctwa_leads)::int as ctwa_leads, {_FONTES_SUM}
                    from whatsapp_fluxo_diario
                    where tenant_id=%s and dia >= current_date - 84
                    group by date_trunc('week', dia) order by date_trunc('week', dia)
                    """, (tid,))
                fluxo_leads["por_semana"] = [dict(r) for r in cur.fetchall()]
                cur.execute(
                    f"""
                    select to_char(date_trunc('month', dia), 'MM/YYYY') as periodo,
                           sum(contatos_ativos)::int as contatos_ativos,
                           sum(contatos_novos)::int as contatos_novos,
                           sum(msgs_inbound)::int as msgs_inbound,
                           sum(ctwa_leads)::int as ctwa_leads, {_FONTES_SUM}
                    from whatsapp_fluxo_diario
                    where tenant_id=%s and dia >= current_date - 185
                    group by date_trunc('month', dia) order by date_trunc('month', dia)
                    """, (tid,))
                fluxo_leads["por_mes"] = [dict(r) for r in cur.fetchall()]

    for k in keywords:
        k["cpa"] = round(k["gasto"] / k["conv"], 2) if k["conv"] else None
    for g in google_anuncios:
        g["cpa"] = round(g["gasto"] / g["conv"], 2) if g["conv"] else None

    # estado ATUAL da conta (snapshots): keywords existentes (mesmo sem tráfego ainda)
    # e negativas já aplicadas — para nunca recomendar o que JÁ FOI FEITO
    kw_snapshot: set[str] = set()
    negativas_atuais: list[str] = []
    negativas_escopo: list[dict] = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select to_regclass('google_ads_keywords_atuais') is not null as ok")
            if cur.fetchone()["ok"]:
                cur.execute(
                    "select campaign_name, ad_group_name, keyword, match_type, kw_status "
                    "from google_ads_keywords_atuais where tenant_id=%s", (tid,))
                snap = cur.fetchall()
                kw_snapshot = {(r["keyword"] or "").lower().strip() for r in snap}
                # status do snapshot corrige o defasado do relatório — chave por
                # (campanha, grupo, keyword, MATCH TYPE): a mesma palavra existe
                # em versões frase/exata no MESMO grupo, cada uma com seu status
                def _chave(c, g, k, m):
                    return ((c or "").strip(), (g or "").strip(),
                            (k or "").lower().strip(), (m or "").upper().strip())
                status_atual: dict = {}
                for r in snap:
                    ch = _chave(r["campaign_name"], r["ad_group_name"], r["keyword"], r["match_type"])
                    if status_atual.get(ch) != "ENABLED":  # se qualquer critério igual está ativo, vale ativo
                        status_atual[ch] = r["kw_status"]
                for k in keywords:
                    st = status_atual.get(_chave(k.get("campaign_name"), k.get("ad_group_name"),
                                                 k["keyword"], k.get("match_type")))
                    if st:
                        k["kw_status"] = st
            cur.execute("select to_regclass('google_ads_negativos') is not null as ok")
            if cur.fetchone()["ok"]:
                cur.execute("select keyword, nivel, campaign_name, ad_group_name "
                            "from google_ads_negativos where tenant_id=%s", (tid,))
                _negrows = cur.fetchall()
                negativas_atuais = [(r["keyword"] or "").lower().strip() for r in _negrows]
                negativas_escopo = [{"kw": (r["keyword"] or "").lower().strip(), "nivel": r["nivel"],
                                     "campanha": (r["campaign_name"] or "").strip(),
                                     "grupo": (r["ad_group_name"] or "").strip()} for r in _negrows]

    def ja_negativado(term: str) -> bool:
        t = (term or "").lower().strip()
        return any(n == t or (n and n in t) for n in negativas_atuais)

    kw_ativas = {(k["keyword"] or "").lower().strip() for k in keywords} | kw_snapshot
    termos = [t for t in termos if not ja_negativado(t["term"])]
    termos_grao = [t for t in termos_grao if not ja_negativado(t["term"])]
    acoes: list[dict] = []

    # ── Regra 0: SENTINELA — termos fora do alvo detectados pela IA (outro
    #    médico, grátis/SUS, outra cidade…). O que já foi negativado na conta
    #    ou converteu (90d, independente do filtro da página) sai da fila sozinho.
    sentinela_itens: list[dict] = []
    negativas_frase: list[dict] = []
    sentinela_info: dict = {"gerada_em": None, "desatualizada": True}
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(_DDL_SENTINELA)
            cur.execute(_DDL_SENTINELA_RUNS)
            cur.execute(
                "select distinct lower(trim(term)) as t from google_ads_search_terms_daily "
                "where tenant_id=%s and conversions > 0 and metric_date >= current_date - 90", (tid,))
            termos_convertidos = {r["t"] for r in cur.fetchall()}
            cur.execute(
                "select termo, categoria, motivo, campanha, grupo, gasto, cliques, nivel, janela_dias "
                "from ads_negativas_semanticas where tenant_id=%s and categoria <> 'ok' "
                "order by gasto desc nulls last, termo", (tid,))
            _sem = [dict(r) for r in cur.fetchall()]
            cur.execute("select max(executado_em) as m from ads_sentinela_runs where tenant_id=%s", (tid,))
            _run = cur.fetchone()["m"]
            cur.execute("select max(collected_at) as m from google_ads_search_terms_daily where tenant_id=%s", (tid,))
            _col = cur.fetchone()["m"]
    if _run:
        sentinela_info = {"gerada_em": _run.isoformat(),
                          "desatualizada": bool(_col and _run < _col)}
    for r in _sem:
        _t = (r["termo"] or "").lower().strip()
        if ja_negativado(r["termo"]) or _t in termos_convertidos:
            continue
        (negativas_frase if r.get("nivel") == "frase" else sentinela_itens).append(r)
    if sentinela_itens:
        _jan = next((r.get("janela_dias") for r in sentinela_itens if r.get("janela_dias")), 60)
        _gasto_sem = round(sum(r["gasto"] or 0 for r in sentinela_itens), 2)
        _cats: dict[str, int] = {}
        for r in sentinela_itens:
            _cats[r["categoria"]] = _cats.get(r["categoria"], 0) + 1
        _leg = ", ".join(f"{_SENTINELA_ROTULO.get(c, c)} ({n})"
                         for c, n in sorted(_cats.items(), key=lambda x: -x[1]))
        acoes.append({
            "tipo": "negativar_ia", "canal": "google",
            "titulo": f"Blindar a verba: negativar {len(sentinela_itens)} pesquisa(s) fora do alvo",
            "impacto_mensal": round(_gasto_sem * 30 / _jan, 2) if _gasto_sem else None,
            "evidencia": f"a IA leu as pesquisas reais e achou gente procurando outra coisa — {_leg}",
            "conflito": None,
            "itens": [{"termo": r["termo"], "gasto": round(r["gasto"] or 0, 2),
                       "cliques": r["cliques"] or 0, "campanha": r["campanha"],
                       "grupo": r["grupo"], "categoria": r["categoria"], "motivo": r["motivo"]}
                      for r in sentinela_itens],
            "passos": ["Google Ads → Palavras-chave → Palavras-chave negativas → + no nível da CAMPANHA (ou na lista de negativas da conta)",
                       "Escolher o formato ao copiar: [exata] bloqueia só a pesquisa idêntica · \"frase\" bloqueia o que contém a sequência · ampla bloqueia qualquer pesquisa com essas palavras (a mais garantida p/ nomes de médicos/concorrentes)",
                       "Colar a lista — na próxima atualização elas somem daqui"],
        })

    # ── Regra 1: NEGATIVAR — termos com gasto e zero conversão, por família
    familias: dict[str, dict] = {}
    for t in termos:
        fam = _familia(t["term"])
        f = familias.setdefault(fam, {"sem_conv": [], "com_conv": []})
        (f["com_conv"] if t["conv"] > 0 else f["sem_conv"]).append(t)
    for fam, f in familias.items():
        candidatos = [t for t in f["sem_conv"] if t["gasto"] >= _NEG_GASTO_MIN]
        if not candidatos:
            continue
        gasto_total = round(sum(t["gasto"] for t in candidatos), 2)
        conflito = None
        if f["com_conv"]:
            bons = ", ".join(f"'{t['term']}' ({t['conv']:.1f} conv)" for t in f["com_conv"][:3])
            conflito = (f"ATENÇÃO: na mesma família, {bons} CONVERTEU — negativar como frase "
                        f"mataria termo bom. Negative apenas os termos EXATOS listados.")
        acoes.append({
            "tipo": "negativar", "canal": "google",
            "titulo": f"Negativar {len(candidatos)} termo(s) da família “{fam}”",
            "impacto_mensal": round(gasto_total * 30 / days, 2),
            "evidencia": f"{_brl(gasto_total)} em {days}d, {sum(t['cliques'] for t in candidatos)} cliques, 0 conversões",
            "conflito": conflito,
            "itens": [{"termo": t["term"], "gasto": round(t["gasto"], 2), "cliques": t["cliques"],
                       "campanha": t["campaign_name"]} for t in sorted(candidatos, key=lambda x: -x["gasto"])],
            "passos": ["Google Ads → Palavras-chave → Palavras-chave negativas → + no nível da campanha",
                       "Adicionar cada termo como correspondência EXATA: [termo]"],
        })

    # ── Regra 2: KEYWORD NOVA — termo que converte e não é keyword
    novas = [t for t in termos
             if t["conv"] > 0 and (t["term"] or "").lower().strip() not in kw_ativas]
    if novas:
        acoes.append({
            "tipo": "keyword_nova", "canal": "google",
            "titulo": f"Adicionar {len(novas)} termo(s) que convertem como keyword exata",
            "impacto_mensal": None,
            "evidencia": "; ".join(f"“{t['term']}” → {t['conv']:.1f} conv por {_brl(t['gasto'])}"
                                    for t in sorted(novas, key=lambda x: -x["conv"])[:5]),
            "conflito": None,
            "itens": [{"termo": t["term"], "conv": t["conv"], "gasto": round(t["gasto"], 2),
                       "campanha": t["campaign_name"], "grupo": t["ad_group_name"]} for t in novas],
            "passos": ["Google Ads → Grupo de anúncios indicado → Palavras-chave → +",
                       "Adicionar como [correspondência exata] para controlar o lance"],
        })

    # ── Regra 3: PAUSAR KEYWORD — gasto alto sem conversão (só as ATIVAS,
    #    em CAMPANHAS ativas; o que já foi pausado sai da fila na atualização)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select campaign_name from (
                  select campaign_name, campaign_status,
                         row_number() over (partition by campaign_id order by metric_date desc) as rn
                  from google_ads_insights_daily where tenant_id=%s
                ) x where rn = 1 and campaign_status = 'ENABLED'
                """, (tid,))
            campanhas_ativas = {r["campaign_name"] for r in cur.fetchall()}
    # keyword cujo TEXTO já foi negativado no mesmo escopo não dispara mais —
    # pausar vira ruído; marca também p/ a árvore mostrar "já negativada"
    neg_camp_exata = {(n["campanha"], n["kw"]) for n in negativas_escopo if n["nivel"] == "campanha"}
    neg_grupo_exata = {(n["campanha"], n["grupo"], n["kw"]) for n in negativas_escopo if n["nivel"] == "grupo"}
    neg_lista_exata = {n["kw"] for n in negativas_escopo if n["nivel"] == "lista"}
    for k in keywords:
        _kt = (k["keyword"] or "").lower().strip()
        _c = (k.get("campaign_name") or "").strip()
        _g = (k.get("ad_group_name") or "").strip()
        k["negativada"] = (_kt in neg_lista_exata or (_c, _kt) in neg_camp_exata
                           or (_c, _g, _kt) in neg_grupo_exata)

    def kw_ja_negativada(k: dict) -> bool:
        if k.get("negativada"):
            return True
        kt = (k["keyword"] or "").lower().strip()
        camp = (k.get("campaign_name") or "").strip()
        grupo = (k.get("ad_group_name") or "").strip()
        for n in negativas_escopo:  # negativa contida na keyword bloqueia as buscas dela
            if not n["kw"] or n["kw"] not in kt:
                continue
            if n["nivel"] == "lista":  # lista compartilhada vale para a conta toda
                return True
            if n["nivel"] == "campanha" and n["campanha"] == camp:
                return True
            if n["nivel"] == "grupo" and n["campanha"] == camp and n["grupo"] == grupo:
                return True
        return False

    kw_ruins = [k for k in keywords if k["conv"] == 0 and k["gasto"] >= _KW_PAUSA_GASTO_MIN
                and (k.get("kw_status") or "ENABLED") == "ENABLED"
                and k.get("campaign_name") in campanhas_ativas
                and not kw_ja_negativada(k)]
    for k in sorted(kw_ruins, key=lambda x: -x["gasto"]):
        # a mesma keyword pode converter em OUTRO grupo — pausar só onde não performa
        irmas_boas = [o for o in keywords
                      if o["keyword"] == k["keyword"] and o["conv"] > 0
                      and (o.get("ad_group_name") != k.get("ad_group_name")
                           or o.get("campaign_name") != k.get("campaign_name"))]
        conflito = None
        if irmas_boas:
            b = irmas_boas[0]
            conflito = (f"Esta MESMA keyword converte em {b['campaign_name']} › {b['ad_group_name']} "
                        f"({b['conv']:.1f} conv) — pause APENAS no grupo indicado abaixo, não lá.")
        _mt = _MATCH_PT.get((k.get("match_type") or "").upper(), (k.get("match_type") or "?").lower())
        acoes.append({
            "tipo": "pausar_keyword", "canal": "google",
            "titulo": f"Pausar “{k['keyword']}” [{_mt}] no grupo {k['ad_group_name']}",
            "impacto_mensal": round(k["gasto"] * 30 / days, 2),
            "evidencia": f"{_brl(k['gasto'])} em {days}d, {k['cliques']} cliques, 0 conversões — {k['campaign_name']} › {k['ad_group_name']}",
            "conflito": conflito,
            "itens": [],
            "passos": [f"Google Ads → {k['campaign_name']} → {k['ad_group_name']} → Palavras-chave",
                       f"Pausar a keyword “{k['keyword']}” na versão de correspondência {_mt.upper()} "
                       f"(se houver mais de uma versão, as outras continuam)"],
        })

    # ── Regras 4-6: CRIATIVOS Meta (custo por lead ENGAJADO, fadiga, hook)
    custos_eng = [c["gasto"] / c["leads_engajados"] for c in criativos if c["leads_engajados"] > 0]
    mediana_eng = round(median(custos_eng), 2) if custos_eng else None
    for c in criativos:
        c["custo_conversa"] = round(c["gasto"] / c["conversas"], 2) if c["conversas"] else None
        c["custo_lead_engajado"] = round(c["gasto"] / c["leads_engajados"], 2) if c["leads_engajados"] else None
        c["hook_rate"] = round(c["thruplays"] / c["plays"], 3) if c["plays"] else None
        veredito, motivos = "observar", []
        if (c["gasto"] >= _CRIATIVO_GASTO_MIN and c["leads_engajados"] == 0 and c["conversas"] <= 1
                and (c.get("status") or "ACTIVE") == "ACTIVE"):
            veredito = "pausar"
            motivos.append(f"{_brl(c['gasto'])} gastos sem nenhum lead engajado")
            acoes.append({
                "tipo": "pausar_criativo", "canal": "meta",
                "titulo": f"Pausar criativo “{(c['ad_name'] or c['ad_id'])[:60]}”",
                "impacto_mensal": round(c["gasto"] * 30 / days, 2),
                "evidencia": f"{_brl(c['gasto'])} em {days}d → {c['conversas']} conversas, 0 leads engajados — {c['campaign_name']}",
                "conflito": None, "itens": [],
                "passos": [f"Gerenciador de Anúncios → {c['campaign_name']} → {c['adset_name']}",
                           "Desativar o anúncio e subir variação nova do vencedor"],
            })
        elif mediana_eng and c["custo_lead_engajado"] and c["custo_lead_engajado"] <= 0.7 * mediana_eng:
            veredito = "escalar"
            motivos.append(f"lead engajado a {_brl(c['custo_lead_engajado'])} — {round((1 - c['custo_lead_engajado']/mediana_eng)*100)}% abaixo da mediana ({_brl(mediana_eng)})")
        elif mediana_eng and c["custo_lead_engajado"] and c["custo_lead_engajado"] >= 2 * mediana_eng:
            veredito = "revisar"
            motivos.append(f"lead engajado caro: {_brl(c['custo_lead_engajado'])} vs mediana {_brl(mediana_eng)}")
        if c["freq"] and c["freq"] >= 3.5:
            motivos.append(f"frequência {round(c['freq'], 1)} — público saturando")
            if veredito == "escalar":
                acoes.append({
                    "tipo": "novo_criativo", "canal": "meta",
                    "titulo": f"Duplicar vencedor “{(c['ad_name'] or '')[:50]}” com criativo novo",
                    "impacto_mensal": None,
                    "evidencia": f"vence em custo/lead engajado ({_brl(c['custo_lead_engajado'])}) mas frequência {round(c['freq'],1)} — o anúncio cansa antes do público acabar",
                    "conflito": None, "itens": [],
                    "passos": ["Duplicar o anúncio no mesmo conjunto trocando APENAS o vídeo/imagem",
                               "Manter copy e segmentação (isola a variável criativo)"],
                })
        if c["hook_rate"] is not None and c["plays"] >= 500 and c["hook_rate"] < 0.15:
            motivos.append(f"hook fraco: só {round(c['hook_rate']*100)}% assistem além de 15s — refazer os 3 primeiros segundos")
        c["veredito"], c["motivos"] = veredito, motivos

    ordem_tipo = {"negativar": 0, "pausar_keyword": 1, "pausar_criativo": 2,
                  "keyword_nova": 3, "novo_criativo": 4}
    acoes.sort(key=lambda a: (-(a["impacto_mensal"] or 0), ordem_tipo.get(a["tipo"], 9)))
    desperdicio = round(sum(a["impacto_mensal"] or 0 for a in acoes
                            if a["tipo"] in ("negativar", "negativar_ia", "pausar_keyword", "pausar_criativo")), 2)

    # listas na granularidade grupo de anúncios (colar 1x por grupo no Google Ads)
    termos_neg = sorted([t for t in termos_grao if t["conv"] == 0 and t["gasto"] >= _NEG_GASTO_MIN],
                        key=lambda x: (x["campaign_name"] or "", x["ad_group_name"] or "", -x["gasto"]))
    termos_inc = sorted([t for t in termos_grao if t["conv"] > 0
                         and (t["term"] or "").lower().strip() not in kw_ativas],
                        key=lambda x: (x["campaign_name"] or "", x["ad_group_name"] or "", -x["conv"]))
    return {
        "janela_dias": days,
        "resumo": {
            "acoes_total": len(acoes),
            "desperdicio_mensal_estimado": desperdicio,
            "mediana_custo_lead_engajado": mediana_eng,
            "leads_ctwa": sum(c["leads_ctwa"] for c in criativos),
            "leads_engajados": sum(c["leads_engajados"] for c in criativos),
        },
        "acoes": acoes,
        "criativos": criativos,
        "termos_negativar": termos_neg[:80],
        "termos_incluir": termos_inc,
        "termos_negativar_ia": sentinela_itens,
        "negativas_frase": negativas_frase,
        "sentinela": sentinela_info,
        "keywords": sorted(keywords, key=lambda x: -x["gasto"]),
        "google_anuncios": sorted(google_anuncios, key=lambda x: -x["gasto"]),
        "serie_diaria": serie_diaria,
        "gasto_total": round(sum(s["gasto"] for s in serie_diaria), 2),
        "conversas_total": sum(s["conversas"] for s in serie_diaria),
        "leads_recentes": leads_recentes,
        "fluxo_leads": fluxo_leads,
        "dados_atualizados_em": _dados_atualizados_em(),
    }


def _dados_atualizados_em() -> str | None:
    """Coleta mais recente entre as tabelas do painel (p/ carimbo + auto-refresh)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select max(t) as m from (
                  select max(collected_at) as t from meta_ads_ad_insights_daily
                  union all select max(collected_at) from google_ads_search_terms_daily
                  union all select max(collected_at) from whatsapp_ctwa_leads
                ) x
                """)
            row = cur.fetchone()
    return row["m"].isoformat() if row and row["m"] else None


@router.post("/atualizar")
async def ads_atualizar() -> dict:
    """Dispara as coletas AGORA (Meta, Google, CTWA) via helper no host e retorna quando concluir."""
    import httpx as _httpx

    from ..config import settings
    token = settings.codex_gateway_token or ""
    try:
        async with _httpx.AsyncClient(timeout=600) as cli:
            r = await cli.post("http://172.19.0.1:8045/refresh",
                               headers={"Authorization": f"Bearer {token}"})
            r.raise_for_status()
            dados = r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"refresh falhou: {str(e)[:160]}")

    # sempre que os dados atualizam, a Sentinela reavalia os termos novos (2º plano)
    import asyncio as _asyncio

    async def _sentinela_bg() -> None:
        try:
            await ads_sentinela(tenant_slug="demo")
        except Exception:
            pass
    _task = _asyncio.get_running_loop().create_task(_sentinela_bg())
    _SENTINELA_TASKS.add(_task)
    _task.add_done_callback(_SENTINELA_TASKS.discard)

    return {"ok": True, "segundos": dados.get("segundos"),
            "resultados": dados.get("resultados"),
            "dados_atualizados_em": _dados_atualizados_em()}


# ── Sentinela de termos: negativação semântica automática (IA) ──────────────
# Classifica TODA pesquisa nova (mesmo com gasto baixo) em categorias de
# desperdício — outro médico, concorrente, grátis/SUS, outra cidade, emprego/
# curso, fora de escopo — e alimenta a fila de negativação. Memória por termo:
# cada termo é avaliado UMA vez; o veredito fica salvo e some da fila quando
# a negativa aparece no snapshot da conta.

_DDL_SENTINELA = """
create table if not exists ads_negativas_semanticas (
  id bigserial primary key,
  tenant_id uuid not null,
  termo text not null,
  categoria text not null,
  motivo text not null default '',
  campanha text,
  grupo text,
  gasto double precision default 0,
  cliques int default 0,
  nivel text not null default 'exata',
  janela_dias int default 60,
  created_at timestamptz not null default now(),
  unique (tenant_id, termo, nivel)
);
"""

_DDL_SENTINELA_RUNS = """
create table if not exists ads_sentinela_runs (
  id bigserial primary key,
  tenant_id uuid not null,
  janela_dias int,
  termos_avaliados int,
  suspeitos_novos int,
  executado_em timestamptz not null default now()
);
"""

_SENTINELA_TASKS: set = set()  # segura as tasks de 2º plano (evita GC no meio)

_SENTINELA_CATEGORIAS = {"outro_medico", "concorrente", "gratuito_sus_plano",
                         "outra_cidade", "emprego_curso", "fora_de_escopo", "ok"}
_SENTINELA_ROTULO = {
    "outro_medico": "outros médicos", "concorrente": "concorrentes",
    "gratuito_sus_plano": "grátis/SUS/plano", "outra_cidade": "outra cidade",
    "emprego_curso": "emprego/curso", "fora_de_escopo": "fora de escopo",
}

_SENTINELA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "avaliacoes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "termo": {"type": "string"},
                    "categoria": {"type": "string"},
                    "motivo": {"type": "string"},
                },
                "required": ["termo", "categoria", "motivo"],
            },
        },
        "negativas_de_frase": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "frase": {"type": "string"},
                    "motivo": {"type": "string"},
                },
                "required": ["frase", "motivo"],
            },
        },
    },
    "required": ["avaliacoes", "negativas_de_frase"],
}


@router.post("/sentinela")
async def ads_sentinela(tenant_slug: str = "demo", days: int = 60) -> dict:
    """Classifica com IA os termos de busca ainda não avaliados e alimenta a fila de negativação."""
    days = max(14, min(days, 120))
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(_DDL_SENTINELA)
            cur.execute(_DDL_SENTINELA_RUNS)
            cur.execute(
                """
                select term, sum(coalesce(spend,0))::float as gasto, sum(clicks)::int as cliques,
                       sum(coalesce(conversions,0))::float as conv,
                       (array_agg(campaign_name order by coalesce(spend,0) desc))[1] as campanha,
                       (array_agg(ad_group_name order by coalesce(spend,0) desc))[1] as grupo
                from google_ads_search_terms_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                group by term order by sum(coalesce(spend,0)) desc limit 600
                """, (tid, days))
            candidatos = [dict(r) for r in cur.fetchall()]
            cur.execute(
                "select distinct lower(trim(term)) as t from google_ads_search_terms_daily "
                "where tenant_id=%s and conversions > 0 and metric_date >= current_date - 90", (tid,))
            convertidos90 = {r["t"] for r in cur.fetchall()}
            negativas: list[str] = []
            kws_atuais: set[str] = set()
            cur.execute("select to_regclass('google_ads_negativos') is not null as ok")
            if cur.fetchone()["ok"]:
                cur.execute("select keyword from google_ads_negativos where tenant_id=%s", (tid,))
                negativas = [(r["keyword"] or "").lower().strip() for r in cur.fetchall()]
            cur.execute("select to_regclass('google_ads_keywords_atuais') is not null as ok")
            if cur.fetchone()["ok"]:
                cur.execute("select keyword from google_ads_keywords_atuais where tenant_id=%s", (tid,))
                kws_atuais = {(r["keyword"] or "").lower().strip() for r in cur.fetchall()}
            cur.execute("select termo from ads_negativas_semanticas where tenant_id=%s", (tid,))
            ja_avaliados = {(r["termo"] or "").lower().strip() for r in cur.fetchall()}

    def _neg(t: str) -> bool:
        t = (t or "").lower().strip()
        return any(n == t or (n and n in t) for n in negativas)

    novos = [c for c in candidatos
             if (c["term"] or "").strip()
             and (c["conv"] or 0) == 0
             and (c["term"] or "").lower().strip() not in convertidos90
             and (c["term"] or "").lower().strip() not in ja_avaliados
             and (c["term"] or "").lower().strip() not in kws_atuais
             and not _neg(c["term"])]

    # refresca gasto/cliques dos termos JÁ avaliados (o desperdício real cresce
    # com o tempo; sem isso o impacto do card fica congelado na 1ª avaliação)
    with get_conn() as conn:
        with conn.transaction(), conn.cursor() as cur:
            for c in candidatos:
                t = (c["term"] or "").lower().strip()
                if t in ja_avaliados:
                    cur.execute(
                        "update ads_negativas_semanticas set gasto=%s, cliques=%s, janela_dias=%s "
                        "where tenant_id=%s and lower(termo)=%s and nivel='exata'",
                        (c["gasto"], c["cliques"], days, tid, t))

    if not novos:
        with get_conn() as conn:
            with conn.transaction(), conn.cursor() as cur:
                cur.execute(
                    "insert into ads_sentinela_runs (tenant_id, janela_dias, termos_avaliados, suspeitos_novos) "
                    "values (%s, %s, 0, 0)", (tid, days))
        return {"avaliados": 0, "suspeitos_novos": 0, "frases_novas": 0}

    codex = CodexClient()
    if not codex.available:
        raise HTTPException(status_code=503, detail="codex-gateway não configurado")

    # trava: 1 varredura por vez (corrida front × /atualizar × cron duplicaria o custo de LLM)
    with get_conn() as conn:
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(
                "select id from ads_sentinela_runs where tenant_id=%s and termos_avaliados is null "
                "and executado_em > now() - interval '10 minutes' for update", (tid,))
            if cur.fetchone():
                return {"em_andamento": True, "avaliados": 0, "suspeitos_novos": 0, "frases_novas": 0}
            cur.execute(
                "insert into ads_sentinela_runs (tenant_id, janela_dias) values (%s, %s) returning id",
                (tid, days))
            run_id = cur.fetchone()["id"]

    # se o codex falhar no meio, a run fica "em andamento" e expira sozinha em 10 min
    avaliados = suspeitos = frases_novas = 0
    for lote in [novos[i:i + 150] for i in range(0, len(novos), 150)]:
        linhas = "\n".join(
            f'- "{c["term"]}" (R${c["gasto"]:.2f}, {c["cliques"]} cliques) [{c["campanha"]} › {c["grupo"]}]'
            for c in lote)
        prompt = f"""CONTA GOOGLE ADS da clínica Instituto Vital Slim — Dra. Daniely Freitas (nutróloga; emagrecimento saudável, saúde hormonal, longevidade). Clínica PARTICULAR, presencial em Lauro de Freitas-BA, atende Salvador e região metropolitana. Não é SUS, não é gratuita, não vende medicamento, não oferece emprego nem curso.

TERMOS DE PESQUISA que acionaram anúncios (nenhum converteu até agora):
{linhas}

TAREFA: classifique CADA termo em UMA categoria. O objetivo é achar pesquisas que ROUBAM verba (a pessoa procura outra coisa e clica no anúncio):
- outro_medico: contém nome próprio de OUTRO profissional de saúde (médico, nutrólogo, nutricionista, endocrinologista). NUNCA use para "daniely freitas" ou variações.
- concorrente: clínica, franquia, programa ou marca concorrente com nome próprio.
- gratuito_sus_plano: intenção de grátis, SUS, "pelo plano", convênio, "popular", "de graça".
- outra_cidade: cidade/estado claramente FORA de Salvador, Lauro de Freitas e região metropolitana.
- emprego_curso: vaga, emprego, salário, currículo, curso, faculdade, pós, residência médica, "como se tornar".
- fora_de_escopo: intenção que a clínica não atende — público infantil/pediátrico, veterinário, COMPRAR medicamento/produto (ex.: "ozempic preço"), receita/dieta caseira sem intenção de consulta, cirurgia bariátrica.
- ok: termo relevante (pessoa procurando médico/tratamento de emagrecimento ou hormonal na região) — NÃO negativar.

REGRAS:
1. NA DÚVIDA → "ok". Só use categoria de bloqueio com ALTA confiança: negativar termo bom custa caro.
2. "médico para emagrecer", "nutrólogo perto de mim", "tratamento hormonal" → ok.
3. Quem busca médico para ACOMPANHAR medicação (ex.: "médico que prescreve mounjaro") é lead válido → ok; quem busca COMPRAR/preço do remédio → fora_de_escopo.
4. Responda TODOS os termos, copiando o termo EXATAMENTE como está acima, com motivo de 1 frase curta.
5. negativas_de_frase: até 8 palavras genéricas presentes nos termos acima que valem negativar em FRASE na conta toda (ex.: "gratuito", "vaga", "curso") — só as claramente irrelevantes; se nenhuma, lista vazia."""
        out = await codex.generate(
            prompt,
            system="Você é um gestor de tráfego sênior de Google Ads para clínicas médicas. Responda APENAS o JSON pedido.",
            output_schema=_SENTINELA_SCHEMA, timeout=300)
        try:
            res = json.loads(out.get("content") or "{}")
        except json.JSONDecodeError:
            continue
        por_termo = {(c["term"] or "").lower().strip(): c for c in lote}
        with get_conn() as conn:
            with conn.transaction(), conn.cursor() as cur:
                for av in res.get("avaliacoes") or []:
                    termo = (av.get("termo") or "").strip()
                    base = por_termo.get(termo.lower())
                    if not termo or base is None:
                        continue
                    cat = (av.get("categoria") or "ok").strip()
                    if cat not in _SENTINELA_CATEGORIAS:
                        cat = "ok"
                    avaliados += 1
                    if cat != "ok":
                        suspeitos += 1
                    cur.execute(
                        """
                        insert into ads_negativas_semanticas
                          (tenant_id, termo, categoria, motivo, campanha, grupo, gasto, cliques, nivel, janela_dias)
                        values (%s,%s,%s,%s,%s,%s,%s,%s,'exata',%s)
                        on conflict (tenant_id, termo, nivel) do update
                          set categoria=excluded.categoria, motivo=excluded.motivo,
                              gasto=excluded.gasto, cliques=excluded.cliques,
                              janela_dias=excluded.janela_dias
                        """,
                        (tid, base["term"], cat, (av.get("motivo") or "")[:300],
                         base["campanha"], base["grupo"], base["gasto"], base["cliques"], days))
                for fr in (res.get("negativas_de_frase") or [])[:10]:
                    frase = (fr.get("frase") or "").lower().strip()
                    if not frase or len(frase) < 3 or _neg(frase):
                        continue
                    frases_novas += 1
                    cur.execute(
                        """
                        insert into ads_negativas_semanticas
                          (tenant_id, termo, categoria, motivo, campanha, grupo, gasto, cliques, nivel, janela_dias)
                        values (%s,%s,'frase_conta',%s,null,null,0,0,'frase',%s)
                        on conflict (tenant_id, termo, nivel) do update
                          set categoria='frase_conta', motivo=excluded.motivo
                          where ads_negativas_semanticas.categoria <> 'ok'
                        """,
                        (tid, frase, (fr.get("motivo") or "")[:300], days))

    with get_conn() as conn:
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(
                "update ads_sentinela_runs set termos_avaliados=%s, suspeitos_novos=%s, executado_em=now() "
                "where id=%s", (avaliados, suspeitos, run_id))
    return {"avaliados": avaliados, "suspeitos_novos": suspeitos, "frases_novas": frases_novas}


@router.post("/sentinela_descartar")
def ads_sentinela_descartar(termo: str, tenant_slug: str = "demo", nivel: str = "exata") -> dict:
    """Saída manual da fila p/ falso positivo da IA: marca o termo como 'ok'."""
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(
                "update ads_negativas_semanticas set categoria='ok', "
                "motivo='descartado manualmente no painel' "
                "where tenant_id=%s and lower(termo)=lower(%s) and nivel=%s",
                (tid, termo, nivel))
            n = cur.rowcount
    return {"ok": True, "atualizados": n}


# ── Roteiros para regravar (GPT-5.5 via codex-gateway) ──────────────────────

_DDL_ROTEIROS = """
create table if not exists ads_roteiros_gerados (
  id bigserial primary key,
  tenant_id uuid not null,
  ad_id text not null,
  diagnostico text,
  roteiros jsonb not null,
  padroes jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists idx_roteiros_ad on ads_roteiros_gerados (tenant_id, ad_id, created_at desc);
"""


@router.get("/roteiros_salvos")
def ads_roteiros_salvos(ad_id: str, tenant_slug: str = "demo") -> dict:
    """Última geração de roteiros salva para o anúncio (persistem entre sessões)."""
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(_DDL_ROTEIROS)
            cur.execute(
                """
                select diagnostico, roteiros, padroes, created_at
                from ads_roteiros_gerados
                where tenant_id=%s and ad_id=%s
                order by created_at desc limit 1
                """, (tid, ad_id))
            row = cur.fetchone()
    if not row:
        return {"ad_id": ad_id, "roteiros": [], "padroes": []}
    return {"ad_id": ad_id, "diagnostico": row["diagnostico"],
            "roteiros": row["roteiros"], "padroes": row["padroes"],
            "gerado_em": row["created_at"].isoformat()}


# ── Análise estrutural dos termos de busca (Google) ─────────────────────────

_DDL_ANALISE = """
create table if not exists ads_analise_busca (
  id bigserial primary key,
  tenant_id uuid not null,
  janela_dias int not null,
  analise jsonb not null,
  created_at timestamptz not null default now()
);
"""

_ANALISE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "resumo_executivo": {"type": "string"},
        "novos_grupos": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nome": {"type": "string"},
                    "campanha_destino": {"type": "string"},
                    "por_que": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}},
                    "termos_origem": {"type": "array", "items": {"type": "string"}},
                    "titulos": {"type": "array", "items": {"type": "string"}},
                    "descricoes": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["nome", "campanha_destino", "por_que", "keywords",
                             "termos_origem", "titulos", "descricoes"],
            },
        },
        "keywords_por_grupo": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "campanha": {"type": "string"},
                    "grupo": {"type": "string"},
                    "adicionar": {"type": "array", "items": {"type": "string"}},
                    "por_que": {"type": "string"},
                },
                "required": ["campanha", "grupo", "adicionar", "por_que"],
            },
        },
        "melhorias_anuncios": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "campanha": {"type": "string"},
                    "grupo": {"type": "string"},
                    "problema": {"type": "string"},
                    "titulos_novos": {"type": "array", "items": {"type": "string"}},
                    "descricoes_novas": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["campanha", "grupo", "problema", "titulos_novos", "descricoes_novas"],
            },
        },
    },
    "required": ["resumo_executivo", "novos_grupos", "keywords_por_grupo", "melhorias_anuncios"],
}


@router.get("/analise_busca_salva")
def ads_analise_salva(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(_DDL_ANALISE)
            cur.execute(
                "select analise, janela_dias, created_at from ads_analise_busca "
                "where tenant_id=%s order by created_at desc limit 1", (tid,))
            row = cur.fetchone()
    if not row:
        return {"analise": None}
    return {"analise": row["analise"], "janela_dias": row["janela_dias"],
            "gerado_em": row["created_at"].isoformat()}


@router.post("/analise_busca")
async def ads_analise_busca(tenant_slug: str = "demo", days: int = 30) -> dict:
    """Análise estratégica dos termos de busca: novos grupos, keywords e copy de RSA."""
    days = max(7, min(days, 90))
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select campaign_name, ad_group_name, term,
                       sum(spend)::float as gasto, sum(clicks)::int as cliques,
                       sum(conversions)::float as conv
                from google_ads_search_terms_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                group by campaign_name, ad_group_name, term
                having sum(clicks) > 0
                order by sum(conversions) desc, sum(spend) desc limit 90
                """, (tid, days))
            termos = [dict(r) for r in cur.fetchall()]
            cur.execute(
                """
                select campaign_name, ad_group_name, keyword, max(match_type) as match_type,
                       sum(spend)::float as gasto, sum(conversions)::float as conv
                from google_ads_keywords_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                group by campaign_name, ad_group_name, keyword
                order by sum(spend) desc limit 60
                """, (tid, days))
            kws = [dict(r) for r in cur.fetchall()]
            cur.execute(
                """
                select campaign_name, ad_group_name,
                       (array_agg(headlines order by metric_date desc))[1] as headlines,
                       (array_agg(descriptions order by metric_date desc))[1] as descriptions,
                       sum(spend)::float as gasto, sum(clicks)::int as cliques,
                       sum(impressions)::int as impressoes, sum(conversions)::float as conv
                from google_ads_ads_daily
                where tenant_id=%s and metric_date >= current_date - %s::int
                group by campaign_name, ad_group_name
                """, (tid, days))
            rsas = [dict(r) for r in cur.fetchall()]

    linhas_termos = "\n".join(
        f"- \"{t['term']}\" [{t['campaign_name']} › {t['ad_group_name']}] "
        f"R${t['gasto']:.2f}, {t['cliques']} cliques, {t['conv']:.1f} conv"
        for t in termos)
    linhas_kws = "\n".join(
        f"- {k['keyword']} ({k['match_type']}) [{k['campaign_name']} › {k['ad_group_name']}] "
        f"R${k['gasto']:.2f}, {k['conv']:.1f} conv" for k in kws)
    linhas_rsas = "\n".join(
        f"- [{a['campaign_name']} › {a['ad_group_name']}] CTR {(a['cliques']/a['impressoes']*100 if a['impressoes'] else 0):.1f}% "
        f"| títulos: {json.dumps(a['headlines'], ensure_ascii=False)[:400]} "
        f"| descrições: {json.dumps(a['descriptions'], ensure_ascii=False)[:300]}" for a in rsas)

    prompt = f"""CONTA GOOGLE ADS de clínica médica (Instituto Vital Slim — Dra. Daniely Freitas, nutrologia, emagrecimento saudável e longevidade, Salvador-BA; público: mulheres 35-55; conversão = conversa no WhatsApp).

TERMOS DE PESQUISA REAIS ({days} dias, com cliques):
{linhas_termos}

KEYWORDS ATUAIS:
{linhas_kws}

ANÚNCIOS RSA ATUAIS (por grupo):
{linhas_rsas}

TAREFA — como gestor sênior de Google Ads, proponha melhorias ESTRUTURAIS:
1. novos_grupos: temas presentes nos termos que convertem (ou com alta intenção) que merecem GRUPO DE ANÚNCIOS PRÓPRIO para ter anúncio e lance dedicados. Para cada: nome do grupo, campanha_destino (existente), por_que (com números dos termos), keywords iniciais (formato [exata] ou "frase"), termos_origem (os termos reais que motivaram), e 5-8 titulos (MÁXIMO 30 caracteres cada) + 3-4 descricoes (MÁXIMO 90 caracteres cada) para o RSA do grupo, escritos com o VOCABULÁRIO DOS TERMOS reais.
2. keywords_por_grupo: keywords que faltam em grupos EXISTENTES (não inclua as que já existem).
3. melhorias_anuncios: grupos cujos RSAs atuais estão desalinhados dos termos que os acionam (ou CTR fraco) — descreva o problema e proponha titulos_novos (≤30 chars) e descricoes_novas (≤90 chars).
REGRAS: compliance médico (sem cura/garantia/kg em prazo/medicamento); use os números como evidência; nomes de campanha/grupo EXATAMENTE como estão acima; resumo_executivo de 3-4 frases com o maior ganho esperado."""

    codex = CodexClient()
    if not codex.available:
        raise HTTPException(status_code=503, detail="codex-gateway não configurado")
    out = await codex.generate(
        prompt,
        system="Você é um gestor de tráfego sênior especialista em Google Ads para clínicas. Responda APENAS o JSON pedido.",
        output_schema=_ANALISE_SCHEMA, timeout=300)
    try:
        analise = json.loads(out.get("content") or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="resposta não-JSON — tente de novo")
    if not analise.get("resumo_executivo"):
        raise HTTPException(status_code=502, detail="análise vazia — tente de novo")

    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(_DDL_ANALISE)
            cur.execute(
                "insert into ads_analise_busca (tenant_id, janela_dias, analise) values (%s, %s, %s::jsonb)",
                (tid, days, json.dumps(analise, ensure_ascii=False)))
    return {"analise": analise, "janela_dias": days}


# ── Análise das conversas dos leads, agrupada por criativo ──────────────────

_DDL_CONVERSAS = """
create table if not exists ads_analise_conversas (
  id bigserial primary key,
  tenant_id uuid not null,
  janela_dias int not null,
  analise jsonb not null,
  created_at timestamptz not null default now()
);
"""

_CONVERSAS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "resumo_executivo": {"type": "string"},
        "por_criativo": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "anuncio": {"type": "string"},
                    "qualidade_dos_leads": {"type": "string"},
                    "duvidas_comuns": {"type": "array", "items": {"type": "string"}},
                    "objecoes": {"type": "array", "items": {"type": "string"}},
                    "recomendacao": {"type": "string"},
                },
                "required": ["anuncio", "qualidade_dos_leads", "duvidas_comuns", "objecoes", "recomendacao"],
            },
        },
        "vocabulario_dos_leads": {"type": "array", "items": {"type": "string"}},
        "ideias_para_campanhas": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "tipo": {"type": "string"},
                    "ideia": {"type": "string"},
                    "por_que": {"type": "string"},
                },
                "required": ["tipo", "ideia", "por_que"],
            },
        },
    },
    "required": ["resumo_executivo", "por_criativo", "vocabulario_dos_leads", "ideias_para_campanhas"],
}


@router.get("/analise_conversas_salva")
def ads_analise_conversas_salva(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(_DDL_CONVERSAS)
            cur.execute(
                "select analise, janela_dias, created_at from ads_analise_conversas "
                "where tenant_id=%s order by created_at desc limit 1", (tid,))
            row = cur.fetchone()
    if not row:
        return {"analise": None}
    return {"analise": row["analise"], "janela_dias": row["janela_dias"],
            "gerado_em": row["created_at"].isoformat()}


@router.post("/analise_conversas")
async def ads_analise_conversas(tenant_slug: str = "demo", days: int = 30) -> dict:
    """O que os leads FALAM, agrupado por criativo — vira melhoria de campanha."""
    days = max(7, min(days, 90))
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select l.source_id, coalesce(max(c.ad_name), max(l.ad_title), l.source_id) as anuncio,
                       max(c.thumbnail_url) as thumbnail_url,
                       (select max(campaign_name) from meta_ads_ad_insights_daily i
                        where i.ad_id = l.source_id) as campanha,
                       (select max(adset_name) from meta_ads_ad_insights_daily i
                        where i.ad_id = l.source_id) as conjunto,
                       count(*)::int as leads,
                       count(*) filter (where l.msgs_7d >= %s)::int as engajados,
                       string_agg(
                         coalesce(l.conversa_amostra, l.first_text), ' /// '
                         order by l.first_ts desc) as conversas
                from whatsapp_ctwa_leads l
                left join meta_ads_creatives c on c.ad_id = l.source_id
                where l.tenant_id=%s and l.first_ts >= current_date - %s::int
                group by l.source_id
                having count(*) >= 2
                order by count(*) desc limit 12
                """, (_ENGAJADO_MSGS, tid, days))
            grupos = [dict(r) for r in cur.fetchall()]
    if not grupos:
        raise HTTPException(status_code=404, detail="sem conversas de leads na janela")

    blocos = "\n\n".join(
        f"### ANÚNCIO: {g['anuncio']} [ref:{g['source_id']}] "
        f"(campanha: {g['campanha'] or '?'} › conjunto: {g['conjunto'] or '?'} · {g['leads']} leads, {g['engajados']} engajados)\n"
        f"CONVERSAS (mensagens dos leads, separadas por ///):\n{(g['conversas'] or '')[:2200]}"
        for g in grupos)

    prompt = f"""Conversas REAIS de WhatsApp de leads que chegaram por anúncios da clínica Instituto Vital Slim (Dra. Daniely Freitas — nutrologia, emagrecimento saudável, longevidade, Salvador-BA; público: mulheres 35-55). Agrupadas pelo ANÚNCIO que trouxe cada lead ({days} dias):

{blocos}

TAREFA — como estrategista de tráfego + CRM, analise o que essas conversas ensinam:
1. por_criativo: para CADA anúncio acima — qualidade_dos_leads (compradores? curiosos? preço-sensíveis? — cite evidência das falas), duvidas_comuns (as perguntas que se repetem), objecoes (o que trava: preço, convênio, distância, medo...), recomendacao (o que mudar NESSE anúncio/página para atrair lead melhor ou preparar a resposta).
2. vocabulario_dos_leads: 6-10 FRASES EXATAS ou expressões que os leads usam (ótimas para copy de anúncio e keywords — a linguagem deles, não a nossa).
3. ideias_para_campanhas: 3-6 ideias acionáveis (tipo: novo_anuncio | nova_campanha | ajuste_copy | ajuste_publico | faq_whatsapp), cada uma com por_que ancorado nas conversas.
REGRAS: compliance médico; respostas em pt-BR; seja específico, nada genérico."""

    codex = CodexClient()
    if not codex.available:
        raise HTTPException(status_code=503, detail="codex-gateway não configurado")
    out = await codex.generate(
        prompt,
        system="Você é estrategista sênior de aquisição para clínicas médicas. Responda APENAS o JSON pedido.",
        output_schema=_CONVERSAS_SCHEMA, timeout=300)
    try:
        analise = json.loads(out.get("content") or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="resposta não-JSON — tente de novo")
    if not analise.get("resumo_executivo"):
        raise HTTPException(status_code=502, detail="análise vazia — tente de novo")

    # reancora cada bloco no criativo REAL (id, thumbnail, campanha › conjunto) —
    # nomes duplicados em grupos diferentes deixam de ser ambíguos
    por_ref = {g["source_id"]: g for g in grupos}
    import re as _re
    for pc in analise.get("por_criativo") or []:
        m = _re.search(r"\[ref:([0-9]+)\]", pc.get("anuncio") or "")
        g = por_ref.get(m.group(1)) if m else None
        if not g:  # fallback: casa por nome
            g = next((x for x in grupos if x["anuncio"] in (pc.get("anuncio") or "")), None)
        if g:
            pc["ad_id"] = g["source_id"]
            pc["thumbnail_url"] = g["thumbnail_url"]
            pc["campanha"] = g["campanha"]
            pc["conjunto"] = g["conjunto"]
            pc["anuncio"] = g["anuncio"]  # nome limpo, sem o [ref:]

    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(_DDL_CONVERSAS)
            cur.execute(
                "insert into ads_analise_conversas (tenant_id, janela_dias, analise) values (%s, %s, %s::jsonb)",
                (tid, days, json.dumps(analise, ensure_ascii=False)))
    return {"analise": analise, "janela_dias": days}


# ── Criação de peças a partir das ideias (carrossel + estático + vídeo) ─────

_DDL_PECAS = """
create table if not exists ads_pecas_geradas (
  id bigserial primary key,
  tenant_id uuid not null,
  ideia text not null,
  pecas jsonb not null,
  created_at timestamptz not null default now()
);
"""

_PECAS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "carrossel": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "titulo_capa": {"type": "string"},
                "slides": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {"titulo": {"type": "string"}, "texto": {"type": "string"}},
                        "required": ["titulo", "texto"],
                    },
                },
                "cta_final": {"type": "string"},
                "copy_legenda": {"type": "string"},
            },
            "required": ["titulo_capa", "slides", "cta_final", "copy_legenda"],
        },
        "estatico": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "headline": {"type": "string"},
                "subtexto": {"type": "string"},
                "copy_primaria": {"type": "string"},
                "titulo_anuncio": {"type": "string"},
                "descricao_anuncio": {"type": "string"},
            },
            "required": ["headline", "subtexto", "copy_primaria", "titulo_anuncio", "descricao_anuncio"],
        },
        "video": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "ganchos": {"type": "array", "items": {"type": "string"}},
                "estrutura": {"type": "array", "items": {"type": "string"}},
                "cta": {"type": "string"},
            },
            "required": ["ganchos", "estrutura", "cta"],
        },
    },
    "required": ["carrossel", "estatico", "video"],
}


@router.get("/pecas_salvas")
def ads_pecas_salvas(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(_DDL_PECAS)
            cur.execute(
                "select ideia, pecas, created_at from ads_pecas_geradas "
                "where tenant_id=%s order by created_at desc limit 30", (tid,))
            rows = [dict(r) for r in cur.fetchall()]
    return {"pecas": [{"ideia": r["ideia"], "pecas": r["pecas"],
                       "gerado_em": r["created_at"].isoformat()} for r in rows]}


@router.post("/criar_pecas")
async def ads_criar_pecas(tenant_slug: str = "demo", ideia: str = "", por_que: str = "") -> dict:
    """Transforma uma ideia da análise em peças prontas: carrossel, estático e vídeo (3 ganchos)."""
    ideia = (ideia or "").strip()
    if not ideia:
        raise HTTPException(status_code=422, detail="ideia obrigatória")

    # contexto: vocabulário real dos leads + padrões virais afins
    vocabulario: list[str] = []
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(_DDL_CONVERSAS)
            cur.execute(
                "select analise from ads_analise_conversas where tenant_id=%s "
                "order by created_at desc limit 1", (tid,))
            row = cur.fetchone()
            if row:
                vocabulario = (row["analise"] or {}).get("vocabulario_dos_leads") or []
        padroes = _padroes_virais(conn, ideia + " " + " ".join(vocabulario[:6]), top=3)

    bloco_padroes = "\n".join(
        f"- [{p['classe_ivs']} · {p['mecanismo']}] hook validado: \"{(p['hook_base'] or '')[:160]}\""
        for p in padroes)
    prompt = f"""BRIEF (clínica Instituto Vital Slim — Dra. Daniely Freitas, nutrologia/emagrecimento saudável/longevidade, Salvador-BA; público: mulheres 35-55; conversão = conversa WhatsApp):

IDEIA APROVADA: {ideia}
POR QUÊ (evidência das conversas dos leads): {por_que or 'n/d'}

VOCABULÁRIO REAL DOS LEADS (use estas expressões, é a língua delas):
{chr(10).join('- ' + v for v in vocabulario[:10]) or '- n/d'}

PADRÕES VIRAIS VALIDADOS (inspire os hooks nestes mecanismos):
{bloco_padroes or '- n/d'}

TAREFA: produza o pacote completo desta ideia em 3 formatos, prontos para produção:
1. carrossel: titulo_capa (curiosidade, afirmação — NUNCA pergunta; sem nome de marca), 6-8 slides (titulo curto + texto de 1-3 frases, fio contínuo com micro-transformação), cta_final (palavra-comentário ou WhatsApp) e copy_legenda.
2. estatico: headline (afirmação forte ≤8 palavras), subtexto (1 frase), copy_primaria (texto do anúncio, 3-5 frases com qualificação explícita: consulta médica particular em Salvador), titulo_anuncio (≤40 chars), descricao_anuncio (≤30 chars).
3. video: ganchos = EXATAMENTE 3 aberturas de 3s DIFERENTES entre si (mecanismos distintos), estrutura = 5-7 passos de gravação (fala + cena) que funcionem com QUALQUER um dos 3 ganchos, cta final para WhatsApp.
COMPLIANCE: sem cura/garantia/kg em prazo/medicamentos; tom acolhedor; cenário lifestyle (nunca jaleco/hospital)."""

    codex = CodexClient()
    if not codex.available:
        raise HTTPException(status_code=503, detail="codex-gateway não configurado")
    out = await codex.generate(
        prompt,
        system="Você é o diretor criativo sênior de uma clínica médica premium. Responda APENAS o JSON pedido.",
        output_schema=_PECAS_SCHEMA, timeout=300)
    try:
        pecas = json.loads(out.get("content") or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="resposta não-JSON — tente de novo")
    if not pecas.get("video", {}).get("ganchos"):
        raise HTTPException(status_code=502, detail="geração incompleta — tente de novo")

    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(_DDL_PECAS)
            cur.execute(
                "insert into ads_pecas_geradas (tenant_id, ideia, pecas) values (%s, %s, %s::jsonb)",
                (tid, ideia, json.dumps(pecas, ensure_ascii=False)))
    return {"ideia": ideia, "pecas": pecas}


# modo estrito do Codex: additionalProperties:false em todo objeto, sem minItems/maxItems
_ROTEIROS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "roteiros": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "titulo": {"type": "string"},
                    "hook_3s": {"type": "string"},
                    "hooks_alternativos": {"type": "array", "items": {"type": "string"}},
                    "estrutura": {"type": "array", "items": {"type": "string"}},
                    "cta": {"type": "string"},
                    "por_que_funciona": {"type": "string"},
                },
                "required": ["titulo", "hook_3s", "hooks_alternativos", "estrutura", "cta", "por_que_funciona"],
            },
        }
    },
    "required": ["roteiros"],
}


def _padroes_virais(conn, texto_anuncio: str, top: int = 4) -> list[dict]:
    """Padrões da biblioteca de viralização (592 scripts minerados de virais reais)
    mais afins ao anúncio, por sobreposição de vocabulário com hook/tese."""
    stop = {"de", "da", "do", "que", "com", "para", "uma", "um", "as", "os", "e", "o", "a",
            "em", "no", "na", "se", "por", "mais", "sem", "seu", "sua", "você", "voce"}
    palavras = {w for w in (texto_anuncio or "").lower().split() if len(w) > 3 and w not in stop}
    with conn.cursor() as cur:
        cur.execute(
            """
            select codigo, classe_ivs, mecanismo, objetivo, hook_base, tese_central,
                   adaptacao_ivs, uso_recomendado
            from viral_scripts
            where hook_base is not null and length(hook_base) > 40
            order by created_at desc limit 250
            """)
        candidatos = [dict(r) for r in cur.fetchall()]
    def score(p: dict) -> int:
        alvo_txt = f"{p.get('hook_base') or ''} {p.get('tese_central') or ''}".lower()
        return sum(1 for w in palavras if w in alvo_txt)
    candidatos.sort(key=score, reverse=True)
    return candidatos[:top]


@router.post("/roteiros")
async def ads_roteiros(ad_id: str, tenant_slug: str = "demo", days: int = 30) -> dict:
    """3 roteiros de regravação para um anúncio, escritos a partir do diagnóstico real
    + padrões da biblioteca de viralização."""
    cockpit = ads_cockpit(tenant_slug, days)
    alvo = next((c for c in cockpit["criativos"] if c["ad_id"] == ad_id), None)
    if not alvo:
        raise HTTPException(status_code=404, detail="anúncio não encontrado na janela")
    vencedor = next((c for c in cockpit["criativos"]
                     if c["veredito"] == "escalar" and c["ad_id"] != ad_id), None)
    with get_conn() as conn:
        padroes = _padroes_virais(conn, f"{alvo.get('ad_name') or ''} {alvo.get('body') or ''}")

    diag = "; ".join(alvo["motivos"]) or "sem alerta — otimização incremental"
    contexto = f"""ANÚNCIO ATUAL (Meta, clínica Instituto Vital Slim — Dra. Daniely Freitas, nutrologia/emagrecimento/longevidade em Salvador-BA; público: mulheres 35-55):
- Nome: {alvo['ad_name']}
- Campanha: {alvo['campaign_name']}
- Copy atual: {(alvo.get('body') or 'sem texto')[:700]}
- Números na janela de {days}d: investido R${alvo['gasto']:.0f}; {alvo['conversas']} conversas; {alvo['leads_engajados']} leads engajados; custo/lead engajado {('R$%.2f' % alvo['custo_lead_engajado']) if alvo['custo_lead_engajado'] else 'n/d'}; hook rate {(str(round((alvo['hook_rate'] or 0)*100)) + '%') if alvo['hook_rate'] is not None else 'n/d'}; frequência {round(alvo['freq'] or 0, 1)}
- DIAGNÓSTICO: {diag}"""
    if vencedor and vencedor.get("body"):
        contexto += f"""

REFERÊNCIA (anúncio VENCEDOR da mesma conta — custo/lead {('R$%.2f' % vencedor['custo_lead_engajado']) if vencedor['custo_lead_engajado'] else 'n/d'}):
- Copy: {vencedor['body'][:500]}"""
    if padroes:
        contexto += "\n\nPADRÕES DE VIRALIZAÇÃO VALIDADOS (biblioteca IVS, minerados de vídeos que viralizaram — use o MECANISMO deles nos hooks, adaptado ao tema do anúncio):"
        for p in padroes:
            contexto += (f"\n- [{p['classe_ivs'] or 'padrão'} · {p['mecanismo'] or ''}] "
                         f"hook validado: \"{(p['hook_base'] or '')[:180]}\""
                         + (f" | adaptação IVS: {(p['adaptacao_ivs'] or '')[:150]}" if p.get('adaptacao_ivs') else ""))

    if alvo["veredito"] == "escalar":
        tarefa = """TAREFA: este anúncio é um CAMPEÃO (melhor custo por lead engajado da conta). Escreva 3 VARIAÇÕES para ESCALAR sem fadiga de público:
- Mantenha a PROMESSA e a mecânica que funcionam (é o que os leads respondem) — o que varia é o ângulo de entrada e o hook.
- VARIAÇÃO 1 = mesma estrutura do vídeo atual com abertura nova (hook_3s + 3 hooks_alternativos).
- VARIAÇÕES 2 e 3 = ângulos diferentes da MESMA promessa (ex: outra dor de entrada, outra prova, outro contexto de cena), para rodar em paralelo e renovar o criativo antes do público cansar."""
    else:
        tarefa = """TAREFA: escreva 3 roteiros de vídeo (30-40s) para a Dra. regravar este anúncio, atacando o diagnóstico acima.
- ROTEIRO 1 (obrigatório) = "REGRAVAR O MESMO VÍDEO": reconstrua fielmente a mensagem/estrutura do anúncio ATUAL a partir do copy acima (mesmo argumento, mesma ordem) trocando APENAS a abertura — hook_3s novo + 3 hooks_alternativos também novos para a mesma abertura. Assim a Dra regrava o vídeo que já funciona só consertando o começo.
- ROTEIROS 2 e 3 = variações com TIPOS DE HOOK diferentes (pergunta que dói, quebra de crença, história/prova), podendo reestruturar a mensagem."""

    prompt = f"""{contexto}

{tarefa}
Regras para todos:
- hook_3s = a fala EXATA dos 3 primeiros segundos; hooks_alternativos = 2-3 variações da mesma abertura para a Dra escolher
- estrutura = 4-6 passos de gravação, cada um com a fala resumida + instrução de cena (ex: "close no rosto", "mostra na mão", "b-roll de prato")
- cta = fechamento para clicar e chamar no WhatsApp
- linguagem simples e direta, tom acolhedor da Dra (nunca jaleco/hospital; cenário lifestyle)
- COMPLIANCE MÉDICO: sem promessa de cura, sem garantia de resultado, sem número de kg em prazo, sem citar medicamentos
- por_que_funciona = 1 frase ligando o roteiro ao diagnóstico"""

    codex = CodexClient()
    if not codex.available:
        raise HTTPException(status_code=503, detail="codex-gateway não configurado")
    out = await codex.generate(
        prompt,
        system="Você é o melhor roteirista de anúncios de saúde do Brasil. Responda APENAS o JSON pedido.",
        output_schema=_ROTEIROS_SCHEMA, timeout=240)
    try:
        dados = json.loads(out.get("content") or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="resposta não-JSON do gerador — tente de novo")
    roteiros = dados.get("roteiros") or []
    if not roteiros:
        raise HTTPException(status_code=502, detail="geração vazia — tente de novo")
    padroes_slim = [{"codigo": p["codigo"], "classe": p["classe_ivs"],
                     "mecanismo": p["mecanismo"], "hook_base": p["hook_base"]}
                    for p in padroes]
    # persiste — os roteiros ficam no card mesmo fechando o navegador
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(_DDL_ROTEIROS)
            cur.execute(
                """
                insert into ads_roteiros_gerados (tenant_id, ad_id, diagnostico, roteiros, padroes)
                values (%s, %s, %s, %s::jsonb, %s::jsonb)
                """, (tid, ad_id, diag, json.dumps(roteiros, ensure_ascii=False),
                      json.dumps(padroes_slim, ensure_ascii=False)))
    return {"ad_id": ad_id, "diagnostico": diag, "roteiros": roteiros, "padroes": padroes_slim}
