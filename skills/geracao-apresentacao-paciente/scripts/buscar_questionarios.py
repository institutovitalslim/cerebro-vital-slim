#!/usr/bin/env python3
"""
Busca respostas de questionários do Google Forms para um paciente específico.

Se não encontrar no Google Forms, verifica se há PDF de questionário na pasta
do paciente no Google Drive (alguns pacientes preenchem em papel/PDF).

Formulários:
- Pré-Consulta: 1j8h3FUn4riAqSPJoWsRv1Ura_PPcFx4SDG7kafVcX1g
- Análise Hormonal: 1XGIH3MiwVkHWI5FaH9hjsmByMTAS-Td_H2_rm7T7T0s

Uso:
    python3 buscar_questionarios.py "Nome do Paciente" [--sexo FEMININO|MASCULINO]

Saída: JSON com as respostas encontradas para cada formulário + status de PDF no Drive
"""

import sys
import json
import subprocess
import re

GOG_ACCOUNT = "institutovitalslim@gmail.com"
DRIVE_ACCOUNT = "medicalcontabilidade@gmail.com"
DRIVE_FOLDER_ID = "1dCDANfnUcTX-iRFCCNtipQ5a3NWzHzSL"
FORMS = {
    "pre-consulta": "1j8h3FUn4riAqSPJoWsRv1Ura_PPcFx4SDG7kafVcX1g",
    "analise-hormonal": "1XGIH3MiwVkHWI5FaH9hjsmByMTAS-Td_H2_rm7T7T0s",
}


def gog_forms_get(form_id):
    """Obtém a estrutura do formulário."""
    cmd = ["/usr/local/bin/gog", "forms", "get", form_id, "--json", "--results-only"]
    env = {"GOG_ACCOUNT": GOG_ACCOUNT, "HOME": "/root", "GOG_KEYRING_PASSWORD": "Tf100314@!"}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERRO gog forms get: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def gog_forms_responses(form_id, page_token=None, max_per_page=200):
    """Lista respostas do formulário com paginação automática."""
    cmd = ["/usr/local/bin/gog", "forms", "responses", "list", form_id, "--json", "--results-only", f"--max={max_per_page}"]
    if page_token:
        cmd.append(f"--page={page_token}")
    
    env = {"GOG_ACCOUNT": GOG_ACCOUNT, "HOME": "/root", "GOG_KEYRING_PASSWORD": "Tf100314@!"}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERRO gog forms responses: {result.stderr}", file=sys.stderr)
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def gog_forms_responses_all(form_id, max_per_page=200):
    """Busca TODAS as respostas do formulário (paginando automaticamente)."""
    all_responses = []
    page_token = None
    page_count = 0
    max_pages = 50  # Limite de segurança
    
    while page_count < max_pages:
        data = gog_forms_responses(form_id, page_token, max_per_page)
        
        if isinstance(data, dict):
            responses = data.get("responses", [])
            page_token = data.get("nextPageToken")
        elif isinstance(data, list):
            responses = data
            page_token = None
        else:
            break
        
        all_responses.extend(responses)
        page_count += 1
        
        if not page_token:
            break
    
    if page_count >= max_pages:
        print(f"AVISO: limite de {max_pages} páginas atingido. Pode haver mais respostas.", file=sys.stderr)
    
    print(f"Total de respostas carregadas: {len(all_responses)} (em {page_count} página(s))", file=sys.stderr)
    return all_responses


def gog_drive_search(query, max_results=50):
    """Executa busca no Google Drive."""
    cmd = [
        "/usr/local/bin/gog", "drive", "search", query,
        "--max", str(max_results),
        "--json"
    ]
    env = {"GOG_ACCOUNT": DRIVE_ACCOUNT, "HOME": "/root", "GOG_KEYRING_PASSWORD": "Tf100314@!"}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERRO gog drive: {result.stderr}", file=sys.stderr)
        return []
    try:
        data = json.loads(result.stdout)
        return data.get("files", [])
    except json.JSONDecodeError:
        return []


def encontrar_pasta_paciente_drive(nome_paciente):
    """Encontra a pasta do paciente no Drive."""
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    pastas = gog_drive_search(query, max_results=100)
    
    nome_norm = re.sub(r'[^a-zA-Z0-9]', '', nome_paciente).upper()
    
    for pasta in pastas:
        pasta_nome = pasta.get("name", "").upper()
        pasta_nome_norm = re.sub(r'[^a-zA-Z0-9]', '', pasta_nome)
        
        if nome_norm == pasta_nome_norm:
            return pasta
        
        # Match parcial por palavras significativas
        palavras_nome = {p for p in re.split(r'[^A-Z0-9]+', nome_paciente.upper()) if len(p) > 2}
        palavras_pasta = {p for p in re.split(r'[^A-Z0-9]+', pasta_nome) if len(p) > 2}
        palavras_comuns = palavras_nome & palavras_pasta
        
        if len(palavras_comuns) >= 3:
            return pasta
    
    return None


def verificar_questionario_pdf_na_pasta(pasta_id):
    """Verifica se há PDF com 'Questionário' ou 'questionario' na pasta do paciente."""
    query = f"'{pasta_id}' in parents and mimeType = 'application/pdf'"
    arquivos = gog_drive_search(query, max_results=50)
    
    for arq in arquivos:
        nome = arq.get("name", "").lower()
        if "questionario" in nome or "questionário" in nome or "pre-consulta" in nome or "pre consulta" in nome:
            return {
                "encontrado": True,
                "arquivo": arq.get("name", ""),
                "id": arq.get("id", ""),
                "link": f"https://drive.google.com/file/d/{arq.get('id', '')}/view"
            }
    
    return {"encontrado": False}


def encontrar_resposta_paciente(responses, nome_paciente):
    """
    Encontra a resposta que corresponde ao paciente no Google Forms.
    O campo de nome geralmente é o 11b6db9b (identificado empiricamente).
    
    Matching adaptativo: o threshold depende do tamanho do nome NA RESPOSTA.
    Se o paciente preencheu um nome curto no Forms, aceita match com menos palavras.
    """
    nome_norm = re.sub(r'[^a-zA-Z0-9]', '', nome_paciente).upper()
    palavras_nome = {p for p in re.split(r'[^A-Z0-9]+', nome_paciente.upper()) if len(p) > 2}
    
    melhor_match = None
    melhor_score = 0
    
    for resp in responses:
        answers = resp.get("answers", {})
        
        # Tenta encontrar o nome em qualquer campo de texto
        for qid, ans in answers.items():
            val = ans.get("textAnswers", {}).get("answers", [{}])[0].get("value", "")
            val_norm = re.sub(r'[^a-zA-Z0-9]', '', val).upper()
            
            # Match exato
            if nome_norm == val_norm:
                return resp
            
            # Match parcial por palavras
            palavras_val = {p for p in re.split(r'[^A-Z0-9]+', val.upper()) if len(p) > 2}
            comuns = palavras_nome & palavras_val
            score = len(comuns)
            
            if score > melhor_score:
                melhor_score = score
                melhor_match = resp
    
    # Threshold: 2 palavras em comum já é suficientemente discriminativo
    # (ex: "Mario" + "Abreu" é muito improvável de ser outra pessoa)
    if melhor_match and melhor_score >= 2:
        return melhor_match
    
    return None


def formatar_resposta(resposta, form_structure):
    """Formata a resposta em um dict legível com perguntas e respostas."""
    if not resposta:
        return None
    
    items = form_structure.get("items", [])
    question_map = {}
    for item in items:
        qid = item.get("questionItem", {}).get("question", {}).get("questionId", "")
        title = item.get("title", "")
        if qid:
            question_map[qid] = title
    
    answers = resposta.get("answers", {})
    result = {}
    
    for qid, answer_data in answers.items():
        pergunta = question_map.get(qid, qid)
        valores = answer_data.get("textAnswers", {}).get("answers", [])
        valor = ", ".join([v.get("value", "") for v in valores])
        result[pergunta] = valor
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 buscar_questionarios.py 'Nome do Paciente' [--sexo FEMININO|MASCULINO]")
        sys.exit(1)
    
    nome_paciente = sys.argv[1]
    sexo = None
    if "--sexo" in sys.argv:
        idx = sys.argv.index("--sexo")
        if idx + 1 < len(sys.argv):
            sexo = sys.argv[idx + 1].upper()
    
    resultados = {}
    
    # Busca pasta do paciente no Drive (para verificar PDFs de questionário)
    pasta_paciente = encontrar_pasta_paciente_drive(nome_paciente)
    
    # --- Pré-Consulta ---
    form_id = FORMS["pre-consulta"]
    form_structure = gog_forms_get(form_id)
    responses = gog_forms_responses_all(form_id)
    
    resposta_forms = None
    if responses:
        resposta_forms = encontrar_resposta_paciente(responses, nome_paciente)
    
    # Verifica se há PDF de questionário no Drive
    pdf_questionario = {"encontrado": False}
    if pasta_paciente:
        pdf_questionario = verificar_questionario_pdf_na_pasta(pasta_paciente["id"])
    
    encontrado = resposta_forms is not None or pdf_questionario["encontrado"]
    
    resultados["pre-consulta"] = {
        "encontrado": encontrado,
        "fonte": "forms" if resposta_forms else ("pdf_drive" if pdf_questionario["encontrado"] else None),
        "respostas": formatar_resposta(resposta_forms, form_structure) if resposta_forms else None,
        "pdf_drive": pdf_questionario if pdf_questionario["encontrado"] else None
    }
    
    # --- Análise Hormonal (apenas mulheres) ---
    if sexo == "FEMININO":
        form_id = FORMS["analise-hormonal"]
        form_structure = gog_forms_get(form_id)
        responses = gog_forms_responses_all(form_id)
        
        resposta_forms = None
        if responses:
            resposta_forms = encontrar_resposta_paciente(responses, nome_paciente)
        
        encontrado = resposta_forms is not None
        
        resultados["analise-hormonal"] = {
            "encontrado": encontrado,
            "fonte": "forms" if resposta_forms else None,
            "respostas": formatar_resposta(resposta_forms, form_structure) if resposta_forms else None
        }
    
    print(json.dumps(resultados, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
