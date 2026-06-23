#!/usr/bin/env python3
"""LLM-COUNCIL — stress-test adversarial de uma DECISÃO de alto impacto por
múltiplos LLMs diversos (via OpenRouter). NÃO executa a decisão: só delibera,
expõe riscos e dá um veredito consolidado. Carta: "usar stress-test em uma
decisão de alto impacto, sem executar a decisão automaticamente."

Uso: council_llm.py "<decisão/pergunta de alto impacto>"
"""
import sys, json, urllib.request, concurrent.futures as cf

def secret(path, key):
    try:
        for ln in open(path):
            if ln.startswith(key + "="): return ln.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception: pass
    return ""
KEY = secret("/root/.openclaw/secure/openrouter.env", "OPENROUTER_API_KEY") or secret("/root/.hermes/.env", "OPENROUTER_API_KEY")

# Conselheiros = modelos DIVERSOS (provedores diferentes) p/ diversidade real de falha
COUNCIL = [
    ("Opus 4.8", "anthropic/claude-opus-4.8"),
    ("GPT-5.5", "openai/gpt-5.5"),
    ("Kimi K2.6", "moonshotai/kimi-k2.6"),
    ("Gemini 2.5 Pro", "google/gemini-2.5-pro"),
]
SYNTH = "anthropic/claude-opus-4.8"

def ask(model, system, user, max_tokens=900):
    body = json.dumps({"model": model, "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    d = json.loads(urllib.request.urlopen(req, timeout=180).read().decode())
    return d["choices"][0]["message"]["content"] if "choices" in d else "[falha: " + str(d.get("error", {}).get("message", ""))[:80] + "]"

MEMBER_SYS = ("Voce e um conselheiro CETICO num conselho de decisao do Instituto Vital Slim (clinica de emagrecimento/saude). "
    "Faca STRESS-TEST da decisao: aponte os MAIORES riscos, premissas frageis, modos de falha, e o que poderia dar errado. "
    "Termine com seu VEREDITO: APROVAR / APROVAR COM RESSALVAS / NAO APROVAR + 1 frase. Seja direto, pt-BR, sem floreio. Max 12 linhas.")

def member(args):
    name, model, decision = args
    try:
        return name, ask(model, MEMBER_SYS, f"DECISAO DE ALTO IMPACTO:\n{decision}")
    except Exception as e:
        return name, f"[indisponivel: {str(e)[:60]}]"

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    decision = " ".join(sys.argv[1:])
    print(f"🏛️  LLM-COUNCIL — stress-test (NAO executa):\n{decision}\n" + "=" * 60)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        votes = list(ex.map(member, [(n, m, decision) for n, m in COUNCIL]))
    transcript = ""
    for name, op in votes:
        print(f"\n## {name}\n{op}")
        transcript += f"\n### {name}\n{op}\n"
    synth = ask(SYNTH,
        "Voce e o presidente do conselho. Consolide os pareceres num VEREDITO EXECUTIVO pt-BR: "
        "(1) Riscos criticos em comum; (2) Divergencias; (3) Veredito final (Aprovar/Ressalvas/Nao aprovar) + condicoes; "
        "(4) Proximo passo. NUNCA executar a decisao — so recomendar. Conciso.",
        f"DECISAO:\n{decision}\n\nPARECERES:\n{transcript}", max_tokens=1100)
    print("\n" + "=" * 60 + f"\n🎯 VEREDITO CONSOLIDADO (presidente):\n{synth}")

if __name__ == "__main__":
    main()
