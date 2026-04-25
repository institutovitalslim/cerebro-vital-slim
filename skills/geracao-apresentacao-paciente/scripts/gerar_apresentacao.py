#!/usr/bin/env python3
"""
Script principal de geração de apresentação de paciente.

Orquestra todo o fluxo:
1. Busca pacientes novos no Quarkclinic para uma data/turno
2. Para cada paciente:
   a. Busca exames no Google Drive
   b. Busca respostas dos questionários
   c. Extrai dados dos PDFs de exames
   d. Gera apresentação HTML usando template Jinja2
   e. Envia notificação se faltar informação

Uso:
    python3 gerar_apresentacao.py <data_dd-MM-yyyy> <turno>

    turno: manha | tarde
"""

import sys
import os
import json
import subprocess
import tempfile
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

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


def gerar_stats_section(exames_analisados=None):
    """Gera seção de stats. Placeholder até análise clínica."""
    if not exames_analisados:
        return '<!-- stats_section: preencher com dados dos exames -->'
    # TODO: gerar HTML real a partir dos exames analisados
    return '<!-- stats_section: preencher com dados dos exames -->'


def gerar_diagnostico_section(exames_analisados=None):
    """Gera seção de diagnóstico. Placeholder até análise clínica."""
    if not exames_analisados:
        return '<!-- diagnostico_section: preencher com dados dos exames -->'
    return '<!-- diagnostico_section: preencher com dados dos exames -->'


def gerar_anchor_section():
    """Gera seção anchor com link para a Dra."""
    return '''<section class="anchor" aria-labelledby="anchor-title">
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
</section>'''


def gerar_history_section(questionarios=None):
    """Gera seção de histórico a partir dos questionários."""
    if not questionarios:
        return '<!-- history_section: preencher com dados do questionário -->'

    pre = questionarios.get("pre-consulta", {})
    if not pre.get("encontrado"):
        return '<!-- history_section: questionário não encontrado -->'

    dados = pre.get("dados", {})
    linhas = []

    def val(campo, fallback="—"):
        v = dados.get(campo)
        if not v or v == "" or str(v).lower() in ("nenhum", "nenhuma", "nao", "não"):
            return fallback
        return str(v)

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
    linhas.append('      </div>')

    # Card 2: Rotina
    linhas.append('      <div class="hist-card">')
    linhas.append('        <h3>Rotina</h3>')
    linhas.append(f'        <p><strong>Atividade:</strong> {val("atividadeFisica")} ({val("frequenciaAtividade")})</p>')
    linhas.append(f'        <p><strong>Sono:</strong> {val("horasSono")}h (nota {val("qualidadeSono")}/10)</p>')
    linhas.append(f'        <p><strong>Energia:</strong> {val("nivelEnergia")}/10</p>')
    linhas.append(f'        <p><strong>Água:</strong> {val("consumoAgua")}</p>')
    linhas.append('      </div>')

    # Card 3: Alimentação
    linhas.append('      <div class="hist-card">')
    linhas.append('        <h3>Alimentação</h3>')
    linhas.append(f'        <p><strong>Refeições:</strong> {val("refeicoesDia")}/dia</p>')
    linhas.append(f'        <p><strong>Café da manhã:</strong> {val("cafeDaManha")}</p>')
    linhas.append(f'        <p><strong>Almoço:</strong> {val("almoco")}</p>')
    linhas.append(f'        <p><strong>Jantar:</strong> {val("jantar")}</p>')
    linhas.append('      </div>')

    # Card 4: Jornada
    linhas.append('      <div class="hist-card">')
    linhas.append('        <h3>Jornada</h3>')
    linhas.append(f'        <p><strong>Tempo de luta:</strong> {val("spin_s_tempoLuta")}</p>')
    linhas.append(f'        <p><strong>O que já tentou:</strong> {val("spin_s_tentativas")}</p>')
    linhas.append(f'        <p><strong>Principal incômodo:</strong> {val("spin_p_principalIncomodo")}</p>')
    linhas.append(f'        <p><strong>Objetivo:</strong> {val("tresObjetivos")}</p>')
    linhas.append('      </div>')

    linhas.append('    </div>')
    linhas.append('  </div>')
    linhas.append('</section>')

    return '\n'.join(linhas)


def gerar_exams_section(exames=None):
    """Gera seção de exames. Placeholder até análise clínica dos PDFs."""
    if not exames or not exames.get("encontrado"):
        return '<!-- exams_section: preencher após análise dos PDFs de exames -->'
    total = exames.get("total_pdfs", 0)
    return f'<!-- exams_section: {total} PDF(s) encontrado(s). Análise clínica pendente. -->'


def gerar_timeline_section():
    """Gera seção de timeline padrão de 180 dias."""
    return '''<section class="timeline" aria-labelledby="time-title">
  <div class="wrap">
    <h2 id="time-title">O que esperar em 180 dias</h2>
    <ul class="time-list">
      <li><strong>Mês 1 — Diagnóstico e ajuste:</strong> Plano alimentar personalizado, suplementação de base e primeiros ajustes de estilo de vida.</li>
      <li><strong>Mês 2 — Reversão:</strong> Sensibilidade insulínica começa a melhorar, energia sobe, sono fica mais reparador.</li>
      <li><strong>Mês 3 — Consolidação:</strong> Peso em queda sustentável, exames mostrando melhora objetiva.</li>
      <li><strong>Mês 4-6 — Otimização:</strong> Ajustes finos baseados em novos exames. Resultado sustentável a longo prazo.</li>
    </ul>
  </div>
</section>'''


def gerar_contexto_section(questionarios=None):
    """Gera seção de contexto a partir dos questionários."""
    if not questionarios:
        return '<!-- contexto_section: preencher com dados do questionário -->'

    pre = questionarios.get("pre-consulta", {})
    if not pre.get("encontrado"):
        return '<!-- contexto_section: questionário não encontrado -->'

    dados = pre.get("dados", {})

    def val(campo, fallback="—"):
        v = dados.get(campo)
        if not v or v == "" or str(v).lower() in ("nenhum", "nenhuma", "nao", "não"):
            return fallback
        return str(v)

    panels = []

    # Panel 1: Histórico e objetivos
    panels.append(f'''<div class="ctx-panel">
  <h3>Histórico e objetivos</h3>
  <dl>
    <dt>Objetivo</dt><dd>{val("tresObjetivos", "Não informado")}</dd>
    <dt>Peso atual</dt><dd>{val("pesoAtual")} kg</dd>
    <dt>Peso desejado</dt><dd>{val("pesoIdeal")} kg</dd>
    <dt>Altura</dt><dd>{val("altura")} cm</dd>
    <dt>Medicamentos</dt><dd>{val("medicamentosAtuais")}</dd>
    <dt>Condições</dt><dd>{val("doencasCronicas")}</dd>
    <dt>Atividade física</dt><dd>{val("atividadeFisica")}</dd>
  </dl>
</div>''')

    # Panel 2: Hábitos alimentares
    panels.append(f'''<div class="ctx-panel">
  <h3>Hábitos alimentares</h3>
  <dl>
    <dt>Refeições / dia</dt><dd>{val("refeicoesDia")}</dd>
    <dt>Café da manhã</dt><dd>{val("cafeDaManha")}</dd>
    <dt>Almoço</dt><dd>{val("almoco")}</dd>
    <dt>Jantar</dt><dd>{val("jantar")}</dd>
    <dt>Água</dt><dd>{val("consumoAgua")}</dd>
  </dl>
</div>''')

    return '<section class="contexto" aria-labelledby="ctx-title">\n  <div class="wrap">\n    <h2 id="ctx-title">Contexto do paciente</h2>\n    <div class="ctx-grid">\n' + '\n'.join(panels) + '\n    </div>\n  </div>\n</section>'


def gerar_references_section():
    """Gera seção de referências bibliográficas padrão."""
    return '''<section class="references" aria-labelledby="ref-title">
  <div class="wrap">
    <h2 id="ref-title">Referências</h2>
    <ul class="ref-list">
      <li>American Diabetes Association. Standards of Care in Diabetes—2024. <em>Diabetes Care</em>.</li>
      <li>Holick MF. Vitamin D deficiency. <em>N Engl J Med</em>. 2007;357(3):266-81.</li>
      <li>DeFronzo RA. Insulin resistance, lipotoxicity, type 2 diabetes and atherosclerosis. <em>Diabetologia</em>. 2010.</li>
    </ul>
  </div>
</section>'''


def gerar_html_apresentacao(paciente, dados_exames, dados_questionarios):
    """
    Gera o arquivo HTML da apresentação do paciente.
    Usa o template Jinja2 e substitui os placeholders.
    """
    env = Environment(loader=FileSystemLoader(ASSETS_DIR))
    template = env.get_template("template-apresentacao.html")

    idade = calcular_idade(paciente.get("dataNascimento"))
    nome = paciente.get("nome", "Paciente")

    context = {
        "nome_paciente": nome,
        "idade_paciente": idade if idade else "—",
        "crm_medico": "27.588",
        "stats_section": gerar_stats_section(dados_exames),
        "diagnostico_section": gerar_diagnostico_section(dados_exames),
        "anchor_section": gerar_anchor_section(),
        "history_section": gerar_history_section(dados_questionarios),
        "exams_section": gerar_exams_section(dados_exames),
        "timeline_section": gerar_timeline_section(),
        "contexto_section": gerar_contexto_section(dados_questionarios),
        "references_section": gerar_references_section(),
        "resumo_clinico_breve": "[resumo clínico a ser preenchido após análise dos exames]",
    }

    html = template.render(context)

    # Salva o arquivo
    nome_slug = nome.lower().replace(' ', '-').replace('.', '')
    nome_arquivo = f"apresentacao-{nome_slug}.html"
    output_path = os.path.join(DELIVERABLES_DIR, nome_arquivo)

    # Se já existir, usa nome com timestamp
    if os.path.exists(output_path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"apresentacao-{nome_slug}-{ts}.html"
        output_path = os.path.join(DELIVERABLES_DIR, nome_arquivo)

    os.makedirs(DELIVERABLES_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


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

    # 2. Para cada paciente, busca exames e questionários
    relatorio = []

    for paciente in pacientes:
        nome = paciente.get("nome", "")
        sexo = paciente.get("sexo", "")
        print(f"\n--- Processando: {nome} ---")

        # Busca exames no Drive
        print("  Buscando exames no Drive...")
        exames = run_script("buscar_exames_drive.py", nome)
        tem_exames = exames and exames.get("encontrado") and exames.get("total_pdfs", 0) > 0

        # Busca questionários
        print("  Buscando questionários...")
        if sexo:
            questionarios = run_script("buscar_questionarios.py", nome, "--sexo", sexo)
        else:
            questionarios = run_script("buscar_questionarios.py", nome)

        tem_pre_consulta = questionarios and questionarios.get("pre-consulta", {}).get("encontrado")
        tem_hormonal = questionarios and questionarios.get("analise-hormonal", {}).get("encontrado")

        # Verifica o que falta
        faltantes = []
        if not tem_exames:
            faltantes.append("exames laboratoriais")
        if not tem_pre_consulta:
            faltantes.append("questionário de pré-consulta")
        if sexo == "FEMININO" and not tem_hormonal:
            faltantes.append("questionário de análise hormonal")

        if faltantes:
            msg = f"⚠️ PACIENTE: {nome}\n❌ FALTAM: {', '.join(faltantes)}\n📞 Contato: {paciente.get('telefone', 'N/A')}"
            relatorio.append({
                "paciente": nome,
                "status": "incompleto",
                "faltantes": faltantes,
                "mensagem": msg
            })
            print(f"  ⚠️ Faltam informações: {', '.join(faltantes)}")
        else:
            # Tudo OK - gera apresentação
            print("  ✅ Todas as informações encontradas. Gerando apresentação...")

            html_path = gerar_html_apresentacao(paciente, exames, questionarios)

            relatorio.append({
                "paciente": nome,
                "status": "ok",
                "html_path": html_path,
                "total_exames": exames.get("total_pdfs", 0),
                "exames": [p["nome"] for p in exames.get("pdfs", [])]
            })
            print(f"  ✅ Apresentação gerada: {html_path}")

    # 3. Imprime relatório final
    print("\n=== RELATÓRIO FINAL ===")
    incompletos = [r for r in relatorio if r["status"] == "incompleto"]
    completos = [r for r in relatorio if r["status"] == "ok"]

    if incompletos:
        print(f"\n⚠️ {len(incompletos)} PACIENTE(S) COM INFORMAÇÕES PENDENTES:")
        for r in incompletos:
            print(f"\n{r['mensagem']}")

    if completos:
        print(f"\n✅ {len(completos)} PACIENTE(S) COM APRESENTAÇÃO GERADA:")
        for r in completos:
            print(f"  - {r['paciente']}: {r['html_path']}")

    # Salva relatório JSON para o agente processar
    relatorio_path = os.path.join(DELIVERABLES_DIR, f"relatorio-{data_str}-{turno}.json")
    with open(relatorio_path, "w") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"\nRelatório salvo em: {relatorio_path}")


if __name__ == "__main__":
    main()
