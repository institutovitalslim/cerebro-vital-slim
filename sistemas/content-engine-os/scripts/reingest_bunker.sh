#!/bin/bash
# Re-ingestão Notion -> bunker -> SaaS. Pré-requisito: banco do Notion compartilhado com a integração "Openclaw".
set -e
BK=/root/cerebro-vital-slim/cerebro/areas/marketing/projetos/bunker-roteiros-ivs/scripts; CE=/root/cerebro-vital-slim/sistemas/content-engine-os
echo "[1/4] Notion --full --all"; python3 $BK/importer_notion.py --full --all || echo "  (acesso negado? compartilhe o Notion com Openclaw)"
echo "[2/4] adaptar brutos novos"; python3 $BK/bunker_cli.py adaptar --auto 2>/dev/null || echo "  (rodar adaptação manual via bunker_cli se necessário)"
echo "[3/4] enriquecer (refs/prompt/fonte)"; python3 $CE/scripts/enrich_bunker.py
echo "[4/4] sync -> SaaS"; python3 $CE/scripts/sync_bunker_to_viral.py | docker exec -i content-engine-postgres psql -U content_engine -d content_engine | tail -1
echo "OK."
