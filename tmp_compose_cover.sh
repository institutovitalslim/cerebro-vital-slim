#!/bin/bash
# Gerar capa do carrossel GLP-1 + Câncer Endometrial
cd /root/.openclaw/workspace/skills/tweet-carrossel
python3 scripts/compose_cover.py \
  --foto /root/.openclaw/workspace/fotos_dra/originais/seria_bracos_cruzados.png \
  --tema "microscopio laboratorio pesquisa celulas medicina oncologia" \
  --headline "UM REMEDIO PARA EMAGRECER|PODE SALVAR SEU UTERO" \
  --destaques "REMEDIO,EMAGRECER,SALVAR,UTERO" \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/capa.jpg 2>&1
