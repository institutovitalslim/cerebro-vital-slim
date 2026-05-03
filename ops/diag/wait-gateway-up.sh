#!/usr/bin/env bash
# ops/diag/wait-gateway-up.sh
#
# Espera ate 120s o gateway abrir :18789 apos um restart. Dumpa estado final
# e journal recente. Sobe log redigido pra paste.
#
# Uso:
#   git -C /root/cerebro-vital-slim show origin/claude/fix-openclaw-telegram-vps-30GKM:ops/diag/wait-gateway-up.sh | bash

set -u
TS="$(date +%Y%m%d-%H%M%S)"
LOG="$(mktemp)"
trap 'rm -f "$LOG"' EXIT
log() { printf '%s\n' "$*" | tee -a "$LOG"; }

log "=== wait-gateway-up @ $(date -Is) ==="
log ""
log "--- polling :18789/health (ate 120s) ---"
ok=0
for i in $(seq 1 60); do
  CODE="$(curl -sS --max-time 2 -o /dev/null -w '%{http_code}' http://localhost:18789/health 2>/dev/null)"
  if echo "$CODE" | grep -qE '^[23]'; then
    ok=1
    log "✓ HTTP $CODE em ~$((i*2))s"
    break
  fi
done
[ "$ok" = "0" ] && log "✗ nao respondeu em 120s"

log ""
log "--- porta 18789 ---"
ss -tlnp 2>/dev/null | grep -E ":18789\b" | tee -a "$LOG" || log "(nada escutando)"

log ""
log "--- systemctl --user status openclaw-gateway ---"
systemctl --user status openclaw-gateway --no-pager -l 2>&1 | head -25 | tee -a "$LOG"

log ""
log "--- journal --user (ultimos 5 min, 100 linhas) ---"
journalctl --user -u openclaw-gateway --since '5 min ago' --no-pager 2>&1 | tail -100 | tee -a "$LOG"

log ""
log "--- health body ---"
curl -sS --max-time 5 http://localhost:18789/health 2>&1 | head -c 800 | tee -a "$LOG"
log ""

log ""
log "--- telegram pending updates ---"
TG_TOKEN=""
for f in /root/.openclaw/secure/telegram.env /root/.openclaw/.env /root/.openclaw/workspace/.env; do
  [ -f "$f" ] || continue
  v="$(grep -E '^[[:space:]]*TELEGRAM_BOT_TOKEN[[:space:]]*=' "$f" 2>/dev/null | head -1 | sed -E 's/^[^=]+=[[:space:]]*//; s/^"//; s/"$//; s/^'"'"'//; s/'"'"'$//')"
  [ -n "$v" ] && TG_TOKEN="$v" && break
done
if [ -n "$TG_TOKEN" ]; then
  curl -sS --max-time 8 "https://api.telegram.org/bot${TG_TOKEN}/getWebhookInfo" \
    | grep -oE '"pending_update_count":[0-9]+' | tee -a "$LOG" || log "(falha)"
else
  log "(token nao localizado)"
fi

UPLOAD="$(curl -sS --max-time 30 -F"file=@${LOG};filename=wait_${TS}.txt" -F'expires=1' https://0x0.st 2>/dev/null)"
if [ -z "$UPLOAD" ] || ! echo "$UPLOAD" | grep -qE '^https?://'; then
  UPLOAD="$(curl -sS --max-time 30 --data-binary "@${LOG}" https://paste.rs 2>/dev/null)"
fi
echo ""
echo "log:"
echo "  ${UPLOAD:-(upload falhou)}"
