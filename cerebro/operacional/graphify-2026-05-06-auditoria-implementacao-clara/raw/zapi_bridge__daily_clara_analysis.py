#!/usr/bin/env python3
# daily_clara_analysis.py - Cron diario 00:00 BRT
import json, os, re, subprocess, sys, urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

SPREADSHEET_ID = "1QXvRhElCx1t7mxMAwGkcvh5V7YyKLjP9zozSGH7LHnM"
ACCOUNT = "institutovitalslim@gmail.com"
RAW_SHEET = "Folha1"

BRIDGE_DIR = Path("/root/.openclaw/workspace/ops/zapi_bridge")
ROLLING_FILE = BRIDGE_DIR / "clara_learnings_rolling.md"
ROLLING_MAX_DAYS = 7

CEREBRO_DIR = Path("/root/cerebro-vital-slim")
LOGS_DIR = CEREBRO_DIR / "cerebro" / "logs" / "clara-learnings"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "moonshotai/kimi-k2.6"

LOCK_FILE = Path("/tmp/daily_clara_analysis.lock")
LOG_FILE = Path("/var/log/daily_clara_analysis.log")


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = "[" + ts + "] " + str(msg)
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def require_lock():
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            os.kill(pid, 0)
            log("another run alive pid=" + str(pid))
            sys.exit(0)
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    LOCK_FILE.write_text(str(os.getpid()))


def release_lock():
    try:
        LOCK_FILE.unlink()
    except Exception:
        pass


def get_openrouter_key():
    for path in [Path("/root/.openclaw/secure/openrouter.env"), BRIDGE_DIR / "zapi_bridge.env"]:
        if path.exists():
            for line in path.read_text().splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    if key and not key.startswith("op://"):
                        return key
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def setup_gog_env():
    if not os.environ.get("GOG_KEYRING_PASSWORD"):
        sa_env = "/root/.openclaw/.op.service-account.env"
        if os.path.isfile(sa_env):
            with open(sa_env) as f:
                for line in f:
                    if line.startswith("OP_SERVICE_ACCOUNT_TOKEN="):
                        os.environ["OP_SERVICE_ACCOUNT_TOKEN"] = line.split("=", 1)[1].strip()
        try:
            r = subprocess.run(["op", "item", "get", "gog-keyring-pass", "--vault", "openclaw",
                                "--fields", "password", "--reveal"],
                               capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                os.environ["GOG_KEYRING_PASSWORD"] = r.stdout.strip()
        except Exception as e:
            log("gog keyring: " + str(e))
    os.environ["GOG_ACCOUNT"] = ACCOUNT


def fetch_sheet_rows():
    cmd = ["gog", "sheets", "get", "-a", ACCOUNT, SPREADSHEET_ID, RAW_SHEET + "!A1:J20000", "-j"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        log("gog sheets failed: " + (r.stderr or "")[:300])
        return []
    try:
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        return data.get("values", [])
    except Exception as e:
        log("json parse failed: " + str(e))
        return []


def normalize_phone(phone):
    digits = re.sub(r"\D", "", str(phone))
    if digits.startswith("55") and len(digits) >= 12:
        return digits[-11:]
    return digits


def parse_rows(rows, since_ts):
    msgs = []
    for r in rows[1:]:
        if len(r) < 10:
            continue
        ts_str, _, mtype, phone, sender, chat, fromMe, msgid, moment, text = r[:10]
        if not phone or not text:
            continue
        try:
            moment_ms = int(moment)
        except Exception:
            continue
        if moment_ms < since_ts * 1000:
            continue
        msgs.append({
            "phone": normalize_phone(phone),
            "sender": sender,
            "from_me": str(fromMe).upper() == "TRUE",
            "text": text,
            "moment": moment_ms,
        })
    return msgs


def cluster_conversations(msgs):
    convos = defaultdict(list)
    for m in msgs:
        convos[m["phone"]].append(m)
    for k in convos:
        convos[k].sort(key=lambda x: x["moment"])
    return convos


WIN_RX = re.compile(r"\b(confirmo|confirmado|agendada|fechado|combinado|pix enviado|paguei|pagamento feito|quero marcar|pode marcar|marcado)\b", re.I)
DROP_RX = re.compile(r"\b(vou pensar|vou conversar|te aviso|por enquanto|agora nao|mais pra frente)\b", re.I)


def extract_signals(msgs, convos):
    inbound = [m["text"] for m in msgs if not m["from_me"] and m["text"]]
    outbound = [m["text"] for m in msgs if m["from_me"] and m["text"]]
    openings = []
    for phone, conv in convos.items():
        for m in conv:
            if not m["from_me"] and m["text"]:
                openings.append(m["text"].strip()[:150])
                break
    wins, drops = [], []
    for phone, conv in convos.items():
        inbound_side = [m for m in conv if not m["from_me"]]
        if not inbound_side:
            continue
        for i, m in enumerate(conv):
            if not m["from_me"] and WIN_RX.search(m["text"] or ""):
                for j in range(i - 1, -1, -1):
                    if conv[j]["from_me"]:
                        wins.append({"closer": conv[j]["text"][:400], "win": m["text"][:200]})
                        break
                break
        for i, m in enumerate(conv):
            if not m["from_me"] and DROP_RX.search(m["text"] or ""):
                for j in range(i - 1, -1, -1):
                    if conv[j]["from_me"]:
                        drops.append({"last": conv[j]["text"][:400], "drop": m["text"][:200]})
                        break
                break
    return {
        "total_messages": len(msgs),
        "total_inbound": len(inbound),
        "total_outbound": len(outbound),
        "unique_leads": len(convos),
        "openings": openings,
        "wins": wins,
        "drops": drops,
        "inbound_samples": inbound[:40],
    }


def call_kimi_for_insights(signals, day_str):
    key = get_openrouter_key()
    if not key:
        log("no openrouter key")
        return None
    NL = "\n"
    ob = NL.join("- " + (o or "")[:150] for o in signals["openings"][:30])
    ib = NL.join("- " + (t or "").replace(NL, " ")[:200] for t in signals["inbound_samples"][:30])
    wb = NL.join("- CLOSER: " + w["closer"][:300] + NL + "  WIN: " + w["win"][:100] for w in signals["wins"][:10])
    db = NL.join("- ULTIMA: " + d["last"][:300] + NL + "  DROP: " + d["drop"][:100] for d in signals["drops"][:10])
    context = (
        "Data: " + day_str + NL +
        "Total de mensagens: " + str(signals["total_messages"]) + NL +
        "Leads unicos: " + str(signals["unique_leads"]) + NL +
        "Recebidas: " + str(signals["total_inbound"]) + " | Enviadas: " + str(signals["total_outbound"]) + NL +
        "Vitorias: " + str(len(signals["wins"])) + " | Drops: " + str(len(signals["drops"])) + NL + NL +
        "=== ABERTURAS DE LEADS ===" + NL + ob + NL + NL +
        "=== MENSAGENS RECEBIDAS (amostra) ===" + NL + ib + NL + NL +
        "=== VITORIAS (msg enviada antes do lead confirmar) ===" + NL + wb + NL + NL +
        "=== DROPS (msg enviada antes do lead dizer vou pensar) ===" + NL + db + NL
    )
    system = (
        "Voce e consultor comercial senior auditando conversas de WhatsApp da clinica Instituto Vital Slim. "
        "Extraia APRENDIZADOS OPERACIONAIS ACIONAVEIS para a Clara (IA concierge) usar nas proximas conversas." + NL +
        "REGRAS: Foco em padroes observados NOS DADOS. Seja CONCRETO - cite frases reais. "
        "No maximo 5 aprendizados. Menos dados = menos aprendizados. Nao invente."
    )
    user = (
        "Dados abaixo. Extraia 2 a 5 aprendizados acionaveis. Formato obrigatorio:" + NL + NL +
        "## [N]. [Nome curto do padrao]" + NL +
        "**Observacao:** [o que voce viu, com exemplo literal]" + NL +
        "**Acao para a Clara:** [regra ou frase concreta que ela deve aplicar]" + NL + NL +
        "Se insuficiente: responda SOMENTE: SEM_APRENDIZADOS_NOVOS - volume insuficiente" + NL + NL +
        context
    )
    payload = {"model": OPENROUTER_MODEL,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}],
               "temperature": 0.3}
    headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json",
               "HTTP-Referer": "https://institutovitalslim.com.br",
               "X-Title": "Clara Daily Learnings"}
    req = urllib.request.Request(OPENROUTER_URL, data=json.dumps(payload).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode())
        choices = data.get("choices") or []
        if not choices:
            return None
        content = choices[0].get("message", {}).get("content", "")
        if isinstance(content, list):
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        return content.strip() or None
    except Exception as e:
        log("kimi failed: " + str(e))
        return None


def build_daily_report(day_str, signals, insights):
    NL = "\n"
    body = insights if insights else "_Sem aprendizados hoje._"
    parts = [
        "# Licoes diarias da Clara - " + day_str, "",
        "> Gerado automaticamente em " + datetime.now(timezone.utc).isoformat(), "",
        "## Contadores do dia", "",
        "- Mensagens totais: **" + str(signals["total_messages"]) + "**",
        "- Leads unicos: **" + str(signals["unique_leads"]) + "**",
        "- Recebidas: " + str(signals["total_inbound"]) + " | Enviadas: " + str(signals["total_outbound"]),
        "- Vitorias: **" + str(len(signals["wins"])) + "**",
        "- Drops: **" + str(len(signals["drops"])) + "**", "",
        "## Aprendizados extraidos", "", body,
    ]
    return NL.join(parts).strip() + NL


def update_rolling(day_str, insights):
    if not insights or insights.startswith("SEM_APRENDIZADOS_NOVOS"):
        log("skip rolling")
        return
    entries = []
    if ROLLING_FILE.exists():
        raw = ROLLING_FILE.read_text(encoding="utf-8")
        chunks = re.split(r"(?=^# \[\d{4}-\d{2}-\d{2}\])", raw, flags=re.MULTILINE)
        for c in chunks:
            c = c.strip()
            if c and c.startswith("# ["):
                entries.append(c)
    new_entry = "# [" + day_str + "]\n\n" + insights.strip()
    entries = [new_entry] + [e for e in entries if not e.startswith("# [" + day_str + "]")]
    entries = entries[:ROLLING_MAX_DAYS]
    header = ("# Observacoes recentes (rolling buffer, ultimos 7 dias)\n\n"
              "> Atualizado automaticamente pelo cron daily_clara_analysis toda meia-noite (00:00 BRT).\n"
              "> Prioridade secundaria as regras absolutas do prompt principal.\n\n---\n\n")
    body = "\n\n---\n\n".join(entries)
    ROLLING_FILE.write_text(header + body + "\n", encoding="utf-8")
    log("rolling updated entries=" + str(len(entries)))


def git_commit_push(day_str, report_path):
    try:
        subprocess.run(["git", "-C", str(CEREBRO_DIR), "add", str(report_path.relative_to(CEREBRO_DIR))],
                       check=True, capture_output=True, text=True, timeout=30)
        r = subprocess.run(["git", "-C", str(CEREBRO_DIR), "commit", "-m",
                            "Daily Clara learnings " + day_str + " (auto)"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0 and "nothing to commit" in (r.stdout + r.stderr).lower():
            log("nothing to commit")
            return
        subprocess.run(["git", "-C", str(CEREBRO_DIR), "push", "origin", "main"],
                       check=True, capture_output=True, text=True, timeout=60)
        log("git pushed: " + report_path.name)
    except Exception as e:
        log("git push failed: " + str(e))


def main():
    require_lock()
    try:
        now = datetime.now(timezone.utc)
        since = now - timedelta(hours=24)
        day_str = since.strftime("%Y-%m-%d")
        log("start " + since.isoformat() + " -> " + now.isoformat())
        setup_gog_env()
        rows = fetch_sheet_rows()
        if not rows:
            log("no rows")
            return
        log("rows=" + str(len(rows)))
        msgs = parse_rows(rows, int(since.timestamp()))
        if not msgs:
            signals = {"total_messages": 0, "total_inbound": 0, "total_outbound": 0,
                       "unique_leads": 0, "openings": [], "wins": [], "drops": [], "inbound_samples": []}
            insights = "SEM_APRENDIZADOS_NOVOS - sem mensagens nas ultimas 24h"
        else:
            convos = cluster_conversations(msgs)
            signals = extract_signals(msgs, convos)
            log("signals msgs=" + str(signals["total_messages"]) + " leads=" + str(signals["unique_leads"]) +
                " wins=" + str(len(signals["wins"])) + " drops=" + str(len(signals["drops"])))
            insights = call_kimi_for_insights(signals, day_str) or "SEM_APRENDIZADOS_NOVOS - falha na extracao"
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = LOGS_DIR / (day_str + ".md")
        report_path.write_text(build_daily_report(day_str, signals, insights), encoding="utf-8")
        log("report written: " + str(report_path))
        update_rolling(day_str, insights)
        git_commit_push(day_str, report_path)
        log("done")
    finally:
        release_lock()


if __name__ == "__main__":
    main()
