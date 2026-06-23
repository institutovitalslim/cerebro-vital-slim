#!/usr/bin/env python3
"""Ponte de aprendizado DURAVEL da Clara (fecha o loop que estava quebrado).

Fluxo: le conversas reais do audit spool Z-API -> Opus extrai aprendizados
operacionais NOVOS (dedup vs permanent_knowledge + reconciliacao com regras duras
RC-34/40/44/46/50) -> anexa ao permanent_knowledge (unico canal que o bridge le)
-> PORTAO DE REGRESSAO (roda a bateria; REVERTE se quebrar) -> alerta o Tiaro
e separa conflitos. Idempotente por dia. Roda no cron apos a analise diaria.
"""
import json, urllib.request, subprocess, glob, os, re, shutil, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

AUDIT_DIR = Path("/root/.openclaw/workspace/ops/zapi_bridge/audit")
PERM = Path("/root/.openclaw/workspace/ops/zapi_bridge/clara_permanent_knowledge.md")
REGRESSION = "/root/.openclaw/workspace/ops/zapi_bridge/clara_patient_regression_tests.py"
LOG = Path("/root/.openclaw/workspace/ops/zapi_bridge/clara_learning_promote_daily.log")
CONFLICTS = Path("/root/.openclaw/workspace/ops/zapi_bridge/clara_learning_conflicts_pending.md")
CORE_MARKER = "recuperado do treino diário"   # fim do bloco-nucleo estavel
CAP = 38000                                   # mantem abaixo do cap do loader (40000)
BRT = timezone(timedelta(hours=-3))
TIARO_CHAT = "971050173"

def log(m):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {m}"
    print(line)
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def secret(path, key):
    try:
        for ln in open(path):
            if ln.startswith(key + "="):
                return ln.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return ""

def get_key(name, files):
    for p in files:
        v = secret(p, name)
        if v:
            return v
    return os.getenv(name, "")

ENVS = ["/root/.openclaw/secure/openrouter.env", "/root/.hermes/.env",
        "/root/.openclaw/workspace/ops/zapi_bridge/zapi_bridge.env"]
OPENROUTER_KEY = get_key("OPENROUTER_API_KEY", ENVS)

EXCLUSIONS_FILE = "/root/.openclaw/workspace/ops/zapi_bridge/clara_exclusions.json"

# Numeros internos (equipe/Tiaro) — NUNCA sao lead; alertas operacionais vao pra ca.
NOTIFY_PHONES = {"5571986968887", "5571991574827"}

def _digits(p):
    return re.sub(r"\D", "", p or "")

def phone_keys(p):
    """Chaves comparaveis de um telefone (tolera DDI/DDD e o 9 do celular BR)."""
    d = _digits(p)
    keys = set()
    if len(d) >= 8:
        keys.add(d)
        keys.add(d[-10:])
        keys.add(d[-8:])   # ultimos 8 digitos = ancora estavel
    return keys

def load_patient_keys():
    """Lista canonica de PACIENTES/bloqueados (clara_exclusions.json). Conversa com
    paciente NUNCA entra no aprendizado — a Clara so conduz LEAD."""
    keys = set()
    try:
        import json as _j
        data = _j.load(open(EXCLUSIONS_FILE, encoding="utf-8"))
        for ph in (data.get("phones") or {}):
            keys |= phone_keys(ph)
    except Exception as e:
        log(f"exclusions_load_failed (fail-safe: sem aprendizado): {e}")
        return None  # None => sinaliza para abortar (nao arriscar aprender de paciente)
    return keys
# Marcadores de conteudo de SISTEMA/INTERNO que nao e conversa Clara<->lead.
SYSTEM_MARKERS = (
    "alerta operacional", "congratulations on your new bot", "use this token",
    "não há atendimentos", "nao ha atendimentos", "healthcheck", "phone_hash",
    "message_hash", "t.me/", "botfather", "bom dia! não há", "[bridge",
)

def load_recent_conversations(days=1):
    """Le as ultimas mensagens reais Clara<->lead do audit spool, anonimizadas.
    FILTRA mensagens internas/sistema (alertas a equipe, BotFather, healthchecks)
    para nao poluir o aprendizado com conteudo que nao e conversa de paciente."""
    patient_keys = load_patient_keys()
    if patient_keys is None:
        log("ABORT: nao consegui carregar exclusoes de paciente; nao aprendo para nao usar dado de paciente")
        return ""
    files = sorted(AUDIT_DIR.glob("zapi_webhook_events_*.jsonl"))[-(days + 1):]
    rows = []
    skipped_patients = 0
    for fp in files:
        try:
            for line in fp.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    it = json.loads(line)
                except Exception:
                    continue
                txt = str(it.get("text") or "").strip()
                if not txt:
                    continue
                phone = str(it.get("phone") or "")
                low = txt.lower()
                # descarta internos: numeros da equipe, grupos, @lid de sistema, conteudo de sistema
                if phone in NOTIFY_PHONES:
                    continue
                if it.get("is_group"):
                    continue
                # EXCLUSAO DE PACIENTE: conversa com paciente NUNCA entra no aprendizado
                if phone_keys(phone) & patient_keys:
                    skipped_patients += 1
                    continue
                if any(mk in low for mk in SYSTEM_MARKERS):
                    continue
                if "@lid" in phone and it.get("from_me"):
                    continue  # auto-chats/dispositivos do Tiaro capturados no spool
                # ROTULO CRITICO: from_api=True => Clara (automatico); from_me sem from_api => HUMANO assumiu
                if it.get("from_me"):
                    role = "CLARA(auto)" if it.get("from_api") else "HUMANO(takeover)"
                else:
                    role = "LEAD"
                ts = str(it.get("received_at_utc") or "")[:16]
                rows.append(f"{ts} {role}: {re.sub(r'\\s+', ' ', txt)[:600]}")
        except Exception as e:
            log(f"audit_read_failed {fp}: {e}")
    log(f"conversas LEAD: {len(rows)} msgs | pacientes excluidos: {skipped_patients} msgs")
    # anonimizacao defensiva
    text = "\n".join(rows[-400:])
    text = re.sub(r"55\d{9,13}", "[tel]", text)
    return text

def opus(messages, max_tokens=4000):
    body = json.dumps({"model": "anthropic/claude-opus-4.8", "max_tokens": max_tokens,
                       "messages": messages}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=600).read().decode())["choices"][0]["message"]["content"]

def telegram_alert(msg):
    token = get_key("TELEGRAM_BOT_TOKEN", ["/root/.hermes/profiles/clara/.env",
                    "/root/.hermes/.env"]) or get_key("TELEGRAM_TOKEN", ["/root/.openclaw/openclaw.json"])
    if not token:
        log("telegram_alert: sem token, pulando")
        return
    try:
        body = json.dumps({"chat_id": TIARO_CHAT, "text": msg[:3900]}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",
            data=body, headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=30)
        log("telegram_alert enviado")
    except Exception as e:
        log(f"telegram_alert_failed: {e}")

def sync_to_cerebro():
    """Replica o conhecimento permanente + conflitos para o cerebro (git) — evolui no cerebro tambem."""
    try:
        dest = "/root/cerebro-vital-slim/cerebro/operacional/clara-conhecimento-permanente"
        os.makedirs(dest, exist_ok=True)
        shutil.copy2(str(PERM), dest + "/clara_permanent_knowledge.md")
        if CONFLICTS.exists():
            shutil.copy2(str(CONFLICTS), dest + "/clara_conflitos_pendentes.md")
        g = ["git", "-C", "/root/cerebro-vital-slim"]
        subprocess.run(g + ["add", "cerebro/operacional/clara-conhecimento-permanente/"], timeout=60)
        subprocess.run(g + ["-c", "user.email=clara@ivs", "-c", "user.name=Clara Learning",
                            "commit", "-m", "Clara: aprendizado diario sincronizado ao cerebro"], timeout=60)
        subprocess.run(g + ["push"], timeout=120)
        log("cerebro sincronizado")
    except Exception as e:
        log(f"cerebro_sync_failed (nao-fatal): {e}")

def enforce_cap(text):
    """Se passar do CAP, remove os blocos diarios MAIS ANTIGOS (preserva o nucleo)."""
    if len(text) <= CAP:
        return text
    idx = text.find(CORE_MARKER)
    head = text[:idx] if idx >= 0 else text[: CAP // 2]
    blocks = re.split(r"(?=\n### Aprendizados \[\d{4}-\d{2}-\d{2}\])", text[len(head):])
    while len("".join([head] + blocks)) > CAP and len(blocks) > 1:
        # remove o bloco diario mais antigo (primeiro que casa o padrao)
        for i, b in enumerate(blocks):
            if b.lstrip().startswith("### Aprendizados ["):
                log(f"cap: removendo bloco antigo: {b[:60].strip()}")
                blocks.pop(i)
                break
        else:
            break
    return "".join([head] + blocks)

def main():
    if not OPENROUTER_KEY:
        log("ERRO: sem OPENROUTER_API_KEY"); sys.exit(1)
    day = datetime.now(BRT).strftime("%Y-%m-%d")
    perm = PERM.read_text(encoding="utf-8") if PERM.exists() else ""
    if f"### Aprendizados [{day}]" in perm:
        log(f"ja processado hoje ({day}); saindo"); return

    convos = load_recent_conversations(days=1)
    if len(convos) < 200:
        log(f"poucas conversas hoje ({len(convos)} chars); nada a aprender"); return

    SYS = (
        "Voce e engenheiro de conhecimento da agente CLARA (concierge WhatsApp do Instituto Vital Slim). "
        "PAPEIS nas conversas: 'LEAD' = paciente potencial; 'CLARA(auto)' = resposta automatica da Clara; "
        "'HUMANO(takeover)' = quando o Tiaro/equipe ASSUME o atendimento (geralmente PORQUE a Clara errou — "
        "a Clara para automaticamente quando um humano assume). TRATAMENTO: as mensagens 'HUMANO(takeover)' sao o "
        "PADRAO-OURO a EMULAR (como um humano experiente conduziu); as 'CLARA(auto)' que precederam um takeover ou "
        "geraram atrito sao ANTI-PADROES a corrigir. NUNCA atribua a Clara o que foi dito por HUMANO. "
        "A partir das CONVERSAS REAIS de hoje, extraia APENAS aprendizados operacionais NOVOS e acionaveis "
        "(o que a Clara deve passar a fazer, espelhando o humano; o que deve parar de fazer): "
        "abertura, preco/convenio, exames, sintomas hormonais, agendamento, tom, objecoes, guardrails. "
        "ESCOPO — APRENDA SO DE LEAD (captacao/agendamento da 1a consulta). ESTRATEGIA CENTRAL: SPIN selling "
        "para evoluir a CONSCIENCIA do lead sobre a necessidade da solucao medica para o problema dele e, "
        "SO ENTAO (no momento certo, com valor ja construido), informar o preco da consulta R$1.000 COM o "
        "desconto autorizado (R$100 fechando na hora => R$900; parcelavel R$300 pre + saldo; cashback de R$900 "
        "como credito se aderir ao Programa no dia). Esses valores de CONSULTA sao AUTORIZADOS — NAO trate "
        "R$1.000/R$900/R$300/parcelamento/cashback como conflito nem como erro de numero. So sinalize conflito se "
        "a Clara violar a politica de verdade: divulgar valor de PROGRAMA/acompanhamento pre-consulta (proibido RC-01), "
        "dar desconto de 35%/valor de paciente recorrente (so humano RC-07) ou inventar valor nao autorizado. "
        "O aprendizado de preco e sobre TIMING: preco cedo/sem valor = erro; preco apos SPIN e consciencia = certo. "
        "REGRAS: (1) DEDUPLIQUE contra o CONHECIMENTO ATUAL — so traga o que ainda NAO esta la. "
        "(2) RECONCILIE com as regras duras, NUNCA contradiga: RC-34 (nome so apos lead confirmar), "
        "RC-40/RC-50 (nao jogar preco cedo; transparente so quando o lead insistir, sustentar valor antes), "
        "RC-44 (anuncio generico nao agenda direto), RC-46 (sempre continuar a conversa). "
        "(3) Cada aprendizado = regra acionavel curta + frase-modelo quando util. (4) SEM PII. "
        "Responda em JSON puro: {\"additions\":\"<markdown dos aprendizados novos, ou string vazia se nada novo>\", "
        "\"conflicts\":\"<markdown de qualquer coisa que conflite com regra dura e precise decisao do Tiaro, ou vazio>\", "
        "\"summary\":\"<1-2 frases do que foi aprendido hoje>\"}. Se nao houver nada novo seguro, additions=\"\"."
    )
    try:
        raw = opus([{"role": "system", "content": SYS},
                    {"role": "user", "content": "CONHECIMENTO ATUAL:\n\n" + perm[-12000:] +
                     "\n\n===== CONVERSAS REAIS DE HOJE =====\n\n" + convos}], max_tokens=3500)
    except Exception as e:
        log(f"opus_failed: {e}"); sys.exit(1)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?|\n?```$", "", raw).strip()
    try:
        data = json.loads(raw)
    except Exception as e:
        log(f"json_parse_failed: {e} | raw={raw[:300]}"); sys.exit(1)

    additions = (data.get("additions") or "").strip()
    conflicts = (data.get("conflicts") or "").strip()
    summary = (data.get("summary") or "").strip()

    if conflicts:
        with CONFLICTS.open("a", encoding="utf-8") as f:
            f.write(f"\n\n## [{day}] conflitos/decisoes\n{conflicts}\n")

    if not additions:
        log(f"nada novo seguro hoje. summary={summary}")
        telegram_alert(f"🧠 Clara aprendizado {day}: nada novo seguro pra promover.\n{summary}"
                       + (f"\n⚠️ Conflitos p/ decidir:\n{conflicts[:1500]}" if conflicts else ""))
        return

    # PROMOVE com portao de regressao
    backup = str(PERM) + f".bak-autopromote-{datetime.now(BRT).strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(PERM, backup)
    new_text = perm.rstrip() + f"\n\n### Aprendizados [{day}]\n> Promovido automaticamente das conversas reais (com portao de regressao).\n\n{additions}\n"
    new_text = enforce_cap(new_text)
    PERM.write_text(new_text, encoding="utf-8")

    rc = subprocess.run(["python3", REGRESSION], capture_output=True, text=True, timeout=400)
    passed = ('"ok": true' in rc.stdout) or ('"ok":true' in rc.stdout)
    if not passed:
        shutil.copy2(backup, PERM)
        log(f"REGRESSAO FALHOU — revertido. stdout_tail={rc.stdout[-400:]}")
        telegram_alert(f"⚠️ Clara aprendizado {day}: tentei promover mas a REGRESSAO FALHOU — revertido, nada mudou. Verificar.")
        sys.exit(1)
    log(f"promovido OK ({len(additions)} chars). perm={len(new_text)} chars. summary={summary}")
    sync_to_cerebro()
    telegram_alert(f"🧠 Clara aprendizado {day} promovido (regressao OK):\n{summary}"
                   + (f"\n\n⚠️ Conflitos p/ sua decisao:\n{conflicts[:1500]}" if conflicts else ""))

if __name__ == "__main__":
    main()
