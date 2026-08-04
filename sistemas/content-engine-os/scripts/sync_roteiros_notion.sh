#!/usr/bin/env bash
# Sincroniza roteiros do Notion (teamspace) -> bunker -> SaaS. Sob demanda (João) ou manual.
# Trava flock (não roda 2x). Navegador logado no perfil compartilhado.
set -uo pipefail
BK=/root/cerebro-vital-slim/cerebro/areas/marketing/projetos/bunker-roteiros-ivs
CE=/root/cerebro-vital-slim/sistemas/content-engine-os
DB="$BK/bunker.db"
exec 9>/tmp/sync_roteiros.lock
flock -n 9 || { echo "[$(date)] já está rodando — abortando"; exit 0; }
cd "$BK/scripts"
echo "[$(date)] === SYNC ROTEIROS — início ==="
echo "[1/4] capturando teamspace (só os novos)..."
python3 importer_teamspace_roteiros.py
echo "[1.5] limpando nav + classificando brutos novos..."
sqlite3 "$DB" "update roteiros_brutos set conteudo_raw=substr(conteudo_raw, instr(conteudo_raw,'[ROTEIRO')) where status='bruto' and instr(conteudo_raw,'[ROTEIRO')>1"
python3 classifier_brutos.py >/dev/null 2>&1
echo "[2/4] adaptando brutos novos..."
IDS=$(sqlite3 "$DB" "select id from roteiros_brutos where status='bruto' and (roteiro_ivs_codigo is null or roteiro_ivs_codigo='') order by id")
n=0; for id in $IDS; do python3 bunker_cli.py adapt "$id" --yes >/dev/null 2>&1 && n=$((n+1)); done
echo "  adaptados: $n"
echo "[3/4] enriquecendo (links/prompt/fonte)..."; python3 "$CE/scripts/enrich_bunker.py"
echo "[4/4] sync -> SaaS..."; python3 "$CE/scripts/sync_bunker_to_viral.py" | docker exec -i content-engine-postgres psql -U content_engine -d content_engine >/dev/null 2>&1
TOT=$(docker exec content-engine-postgres psql -U content_engine -d content_engine -tAc "select count(*) from viral_scripts where tenant_id is null")
echo "[$(date)] === DONE — Banco do SaaS: $TOT roteiros (adaptados nesta rodada: $n) ==="
