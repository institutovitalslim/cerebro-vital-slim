#!/usr/bin/env bash
# ops/diag/openclaw-gateway.sh
#
# Diagnostico focado: por que openclaw-gateway.service esta com Failed to start.
# Cobre system mode E user mode (systemd[1153]: nos logs sugere user manager).
# Coleta status, journal, unit files, binario do openclaw, dependencias de auth
# e tenta identificar a causa concreta do crash. Redige segredos, sobe pra paste.
#
# Uso (na VPS, root):
#   cd /root/cerebro-vital-slim && bash ops/diag/openclaw-gateway.sh

set +e
shopt -s nullglob

TS="$(date +%Y%m%d-%H%M%S)"
TMP="$(mktemp)"
REDACTED="$(mktemp)"
trap 'rm -f "$TMP" "$REDACTED"' EXIT

section() { printf '\n===== %s =====\n' "$1" >> "$TMP"; }

redact() {
  sed -E \
    -e 's/[0-9]{8,}:[A-Za-z0-9_-]{30,}/[REDACTED_BOT_TOKEN]/g' \
    -e 's/sk-[A-Za-z0-9_-]{20,}/[REDACTED_API_KEY]/g' \
    -e 's/(ey[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,})/[REDACTED_JWT]/g' \
    -e 's/((TOKEN|KEY|SECRET|PASSWORD|PASSWD|APIKEY)[A-Z_]*[[:space:]]*[:=][[:space:]]*)["'"'"']?[^"'"'"'[:space:],]+/\1[REDACTED]/gI' \
    -e 's/(Authorization:[[:space:]]*Bearer[[:space:]]+)[A-Za-z0-9._~+/=-]+/\1[REDACTED]/gI' \
    -e 's/(\"token\"[[:space:]]*:[[:space:]]*)"[^"]+"/\1"[REDACTED]"/g'
}

{
  echo "=== DIAG OPENCLAW GATEWAY ==="
  echo "timestamp: $(date -Is)"
  echo "host: $(hostname)"
} > "$TMP"

echo "[1/9] systemctl status (system)..."
section "systemctl status openclaw-gateway (system)"
systemctl status openclaw-gateway --no-pager -l 2>&1 | head -60 >> "$TMP"

echo "[2/9] systemctl status (user)..."
section "systemctl --user status openclaw-gateway"
systemctl --user status openclaw-gateway --no-pager -l 2>&1 | head -60 >> "$TMP"

echo "[3/9] journal (system)..."
section "journalctl -u openclaw-gateway (system, 200)"
journalctl -u openclaw-gateway --no-pager -n 200 2>&1 | tail -200 >> "$TMP"

echo "[4/9] journal (user)..."
section "journalctl --user -u openclaw-gateway (200)"
journalctl --user -u openclaw-gateway --no-pager -n 200 2>&1 | tail -200 >> "$TMP"

echo "[5/9] unit files..."
section "unit files openclaw*"
find /etc/systemd /lib/systemd /usr/lib/systemd /root/.config/systemd /home/*/.config/systemd \
  -maxdepth 6 -name 'openclaw*' 2>/dev/null | while read -r f; do
  echo "--- $f ---" >> "$TMP"
  cat "$f" 2>/dev/null >> "$TMP"
  echo "" >> "$TMP"
done

echo "[6/9] binario openclaw..."
section "binario openclaw"
which openclaw >> "$TMP" 2>&1
which claw >> "$TMP" 2>&1
ls -la /usr/lib/node_modules/openclaw 2>/dev/null | head -10 >> "$TMP"
ls -la /root/.openclaw 2>/dev/null | head -20 >> "$TMP"

section "openclaw --version (se chamavel)"
timeout 10 openclaw --version 2>&1 | head -10 >> "$TMP"

echo "[7/9] tentar start manual (modo foreground, 8s)..."
section "start manual com 8s timeout"
# Tenta como o systemd faria: ExecStart provavel; pegamos do unit file.
UNIT_FILE="$(find /etc/systemd /lib/systemd /usr/lib/systemd /root/.config/systemd \
  -maxdepth 6 -name 'openclaw-gateway.service' 2>/dev/null | head -1)"
if [ -n "$UNIT_FILE" ]; then
  EXEC="$(grep -E '^ExecStart=' "$UNIT_FILE" | head -1 | sed 's/^ExecStart=//')"
  echo "ExecStart: $EXEC" >> "$TMP"
  if [ -n "$EXEC" ]; then
    timeout 8 sh -c "$EXEC" 2>&1 | head -80 >> "$TMP"
  fi
else
  echo "unit file nao encontrado nas paths conhecidas" >> "$TMP"
fi

echo "[8/9] config gateway (porta/token/auth)..."
section "config gateway"
for f in /root/.openclaw/config.js \
         /root/.openclaw/config.json \
         /root/.openclaw/.tmp-openclaw-config.js \
         /root/cerebro-vital-slim/.tmp-openclaw-config.js; do
  [ -f "$f" ] || continue
  echo "--- $f ---" >> "$TMP"
  grep -nE 'gateway|18789|port|mode|token|auth' "$f" 2>/dev/null | head -40 >> "$TMP"
done

section "porta 18789"
ss -tlnp 2>/dev/null | grep -E ":18789\b" >> "$TMP" || echo "(nenhum listener)" >> "$TMP"

section "processos openclaw/node"
ps -eo pid,etime,rss,cmd --sort=-rss 2>/dev/null \
  | grep -iE 'openclaw|claw|node.*gateway' \
  | grep -v grep | head -30 >> "$TMP"

echo "[9/9] redigindo e fazendo upload..."
redact < "$TMP" > "$REDACTED"
SIZE="$(wc -c < "$REDACTED")"
echo "tamanho redigido: ${SIZE} bytes"

URL="$(curl -sS --max-time 30 \
        -F"file=@${REDACTED};filename=openclaw_gw_${TS}.txt" \
        -F'expires=1' \
        https://0x0.st 2>/dev/null)"
if [ -z "$URL" ] || ! echo "$URL" | grep -qE '^https?://'; then
  URL="$(curl -sS --max-time 30 --data-binary "@${REDACTED}" https://paste.rs 2>/dev/null)"
fi
if [ -z "$URL" ] || ! echo "$URL" | grep -qE '^https?://'; then
  SAVE="/root/openclaw_gw_${TS}.txt"
  cp "$REDACTED" "$SAVE"
  echo "upload falhou. arquivo salvo em: $SAVE"
  exit 2
fi

echo ""
echo "================================================================"
echo " URL (expira em 1h):"
echo ""
echo "   $URL"
echo ""
echo "================================================================"
