#!/bin/bash
set -e

echo "=== ETAPA 1: Selecionar foto real via photo_selector.py ==="
cd /root/.openclaw/workspace/skills/tweet-carrossel
python3 scripts/photo_selector.py --theme "cancer endometrial GLP-1 medicina oncologia" --top-k 5 2>&1 || true

echo ""
echo "=== ETAPA 2: Gerar capa via compose_cover.py ==="
python3 scripts/compose_cover.py \
  --foto /root/.openclaw/workspace/fotos_dra/originais/seria_bracos_cruzados.png \
  --tema "microscopio laboratorio pesquisa celulas medicina oncologia" \
  --headline "UM REMEDIO PARA EMAGRECER|PODE SALVAR SEU UTERO" \
  --destaques "REMEDIO,EMAGRECER,SALVAR,UTERO" \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/refazer/capa.jpg 2>&1

echo ""
echo "=== ETAPA 3: Capture PubMed ==="
python3 scripts/capture_pubmed.py \
  --pmid 39537842 \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/refazer/pubmed.png 2>&1

echo ""
echo "=== ETAPA 4: Verificar arquivos ==="
ls -la /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/refazer/
