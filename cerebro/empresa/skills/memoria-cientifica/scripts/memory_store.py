#!/usr/bin/env python3
"""
memory_store.py — Armazena pesquisa cientifica com indexacao semantica.

Estrutura de cada pesquisa:
/root/cerebro-vital-slim/cerebro/empresa/conhecimento/pesquisas/YYYY-MM-DD_slug/
├── source.json             # URLs, tipo de conteudo, metadados
├── original.md             # Conteudo original recebido
├── research.md             # Pesquisa aprofundada (Perplexity + PubMed)
├── clinical.md             # Aplicacao clinica pratica
├── summary.md              # Resumo curto (TL;DR) para Clara
├── embeddings.json         # Embeddings dos chunks (semantic search)
└── metadata.json           # Topic, tags, data, uso

Indice global:
/root/cerebro-vital-slim/cerebro/empresa/conhecimento/index/
├── master.jsonl            # Linha por pesquisa: slug, topic, tags, path, timestamp
├── embeddings.jsonl        # Linha por chunk: research_id, chunk_id, text, vec (gemini)
├── topics.json             # Taxonomia: topico -> list de pesquisas
└── keywords.json           # keyword -> list de pesquisas (backup de texto)
"""

import argparse
import json
import os
import re
import sys
import time
import hashlib
import urllib.request
from pathlib import Path
from datetime import datetime

BASE = Path("/root/cerebro-vital-slim/cerebro/empresa/conhecimento")
PESQUISAS = BASE / "pesquisas"
INDEX = BASE / "index"
TOPICOS = BASE / "topicos"
LOGS = BASE / "logs"

GEMINI_EMBED_MODEL = "gemini-embedding-001"
GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"


def slugify(text: str) -> str:
    """Converte texto em slug URL-safe."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")[:60]


def chunk_text(text: str, max_chars: int = 800) -> list:
    """Quebra texto em chunks preservando paragrafos."""
    chunks = []
    paragraphs = text.split("\n\n")
    current = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(current) + len(p) + 2 <= max_chars:
            current = (current + "\n\n" + p) if current else p
        else:
            if current:
                chunks.append(current)
            if len(p) > max_chars:
                # split long paragraph
                for i in range(0, len(p), max_chars):
                    chunks.append(p[i:i+max_chars])
                current = ""
            else:
                current = p
    if current:
        chunks.append(current)
    return chunks


def get_embedding(text: str, api_key: str, retries: int = 3) -> list:
    """Gera embedding via Gemini API (768 dims)."""
    url = GEMINI_EMBED_URL.format(model=GEMINI_EMBED_MODEL) + f"?key={api_key}"
    body = {
        "model": f"models/{GEMINI_EMBED_MODEL}",
        "content": {"parts": [{"text": text[:8000]}]},
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                response = json.loads(r.read())
            return response["embedding"]["values"]
        except Exception as e:
            if attempt == retries - 1:
                print(f"  Embedding falhou: {e}", file=sys.stderr)
                return []
            time.sleep(2 ** attempt)
    return []


def extract_keywords(text: str, max_keywords: int = 20) -> list:
    """Extrai keywords simples (palavras >4 chars, frequencia > 1)."""
    words = re.findall(r"\b[a-záéíóúâêôãõç]{4,}\b", text.lower())
    stop = {"para", "esta", "este", "sobre", "quando", "pode", "isso", "como", "mais", "mesmo",
            "entre", "porque", "depois", "antes", "muito", "pelo", "pela", "nesse", "dessa",
            "sendo", "todos", "todas", "algum", "outra", "outro", "dessa", "pelas", "pelos",
            "ainda", "onde", "seja", "qual", "suas", "meus", "minhas"}
    freq = {}
    for w in words:
        if w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1
    # Ordena por frequencia, pega os mais frequentes
    top = sorted(freq.items(), key=lambda x: -x[1])[:max_keywords]
    return [w for w, c in top if c >= 2]


def store_research(
    slug: str,
    topic: str,
    original_content: str,
    research_content: str,
    clinical_content: str,
    summary: str,
    source_urls: list = None,
    tags: list = None,
):
    """Armazena pesquisa com indexacao."""
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        print("AVISO: GOOGLE_API_KEY nao definida, pulando embeddings", file=sys.stderr)

    source_urls = source_urls or []
    tags = tags or []
    timestamp = datetime.now().strftime("%Y-%m-%d")
    research_id = f"{timestamp}_{slug}"
    research_dir = PESQUISAS / research_id
    research_dir.mkdir(parents=True, exist_ok=True)

    # 1. Salva arquivos markdown
    (research_dir / "original.md").write_text(original_content, encoding="utf-8")
    (research_dir / "research.md").write_text(research_content, encoding="utf-8")
    (research_dir / "clinical.md").write_text(clinical_content, encoding="utf-8")
    (research_dir / "summary.md").write_text(summary, encoding="utf-8")

    # 2. Metadata
    metadata = {
        "id": research_id,
        "slug": slug,
        "topic": topic,
        "tags": tags,
        "created_at": datetime.now().isoformat(),
        "source_urls": source_urls,
        "files": {
            "original": "original.md",
            "research": "research.md",
            "clinical": "clinical.md",
            "summary": "summary.md",
        },
        "stats": {
            "original_chars": len(original_content),
            "research_chars": len(research_content),
            "clinical_chars": len(clinical_content),
        },
    }
    (research_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 3. Source
    source = {"urls": source_urls, "type": "ingested", "date": timestamp}
    (research_dir / "source.json").write_text(
        json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 4. Embeddings (chunks de research + clinical + summary)
    full_text = f"TOPICO: {topic}\n\nRESUMO: {summary}\n\nPESQUISA:\n{research_content}\n\nAPLICACAO CLINICA:\n{clinical_content}"
    chunks = chunk_text(full_text)
    embeddings = []

    if api_key:
        print(f"  Gerando {len(chunks)} embeddings...")
        for i, chunk in enumerate(chunks):
            vec = get_embedding(chunk, api_key)
            if vec:
                embeddings.append({
                    "chunk_id": f"{research_id}#{i:03d}",
                    "text": chunk,
                    "vec": vec,
                })
            time.sleep(0.3)  # rate limit

    (research_dir / "embeddings.json").write_text(
        json.dumps({"chunks": embeddings}, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  {len(embeddings)} embeddings salvos em {research_dir}/embeddings.json")

    # 5. Atualiza indice global (append-only)
    INDEX.mkdir(parents=True, exist_ok=True)

    # 5a. master.jsonl (uma linha por pesquisa)
    master_entry = {
        "id": research_id,
        "slug": slug,
        "topic": topic,
        "tags": tags,
        "path": str(research_dir),
        "summary": summary,
        "created_at": metadata["created_at"],
        "keywords": extract_keywords(full_text),
    }
    with open(INDEX / "master.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(master_entry, ensure_ascii=False) + "\n")

    # 5b. embeddings.jsonl (uma linha por chunk)
    with open(INDEX / "embeddings.jsonl", "a", encoding="utf-8") as f:
        for emb in embeddings:
            row = {
                "research_id": research_id,
                "chunk_id": emb["chunk_id"],
                "text": emb["text"],
                "vec": emb["vec"],
                "topic": topic,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # 5c. topics.json (topico -> list de pesquisas)
    topics_path = INDEX / "topics.json"
    if topics_path.exists():
        topics = json.loads(topics_path.read_text(encoding="utf-8"))
    else:
        topics = {}
    topics.setdefault(topic, []).append({
        "id": research_id,
        "slug": slug,
        "summary": summary[:200],
        "created_at": metadata["created_at"],
    })
    topics_path.write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")

    # 5d. keywords.json (fallback textual)
    keywords_path = INDEX / "keywords.json"
    if keywords_path.exists():
        kwdict = json.loads(keywords_path.read_text(encoding="utf-8"))
    else:
        kwdict = {}
    for kw in master_entry["keywords"]:
        kwdict.setdefault(kw, []).append(research_id)
    keywords_path.write_text(json.dumps(kwdict, ensure_ascii=False, indent=2), encoding="utf-8")

    # 6. Link simbolico por topico para facilitar navegacao
    TOPICOS.mkdir(parents=True, exist_ok=True)
    topic_dir = TOPICOS / slugify(topic)
    topic_dir.mkdir(parents=True, exist_ok=True)
    symlink = topic_dir / research_id
    if not symlink.exists():
        try:
            symlink.symlink_to(research_dir)
        except Exception:
            pass

    # 7. Log
    log_path = LOGS / f"{timestamp}.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} STORED {research_id} topic={topic}\n")

    return research_id, research_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True, help="Slug curto (ex: creatina-cerebro)")
    ap.add_argument("--topic", required=True, help="Topico principal (ex: creatina)")
    ap.add_argument("--original", required=True, help="Arquivo ou texto original")
    ap.add_argument("--research", required=True, help="Pesquisa aprofundada")
    ap.add_argument("--clinical", required=True, help="Aplicacao clinica")
    ap.add_argument("--summary", required=True, help="Resumo TL;DR")
    ap.add_argument("--tags", default="", help="Tags separadas por virgula")
    ap.add_argument("--urls", default="", help="URLs separadas por virgula")
    args = ap.parse_args()

    # Le arquivos se for path
    def read_or_text(v):
        try:
            return Path(v).read_text(encoding="utf-8") if Path(v).is_file() else v
        except (OSError, ValueError):
            return v

    rid, path = store_research(
        slug=args.slug,
        topic=args.topic,
        original_content=read_or_text(args.original),
        research_content=read_or_text(args.research),
        clinical_content=read_or_text(args.clinical),
        summary=read_or_text(args.summary),
        source_urls=[u.strip() for u in args.urls.split(",") if u.strip()],
        tags=[t.strip() for t in args.tags.split(",") if t.strip()],
    )
    print(f"\nOK! Pesquisa armazenada:")
    print(f"  ID: {rid}")
    print(f"  Path: {path}")


if __name__ == "__main__":
    main()
