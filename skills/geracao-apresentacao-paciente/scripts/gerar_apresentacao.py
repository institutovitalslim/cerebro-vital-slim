#!/usr/bin/env python3
"""
Script principal de geração de apresentação de paciente.

Orquestra todo o fluxo:
1. Busca pacientes novos no Quarkclinic para uma data/turno
2. Para cada paciente:
   a. Busca exames no Google Drive
   b. Busca respostas dos questionários
   c. Extrai dados dos PDFs de exames
   d. Gera apresentação HTML
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
import shutil
from datetime import datetime, timedelta

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


def extrair_dados_exames_pdf(pdf_id, pdf_name):
    """
    Extrai dados de exames de um PDF no Google Drive.
    Faz download do PDF e usa a ferramenta de análise de PDF.
    """
    # Cria diretório temporário
    tmpdir = tempfile.mkdtemp(prefix="exames_")
    pdf_path = os.path.join(tmpdir, pdf_name)
    
    try:
        # Download do PDF via gog
        env = {"GOG_ACCOUNT": "medicalcontabilidade@gmail.com"}
        download_cmd = ["gog", "drive", "export", pdf_id, "--out", pdf_path]
        result = subprocess.run(download_cmd, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            print(f"ERRO ao baixar PDF {pdf_name}: {result.stderr}", file=sys.stderr)
            return None
        
        # Extrai texto do PDF usando pdfplumber ou similar
        # Como não temos pdfplumber instalado, vamos usar o comando 'pdf' do OpenClaw
        # Na prática, isso será feito pelo agente que carrega a skill
        # Aqui retornamos o path para o agente processar
        return {"pdf_path": pdf_path, "pdf_name": pdf_name}
    except Exception as e:
        print(f"ERRO ao processar PDF {pdf_name}: {e}", file=sys.stderr)
        return None
    finally:
        # Não remove o tmpdir aqui - o agente precisa do PDF
        pass


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


def gerar_html_apresentacao(paciente, dados_exames, dados_questionarios):
    """
    Gera o arquivo HTML da apresentação do paciente.
    Usa o template base e substitui os placeholders.
    """
    template_path = os.path.join(ASSETS_DIR, "template-apresentacao.html")
    with open(template_path, "r") as f:
        html = f.read()
    
    # Substitui informações básicas do paciente
    html = html.replace("Mário Gomes de Abreu Filho", paciente.get("nome", "Paciente"))
    
    idade = calcular_idade(paciente.get("dataNascimento"))
    if idade:
        html = html.replace("52 anos", f"{idade} anos")
    
    # O restante das substituições (exames, cards, textos) deve ser feito
    # pelo agente que carrega a skill, pois requer análise dos PDFs e
    # geração de conteúdo clínico personalizado.
    
    # Salva o arquivo
    nome_arquivo = f"apresentacao-{paciente.get('nome', '').lower().replace(' ', '-')}.html"
    output_path = os.path.join(DELIVERABLES_DIR, nome_arquivo)
    
    # Se já existir, usa nome com timestamp
    if os.path.exists(output_path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"apresentacao-{paciente.get('nome', '').lower().replace(' ', '-')}-{ts}.html"
        output_path = os.path.join(DELIVERABLES_DIR, nome_arquivo)
    
    with open(output_path, "w") as f:
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
        sexo_arg = f"--sexo {sexo}" if sexo else ""
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
            
            # Extrai dados dos PDFs
            pdfs = exames.get("pdfs", [])
            dados_exames = []
            for pdf in pdfs:
                dados = extrair_dados_exames_pdf(pdf["id"], pdf["nome"])
                if dados:
                    dados_exames.append(dados)
            
            # Gera HTML (template base - o agente completa com dados dos exames)
            html_path = gerar_html_apresentacao(paciente, dados_exames, questionarios)
            
            relatorio.append({
                "paciente": nome,
                "status": "ok",
                "html_path": html_path,
                "total_exames": len(pdfs),
                "exames": [p["nome"] for p in pdfs]
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
