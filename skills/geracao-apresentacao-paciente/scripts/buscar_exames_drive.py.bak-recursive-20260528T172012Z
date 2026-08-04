#!/usr/bin/env python3
"""
Busca exames de um paciente no Google Drive (conta medicalcontabilidade@gmail.com).

Estratégia:
  1. Busca subpasta do paciente dentro da pasta Pacientes usando --query "name contains 'nome'"
  2. Lista TODOS os PDFs dentro da pasta do paciente
  3. Para exames de sangue (sangue/hemograma/laudo): retorna APENAS o mais recente
  4. Os demais PDFs são todos retornados para extração de conteúdo
  IMPORTANTE: o conteúdo de TODOS os PDFs é extraído — nunca filtrar apenas pelo nome.

Uso:
    python3 buscar_exames_drive.py "Nome do Paciente"

Saída: JSON com lista de arquivos PDF encontrados (nome, id, link, modifiedTime, tipo)
"""

import sys
import json
import subprocess
import re
import unicodedata

DRIVE_FOLDER_ID = "1dCDANfnUcTX-iRFCCNtipQ5a3NWzHzSL"  # pasta "Pacientes"
GOG_ACCOUNT = "medicalcontabilidade@gmail.com"
GOG_ENV = {
    "GOG_ACCOUNT": GOG_ACCOUNT,
    "HOME": "/root",
    "GOG_KEYRING_PASSWORD": "Tf100314@!",
    "PATH": "/usr/local/bin:/usr/bin:/bin",
}

# Palavras que identificam exame de sangue / laudo laboratorial
SANGUE_KEYWORDS = {
    "sangue", "hemograma", "laborat", "laudo", "bioquim",
    "hematol", "sorolog", "hematocrit", "clinico",
}

STOP_WORDS = {"de", "da", "do", "dos", "das", "e", "em", "o", "a", "os", "as", "nf", "pdf"}


def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def palavras_significativas(nome):
    words = re.split(r"[^A-Za-z0-9]+", strip_accents(nome.lower()))
    return {w for w in words if len(w) >= 3 and w not in STOP_WORDS}


def gog_ls(parent_id, query=None, max_results=200):
    """Lista arquivos dentro de um folder do Drive usando gog drive ls."""
    cmd = [
        "/usr/local/bin/gog", "drive", "ls",
        "--parent", parent_id,
        "--max", str(max_results),
        "--json",
    ]
    if query:
        cmd += ["--query", query]

    result = subprocess.run(cmd, capture_output=True, text=True, env=GOG_ENV)
    if result.returncode != 0:
        print(f"ERRO gog drive ls: {result.stderr[:300]}", file=sys.stderr)
        return []
    try:
        data = json.loads(result.stdout)
        return data.get("files", [])
    except json.JSONDecodeError:
        print(f"ERRO: resposta inválida do gog: {result.stdout[:200]}", file=sys.stderr)
        return []


def encontrar_pasta_paciente(nome_paciente):
    """
    Encontra a pasta do paciente dentro da pasta Pacientes.
    Usa Drive query 'name contains PRIMEIRO_NOME' e depois faz fuzzy match.
    """
    primeiro_nome = nome_paciente.strip().split()[0].upper()

    # Busca por folders que contenham o primeiro nome
    itens = gog_ls(
        DRIVE_FOLDER_ID,
        query=f"name contains '{primeiro_nome}' and mimeType = 'application/vnd.google-apps.folder'",
        max_results=50,
    )

    # Se não achou pasta, tenta buscar qualquer item com o primeiro nome
    if not itens:
        itens = gog_ls(
            DRIVE_FOLDER_ID,
            query=f"name contains '{primeiro_nome}'",
            max_results=50,
        )
        itens = [i for i in itens if "folder" in i.get("mimeType", "")]

    if not itens:
        return None

    # Fuzzy match: seleciona a pasta com mais palavras em comum com o nome completo
    palavras_pac = palavras_significativas(nome_paciente)
    melhor = None
    melhor_score = 0

    for pasta in itens:
        palavras_pasta = palavras_significativas(pasta.get("name", ""))
        score = len(palavras_pac & palavras_pasta)
        if score > melhor_score:
            melhor_score = score
            melhor = pasta

    # Aceita com pelo menos 1 palavra em comum (nome único como Tiaro)
    if melhor and melhor_score >= 1:
        return melhor

    return None


def is_sangue(nome_arquivo):
    """Detecta se o PDF é um exame de sangue / laudo laboratorial."""
    nome_lower = strip_accents(nome_arquivo.lower())
    return any(kw in nome_lower for kw in SANGUE_KEYWORDS)


def listar_pdfs_pasta(pasta_id):
    """Lista todos os PDFs dentro da pasta do paciente."""
    arquivos = gog_ls(
        pasta_id,
        query="mimeType = 'application/pdf'",
        max_results=100,
    )
    return arquivos


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 buscar_exames_drive.py 'Nome do Paciente'")
        sys.exit(1)

    nome_paciente = sys.argv[1]

    # 1. Encontrar pasta do paciente
    pasta = encontrar_pasta_paciente(nome_paciente)
    if not pasta:
        print(json.dumps({
            "encontrado": False,
            "mensagem": f"Pasta do paciente '{nome_paciente}' não encontrada no Drive.",
            "pdfs": [],
        }, indent=2, ensure_ascii=False))
        sys.exit(0)

    print(f"  📁 Pasta encontrada: {pasta['name']} ({pasta['id']})", file=sys.stderr)

    # 2. Listar todos os PDFs na pasta
    todos_pdfs = listar_pdfs_pasta(pasta["id"])

    if not todos_pdfs:
        print(json.dumps({
            "encontrado": True,
            "pasta_nome": pasta.get("name", ""),
            "pasta_id": pasta.get("id", ""),
            "total_pdfs": 0,
            "mensagem": "Pasta encontrada mas sem PDFs.",
            "pdfs": [],
        }, indent=2, ensure_ascii=False))
        sys.exit(0)

    # 3. Retorna TODOS os PDFs ordenados por data decrescente.
    #    A regra "exame de sangue mais atual" é aplicada na extração de conteúdo
    #    (extrair_exames_pdf.py), que mescla os resultados e prioriza os valores
    #    do PDF mais recente quando há duplicidade de exames.
    pdfs_finais = sorted(
        todos_pdfs,
        key=lambda x: x.get("modifiedTime", ""),
        reverse=True,
    )

    # 4. Formata saída — TODOS os PDFs são retornados para extração de conteúdo.
    #    Nunca filtrar apenas pelo nome do arquivo.
    resultado = []
    for arq in pdfs_finais:
        resultado.append({
            "nome": arq.get("name", ""),
            "id": arq.get("id", ""),
            "link": f"https://drive.google.com/file/d/{arq.get('id', '')}/view",
            "mimeType": arq.get("mimeType", ""),
            "modifiedTime": arq.get("modifiedTime", ""),
            "tipo": "sangue" if is_sangue(arq.get("name", "")) else "outro",
        })

    print(json.dumps({
        "encontrado": True,
        "pasta_nome": pasta.get("name", ""),
        "pasta_id": pasta.get("id", ""),
        "total_pdfs": len(resultado),
        "pdfs": resultado,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
