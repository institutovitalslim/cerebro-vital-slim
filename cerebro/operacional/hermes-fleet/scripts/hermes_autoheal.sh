#!/usr/bin/env bash
# IVS — Autoheal Hermes-aware (nível SISTEMA, não depende de LLM).
# Garante: os 6 gateways Hermes + o caminho WhatsApp da Clara (pacientes) + portas.
# Substitui o ivs_autoheal.sh (que era 100% OpenClaw). Alerta o Tiaro quando age.
export XDG_RUNTIME_DIR=/run/user/0
SU="systemctl --user"
LOG=/root/clone_dra/hermes_autoheal.log
TOKEN=$(grep -oE 'TELEGRAM_BOT_TOKEN=[^ ]+' /root/.hermes/.env 2>/dev/null | head -1 | cut -d= -f2)
TIARO=971050173
alert(){ [ -n "$TOKEN" ] && curl -s "https://api.telegram.org/bot$TOKEN/sendMessage" -d chat_id=$TIARO --data-urlencode "text=🩺 autoheal: $1" >/dev/null 2>&1; echo "$(date -Is) $1" >> "$LOG"; }
actions=0

# 1) os 6 gateways Hermes (frota de agentes)
for g in hermes-gateway hermes-gateway-jarvis hermes-gateway-pedro hermes-gateway-clara hermes-gateway-ana hermes-gateway-joao; do
  if ! $SU is-active "$g.service" 2>/dev/null | grep -q '^active'; then
    $SU reset-failed "$g.service" 2>/dev/null
    $SU restart "$g.service" 2>/dev/null
    sleep 2
    actions=$((actions+1))
    alert "$g estava DOWN -> reiniciei (agora: $($SU is-active $g.service 2>/dev/null))"
  fi
done

# 2) caminho WhatsApp da Clara (pacientes): cerebro Codex-fallback + bridge
for s in openclaw-gateway zapi-clara-bridge cloudflared-zapi-bridge; do
  # cloudflared esta aposentado de proposito (nginx) -> so cuida dos 2 primeiros
  [ "$s" = "cloudflared-zapi-bridge" ] && continue
  if ! $SU is-active "$s.service" 2>/dev/null | grep -q '^active'; then
    $SU restart "$s.service" 2>/dev/null
    sleep 2
    actions=$((actions+1))
    alert "$s (caminho WhatsApp da Clara) estava DOWN -> reiniciei (agora: $($SU is-active $s.service 2>/dev/null))"
  fi
done

# 3) portas criticas do atendimento de paciente
ss -ltn 2>/dev/null | grep -q '127.0.0.1:18789' || { alert "cerebro 18789 NAO escuta (Clara fallback)"; actions=$((actions+1)); }
ss -ltn 2>/dev/null | grep -q ':8787' || { alert "bridge 8787 NAO escuta (entrada WhatsApp)"; actions=$((actions+1)); }

# 4) browser de cursos (CDP 9222) — usado por cursos + fallback NotebookLM da Ana
curl -s -m 5 http://localhost:9222/json/version >/dev/null 2>&1 || { /root/clone_dra/course_browser_ensure.sh >/dev/null 2>&1; echo "$(date -Is) CDP 9222 down -> course_browser_ensure" >> "$LOG"; }

[ "$actions" -eq 0 ] && echo "$(date -Is) OK (6 gateways + WhatsApp + portas)" >> "$LOG"
