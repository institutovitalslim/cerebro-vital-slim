#!/usr/bin/env python3
"""
ingest_content.py — Pipeline completo quando Clara recebe conteudo novo.

Fluxo:
1. Recebe conteudo (URL, arquivo PDF/imagem, ou texto)
2. Faz fetch/OCR/parse para extrair texto
3. Aprofunda via Perplexity API (busca cientifica)
4. Sintetiza aplicacao clinica pratica
5. Gera resumo
6. Chama memory_store.py para indexar e salvar
7. Retorna resumo estruturado para apresentacao ao usuario

Uso:
    python3 ingest_content.py --url "https://example.com/paper.html" --topic creatina
    python3 ingest_content.py --file /path/to/paper.pdf --topic magnesio
    python3 ingest_content.py --text "conteudo direto" --topic vitamina-d --slug vitamina-d-imunidade
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path("/root/cerebro-vital-slim/cerebro/empresa/skills/memoria-cientifica/scripts")
STORE_SCRIPT = SCRIPTS_DIR / "memory_store.py"
SEARCH_SCRIPT = SCRIPTS_DIR / "memory_search.py"

GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")[:60]


def fetch_url(url: str) -> str:
    """Baixa conteudo da URL. Para PubMed, usa capture_pubmed.py se for PMID."""
    # Detecta PMID
    pmid_match = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", url)
    if pmid_match:
        pmid = pmid_match.group(1)
        # Usa eutils para metadata estruturada
        eurl = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        eabs = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=text"
        try:
            with urllib.request.urlopen(eurl, timeout=30) as r:
                meta = json.loads(r.read()).get("result", {}).get(pmid, {})
            with urllib.request.urlopen(eabs, timeout=30) as r:
                abstract = r.read().decode("utf-8", errors="ignore")
            title = meta.get("title", "")
            authors = ", ".join(a.get("name", "") for a in meta.get("authors", [])[:10])
            journal = meta.get("fulljournalname", "")
            doi = next((x.get("value") for x in meta.get("articleids", []) if x.get("idtype") == "doi"), "")
            return f"TITLE: {title}\nAUTHORS: {authors}\nJOURNAL: {journal}\nDOI: {doi}\nPMID: {pmid}\n\nABSTRACT:\n{abstract}"
        except Exception as e:
            print(f"  PubMed fetch failed: {e}", file=sys.stderr)

    # URL generica
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", errors="ignore")
        # Tenta extrair texto de HTML
        if "<html" in raw.lower():
            text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:20000]
        return raw[:20000]
    except Exception as e:
        return f"[ERRO ao baixar URL: {e}]"


def read_file(path: str) -> str:
    """Le arquivo texto/PDF/imagem (OCR via Chromium/tesseract se necessario)."""
    p = Path(path)
    if not p.exists():
        return f"[ARQUIVO NAO ENCONTRADO: {path}]"

    suffix = p.suffix.lower()
    if suffix in [".txt", ".md"]:
        return p.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        # Tenta pdftotext
        try:
            result = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True, timeout=60)
            return result.stdout[:50000]
        except FileNotFoundError:
            return f"[PDF requer pdftotext - install: apt install poppler-utils]"
    if suffix in [".jpg", ".jpeg", ".png"]:
        # OCR via tesseract
        try:
            result = subprocess.run(["tesseract", str(p), "-", "-l", "por+eng"],
                                    capture_output=True, text=True, timeout=60)
            return result.stdout[:50000]
        except FileNotFoundError:
            return f"[Imagem requer tesseract - install: apt install tesseract-ocr tesseract-ocr-por]"
    return p.read_text(encoding="utf-8", errors="ignore")


def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """Chama Gemini para gerar sintese."""
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        return "[GOOGLE_API_KEY nao definida]"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read())
        parts = resp["candidates"][0]["content"]["parts"]
        return "\n".join(p.get("text", "") for p in parts if "text" in p)
    except Exception as e:
        return f"[Gemini erro: {e}]"


def call_perplexity(query: str) -> str:
    """Chama Perplexity API via 1Password CLI (como faz deep-research)."""
    try:
        # Busca a key do Perplexity via op CLI
        key_result = subprocess.run(
            ["op", "item", "get", "Perplexity API", "--vault", "openclaw",
             "--field", "credential", "--reveal"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ,
                 "OP_SERVICE_ACCOUNT_TOKEN": os.environ.get("OP_SERVICE_ACCOUNT_TOKEN", "")}
        )
        if key_result.returncode != 0:
            return f"[Perplexity key nao disponivel: {key_result.stderr[:200]}]"
        pplx_key = key_result.stdout.strip()
    except FileNotFoundError:
        return "[1Password CLI (op) nao instalado]"
    except Exception as e:
        return f"[Erro ao buscar Perplexity key: {e}]"

    url = "https://api.perplexity.ai/chat/completions"
    body = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": (
                "Voce e um assistente de pesquisa cientifica. Responda em portugues. "
                "Sempre cite fontes (PubMed, DOI, journal). Foque em evidencias de estudos clinicos. "
                "Estruture em: 1) Mecanismo biologico, 2) Estudos principais, 3) Dosagem e seguranca, "
                "4) Contraindicacoes, 5) Evidencias contradictorias."
            )},
            {"role": "user", "content": query},
        ],
        "temperature": 0.2,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Authorization": f"Bearer {pplx_key}", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read())
        msg = resp["choices"][0]["message"]
        text = msg.get("content", "")
        # Se tiver citations
        citations = resp.get("citations", [])
        if citations:
            text += "\n\n**Fontes citadas:**\n"
            for i, c in enumerate(citations, 1):
                text += f"{i}. {c}\n"
        return text
    except Exception as e:
        return f"[Perplexity erro: {e}]"


def deep_research(content: str, topic: str) -> str:
    """Combina Perplexity + Gemini para pesquisa aprofundada."""
    preview = content[:3000]
    query = (
        f"Pesquisa cientifica aprofundada sobre '{topic}'. "
        f"Contexto inicial:\n\n{preview}\n\n"
        f"Aprofunde o tema buscando: mecanismo biologico, estudos clinicos recentes (meta-analises "
        f"e ECRs), dosagem segura, contraindicacoes, efeitos adversos, e aplicacoes clinicas em "
        f"emagrecimento/longevidade/cognicao/performance. Cite PubMed IDs e DOIs."
    )

    print("  Consultando Perplexity...")
    perplexity_result = call_perplexity(query)

    # Se Perplexity falhar, usa Gemini com busca
    if perplexity_result.startswith("["):
        print("  Perplexity indisponivel, usando Gemini...")
        gemini_prompt = (
            f"Voce e um medico pesquisador. Faca uma revisao cientifica aprofundada do tema "
            f"'{topic}' com base no conteudo abaixo. Inclua mecanismo de acao, evidencias de "
            f"estudos (meta-analises, ECRs, PMIDs quando souber), dosagem, contraindicacoes, "
            f"e populacoes que mais se beneficiam.\n\nConteudo:\n{preview}"
        )
        return call_gemini(gemini_prompt)

    return perplexity_result


def clinical_application(research: str, topic: str) -> str:
    """Gera aplicacao clinica pratica no Instituto Vital Slim."""
    prompt = f"""Voce e consultor clinico do Instituto Vital Slim, clinica de emagrecimento,
longevidade e saude metabolica, comandada pela Dra. Daniely Freitas.

Com base na pesquisa cientifica abaixo sobre "{topic}", crie um guia PRATICO de aplicacao
clinica para a Dra. Daniely usar com seus pacientes. Inclua:

1. **Quando prescrever**: perfil de paciente ideal (idade, condicao, sintomas)
2. **Como prescrever**: dose, forma farmaceutica, horario, duracao do tratamento
3. **Combinacoes sinergicas**: outros suplementos/nutrientes que potencializam
4. **Monitoramento**: exames para pedir antes, durante e apos
5. **Sinais de alerta**: quando suspender ou ajustar
6. **Como explicar ao paciente**: linguagem simples para conversa no consultorio
7. **Criterios de exclusao**: casos em que NAO usar

PESQUISA CIENTIFICA:
{research}

Responda em portugues, em formato markdown, focado em praticidade clinica."""
    return call_gemini(prompt)


def generate_summary(research: str, clinical: str, topic: str) -> str:
    """Gera resumo TL;DR conciso."""
    prompt = f"""Crie um RESUMO executivo (maximo 250 palavras) sobre '{topic}' combinando a
pesquisa cientifica e a aplicacao clinica abaixo. Estruture em:

- **O que e**: 1-2 frases explicando o tema
- **Evidencia**: principais achados cientificos (com PMIDs se souber)
- **Para quem**: perfil de paciente que se beneficia
- **Como usar na clinica**: dose, forma, tempo
- **Atencao**: principais contraindicacoes

PESQUISA:
{research[:3000]}

CLINICA:
{clinical[:2000]}

Responda em portugues, sem jargao desnecessario, direto ao ponto."""
    return call_gemini(prompt)


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="URL (PubMed, artigo, blog)")
    src.add_argument("--file", help="Arquivo local (PDF, imagem, texto)")
    src.add_argument("--text", help="Texto direto")
    ap.add_argument("--topic", required=True, help="Topico principal (ex: creatina)")
    ap.add_argument("--slug", help="Slug curto (auto-gerado se omitido)")
    ap.add_argument("--tags", default="", help="Tags separadas por virgula")
    ap.add_argument("--skip-store", action="store_true", help="So roda research, nao salva")
    args = ap.parse_args()

    # 1. Extrai conteudo
    print("=== 1. Extraindo conteudo ===")
    if args.url:
        content = fetch_url(args.url)
        source_urls = [args.url]
    elif args.file:
        content = read_file(args.file)
        source_urls = []
    else:
        content = args.text
        source_urls = []
    print(f"  {len(content)} caracteres extraidos")

    # 2. Research aprofundado
    print("\n=== 2. Pesquisa aprofundada (Perplexity/Gemini) ===")
    research = deep_research(content, args.topic)
    print(f"  {len(research)} caracteres de pesquisa")

    # 3. Aplicacao clinica
    print("\n=== 3. Aplicacao clinica no Instituto Vital Slim ===")
    clinical = clinical_application(research, args.topic)
    print(f"  {len(clinical)} caracteres de aplicacao clinica")

    # 4. Resumo
    print("\n=== 4. Resumo TL;DR ===")
    summary = generate_summary(research, clinical, args.topic)
    print(f"  {len(summary)} caracteres de resumo")

    # 5. Armazena
    slug = args.slug or slugify(args.topic)
    if not args.skip_store:
        print("\n=== 5. Armazenando com indexacao semantica ===")
        cmd = [
            "python3", str(STORE_SCRIPT),
            "--slug", slug,
            "--topic", args.topic,
            "--original", content,
            "--research", research,
            "--clinical", clinical,
            "--summary", summary,
            "--tags", args.tags,
            "--urls", ",".join(source_urls),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print(result.stdout)
        if result.returncode != 0:
            print("ERRO:", result.stderr, file=sys.stderr)

    # 6. Output para apresentacao ao usuario
    print("\n" + "=" * 70)
    print("RESUMO PARA APRESENTACAO AO USUARIO:")
    print("=" * 70)
    print(summary)
    print("\n" + "=" * 70)
    print("APLICACAO CLINICA (completa):")
    print("=" * 70)
    print(clinical)


if __name__ == "__main__":
    main()
