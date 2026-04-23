#!/usr/bin/env bash
# ops/diag/clara-telegram.sh
#
# One-shot diagnostic para investigar por que a Clara parou de responder
# no Telegram. Coleta status de processos, gateway, token, logs e config,
# redige segredos, e faz upload pra um paste público com expiração de 1h.
#
# Uso (na VPS, como root ou com sudo):
#   cd /root/cerebro-vital-slim && bash ops/diag/clara-telegram.sh
#
# Saída: imprime UMA URL no final — envie essa URL ao Claude.

set +e
shopt -s nullglob

TS="$(date +%Y%m%d-%H%M%S)"
TMP="$(mktemp)"
REDACTED="$(mktemp)"

trap 'rm -f "$TMP" "$REDACTED"' EXIT

section() { printf '\n===== %s =====\n' "$1" >> "$TMP"; }

# Redige tokens, chaves e secrets antes do upload.
redact() {
  sed -E \
    -e 's/[0-9]{8,}:[A-Za-z0-9_-]{30,}/[REDACTED_BOT_TOKEN]/g' \
    -e 's/sk-[A-Za-z0-9_-]{20,}/[REDACTED_API_KEY]/g' \
    -e 's/(ey[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,})/[REDACTED_JWT]/g' \
    -e 's/((TOKEN|KEY|SECRET|PASSWORD|PASSWD|APIKEY)[A-Z_]*[[:space:]]*[:=][[:space:]]*)["'"'"']?[^"'"'"'[:space:],]+/\1[REDACTED]/gI' \
    -e 's/(Authorization:[[:space:]]*Bearer[[:space:]]+)[A-Za-z0-9._~+/=-]+/\1[REDACTED]/gI' \
    -e 's/(\"token\"[[:space:]]*:[[:space:]]*)"[^"]+"/\1"[REDACTED]"/g'
}

echo "[1/10] metadata do host..."
{
  echo "=== DIAG CLARA TELEGRAM ==="
  echo "timestamp: $(date -Is)"
  echo "host: $(hostname)"
  echo "uname: $(uname -a)"
  echo "uptime: $(uptime)"
} > "$TMP"

echo "[2/10] processos e pm2..."
section "pm2 list"
pm2 list --no-color 2>&1 | head -40 >> "$TMP"

section "processos openclaw/node/gateway"
ps -eo pid,etime,rss,cmd --sort=-rss 2>/dev/null \
  | grep -iE "openclaw|claw|gateway|cerebro|node|telegram" \
  | grep -v grep | head -40 >> "$TMP"

section "systemd units openclaw*"
systemctl list-units --all --plain --no-legend 'openclaw*' 'claw*' 2>/dev/null | head -20 >> "$TMP"
for svc in openclaw openclaw-gateway openclaw-cerebro clara; do
  if systemctl list-unit-files --no-legend 2>/dev/null | awk '{print $1}' | grep -qx "${svc}.service"; then
    echo "--- $svc ---" >> "$TMP"
    systemctl status "$svc" --no-pager -l 2>&1 | head -30 >> "$TMP"
  fi
done

echo "[3/10] portas..."
section "portas (18789 gateway / 8787 zapi / 3000 / 4000)"
ss -tulpn 2>/dev/null | grep -E ":(18789|8787|3000|4000)\b" >> "$TMP" || echo "nenhuma porta esperada escutando" >> "$TMP"

echo "[4/10] gateway health..."
section "gateway http://localhost:18789/health"
curl -sS --max-time 8 -o /dev/null -w "HTTP %{http_code} em %{time_total}s\n" http://localhost:18789/health 2>&1 >> "$TMP"
curl -sS --max-time 8 http://localhost:18789/health 2>&1 | head -c 1500 >> "$TMP"
echo "" >> "$TMP"
section "gateway /v1/models"
curl -sS --max-time 8 http://localhost:18789/v1/models 2>&1 | head -c 2000 >> "$TMP"
echo "" >> "$TMP"

echo "[5/10] telegram API..."
section "telegram: localizar token"
TG_TOKEN=""
TG_SRC=""
for f in /root/.openclaw/secure/telegram.env \
         /root/.openclaw/secure/*.env \
         /root/.openclaw/.env \
         /root/.openclaw/workspace/.env \
         /root/cerebro-vital-slim/.env \
         /etc/openclaw/telegram.env; do
  [ -f "$f" ] || continue
  v="$(grep -E '^[[:space:]]*TELEGRAM_BOT_TOKEN[[:space:]]*=' "$f" 2>/dev/null \
        | head -1 | sed -E 's/^[^=]+=[[:space:]]*//; s/^"//; s/"$//; s/^'"'"'//; s/'"'"'$//')"
  if [ -n "$v" ]; then TG_TOKEN="$v"; TG_SRC="$f"; break; fi
done
[ -z "$TG_TOKEN" ] && [ -n "$TELEGRAM_BOT_TOKEN" ] && TG_TOKEN="$TELEGRAM_BOT_TOKEN" && TG_SRC="env"
if [ -n "$TG_TOKEN" ]; then
  echo "fonte do token: $TG_SRC" >> "$TMP"
  echo "tamanho do token: ${#TG_TOKEN} chars" >> "$TMP"
  section "telegram getMe"
  curl -sS --max-time 10 "https://api.telegram.org/bot${TG_TOKEN}/getMe" >> "$TMP"
  echo "" >> "$TMP"
  section "telegram getWebhookInfo"
  curl -sS --max-time 10 "https://api.telegram.org/bot${TG_TOKEN}/getWebhookInfo" >> "$TMP"
  echo "" >> "$TMP"
  section "telegram getUpdates (limit 3)"
  curl -sS --max-time 10 "https://api.telegram.org/bot${TG_TOKEN}/getUpdates?limit=3&timeout=0" >> "$TMP"
  echo "" >> "$TMP"
else
  echo "TELEGRAM_BOT_TOKEN nao localizado em paths padrao nem em env" >> "$TMP"
fi

echo "[6/10] logs pm2 / journalctl..."
section "pm2 logs (tail 300)"
pm2 logs --lines 300 --nostream --raw 2>&1 | tail -500 >> "$TMP"

section "journalctl -u openclaw (24h)"
journalctl -u openclaw -S "24 hours ago" --no-pager 2>/dev/null | tail -200 >> "$TMP"

section "journalctl erros gerais 24h (filtrado)"
journalctl -p err -S "24 hours ago" --no-pager 2>/dev/null \
  | grep -iE "openclaw|telegram|bot|gateway|18789|ECONNREFUSED|timeout|401|429" \
  | tail -120 >> "$TMP"

echo "[7/10] crontab..."
section "crontab root"
crontab -l 2>/dev/null >> "$TMP" || echo "(sem crontab)" >> "$TMP"

echo "[8/10] git do cerebro..."
section "git /root/cerebro-vital-slim"
if [ -d /root/cerebro-vital-slim/.git ]; then
  git -C /root/cerebro-vital-slim branch --show-current >> "$TMP"
  git -C /root/cerebro-vital-slim log --oneline -10 >> "$TMP"
  echo "--- status ---" >> "$TMP"
  git -C /root/cerebro-vital-slim status -s >> "$TMP"
  echo "--- remote ---" >> "$TMP"
  git -C /root/cerebro-vital-slim remote -v >> "$TMP"
fi

echo "[9/10] config openclaw (trechos)..."
section "config openclaw (trechos relevantes)"
for f in /root/.openclaw/config.js \
         /root/.openclaw/config.json \
         /root/.openclaw/.tmp-openclaw-config.js \
         /root/cerebro-vital-slim/.tmp-openclaw-config.js; do
  [ -f "$f" ] || continue
  echo "--- $f (mtime $(stat -c %y "$f" 2>/dev/null)) ---" >> "$TMP"
  grep -n -iE "telegram|gateway|18789|mode:|token|allowFrom|groups" "$f" 2>/dev/null | head -60 >> "$TMP"
done

section "workspace-state"
cat /root/.openclaw/workspace-state.json 2>/dev/null >> "$TMP"

section "disk / mem"
df -h / /root 2>/dev/null >> "$TMP"
free -h >> "$TMP"

section "saida de rede (teste)"
curl -sS --max-time 5 -o /dev/null -w "api.telegram.org  %{http_code}  %{time_total}s\n" https://api.telegram.org/ 2>&1 >> "$TMP"
curl -sS --max-time 5 -o /dev/null -w "github.com        %{http_code}  %{time_total}s\n" https://github.com/ 2>&1 >> "$TMP"

echo "[10/10] redigindo segredos e fazendo upload..."
redact < "$TMP" > "$REDACTED"

SIZE="$(wc -c < "$REDACTED")"
echo "tamanho redigido: ${SIZE} bytes"

URL="$(curl -sS --max-time 30 \
        -F"file=@${REDACTED};filename=clara_diag_${TS}.txt" \
        -F'expires=1' \
        https://0x0.st 2>/dev/null)"

if [ -z "$URL" ] || ! echo "$URL" | grep -qE '^https?://'; then
  echo "0x0.st falhou, tentando paste.rs..."
  URL="$(curl -sS --max-time 30 --data-binary "@${REDACTED}" https://paste.rs 2>/dev/null)"
fi

if [ -z "$URL" ] || ! echo "$URL" | grep -qE '^https?://'; then
  echo "--- upload falhou em todos os paste services ---"
  echo "alternativa: salve o arquivo localmente e me diga:"
  SAVE="/root/clara_diag_${TS}.txt"
  cp "$REDACTED" "$SAVE"
  echo "arquivo salvo em: $SAVE"
  exit 2
fi

echo ""
echo "================================================================"
echo " URL (expira em 1h) — envie essa linha ao Claude:"
echo ""
echo "   $URL"
echo ""
echo "================================================================"
