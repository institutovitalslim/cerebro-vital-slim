#!/usr/bin/env python3
"""
photo_selector.py — Seleciona a melhor foto da Dra. para o tema do carrossel.

Logica:
1. Busca no catalog.json por similaridade semantica (embeddings)
2. Evita fotos usadas recentemente (usage.json - ultimos 30 dias)
3. Se nenhuma passar threshold (score >= 0.55) OU todas foram muito usadas:
   retorna a menos usada entre as top-5 matches ou sugere gerar variacao

Uso:
    python3 photo_selector.py --theme "retatrutide emagrecimento" --top-k 5
    python3 photo_selector.py --theme "..." --avoid-days 30
    python3 photo_selector.py --theme "..." --mark-used "Imagem PNG 11.png"
"""
import os, json, argparse, urllib.request, sys
from pathlib import Path
from datetime import datetime, timedelta

CATALOG_PATH = Path("/root/.openclaw/workspace/fotos_dra/catalog.json")
USAGE_PATH = Path("/root/.openclaw/workspace/fotos_dra/usage.json")
EMBED_MODEL = "gemini-embedding-001"


def cosine(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    num = sum(x*y for x, y in zip(a, b))
    na = sum(x*x for x in a)**0.5
    nb = sum(x*x for x in b)**0.5
    return num/(na*nb) if (na*nb) > 0 else 0.0


def get_theme_embedding(theme: str) -> list:
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        return []
    # Enriquece a query com contexto de foto
    query = (
        f"Tema de carrossel de saude/medicina: {theme}. "
        f"Foto de estudio profissional de medica adequada para capa deste tema."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBED_MODEL}:embedContent?key={key}"
    body = {"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": query[:8000]}]}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["embedding"]["values"]
    except Exception as e:
        print(f"  embedding query falhou: {e}", file=sys.stderr)
        return []


def load_catalog():
    if not CATALOG_PATH.exists():
        return {}
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def load_usage():
    if not USAGE_PATH.exists():
        return {"usage": {}}
    return json.loads(USAGE_PATH.read_text(encoding="utf-8"))


def save_usage(data):
    USAGE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def mark_photo_used(filename: str, theme: str = None):
    """Registra uso de uma foto (para evitar reutilizacao em breve)."""
    usage = load_usage()
    entry = usage["usage"].setdefault(filename, {"count": 0, "last_used": None, "themes": []})
    entry["count"] += 1
    entry["last_used"] = datetime.now().isoformat()
    if theme:
        entry["themes"].append({"theme": theme, "date": entry["last_used"]})
        # Mantem apenas ultimos 20
        entry["themes"] = entry["themes"][-20:]
    save_usage(usage)
    return entry


def select_best(theme: str, top_k: int = 5, avoid_days: int = 30, min_score: float = 0.55):
    """
    Retorna ranking de fotos adequadas ao tema.
    Ordem: score semantico * penalidade de uso recente.
    """
    catalog = load_catalog()
    usage = load_usage()["usage"]

    if not catalog:
        return {"error": "catalog vazio. Rode catalog_photos.py primeiro."}

    qvec = get_theme_embedding(theme)
    if not qvec:
        return {"error": "nao conseguiu gerar embedding do tema"}

    now = datetime.now()
    avoid_cutoff = now - timedelta(days=avoid_days)

    scored = []
    for fname, entry in catalog.items():
        vec = entry.get("embedding") or []
        if not vec:
            continue
        sim = cosine(qvec, vec)

        # Penalidade de uso recente
        u = usage.get(fname, {})
        last = u.get("last_used")
        count = u.get("count", 0)
        penalty = 1.0
        if last:
            try:
                last_dt = datetime.fromisoformat(last)
                days_ago = (now - last_dt).days
                if days_ago < avoid_days:
                    # Quanto mais recente e mais usado, mais penaliza
                    penalty = 1.0 - (0.5 * (avoid_days - days_ago) / avoid_days)
                    penalty = max(0.3, penalty)  # Minimo 0.3 pra nunca zerar totalmente
            except:
                pass
        # Tambem penaliza uso total
        if count > 3:
            penalty *= 0.85
        if count > 6:
            penalty *= 0.8

        final_score = sim * penalty
        scored.append({
            "filename": fname,
            "semantic_score": round(sim, 4),
            "penalty": round(penalty, 3),
            "final_score": round(final_score, 4),
            "usage_count": count,
            "last_used": last,
            "description": entry.get("description", {}).get("descricao_curta", ""),
            "adequate_themes": entry.get("description", {}).get("adequacao_temas", []),
        })

    scored.sort(key=lambda x: -x["final_score"])
    results = scored[:top_k]

    best = results[0] if results else None
    need_generation = not best or best["semantic_score"] < min_score

    return {
        "theme": theme,
        "best_match": best,
        "top_k": results,
        "needs_generation": need_generation,
        "reason": (
            "score semantico baixo, melhor gerar variacao" if need_generation
            else "match encontrado" if best["semantic_score"] >= 0.65
            else "match fraco mas utilizavel"
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", help="Tema do carrossel (ex: 'retatrutide emagrecimento')")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--avoid-days", type=int, default=30,
                    help="Dias para evitar fotos usadas (default 30)")
    ap.add_argument("--min-score", type=float, default=0.55,
                    help="Score minimo semantico (default 0.55)")
    ap.add_argument("--mark-used", help="Marca foto como usada (filename)")
    ap.add_argument("--with-theme", help="Tema associado ao --mark-used")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    if args.mark_used:
        entry = mark_photo_used(args.mark_used, args.with_theme)
        print(f"Marcada: {args.mark_used}")
        print(f"  Total uso: {entry['count']}x")
        print(f"  Ultimo uso: {entry['last_used']}")
        return

    if not args.theme:
        print("Use --theme '<tema>' ou --mark-used '<filename>'", file=sys.stderr)
        sys.exit(1)

    result = select_best(args.theme, args.top_k, args.avoid_days, args.min_score)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if "error" in result:
        print(f"ERRO: {result['error']}")
        sys.exit(1)

    print(f"\nTema: {result['theme']}")
    if result["needs_generation"]:
        print(f"\n⚠️  PRECISA GERAR VARIACAO (nenhuma foto com score suficiente)")
        print(f"   Sugestao: use generate_variation.py com a foto mais proxima como base:")
        if result["best_match"]:
            print(f"   → {result['best_match']['filename']} (score: {result['best_match']['semantic_score']})")
    else:
        best = result["best_match"]
        print(f"\n✅ MELHOR MATCH: {best['filename']}")
        print(f"   Score semantico: {best['semantic_score']}")
        print(f"   Penalidade uso: {best['penalty']} (usada {best['usage_count']}x)")
        print(f"   Score final: {best['final_score']}")
        print(f"   Descricao: {best['description']}")
        print(f"   Temas adequados: {', '.join(best['adequate_themes'][:5])}")

    print(f"\nTop {len(result['top_k'])} ranking:")
    for i, r in enumerate(result["top_k"], 1):
        usage_str = f"(usada {r['usage_count']}x)" if r["usage_count"] > 0 else "(nunca usada)"
        print(f"  [{i}] {r['final_score']:.3f} | {r['filename']} {usage_str}")
        print(f"      {r['description'][:100]}")


if __name__ == "__main__":
    main()
