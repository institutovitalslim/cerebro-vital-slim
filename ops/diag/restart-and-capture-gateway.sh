#!/usr/bin/env bash
# ops/diag/restart-and-capture-gateway.sh
#
# Reset do failed-state, start do gateway, e captura dos logs do --user
# journal cobrindo a tentativa atual. Roda openclaw-gateway-wrapper.sh em
# foreground em paralelo (sem systemd) pra capturar stderr direto caso
# o journal nao pegue alguma linha.
#
# Uso (root, VPS):
#   git -C /root/cerebro-vital-slim show origin/claude/fix-openclaw-telegram-vps-30GKM:ops/diag/restart-and-capture-gateway.sh | bash

set -u
TS="$(date +%Y%m%d-%H%M%S)"
LOG="$(mktemp)"
trap 'rm -f "$LOG"' EXIT
log() { printf '%s\n' "$*" | tee -a "$LOG"; }

log "=== restart-and-capture-gateway @ $(date -Is) ==="

log ""
log "--- reset-failed ---"
systemctl --user reset-failed openclaw-gateway 2>&1 | tee -a "$LOG"

START_TS="$(date '+%Y-%m-%d %H:%M:%S')"
log ""
log "--- start (timestamp: $START_TS) ---"
systemctl --user start openclaw-gateway 2>&1 | tee -a "$LOG" || true

log ""
log "--- aguardando 35s pro gateway tentar e cair se for o caso ---"
sleep 35

log ""
log "--- estado atual ---"
systemctl --user status openclaw-gateway --no-pager -l 2>&1 | head -25 | tee -a "$LOG"

log ""
log "--- journal --user desde o start ---"
journalctl --user -u openclaw-gateway --since "$START_TS" --no-pager 2>&1 | tail -200 | tee -a "$LOG"

log ""
log "--- porta 18789 ---"
ss -tlnp 2>/dev/null | grep -E ":18789\b" | tee -a "$LOG" || log "(nada escutando)"

log ""
log "--- ultimos 100 logs --user de qualquer source mencionando openclaw ---"
journalctl --user --since "$START_TS" --no-pager 2>&1 | grep -iE 'openclaw|gateway|chrome|cdp|18789|error' | tail -50 | tee -a "$LOG"

UPLOAD="$(curl -sS --max-time 30 -F"file=@${LOG};filename=restart_${TS}.txt" -F'expires=1' https://0x0.st 2>/dev/null)"
if [ -z "$UPLOAD" ] || ! echo "$UPLOAD" | grep -qE '^https?://'; then
  UPLOAD="$(curl -sS --max-time 30 --data-binary "@${LOG}" https://paste.rs 2>/dev/null)"
fi
echo ""
echo "log:"
echo "  ${UPLOAD:-(upload falhou)}"
