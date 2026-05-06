#!/usr/bin/env python3
"""
Script principal de geração de apresentação de paciente.

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
import subprocess
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


def gerar_html_apresentacao(paciente, exames_parsed, questionarios):
    """
    Gera o arquivo HTML da apresentação do paciente.
    """
    env = Environment(loader=FileSystemLoader(ASSETS_DIR))
    template = env.get_template("template-apresentacao.html")

    idade = calcular_idade(paciente.get("dataNascimento"))
    nome = paciente.get("nome", "Paciente")

    # Dados extras do questionário para o card do paciente
    dados_q = questionarios.get("pre-consulta", {}).get("dados", {}) if questionarios else {}
    peso = dados_q.get("pesoAtual", "")
    altura = dados_q.get("altura", "")
    imc = calcular_imc(peso, altura)
    imc_label, _ = classificar_imc(imc)

    context = {
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


# ---------------------------------------------------------------------------
# OpenClaw: delega geração HTML com design-impeccable + stitch-design
# ---------------------------------------------------------------------------

# Session ID do tópico 4 (AI Vital Slim — canal principal da Clara)
OPENCLAW_SESSION_ID = "782d6df3-83de-4c50-ac79-2aef5d55480d"
DELIVERABLES_URL_BASE = "https://vps.institutovitalslim.com.br/deliverables"


def delegar_geracao_openclaw(paciente, exames_parsed, questionarios, dados_path, faltantes):
    """
    Envia mensagem ao OpenClaw agent (topic 4) para gerar apresentação HTML
    usando as skills design-impeccable e stitch-design. Retorna True se enviado com sucesso.
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


def salvar_dados_paciente(paciente, exames_drive, exames_parsed, questionarios, data_str, turno):
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

        # Extrai e analisa os PDFs de exames
        exames_parsed = None
        if tem_exames:
            print(f"  Extraindo dados de {exames_drive['total_pdfs']} PDF(s)...")
            exames_parsed = extrair_todos_exames(exames_drive.get("pdfs", []))
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
                paciente, exames_drive, exames_parsed, questionarios, data_str, turno
            )
            print(f"  📁 Dados salvos: {dados_path}")

            delegado = delegar_geracao_openclaw(
                paciente, exames_parsed, questionarios, dados_path, faltantes
            )

            relatorio.append({
                "paciente": nome,
                "status": "delegado" if delegado else "dados_coletados",
                "faltantes": faltantes,
                "dados_path": dados_path,
                "total_exames": exames_parsed.get("stats", {}).get("total", 0) if exames_parsed else 0,
            })

    # Relatório final
    print("\n=== RELATÓRIO FINAL ===")
    incompletos = [r for r in relatorio if r["status"] == "incompleto"]
    delegados = [r for r in relatorio if r["status"] == "delegado"]
    coletados = [r for r in relatorio if r["status"] == "dados_coletados"]

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
        print(f"\n📁 {len(coletados)} com dados coletados (openclaw offline):")
        for r in coletados:
            print(f"  - {r['paciente']}: {r['dados_path']}")

    # Salva relatório JSON
    relatorio_path = os.path.join(DELIVERABLES_DIR, f"relatorio-{data_str}-{turno}.json")
    os.makedirs(DELIVERABLES_DIR, exist_ok=True)
    with open(relatorio_path, "w") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"\nRelatório salvo em: {relatorio_path}")


if __name__ == "__main__":
    main()
