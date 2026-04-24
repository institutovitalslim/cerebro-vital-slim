#!/bin/bash
# Enviar carrossel para o Telegram via script oficial
export TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
cd /root/.openclaw/workspace/skills/tweet-carrossel
python3 scripts/send_to_telegram.py \
  --chat-id -1003803476669 \
  --thread-id 4 \
  --dir /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/output_final \
  --caption "🧬 GLP-1 e Câncer Endometrial: O Novo Paradigma da Preservação" 2>&1
