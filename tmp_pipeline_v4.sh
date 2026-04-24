#!/bin/bash
set -e
mkdir -p /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/oficial

cd /root/.openclaw/workspace/skills/tweet-carrossel

# 1. Capa via compose_cover.py
python3 scripts/compose_cover.py \
  --foto /root/.openclaw/workspace/fotos_dra/originais/Imagem\ PNG\ 20.png \
  --tema "cancer endometrial laboratory research medical" \
  --circulo /root/.openclaw/media/tool-image-generation/glp1_endometrial_circle---160061a1-630b-4cee-ad0f-1dd0fd12c4a8.jpg \
  --headline "UM REMÉDIO PARA EMAGRECER|PODE SALVAR SEU ÚTERO" \
  --destaques "REMÉDIO,EMAGRECER,SALVAR,ÚTERO" \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/oficial/slide_01.jpg

# 2. PubMed via capture_pubmed.py
python3 scripts/capture_pubmed.py \
  --pmid 41329840 \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/oficial/slide_02.png

# 3. Slides 3-10 via gen_slides.py (v4 specs)
python3 scripts/gen_slides.py \
  --config /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/final/slides_config.json \
  --avatar /root/avatar_hq.png \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/oficial/

echo "=== Pipeline concluído ==="
ls -la /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/oficial/
