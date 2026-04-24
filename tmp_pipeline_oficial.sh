#!/bin/bash
set -e
cd /root/.openclaw/workspace/skills/tweet-carrossel

# 1. Gerar capa via compose_cover.py
python3 scripts/compose_cover.py \
  --foto /root/.openclaw/workspace/fotos_dra/originais/Imagem\ PNG\ 20.png \
  --tema "cancer endometrial laboratory research medical" \
  --circulo /root/.openclaw/media/tool-image-generation/glp1_endometrial_circle---160061a1-630b-4cee-ad0f-1dd0fd12c4a8.jpg \
  --headline "UM REMÉDIO PARA EMAGRECER|PODE SALVAR SEU ÚTERO" \
  --destaques "REMÉDIO,EMAGRECER,SALVAR,ÚTERO" \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/final/slide_01.jpg

# 2. Capture PubMed
python3 scripts/capture_pubmed.py \
  --pmid 41329840 \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/final/slide_02.png

echo "=== ETAPA 1 e 2 concluídas ==="
