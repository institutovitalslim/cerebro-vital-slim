#!/bin/bash
# Capturar screenshot do PubMed para o slide 2
cd /root/.openclaw/workspace/skills/tweet-carrossel
python3 scripts/capture_pubmed.py \
  --pmid 39537842 \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/pubmed.png 2>&1
