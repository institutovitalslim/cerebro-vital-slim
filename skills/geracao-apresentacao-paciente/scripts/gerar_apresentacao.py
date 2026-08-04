#!/usr/bin/env python3
"""
COLETOR de dados de paciente (NÃO é mais o entrypoint da apresentação).

╔══════════════════════════════════════════════════════════════════════════════╗
║  ENTRYPOINT ÚNICO DA APRESENTAÇÃO:  scripts/gerar_apresentacao_paciente.py   ║
║                                                                              ║
║  O main() deste arquivo DELEGAVA o render a um agente LLM por mensagem       ║
║  (delegar_geracao_openclaw) — caminho que improvisava HTML fora do renderer  ║
║  canônico e nunca chamava o validador bloqueante _v10_internal_validation.   ║
║  Essa delegação está DESATIVADA: main() agora só coleta dados, avisa e sai   ║
║  com código 2. Para gerar apresentação, use o entrypoint acima.              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Orquestra todo o fluxo:
1. Busca pacientes novos no Quarkclinic para uma data/turno
2. Para cada paciente:
   a. Busca exames no Google Drive
   b. Busca respostas dos questionários
   c. Extrai e classifica dados dos PDFs de exames
   d. Gera apresentação HTML
   e. Loga pacientes com informações pendentes

Uso:
    python3 gerar_apresentacao.py <data_dd-MM-yyyy> <turno>

    turno: manha | tarde
"""

import sys
import os
import json
import time
import subprocess
import re
import html as html_lib
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Verificar se o cron está desabilitado
DISABLED_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".disabled")
if os.path.exists(DISABLED_FILE):
    with open(DISABLED_FILE, "r") as f:
        print(f"[BLOQUEADO] Cron de apresentação desabilitado: {f.read().strip()}")
    sys.exit(0)

# Diretório base da skill
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")
DELIVERABLES_DIR = "/root/cerebro-vital-slim/deliverables"


def run_script(script_name, *args):
    """Executa um script auxiliar e retorna o JSON parseado."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    cmd = ["python3", script_path] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERRO ao executar {script_name}: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"ERRO: resposta inválida de {script_name}: {result.stdout[:200]}", file=sys.stderr)
        return None


def calcular_idade(data_nascimento_ms):
    """Calcula idade a partir do timestamp em milissegundos."""
    if not data_nascimento_ms:
        return None
    try:
        nasc = datetime.fromtimestamp(data_nascimento_ms / 1000)
        hoje = datetime.now()
        idade = hoje.year - nasc.year
        if (hoje.month, hoje.day) < (nasc.month, nasc.day):
            idade -= 1
        return idade
    except (ValueError, OverflowError):
        return None


def calcular_imc(peso_str, altura_str):
    """Calcula IMC a partir de peso (kg) e altura (cm)."""
    try:
        peso = float(str(peso_str).replace(",", "."))
        altura_cm = float(str(altura_str).replace(",", "."))
        altura_m = altura_cm / 100
        return round(peso / (altura_m ** 2), 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def classificar_imc(imc):
    """Retorna label e class CSS para o IMC."""
    if imc is None:
        return "—", ""
    if imc < 18.5:
        return "Abaixo do peso", "tag-attn"
    if imc < 25.0:
        return "Normal", "tag-optimal"
    if imc < 30.0:
        return "Sobrepeso", "tag-attn"
    if imc < 35.0:
        return "Obesidade I", "tag-alert"
    if imc < 40.0:
        return "Obesidade II", "tag-alert"
    return "Obesidade III", "tag-crit"


# ---------------------------------------------------------------------------
# Geração de seções HTML
# ---------------------------------------------------------------------------

def gerar_stats_section(exames_parsed=None):
    """
    Gera os 4 hero alert cards com os achados mais relevantes.
    """
    if not exames_parsed or not exames_parsed.get("hero_alerts"):
        return "<!-- stats_section: aguardando exames -->"

    hero_alerts = exames_parsed["hero_alerts"]
    if not hero_alerts:
        # Sem alterações — mostra mensagem positiva
        stats = exames_parsed.get("stats", {})
        return f"""<section class="hero-alerts" aria-label="Destaques dos exames">
  <div class="wrap">
    <div class="hero-alerts intro">
      <h2>Exames analisados</h2>
      <p>{stats.get("total", 0)} parâmetros avaliados · <strong style="color:var(--sev-ok)">{stats.get("normais", 0)} dentro da referência</strong></p>
    </div>
  </div>
</section>"""

    severity_label = {"crit": "CRÍTICO", "alert": "ATENÇÃO", "attn": "MONITORAR", "baixo": "BAIXO", "normal": "NORMAL"}

    cards = []
    for alert in hero_alerts:
        sev = alert.get("status", "alert")
        sev_class = "crit" if sev == "crit" else ("attn" if sev == "attn" else "alert")
        label = severity_label.get(sev, "ATENÇÃO")
        unidade_html = f'<span style="font-size:0.4em;font-weight:400;color:var(--ink-dim);margin-left:6px;">{alert["unidade"]}</span>' if alert.get("unidade") else ""
        ref_html = f'<div class="alert-ref">Ref: {alert["referencia"]}</div>' if alert.get("referencia") else ""

        cards.append(f"""    <article class="alert-card {sev_class}" role="listitem" aria-labelledby="a-{alert["nome"].replace(" ", "-").lower()}-name">
      <span class="alert-label">{label}</span>
      <div class="alert-name" id="a-{alert["nome"].replace(" ", "-").lower()}-name">{alert["nome"]}</div>
      <div class="hero-number">{alert["valor"]}{unidade_html}</div>
      {ref_html}
      <p class="alert-explain">{alert["explicacao"]}</p>
    </article>""")

    cards_html = "\n".join(cards)
    stats = exames_parsed.get("stats", {})
    return f"""<section class="hero-alerts" aria-label="Principais achados">
  <div class="hero-alerts intro">
    <h2>Principais achados</h2>
    <p>{stats.get("total", 0)} parâmetros · <strong>{stats.get("criticos", 0) + stats.get("alertas", 0)}</strong> fora da referência · {stats.get("normais", 0)} normais</p>
  </div>
  <div class="alert-grid" role="list">
{cards_html}
  </div>
</section>"""


def gerar_exams_section(exames_parsed=None):
    """
    Gera a seção de tabela de exames agrupados por categoria.
    """
    if not exames_parsed or not exames_parsed.get("grupos"):
        return "<!-- exams_section: aguardando extração dos PDFs de exames -->"

    grupos = exames_parsed["grupos"]
    if not grupos:
        return "<!-- exams_section: nenhum exame identificado nos PDFs -->"

    html_partes = []
    for grupo in grupos:
        exames = grupo.get("exames", [])
        if not exames:
            continue

        rows = []
        for ex in exames:
            altered_class = " altered" if ex["alterado"] else ""
            unidade_html = f'<span class="unit">{ex["unidade"]}</span>' if ex.get("unidade") else ""
            ref_html = f'<span class="exam-ref">Ref: {ex["referencia"]}</span>' if ex.get("referencia") else ""
            rows.append(f"""  <div class="exam-row{altered_class}">
    <div><span class="exam-name">{ex["nome"]}</span><br>{ref_html}</div>
    <div class="exam-value">{ex["valor"]}{unidade_html}</div>
    <span class="exam-tag {ex["tag_class"]}">{ex["tag_label"]}</span>
  </div>""")

        rows_html = "\n".join(rows)
        hint_html = f'<span class="hint">{grupo["hint"]}</span>' if grupo.get("hint") else ""
        html_partes.append(f"""<div class="exam-group">
  <div class="exam-group-head"><h4>{grupo["nome"]}</h4>{hint_html}</div>
{rows_html}
</div>""")

    return "\n\n".join(html_partes)


def gerar_diagnostico_section(exames_parsed=None, questionarios=None):
    """
    Gera interpretação clínica baseada nos achados alterados.
    """
    if not exames_parsed or not exames_parsed.get("grupos"):
        return "<!-- diagnostico_section: aguardando exames -->"

    # Coleta todos os exames alterados
    alterados = []
    for grupo in exames_parsed.get("grupos", []):
        for ex in grupo.get("exames", []):
            if ex.get("alterado"):
                alterados.append(ex)

    if not alterados:
        return """<section class="implications" aria-labelledby="impl-title">
  <div class="wrap">
    <h2 id="impl-title">Interpretação clínica</h2>
    <p class="lead">Exames dentro dos parâmetros de referência. Ótimo ponto de partida para otimização metabólica.</p>
  </div>
</section>"""

    # Monta texto de interpretação por sistema
    por_grupo = {}
    for ex in alterados:
        g = ex["grupo"]
        if g not in por_grupo:
            por_grupo[g] = []
        direcao = "elevado" if ex["status"] in ("alert", "crit") else "baixo"
        por_grupo[g].append(f"{ex['nome']} {direcao} ({ex['valor']} {ex['unidade']})")

    group_labels = {
        "metabolico": "Metabolismo glicêmico",
        "lipidico": "Perfil lipídico",
        "hormonal": "Eixo hormonal",
        "hepatico": "Função hepática",
        "renal": "Função renal",
        "hemograma": "Sangue",
        "vitaminas": "Micronutrientes",
        "inflamacao": "Inflamação",
        "autoimune": "Autoimunidade",
        "oncologico": "Marcadores oncológicos",
        "outros": "Outros",
    }

    cards = []
    for grupo_key, items in por_grupo.items():
        titulo = group_labels.get(grupo_key, grupo_key.capitalize())
        itens_html = "".join(f"<li>{item}</li>" for item in items)
        cards.append(f"""      <div class="imp-card">
        <h3>{titulo}</h3>
        <ul style="padding-left:1.2em;color:var(--ink-soft);font-size:14px;line-height:1.7">{itens_html}</ul>
      </div>""")

    cards_html = "\n".join(cards)

    # Dados do paciente para contextualizar
    dados_q = questionarios.get("pre-consulta", {}).get("dados", {}) if questionarios else {}
    peso = dados_q.get("pesoAtual", "")
    altura = dados_q.get("altura", "")
    imc = calcular_imc(peso, altura)
    imc_label, _ = classificar_imc(imc)
    contexto_imc = f" (IMC {imc} kg/m² — {imc_label})" if imc else ""

    return f"""<section class="implications" aria-labelledby="impl-title">
  <div class="wrap">
    <h2 id="impl-title">Interpretação clínica</h2>
    <p class="lead">{len(alterados)} parâmetro(s) fora da referência{contexto_imc}. Cada achado informa o plano individual.</p>
    <div class="imp-grid">
{cards_html}
    </div>
  </div>
</section>"""


def gerar_anchor_section():
    """Gera seção anchor com link para a Dra."""
    return """<section class="anchor" aria-labelledby="anchor-title">
  <div class="wrap">
    <h2 id="anchor-title">Sua médica</h2>
    <div class="anchor-card">
      <div class="anchor-info">
        <h3>Dra. Daniely Alves Freitas</h3>
        <p class="anchor-role">Médica especialista em emagrecimento e saúde metabólica</p>
        <p class="anchor-crm">CRM-BA 27.588</p>
      </div>
      <p class="anchor-text">Cada paciente recebe um plano individual construído a partir dos próprios exames, histórico e objetivos. Nada de protocolo genérico.</p>
    </div>
  </div>
</section>"""


def gerar_history_section(questionarios=None):
    """Gera seção de histórico a partir dos questionários."""
    if not questionarios:
        return "<!-- history_section: preencher com dados do questionário -->"

    pre = questionarios.get("pre-consulta", {})
    if not pre.get("encontrado"):
        return "<!-- history_section: questionário não encontrado -->"

    dados = pre.get("dados", {})
    if not dados:
        return "<!-- history_section: dados do questionário vazios -->"

    def val(campo, fallback="—"):
        v = dados.get(campo)
        if not v or str(v).strip() == "" or str(v).lower() in ("nenhum", "nenhuma", "nao", "não"):
            return fallback
        return str(v)

    # Calcula IMC se possível
    imc = calcular_imc(val("pesoAtual", ""), val("altura", ""))
    imc_label, imc_class = classificar_imc(imc)
    imc_html = f'<p><strong>IMC:</strong> {imc} kg/m² <span style="font-size:12px;color:var(--ink-dim)">({imc_label})</span></p>' if imc else ""

    linhas = []
    linhas.append('<section class="history" aria-labelledby="hist-title">')
    linhas.append('  <div class="wrap">')
    linhas.append('    <h2 id="hist-title">O que nos contou</h2>')
    linhas.append('    <div class="hist-grid">')

    # Card 1: Perfil
    linhas.append('      <div class="hist-card">')
    linhas.append('        <h3>Perfil</h3>')
    linhas.append(f'        <p><strong>Altura:</strong> {val("altura")} cm</p>')
    linhas.append(f'        <p><strong>Peso atual:</strong> {val("pesoAtual")} kg</p>')
    linhas.append(f'        <p><strong>Peso ideal:</strong> {val("pesoIdeal")} kg</p>')
    linhas.append(f'        <p><strong>Maior peso:</strong> {val("pesoMaximoAnterior")} kg</p>')
    if imc_html:
        linhas.append(f'        {imc_html}')
    linhas.append('      </div>')

    # Card 2: Rotina
    linhas.append('      <div class="hist-card">')
    linhas.append('        <h3>Rotina</h3>')
    linhas.append(f'        <p><strong>Atividade:</strong> {val("atividadeFisica")} ({val("frequenciaAtividade")})</p>')
    linhas.append(f'        <p><strong>Sono:</strong> {val("horasSono")}h (nota {val("qualidadeSono")}/10)</p>')
    linhas.append(f'        <p><strong>Energia:</strong> {val("nivelEnergia")}/10</p>')
    linhas.append(f'        <p><strong>Água:</strong> {val("consumoAgua")}</p>')
    linhas.append(f'        <p><strong>Reposição hormonal:</strong> {val("reposicaoHormonal")}</p>')
    linhas.append('      </div>')

    # Card 3: Alimentação
    linhas.append('      <div class="hist-card">')
    linhas.append('        <h3>Alimentação</h3>')
    linhas.append(f'        <p><strong>Refeições:</strong> {val("refeicoesDia")}/dia</p>')
    linhas.append(f'        <p><strong>Café da manhã:</strong> {val("cafeDaManha")}</p>')
    linhas.append(f'        <p><strong>Almoço:</strong> {val("almoco")}</p>')
    linhas.append(f'        <p><strong>Jantar:</strong> {val("jantar")}</p>')
    linhas.append(f'        <p><strong>Doces:</strong> {val("consumoDoces")}</p>')
    linhas.append(f'        <p><strong>Álcool:</strong> {val("consumoAlcool")}</p>')
    linhas.append('      </div>')

    # Card 4: Jornada (SPIN)
    linhas.append('      <div class="hist-card">')
    linhas.append('        <h3>Jornada</h3>')
    linhas.append(f'        <p><strong>Tempo de luta:</strong> {val("spin_s_tempoLuta")}</p>')
    linhas.append(f'        <p><strong>Já tentou:</strong> {val("spin_s_tentativas")}</p>')
    linhas.append(f'        <p><strong>Principal incômodo:</strong> {val("spin_p_principalIncomodo")}</p>')
    linhas.append(f'        <p><strong>Impacto na vida:</strong> {val("spin_i_impactoVida")}</p>')
    linhas.append(f'        <p><strong>Vida resolvida seria:</strong> {val("spin_n_vidaResolvida")}</p>')
    linhas.append('      </div>')

    linhas.append('    </div>')
    linhas.append('  </div>')
    linhas.append('</section>')

    return "\n".join(linhas)


def gerar_contexto_section(questionarios=None):
    """Gera seção de contexto do paciente."""
    if not questionarios:
        return "<!-- contexto_section: preencher com dados do questionário -->"

    pre = questionarios.get("pre-consulta", {})
    if not pre.get("encontrado"):
        return "<!-- contexto_section: questionário não encontrado -->"

    dados = pre.get("dados", {})

    def val(campo, fallback="—"):
        v = dados.get(campo)
        if not v or str(v).strip() == "" or str(v).lower() in ("nenhum", "nenhuma", "nao", "não"):
            return fallback
        return str(v)

    panels = []

    # Panel 1: Histórico e objetivos
    panels.append(f"""      <div class="ctx-panel">
        <h3>Histórico e objetivos</h3>
        <dl>
          <dt>Objetivo</dt><dd>{val("spin_n_vidaResolvida", val("tresObjetivos", "Não informado"))}</dd>
          <dt>Peso atual</dt><dd>{val("pesoAtual")} kg</dd>
          <dt>Peso desejado</dt><dd>{val("pesoIdeal")} kg</dd>
          <dt>Altura</dt><dd>{val("altura")} cm</dd>
          <dt>Medicamentos</dt><dd>{val("medicamentosAtuais")}</dd>
          <dt>Condições</dt><dd>{val("doencasCronicas")}</dd>
          <dt>Atividade física</dt><dd>{val("atividadeFisica")} ({val("frequenciaAtividade")})</dd>
          <dt>Perfil DISC</dt><dd>{val("discPerfil")}</dd>
          <dt>Perfil financeiro</dt><dd>{val("perfilFinanceiro")}</dd>
        </dl>
      </div>""")

    # Panel 2: Hábitos alimentares
    panels.append(f"""      <div class="ctx-panel">
        <h3>Hábitos alimentares</h3>
        <dl>
          <dt>Refeições / dia</dt><dd>{val("refeicoesDia")}</dd>
          <dt>Café da manhã</dt><dd>{val("cafeDaManha")}</dd>
          <dt>Almoço</dt><dd>{val("almoco")}</dd>
          <dt>Jantar</dt><dd>{val("jantar")}</dd>
          <dt>Água</dt><dd>{val("consumoAgua")}</dd>
          <dt>Álcool</dt><dd>{val("consumoAlcool")}</dd>
          <dt>Doces</dt><dd>{val("consumoDoces")}</dd>
          <dt>Intestino</dt><dd>{val("frequenciaIntestinal")}</dd>
        </dl>
      </div>""")

    panels_html = "\n".join(panels)
    return f"""<section class="contexto" aria-labelledby="ctx-title">
  <div class="wrap">
    <h2 id="ctx-title">Contexto do paciente</h2>
    <div class="ctx-grid">
{panels_html}
    </div>
  </div>
</section>"""


def gerar_timeline_section():
    """Gera seção de timeline padrão de 180 dias."""
    return """<section class="timeline" aria-labelledby="time-title">
  <div class="wrap">
    <h2 id="time-title">O que esperar em 180 dias</h2>
    <ul class="time-list">
      <li><strong>Mês 1 — Diagnóstico e ajuste:</strong> Plano alimentar personalizado, suplementação de base e primeiros ajustes de estilo de vida.</li>
      <li><strong>Mês 2 — Reversão:</strong> Sensibilidade insulínica começa a melhorar, energia sobe, sono fica mais reparador.</li>
      <li><strong>Mês 3 — Consolidação:</strong> Peso em queda sustentável, exames mostrando melhora objetiva.</li>
      <li><strong>Mês 4–6 — Otimização:</strong> Ajustes finos baseados em novos exames. Resultado sustentável a longo prazo.</li>
    </ul>
  </div>
</section>"""


def gerar_references_section():
    """Gera seção de referências bibliográficas padrão."""
    return """<section class="references" aria-labelledby="ref-title">
  <div class="wrap">
    <h2 id="ref-title">Referências</h2>
    <ul class="ref-list">
      <li>American Diabetes Association. Standards of Care in Diabetes—2024. <em>Diabetes Care</em>.</li>
      <li>Holick MF. Vitamin D deficiency. <em>N Engl J Med</em>. 2007;357(3):266-81.</li>
      <li>DeFronzo RA. Insulin resistance, lipotoxicity, type 2 diabetes and atherosclerosis. <em>Diabetologia</em>. 2010.</li>
    </ul>
  </div>
</section>"""


# ---------------------------------------------------------------------------
# Extração de exames dos PDFs
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Pipeline LLM-based: PDF → LLM extrai → Validador classifica → formato legacy
# ---------------------------------------------------------------------------

def extrair_todos_exames_llm(lista_pdfs, paciente):
    """
    Extrai exames via LLM (gpt-4o) + validador multi-layer (sex+age aware).

    REGRA CANÔNICA RC-01: paciente DEVE conter 'sexo' (M ou F).
    A idade é calculada de paciente['dataNascimento'] se não fornecida.

    Args:
        lista_pdfs: lista de dicts {id, nome} do Drive
        paciente: dict com nome, sexo, dataNascimento

    Returns:
        dict legacy {grupos, hero_alerts, stats, _audit} para gerar_html_apresentacao
    """
    if not lista_pdfs:
        return None

    # Idade
    idade = paciente.get("idade") or calcular_idade(paciente.get("dataNascimento"))
    sexo = str(paciente.get("sexo", "")).upper()[:1]

    todos_grupos = {}
    todos_hero = []
    stats_total = {"total": 0, "criticos": 0, "alertas": 0, "atencao": 0, "normais": 0}
    audit = {
        "paciente_nome": paciente.get("nome", ""),
        "sexo": sexo,
        "idade": idade,
        "pdfs_processados": [],
        "exames_validados": 0,
        "exames_revisao_manual": [],
        "cross_check_warnings": [],
    }

    for pdf in lista_pdfs:
        pdf_id = pdf.get("id")
        pdf_nome = pdf.get("nome", "exame.pdf")
        if not pdf_id:
            continue

        # Baixa PDF do Drive para arquivo temporário
        with tempfile.TemporaryDirectory() as tmpdir:
            local_pdf = os.path.join(tmpdir, pdf_nome)
            print(f"  [LLM] Baixando {pdf_nome}...", file=sys.stderr)
            try:
                ok = _baixar_pdf_drive(pdf_id, local_pdf)
            except Exception as e:
                print(f"  [LLM] Erro download: {e}", file=sys.stderr)
                continue
            if not ok or not os.path.exists(local_pdf):
                print(f"  [LLM] Falha download {pdf_nome}", file=sys.stderr)
                continue

            # LLM extrai
            print(f"  [LLM] Extraindo via gpt-4o (sexo={sexo}, idade={idade})...", file=sys.stderr)
            extracao = extrair_exames_via_llm(local_pdf, paciente_meta={"sexo": sexo, "idade": idade})
            if "erro" in extracao:
                print(f"  [LLM] Erro extração: {extracao['erro']}", file=sys.stderr)
                continue

            print(f"  [LLM] {len(extracao.get('exames', []))} exames extraídos", file=sys.stderr)

            # Validador classifica usando refs canônicas (sex+age) + L10 anti-alucinação
            texto_pdf = extracao.get("_texto_pdf", "")
            val = validar_exames(extracao, {"sexo": sexo, "idade": idade}, texto_pdf=texto_pdf)
            print(f"  [LLM] {len(val['validados'])} validados / {len(val['revisao_manual'])} revisão manual",
                  file=sys.stderr)

            # RC-25 operacional — auditoria determinística de tireoide.
            # Padrão TSH suprimido + T3L/T4L altos muda decisão clínica e não pode depender só do LLM.
            def _brfloat_local(x):
                return float(str(x).replace('.', '').replace(',', '.'))
            def _ensure_validado(nome, valor, unidade, rmin, rmax, grupo='tireoide', status='crit', nome_laudo=None):
                if any(e.get('nome_canonico') == nome for e in val.get('validados', [])):
                    return
                val.setdefault('validados', []).append({
                    'nome_canonico': nome,
                    'nome_no_laudo': nome_laudo or nome,
                    'valor_f': float(valor),
                    'unidade': unidade,
                    'unidade_canonica': unidade,
                    'ref_min_final': rmin,
                    'ref_max_final': rmax,
                    'grupo': grupo,
                    'status_final': status,
                    'observacao': 'Inserido por auditoria determinística de eixo tireoidiano no texto do PDF.',
                })
                audit.setdefault('cross_check_warnings', []).append(f"Auditoria determinística inseriu {nome}={valor}{unidade}")
            m_t3l = re.search(r'T3-\s*TRIIODOTIRONINA\s+LIVRE[^:]*:\s*([0-9.,]+)\s*pg/mL', texto_pdf, re.I)
            if m_t3l:
                _ensure_validado('T3 Livre', _brfloat_local(m_t3l.group(1)), 'pg/mL', 2.3, 4.2, nome_laudo='T3- TRIIODOTIRONINA LIVRE')
            m_t4l = re.search(r'TIROXINA\s+LIVRE\s*-\s*T4\s+LIVRE[^:]*:\s*([0-9.,]+)\s*ng/dL', texto_pdf, re.I)
            if m_t4l:
                _ensure_validado('T4 Livre', _brfloat_local(m_t4l.group(1)), 'ng/dL', 0.89, 1.61, nome_laudo='TIROXINA LIVRE - T4 LIVRE')
            m_tsh = re.search(r'TSH-HORM[ÔO]NIO\s+TIREOESTIMULANTE[^:]*:\s*([0-9.,]+)\s*microUI/mL', texto_pdf, re.I)
            if m_tsh:
                _ensure_validado('TSH', _brfloat_local(m_tsh.group(1)), 'microUI/mL', 0.27, 4.2, nome_laudo='TSH-HORMÔNIO TIREOESTIMULANTE')

            # RC-25 operacional — auditoria determinística de metabolismo do ferro.
            m_ferr = re.search(r'FERRITINA[\s\S]{0,220}?Resultado:\s*([0-9.,]+)\s*ng/mL', texto_pdf, re.I)
            if m_ferr:
                _ensure_validado('Ferritina', _brfloat_local(m_ferr.group(1)), 'ng/mL', 30, 400, grupo='vitaminas', nome_laudo='FERRITINA')
            m_ferro = re.search(r'\bFERRO[.\s]*:\s*([0-9.,]+)\s*[µu]?g/dL', texto_pdf, re.I)
            if m_ferro:
                _ensure_validado('Ferro', _brfloat_local(m_ferro.group(1)), 'µg/dL', 65, 175, grupo='vitaminas', nome_laudo='FERRO')
            m_sat = re.search(r'Indice\s+de\s+Saturacao\s+da\s+Transferrina[^0-9]{0,120}([0-9.,]+)\s*%', texto_pdf, re.I)
            if m_sat:
                _ensure_validado('Índice de Saturação da Transferrina', _brfloat_local(m_sat.group(1)), '%', 20, 50, grupo='vitaminas', nome_laudo='Índice de Saturação da Transferrina')
            m_clf = re.search(r'Capacidade de Fixacao Latente do Ferro:\s*([0-9.,]+)\s*[µu]?g/dL', texto_pdf, re.I)
            if m_clf:
                _ensure_validado('Capacidade de Fixação Latente do Ferro', _brfloat_local(m_clf.group(1)), 'µg/dL', 120, 450, grupo='vitaminas', status='low', nome_laudo='Capacidade de Fixação Latente do Ferro')

            # PCR-us: alguns laboratórios reportam mg/dL; canônica IVS usa mg/L. Converter x10 para não perder o exame.
            m_pcr = re.search(r'PROTE[ÍI]NA\s+C\s+REATIVA\s+ULTRA\s+SENS[IÍ]VEL[^:]{0,120}:\s*([0-9.,]+)\s*(mg/dL|mg/L)', texto_pdf, re.I)
            if not m_pcr:
                m_pcr = re.search(r'Prote[ií]na\s+C\s+Reativa\s+Ultra\s+Sens[ií]vel[\s\S]{0,220}?([0-9.,]+)\s*(mg/dL|mg/L)', texto_pdf, re.I)
            if m_pcr:
                pcr = _brfloat_local(m_pcr.group(1))
                unit = m_pcr.group(2).lower()
                if unit == 'mg/dl':
                    pcr = pcr * 10
                _ensure_validado('PCR-us', pcr, 'mg/L', None, 3.0, grupo='inflamatorio', status='alert' if pcr > 3 else 'normal', nome_laudo='PROTEÍNA C REATIVA ULTRA SENSÍVEL')

            # SHBG e cortisol às vezes aparecem em layout vertical e o LLM pode omitir.
            m_shbg = re.search(r'SHBG\s*\(Globulina\s+Transportadora\s+de[\s\S]{0,120}?([0-9.,]+)\s*nmol/L', texto_pdf, re.I)
            if m_shbg:
                shbg = _brfloat_local(m_shbg.group(1))
                _ensure_validado('SHBG', shbg, 'nmol/L', 27.1, 128.0, grupo='hormonal', status='low' if shbg < 27.1 else ('alert' if shbg > 128.0 else 'normal'), nome_laudo='SHBG')

            m_cort = re.search(r'RESULTADO\s*([0-9.,]+)\s*µg/dL[\s\S]{0,80}?Cortisol', texto_pdf, re.I)
            if not m_cort:
                m_cort = re.search(r'R\s*E\s*S\s*U\s*LTA\s*D\s*O[\s\S]{0,50}?([0-9.,]+)\s*µg/dL[\s\S]{0,100}?Cortisol', texto_pdf, re.I)
            if not m_cort:
                m_cort = re.search(r'([0-9.,]+)\s*µg/dL\s*\n\s*Cortisol', texto_pdf, re.I)
            if m_cort:
                cort = _brfloat_local(m_cort.group(1))
                _ensure_validado('Cortisol', cort, 'µg/dL', 6.2, 18.0, grupo='adrenal', status='normal' if 6.2 <= cort <= 18.0 else 'alert', nome_laudo='Cortisol')

            # Minerais/eixo ósseo que às vezes o LLM omite quando estão normais — ainda precisam aparecer na cobertura total.
            m_ca = re.search(r'C[ÁA]LCIO[^:]{0,80}:\s*([0-9.,]+)\s*mg/dL', texto_pdf, re.I)
            if m_ca:
                ca = _brfloat_local(m_ca.group(1))
                _ensure_validado('Cálcio', ca, 'mg/dL', 8.6, 10.2, grupo='vitaminas', status='normal' if 8.6 <= ca <= 10.2 else 'alert', nome_laudo='CÁLCIO')
            m_na = re.search(r'S[ÓO]DIO[^:]{0,80}:\s*([0-9.,]+)\s*mEq/L', texto_pdf, re.I)
            if m_na:
                na = _brfloat_local(m_na.group(1))
                _ensure_validado('Sódio', na, 'mEq/L', 136, 145, grupo='vitaminas', status='normal' if 136 <= na <= 145 else 'alert', nome_laudo='SODIO')
            m_pth = re.search(r'PARATORM[ÔO]NIO\s*\(PTH\)[^:]{0,80}:\s*([0-9.,]+)\s*pg/mL', texto_pdf, re.I)
            if m_pth:
                pth = _brfloat_local(m_pth.group(1))
                _ensure_validado('PTH', pth, 'pg/mL', 18.5, 88.0, grupo='vitaminas', status='normal' if 18.5 <= pth <= 88.0 else 'alert', nome_laudo='PARATORMÔNIO (PTH)')

            # Glicídico/anabólico omitidos às vezes pelo LLM.
            m_ins = re.search(r'\bINSULINA\b[^:]{0,80}:\s*([0-9.,]+)\s*(?:microUI/mL|mU/mL)', texto_pdf, re.I)
            if m_ins:
                ins = _brfloat_local(m_ins.group(1))
                _ensure_validado('Insulina', ins, 'mU/mL', 2.6, 24.9, grupo='glicidico', status='normal' if 2.6 <= ins <= 24.9 else 'alert', nome_laudo='INSULINA')
            m_igf = re.search(r'SOMATOMEDINA\s+C\s*\(IGF-1\)[^:]{0,80}:\s*([0-9.,]+)\s*ng/mL', texto_pdf, re.I)
            if m_igf:
                igf = _brfloat_local(m_igf.group(1))
                _ensure_validado('IGF-1', igf, 'ng/mL', 100, 303, grupo='adrenal', status='low' if igf < 100 else ('alert' if igf > 303 else 'normal'), nome_laudo='SOMATOMEDINA C (IGF-1)')
            m_zinco = re.search(r'ZINCO\s+S[ÉE]RICO[^:]{0,80}:\s*([0-9.,]+)\s*(?:mcg/dL|µg/dL)', texto_pdf, re.I)
            if m_zinco:
                zinco = _brfloat_local(m_zinco.group(1))
                _ensure_validado('Zinco', zinco, 'mcg/dL', 60, 120, grupo='vitaminas', status='alert' if zinco > 120 else ('low' if zinco < 60 else 'normal'), nome_laudo='ZINCO SÉRICO')
            m_homo = re.search(r'HOMOCISTE[IÍ]NA[^:]{0,80}:\s*([0-9.,]+)\s*(?:micromol/L|µmol/L|umol/L)', texto_pdf, re.I)
            if m_homo:
                homo = _brfloat_local(m_homo.group(1))
                _ensure_validado('Homocisteína', homo, 'micromol/L', 5, 10, grupo='inflamatorio', status='alert' if homo > 10 else ('low' if homo < 5 else 'normal'), nome_laudo='HOMOCISTEINA')

            # RC-25 operacional — cobertura determinística hormonal/metabólica para laudos DASA/NAM.
            # Alguns laudos posicionam o RESULTADO antes/depois do nome ou usam "Inferior a"; o LLM pode truncar
            # páginas finais. Se o exame suportado está literalmente no PDF, ele não pode sumir da apresentação.
            def _status_from_range(v, rmin=None, rmax=None):
                if rmin is not None and v < rmin:
                    return 'low'
                if rmax is not None and v > rmax:
                    return 'alert'
                return 'normal'

            def _num_after(label_pat, unit_pat, window=220):
                m = re.search(label_pat + r'[\s\S]{0,' + str(window) + r'}?([0-9]+(?:[,.][0-9]+)?)\s*' + unit_pat, texto_pdf, re.I)
                return _brfloat_local(m.group(1)) if m else None

            def _num_before(label_pat, unit_pat, window=180):
                m = re.search(r'([0-9]+(?:[,.][0-9]+)?)\s*' + unit_pat + r'[\s\S]{0,' + str(window) + r'}?' + label_pat, texto_pdf, re.I)
                return _brfloat_local(m.group(1)) if m else None

            def _inferior_after(label_pat, unit_pat, window=180):
                m = re.search(label_pat + r'[\s\S]{0,' + str(window) + r'}?Inferior\s+a\s*([0-9]+(?:[,.][0-9]+)?)\s*' + unit_pat, texto_pdf, re.I)
                return _brfloat_local(m.group(1)) if m else None

            # Eixo tireoidiano em layout NAM sem prefixo "TSH-".
            tsh_alt = _num_after(r'Horm[ôo]nio\s+Tireoestimulante', r'(?:µUI/mL|uUI/mL|microUI/mL)')
            if tsh_alt is not None:
                _ensure_validado('TSH', tsh_alt, 'uUI/mL', 0.27, 4.2, grupo='tireoide', status=_status_from_range(tsh_alt, 0.27, 4.2), nome_laudo='Hormônio Tireoestimulante')
            t4_alt = _num_after(r'Tiroxina\s+Livre\s*\(T4\s+Livre\)', r'ng/dL')
            if t4_alt is not None:
                _ensure_validado('T4 Livre', t4_alt, 'ng/dL', 0.85, 1.86, grupo='tireoide', status=_status_from_range(t4_alt, 0.85, 1.86), nome_laudo='Tiroxina Livre (T4 Livre)')
            t3_total = _num_after(r'T3\s*\(Triiodotironina\)', r'ng/dL')
            if t3_total is not None:
                _ensure_validado('T3 Total', t3_total, 'ng/dL', 60, 200, grupo='tireoide', status=_status_from_range(t3_total, 60, 200), nome_laudo='T3 (Triiodotironina)')

            # Eixo hormonal feminino / androgênico.
            estr = _inferior_after(r'Estradiol\b', r'pg/mL') or _num_after(r'Estradiol\b', r'pg/mL')
            if estr is not None:
                # Para mulher pós-menopausa, faixa conservadora IVS no refs_canonicas é até 32 pg/mL.
                _ensure_validado('Estradiol', estr, 'pg/mL', None, 32 if sexo == 'F' and idade and idade >= 51 else 350, grupo='hormonal', status=_status_from_range(estr, None, 32 if sexo == 'F' and idade and idade >= 51 else 350), nome_laudo='Estradiol')
            fsh = _num_after(r'FSH\s*-\s*Horm[ôo]nio\s+Fol[ií]culo', r'mUI/mL')
            if fsh is not None:
                rmin, rmax = (25.8, 134.8) if sexo == 'F' and idade and idade >= 51 else (3.5, 12.5)
                _ensure_validado('FSH', fsh, 'mUI/mL', rmin, rmax, grupo='hormonal', status=_status_from_range(fsh, rmin, rmax), nome_laudo='FSH - Hormônio Folículo Estimulante')
            lh = _num_after(r'Horm[ôo]nio\s+Luteinizante\s*\(LH\)', r'mUI/mL')
            if lh is not None:
                rmin, rmax = (7.7, 58.5) if sexo == 'F' and idade and idade >= 51 else (2.4, 12.6)
                _ensure_validado('LH', lh, 'mUI/mL', rmin, rmax, grupo='hormonal', status=_status_from_range(lh, rmin, rmax), nome_laudo='Hormônio Luteinizante (LH)')
            prol = _num_after(r'Prolactina\b', r'ng/mL')
            if prol is not None:
                rmin, rmax = (4.79, 23.3) if sexo == 'F' else (4.04, 15.2)
                _ensure_validado('Prolactina', prol, 'ng/mL', rmin, rmax, grupo='hormonal', status=_status_from_range(prol, rmin, rmax), nome_laudo='Prolactina')
            testo_total = _num_after(r'Testosterona\s+Total\b', r'ng/dL')
            if testo_total is not None:
                rmin, rmax = (5, 50) if sexo == 'F' and idade and idade >= 51 else ((15, 70) if sexo == 'F' else (400, 700))
                _ensure_validado('Testosterona Total', testo_total, 'ng/dL', rmin, rmax, grupo='hormonal', status=_status_from_range(testo_total, rmin, rmax), nome_laudo='Testosterona Total')
            testo_livre = _num_after(r'Testosterona\s+Livre\s+Calculada\b', r'ng/dL')
            if testo_livre is not None:
                _ensure_validado('Testosterona Livre', testo_livre, 'ng/dL', 0.19 if sexo == 'F' and idade and idade >= 51 else None, 2.06 if sexo == 'F' and idade and idade >= 51 else None, grupo='hormonal', status=_status_from_range(testo_livre, 0.19 if sexo == 'F' and idade and idade >= 51 else None, 2.06 if sexo == 'F' and idade and idade >= 51 else None), nome_laudo='Testosterona Livre Calculada')
            testo_bio = _num_after(r'Testosterona\s+Biodispon[ií]vel\b', r'ng/dL')
            if testo_bio is not None:
                _ensure_validado('Testosterona Biodisponível', testo_bio, 'ng/dL', 4.4 if sexo == 'F' and idade and idade >= 51 else None, 48.0 if sexo == 'F' and idade and idade >= 51 else None, grupo='hormonal', status=_status_from_range(testo_bio, 4.4 if sexo == 'F' and idade and idade >= 51 else None, 48.0 if sexo == 'F' and idade and idade >= 51 else None), nome_laudo='Testosterona Biodisponível')
            prog = (_num_before(r'\bProgesterona\b', r'ng/mL')
                    or _inferior_after(r'\bProgesterona\b', r'ng/mL')
                    or _num_after(r'\bProgesterona\b', r'ng/mL'))
            if prog is not None:
                if sexo == 'M':
                    p_min, p_max = 0, 0.5
                elif idade and idade >= 51:
                    p_min, p_max = None, 0.7
                else:
                    p_min, p_max = 0.1, 25
                _ensure_validado('Progesterona', prog, 'ng/mL', p_min, p_max, grupo='hormonal', status=_status_from_range(prog, p_min, p_max), nome_laudo='Progesterona')

            # Outros marcadores de páginas finais frequentemente omitidos por truncamento do LLM.
            cort = (_num_before(r'\bCortisol\b', r'µg/dL') or _num_after(r'\bCortisol\b', r'µg/dL'))
            if cort is not None:
                _ensure_validado('Cortisol', cort, 'µg/dL', 6.2, 18.0, grupo='adrenal', status=_status_from_range(cort, 6.2, 18.0), nome_laudo='Cortisol')
            igf = _num_after(r'IGF-?1\s*\(Somatomedina\s+C\)', r'ng/mL')
            if igf is not None:
                _ensure_validado('IGF-1', igf, 'ng/mL', 78 if idade and idade >= 51 else 100, 258 if idade and idade >= 51 else 303, grupo='adrenal', status=_status_from_range(igf, 78 if idade and idade >= 51 else 100, 258 if idade and idade >= 51 else 303), nome_laudo='IGF-1 (Somatomedina C)')
            ggt_alt = _num_after(r'Gama-Glutamil\s+Transferase', r'U/L')
            if ggt_alt is not None:
                ggt_max = 38 if sexo == 'F' else 60
                _ensure_validado('GGT', ggt_alt, 'U/L', None, ggt_max, grupo='hepatico', status=_status_from_range(ggt_alt, None, ggt_max), nome_laudo='Gama-Glutamil Transferase')
            ldh = _num_after(r'Desidrogenase\s+L[áa]ctica\s*-\s*LDH', r'UI/L')
            if ldh is not None:
                _ensure_validado('LDH', ldh, 'UI/L', 135, 214, grupo='inflamatorio', status=_status_from_range(ldh, 135, 214), nome_laudo='Desidrogenase Láctica - LDH')
            fibr = _num_after(r'Fibrinog[êe]nio', r'mg/dL')
            if fibr is not None:
                _ensure_validado('Fibrinogênio', fibr, 'mg/dL', 200, 400, grupo='inflamatorio', status=_status_from_range(fibr, 200, 400), nome_laudo='Fibrinogênio')
            apob = _num_after(r'Apolipoprote[íi]na\s+"B"', r'mg/dL')
            if apob is not None:
                _ensure_validado('ApoB', apob, 'mg/dL', None, 100, grupo='lipidico', status=_status_from_range(apob, None, 100), nome_laudo='Apolipoproteína B')
            apoa = _num_after(r'Apolipoprote[íi]na\s+"A"', r'mg/dL')
            if apoa is not None:
                _ensure_validado('ApoA', apoa, 'mg/dL', 76 if sexo == 'F' else 79, 214 if sexo == 'F' else 169, grupo='lipidico', status=_status_from_range(apoa, 76 if sexo == 'F' else 79, 214 if sexo == 'F' else 169), nome_laudo='Apolipoproteína A')

            # RC-25 operacional — cobertura determinística mínima: se um exame suportado aparece no PDF, não pode sumir.
            cobertura_patterns = {
                'Glicose': r'\bGLICOSE\b[^:]{0,80}:\s*[0-9]',
                'HbA1c': r'(HEMOGLOBINA\s+GLICADA|HbA1c)[^:]{0,120}:\s*[0-9]',
                'Insulina': r'\bINSULINA\b[^:]{0,120}:\s*[0-9]',
                'Hemácias': r'HEM[ÁA]CIAS[^:]{0,80}:\s*[0-9]',
                'Hemoglobina': r'\bHEMOGLOBINA\b[^:]{0,80}:\s*[0-9]',
                'Hematócrito': r'HEMAT[ÓO]CRITO[^:]{0,80}:\s*[0-9]',
                'Leucócitos': r'LEUC[ÓO]CITOS[^:]{0,80}:\s*[0-9]',
                'Plaquetas': r'PLAQUETAS[^:]{0,80}:\s*[0-9]',
                'Colesterol Total': r'COLESTEROL\s+TOTAL[^:]{0,80}:\s*[0-9]',
                'HDL': r'\bHDL\b[^:]{0,80}:\s*[0-9]',
                'LDL': r'\bLDL\b[^:]{0,80}:\s*[0-9]',
                'Triglicérides': r'TRIGLIC[ÉE]RIDES[^:]{0,80}:\s*[0-9]',
                'TGO': r'\b(TGO|AST)\b[^:]{0,80}:\s*[0-9]',
                'TGP': r'\b(TGP|ALT)\b[^:]{0,80}:\s*[0-9]',
                'GGT': r'\b(GGT|GAMA\s*GT)\b[^:]{0,80}:\s*[0-9]',
                'Ureia': r'\bUREIA\b[^:]{0,80}:\s*[0-9]',
                'Creatinina': r'CREATININA[^:]{0,80}:\s*[0-9]',
                'Ácido Úrico': r'[ÁA]CIDO\s+[ÚU]RICO[^:]{0,80}:\s*[0-9]',
                'TSH': r'TSH-HORM[ÔO]NIO\s+TIREOESTIMULANTE[^:]*:\s*[0-9]',
                'T4 Livre': r'TIROXINA\s+LIVRE\s*-\s*T4\s+LIVRE[^:]*:\s*[0-9]',
                'T3 Livre': r'T3-\s*TRIIODOTIRONINA\s+LIVRE[^:]*:\s*[0-9]',
                'Testosterona Total': r'TESTOSTERONA\s+TOTAL[^:]{0,120}:\s*[0-9]',
                'Testosterona Livre': r'TESTOSTERONA\s+LIVRE[^:]{0,120}:\s*[0-9]',
                'Estradiol': r'ESTRADIOL[^:]{0,80}:\s*[0-9]',
                'Progesterona': r'PROGESTERONA[^:]{0,80}:\s*[0-9]',
                'FSH': r'\bFSH\b[^:]{0,80}:\s*[0-9]',
                'LH': r'\bLH\b[^:]{0,80}:\s*[0-9]',
                'Prolactina': r'PROLACTINA[^:]{0,80}:\s*[0-9]',
                'SHBG': r'\bSHBG\b[^:]{0,120}:\s*[0-9]',
                'PCR-us': r'PROTE[ÍI]NA\s+C\s+REATIVA\s+ULTRA\s+SENS[IÍ]VEL[^:]{0,120}:\s*[0-9]',
                'Homocisteína': r'HOMOCISTE[ÍI]NA[^:]{0,80}:\s*[0-9]',
                'Vitamina D': r'VITAMINA\s+D[^:]{0,120}:\s*[0-9]',
                'Vitamina B12': r'VITAMINA\s+B12[^:]{0,120}:\s*[0-9]',
                'Ácido Fólico': r'[ÁA]CIDO\s+F[ÓO]LICO[^:]{0,80}:\s*[0-9]',
                'Zinco': r'ZINCO\s+S[ÉE]RICO[^:]{0,80}:\s*[0-9]',
                'Ferro': r'\bFERRO[.\s]*:\s*[0-9]',
                'Ferritina': r'FERRITINA[\s\S]{0,220}?Resultado:\s*[0-9]',
                'Magnésio': r'MAGN[ÉE]SIO[^:]{0,80}:\s*[0-9]',
                'Cálcio': r'C[ÁA]LCIO[^:]{0,80}:\s*[0-9]',
                'Sódio': r'S[ÓO]DIO[^:]{0,80}:\s*[0-9]',
                'Potássio': r'POT[ÁA]SSIO[^:]{0,80}:\s*[0-9]',
                'PTH': r'\bPTH\b[^:]{0,120}:\s*[0-9]',
                'IGF-1': r'\bIGF-?1\b[^:]{0,120}:\s*[0-9]',
                'Índice de Saturação da Transferrina': r'Indice\s+de\s+Saturacao\s+da\s+Transferrina[^0-9]{0,120}[0-9]',
                'Capacidade de Fixação Latente do Ferro': r'Capacidade de Fixacao Latente do Ferro:\s*[0-9]',
            }
            nomes_validados = {e.get('nome_canonico') for e in val.get('validados', [])}
            nomes_revisao = {((r.get('exame') or {}).get('nome_canonico')) for r in val.get('revisao_manual', []) if isinstance(r, dict)}
            detectados_pdf = sorted([nome for nome, pat in cobertura_patterns.items() if re.search(pat, texto_pdf, re.I)])
            faltando_pdf = [nome for nome in detectados_pdf if nome not in nomes_validados]
            if faltando_pdf:
                audit.setdefault('cross_check_warnings', []).append({
                    'tipo': 'cobertura_pdf_bloqueada',
                    'detectados_pdf': detectados_pdf,
                    'faltando_validados': faltando_pdf,
                    'em_revisao_manual': sorted([n for n in faltando_pdf if n in nomes_revisao]),
                })
                raise RuntimeError('VALIDAÇÃO COBERTURA EXAMES BLOQUEOU: exames presentes no PDF não chegaram à estrutura validada: ' + ', '.join(faltando_pdf))

            # Acumula auditoria
            audit["pdfs_processados"].append({
                "nome": pdf_nome,
                "extraidos_pelo_llm": len(extracao.get("exames", [])),
                "validados": len(val["validados"]),
                "lab_origem": extracao.get("lab_origem", ""),
                "data_coleta": extracao.get("data_coleta", ""),
            })
            audit["exames_validados"] += len(val["validados"])
            audit["exames_revisao_manual"].extend(val.get("revisao_manual", []))
            audit["cross_check_warnings"].extend(val.get("cross_check_warnings", []))

            # Converte exames validados para o formato legacy (grupos, hero_alerts, stats)
            for ex in val["validados"]:
                gid = ex.get("grupo", "outros")
                if gid not in todos_grupos:
                    titulo, hint = _GRUPO_TITULOS.get(gid, (gid.capitalize(), ""))
                    todos_grupos[gid] = {"id": gid, "nome": titulo, "hint": hint, "exames": []}

                # Formato legacy do exame
                rmin = ex.get("ref_min_final")
                rmax = ex.get("ref_max_final")
                ref_str = _formatar_ref(rmin, rmax)
                exame_legacy = {
                    "nome": ex["nome_canonico"],
                    "valor": _formatar_num(ex["valor_f"]),
                    "valor_f": ex["valor_f"],
                    "unidade": ex.get("unidade", "") or ex.get("unidade_canonica", ""),
                    "referencia": ref_str,
                    "status": ex["status_final"],
                    "tag_label": ex["status_final"].upper(),
                    "tag_class": ex["status_final"],
                    "alterado": ex["status_final"] != "normal",
                    "grupo": gid,
                }

                # Evita duplicar (mesmo nome canônico, último ganha)
                existente = next((e for e in todos_grupos[gid]["exames"]
                                  if e["nome"] == exame_legacy["nome"]), None)
                if existente:
                    todos_grupos[gid]["exames"].remove(existente)
                todos_grupos[gid]["exames"].append(exame_legacy)

                # Stats
                s = ex["status_final"]
                stats_total["total"] += 1
                if s == "crit":
                    stats_total["criticos"] += 1
                elif s in ("alert", "low"):
                    stats_total["alertas"] += 1
                elif s == "attn":
                    stats_total["atencao"] += 1
                else:
                    stats_total["normais"] += 1

            # Hero alerts: top 4 alterados
            for ex in val["validados"]:
                if ex["status_final"] != "normal":
                    todos_hero.append({
                        "nome": ex["nome_canonico"],
                        "valor": _formatar_num(ex["valor_f"]),
                        "unidade": ex.get("unidade", "") or ex.get("unidade_canonica", ""),
                        "referencia": _formatar_ref(ex.get("ref_min_final"), ex.get("ref_max_final")),
                        "status": ex["status_final"],
                        "tag_label": ex["status_final"].upper(),
                        "tag_class": ex["status_final"],
                    })

    if not todos_grupos:
        return None

    # Ordena hero alerts por severidade (crit primeiro)
    rank = {"crit": 0, "alert": 1, "low": 1, "attn": 2}
    todos_hero.sort(key=lambda h: rank.get(h["status"], 9))
    todos_hero = todos_hero[:4]

    # Ordena grupos por prioridade clínica
    PRIO = ["glicidico", "lipidico", "hormonal", "inflamatorio", "vitaminas",
            "tireoide", "hepatico", "renal", "adrenal", "hemograma", "outros"]
    grupos_ordenados = []
    for g in PRIO:
        if g in todos_grupos:
            grupos_ordenados.append(todos_grupos[g])
    for g, val_g in todos_grupos.items():
        if g not in PRIO:
            grupos_ordenados.append(val_g)

    # Salva log de auditoria
    _salvar_audit(audit, paciente)

    return {
        "grupos": grupos_ordenados,
        "hero_alerts": todos_hero,
        "stats": stats_total,
        "_audit": audit,
    }


_GRUPO_TITULOS = {
    "hemograma":     ("Hemograma", "Avalia hemácias, hemoglobina, leucócitos, plaquetas."),
    "glicidico":     ("Perfil Glicídico", "Glicose, insulina, HbA1c, HOMA-IR."),
    "lipidico":      ("Perfil Lipídico", "Colesterol, HDL, LDL, triglicérides."),
    "hepatico":      ("Função Hepática", "TGO, TGP, GGT, fosfatase alcalina."),
    "renal":         ("Função Renal", "Ureia, creatinina, ácido úrico."),
    "tireoide":      ("Tireoide", "TSH, T4 Livre, T3 Livre."),
    "hormonal":      ("Hormonal Sexual", "Testosterona, estradiol, FSH, LH, prolactina."),
    "inflamatorio":  ("Marcadores Inflamatórios", "PCR-us, homocisteína, VHS."),
    "vitaminas":     ("Vitaminas e Minerais", "Vit D, B12, ferro, ferritina, magnésio."),
    "adrenal":       ("Adrenal", "Cortisol, IGF-1."),
}


def _formatar_num(n):
    if n is None:
        return "—"
    if abs(n - int(n)) < 0.001:
        return str(int(n))
    return f"{n:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def _formatar_ref(rmin, rmax):
    if rmin is not None and rmax is not None:
        return f"{_formatar_num(rmin)} a {_formatar_num(rmax)}"
    if rmax is not None:
        return f"<{_formatar_num(rmax)}"
    if rmin is not None:
        return f">{_formatar_num(rmin)}"
    return "—"


def _salvar_audit(audit, paciente):
    """Salva log de auditoria do pipeline LLM+validador por paciente."""
    audit_dir = os.path.join(SKILL_DIR, "state", "auditoria")
    os.makedirs(audit_dir, exist_ok=True)
    nome_slug = re.sub(r"[^a-z0-9-]", "", paciente.get("nome", "?").lower().replace(" ", "-"))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(audit_dir, f"{nome_slug}_{ts}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(audit, f, indent=2, ensure_ascii=False, default=str)
        print(f"  [LLM] Audit log: {path}", file=sys.stderr)
    except Exception as e:
        print(f"  [LLM] Erro salvando audit: {e}", file=sys.stderr)


def extrair_todos_exames(lista_pdfs):
    """
    Extrai exames de todos os PDFs de um paciente e mescla os resultados.
    Retorna dict no formato esperado pelas funções de seção.
    """
    if not lista_pdfs:
        return None

    todos_grupos = {}
    todos_hero = []
    stats_total = {"total": 0, "criticos": 0, "alertas": 0, "atencao": 0, "normais": 0}

    for pdf in lista_pdfs:
        pdf_id = pdf.get("id")
        pdf_nome = pdf.get("nome", "exame.pdf")
        if not pdf_id:
            continue

        resultado = run_script("extrair_exames_pdf.py", pdf_id, "--nome", pdf_nome)
        if not resultado or not resultado.get("encontrado"):
            print(f"  PDF {pdf_nome}: não foi possível extrair exames.", file=sys.stderr)
            continue

        # Mescla grupos
        for grupo in resultado.get("grupos", []):
            gid = grupo["id"]
            if gid not in todos_grupos:
                todos_grupos[gid] = grupo.copy()
                todos_grupos[gid]["exames"] = []
            # Adiciona exames que ainda não estão (por nome)
            nomes_existentes = {ex["nome"] for ex in todos_grupos[gid]["exames"]}
            for ex in grupo.get("exames", []):
                if ex["nome"] not in nomes_existentes:
                    todos_grupos[gid]["exames"].append(ex)
                    nomes_existentes.add(ex["nome"])

        # Mescla hero alerts (sem duplicar)
        nomes_hero = {h["nome"] for h in todos_hero}
        for h in resultado.get("hero_alerts", []):
            if h["nome"] not in nomes_hero:
                todos_hero.append(h)
                nomes_hero.add(h["nome"])

        # Acumula stats
        s = resultado.get("stats", {})
        for k in stats_total:
            stats_total[k] += s.get(k, 0)

    if not todos_grupos:
        return None

    PRIORITY_GROUPS = ["metabolico", "hormonal", "lipidico", "inflamacao",
                       "vitaminas", "hepatico", "renal", "hemograma",
                       "autoimune", "oncologico", "outros"]

    SEVERIDADE_ORDEM = {"crit": 0, "alert": 1, "baixo": 1, "attn": 2, "normal": 3, "otimo": 4}

    grupos_ordenados = []
    for gid in PRIORITY_GROUPS:
        if gid in todos_grupos:
            grupos_ordenados.append(todos_grupos[gid])

    # Mantém os 4 hero alerts mais graves
    todos_hero.sort(key=lambda x: SEVERIDADE_ORDEM.get(x.get("status", "normal"), 5))
    todos_hero = todos_hero[:4]

    return {
        "encontrado": True,
        "grupos": grupos_ordenados,
        "hero_alerts": todos_hero,
        "stats": stats_total,
    }


# ---------------------------------------------------------------------------
# Geração do HTML final
# ---------------------------------------------------------------------------

def gerar_resumo_clinico(exames_parsed, questionarios):
    """Gera frase de resumo clínico breve para o cover da apresentação."""
    if not exames_parsed:
        return "Apresentação clínica em elaboração."

    dados = questionarios.get("pre-consulta", {}).get("dados", {}) if questionarios else {}
    peso = dados.get("pesoAtual", "")
    altura = dados.get("altura", "")
    imc = calcular_imc(peso, altura)

    alterados = []
    for grupo in exames_parsed.get("grupos", []):
        for ex in grupo.get("exames", []):
            if ex.get("alterado"):
                alterados.append(ex["nome"])

    partes = []
    if imc:
        _, imc_label = classificar_imc(imc)
        partes.append(f"IMC {imc} kg/m²")

    if alterados:
        partes.append(f"{len(alterados)} parâmetro(s) fora da referência: {', '.join(alterados[:3])}" +
                      (f" e mais {len(alterados) - 3}" if len(alterados) > 3 else ""))

    return " · ".join(partes) if partes else "Perfil metabólico em análise."



# ---------------------------------------------------------------------------
# RC-06: Envio canônico para tópico Pacientes no Telegram
# ---------------------------------------------------------------------------

# Canônica IVS — confirmado em painel-unico-backlog 2026-05-03:
#   group_id: -1003803476669 (AI Vital Slim)
#   topic_id Pacientes: 271
TELEGRAM_GROUP_ID = "-1003803476669"
TELEGRAM_TOPIC_PACIENTES = 271


def enviar_apresentacao_para_topico_pacientes(html_path, paciente, exames_parsed=None):
    """
    REGRA CANÔNICA RC-06: toda apresentação gerada DEVE ser enviada ao
    tópico Pacientes (group_id -1003803476669, topic_id 271) via Telegram.

    Returns:
        dict com {ok: bool, message_id: int|None, erro: str|None}
    """
    import urllib.request, urllib.parse, json as _json, mimetypes, uuid

    # Carrega TELEGRAM_BOT_TOKEN
    token = ""
    for env_path in ["/root/.openclaw/.env.runtime", "/root/.openclaw/.env"]:
        if not os.path.exists(env_path):
            continue
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    val = line.split("=", 1)[1]
                    if val and not val.startswith("op://"):
                        token = val
                        break
        if token:
            break
    if not token:
        return {"ok": False, "erro": "TELEGRAM_BOT_TOKEN não encontrado"}

    # Caption: resumo clínico curto
    nome = paciente.get("nome", "Paciente")
    sexo = paciente.get("sexo", "?")
    idade = paciente.get("idade") or calcular_idade(paciente.get("dataNascimento"))
    stats = (exames_parsed or {}).get("stats", {})

    caption_lines = [f"Apresentação {nome} — {idade}a {sexo}"]
    if stats:
        crit = stats.get("criticos", 0)
        alert = stats.get("alertas", 0)
        normal = stats.get("normais", 0)
        total = stats.get("total", 0)
        caption_lines.append(f"Exames: {total} | {crit} crit | {alert} alert | {normal} normal")
    caption_lines.append(f"Gerada em {time.strftime('%d/%m/%Y %H:%M')}")
    caption = "\n".join(caption_lines)
    if len(caption) > 1000:
        caption = caption[:1000]

    # Multipart upload via curl (mais confiável que urllib pra arquivos grandes)
    cmd = [
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{token}/sendDocument",
        "-F", f"chat_id={TELEGRAM_GROUP_ID}",
        "-F", f"message_thread_id={TELEGRAM_TOPIC_PACIENTES}",
        "-F", f"document=@{html_path}",
        "-F", f"caption={caption}",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        resp = _json.loads(result.stdout) if result.stdout else {}
        if resp.get("ok"):
            mid = resp.get("result", {}).get("message_id")
            print(f"  [TG] Enviado para tópico Pacientes — message_id={mid}", file=sys.stderr)
            return {"ok": True, "message_id": mid}
        return {"ok": False, "erro": resp.get("description", "envio falhou")}
    except Exception as e:
        return {"ok": False, "erro": str(e)}


def _flatten_exames_v9(exames_parsed):
    """Achata exames_parsed (com grupos) numa lista compatível com v9."""
    if not exames_parsed:
        return []
    flat = []
    for grupo in exames_parsed.get("grupos", []):
        for ex in grupo.get("exames", []):
            flat.append({
                "nome": ex.get("nome", ""),
                "valor": ex.get("valor", "—"),
                "unit": ex.get("unidade", ""),
                "ref": ex.get("referencia", "—"),
                "status": ex.get("status", "normal"),
                "grupo": ex.get("grupo") or grupo.get("id", ""),
            })
    return flat


def _valor_float_exame(ex):
    if not ex:
        return None
    if ex.get("valor_f") is not None:
        try:
            return float(ex.get("valor_f"))
        except Exception:
            pass
    raw = str(ex.get("valor", "")).strip()
    m = re.search(r"-?\d+(?:[\.,]\d+)?", raw)
    if not m:
        return None
    try:
        return float(m.group(0).replace(".", "").replace(",", "."))
    except Exception:
        return None


def _ref_max_exame(ex):
    ref = str((ex or {}).get("referencia", "")).replace(",", ".")
    m = re.search(r"(?:a|até|<=|≤|<)\s*(-?\d+(?:\.\d+)?)", ref, re.I)
    if m:
        return float(m.group(1))
    nums = re.findall(r"-?\d+(?:\.\d+)?", ref)
    if len(nums) >= 2:
        return float(nums[-1])
    return None


def _v10_internal_validation(paciente, exames_parsed, questionarios, html_path, bioimpedancia=None,
                             fase="completa"):
    """Validação interna pré-envio. Falha aqui BLOQUEIA envio ao Telegram.

    Regra de gestão: a V10 cruza dois pilares — questionário + todos os exames
    disponíveis (sangue ou não). A validação confirma cobertura da estrutura antes
    do envio e bloqueia omissões críticas ou inconsistências de leitura.

    fase (gates CONDICIONAIS — usado pelo entrypoint gerar_apresentacao_paciente.py):
      "completa"    → todos os gates (default; compatível com as chamadas antigas).
      "preconsulta" → T0/D-5: bioimpedância e antropometria ainda NÃO foram
                      coletadas, então os 13 marcadores de bioimpedância não se
                      aplicam. Todos os demais gates continuam valendo (exames,
                      questionário, padrões clínicos críticos, copy neutra) e
                      entra um gate novo: o HTML PRECISA exibir o estado
                      "a coletar na consulta" (id="bioimpedancia-pendente"),
                      para não existir saída silenciosamente incompleta.
    """
    fase = str(fase or "completa").strip().lower()
    if fase not in ("completa", "preconsulta"):
        raise ValueError(f"fase de validação inválida: {fase!r} (use 'completa' ou 'preconsulta')")
    gates_aplicados = [
        "copy_neutra", "eixo_tireoidiano", "sobrecarga_ferro",
        "exames_no_html", "questionario_cobertura",
    ]
    gates_ignorados = []
    erros = []
    flat = []
    for grupo in (exames_parsed or {}).get("grupos", []):
        for ex in grupo.get("exames", []):
            item = dict(ex)
            item.setdefault("grupo", grupo.get("id", ""))
            flat.append(item)
    by_name = {e.get("nome"): e for e in flat if e.get("nome")}
    html_txt = ""
    try:
        with open(html_path, encoding="utf-8", errors="ignore") as fh:
            html_txt = fh.read()
    except Exception as e:
        erros.append(f"HTML não pôde ser lido para validação: {e}")
    _visible_txt = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->", " ", html_txt, flags=re.I)
    _visible_txt = re.sub(r"<[^>]+>", " ", _visible_txt)
    html_plain = html_lib.unescape(re.sub(r"\s+", " ", _visible_txt))
    if re.search(r"\bSPIN\b|spin[_-]", html_plain, re.I):
        erros.append("Apresentação contém referência visível a SPIN selling; substituir por linguagem clínica neutra.")
    if "Decisão:" in html_plain:
        erros.append("Apresentação contém bloco 'Decisão:'; usar 'Risco no seu caso' cruzado com questionário.")

    # 1) Eixo tireoidiano: TSH suprimido + T3L/T4L altos nunca pode ser omitido.
    tsh, t3l, t4l = by_name.get("TSH"), by_name.get("T3 Livre"), by_name.get("T4 Livre")
    vtsh, vt3l, vt4l = _valor_float_exame(tsh), _valor_float_exame(t3l), _valor_float_exame(t4l)
    t3_max, t4_max = _ref_max_exame(t3l) or 4.4, _ref_max_exame(t4l) or 1.86
    padrao_tireotox = (vtsh is not None and vtsh <= 0.10 and ((vt3l is not None and vt3l > t3_max) or (vt4l is not None and vt4l > t4_max)))
    if padrao_tireotox:
        for nome in ("TSH", "T3 Livre", "T4 Livre"):
            ex = by_name.get(nome)
            if not ex:
                erros.append(f"Eixo tireoidiano crítico: {nome} ausente da estrutura de exames.")
            elif ex.get("status") != "crit":
                erros.append(f"Eixo tireoidiano crítico: {nome} deveria estar como crit, veio {ex.get('status')}.")
            if nome not in html_txt:
                erros.append(f"Eixo tireoidiano crítico: {nome} ausente do HTML final.")
        if not re.search(r"hipertireoidismo|tireotoxicose", html_txt, re.I):
            erros.append("Eixo tireoidiano crítico presente, mas HTML não cita hipertireoidismo/tireotoxicose.")

    # 2) Metabolismo do ferro: ferritina muito alta + ferro/saturação altos nunca pode ser tratado como deficiência.
    ferr, ferro, sat = by_name.get("Ferritina"), by_name.get("Ferro"), by_name.get("Índice de Saturação da Transferrina")
    vferr, vferro, vsat = _valor_float_exame(ferr), _valor_float_exame(ferro), _valor_float_exame(sat)
    ferro_max = _ref_max_exame(ferro) or 175
    padrao_sobrecarga = (vferr is not None and vferr >= 500 and ((vferro is not None and vferro > ferro_max) or (vsat is not None and vsat > 50)))
    if padrao_sobrecarga:
        for nome in ("Ferritina", "Ferro"):
            if nome not in by_name:
                erros.append(f"Sobrecarga de ferro: {nome} ausente da estrutura de exames.")
            if nome not in html_txt:
                erros.append(f"Sobrecarga de ferro: {nome} ausente do HTML final.")
        if not re.search(r"sobrecarga de ferro|hemocromatose", html_txt, re.I):
            erros.append("Sobrecarga de ferro presente, mas HTML não cita sobrecarga de ferro/hemocromatose.")
        html_sem_negacao = re.sub(r"não\s+deve\s+ser\s+lida\s+como\s+['\"]?boa\s+reserva['\"]?", "", html_txt, flags=re.I)
        if re.search(r"queda capilar|reserva de ferro do organismo|(?<!não deve ser lida como )boa reserva", html_sem_negacao, re.I):
            erros.append("Sobrecarga de ferro presente, mas HTML contém copy incompatível de deficiência/reserva de ferro.")

    # 3) Todo exame validado precisa aparecer no HTML final — não só os críticos.
    for ex in flat:
        nome = ex.get("nome")
        if nome and nome not in html_txt:
            erros.append(f"Exame validado ausente do HTML final: {nome}")

    # 4) Exames não-sangue: se bioimpedância existir, os principais marcadores precisam aparecer.
    #    GATE CONDICIONAL POR FASE: em pré-consulta (T0) a bioimpedância só é medida
    #    no dia da consulta — cobrar os 13 marcadores aqui reprovaria uma saída correta.
    if fase == "preconsulta":
        gates_ignorados.append("bioimpedancia_marcadores(fase=preconsulta)")
        if bioimpedancia:
            erros.append(
                "Fase pré-consulta recebeu bioimpedância — use --modo completa/--completar "
                "para gerar a versão com composição corporal."
            )
    elif not bioimpedancia:
        gates_ignorados.append("bioimpedancia_marcadores(sem dados)")
    if fase == "completa" and bioimpedancia:
        gates_aplicados.append("bioimpedancia_marcadores")
        bio_checks = []
        for path in [
            ("peso",), ("imc",), ("tmb",),
            ("gordura", "massa"), ("gordura", "pct"),
            ("massa", "magra_kg"), ("massa", "muscular_kg"), ("massa", "razao_musc_gord"),
            ("hidratacao", "agua_total"), ("agua_celular", "intra"), ("agua_celular", "extra"),
            ("celular", "angulo_fase"), ("celular", "idade_celular"),
        ]:
            cur = bioimpedancia
            for k in path:
                cur = cur.get(k, {}) if isinstance(cur, dict) else None
            if cur not in (None, "", {}, []):
                bio_checks.append((".".join(path), str(cur)))
        for label, value in bio_checks:
            if value not in html_txt and value.replace(".", ",") not in html_txt:
                erros.append(f"Bioimpedância: marcador {label}={value} ausente do HTML final.")

    # 5) Questionário: fonte precisa estar carregada e campos essenciais precisam ser usados corretamente.
    pre = (questionarios or {}).get("pre-consulta") or {}
    dados_q = pre.get("dados", {})
    if not pre.get("encontrado") and not dados_q:
        erros.append("Questionário: pré-consulta não encontrada/carregada.")
    non_empty_q = {k: v for k, v in dados_q.items() if v not in (None, "", [], {}) and not str(k).startswith("draft")}
    if len(non_empty_q) < 20:
        erros.append(f"Questionário: cobertura insuficiente de respostas não vazias ({len(non_empty_q)}).")
    required_q = [
        "spin_p_principalIncomodo", "spin_s_tempoLuta", "spin_s_tentativas",
        "spin_p_desafios", "spin_i_impactoVida", "spin_i_cenario1ano",
        "spin_n_vidaResolvida", "nivelEnergia", "qualidadeSono", "horasSono",
        "medicamentosAtuais", "doencasCronicas", "atividadeFisica", "consumoAgua",
        "pesoAtual", "altura", "alimentacaoFimSemana", "cafeDaManha", "almoco", "jantar",
    ]
    for key in required_q:
        if key in dados_q and dados_q.get(key) in (None, "", [], {}):
            erros.append(f"Questionário: campo essencial vazio — {key}.")
    # Todas as respostas não vazias precisam estar levantadas no HTML interno/auditoria.
    # A narrativa principal continua focada nos problemas; a cobertura total fica no apêndice técnico.
    def _q_value_to_text(v):
        if isinstance(v, (list, tuple)):
            return "; ".join(str(x) for x in v if x not in (None, ""))
        if isinstance(v, dict):
            return json.dumps(v, ensure_ascii=False)
        return str(v)
    q_missing = []
    for key, val in non_empty_q.items():
        if key in {"draftSessionId", "updatedAt"}:
            continue
        txt = _q_value_to_text(val).strip()
        if not txt:
            continue
        variants = {txt, txt.replace(".", ","), re.sub(r"\s+", " ", txt)}
        if not any(v and v in html_plain for v in variants):
            q_missing.append(key)
    if q_missing:
        erros.append("Questionário: respostas não apareceram no HTML interno/auditoria — " + ", ".join(q_missing[:20]) + ("..." if len(q_missing) > 20 else ""))

    # 6) GATE DE FASE — pré-consulta precisa DECLARAR visualmente o que ainda falta.
    #    Sem este bloco a apresentação sairia sem composição corporal e sem dizer
    #    que ela está pendente: exatamente a "saída meio certa" que queremos proibir.
    if fase == "preconsulta":
        gates_aplicados.append("marcador_fase_preconsulta")
        if 'id="bioimpedancia-pendente"' not in html_txt:
            erros.append(
                "Fase pré-consulta: HTML não exibe o estado 'a coletar na consulta' "
                "(bloco id=\"bioimpedancia-pendente\" ausente)."
            )

    status = "blocked" if erros else "passed"
    log_dir = os.path.join(SKILL_DIR, "state", "validacao_v10")
    os.makedirs(log_dir, exist_ok=True)
    slug = re.sub(r"[^a-z0-9-]+", "-", str(paciente.get("nome", "paciente")).lower()).strip("-")
    log_path = os.path.join(log_dir, f"{slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(log_path, "w", encoding="utf-8") as fh:
        json.dump({
            "status": status,
            "fase": fase,
            "paciente": paciente.get("nome"),
            "html_path": html_path,
            "gates_aplicados": gates_aplicados,
            "gates_ignorados": gates_ignorados,
            "erros": erros,
            "checks": {
                "padrao_tireotox": padrao_tireotox,
                "padrao_sobrecarga_ferro": padrao_sobrecarga,
                "criticos": [e.get("nome") for e in flat if e.get("status") == "crit"],
            },
        }, fh, ensure_ascii=False, indent=2)
    if erros:
        raise RuntimeError(
            f"VALIDAÇÃO V10 [fase={fase}] BLOQUEOU ENVIO: " + " | ".join(erros) + f" | log={log_path}"
        )
    print(f"  [VALIDAÇÃO V10] OK (fase={fase}, gates={len(gates_aplicados)}) — {log_path}", file=sys.stderr)
    return True


def gerar_html_apresentacao(paciente, exames_parsed, questionarios, bioimpedancia=None):
    """
    Gera o arquivo HTML da apresentação do paciente — agora via v9 renderer.
    """
    # REGRA CANÔNICA RC-01: sexo é OBRIGATÓRIO
    sexo_paciente = paciente.get("sexo") or paciente.get("gender") or ""
    if not sexo_paciente or str(sexo_paciente).upper()[:1] not in {"M", "F"}:
        # Default seguro: pula geração e loga
        log_path = os.path.join(SKILL_DIR, "state", "sem_sexo.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().isoformat()}\t{paciente.get('nome','?')}\tsexo={sexo_paciente!r}\n")
        raise ValueError(
            f"REGRA CANÔNICA RC-01: sexo do paciente '{paciente.get('nome')}' é obrigatório "
            f"(recebido: {sexo_paciente!r}). Veja REGRAS_CANONICAS.md."
        )
    paciente_v9 = {
        "nome": paciente.get("nome", "Paciente"),
        "dataNascimento": paciente.get("dataNascimento"),
        "idade": paciente.get("idade"),
        "sexo": str(sexo_paciente).upper()[:1],
        "data_consulta": time.strftime("%d.%m.%Y"),
    }
    exames_v9 = _flatten_exames_v9(exames_parsed)

    # V2.7 — Gera 2 versoes:
    # 1. interna (com Medica/objecoes/botao WA) p/ uso da equipe
    # 2. paciente (sem objecoes/botao) p/ envio direto ao paciente
    output_path = render_apresentacao_v10(
        paciente_v9, questionarios or {}, exames_v9,
        output_dir=DELIVERABLES_DIR,
        versao_paciente=False,
        bioimpedancia=bioimpedancia,
    )
    output_path = str(output_path)
    output_path_paciente = render_apresentacao_v10(
        paciente_v9, questionarios or {}, exames_v9,
        output_dir=DELIVERABLES_DIR,
        versao_paciente=True,
        bioimpedancia=bioimpedancia,
    )
    output_path_paciente = str(output_path_paciente)
    print(f'  [V2.7] Versao paciente: {output_path_paciente}', file=sys.stderr)

    # RC-25 operacional: validação interna obrigatória antes de qualquer envio.
    # Se falhar, levanta exceção e BLOQUEIA RC-06 para impedir versão errada no tópico Pacientes.
    _v10_internal_validation(paciente_v9, exames_parsed, questionarios, output_path, bioimpedancia=bioimpedancia)

    # REGRA CANONICA RC-06: envio automatico para topico Pacientes (versao interna)
    try:
        envio = enviar_apresentacao_para_topico_pacientes(output_path, paciente_v9, exames_parsed)
        if envio.get('ok'):
            print(f'  [RC-06] Enviado ao topico Pacientes (msg_id={envio["message_id"]})', file=sys.stderr)
        else:
            print(f'  [RC-06] WARN: envio falhou — {envio.get("erro")}', file=sys.stderr)
    except Exception as e:
        print(f'  [RC-06] ERRO no envio (HTML gerado normalmente): {e}', file=sys.stderr)

    return output_path


def _gerar_html_apresentacao_v8_legacy(paciente, exames_parsed, questionarios):
    """Render v8 (legacy) — preservado para fallback se necessário."""
    env = Environment(loader=FileSystemLoader(ASSETS_DIR))
    template = env.get_template("template-apresentacao-v8.html")

    idade = calcular_idade(paciente.get("dataNascimento"))
    nome = paciente.get("nome", "Paciente")

    # Dados extras do questionário para o card do paciente
    dados_q = questionarios.get("pre-consulta", {}).get("dados", {}) if questionarios else {}
    peso = dados_q.get("pesoAtual", "")
    altura = dados_q.get("altura", "")
    imc = calcular_imc(peso, altura)
    imc_label, _ = classificar_imc(imc)

    # Compat v8: placeholders novos + antigos
    primeiro_nome = nome.split()[0] if nome else "Paciente"
    nome_slug_data = re.sub(r"[^a-zA-Z0-9-]", "", nome.lower().replace(" ", "-"))
    paciente_dict = {
        "nome_completo": nome,
        "primeiro_nome": primeiro_nome,
        "idade": idade if idade else "—",
    }
    context = {
        # === v8 placeholders ===
        "paciente": paciente_dict,
        "exames": {
            "data_mais_recente": time.strftime("%d/%m/%Y") if not exames_parsed else "—",
            "data_extenso": "",
        },
        # === legacy placeholders (mantidos por compat) ===
        "nome_paciente": nome,
        "idade_paciente": idade if idade else "—",
        "crm_medico": "27.588",
        "peso_paciente": peso or "—",
        "altura_paciente": altura or "—",
        "imc_paciente": f"{imc} kg/m² ({imc_label})" if imc else "—",
        "stats_section": gerar_stats_section(exames_parsed),
        "diagnostico_section": gerar_diagnostico_section(exames_parsed, questionarios),
        "anchor_section": gerar_anchor_section(),
        "history_section": gerar_history_section(questionarios),
        "exams_section": gerar_exams_section(exames_parsed),
        "timeline_section": gerar_timeline_section(),
        "contexto_section": gerar_contexto_section(questionarios),
        "references_section": gerar_references_section(),
        "resumo_clinico_breve": gerar_resumo_clinico(exames_parsed, questionarios),
    }

    html = template.render(context)

    # Salva o arquivo
    nome_slug = re.sub(r"[^a-z0-9\-]", "", nome.lower().replace(" ", "-").replace(".", ""))
    nome_arquivo = f"apresentacao-{nome_slug}.html"
    output_path = os.path.join(DELIVERABLES_DIR, nome_arquivo)

    if os.path.exists(output_path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"apresentacao-{nome_slug}-{ts}.html"
        output_path = os.path.join(DELIVERABLES_DIR, nome_arquivo)

    os.makedirs(DELIVERABLES_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


import re  # usado em gerar_html_apresentacao

# v9 renderer (Light cream luxury, 7 secoes, SPIN selling, biblioteca PubMed)
import importlib.util as _ilu
_v9_spec = _ilu.spec_from_file_location("v9_render", os.path.join(SCRIPTS_DIR, "gerar_apresentacao_v9.py"))
_v9_mod = _ilu.module_from_spec(_v9_spec)
_v9_spec.loader.exec_module(_v9_mod)
render_apresentacao_v9 = _v9_mod.render_apresentacao_v9

# v10 — Apresentacao V2 conforme briefing Conselho Growth (premium executive)
_v10_spec = _ilu.spec_from_file_location("v10_render", os.path.join(SCRIPTS_DIR, "gerar_apresentacao_v10.py"))
_v10_mod = _ilu.module_from_spec(_v10_spec)
_v10_spec.loader.exec_module(_v10_mod)
render_apresentacao_v10 = _v10_mod.render_apresentacao_v10

# Extrator de bioimpedancia via gpt-4o vision (PDF dashboard -> dict structured)
_bio_spec = _ilu.spec_from_file_location("bio_extract", os.path.join(SCRIPTS_DIR, "extrair_bioimpedancia_llm.py"))
_bio_mod = _ilu.module_from_spec(_bio_spec)
_bio_spec.loader.exec_module(_bio_mod)
extrair_bioimpedancia_drive = _bio_mod.extrair_bioimpedancia_drive
detectar_pdf_bioimpedancia = _bio_mod.detectar_pdf_bioimpedancia

# Pipeline LLM + Validador (substitui regex parser frágil)
from extrair_exames_llm import extrair_exames_via_llm
from validador_exames import validar_exames
import tempfile

# Drive download (reuso do código existente em extrair_exames_pdf)
from extrair_exames_pdf import baixar_pdf as _baixar_pdf_drive


# ---------------------------------------------------------------------------
# OpenClaw: delega geração HTML com design-impeccable + stitch-design
# ---------------------------------------------------------------------------

# Session ID do tópico 4 (AI Vital Slim — canal principal da Clara)
OPENCLAW_SESSION_ID = "782d6df3-83de-4c50-ac79-2aef5d55480d"
DELIVERABLES_URL_BASE = "https://vps.institutovitalslim.com.br/deliverables"


def _delegar_geracao_openclaw_LEGACY_DESATIVADO(paciente, exames_parsed, questionarios, dados_path, faltantes):
    """DESATIVADO — mantido apenas como registro histórico do caminho que improvisava.

    Este era o bypass: em vez de renderizar, mandava uma MENSAGEM pedindo a um
    agente LLM que "gerasse o UI completo da apresentação". O agente então escrevia
    script próprio e fazia cirurgia sobre o HTML de outra paciente — sem renderer
    canônico e sem passar pelo validador bloqueante.
    Nada chama mais esta função. Use gerar_apresentacao_paciente.py.
    """
    nome = paciente.get("nome", "Paciente")
    idade = calcular_idade(paciente.get("dataNascimento"))
    sexo = paciente.get("sexo", "")
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    # Resume os achados principais para o contexto
    dados_q = questionarios.get("pre-consulta", {}).get("dados", {}) if questionarios else {}
    peso = dados_q.get("pesoAtual", "?")
    altura = dados_q.get("altura", "?")
    imc = calcular_imc(peso, altura)

    heroes = []
    if exames_parsed:
        for h in exames_parsed.get("hero_alerts", []):
            heroes.append(f"• {h['nome']}: {h['valor']} {h['unidade']} [{h['tag_label']}]")

    faltantes_str = f"\n⚠️ FALTANTES: {', '.join(faltantes)}" if faltantes else ""

    msg = f"""📋 CRON APRESENTACAO — {data_hoje}

Novo paciente para consulta detectado no Quarkclinic:

👤 **{nome}**
📅 {idade} anos | {sexo} | IMC {imc} kg/m²
📞 {paciente.get("telefone", "—")} | ✉️ {paciente.get("email", "—")}
{faltantes_str}

📊 Dados coletados em:
`{dados_path}`

🔬 Principais achados:{chr(10) + chr(10).join(heroes) if heroes else " (exames ainda não extraídos)"}

**Ação:**
1. Ler o arquivo de dados em `{dados_path}`
2. Usar a skill **`stitch-design`** (Google Stitch MCP) para gerar o UI completo da apresentação — componentes visuais, layout responsivo, cards de exames, hero alerts
3. Aplicar revisão com **`design-impeccable`** para garantir tipografia, hierarquia visual e brand IVS (tokens em `brand-adapter.md`)
4. Salvar o HTML final em `{DELIVERABLES_DIR}/apresentacao-{re.sub(r"[^a-z0-9-]", "", nome.lower().replace(" ", "-"))}.html`
5. Enviar o link da apresentação aqui."""

    cmd = [
        "openclaw", "agent",
        "--session-id", OPENCLAW_SESSION_ID,
        "-m", msg,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  ✅ Delegado ao OpenClaw (session {OPENCLAW_SESSION_ID[:8]}...)")
            return True
        else:
            print(f"  ⚠️ OpenClaw retornou erro: {result.stderr[:200]}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ OpenClaw timeout (30s) — mensagem pode ter sido enviada", file=sys.stderr)
        return True
    except Exception as e:
        print(f"  ⚠️ Erro ao chamar openclaw: {e}", file=sys.stderr)
        return False


def delegar_geracao_openclaw(paciente, exames_parsed, questionarios, dados_path, faltantes):
    """BYPASS PROIBIDO — não delega mais o render a agente LLM.

    Sempre retorna False e imprime aviso fatal apontando o entrypoint correto.
    Motivo (incidente real): o render delegado por mensagem produziu apresentação
    com hero sem foto da Dra, sem imagem do laudo de bioimpedância e com copy de
    decisão do perfil DISC de OUTRA paciente — porque o validador bloqueante
    (_v10_internal_validation) nunca foi chamado nesse caminho.
    """
    nome = paciente.get("nome", "Paciente")
    entrypoint = os.path.join(SCRIPTS_DIR, "gerar_apresentacao_paciente.py")
    aviso = "\n".join([
        "",
        "=" * 78,
        "[FATAL] DELEGAÇÃO DO RENDER A AGENTE LLM ESTÁ DESATIVADA.",
        f"  Paciente: {nome}",
        "  Motivo:   render delegado por mensagem improvisa HTML fora do renderer",
        "            canônico e NÃO passa pelo validador bloqueante.",
        "",
        "  CAMINHO CORRETO — entrypoint único, determinístico, com gate:",
        f"    python3 {entrypoint} \\",
        f'        --paciente "{nome}" --modo preconsulta --sexo <F|M> \\',
        "        --questionario <questionario.json> --exames-pdfs <exames_pdfs.json>",
        "",
        f"  Dados já coletados por este script: {dados_path}",
        "=" * 78,
        "",
    ])
    print(aviso, file=sys.stderr)
    return False


def salvar_dados_paciente(paciente, exames_drive, exames_parsed, questionarios, data_str, turno, bioimpedancia=None):
    """
    Salva todos os dados coletados em JSON.
    Deduplicacao por hash: se ja existir arquivo do mesmo paciente no mesmo dia
    com conteudo identico (exceto timestamp), retorna o arquivo existente.
    """
    import hashlib
    import glob as _glob

    nome = paciente.get("nome", "paciente")
    nome_slug = re.sub(r"[^a-z0-9-]", "", nome.lower().replace(" ", "-"))

    dados_sem_ts = {
        "data_consulta": data_str,
        "turno": turno,
        "paciente": paciente,
        "exames_drive": exames_drive,
        "exames_analisados": exames_parsed,
        "questionarios": questionarios,
        "bioimpedancia": bioimpedancia,
    }

    conteudo_hash = hashlib.md5(
        json.dumps(dados_sem_ts, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()[:8]

    # Verifica se ja existe arquivo com mesmo hash hoje
    hoje = datetime.now().strftime("%Y%m%d")
    pattern = os.path.join(DELIVERABLES_DIR, f"dados-{nome_slug}-{hoje}*.json")
    for existente in _glob.glob(pattern):
        try:
            with open(existente) as f_ex:
                ex_dados = json.load(f_ex)
            if ex_dados.get("content_hash") == conteudo_hash:
                print(f"  Arquivo identico ja existe: {os.path.basename(existente)} -- pulando", file=sys.stderr)
                return existente
        except Exception:
            pass

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"dados-{nome_slug}-{ts}.json"

    dados = {
        "gerado_em": datetime.now().isoformat(),
        "content_hash": conteudo_hash,
        **dados_sem_ts,
    }

    os.makedirs(DELIVERABLES_DIR, exist_ok=True)
    path_out = os.path.join(DELIVERABLES_DIR, filename)
    with open(path_out, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    return path_out

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 gerar_apresentacao.py <data_dd-MM-yyyy> <turno>")
        print("  turno: manha | tarde")
        sys.exit(1)

    data_str = sys.argv[1]
    turno = sys.argv[2].lower()

    if turno not in ("manha", "tarde"):
        print("ERRO: turno deve ser 'manha' ou 'tarde'")
        sys.exit(1)

    print(f"=== Buscando pacientes novos para {data_str} - turno: {turno} ===")

    # 1. Busca pacientes novos no Quarkclinic
    pacientes = run_script("buscar_pacientes_novos.py", data_str, turno)
    if not pacientes:
        print("Nenhum paciente novo encontrado.")
        sys.exit(0)

    print(f"Encontrados {len(pacientes)} pacientes novos:")
    for p in pacientes:
        print(f"  - {p['nome']} ({p.get('sexo', 'N/A')})")

    relatorio = []

    for paciente in pacientes:
        nome = paciente.get("nome", "")
        sexo = paciente.get("sexo", "")
        print(f"\n--- Processando: {nome} ---")

        # Busca exames no Drive
        print("  Buscando exames no Drive...")
        exames_drive = run_script("buscar_exames_drive.py", nome)
        tem_exames = exames_drive and exames_drive.get("encontrado") and exames_drive.get("total_pdfs", 0) > 0

        # Detectar e extrair bioimpedancia (PDF separado, dashboard visual via vision)
        bioimpedancia_data = None
        if tem_exames:
            try:
                pdf_bio = detectar_pdf_bioimpedancia(exames_drive.get("pdfs", []))
                if pdf_bio:
                    print(f"  📊 Bioimpedância detectada: {pdf_bio.get('nome')} — extraindo via gpt-4o...")
                    bioimpedancia_data = extrair_bioimpedancia_drive(
                        pdf_bio["id"],
                        {"sexo": paciente.get("sexo", ""), "idade": paciente.get("idade", "")},
                    )
                    print(f"  ✅ Bioimpedância: peso={bioimpedancia_data.get('peso')} IMC={bioimpedancia_data.get('imc')} %gord={bioimpedancia_data.get('gordura',{}).get('pct')}")
            except Exception as _e_bio:
                print(f"  ⚠️ Falha ao extrair bioimpedância (segue sem): {_e_bio}")

        # Extrai e analisa os PDFs de exames
        exames_parsed = None
        if tem_exames:
            print(f"  Extraindo dados de {exames_drive['total_pdfs']} PDF(s)...")
            exames_parsed = extrair_todos_exames_llm(exames_drive.get("pdfs", []), paciente)
            if exames_parsed:
                stats = exames_parsed.get("stats", {})
                print(f"  ✅ {stats.get('total', 0)} exames extraídos "
                      f"({stats.get('criticos', 0) + stats.get('alertas', 0)} alterados)")
            else:
                print("  ⚠️ PDFs encontrados mas extração sem resultado.")

        # Busca questionários
        print("  Buscando questionários...")
        args_q = [nome]
        if sexo:
            args_q += ["--sexo", sexo]
        questionarios = run_script("buscar_questionarios.py", *args_q)
        tem_pre_consulta = questionarios and questionarios.get("pre-consulta", {}).get("encontrado")

        # Verifica faltantes
        faltantes = []
        if not tem_exames:
            faltantes.append("exames laboratoriais")
        if not tem_pre_consulta:
            faltantes.append("questionário de pré-consulta")
        if sexo == "FEMININO" and not (questionarios and questionarios.get("analise-hormonal", {}).get("encontrado")):
            faltantes.append("questionário de análise hormonal")

        if faltantes and not tem_pre_consulta and not tem_exames:
            # Sem NADA — log simples, sem delegação
            msg = (f"⚠️ PACIENTE: {nome}\n"
                   f"❌ FALTAM: {', '.join(faltantes)}\n"
                   f"📞 Contato: {paciente.get('telefone', 'N/A')}")
            relatorio.append({
                "paciente": nome,
                "status": "incompleto",
                "faltantes": faltantes,
                "mensagem": msg,
            })
            print(f"  ⚠️ Sem dados suficientes para apresentação.")
        else:
            # Tem dados suficientes — salva JSON e delega ao OpenClaw
            dados_path = salvar_dados_paciente(
                paciente, exames_drive, exames_parsed, questionarios, data_str, turno,
                bioimpedancia=bioimpedancia_data,
            )
            print(f"  📁 Dados salvos: {dados_path}")

            delegado = delegar_geracao_openclaw(
                paciente, exames_parsed, questionarios, dados_path, faltantes
            )

            relatorio.append({
                "paciente": nome,
                "status": "delegado" if delegado else "render_pendente_entrypoint",
                "faltantes": faltantes,
                "dados_path": dados_path,
                "total_exames": exames_parsed.get("stats", {}).get("total", 0) if exames_parsed else 0,
            })

    # Relatório final
    print("\n=== RELATÓRIO FINAL ===")
    incompletos = [r for r in relatorio if r["status"] == "incompleto"]
    delegados = [r for r in relatorio if r["status"] == "delegado"]
    coletados = [r for r in relatorio if r["status"] == "render_pendente_entrypoint"]

    if incompletos:
        print(f"\n⚠️ {len(incompletos)} sem dados suficientes:")
        for r in incompletos:
            print(f"\n{r['mensagem']}")

    if delegados:
        print(f"\n✅ {len(delegados)} delegado(s) ao OpenClaw:")
        for r in delegados:
            parcial = f" [parcial: faltam {', '.join(r['faltantes'])}]" if r.get("faltantes") else ""
            print(f"  - {r['paciente']}: {r['dados_path']}{parcial}")

    if coletados:
        print(f"\n📁 {len(coletados)} com dados coletados — RENDER NÃO FOI FEITO por este script:")
        for r in coletados:
            print(f"  - {r['paciente']}: {r['dados_path']}")

    # Salva relatório JSON
    relatorio_path = os.path.join(DELIVERABLES_DIR, f"relatorio-{data_str}-{turno}.json")
    os.makedirs(DELIVERABLES_DIR, exist_ok=True)
    with open(relatorio_path, "w") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"\nRelatório salvo em: {relatorio_path}")

    # Este script é COLETOR de dados. O render/entrega tem entrypoint próprio,
    # determinístico e com gate bloqueante. Sair 0 aqui daria a falsa impressão
    # de que a apresentação foi gerada.
    if coletados:
        entrypoint = os.path.join(SCRIPTS_DIR, "gerar_apresentacao_paciente.py")
        print("\n" + "=" * 78, file=sys.stderr)
        print("[FATAL] Nenhuma apresentação foi renderizada por este script.", file=sys.stderr)
        print("        Este caminho só COLETA dados. Para gerar a apresentação use:", file=sys.stderr)
        print(f"          python3 {entrypoint} --paciente \"<Nome>\" --modo preconsulta \\", file=sys.stderr)
        print("              --sexo <F|M> --questionario <q.json> --exames-pdfs <pdfs.json>", file=sys.stderr)
        print("=" * 78 + "\n", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
