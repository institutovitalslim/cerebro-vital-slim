#!/bin/bash
export TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/send_to_telegram.py \
  --chat-id -1003803476669 \
  --thread-id 4 \
  --dir /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/final \
  --caption "🧬 GLP-1 e Câncer Endometrial — Pipeline Oficial"
