#!/usr/bin/env python3
"""Etapa 5 do pipeline V11 — Renderizador da apresentação.

Reaproveita o renderer V10 mas estende com:
  - Seção "O que os exames dizem clinicamente" (baseada em Etapa 3)
  - Seção "Como suas queixas se conectam aos resultados" (baseada em Etapa 4)
  - Diagnóstico executivo apoiado em hipóteses integradas (Etapa 4) em vez de
    contagem genérica de alterados
  - Plano clínico integrado (alvos prioritários da Etapa 4)

Mantém todo o resto da V10 (hero, mirror, bioimped, levers, programa, CTA, modos).

Uso programático:
    from gerar_apresentacao_v11 import render_apresentacao_v11
    out = render_apresentacao_v11(
        paciente, questionario, exames, bioimpedancia,
        analise_questionario, interpretacao_exames, cruzamento,
        output_dir="/tmp", versao_paciente=False,
    )
"""
from __future__ import annotations
import sys
import os
from pathlib import Path
from html import escape as safe_html

BASE = Path("/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/scripts")
sys.path.insert(0, str(BASE))

# Reutiliza tudo da V10
from gerar_apresentacao_v10 import (
    render_apresentacao_v10 as _render_v10_orig,
    _detectar_perfil_disc,
)


# Helpers V11 — geração de blocos novos

def _sev_color(severidade):
    """Cor baseada em severidade 1-5."""
    mapa = {1: "#2D8A3F", 2: "#5fa57f", 3: "#D4A000", 4: "#C46A30", 5: "#BE3226"}
    return mapa.get(severidade, "#7a6552")


def _sev_label(severidade):
    return {1: "Normal", 2: "Monitorar", 3: "Alterado leve", 4: "Significativo", 5: "Crítico"}.get(severidade, "—")


def render_interpretacao_clinica_section(interpretacao):
    """Seção V11: 'O que os exames mostram' — highlights pro paciente, não livro técnico.
    Filtra só severidade 4-5 (problemas reais), 2 blocos por card: o que significa + implicação se não tratar.
    A médica explica os detalhes na consulta.
    """
    if not interpretacao or not interpretacao.get("sistemas"):
        return ""

    # Coleta TODOS os exames severidade 4-5 entre todos os sistemas
    problemas = []
    for sis_key, sis_data in interpretacao["sistemas"].items():
        if not isinstance(sis_data, dict) or "exames_interpretados" not in sis_data:
            continue
        for ex in sis_data.get("exames_interpretados", []):
            if ex.get("severidade", 1) >= 4:
                ex_copy = dict(ex)
                ex_copy["_sistema"] = sis_key.replace("_", " ").title()
                problemas.append(ex_copy)

    if not problemas:
        # se nenhum severidade 4-5, mostra os top 6 severidade 3
        for sis_key, sis_data in interpretacao["sistemas"].items():
            if not isinstance(sis_data, dict):
                continue
            for ex in sis_data.get("exames_interpretados", []):
                if ex.get("severidade", 1) >= 3:
                    ex_copy = dict(ex); ex_copy["_sistema"] = sis_key.replace("_", " ").title()
                    problemas.append(ex_copy)

    # Ordena por severidade desc e limita a 8 cards (preserva foco)
    problemas.sort(key=lambda x: -x.get("severidade", 1))
    problemas = problemas[:8]

    if not problemas:
        return ""

    cards = []
    for ex in problemas:
        sev = ex.get("severidade", 1)
        cor = _sev_color(sev)
        sev_lab = "Atenção" if sev == 3 else ("Significativo" if sev == 4 else "Prioridade alta")

        # Reusa risco_curto_prazo como "o que significa" — costuma ser mais imediato/concreto
        # e risco_medio_prazo como "implicação se não tratar"
        o_que_significa = ex.get('risco_curto_prazo', '') or ex.get('diagnostico_tendencia', '')
        se_nao_tratar = ex.get('risco_medio_prazo', '')

        cards.append(f"""
        <div class="ex-card-v2" style="border-left:4px solid {cor}">
          <div class="ex-head-v2">
            <div class="ex-title">
              <strong>{safe_html(ex.get('nome',''))}</strong>
              <span class="ex-val-inline">{safe_html(ex.get('valor',''))} {safe_html(ex.get('unidade',''))}</span>
              <span class="ex-ref-inline">referência: {safe_html(ex.get('referencia','—'))}</span>
            </div>
            <span class="ex-sev-tag" style="background:{cor}1a;color:{cor};border-color:{cor}">{sev_lab}</span>
          </div>
          <div class="ex-body-v2">
            <div class="ex-bloco">
              <span class="ex-label">O que isso significa</span>
              <p>{safe_html(o_que_significa)}</p>
            </div>
            <div class="ex-bloco ex-bloco-warn">
              <span class="ex-label">Se não for tratado</span>
              <p>{safe_html(se_nao_tratar)}</p>
            </div>
          </div>
        </div>""")

    return f"""
<section id="interpretacao-clinica" class="section interpretacao-section medical-mode">
  <div class="wrap">
    <h2>O que os exames mostram</h2>
    <p class="lead">Resumo dos achados mais relevantes para apoio da consulta. Eu detalho cada ponto pessoalmente: <strong>o que cada alteração significa</strong> e <strong>o que pode acontecer se nada for feito</strong>.</p>
    <div class="ex-grid-v2">
      {''.join(cards)}
    </div>
  </div>
</section>
"""


def render_cruzamento_section(cruzamento, primeiro_nome):
    """Seção V11 NOVA: 'Como suas queixas se conectam aos resultados'."""
    if not cruzamento or not cruzamento.get("hipoteses_integradas"):
        return ""

    pri_color = {1: "#5fa57f", 2: "#D4A000", 3: "#BE3226"}
    pri_label = {1: "Baixa", 2: "Média", 3: "Alta"}

    hipoteses_cards = []
    for h in sorted(cruzamento["hipoteses_integradas"], key=lambda x: -x.get("prioridade", 1)):
        pri = h.get("prioridade", 1)
        cor = pri_color.get(pri, "#7a6552")
        queixas = h.get("queixas_relacionadas", [])
        exames = h.get("exames_relacionados", [])
        hipoteses_cards.append(f"""
        <div class="hip-card" style="border-top:4px solid {cor}">
          <div class="hip-head">
            <h4>{safe_html(h.get('titulo',''))}</h4>
            <span class="hip-pri" style="background:{cor}1a;color:{cor}">Prioridade {pri_label.get(pri,'?')}</span>
          </div>
          <p class="hip-desc">{safe_html(h.get('descricao_clinica',''))}</p>
          <div class="hip-grid">
            <div>
              <span class="hip-label">Sintomas que apoiam</span>
              <ul>{''.join(f'<li>{safe_html(q)}</li>' for q in queixas)}</ul>
            </div>
            <div>
              <span class="hip-label">Exames que apoiam</span>
              <ul>{''.join(f'<li>{safe_html(e)}</li>' for e in exames)}</ul>
            </div>
          </div>
          <p class="hip-acao"><strong>Ação proposta:</strong> {safe_html(h.get('acao_proposta',''))}</p>
        </div>""")

    queixas_sem_lab = cruzamento.get("queixas_sem_correlato_laboratorial", []) or []
    achados_sem_q = cruzamento.get("achados_sem_queixa_correspondente", []) or []

    blocos_extras = []
    if queixas_sem_lab:
        items = "".join(f"<li><strong>{safe_html(q['queixa'])}.</strong> {safe_html(q.get('interpretacao',''))} <em>Próxima ação: {safe_html(q.get('proxima_acao',''))}</em></li>" for q in queixas_sem_lab)
        blocos_extras.append(f"""
        <div class="extra-bloco">
          <h4>Sintomas sem correlato laboratorial</h4>
          <p class="extra-lead">Pontos que merecem investigação além do laboratório (estilo de vida, psicossocial, função).</p>
          <ul>{items}</ul>
        </div>""")
    if achados_sem_q:
        items = "".join(f"<li><strong>{safe_html(a['achado'])}.</strong> {safe_html(a.get('relevancia_clinica',''))} <em>Monitoramento: {safe_html(a.get('monitoramento',''))}</em></li>" for a in achados_sem_q)
        blocos_extras.append(f"""
        <div class="extra-bloco">
          <h4>Achados sem queixa correspondente</h4>
          <p class="extra-lead">Alterações silenciosas que merecem atenção mesmo sem sintoma percebido.</p>
          <ul>{items}</ul>
        </div>""")

    plano = cruzamento.get("plano_clinico_integrado", {}) or {}
    alvos = plano.get("alvos_prioritarios", []) or []
    invest = plano.get("investigacoes_adicionais", []) or []
    monitoramento = plano.get("monitoramento_sugerido", "")

    plano_html = f"""
    <div class="plano-bloco">
      <h3>Plano clínico integrado</h3>
      <div class="plano-grid">
        <div>
          <h5>Alvos prioritários</h5>
          <ol>{''.join(f'<li>{safe_html(a)}</li>' for a in alvos)}</ol>
        </div>
        <div>
          <h5>Investigações sugeridas</h5>
          {('<ul>' + ''.join(f'<li>{safe_html(i)}</li>' for i in invest) + '</ul>') if invest else '<p class="small">Nenhuma investigação adicional sugerida no momento.</p>'}
        </div>
        <div>
          <h5>Monitoramento</h5>
          <p>{safe_html(monitoramento)}</p>
        </div>
      </div>
    </div>"""

    return f"""
<section id="cruzamento-q-e" class="section cruzamento-section medical-mode">
  <div class="wrap">
    <h2>Como suas queixas se conectam aos resultados, {safe_html(primeiro_nome)}</h2>
    <p class="lead">Hipóteses integradas cruzando o que você relatou no questionário com o que os exames mostram. Cada hipótese tem prioridade clínica e ação proposta.</p>
    <div class="hip-grid-list">
      {''.join(hipoteses_cards)}
    </div>
    {''.join(blocos_extras)}
    {plano_html}
  </div>
</section>
"""


V11_CSS = """
/* === V11: Interpretação clínica (highlights) + Cruzamento Q×E === */
.interpretacao-section{ background:var(--paper); padding:var(--s-7) 0; }
.interpretacao-section .ex-grid-v2{ display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:var(--s-3);margin-top:var(--s-5); }
.interpretacao-section .ex-card-v2{ background:var(--paper);border:1px solid var(--line);
  border-radius:14px;padding:var(--s-4);box-shadow:0 4px 14px rgba(88,62,32,.04); }
.interpretacao-section .ex-head-v2{ display:flex;justify-content:space-between;align-items:flex-start;
  gap:var(--s-3);margin-bottom:var(--s-3);flex-wrap:wrap;padding-bottom:var(--s-3);border-bottom:1px dashed var(--line); }
.interpretacao-section .ex-title{ flex:1; }
.interpretacao-section .ex-title strong{ font-size:15px;color:var(--ink);display:block; }
.interpretacao-section .ex-val-inline{ display:inline-block;font-variant-numeric:tabular-nums;
  font-weight:700;color:var(--gold-dark);font-size:14px;margin-top:4px; }
.interpretacao-section .ex-ref-inline{ display:block;font-size:11.5px;color:var(--muted);margin-top:2px; }
.interpretacao-section .ex-sev-tag{ font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;
  border:1px solid; letter-spacing:0.04em;text-transform:uppercase;white-space:nowrap; }
.interpretacao-section .ex-body-v2{ display:grid;gap:var(--s-3); }
.interpretacao-section .ex-bloco{ background:rgba(245,234,217,.4);border-radius:8px;padding:10px 12px; }
.interpretacao-section .ex-bloco-warn{ background:rgba(217,160,0,.08);border-left:3px solid var(--gold-dark); }
.interpretacao-section .ex-label{ display:block;font-size:11px;color:var(--gold-dark);
  font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px; }
.interpretacao-section .ex-bloco p{ margin:0;font-size:13.5px;line-height:1.55;color:var(--ink); }

.cruzamento-section{ background: var(--cream); padding:var(--s-7) 0; }
.cruzamento-section .hip-grid-list{ display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:var(--s-4);margin-top:var(--s-5); }
.cruzamento-section .hip-card{ background:var(--paper);border:1px solid var(--line);
  border-radius:14px;padding:var(--s-5);box-shadow:0 6px 18px rgba(88,62,32,.05); }
.cruzamento-section .hip-head{ display:flex;justify-content:space-between;align-items:center;gap:var(--s-3); }
.cruzamento-section .hip-head h4{ margin:0;font-size:16px;color:var(--ink);font-weight:700; }
.cruzamento-section .hip-pri{ font-size:11px;font-weight:700;padding:3px 10px;border-radius:999px;letter-spacing:0.04em;text-transform:uppercase; }
.cruzamento-section .hip-desc{ margin:var(--s-3) 0;font-size:13.5px;line-height:1.6;color:var(--ink-soft); }
.cruzamento-section .hip-grid{ display:grid;grid-template-columns:1fr 1fr;gap:var(--s-3);
  background:rgba(217,192,139,.08);border-radius:10px;padding:var(--s-3);margin:var(--s-3) 0; }
.cruzamento-section .hip-label{ display:block;font-size:11px;color:var(--gold-dark);font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px; }
.cruzamento-section .hip-grid ul{ margin:0;padding-left:18px; }
.cruzamento-section .hip-grid li{ font-size:12.5px;line-height:1.5;color:var(--ink-soft);margin:3px 0; }
.cruzamento-section .hip-acao{ font-size:13px;color:var(--ink);background:#fff8eb;
  border-left:3px solid var(--gold);padding:10px 12px;border-radius:8px;margin:var(--s-3) 0 0; }

.cruzamento-section .extra-bloco{ background:var(--paper);border:1px dashed var(--line);
  border-radius:12px;padding:var(--s-4);margin-top:var(--s-4); }
.cruzamento-section .extra-bloco h4{ margin:0 0 6px;font-size:14px;color:var(--gold-dark);
  text-transform:uppercase;letter-spacing:.06em; }
.cruzamento-section .extra-lead{ font-size:12.5px;color:var(--muted);margin:0 0 var(--s-2); }
.cruzamento-section .extra-bloco ul{ margin:var(--s-2) 0 0;padding-left:18px; }
.cruzamento-section .extra-bloco li{ font-size:13px;line-height:1.55;color:var(--ink-soft);margin:6px 0; }

.cruzamento-section .plano-bloco{ background:linear-gradient(135deg,rgba(193,154,69,0.08),rgba(193,154,69,0.02));
  border:1px solid rgba(193,154,69,0.2);border-radius:14px;padding:var(--s-5);margin-top:var(--s-5); }
.cruzamento-section .plano-bloco h3{ margin:0 0 var(--s-3);font-size:16px;color:var(--gold-dark);
  text-transform:uppercase;letter-spacing:.08em; }
.cruzamento-section .plano-grid{ display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s-4); }
.cruzamento-section .plano-grid h5{ margin:0 0 var(--s-2);font-size:12px;color:var(--gold-dark);
  text-transform:uppercase;letter-spacing:.05em; }
.cruzamento-section .plano-grid li, .cruzamento-section .plano-grid p{ font-size:12.5px;line-height:1.55;color:var(--ink); }

/* Contexto pessoal — mobile-first, sem bullets nativos quebrando a leitura */
.compact-decision .context-list{ display:grid;gap:10px;margin:12px 0 0;padding:0;list-style:none; }
.compact-decision .context-item{ background:rgba(255,255,255,.58);border:1px solid var(--line);border-left:3px solid var(--gold);
  border-radius:10px;padding:12px 14px;list-style:none; }
.compact-decision .context-item strong{ display:block;color:var(--ink);font-size:13.5px;line-height:1.38;margin-bottom:4px;font-weight:700; }
.compact-decision .context-item span{ display:block;color:var(--muted);font-size:13px;line-height:1.48; }

@media(max-width:900px){
  .interpretacao-section .ex-grid{ grid-template-columns:1fr; }
  .cruzamento-section .hip-grid-list{ grid-template-columns:1fr; }
  .cruzamento-section .hip-grid, .cruzamento-section .plano-grid{ grid-template-columns:1fr; }
  .compact-decision{ padding-left:0;padding-right:0; }
  .compact-decision .context-item{ padding:12px; }
}
"""


def render_apresentacao_v11(paciente, questionario=None, exames=None,
                             output_dir=None, versao_paciente=False,
                             perfil_disc=None, bioimpedancia=None,
                             analise_questionario=None,
                             interpretacao_exames=None,
                             cruzamento=None):
    """Gera apresentação V11 = V10 + 2 seções novas (interpretação clínica + cruzamento Q×E).

    Estratégia: render V10 normal, depois injeta as 2 seções novas antes
    do bloco de programa 180 dias, e adiciona o CSS V11 no <head>.
    """
    # 1) chama o renderer V10 padrão
    html_path = _render_v10_orig(
        paciente=paciente,
        questionario=questionario,
        exames=exames,
        output_dir=output_dir,
        versao_paciente=versao_paciente,
        perfil_disc=perfil_disc,
        bioimpedancia=bioimpedancia,
    )

    # 2) le HTML gerado
    html = Path(html_path).read_text(encoding="utf-8")

    # 3) gera os 2 blocos V11
    primeiro_nome = safe_html(str(paciente.get("nome", "")).split()[0] if paciente.get("nome") else "")
    interp_html = render_interpretacao_clinica_section(interpretacao_exames) if interpretacao_exames else ""
    cruz_html = render_cruzamento_section(cruzamento, primeiro_nome) if cruzamento else ""

    # 3b) Substituições de blocos genéricos do V10 por dados reais V11
    if cruzamento or interpretacao_exames or analise_questionario:
        import re as _re

        # Função reutilizável pra remover qualquer SENTENÇA que mencione DISC
        _disc_pats = [
            r'O\s+perfil\s+DISC[^.<]*\.',
            r'\bperfil\s+DISC[^.<]*\.',
            r'tipo\s+[DISC]\s+\(estável[^)]*\)[^.]*\.',
            r'\(estável,\s*colaborativ[ao]?,?\s*avess[ao][^)]*\)',
            r'\(estável,\s*avess[ao][^)]*\)',
            r'A\s+abordagem\s+deve\s+respeitar\s+o\s+perfil[^.]*\.',
        ]
        def _strip_disc(text):
            if not text:
                return text
            for pat in _disc_pats:
                text = _re.sub(pat, '', text, flags=_re.IGNORECASE | _re.DOTALL)
            text = _re.sub(r'\s+', ' ', text).strip()
            return text

        # ---- (0) Cards do diagnóstico executivo "O que está acontecendo" + "Onde aparece" ----
        narrativa_raw = _strip_disc((cruzamento or {}).get("narrativa_executiva", "")) if cruzamento else ""
        alertas = (interpretacao_exames or {}).get("alertas_criticos_globais", []) if interpretacao_exames else []
        hipoteses_tmp = (cruzamento or {}).get("hipoteses_integradas", []) if cruzamento else []

        # Truncar narrativa em 2 frases (max ~360 chars) — é APRESENTAÇÃO, não relatório
        def _resumir_2_frases(txt, max_chars=360):
            if not txt:
                return ""
            sentencas = _re.split(r'(?<=[.!?])\s+', txt.strip())
            res = ""
            for s in sentencas[:2]:
                if len(res) + len(s) > max_chars:
                    break
                res = (res + " " + s).strip()
            if not res:
                res = sentencas[0][:max_chars].rstrip() + "..."
            return res

        narrativa = _resumir_2_frases(narrativa_raw)

        # Top 3 hipóteses como chips visuais
        chips_html = ""
        for h in sorted(hipoteses_tmp, key=lambda x: -x.get("prioridade", 1))[:3]:
            t = safe_html(h.get("titulo", "")[:80])
            pri = h.get("prioridade", 1)
            cor = {3: "#BE3226", 2: "#D4A000", 1: "#5fa57f"}.get(pri, "#8a6730")
            chips_html += (
                f'<span style="display:inline-block;background:{cor}1a;color:{cor};'
                f'border:1px solid {cor}33;border-radius:8px;padding:6px 12px;margin:4px 6px 0 0;'
                f'font-size:12.5px;font-weight:600;line-height:1.3">{t}</span>'
            )

        if narrativa or alertas or hipoteses_tmp:
            if narrativa:
                card1 = (
                    f'<h4>O que está acontecendo</h4>\n'
                    f'        <p class="body-text">{safe_html(narrativa)}</p>\n'
                    + (f'        <div style="margin-top:var(--s-3)">{chips_html}</div>' if chips_html else '')
                )
            elif hipoteses_tmp:
                top = hipoteses_tmp[0]
                desc = _resumir_2_frases(_strip_disc(top.get("descricao_clinica", "")))
                card1 = (
                    f'<h4>O que está acontecendo</h4>\n'
                    f'        <p class="body-text"><strong>{safe_html(top.get("titulo",""))}.</strong> {safe_html(desc)}</p>'
                )
            else:
                card1 = '<h4>O que está acontecendo</h4>\n        <p class="body-text">Análise integrada não disponível.</p>'
            achados_html = ""
            if alertas:
                for a in alertas[:4]:  # max 4 — apresentação é highlight
                    motivo_curto = a.get("motivo", "")
                    if len(motivo_curto) > 140:
                        motivo_curto = motivo_curto[:140].rsplit(" ", 1)[0] + "..."
                    achados_html += (
                        '<div style="background:#fff8eb;border-left:3px solid var(--gold);'
                        'padding:8px 12px;border-radius:6px;margin:6px 0;font-size:13px;line-height:1.5">'
                        f'<strong>{safe_html(a.get("exame",""))}</strong>: {safe_html(motivo_curto)}'
                        '</div>'
                    )
            if not achados_html and hipoteses_tmp:
                exs = []
                for h in hipoteses_tmp:
                    for e in h.get("exames_relacionados", [])[:3]:
                        if e and e not in exs:
                            exs.append(e)
                    if len(exs) >= 10:
                        break
                for ex in exs[:10]:
                    achados_html += (
                        '<span class="tag" style="background:#f3ead1;color:var(--ink);'
                        'display:inline-block;padding:4px 10px;border-radius:6px;margin:2px 4px 2px 0;'
                        f'font-size:12px;font-weight:600;">{safe_html(ex)}</span>'
                    )
            if not achados_html:
                achados_html = '<p class="body-text" style="color:var(--muted);font-style:italic;margin:0">Nenhum achado crítico mapeado.</p>'
            card2 = f'<h4>Onde aparece nos exames</h4>\n        <div style="margin-top:var(--s-3)">{achados_html}</div>'
            diag_pat = _re.compile(
                r'<div class="diag-card fade-up">\s*<h4>O que está acontecendo</h4>.*?</div>\s*'
                r'<div class="diag-card fade-up">\s*<h4>Onde aparece nos exames</h4>.*?</div>',
                _re.DOTALL
            )
            replacement = (
                f'<div class="diag-card fade-up">\n        {card1}\n      </div>\n'
                f'      <div class="diag-card fade-up">\n        {card2}\n      </div>'
            )
            html = diag_pat.sub(replacement, html, count=1)

        # ---- (a) REMOVER card "Perfil DISC" do mirror-grid ----
        # O DISC é usado internamente pra adaptar tom mas NÃO deve aparecer pro paciente
        disc_card_pattern = _re.compile(
            r'<div class="mirror-card">\s*<div class="label">Perfil DISC</div>\s*<div class="value">[^<]*</div>\s*</div>',
            _re.DOTALL
        )
        html = disc_card_pattern.sub("", html)

        # Hotfix: função reutilizável pra remover qualquer SENTENÇA que mencione DISC
        _disc_pats = [
            r'O\s+perfil\s+DISC[^.<]*\.',
            r'\bperfil\s+DISC[^.<]*\.',
            r'tipo\s+[DISC]\s+\(estável[^)]*\)[^.]*\.',
            r'\(estável,\s*colaborativ[ao]?,?\s*avess[ao][^)]*\)',
            r'\(estável,\s*avess[ao][^)]*\)',
            r'A\s+abordagem\s+deve\s+respeitar\s+o\s+perfil[^.]*\.',
        ]
        def _strip_disc(text):
            if not text:
                return text
            for pat in _disc_pats:
                text = _re.sub(pat, '', text, flags=_re.IGNORECASE | _re.DOTALL)
            text = _re.sub(r'\s+', ' ', text).strip()
            return text

        # ---- (b) Substituir "Leitura gerencial do questionário" ----
        # Hoje: 4 bullets hardcoded genéricos. Trocar por: interpretacao_inicial + sinais_alerta (top 3-4)
        if analise_questionario:
            # Pega APENAS a primeira frase da interpretação inicial (cenário em 1 linha)
            interp_inicial_full = _strip_disc(analise_questionario.get("interpretacao_inicial", ""))
            interp_resumida = _resumir_2_frases(interp_inicial_full, max_chars=240)
            sinais = analise_questionario.get("sinais_alerta", []) or []
            # max 3 sinais, justificativa truncada em 100 chars
            sinais_top = sorted(sinais, key=lambda x: -x.get("prioridade", 1))[:3]
            bullets_html = ""
            for s in sinais_top:
                just = _strip_disc(s.get("justificativa",""))
                if len(just) > 100:
                    just = just[:100].rsplit(" ", 1)[0] + "..."
                bullets_html += f'<li class="context-item"><strong>{safe_html(s.get("sinal",""))}.</strong><span>{safe_html(just)}</span></li>'
            if interp_resumida or bullets_html:
                nova_leitura = (
                    '<h4>Leitura do contexto pessoal</h4>'
                    + (f'<p class="body-text" style="margin-bottom:var(--s-3);font-size:14.5px">{safe_html(interp_resumida)}</p>' if interp_resumida else '')
                    + (f'<ul class="context-list">{bullets_html}</ul>' if bullets_html else '')
                )
                leitura_pat = _re.compile(
                    r'<h4>Leitura gerencial do questionário</h4>\s*<ul>.*?</ul>',
                    _re.DOTALL
                )
                html = leitura_pat.sub(nova_leitura, html, count=1)

        # ---- (c) Substituir "Os sinais que se conectam" ----
        # Visual leve: pares "Sintoma → Exame que confirma" (max 4 conexões)
        # SEM repetir descrição detalhada (que já está em "O que os exames mostram")
        if cruzamento:
            hipoteses = cruzamento.get("hipoteses_integradas", []) or []
            top_conexoes = [h for h in sorted(hipoteses, key=lambda x: -x.get("prioridade", 1))
                            if h.get("queixas_relacionadas") and h.get("exames_relacionados")][:4]
            if top_conexoes:
                conexoes_html = ""
                for h in top_conexoes:
                    pri = h.get("prioridade", 1)
                    cor = {1: "#5fa57f", 2: "#D4A000", 3: "#BE3226"}.get(pri, "#7a6552")
                    queixas = h.get("queixas_relacionadas", [])[:2]
                    exames = h.get("exames_relacionados", [])[:2]
                    queixas_str = " · ".join(safe_html(q) for q in queixas)
                    exames_str = " · ".join(safe_html(e.split('(')[0].strip()) for e in exames)
                    conexoes_html += f"""
                    <div style="background:#fffdf8;border:1px solid var(--line);border-left:4px solid {cor};border-radius:10px;padding:14px 18px;margin:10px 0;display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center">
                      <div>
                        <div style="font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">O que você sente</div>
                        <div style="font-size:13.5px;color:var(--ink);font-weight:500">{queixas_str}</div>
                      </div>
                      <div style="color:{cor};font-size:20px;font-weight:300">→</div>
                      <div>
                        <div style="font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">O que o exame confirma</div>
                        <div style="font-size:13.5px;color:var(--ink);font-weight:500">{exames_str}</div>
                      </div>
                    </div>"""
                # Substitui a tabela inteira por estes cards de conexão
                sinais_pat = _re.compile(
                    r'(<h3>Os sinais que se conectam</h3>\s*<p[^>]*>[^<]*</p>\s*)<table[^>]*>.*?</table>',
                    _re.DOTALL
                )
                replacement = r'\1' + conexoes_html
                html = sinais_pat.sub(replacement, html, count=1)

        # ---- (d) "Para onde a tendência aponta" — 1 parágrafo curto, sem lista repetitiva ----
        # (Os riscos detalhados por exame já estão em "O que os exames mostram")
        if interpretacao_exames or cruzamento:
            # Pega só o EXAME de maior severidade pra ser exemplo de risco principal
            riscos_medio = []
            for sis_key, sis_data in (interpretacao_exames or {}).get("sistemas", {}).items():
                if not isinstance(sis_data, dict):
                    continue
                for ex in sis_data.get("exames_interpretados", []):
                    if ex.get("severidade", 1) >= 4 and ex.get("risco_medio_prazo"):
                        riscos_medio.append({
                            "exame": ex.get("nome", ""),
                            "risco": ex.get("risco_medio_prazo", ""),
                            "sev": ex.get("severidade", 1)
                        })
            riscos_top = sorted(riscos_medio, key=lambda x: -x["sev"])[:1]  # só 1 exemplo

            cenario_q = ""
            if analise_questionario:
                cenario_q = analise_questionario.get("spin", {}).get("cenario_sem_tratamento", "")

            # Total de problemas (pra dar dimensão sem listar tudo)
            total_alterados = 0
            for sis_data in (interpretacao_exames or {}).get("sistemas", {}).values():
                if isinstance(sis_data, dict):
                    total_alterados += sum(1 for ex in sis_data.get("exames_interpretados", []) if ex.get("severidade", 1) >= 4)

            destaque_html = ""
            if riscos_top:
                r = riscos_top[0]
                # Não truncar com reticências: em apresentação clínica, texto cortado parece falha.
                risco_texto = str(r.get("risco", "")).strip()
                destaque_html = f'<p class="body-text" style="margin:var(--s-3) 0;padding:12px 14px;background:#fff8eb;border-left:3px solid var(--gold);border-radius:6px;font-size:13.5px"><strong>Exemplo principal — {safe_html(r["exame"])}:</strong> {safe_html(risco_texto)}</p>'

            cenario_html = ""
            if cenario_q and cenario_q.lower() not in ("permanecerá da mesma forma", "da mesma forma"):
                cenario_html = f'<p class="small" style="font-style:italic;color:var(--muted);margin-top:var(--s-3)">Sua percepção quando perguntamos sobre cenário sem tratamento: "{safe_html(cenario_q)}". A leitura clínica confirma essa percepção como real e mensurável.</p>'

            n_text = f"<strong>{total_alterados} marcadores</strong> em situação que merece atenção" if total_alterados else "Os marcadores avaliados"

            nova_tendencia = (
                '<h3>Para onde a tendência aponta</h3>'
                f'<p class="body-text">{n_text} indicam que, sem intervenção nos próximos 1–5 anos, o quadro tende a progredir — com impacto direto em energia, composição corporal, função hormonal e risco metabólico.</p>'
                + destaque_html
                + cenario_html
            )
            tend_pat = _re.compile(
                r'<h3>Para onde a tendência aponta</h3>.*?(?=</div>\s*<div class="leitura-block)',
                _re.DOTALL
            )
            html = tend_pat.sub(nova_tendencia, html, count=1)

        # ---- (e) "Recomendação clínica" — 3 prioridades + método (sem listar investigações extensas) ----
        if cruzamento:
            plano = cruzamento.get("plano_clinico_integrado", {}) or {}
            alvos_full = plano.get("alvos_prioritarios", []) or []
            # Top 3 alvos com texto reduzido
            alvos_top3 = []
            for a in alvos_full[:3]:
                a_curto = a if len(a) <= 110 else a[:110].rsplit(" ", 1)[0] + "..."
                alvos_top3.append(a_curto)
            if alvos_top3:
                alvos_html = ""
                for i, a in enumerate(alvos_top3, 1):
                    alvos_html += f"""
                <div style="display:flex;align-items:flex-start;gap:12px;margin:10px 0;padding:12px 14px;background:#fffdf8;border:1px solid var(--line);border-radius:10px">
                  <div style="background:var(--gold);color:#fff;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0">{i}</div>
                  <div style="font-size:13.5px;line-height:1.5;color:var(--ink)">{safe_html(a)}</div>
                </div>"""

                nova_rec = (
                    '<h3>Recomendação clínica</h3>'
                    '<p class="body-text" style="margin-bottom:var(--s-3);font-size:14.5px">'
                    'O plano combina os achados em prioridades concretas, aplicadas com método '
                    '<strong>180 dias</strong>: diagnóstico aprofundado, protocolo individualizado, execução assistida e '
                    'reavaliação trimestral. As <strong>3 frentes prioritárias</strong> da sua avaliação:'
                    '</p>'
                    + alvos_html
                )
                rec_pat = _re.compile(
                    r'<h3>Recomendação clínica</h3>.*?(?=</div>\s*</div>\s*</section>)',
                    _re.DOTALL
                )
                html = rec_pat.sub(nova_rec, html, count=1)
        narrativa = _strip_disc((cruzamento or {}).get("narrativa_executiva", "")) if cruzamento else ""
        alertas = (interpretacao_exames or {}).get("alertas_criticos_globais", []) if interpretacao_exames else []
        hipoteses = (cruzamento or {}).get("hipoteses_integradas", []) if cruzamento else []

        # Card 1: narrativa executiva (vinda do cruzamento Q × E)
        if narrativa:
            card1_html = f"""<h4>O que está acontecendo</h4>
        <p class="body-text">{safe_html(narrativa)}</p>"""
        else:
            # fallback: pega top hipótese
            top = hipoteses[0] if hipoteses else None
            if top:
                card1_html = f"""<h4>O que está acontecendo</h4>
        <p class="body-text"><strong>{safe_html(top.get('titulo',''))}.</strong> {safe_html(top.get('descricao_clinica',''))}</p>"""
            else:
                card1_html = """<h4>O que está acontecendo</h4>
        <p class="body-text">Análise integrada não disponível.</p>"""

        # Card 2: alertas críticos REAIS da Etapa 3 + exames das hipóteses
        achados_html = ""
        if alertas:
            for a in alertas[:8]:  # max 8
                ex_nome = a.get("exame", "")
                motivo = a.get("motivo", "")
                achados_html += (
                    '<div style="background:#fff8eb;border-left:3px solid var(--gold);'
                    'padding:8px 12px;border-radius:6px;margin:6px 0;font-size:13px;line-height:1.5">'
                    f'<strong>{safe_html(ex_nome)}</strong>: {safe_html(motivo)}'
                    '</div>'
                )
        if not achados_html and hipoteses:
            exames_set = []
            for h in hipoteses:
                for e in h.get("exames_relacionados", [])[:3]:
                    if e and e not in exames_set:
                        exames_set.append(e)
                if len(exames_set) >= 10:
                    break
            for ex in exames_set[:10]:
                achados_html += (
                    '<span class="tag" style="background:#f3ead1;color:var(--ink);'
                    'display:inline-block;padding:4px 10px;border-radius:6px;margin:2px 4px 2px 0;'
                    f'font-size:12px;font-weight:600;">{safe_html(ex)}</span>'
                )
        if not achados_html:
            achados_html = '<p class="body-text" style="color:var(--muted);font-style:italic;margin:0">Nenhum achado crítico mapeado neste cohort.</p>'

        card2_html = f"""<h4>Onde aparece nos exames</h4>
        <div style="margin-top:var(--s-3)">{achados_html}</div>"""

        # Substituir no HTML — pattern compreensivo
        pattern = _re.compile(
            r'<div class="diag-card fade-up">\s*<h4>O que está acontecendo</h4>.*?</div>\s*'
            r'<div class="diag-card fade-up">\s*<h4>Onde aparece nos exames</h4>.*?</div>',
            _re.DOTALL
        )
        replacement = (
            f'<div class="diag-card fade-up">\n        {card1_html}\n      </div>\n'
            f'      <div class="diag-card fade-up">\n        {card2_html}\n      </div>'
        )
        new_html, n_sub = pattern.subn(replacement, html, count=1)
        if n_sub > 0:
            html = new_html

    if interp_html or cruz_html:
        # injeta CSS V11 antes do </style>
        if "</style>" in html:
            html = html.replace("</style>", V11_CSS + "\n</style>", 1)
        # injeta as 2 seções antes do bloco de programa 180 dias
        anchor_candidates = [
            '<section id="program-180"',
            '<section class="program-180"',
            '<section id="critical-levers" class="section critical-levers">',
            '<!-- PROGRAMA 180 DIAS -->',
        ]
        injected = False
        injection = interp_html + "\n" + cruz_html
        for a in anchor_candidates:
            if a in html:
                html = html.replace(a, injection + "\n" + a, 1)
                injected = True
                break
        if not injected:
            # fallback: antes do </main>
            html = html.replace("</main>", injection + "\n</main>", 1)

        # Final hotfix: aplicar SÓ AGORA (após todas as injeções) pra pegar
        # qualquer menção de DISC vinda das seções dinâmicas
        import re as _re_final
        final_disc_pats = [
            r'O\s+perfil\s+DISC[^.<]*\.',
            r'\bperfil\s+DISC[^.<]*\.',
            r'A\s+abordagem\s+deve\s+respeitar\s+o\s+perfil[^.]*\.',
        ]
        for pat in final_disc_pats:
            html = _re_final.sub(pat, '', html, flags=_re_final.IGNORECASE | _re_final.DOTALL)

        # 4) salvar de volta no mesmo path mas com sufixo v11
        v11_path = Path(html_path).with_name(Path(html_path).name.replace("-v10-", "-v11-"))
        v11_path.write_text(html, encoding="utf-8")
        return v11_path

    return html_path  # sem alterações se não houver V11 data


if __name__ == "__main__":
    import argparse, json, time
    ap = argparse.ArgumentParser()
    ap.add_argument("--paciente", required=True, help="JSON paciente meta")
    ap.add_argument("--questionario", required=True)
    ap.add_argument("--exames", required=True)
    ap.add_argument("--bioimpedancia", default="")
    ap.add_argument("--analise-questionario", default="")
    ap.add_argument("--interpretacao-exames", default="")
    ap.add_argument("--cruzamento", default="")
    ap.add_argument("--output-dir", default="/tmp")
    ap.add_argument("--versao-paciente", action="store_true")
    args = ap.parse_args()

    paciente = json.load(open(args.paciente))
    questionario = json.load(open(args.questionario))
    exames = json.load(open(args.exames))
    bioimped = json.load(open(args.bioimpedancia)) if args.bioimpedancia else None
    analise_q = json.load(open(args.analise_questionario)) if args.analise_questionario else None
    interp_e = json.load(open(args.interpretacao_exames)) if args.interpretacao_exames else None
    cruz = json.load(open(args.cruzamento)) if args.cruzamento else None

    out = render_apresentacao_v11(
        paciente=paciente, questionario=questionario, exames=exames,
        output_dir=args.output_dir, versao_paciente=args.versao_paciente,
        bioimpedancia=bioimped, analise_questionario=analise_q,
        interpretacao_exames=interp_e, cruzamento=cruz,
    )
    print(f"[V11] {out}")
