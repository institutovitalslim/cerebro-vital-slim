#!/usr/bin/env python3
"""Skill da Ana — Google/Gemini (conta institutovitalslim@gmail.com): resumos
cientificos + graficos. Tenta a API Gemini (chave renovada no env canonico do
OpenClaw); se a chave falhar, sinaliza fallback p/ sessao logada no Chrome.

Uso:
  ana_google.py summarize <arquivo|->         # resumo cientifico estruturado
  ana_google.py graph <arquivo|-> [saida.png] # extrai dados -> grafico PNG
  ana_google.py check                         # so testa o acesso
"""
import os, sys, json, urllib.request, subprocess

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]

def resolve_google_key():
    """Mesma resolucao da skill memoria-cientifica (conta institutovitalslim)."""
    for envp in ("/root/.openclaw/.env.runtime", "/root/.openclaw/.env",
                 "/root/.openclaw/secure/google.env", "/root/.openclaw/secure/gemini.env"):
        try:
            for ln in open(envp):
                ln = ln.strip()
                for k in ("GOOGLE_API_KEY=", "GEMINI_API_KEY="):
                    if ln.startswith(k):
                        return ln.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    for v in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        if os.environ.get(v):
            return os.environ[v].strip()
    return ""

def gemini(prompt, want_json=False, key=None):
    key = key or resolve_google_key()
    if not key:
        raise RuntimeError("NO_KEY")
    cfg = {"responseMimeType": "application/json"} if want_json else {}
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                       "generationConfig": cfg}).encode()
    last = ""
    for m in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            d = json.loads(urllib.request.urlopen(req, timeout=90).read().decode())
            if "candidates" in d:
                return d["candidates"][0]["content"]["parts"][0]["text"], m
            last = d.get("error", {}).get("message", "")[:140]
        except Exception as e:
            last = str(e)[:140]
    raise RuntimeError("GEMINI_FAIL: " + last)

def summarize(text):
    p = ("Voce e a Ana, pesquisadora medica do Instituto Vital Slim. Resuma o material cientifico abaixo "
         "em pt-BR, estruturado: **Tema**, **Principais achados** (bullets), **Metodologia/nivel de evidencia**, "
         "**Aplicacao clinica no IVS**, **Ressalvas**. Fiel, sem inventar.\n\n=== MATERIAL ===\n" + text[:60000])
    out, model = gemini(p)
    return out, model

def make_graph(text, outpng):
    p = ("Extraia do material abaixo dados quantitativos para UM grafico. Responda SO em JSON: "
         '{"title":"...","type":"bar|line","x_label":"...","y_label":"...","labels":[...],"values":[...]}. '
         "Se nao houver dados numericos claros, retorne {\"error\":\"sem dados numericos\"}.\n\n=== MATERIAL ===\n" + text[:40000])
    raw, model = gemini(p, want_json=True)
    spec = json.loads(raw)
    if spec.get("error"):
        return None, spec["error"]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 5))
    if spec.get("type") == "line":
        ax.plot(spec["labels"], spec["values"], marker="o", color="#1f7a5a")
    else:
        ax.bar(spec["labels"], spec["values"], color="#1f7a5a")
    ax.set_title(spec.get("title", "")); ax.set_xlabel(spec.get("x_label", "")); ax.set_ylabel(spec.get("y_label", ""))
    plt.xticks(rotation=30, ha="right"); plt.tight_layout()
    fig.savefig(outpng, dpi=130); plt.close(fig)
    return outpng, model

def read_in(arg):
    if arg == "-":
        return sys.stdin.read()
    return open(arg, encoding="utf-8", errors="ignore").read()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        try:
            out, m = gemini("Responda so: OK")
            print(f"GEMINI OK (modelo {m}): {out.strip()[:30]}")
        except Exception as e:
            print(f"GEMINI FALHOU: {e}\n-> usar fallback de sessao logada no Chrome (institutovitalslim).")
            sys.exit(2)
    elif cmd == "summarize":
        out, m = summarize(read_in(sys.argv[2]))
        print(f"[resumo via {m}]\n{out}")
    elif cmd == "graph":
        outpng = sys.argv[3] if len(sys.argv) > 3 else "/root/.hermes/profiles/ana/grafico.png"
        res, info = make_graph(read_in(sys.argv[2]), outpng)
        print(f"grafico: {res} (via {info})" if res else f"sem grafico: {info}")
    else:
        print(__doc__)
