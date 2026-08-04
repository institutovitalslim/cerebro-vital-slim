# -*- coding: utf-8 -*-
"""
virality_library.py — BIBLIOTECA DE BOAS PRÁTICAS auto-retroalimentada (Content Engine OS).

Loop de aprendizado:
  gerar conteúdo -> Virality Predictor (brain_activity) -> record() guarda o resultado ->
  distill() destila os resultados acumulados em boas práticas (LLM) -> guidance() é LIDA
  pelo diretor criativo ANTES de cada nova geração. Quanto mais conteúdo, mais afiada fica.

Armazenamento: storage/virality_library/  (runs/*.json + best_practices.md + best_practices.json)
Consultar SEMPRE antes de gerar: `from virality_library import guidance; g = guidance()`.
"""
from __future__ import annotations
import os, sys, json, glob, re, datetime
import urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from creative_compliance import _api_key, VISION_MODEL

LIB = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/virality_library"
RUNS = f"{LIB}/runs"
BP_MD = f"{LIB}/best_practices.md"
BP_JSON = f"{LIB}/best_practices.json"


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def record(creative_id: str, prediction: dict, context: dict | None = None, ts: str | None = None) -> str:
    """Guarda 1 resultado do Virality Predictor na biblioteca e re-destila as boas práticas."""
    os.makedirs(RUNS, exist_ok=True)
    ts = ts or _now()
    keep = {k: prediction.get(k) for k in ("index_0_100", "verdict", "hook_score", "avg", "peak",
                                           "peak_s", "retention_delta", "weak_seconds", "advice", "scores")}
    entry = {"ts": ts, "creative_id": creative_id, "context": context or {}, "prediction": keep}
    path = f"{RUNS}/{ts}_{creative_id[:12]}.json"
    json.dump(entry, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    try:
        distill()
    except Exception as e:
        print("distill falhou (nao-fatal):", str(e)[:120])
    return path


def _load_runs() -> list[dict]:
    out = []
    for f in sorted(glob.glob(f"{RUNS}/*.json")):
        try:
            out.append(json.load(open(f, encoding="utf-8")))
        except Exception:
            pass
    return out


def _chat(system: str, user: str, model: str = VISION_MODEL, max_tokens: int = 3000) -> str:
    # REGRA DO TIARO: nunca OpenRouter; sempre Codex GPT-5.5 via gateway OAuth.
    from codex_llm import chat
    return chat(system, user)


def _aggregate(runs: list[dict]) -> dict:
    n = len(runs)
    idx = [r["prediction"].get("index_0_100") for r in runs if r["prediction"].get("index_0_100") is not None]
    hooks = [r["prediction"].get("hook_score") for r in runs if r["prediction"].get("hook_score") is not None]
    weak = {}
    for r in runs:
        for s in (r["prediction"].get("weak_seconds") or []):
            weak[s] = weak.get(s, 0) + 1
    return {"n_runs": n, "avg_index": round(sum(idx) / len(idx), 1) if idx else None,
            "avg_hook": round(sum(hooks) / len(hooks), 3) if hooks else None,
            "weak_seconds_freq": dict(sorted(weak.items(), key=lambda x: -x[1]))}


def distill(model: str = VISION_MODEL) -> str:
    """Destila os resultados acumulados em best_practices.md (consultado antes de gerar)."""
    os.makedirs(LIB, exist_ok=True)
    runs = _load_runs()
    agg = _aggregate(runs)
    prev = open(BP_MD, encoding="utf-8").read() if os.path.exists(BP_MD) else "(vazio)"
    runs_brief = [{"cid": r["creative_id"], "ctx": r.get("context", {}),
                   "idx": r["prediction"].get("index_0_100"), "hook": r["prediction"].get("hook_score"),
                   "peak_s": r["prediction"].get("peak_s"), "ret": r["prediction"].get("retention_delta"),
                   "weak": r["prediction"].get("weak_seconds"), "advice": r["prediction"].get("advice")}
                  for r in runs[-40:]]
    system = (
        "Voce e o EDITOR de uma biblioteca de BOAS PRATICAS DE VIRALIZACAO auto-atualizada para reels verticais "
        "curtos do Instituto Vital Slim (medicina/mulheres 40+ com sobrepeso). Os dados vem do Virality Predictor "
        "do Higgsfield (brain_activity): index 0-100, hook_score, segundos fracos, pico, retencao e conselhos. "
        "Destile TUDO em um guia CONCISO e ACIONAVEL que o diretor criativo le ANTES de gerar cada reel. "
        "Foque no que FAZ O INDICE SUBIR: gancho (0-4s), ritmo/cortes, escolha de cena/visual, transicoes, retencao, "
        "CTA. Use regras objetivas (Faca / Evite) e cite padroes observados nos dados (ex.: 'hook fraco quando X'). "
        "Atualize/mescle com o guia anterior, sem inchar — mantenha enxuto e pratico. Responda em MARKDOWN."
    )
    user = (f"AGREGADO: {json.dumps(agg, ensure_ascii=False)}\n\n"
            f"RUNS (ultimas {len(runs_brief)}): {json.dumps(runs_brief, ensure_ascii=False)[:6000]}\n\n"
            f"GUIA ANTERIOR:\n{prev[:4000]}\n\n"
            "Gere o GUIA ATUALIZADO (markdown), comecando com '# Boas Praticas de Viralizacao — IVS Content OS'.")
    md = _chat(system, user, model=model)
    md = re.sub(r"^```[a-zA-Z]*\n?|```$", "", md.strip())
    header = f"<!-- auto-atualizado {_now()} | {agg['n_runs']} runs | indice medio {agg.get('avg_index')} -->\n"
    open(BP_MD, "w", encoding="utf-8").write(header + md)
    json.dump({"updated": _now(), "aggregate": agg}, open(BP_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return BP_MD


def guidance(max_chars: int = 2600) -> str:
    """Boas práticas atuais p/ injetar no diretor antes de gerar. Vazio se a biblioteca ainda nao existe."""
    if not os.path.exists(BP_MD):
        return ""
    txt = open(BP_MD, encoding="utf-8").read()
    txt = re.sub(r"^<!--.*?-->\n", "", txt)  # tira o comentario de metadados
    return txt[:max_chars]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "distill":
        print("ok ->", distill())
    elif cmd == "show":
        print(guidance())
    elif cmd == "agg":
        print(json.dumps(_aggregate(_load_runs()), ensure_ascii=False, indent=2))
