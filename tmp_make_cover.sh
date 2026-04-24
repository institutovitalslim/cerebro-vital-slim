#!/bin/bash
cd /root/.openclaw/workspace/skills/tweet-carrossel
python3 scripts/make_cover.py \
  --foto /root/.openclaw/workspace/fotos_dra/originais/Imagem\ PNG\ 20.png \
  --circulo /root/.openclaw/media/tool-image-generation/glp1_endometrial_circle---160061a1-630b-4cee-ad0f-1dd0fd12c4a8.jpg \
  --headline "UM REMÉDIO PARA EMAGRECER|PODE SALVAR SEU ÚTERO" \
  --destaques "REMÉDIO,EMAGRECER,SALVAR,ÚTERO" \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/slide_01_OFICIAL.jpg
