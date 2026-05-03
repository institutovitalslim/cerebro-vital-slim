#!/usr/bin/env bash
# ops/setup/fix-openclaw-gateway.sh
#
# Fix do crash do openclaw-gateway diagnosticado em 2026-05-03:
#   browser.profiles.openclaw.color: Invalid input: expected string, received undefined
#
# Causa: alguem editou /root/.openclaw/openclaw.json (provavelmente no SIGUSR1 das 16:00:07
# pra "fixar executablePath do browser host") e removeu/quebrou o campo color.
#
# Fix: backup do json, tenta openclaw doctor --fix; se nao resolver, patcha via jq
# inserindo "color":"blue" no profile openclaw. Depois reset-failed + restart + verify.
#
# Idempotente. Se o config ja estiver valido, nao toca em nada — so faz restart e verify.
#
# Uso (na VPS, root, em qualquer pwd):
#   git -C /root/cerebro-vital-slim show origin/claude/fix-openclaw-telegram-vps-30GKM:ops/setup/fix-openclaw-gateway.sh | bash

set -u
shopt -s nullglob

CFG="/root/.openclaw/openclaw.json"
TS="$(date +%Y%m%d-%H%M%S)"
LOG="$(mktemp)"
trap 'rm -f "$LOG"' EXIT

log() { printf '%s\n' "$*" | tee -a "$LOG"; }

log "=== fix-openclaw-gateway @ $(date -Is) ==="
log "config: $CFG"

if [ ! -f "$CFG" ]; then
  log "ERRO: $CFG nao existe"
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  log "instalando jq..."
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq jq >/dev/null 2>&1 \
    || { log "ERRO: falha instalando jq"; exit 1; }
fi

log ""
log "--- profile.openclaw ANTES ---"
jq '.browser.profiles.openclaw // "(ausente)"' "$CFG" 2>&1 | tee -a "$LOG"

# Backup
BAK="${CFG}.bak-${TS}"
cp -a "$CFG" "$BAK"
log ""
log "backup salvo em: $BAK"

# Schema espera hex RRGGBB (6 chars, sem #). Valida que esta nesse formato.
HAS_COLOR="$(jq -r '.browser.profiles.openclaw.color // "" | tostring' "$CFG" 2>/dev/null)"
is_valid_hex() { echo "$1" | grep -qE '^[0-9a-fA-F]{6}$'; }

if is_valid_hex "$HAS_COLOR"; then
  log ""
  log "color ja em formato hex valido ('$HAS_COLOR') — nao precisa patchar."
else
  log ""
  log "color atual: '${HAS_COLOR:-<vazio>}' (invalido — schema espera RRGGBB)"
  log ""
  log "--- tentando openclaw doctor --fix (60s timeout) ---"
  timeout 60 openclaw doctor --fix </dev/null 2>&1 | tail -40 | tee -a "$LOG" || \
    log "(doctor saiu com codigo nao-zero ou timed out — vamos checar config)"

  HAS_COLOR2="$(jq -r '.browser.profiles.openclaw.color // "" | tostring' "$CFG" 2>/dev/null)"
  if is_valid_hex "$HAS_COLOR2"; then
    log "doctor consertou color: '$HAS_COLOR2'"
  else
    log ""
    log "--- doctor nao preencheu color valido, patchando manualmente: color=3b82f6 ---"
    TMP_JSON="$(mktemp)"
    jq '.browser.profiles.openclaw.color = "3b82f6"' "$CFG" > "$TMP_JSON" \
      && mv "$TMP_JSON" "$CFG" \
      && log "patch aplicado." \
      || { log "ERRO: jq patch falhou"; exit 2; }
  fi
fi

log ""
log "--- profile.openclaw DEPOIS ---"
jq '.browser.profiles.openclaw' "$CFG" 2>&1 | tee -a "$LOG"

log ""
log "--- reset-failed + restart ---"
systemctl --user reset-failed openclaw-gateway 2>&1 | tee -a "$LOG"
systemctl --user restart openclaw-gateway 2>&1 | tee -a "$LOG"

log ""
log "--- aguardando gateway subir (ate 20s) ---"
ok=0
for i in 1 2 3 4 5 6 7 8 9 10; do
  sleep 2
  if curl -sS --max-time 3 -o /dev/null -w '%{http_code}' http://localhost:18789/health 2>/dev/null | grep -qE '^[23]'; then
    ok=1
    log "gateway respondeu apos ${i} tentativa(s) (~$((i*2))s)"
    break
  fi
done

log ""
log "--- estado final ---"
log "porta 18789:"
ss -tlnp 2>/dev/null | grep -E ":18789\b" | tee -a "$LOG" || log "(nada escutando)"

log ""
log "systemctl --user status (head):"
systemctl --user status openclaw-gateway --no-pager -l 2>&1 | head -15 | tee -a "$LOG"

log ""
log "health:"
curl -sS --max-time 5 http://localhost:18789/health 2>&1 | head -c 500 | tee -a "$LOG"
log ""

if [ "$ok" = "1" ]; then
  log ""
  log "================================================================"
  log " ✓ openclaw-gateway UP em :18789"
  log " A Maria deve drenar os 9 updates pendentes em segundos."
  log "================================================================"
else
  log ""
  log "================================================================"
  log " ✗ Gateway ainda nao responde. Veja status acima."
  log " Backup do config preservado: $BAK"
  log "================================================================"
fi

UPLOAD="$(curl -sS --max-time 30 -F"file=@${LOG};filename=fix_${TS}.txt" -F'expires=1' https://0x0.st 2>/dev/null)"
if [ -z "$UPLOAD" ] || ! echo "$UPLOAD" | grep -qE '^https?://'; then
  UPLOAD="$(curl -sS --max-time 30 --data-binary "@${LOG}" https://paste.rs 2>/dev/null)"
fi
echo ""
echo "log completo:"
echo "  ${UPLOAD:-(upload falhou — log em $LOG ate o fim do shell)}"
