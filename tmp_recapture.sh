#!/bin/bash
cd /root/.openclaw/workspace/skills/tweet-carrossel
python3 scripts/capture_pubmed.py \
  --pmid 39537842 \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/pubmed.png 2>&1 | tail -10
