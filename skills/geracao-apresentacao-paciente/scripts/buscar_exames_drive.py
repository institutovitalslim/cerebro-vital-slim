#!/usr/bin/env python3
"""
Busca exames de um paciente no Google Drive (conta medicalcontabilidade@gmail.com).

A pasta base é: 1dCDANfnUcTX-iRFCCNtipQ5a3NWzHzSL
Dentro dela, procura uma subpasta com o nome do paciente (case-insensitive).
Lista todos os arquivos PDF encontrados na pasta do paciente.

Uso:
    python3 buscar_exames_drive.py "Nome do Paciente"
    
Saída: JSON com lista de arquivos PDF encontrados (nome, id, link)
"""

import sys
import json
import subprocess
import re

DRIVE_FOLDER_ID = "1dCDANfnUcTX-iRFCCNtipQ5a3NWzHzSL"
GOG_ACCOUNT = "medicalcontabilidade@gmail.com"


def gog_drive_search(query, max_results=50):
    """Executa busca no Google Drive via gog."""
    cmd = [
        "/usr/local/bin/gog", "drive", "search", query,
        "--max", str(max_results),
        "--json"
    ]
    env = {"GOG_ACCOUNT": GOG_ACCOUNT, "HOME": "/root", "GOG_KEYRING_PASSWORD": "Tf100314@!"}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERRO gog drive: {result.stderr}", file=sys.stderr)
        return []
    try:
        data = json.loads(result.stdout)
        return data.get("files", [])
    except json.JSONDecodeError:
        print(f"ERRO: resposta inválida do gog: {result.stdout[:200]}", file=sys.stderr)
        return []


def encontrar_pasta_paciente(nome_paciente):
    """
    Encontra a pasta do paciente dentro da pasta base.
    Faz busca case-insensitive e com normalização.
    """
    # Busca todas as subpastas da pasta base
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    pastas = gog_drive_search(query, max_results=100)
    
    # Normaliza o nome do paciente para comparação
    nome_norm = re.sub(r'[^a-zA-Z0-9]', '', nome_paciente).upper()
    
    melhor_match = None
    melhor_score = 0
    
    for pasta in pastas:
        pasta_nome = pasta.get("name", "").upper()
        pasta_nome_norm = re.sub(r'[^a-zA-Z0-9]', '', pasta_nome)
        
        # Match exato
        if nome_norm == pasta_nome_norm:
            return pasta
        
        # Match parcial: conta quantas palavras do nome do paciente aparecem na pasta
        palavras_nome = set(re.split(r'[^A-Z0-9]+', nome_paciente.upper()))
        palavras_pasta = set(re.split(r'[^A-Z0-9]+', pasta_nome))
        palavras_comuns = palavras_nome & palavras_pasta
        
        # Ignora palavras muito curtas (DE, DA, DO, etc)
        palavras_comuns = {p for p in palavras_comuns if len(p) > 2}
        
        score = len(palavras_comuns)
        if score > melhor_score:
            melhor_score = score
            melhor_match = pasta
    
    # Retorna o melhor match se tiver pelo menos 3 palavras significativas em comum
    if melhor_match and melhor_score >= 2:
        return melhor_match
    
    return None


def listar_pdfs_na_pasta(pasta_id):
    """Lista todos os PDFs dentro de uma pasta do Drive."""
    query = f"'{pasta_id}' in parents and mimeType = 'application/pdf'"
    arquivos = gog_drive_search(query, max_results=50)
    
    resultados = []
    for arq in arquivos:
        resultados.append({
            "nome": arq.get("name", ""),
            "id": arq.get("id", ""),
            "link": f"https://drive.google.com/file/d/{arq.get('id', '')}/view",
            "mimeType": arq.get("mimeType", ""),
            "createdTime": arq.get("createdTime", ""),
        })
    return resultados


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 buscar_exames_drive.py 'Nome do Paciente'")
        sys.exit(1)
    
    nome_paciente = sys.argv[1]
    
    pasta = encontrar_pasta_paciente(nome_paciente)
    if not pasta:
        print(json.dumps({
            "encontrado": False,
            "mensagem": f"Pasta do paciente '{nome_paciente}' não encontrada no Drive.",
            "pdfs": []
        }, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    pdfs = listar_pdfs_na_pasta(pasta["id"])
    
    print(json.dumps({
        "encontrado": True,
        "pasta_nome": pasta.get("name", ""),
        "pasta_id": pasta.get("id", ""),
        "total_pdfs": len(pdfs),
        "pdfs": pdfs
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
