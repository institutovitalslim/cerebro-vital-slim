"""Orquestrador de geração (motor A) — coração do Content Engine OS.
Combina conhecimento (roteiro viral análogo + dispositivos + tema/persona + voz da marca)
-> gera via Opus 4.8 (OpenRouter) com fallback Codex/OAuth -> checklist -> persiste em creatives.
Saída estruturada: headline com *ênfase dourada* + image_prompt por slide; ciente de feed vs Meta Ads.
"""
from __future__ import annotations

import glob
import itertools
import json
import os
import re
import shutil

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn
from app.routers.calendar import ensure_phase1_schema
from app.services.openrouter_client import OpenRouterClient
from app.services.codex_client import CodexClient

router = APIRouter(prefix="/generation", tags=["generation"])

RENDERS_DIR = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders"
BANNED = ["cura", "garantido", "garantia de", "100%", "milagre", "perca x", "emagrece x"]
CAPTION_FOOTER = (
    "Dra Daniely Freitas\n"
    "Médica, Farmacêutica e Professora de Medicina\n"
    "CRM-BA 27.588\n"
    "(Este conteúdo tem caráter meramente educativo e não substitui uma consulta médica.)"
)
CAPTION_FOOTER_MARKER = "CRM-BA 27.588"

# Camada de direcionamento Meta Ads — 5 conjuntos por ÂNGULO (mentoria 06-14, playbook IVS:
# cerebro/areas/marketing/sub-areas/trafego-pago/playbook-meta-ads-mentoria-06-14-ivs.md).
# Estrutura: 1 campanha / 5 conjuntos (1 ângulo cada) / 3 criativos por conjunto (ABO, público amplo).
ANGULOS_META = {
    "baseline": {
        "nome": "1 · Baseline / oferta clara",
        "diretriz": "Oferta direta: avaliação médica individual para mulheres que querem entender por que "
                    "as tentativas anteriores não sustentaram resultado. Clareza, sem rodeios."},
    "culpa": {
        "nome": "2 · Objeção: culpa / fracasso",
        "diretriz": "Reframe da culpa: o problema não é falta de força de vontade — falta um plano que "
                    "considere o corpo e a rotina dela."},
    "so_dieta": {
        "nome": "3 · Objeção: medo de ser 'só mais uma dieta'",
        "diretriz": "Não é começar outra dieta: é investigar, acompanhar e ajustar com clareza "
                    "(exames, bioimpedância, acompanhamento próximo)."},
    "preco": {
        "nome": "4 · Barreira: preço / valor percebido",
        "diretriz": "Valor antes do preço: o que uma avaliação completa evita — tentativa no escuro, "
                    "efeito sanfona e frustração repetida."},
    "metodo": {
        "nome": "5 · Método / autoridade",
        "diretriz": "Método e autoridade: exames, bioimpedância, consulta e acompanhamento próximo "
                    "para construir um caminho individual."},
}


class OrchestrateRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    objetivo: str = Field(default="identificação")   # atração|identificação|educação|conversão|desejo|retenção
    formato: str = Field(default="reels")            # estatico|carrossel|reels|stories
    rede: str = Field(default="instagram")
    destino: str = Field(default="feed")             # feed|meta_ads  (relevante p/ carrossel)
    angulo: str | None = None                        # baseline|culpa|so_dieta|preco|metodo (conjunto Meta Ads)
    hook_tipo: str | None = None                     # identificacao|mecanismo|contraste|mito|pergunta_direta
    objecao_alvo: str | None = None                  # objeção principal da variação
    quebra_objecao: str | None = None                # reframe/prova para quebrar a objeção
    visual_tipo: str | None = None                   # dra_camera|broll_rotina|prova_metodo|texto_premium
    cta_tipo: str | None = None                      # salvar|pre_avaliacao|whatsapp|agendamento
    test_cycle_id: str | None = None                 # ciclo de teste criativo
    variant_index: int | None = None                 # índice da variação no ciclo
    tema: str | None = None
    persona: str | None = None
    funil: str = Field(default="relacionamento_conversao")
    melhorias: str | None = None
    seo_social_intent: str | None = None          # intenção de busca/descoberta: ex. "por que não consigo emagrecer"
    send_save_reason: str | None = None          # por que alguém salvaria/enviaria essa peça
    trial_reel: bool = Field(default=False)       # usar como laboratório antes de escalar
    expected_intent_signal: str | None = None     # sinal esperado: DM, envio, salvar, WhatsApp, agenda
    quality_metric: str | None = None             # métrica principal de qualidade: dm_util|lead_util|envio|retencao
    source: str | None = None                     # weekly-sprint quando vem do sprint semanal
    thesis: str | None = None                     # tese estruturada do sprint
    pillar: str | None = None                     # pilar do sprint
    audience_stage: str | None = None             # consciência do público
    origin_tag: str | None = None                 # ex.: weekly:pilar:reels
    hook: str | None = None                       # hook literal selecionado no sprint


class MatrixRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    name: str = Field(default="Ciclo de teste criativo")
    objetivo: str = Field(default="conversão")
    formato: str = Field(default="reels")
    rede: str = Field(default="instagram")
    destino: str = Field(default="meta_ads")
    tema: str | None = None
    persona: str | None = None
    funil: str = Field(default="relacionamento_conversao")
    angulos: list[str] = Field(default_factory=lambda: ["culpa", "so_dieta", "metodo"])
    hooks: list[str] = Field(default_factory=lambda: ["identificacao", "mecanismo", "contraste"])
    objecoes: list[str] = Field(default_factory=lambda: ["ja_tentei_de_tudo"])
    ctas: list[str] = Field(default_factory=lambda: ["pre_avaliacao", "whatsapp_qualificado"])
    visuais: list[str] = Field(default_factory=lambda: ["dra_camera", "broll_rotina"])


def _modular_meta(req: OrchestrateRequest, output: dict | None = None) -> dict:
    """Metadados canônicos de teste criativo. Colunas = filtro rápido; JSON = auditoria/blocos."""
    output = output or {}
    blocks = output.get("modular_blocks") if isinstance(output.get("modular_blocks"), dict) else {}
    angulo_ivs = req.angulo or output.get("angulo") or blocks.get("angle") or blocks.get("angulo_ivs")
    hook_tipo = req.hook_tipo or blocks.get("hook_tipo")
    objecao_alvo = req.objecao_alvo or blocks.get("objecao_alvo") or output.get("objecao_principal")
    quebra_objecao = req.quebra_objecao or blocks.get("quebra_objecao") or blocks.get("quebra_objeção")
    visual_tipo = req.visual_tipo or blocks.get("visual_tipo")
    cta_tipo = req.cta_tipo or blocks.get("cta_tipo")
    destino = req.destino or output.get("destino") or blocks.get("destino")
    hypothesis = blocks.get("hypothesis") or blocks.get("hipotese")
    modular_blocks = {
        **blocks,
        "angulo_ivs": angulo_ivs,
        "hook_tipo": hook_tipo,
        "objecao_alvo": objecao_alvo,
        "quebra_objecao": quebra_objecao,
        "visual_tipo": visual_tipo,
        "cta_tipo": cta_tipo,
        "destino": destino,
        "hypothesis": hypothesis,
        "seo_social_intent": req.seo_social_intent or blocks.get("seo_social_intent"),
        "send_save_reason": req.send_save_reason or blocks.get("send_save_reason"),
        "trial_reel": req.trial_reel,
        "expected_intent_signal": req.expected_intent_signal or blocks.get("expected_intent_signal"),
        "quality_metric": req.quality_metric or blocks.get("quality_metric"),
    }
    return {
        "angulo_ivs": angulo_ivs,
        "hook_tipo": hook_tipo,
        "objecao_alvo": objecao_alvo,
        "quebra_objecao": quebra_objecao,
        "visual_tipo": visual_tipo,
        "cta_tipo": cta_tipo,
        "destino_criativo": destino,
        "hypothesis": hypothesis,
        "modular_blocks": modular_blocks,
        "seo_social_intent": modular_blocks.get("seo_social_intent"),
        "send_save_reason": modular_blocks.get("send_save_reason"),
        "trial_reel": modular_blocks.get("trial_reel"),
        "expected_intent_signal": modular_blocks.get("expected_intent_signal"),
        "quality_metric": modular_blocks.get("quality_metric"),
    }


def _cta_rule(formato: str, destino: str) -> str:
    if formato == "reels":
        return "CTA SOMENTE de engajamento: pedir para SALVAR ou COMPARTILHAR. Nenhum outro tipo."
    if formato == "stories":
        return "CTA de conexão/interação leve (responder, tocar, mandar no direct)."
    if formato == "carrossel":
        if destino == "meta_ads":
            return ("CTA de CONVERSÃO (anúncio Meta Ads): levar a AGENDAR / pré-avaliação. "
                    "Arco: dor -> prova/mecanismo -> oferta -> CTA de ação ('agende sua avaliação', "
                    "'quero ser avaliada'). NUNCA 'salva/compartilha' num anúncio.")
        return ("CTA de SALVAR/COMPARTILHAR (feed). Propósito do carrossel: aprofundar conhecimento "
                "+ gerar autoridade da Dra.")
    return "CTA de salvar/compartilhar."


def _output_spec(formato: str) -> str:
    if formato == "carrossel":
        return (
            'Entregue SOMENTE um JSON válido com EXATAMENTE estas chaves:\n'
            '- "title": headline da CAPA, curta e forte (1 linha).\n'
            '- "cover_sub": subtítulo curto da capa (1 frase).\n'
            '- "slides": lista de 4 a 6 objetos, cada um:\n'
            '    {"label": rótulo curto (ex.: "SINAL 1", "ERRO 2"),\n'
            '     "headline": frase curta de impacto,\n'
            '     "sub": 1 frase explicando o mecanismo,\n'
            '     "image_prompt": descrição VISUAL concreta e realista da foto do slide '
            '(ambiente, pessoa/sujeito, ação, luz, clima) — SEM texto e SEM palavras na imagem}.\n'
            '- "cta_headline": headline do slide final (reframe forte).\n'
            '- "cta_sub": subtítulo do CTA.\n'
            '- "caption": legenda do post.\n'
            '- "hashtags": lista de 8 a 12.\n'
            '- "modular_blocks": objeto com angle, hook_tipo, objecao_alvo, quebra_objecao, visual_tipo, cta_tipo e hypothesis.'
        )
    if formato in ("reels", "stories"):
        return ('Entregue SOMENTE um JSON com: "title"; "hook"; "script" (lista de cenas/parágrafos); '
                '"cta"; "caption"; "hashtags" (8-12); "modular_blocks" com angle, hook_tipo, objecao_alvo, quebra_objecao, visual_tipo, cta_tipo e hypothesis.')
    return ('Entregue SOMENTE um JSON com: "title"; "headline"; "body"; "cta"; "caption"; "hashtags" (8-12); '
            '"modular_blocks" com angle, hook_tipo, objecao_alvo, quebra_objecao, visual_tipo, cta_tipo e hypothesis.')


def _tenant_id(conn, slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug=%s", (slug,))
        r = cur.fetchone()
    if not r:
        raise HTTPException(404, f"tenant '{slug}' não encontrado")
    return r["id"]


VIRAL_COLS = ("codigo, classe_ivs, mecanismo, hook_base, tese_central, objecao_principal, adaptacao_ivs")


def _fetch_context(conn, tenant_id: str, objetivo: str, tema: str | None):
    """Escolhe o roteiro viral análogo por RELEVÂNCIA ao tema (o `objetivo` do bunker é texto livre).
    Pontua por nº de palavras-chave do tema presentes em hook/tese/adaptação; desempate aleatório."""
    kws = [w for w in re.findall(r"\w{4,}", (tema or "").lower())][:6]
    with conn.cursor() as cur:
        viral = None
        if kws:
            blob = "lower(coalesce(hook_base,'')||' '||coalesce(tese_central,'')||' '||coalesce(adaptacao_ivs,''))"
            score = " + ".join([f"(case when {blob} like %s then 1 else 0 end)" for _ in kws])
            cur.execute(
                f"select {VIRAL_COLS}, ({score}) as score from viral_scripts where tenant_id is null "
                "order by score desc, random() limit 1", [f"%{k}%" for k in kws])
            viral = cur.fetchone()
            if viral and not viral.get("score"):
                viral = None  # nenhum keyword bateu -> fallback aleatório (variedade)
        if not viral:
            cur.execute(f"select {VIRAL_COLS} from viral_scripts where tenant_id is null order by random() limit 1")
            viral = cur.fetchone()
        cur.execute("select name, logic, example from narrative_devices where tenant_id is null order by random() limit 4")
        devices = cur.fetchall()
        cur.execute("select name, voice_notes, compliance_rules from brands where tenant_id=%s limit 1", (tenant_id,))
        brand = cur.fetchone()
    return viral, devices, brand


def _brand_diretrizes(req) -> str:
    """Diretrizes de Marca & Posicionamento APROVADas (inteligencia criativa validada)."""
    try:
        with get_conn() as conn:
            tid = _tenant_id(conn, req.tenant_slug)
            with conn.cursor() as cur:
                cur.execute("select titulo, conteudo from creative_intelligence where status=%s "
                            "and (tenant_id=%s or tenant_id is null) order by validated_at desc nulls last limit 12",
                            ("aprovado", tid))
                rows = cur.fetchall()
        if not rows:
            return ""
        linhas = chr(10).join(("- " + ((r["titulo"] + ": ") if r["titulo"] else "") + r["conteudo"]) for r in rows)
        return (chr(10) + "DIRETRIZES DE MARCA & POSICIONAMENTO (aprovadas - siga como inteligencia criativa): " + chr(10) + linhas + chr(10))
    except Exception:
        return ""


def _build_prompt(req: OrchestrateRequest, viral, devices, brand):
    dev_txt = "\n".join(f"- {d['name']}: {d['logic']} (ex: {d['example']})" for d in devices)
    viral_txt = ("(nenhum)" if not viral else
                 f"código {viral['codigo']} | classe {viral['classe_ivs']} | mecanismo {viral['mecanismo']}\n"
                 f"hook-base: {viral['hook_base']}\ntese: {viral['tese_central']}\n"
                 f"objeção: {viral['objecao_principal']}\nadaptação IVS: {viral['adaptacao_ivs']}")
    voice = (brand or {}).get("voice_notes") or "Médica sênior, acolhedora e técnica (Sábio+Cuidador). PT-BR impecável, sem emoji decorativo."
    destino_txt = f" | DESTINO: {req.destino}" if req.formato == "carrossel" else ""
    mel = "" if not req.melhorias else ("MELHORIAS SOLICITADAS PELO REVISOR — aplique obrigatoriamente, mantendo o que já está bom: " + req.melhorias)
    diretrizes = _brand_diretrizes(req)
    ang = ANGULOS_META.get(req.angulo or "") if req.destino == "meta_ads" else None
    angulo_block = ("" if not ang else
                    f"\nÂNGULO DO CONJUNTO (Meta Ads — estrutura 1 campanha/5 conjuntos/3 criativos, mentoria 06-14): "
                    f"{ang['nome']}\nDiretriz deste conjunto: {ang['diretriz']}\n"
                    f"A PEÇA INTEIRA serve este ângulo — arco: dor -> prova/mecanismo -> oferta -> CTA de agendamento.\n")
    modular_block = f"""
HIPÓTESE MODULAR DE TESTE (criativo como segmentação):
- ângulo IVS: {req.angulo or 'inferir pelo tema'}
- tipo de hook: {req.hook_tipo or 'inferir e declarar'}
- objeção-alvo: {req.objecao_alvo or 'inferir a principal objeção da paciente'}
- quebra de objeção/prova: {req.quebra_objecao or 'criar reframe seguro, sem promessa médica'}
- visual: {req.visual_tipo or 'inferir visual executável no padrão premium IVS'}
- CTA: {req.cta_tipo or 'seguir regra do formato/destino'}

Inclua na saída a chave "modular_blocks" com: angle, hook_tipo, objecao_alvo,
quebra_objecao, visual_tipo, cta_tipo e hypothesis. A hypothesis deve dizer qual público/objeção
esta variação tenta qualificar.
""".strip()
    return f"""
Crie 1 peça de conteúdo para Instagram, nicho saúde da mulher 40+ (emagrecimento/hormônios).
{mel}
CONTEXTO DE MARCA (tom de voz): {voice}{diretrizes}
OBJETIVO: {req.objetivo} | FORMATO: {req.formato} | REDE: {req.rede}{destino_txt} | FUNIL: {req.funil}
TEMA: {req.tema or 'escolha um tema forte do nicho (perimenopausa, tireoide, resistência à insulina, libido, sono)'}
PERSONA: {req.persona or 'mulher 38-55 que já tentou de tudo e continua travada'}

{angulo_block}
{modular_block}

MÉTODO LIGHT COPY (Leandro Ladeira) — aplicar na criação:
- ASSOCIAÇÃO RICA: prefira analogias inusitadas que ocupam slot vazio na mente. Ex.: "hormônios na perimenopausa como orquestra fora do compasso" (rica) vs "é igual a um músculo" (pobre/batida). Quanto mais inédita a associação, mais memorável.
- TÉCNICAS DE CRIAÇÃO: "conta inusitada" (represente o conceito via dado bizarro/exagerado); "listar o feio/ruim" do nicho antes de ir ao bonito (libera o criativo do óbvio); "oposto" (defenda o contrário do esperado para gerar curiosidade).
- OBSERVAÇÃO ATIVA: transforme falas reais de pacientes em conteúdo. "Me sinto estranha no próprio corpo" é mais poderosa que qualquer copy técnica — anonimize sempre.
- LADO ENGRAÇADO/SÉRIO: use humor leve no cotidiano da mulher 40+ (calor súbito, sono, cansaço) e feche com reflexão séria/acolhedora (não irônica).
- ESTRUTURA: Gancho (loop de curiosidade — dor ou mecanismo inesperado) → Desenvolvimento (associação + prova/mecanismo) → Fechamento (reflexão + CTA que gera ação, não venda).
- IDENTIDADE DA DRA.: valores = acolhimento, ciência séria, escuta, respeito ao corpo da mulher. Inimigo em comum (ético) = desinformação e promessas de emagrecimento rápido.
- COMPLIANCE SEMPRE: "pode ajudar", "muitas mulheres relatam", "investigação individualizada" — NUNCA resultado garantido ou kg prometido.

ROTEIRO VIRAL ANÁLOGO (use como referência de ângulo/hook, adapte — não copie literal):
{viral_txt}

DISPOSITIVOS NARRATIVOS DISPONÍVEIS (escolha 1-2 e aplique):
{dev_txt}

REGRAS OBRIGATÓRIAS:
- {_cta_rule(req.formato, req.destino)}
- REALCE: em TODA headline/hook, marque UMA palavra ou frase-chave entre *asteriscos* (vira realce dourado no design). Só 1 realce por frase; nunca a frase inteira.
- Compliance médico (CFM): SEM promessa de cura/resultado garantido/número de kg; pode explicar mecanismo.
- Toda legenda/caption de conteúdo deve terminar obrigatoriamente com esta assinatura/disclaimer, exatamente neste bloco:\n{CAPTION_FOOTER}
- Instagram 2026: escreva para recomendação + busca. Texto na tela, legenda e semântica precisam carregar intenção real de busca quando houver.
- Retenção: os 2 primeiros segundos devem começar por dor, mecanismo ou objeção — nunca vinheta.
- Métrica de qualidade preferida: {req.quality_metric or 'DM útil / lead útil / envio / retenção, não curtida'}.
- Intenção de busca/SEO social: {req.seo_social_intent or 'inferir pela dor central da paciente'}.
- Motivo para salvar/enviar: {req.send_save_reason or 'a peça deve ser útil o suficiente para salvar ou mandar para uma amiga'}.
- Sinal de intenção esperado: {req.expected_intent_signal or 'resposta no direct, envio, salvamento ou clique para WhatsApp'}.
- Trial Reel: {'sim — tratar como laboratório controlado' if req.trial_reel else 'não obrigatório'}.
- Gancho forte; 1 ideia central; linguagem da paciente; PT-BR impecável.

{_output_spec(req.formato)}
""".strip()


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {"raw": text}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {"raw": text}


def _with_caption_footer(text: object) -> str:
    base = "" if text is None else str(text).strip()
    if CAPTION_FOOTER_MARKER in base:
        return base
    return (base + "\n\n" + CAPTION_FOOTER).strip() if base else CAPTION_FOOTER


def _apply_caption_footer(output: dict) -> dict:
    """Garante assinatura/disclaimer em toda legenda gerada ou persistida."""
    if not isinstance(output, dict):
        return output
    output["caption"] = _with_caption_footer(output.get("caption"))
    # Algumas rotas de engenharia reversa retornam scripts com a chave PT-BR "legenda".
    scripts = output.get("scripts")
    if isinstance(scripts, list):
        for item in scripts:
            if isinstance(item, dict) and "legenda" in item:
                item["legenda"] = _with_caption_footer(item.get("legenda"))
    return output


def _brief_payload(req: OrchestrateRequest) -> dict:
    return {
        "formato": req.formato,
        "objetivo": req.objetivo,
        "rede": req.rede,
        "destino": req.destino,
        "angulo": req.angulo,
        "hook_tipo": req.hook_tipo,
        "objecao_alvo": req.objecao_alvo,
        "quebra_objecao": req.quebra_objecao,
        "visual_tipo": req.visual_tipo,
        "cta_tipo": req.cta_tipo,
        "tema": req.tema,
        "persona": req.persona,
        "funil": req.funil,
        "source": req.source,
        "thesis": req.thesis,
        "pillar": req.pillar,
        "audience_stage": req.audience_stage,
        "origin_tag": req.origin_tag,
        "hook": req.hook,
    }


def _brief_value(brief: dict, key: str) -> str | None:
    value = brief.get(key)
    if value:
        return str(value)
    tema = brief.get("tema") or ""
    patterns = {
        "hook": r"(?:^|\n)Hook:\s*(.+)",
        "origin_tag": r"(?:^|\n)Origem:\s*(.+)",
    }
    if key in patterns:
        m = re.search(patterns[key], tema)
        return m.group(1).strip() if m else None
    if key == "thesis" and tema:
        return str(tema).split("\n", 1)[0].strip()
    return None


def _ensure_calendar_for_creative(conn, cid: str) -> dict | None:
    """Cria/atualiza entrada editorial para peça aprovada, sem duplicar."""
    ensure_phase1_schema(conn)
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.id::text as id, c.tenant_id, c.title, c.format, c.network, c.brief,
                   c.asset_url, c.status
            from creatives c where c.id=%s
            """,
            (cid,),
        )
        c = cur.fetchone()
        if not c:
            return None
        brief = c.get("brief") or {}
        if isinstance(brief, str):
            try:
                brief = json.loads(brief)
            except Exception:
                brief = {}
        title = (c.get("title") or _brief_value(brief, "thesis") or f"Criativo {c.get('format')}").replace("*", "")
        origin_tag = _brief_value(brief, "origin_tag")
        sprint_thesis = _brief_value(brief, "thesis")
        sprint_hook = _brief_value(brief, "hook")
        notes_parts = [
            "Aprovado no Banco de Criativos e enviado ao Calendário Editorial.",
            f"Origem: {origin_tag}" if origin_tag else None,
            f"Tese: {sprint_thesis}" if sprint_thesis else None,
            f"Hook: {sprint_hook}" if sprint_hook else None,
        ]
        notes = "\n".join([p for p in notes_parts if p])
        cur.execute(
            """
            insert into calendar_entries (
                tenant_id, title, format, channel, objective, status, notes, creative_id,
                origin_tag, sprint_thesis, sprint_hook
            ) values (%s,%s,%s,%s,%s,'aprovado_para_publicar',%s,%s,%s,%s,%s)
            on conflict (creative_id) where creative_id is not null do update set
                title=excluded.title,
                format=excluded.format,
                channel=excluded.channel,
                objective=excluded.objective,
                status=case when calendar_entries.status in ('published','publicado','medido') then calendar_entries.status else 'aprovado_para_publicar' end,
                notes=excluded.notes,
                origin_tag=excluded.origin_tag,
                sprint_thesis=excluded.sprint_thesis,
                sprint_hook=excluded.sprint_hook
            returning id::text as id, status, title
            """,
            (c["tenant_id"], title, c.get("format"), c.get("network") or "instagram", brief.get("objetivo"),
             notes, cid, origin_tag, sprint_thesis, sprint_hook),
        )
        return cur.fetchone()


def _quality(output: dict, formato: str) -> tuple[float, dict]:
    blob = json.dumps(output, ensure_ascii=False).lower()
    slides = output.get("slides") or []
    if slides and isinstance(slides[0], dict):
        corpo = " ".join(((s.get("headline") or "") + " " + (s.get("sub") or "")) for s in slides)
    elif slides:
        corpo = " ".join(str(x) for x in slides)
    else:
        c = output.get("script") or output.get("body") or ""
        corpo = " ".join(str(x) for x in c) if isinstance(c, list) else str(c)
    b = {
        "tem_titulo": 1 if output.get("title") else 0,
        "tem_gancho": 1 if (output.get("hook") or output.get("headline") or output.get("title")) else 0,
        "tem_cta": 1 if (output.get("cta") or output.get("cta_headline")
                         or any(k in blob for k in ("salv", "compartilh", "agend"))) else 0,
        "tem_legenda": 1 if output.get("caption") else 0,
        "tem_hashtags": 1 if output.get("hashtags") else 0,
        "compliance_ok": 0 if any(x in blob for x in BANNED) else 1,
        "profundidade": 1 if len(str(corpo)) > 220 else 0,
        "tem_enfase": 1 if "*" in (corpo + json.dumps(output.get("title", ""))) else 0,
    }
    score = round(100 * sum(b.values()) / len(b), 1)
    return score, b


SYSTEM_PROMPT = ("Você é o motor de conteúdo do Instituto Vital Slim: estrategista de conteúdo médico premium. "
                 "Combina bibliotecas (dispositivos, roteiros virais) + tom da marca. Saída sempre JSON puro, "
                 "elegante, orientada a engajamento e compliance CFM.")


async def _motor(prompt: str, system: str):
    try:
        result = await OpenRouterClient().generate(prompt, system=system)
        if result.get("mode") in ("mock", "degraded_mock"):
            raise RuntimeError(f"openrouter falhou: {result.get('errors') or 'sem api_key'}")
    except Exception as e:
        try:
            result = await CodexClient().generate(prompt, system=system)
            result["fallback_reason"] = f"openrouter indisponível: {type(e).__name__}: {e}"
        except Exception as e2:
            raise HTTPException(503, f"motor indisponível (openrouter: {e}; codex: {e2})")
    return result


@router.post("/orchestrate")
async def orchestrate(req: OrchestrateRequest) -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, req.tenant_slug)
        viral, devices, brand = _fetch_context(conn, tenant_id, req.objetivo, req.tema)
    prompt = _build_prompt(req, viral, devices, brand)
    result = await _motor(prompt, SYSTEM_PROMPT)
    output = _apply_caption_footer(_extract_json(result.get("content", "")))
    output["destino"] = req.destino   # feed|meta_ads -> consumido pelo render worker
    if req.destino == "meta_ads" and req.angulo:
        output["angulo"] = req.angulo
        output["angulo_nome"] = (ANGULOS_META.get(req.angulo) or {}).get("nome")
    meta = _modular_meta(req, output)
    score, breakdown = _quality(output, req.formato)
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, req.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """insert into creatives
                   (tenant_id, format, funnel, network, script, caption, title, description, hashtags,
                    status, quality_score, quality_breakdown, brief,
                    test_cycle_id, variant_index, angulo_ivs, hook_tipo, objecao_alvo, quebra_objecao,
                    visual_tipo, cta_tipo, destino_criativo, hypothesis, modular_blocks,
                    seo_social_intent, send_save_reason, trial_reel, expected_intent_signal, quality_metric)
                   values (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,'gerado',%s,%s::jsonb,%s::jsonb,
                           %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s)
                   returning id, created_at""",
                (tenant_id, req.formato, req.funil, req.rede,
                 json.dumps(output, ensure_ascii=False),
                 output.get("caption"), output.get("title"), output.get("description"),
                 json.dumps(output.get("hashtags", []), ensure_ascii=False),
                 score, json.dumps(breakdown, ensure_ascii=False),
                 json.dumps(_brief_payload(req), ensure_ascii=False),
                 req.test_cycle_id, req.variant_index, meta["angulo_ivs"], meta["hook_tipo"], meta["objecao_alvo"],
                 meta["quebra_objecao"], meta["visual_tipo"], meta["cta_tipo"], meta["destino_criativo"],
                 meta["hypothesis"], json.dumps(meta["modular_blocks"], ensure_ascii=False),
                 meta["seo_social_intent"], meta["send_save_reason"], bool(meta["trial_reel"]),
                 meta["expected_intent_signal"], meta["quality_metric"]),
            )
            row = cur.fetchone()
            if req.formato == "reels":
                cur.execute("update creatives set reel_status=%s where id=%s", ("storyboard_pendente", row["id"]))
    return {
        "id": row["id"], "created_at": row["created_at"], "format": req.formato, "destino": req.destino,
        "objetivo": req.objetivo, "model": result.get("model"), "mode": result.get("mode"),
        "viral_ref": (viral or {}).get("codigo"),
        "devices_pool": [d["name"] for d in devices],
        "quality_score": score, "quality_breakdown": breakdown,
        "output": output,
    }


@router.post("/matrix")
async def generate_matrix(req: MatrixRequest) -> dict:
    """Gera um ciclo de teste criativo modular (criativo como segmentação).
    Limite operacional inicial: 36 variações por chamada para manter revisão humana viável.
    """
    combos = list(itertools.product(req.angulos, req.hooks, req.objecoes, req.ctas, req.visuais))
    if not combos:
        raise HTTPException(400, "matriz vazia")
    if len(combos) > 36:
        raise HTTPException(400, f"matriz com {len(combos)} variações; limite inicial é 36")

    with get_conn() as conn:
        tenant_id = _tenant_id(conn, req.tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """insert into creative_test_cycles (tenant_id, name, objective, persona, status, started_at)
                   values (%s,%s,%s,%s,'active',now()) returning id::text as id, created_at""",
                (tenant_id, req.name, req.objetivo, req.persona),
            )
            cycle = cur.fetchone()

    items = []
    errors = []
    parent_id = None
    for idx, (angulo, hook_tipo, objecao, cta_tipo, visual_tipo) in enumerate(combos, start=1):
        one = OrchestrateRequest(
            tenant_slug=req.tenant_slug,
            objetivo=req.objetivo,
            formato=req.formato,
            rede=req.rede,
            destino=req.destino,
            angulo=angulo,
            hook_tipo=hook_tipo,
            objecao_alvo=objecao,
            visual_tipo=visual_tipo,
            cta_tipo=cta_tipo,
            test_cycle_id=cycle["id"],
            variant_index=idx,
            tema=req.tema,
            persona=req.persona,
            funil=req.funil,
        )
        try:
            with get_conn() as conn:
                tid = _tenant_id(conn, one.tenant_slug)
                viral, devices, brand = _fetch_context(conn, tid, one.objetivo, one.tema)
            result = await _motor(_build_prompt(one, viral, devices, brand), SYSTEM_PROMPT)
            output = _apply_caption_footer(_extract_json(result.get("content", "")))
            output["destino"] = one.destino
            if one.destino == "meta_ads" and one.angulo:
                output["angulo"] = one.angulo
                output["angulo_nome"] = (ANGULOS_META.get(one.angulo) or {}).get("nome")
            meta = _modular_meta(one, output)
            score, breakdown = _quality(output, one.formato)
            with get_conn() as conn:
                tenant_id = _tenant_id(conn, one.tenant_slug)
                with conn.cursor() as cur:
                    cur.execute(
                        """insert into creatives
                           (tenant_id, format, funnel, network, script, caption, title, description, hashtags,
                            status, quality_score, quality_breakdown, brief,
                            test_cycle_id, parent_creative_id, variant_index, angulo_ivs, hook_tipo, objecao_alvo,
                            quebra_objecao, visual_tipo, cta_tipo, destino_criativo, hypothesis, modular_blocks,
                            seo_social_intent, send_save_reason, trial_reel, expected_intent_signal, quality_metric)
                           values (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,'gerado',%s,%s::jsonb,%s::jsonb,
                                   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s)
                           returning id::text as id, created_at""",
                        (tenant_id, one.formato, one.funil, one.rede,
                         json.dumps(output, ensure_ascii=False), output.get("caption"), output.get("title"),
                         output.get("description"), json.dumps(output.get("hashtags", []), ensure_ascii=False),
                         score, json.dumps(breakdown, ensure_ascii=False),
                         json.dumps(_brief_payload(one), ensure_ascii=False),
                         one.test_cycle_id, parent_id, one.variant_index, meta["angulo_ivs"], meta["hook_tipo"],
                         meta["objecao_alvo"], meta["quebra_objecao"], meta["visual_tipo"], meta["cta_tipo"],
                         meta["destino_criativo"], meta["hypothesis"], json.dumps(meta["modular_blocks"], ensure_ascii=False),
                         meta["seo_social_intent"], meta["send_save_reason"], bool(meta["trial_reel"]),
                         meta["expected_intent_signal"], meta["quality_metric"]),
                    )
                    row = cur.fetchone()
                    if parent_id is None:
                        parent_id = row["id"]
                    if one.formato == "reels":
                        cur.execute("update creatives set reel_status=%s where id=%s", ("storyboard_pendente", row["id"]))
            items.append({"creative_id": row["id"], "variant_index": idx, "quality_score": score,
                          "angulo_ivs": meta["angulo_ivs"], "hook_tipo": meta["hook_tipo"],
                          "objecao_alvo": meta["objecao_alvo"], "visual_tipo": meta["visual_tipo"],
                          "cta_tipo": meta["cta_tipo"]})
        except Exception as e:
            errors.append({"variant_index": idx, "angulo": angulo, "hook_tipo": hook_tipo,
                           "objecao_alvo": objecao, "cta_tipo": cta_tipo, "visual_tipo": visual_tipo,
                           "error": f"{type(e).__name__}: {e}"})
    return {"test_cycle_id": cycle["id"], "requested": len(combos), "created": len(items), "errors": errors, "items": items}


@router.post("/creatives/{cid}/regerar")
async def regerar(cid: str) -> dict:
    """Regera a peça aplicando o feedback/melhorias solicitado -> status 'gerado' (worker re-renderiza)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select format, network, title, feedback, brief from creatives where id=%s", (cid,))
            c = cur.fetchone()
    if not c:
        raise HTTPException(404, "creative não encontrado")
    brief = c.get("brief") or {}
    if isinstance(brief, str):
        try: brief = json.loads(brief)
        except Exception: brief = {}
    fb = c.get("feedback") or ""
    if fb:
        fb = (
            "CORREÇÕES DO REVISOR — aplique de forma literal quando houver indicação por slide; "
            "se houver 'Slide N', altere aquele slide especificamente e preserve os demais quando não citados:\n" + fb
        )
    req = OrchestrateRequest(
        tenant_slug=brief.get("tenant_slug", "demo"),
        formato=brief.get("formato") or c.get("format") or "carrossel",
        objetivo=brief.get("objetivo", "identificação"),
        rede=brief.get("rede") or c.get("network") or "instagram",
        destino=brief.get("destino", "feed"),
        angulo=brief.get("angulo"),
        hook_tipo=brief.get("hook_tipo"),
        objecao_alvo=brief.get("objecao_alvo"),
        quebra_objecao=brief.get("quebra_objecao"),
        visual_tipo=brief.get("visual_tipo"),
        cta_tipo=brief.get("cta_tipo"),
        tema=brief.get("tema") or (c.get("title") or "").replace("*", ""),
        persona=brief.get("persona"),
        funil=brief.get("funil", "relacionamento_conversao"),
        melhorias=fb or None,
    )
    with get_conn() as conn:
        tid = _tenant_id(conn, req.tenant_slug)
        viral, devices, brand = _fetch_context(conn, tid, req.objetivo, req.tema)
    result = await _motor(_build_prompt(req, viral, devices, brand), SYSTEM_PROMPT)
    output = _apply_caption_footer(_extract_json(result.get("content", "")))
    output["destino"] = req.destino
    if req.destino == "meta_ads" and req.angulo:
        output["angulo"] = req.angulo
        output["angulo_nome"] = (ANGULOS_META.get(req.angulo) or {}).get("nome")
    meta = _modular_meta(req, output)
    score, breakdown = _quality(output, req.formato)
    render_dir = os.path.join(RENDERS_DIR, cid)
    if os.path.isdir(render_dir):
        shutil.rmtree(render_dir, ignore_errors=True)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("update creatives set script=%s, caption=%s, title=%s, hashtags=%s::jsonb, "
                        "quality_score=%s, quality_breakdown=%s::jsonb, status='gerado', asset_url=null, "
                        "angulo_ivs=%s, hook_tipo=%s, objecao_alvo=%s, quebra_objecao=%s, visual_tipo=%s, "
                        "cta_tipo=%s, destino_criativo=%s, hypothesis=%s, modular_blocks=%s::jsonb, "
                        "seo_social_intent=%s, send_save_reason=%s, trial_reel=%s, expected_intent_signal=%s, quality_metric=%s "
                        "where id=%s",
                        (json.dumps(output, ensure_ascii=False), output.get("caption"), output.get("title"),
                         json.dumps(output.get("hashtags", []), ensure_ascii=False),
                         score, json.dumps(breakdown, ensure_ascii=False), meta["angulo_ivs"], meta["hook_tipo"],
                         meta["objecao_alvo"], meta["quebra_objecao"], meta["visual_tipo"], meta["cta_tipo"],
                         meta["destino_criativo"], meta["hypothesis"], json.dumps(meta["modular_blocks"], ensure_ascii=False),
                         meta["seo_social_intent"], meta["send_save_reason"], bool(meta["trial_reel"]),
                         meta["expected_intent_signal"], meta["quality_metric"], cid))
    return {"id": cid, "regenerated": True, "quality_score": score, "model": result.get("model"), "aplicou_melhorias": bool(fb)}


def _assets_for(cid: str) -> list[str]:
    adir = os.path.join(RENDERS_DIR, cid)
    if not os.path.isdir(adir):
        return []
    return [f"/renders/{cid}/{os.path.basename(p)}"
            for p in sorted(glob.glob(os.path.join(adir, "*.png")))]


@router.get("/creatives")
def list_creatives(tenant_slug: str = "demo", limit: int = 40, test_cycle_id: str | None = None,
                   angulo_ivs: str | None = None, hook_tipo: str | None = None,
                   objecao_alvo: str | None = None, visual_tipo: str | None = None,
                   cta_tipo: str | None = None, destino_criativo: str | None = None,
                   status: str | None = None, format: str | None = None) -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            wh = ["tenant_id=%s"]
            params = [tid]
            for col, val in (("test_cycle_id", test_cycle_id), ("angulo_ivs", angulo_ivs), ("hook_tipo", hook_tipo),
                             ("objecao_alvo", objecao_alvo), ("visual_tipo", visual_tipo), ("cta_tipo", cta_tipo),
                             ("destino_criativo", destino_criativo), ("status", status), ("format", format)):
                if val:
                    wh.append(f"{col}=%s")
                    params.append(val)
            params.append(limit)
            cur.execute(
                "select id::text as id, format, funnel, network, title, caption, hashtags, "
                "status, quality_score, asset_url, reel_status, reel_url, created_at, feedback, script, "
                "test_cycle_id::text as test_cycle_id, variant_index, angulo_ivs, hook_tipo, objecao_alvo, "
                "quebra_objecao, visual_tipo, cta_tipo, destino_criativo, hypothesis, modular_blocks, "
                "seo_social_intent, send_save_reason, trial_reel, expected_intent_signal, quality_metric "
                f"from creatives where {' and '.join(wh)} order by created_at desc limit %s", params)
            rows = cur.fetchall()
    items = []
    for r in rows:
        d = dict(r)
        try:
            _o = json.loads(r["script"]) if r.get("script") else {}
            d["destino"] = d.get("destino_criativo") or _o.get("destino")
            d["angulo_nome"] = _o.get("angulo_nome")
        except Exception:
            d["destino"] = None
            d["angulo_nome"] = None
        d.pop("script", None)
        d["assets"] = _assets_for(r["id"]) if r.get("asset_url") else []
        items.append(d)
    return {"items": items}


@router.get("/roteiros")
def list_roteiros(tenant_slug: str = "demo") -> dict:
    """Banco de Roteiros = bunker IVS global + roteiros do tenant (ex.: engenharia reversa)."""
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                "select codigo, origem, objetivo, classe_ivs, mecanismo, hook_base, tese_central, "
                "objecao_principal, adaptacao_ivs, status, referencias, ideia_prompt, plataforma, "
                "fonte_raw from viral_scripts where tenant_id is null or tenant_id=%s order by codigo", (tid,))
            rows = cur.fetchall()
            cur.execute("select classe_ivs, count(*) as n from viral_scripts "
                        "where tenant_id is null or tenant_id=%s group by classe_ivs order by n desc", (tid,))
            classes = [dict(r) for r in cur.fetchall() if r["classe_ivs"]]
    return {"total": len(rows), "classes": classes, "items": [dict(r) for r in rows]}


class EngReversaRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    handle: str | None = None                 # @perfil de referência (opcional)
    referencia: str                            # texto do reel/anúncio campeão (caption, hook, descrição)


ER_FRAMEWORK = (
    "Você executa ENGENHARIA REVERSA DE CONTEÚDO VIRAL para o Instituto Vital Slim (Dra. Daniely Freitas, "
    "médica; nicho mulher 30-55 emagrecimento/hormônios). A partir de uma REFERÊNCIA (reel/anúncio que "
    "performou), você: (1) explica POR QUE viralizou (hook, estrutura, retention drivers); (2) gera 3 SCRIPTS "
    "originais adaptados à voz da Dra. (acolhedora, baseada em evidência, SEM promessa de resultado, sem "
    "antes/depois, sem medicalizar, sempre com CTA de consulta quando levantar sintoma; NUNCA crianças como "
    "sujeito); (3) define o tema dominante; (4) esboça 1 carrossel de 10 slides (hook, rehook, dor, valor x4, "
    "turning point, takeaway, CTA). Compliance CFM obrigatório. Cada script: hook (0-3s), desenvolvimento "
    "(3-25s), cta (25-35s), legenda. Toda legenda deve terminar exatamente com: " + CAPTION_FOOTER.replace("\n", " | ") + ". "
    "Use os dispositivos de engenharia social quando fizer sentido."
)


@router.post("/engenharia-reversa")
async def engenharia_reversa(req: EngReversaRequest) -> dict:
    prompt = (
        f"REFERÊNCIA (perfil {req.handle or 'n/d'}):\n{req.referencia}\n\n"
        'Entregue SOMENTE JSON com as chaves: "por_que_viralizou" (string), "tema_dominante" (string), '
        '"objetivo" (atração|identificação|educação|conversão|desejo|retenção), '
        '"classe_ivs" (quebra_de_mito|identificacao_de_dor|jornada_da_paciente|metodo_ivs|reframe_de_culpa|outro), '
        '"scripts" (lista de 3 objetos {hook, desenvolvimento, cta, legenda}), '
        '"carrossel" (lista de 10 strings, 1 por slide).'
    )
    try:
        result = await OpenRouterClient().generate(prompt, system=ER_FRAMEWORK)
        if result.get("mode") in ("mock", "degraded_mock"):
            raise RuntimeError("openrouter")
    except Exception:
        result = await CodexClient().generate(prompt, system=ER_FRAMEWORK)
    data = _apply_caption_footer(_extract_json(result.get("content", "")))
    scripts = data.get("scripts") or []
    saved = 0
    with get_conn() as conn:
        tid = _tenant_id(conn, req.tenant_slug)
        with conn.cursor() as cur:
            for i, s in enumerate(scripts, 1):
                if not isinstance(s, dict):
                    continue
                cur.execute("select 'ER-'||to_char(now(),'YYMMDDHH24MISS')||'-'||%s", (i,))
                codigo = cur.fetchone()["?column?"]
                adaptacao = "HOOK: %s\nDESENVOLVIMENTO: %s\nCTA: %s\nLEGENDA: %s" % (
                    s.get("hook", ""), s.get("desenvolvimento", ""), s.get("cta", ""), s.get("legenda", ""))
                cur.execute(
                    "insert into viral_scripts (tenant_id, codigo, origem, objetivo, classe_ivs, mecanismo, "
                    "hook_base, tese_central, adaptacao_ivs, status) "
                    "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,'eng_reversa')",
                    (tid, codigo, f"eng-reversa:{req.handle or 'manual'}", data.get("objetivo"),
                     data.get("classe_ivs"), "engenharia_reversa", s.get("hook"),
                     data.get("tema_dominante"), adaptacao))
                saved += 1
    return {"saved": saved, "model": result.get("model"), "mode": result.get("mode"), "analise": data}


class FeedbackRequest(BaseModel):
    texto: str


@router.post("/creatives/{cid}/feedback")
def feedback_creative(cid: str, req: FeedbackRequest) -> dict:
    """Tiaro solicita melhorias numa peça -> guarda o pedido + status 'ajustes_solicitados'."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("update creatives set feedback=%s, status='ajustes_solicitados' "
                        "where id=%s returning id::text as id", (req.texto, cid))
            r = cur.fetchone()
    if not r:
        raise HTTPException(404, "creative não encontrado")
    return {"id": r["id"], "status": "ajustes_solicitados", "feedback": req.texto}


@router.post("/creatives/{cid}/approve")
def approve_creative(cid: str) -> dict:
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        with conn.cursor() as cur:
            cur.execute("update creatives set status='aprovado' where id=%s returning id::text as id", (cid,))
            r = cur.fetchone()
        calendar = _ensure_calendar_for_creative(conn, cid) if r else None
    if not r:
        raise HTTPException(404, "creative não encontrado")
    return {"id": r["id"], "status": "aprovado", "calendar_entry": calendar}


# ---- ANÁLISE DE PERFORMANCE (rubrica IVS de sinais virais do Instagram) ----
class MetricsIn(BaseModel):
    reach: int | None = None
    retencao_3s_pct: float | None = None
    tempo_medio_seg: float | None = None
    conclusao_pct: float | None = None
    shares: int | None = None
    saves: int | None = None
    replays: int | None = None
    comentarios: int | None = None
    comentarios_qualificados: int | None = None
    profile_clicks: int | None = None
    follows: int | None = None
    whatsapp_leads: int | None = None
    likes: int | None = None
    skip_rate_pct: float | None = None
    seo_social_intent: str | None = None
    send_save_reason: str | None = None
    trial_reel: bool = False
    expected_intent_signal: str | None = None
    quality_metric: str | None = None


# pesos pela ordem do ranking IVS (soma ~1.0) + alvos de taxa por alcance
_W = {"ret": 0.20, "tempo": 0.16, "concl": 0.13, "shares": 0.12, "saves": 0.10,
      "replays": 0.08, "coment": 0.07, "clicks": 0.06, "follows": 0.05, "leads": 0.03}
_TARGET = {"shares": 0.02, "saves": 0.03, "replays": 0.10, "coment": 0.01,
           "clicks": 0.02, "follows": 0.005, "leads": 0.002}


def _viral_score(m: dict) -> tuple[float, dict]:
    reach = (m.get("reach") or 0) or 1
    def rate(v): return (v or 0) / reach
    norm = {
        "ret": min(1.0, (m.get("retencao_3s_pct") or 0) / 100),
        "tempo": min(1.0, (m.get("tempo_medio_seg") or 0) / 25),
        "concl": min(1.0, (m.get("conclusao_pct") or 0) / 100),
        "shares": min(1.0, rate(m.get("shares")) / _TARGET["shares"]),
        "saves": min(1.0, rate(m.get("saves")) / _TARGET["saves"]),
        "replays": min(1.0, rate(m.get("replays")) / _TARGET["replays"]),
        "coment": min(1.0, rate(m.get("comentarios_qualificados")) / _TARGET["coment"]),
        "clicks": min(1.0, rate(m.get("profile_clicks")) / _TARGET["clicks"]),
        "follows": min(1.0, rate(m.get("follows")) / _TARGET["follows"]),
        "leads": min(1.0, rate(m.get("whatsapp_leads")) / _TARGET["leads"]),
    }
    base = 100 * sum(_W[k] * norm[k] for k in _W)
    penalty = (m.get("skip_rate_pct") or 0) / 100 * 25  # pular nos 1-2s reduz distribuição
    score = max(0.0, min(100.0, base - penalty))
    fracos = sorted(norm.items(), key=lambda kv: kv[1])[:3]
    return round(score, 1), {"norm": {k: round(v, 2) for k, v in norm.items()}, "fracos": [f[0] for f in fracos]}


@router.get("/creatives/{cid}/metrics")
def get_metrics(cid: str) -> dict:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select * from creative_metrics where creative_id=%s", (cid,))
            r = cur.fetchone()
    return {"metrics": dict(r) if r else None}


@router.post("/creatives/{cid}/metrics")
async def save_metrics(cid: str, m: MetricsIn) -> dict:
    md = m.model_dump()
    score, breakdown = _viral_score(md)
    # análise de melhorias via motor, usando a rubrica + conteúdo da peça
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select title, caption, script from creatives where id=%s", (cid,))
            c = cur.fetchone()
    if not c:
        raise HTTPException(404, "creative não encontrado")
    rubric = ("Ranking IVS de sinais (mais forte→fraco): 1.retenção 3s 2.tempo médio 3.taxa conclusão "
              "4.compartilhamentos/envios por alcance 5.salvamentos/alcance 6.replays 7.comentários qualificados "
              "8.cliques no perfil 9.follows 10.leads WhatsApp. Negativo: pular em 1-2s. Bom p/ IVS = quebra "
              "culpa + explica mecanismo; hook bate na dor nos 3s. Instagram 2026: avaliar SEO social/intenção "
              "de busca, motivo de envio/salvamento, Trial Reel e sinal real de intenção — curtida é apoio, não norte.")
    prompt = (rubric + chr(10) + "CRIATIVO: " + str(c.get("title")) + chr(10) + "Legenda: " + ((c.get("caption") or "")[:400]) + chr(10) + "METRICAS: " + json.dumps(md, ensure_ascii=False) + " | viral_score=" + str(score) + " | sinais mais fracos=" + str(breakdown["fracos"]) + chr(10) + "Faca uma ANALISE DE MELHORIAS objetiva em PT-BR (4-7 bullets): o que esta fraco vs a rubrica e ACOES concretas para melhorar cada sinal fraco (hook, formato, CTA, ritmo, prova). Especifico para o nicho mulher 40+.")
    try:
        result = await _motor(prompt, "Você é analista de performance de Reels do Instituto Vital Slim. Direto e acionável.")
        analise = result.get("content", "").strip()
    except Exception:
        analise = "(análise indisponível agora)"
    cols = ["reach", "retencao_3s_pct", "tempo_medio_seg", "conclusao_pct", "shares", "saves", "replays",
            "comentarios", "comentarios_qualificados", "profile_clicks", "follows", "whatsapp_leads",
            "likes", "skip_rate_pct"]
    text_cols = ["seo_social_intent", "send_save_reason", "trial_reel", "expected_intent_signal", "quality_metric"]
    all_cols = cols + text_cols
    sets = ", ".join(f"{c2}=excluded.{c2}" for c2 in all_cols)
    vals = [md.get(c2) for c2 in all_cols]
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"insert into creative_metrics (creative_id, {', '.join(all_cols)}, viral_score, analise, updated_at) "
                f"values (%s, {', '.join(['%s'] * len(all_cols))}, %s, %s, now()) "
                f"on conflict (creative_id) do update set {sets}, viral_score=excluded.viral_score, "
                f"analise=excluded.analise, updated_at=now()",
                [cid] + vals + [score, analise])
    return {"viral_score": score, "breakdown": breakdown, "analise": analise}


# ---- STORYBOARD DE REELS (aprovação/edição antes de renderizar) ----
class StoryboardEdit(BaseModel):
    beats: list[dict]


@router.post("/creatives/{cid}/storyboard")
def storyboard_gen(cid: str) -> dict:
    """Dispara a geração do storyboard (o daemon do host processa em background)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("update creatives set reel_status='storyboard_pendente' where id=%s "
                        "returning id::text as id", (cid,))
            r = cur.fetchone()
    if not r:
        raise HTTPException(404, "creative não encontrado")
    return {"id": r["id"], "reel_status": "storyboard_pendente"}


@router.get("/creatives/{cid}/storyboard")
def storyboard_get(cid: str) -> dict:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select reel_status, reel_url, storyboard from creatives where id=%s", (cid,))
            r = cur.fetchone()
    if not r:
        raise HTTPException(404, "creative não encontrado")
    return {"reel_status": r["reel_status"], "reel_url": r["reel_url"], "storyboard": r["storyboard"]}


@router.put("/creatives/{cid}/storyboard")
def storyboard_edit(cid: str, req: StoryboardEdit) -> dict:
    """Salva alterações do storyboard (textos/prompts/who editados pelo Tiaro)."""
    import json as _json
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select storyboard from creatives where id=%s", (cid,))
            r = cur.fetchone()
            if not r or not r["storyboard"]:
                raise HTTPException(404, "storyboard não encontrado")
            sb = r["storyboard"]
            sb["beats"] = req.beats
            sb["status"] = "editado"
            cur.execute("update creatives set storyboard=%s::jsonb where id=%s",
                        (_json.dumps(sb, ensure_ascii=False), cid))
    return {"ok": True, "beats": len(req.beats)}


@router.post("/creatives/{cid}/reel")
def reel_render(cid: str) -> dict:
    """Aprova o storyboard e dispara a renderização do reel (daemon do host)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("update creatives set reel_status='render_pendente' where id=%s "
                        "returning id::text as id", (cid,))
            r = cur.fetchone()
    if not r:
        raise HTTPException(404, "creative não encontrado")
    return {"id": r["id"], "reel_status": "render_pendente"}


# ---- INTELIGÊNCIA CRIATIVA (Marca & posicionamento — com validação) ----
class IntelIn(BaseModel):
    tenant_slug: str = "demo"
    titulo: str | None = None
    conteudo: str
    tipo: str | None = "diretriz"
    finalidade: str = "institucional"
    source_id: str | None = None


class IntelValidate(BaseModel):
    status: str  # aprovado | rejeitado | pendente


_INTEL_COLS = ("select id::text as id, source_id::text as source_id, finalidade, tipo, titulo, "
               "conteudo, status, created_at, validated_at from creative_intelligence")


@router.get("/intelligence")
def intel_list(tenant_slug: str = "demo", status: str | None = None) -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            if status:
                cur.execute(_INTEL_COLS + " where (tenant_id=%s or tenant_id is null) and status=%s "
                            "order by created_at desc", (tid, status))
            else:
                cur.execute(_INTEL_COLS + " where (tenant_id=%s or tenant_id is null) "
                            "order by (status='pendente') desc, created_at desc", (tid,))
            rows = cur.fetchall()
    return {"items": [dict(r) for r in rows]}


@router.post("/intelligence")
def intel_add(req: IntelIn) -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, req.tenant_slug)
        with conn.cursor() as cur:
            cur.execute("insert into creative_intelligence (tenant_id, source_id, finalidade, tipo, titulo, "
                        "conteudo, status) values (%s,%s,%s,%s,%s,%s,'pendente') returning id::text as id",
                        (tid, req.source_id, req.finalidade, req.tipo, req.titulo, req.conteudo))
            r = cur.fetchone()
    return {"id": r["id"], "status": "pendente"}


@router.post("/intelligence/{iid}/validate")
def intel_validate(iid: str, req: IntelValidate) -> dict:
    if req.status not in ("aprovado", "rejeitado", "pendente"):
        raise HTTPException(400, "status inválido")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("update creative_intelligence set status=%s, validated_at=now() where id=%s "
                        "returning id::text as id", (req.status, iid))
            r = cur.fetchone()
    if not r:
        raise HTTPException(404, "item não encontrado")
    return {"id": r["id"], "status": req.status}


@router.post("/intelligence/ingest")
async def intel_ingest(tenant_slug: str = "demo") -> dict:
    """Destila os sinais das fontes 'Marca & posicionamento' (institucional) em diretrizes PENDENTES."""
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute("select s.label as label, s.objetivo as objetivo, sg.caption as caption "
                        "from sources s left join source_signals sg on sg.source_id=s.id "
                        "where s.finalidade='institucional' and (s.tenant_id=%s or s.tenant_id is null) "
                        "order by sg.engagement desc nulls last limit 40", (tid,))
            rows = cur.fetchall()
    blobs = [r["caption"] for r in rows if r.get("caption")]
    fontes = sorted({r["label"] for r in rows if r.get("label")})
    if not blobs:
        return {"ingested": 0, "msg": "Sem sinais coletados nas fontes de Marca & posicionamento ainda. "
                "Cadastre fontes institucionais (o monitor diário coleta) ou adicione diretrizes manualmente."}
    amostra = chr(10).join("- " + (b or "")[:400] for b in blobs[:25])
    sys_p = ("Você é estrategista de marca. A partir dos posts de referências de Marca & posicionamento abaixo, "
             "extraia DIRETRIZES acionáveis (tom de voz, ângulos, ganchos, o-que-evitar) para o Instituto Vital "
             "Slim (saúde da mulher 40+). Responda SOMENTE JSON "
             '{"diretrizes":[{"titulo":"...","conteudo":"..."}]} com 5 a 10 itens curtos e específicos.')
    result = await _motor("FONTES: " + ", ".join(fontes) + chr(10) + "POSTS:" + chr(10) + amostra, sys_p)
    data = _extract_json(result.get("content", ""))
    items = data.get("diretrizes", []) if isinstance(data, dict) else []
    n = 0
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            for it in items:
                if not it.get("conteudo"):
                    continue
                cur.execute("insert into creative_intelligence (tenant_id, finalidade, tipo, titulo, conteudo, "
                            "status) values (%s,'institucional','diretriz',%s,%s,'pendente')",
                            (tid, it.get("titulo"), it.get("conteudo")))
                n += 1
    return {"ingested": n, "status": "pendente", "fontes": fontes}
