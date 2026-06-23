#!/usr/bin/env python3
"""CONSELHO DE GROWTH (Vital Slim) — submete UMA hipótese de crescimento à
MATRIZ DE RISCO/RETORNO e devolve scorecard + recomendação (perseguir/parquear/
matar). Carta: "submeter 1 hipótese de crescimento de maior potencial à matriz
de risco/retorno." Painel de lentes de growth via OpenRouter (Opus 4.8).

Uso: council_growth.py "<hipótese de crescimento>"
"""
import sys, json, urllib.request

def secret(path, key):
    try:
        for ln in open(path):
            if ln.startswith(key + "="): return ln.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception: pass
    return ""
KEY = secret("/root/.openclaw/secure/openrouter.env", "OPENROUTER_API_KEY") or secret("/root/.hermes/.env", "OPENROUTER_API_KEY")
MODEL = "anthropic/claude-opus-4.8"

def ask(system, user, max_tokens=1600, want_json=False):
    payload = {"model": MODEL, "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if want_json:
        payload["response_format"] = {"type": "json_object"}
    body = json.dumps(payload).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    d = json.loads(urllib.request.urlopen(req, timeout=200).read().decode())
    return d["choices"][0]["message"]["content"]

SYS = (
 "Voce e o CONSELHO DE GROWTH do Instituto Vital Slim (clinica de emagrecimento e saude hormonal da Dra. Daniely, "
 "modelo: leads via Instagram/Meta Ads -> Clara (WhatsApp) -> consulta R$1.000). Avalie UMA hipotese de crescimento "
 "passando por 5 LENTES (cada uma nota 0-10): (1) RETORNO potencial (impacto em receita/agendamentos); "
 "(2) PROBABILIDADE de sucesso/evidencia; (3) ESFORCO/custo (10=baixo esforco); (4) RISCO (10=baixo risco — a marca, "
 "compliance CFM, experiencia do paciente); (5) FIT com o momento do IVS. "
 "Calcule SCORE = (Retorno*Probabilidade)/(11-Esforco) ajustado pelo Risco. Recomende: PERSEGUIR AGORA / PARQUEAR / MATAR. "
 "Responda em Markdown pt-BR: tabela das 5 lentes (nota + 1 linha de justificativa), o veredito, os 2 maiores riscos, "
 "e o PRIMEIRO experimento barato p/ validar (com metrica de sucesso). Sem floreio.")

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    hyp = " ".join(sys.argv[1:])
    print(f"📈 CONSELHO DE GROWTH — matriz risco/retorno:\n{hyp}\n" + "=" * 60)
    out = ask(SYS, f"HIPOTESE DE CRESCIMENTO:\n{hyp}")
    print(out)

if __name__ == "__main__":
    main()
