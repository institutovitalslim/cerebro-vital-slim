#!/usr/bin/env python3
"""Supervisor da MARIA (gerente): lê os transcripts de TODOS os agentes em disco,
revisa cada troca NOVA (pedido do Tiaro -> resposta do agente) e alerta o Tiaro
no @VitalSlimBot quando acha erro ou melhoria. Roda no cron (a cada poucos minutos).
Não intervém no chat do agente (sem ponto único de falha); sugere ao Tiaro."""
import json, glob, os, re, hashlib, urllib.request
from datetime import datetime, timezone

HERMES = {"Jarvis": "/root/.hermes/profiles/jarvis",
          "Pedro": "/root/.hermes/profiles/pedro",
          "Clara-Telegram": "/root/.hermes/profiles/clara",
          "Ana": "/root/.hermes/profiles/ana",
          "Joao": "/root/.hermes/profiles/joao",
          "Eduardo": "/root/.hermes/profiles/eduardo"}
OPENCLAW = {}
STATE = "/root/.hermes/maria_supervisor_state.json"
LOG = "/root/.hermes/maria_supervisor.log"
TIARO_CHAT = "971050173"

def log(m):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {m}"
    print(line)
    try: open(LOG, "a", encoding="utf-8").write(line + "\n")
    except Exception: pass

def secret(path, key):
    try:
        for ln in open(path):
            if ln.startswith(key + "="): return ln.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception: pass
    return ""

KEY = secret("/root/.openclaw/secure/openrouter.env", "OPENROUTER_API_KEY") or secret("/root/.hermes/.env", "OPENROUTER_API_KEY")
MARIA_TOKEN = secret("/root/.hermes/.env", "TELEGRAM_BOT_TOKEN")

def etext(content):
    if isinstance(content, str): return content
    if isinstance(content, list):
        return " ".join(p.get("text", "") for p in content if isinstance(p, dict))
    return ""

def hermes_recent(profile_dir, n=8):
    dumps = sorted(glob.glob(profile_dir + "/sessions/request_dump_*.json"), key=os.path.getmtime)
    turns = []
    for f in dumps[-3:]:
        try:
            d = json.load(open(f, encoding="utf-8"))
            b = d.get("request", {}).get("body")
            if isinstance(b, str): b = json.loads(b)
            for m in (b.get("messages") or []):
                if m.get("role") in ("user", "assistant"):
                    t = etext(m.get("content")).strip()
                    if t and (not turns or turns[-1][1] != t):
                        turns.append((m["role"], t))
        except Exception: pass
    return turns[-n:]

def openclaw_recent(sessions_dir, n=8):
    files = [f for f in glob.glob(sessions_dir + "/*.jsonl") if "trajectory" not in f and "bak" not in f]
    if not files: return []
    f = max(files, key=os.path.getmtime)
    turns = []
    try:
        for line in open(f, encoding="utf-8", errors="ignore"):
            try: d = json.loads(line)
            except Exception: continue
            if d.get("type") != "message": continue
            m = d.get("message") or {}
            if m.get("role") in ("user", "assistant"):
                t = etext(m.get("content")).strip()
                if t: turns.append((m["role"], t))
    except Exception: pass
    return turns[-n:]

def opus(sys_p, user_p, max_tokens=600):
    body = json.dumps({"model": "anthropic/claude-opus-4.8", "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}]}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=180).read().decode())["choices"][0]["message"]["content"]

SYS = (
 "Voce e a MARIA, Gerente Geral do Instituto Vital Slim, supervisionando a equipe de agentes de IA. "
 "Recebe a troca recente entre o TIARO (CEO) e o agente {AG}. Avalie com olhar de gestora: ha ERRO "
 "(factual, de politica, resposta incompleta/incorreta, promessa indevida, fora de escopo) OU uma MELHORIA "
 "clara (no pedido do Tiaro ou na resposta do agente)? Se SIM, responda em pt-BR com uma correcao CURTA e "
 "ACIONAVEL (1-3 linhas) que o Tiaro pode aplicar ou repassar ao agente — comece com o que esta errado e o "
 "que fazer. Se esta tudo certo ou e conversa trivial, responda EXATAMENTE: OK")

def review(agent, turns):
    convo = "\n".join(f"{'TIARO' if r == 'user' else agent.upper()}: {t[:700]}" for r, t in turns)
    try:
        return opus(SYS.replace("{AG}", agent), f"Troca recente do agente {agent}:\n\n{convo}").strip()
    except Exception as e:
        log(f"review_failed {agent}: {e}"); return "OK"

def alert(text):
    if not MARIA_TOKEN:
        log("sem MARIA_TOKEN, nao alerta"); return
    try:
        body = json.dumps({"chat_id": TIARO_CHAT, "text": text[:3900]}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{MARIA_TOKEN}/sendMessage",
            data=body, headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=30); log("alerta enviado")
    except Exception as e:
        log(f"alert_failed: {e}")

def main():
    state = {}
    if os.path.exists(STATE):
        try: state = json.load(open(STATE, encoding="utf-8"))
        except Exception: state = {}
    first_run = not state.get("_seeded")
    sources = [(a, hermes_recent, d) for a, d in HERMES.items()] + [(a, openclaw_recent, d) for a, d in OPENCLAW.items()]
    for agent, fn, src in sources:
        turns = fn(src)
        if not turns: continue
        h = hashlib.sha1("||".join(t for _, t in turns).encode("utf-8")).hexdigest()
        if state.get(agent) == h: continue          # nada novo
        state[agent] = h
        if first_run:                                 # 1a vez: so semeia, sem alertar (evita spam de historico)
            continue
        verdict = review(agent, turns)
        if verdict and verdict.strip().upper() != "OK" and not verdict.strip().upper().startswith("OK "):
            alert(f"\U0001F454 Maria — supervisão {agent}:\n{verdict}")
            log(f"{agent}: ISSUE -> alertado")
        else:
            log(f"{agent}: ok")
    state["_seeded"] = True
    json.dump(state, open(STATE, "w", encoding="utf-8"))

if __name__ == "__main__":
    main()
