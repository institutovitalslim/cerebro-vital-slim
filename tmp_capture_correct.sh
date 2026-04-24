#!/bin/bash
cd /root/.openclaw/workspace/skills/tweet-carrossel
python3 scripts/capture_pubmed.py \
  --pmid 41329840 \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/pubmed_correct.png 2>&1 | tail -10
