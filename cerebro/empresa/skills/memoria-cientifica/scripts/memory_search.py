#!/usr/bin/env python3
"""
memory_search.py — Busca semantica na memoria cientifica da Clara.

Uso:
    python3 memory_search.py --query "como magnesio afeta sono"
    python3 memory_search.py --query "..." --top-k 5 --format json
    python3 memory_search.py --topic "creatina"  # lista por topico
    python3 memory_search.py --list-topics        # mostra taxonomia

Retorna chunks relevantes ordenados por similaridade cosseno.
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

BASE = Path("/root/cerebro-vital-slim/cerebro/empresa/conhecimento")
INDEX = BASE / "index"

GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"


def get_query_embedding(query: str, api_key: str) -> list:
    body = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": query[:8000]}]},
    }
    url = GEMINI_EMBED_URL + f"?key={api_key}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["embedding"]["values"]


def cosine(a: list, b: list) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    num = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


def load_all_embeddings():
    """Carrega todos os embeddings do indice global."""
    path = INDEX / "embeddings.jsonl"
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except:
                    pass
    return rows


def search_semantic(query: str, top_k: int = 5, topic_filter: str = None):
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        print("ERRO: GOOGLE_API_KEY nao definida", file=sys.stderr)
        return []

    try:
        qvec = get_query_embedding(query, api_key)
    except Exception as e:
        print(f"ERRO embedding da query: {e}", file=sys.stderr)
        return []

    rows = load_all_embeddings()
    if not rows:
        return []

    scored = []
    for row in rows:
        if topic_filter and row.get("topic", "").lower() != topic_filter.lower():
            continue
        score = cosine(qvec, row["vec"])
        scored.append((score, row))

    scored.sort(key=lambda x: -x[0])
    return scored[:top_k]


def search_keyword(query: str, top_k: int = 5):
    """Fallback textual se embeddings falharem."""
    kw_path = INDEX / "keywords.json"
    master_path = INDEX / "master.jsonl"
    if not kw_path.exists() or not master_path.exists():
        return []

    kwdict = json.loads(kw_path.read_text(encoding="utf-8"))
    words = [w for w in query.lower().split() if len(w) > 3]

    # Score por pesquisa: soma de matches
    from collections import Counter
    rid_scores = Counter()
    for w in words:
        if w in kwdict:
            for rid in kwdict[w]:
                rid_scores[rid] += 1

    # Carrega master
    master = {}
    with open(master_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                master[e["id"]] = e

    results = []
    for rid, score in rid_scores.most_common(top_k):
        if rid in master:
            results.append((score, master[rid]))
    return results


def list_topics():
    topics_path = INDEX / "topics.json"
    if not topics_path.exists():
        return {}
    return json.loads(topics_path.read_text(encoding="utf-8"))


def format_result(scored, mode: str = "text"):
    if mode == "json":
        out = []
        for score, row in scored:
            out.append({
                "score": round(score, 4),
                "research_id": row.get("research_id") or row.get("id"),
                "topic": row.get("topic"),
                "text": row.get("text", row.get("summary", ""))[:500],
            })
        return json.dumps(out, ensure_ascii=False, indent=2)

    # text mode
    lines = []
    for i, (score, row) in enumerate(scored, 1):
        rid = row.get("research_id") or row.get("id")
        lines.append(f"\n[{i}] score={score:.4f} | {row.get('topic')} | {rid}")
        lines.append(f"    {row.get('text', row.get('summary', ''))[:400]}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", help="Query semantica")
    ap.add_argument("--topic", help="Filtra por topico (ou lista pesquisas do topico)")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--list-topics", action="store_true", help="Lista todos os topicos")
    ap.add_argument("--keyword-only", action="store_true", help="Usa busca textual (sem embeddings)")
    args = ap.parse_args()

    if args.list_topics:
        topics = list_topics()
        for topic, entries in sorted(topics.items()):
            print(f"\n## {topic} ({len(entries)} pesquisa(s))")
            for e in entries:
                print(f"  - {e['id']}: {e['summary'][:120]}")
        return

    if args.topic and not args.query:
        # Lista pesquisas do topico
        topics = list_topics()
        entries = topics.get(args.topic, [])
        if not entries:
            print(f"Nenhuma pesquisa para topico '{args.topic}'")
            return
        print(f"Pesquisas do topico '{args.topic}':")
        for e in entries:
            print(f"  - {e['id']}: {e['summary'][:150]}")
        return

    if not args.query:
        print("Use --query ou --topic ou --list-topics", file=sys.stderr)
        sys.exit(1)

    if args.keyword_only:
        results = search_keyword(args.query, args.top_k)
    else:
        results = search_semantic(args.query, args.top_k, args.topic)

    if not results:
        print("Nenhum resultado encontrado.")
        # Tenta fallback
        if not args.keyword_only:
            print("Tentando busca textual...")
            results = search_keyword(args.query, args.top_k)

    print(format_result(results, args.format))


if __name__ == "__main__":
    main()
