#!/usr/bin/env bash
# ops/skills-sync/sync-skills.sh
#
# Sincroniza skills do cérebro (fonte de verdade) para o workspace do OpenClaw
# na VPS (onde a Clara efetivamente invoca as skills).
#
#   Source:       /root/cerebro-vital-slim/cerebro/empresa/skills/
#   Destination:  /root/.openclaw/workspace/skills/
#
# Regras:
# - One-way: cérebro → workspace. Nunca o contrário.
# - Não deleta nada do workspace que não exista no cérebro (preserva logs,
#   caches, state files que são runtime-only).
# - Sobrescreve conteúdo das skills (SKILL.md, reference/, scripts/) com a
#   versão do cérebro.
# - Idempotente: rodar 2x produz o mesmo resultado.
# - Logs em ops/skills-sync/logs/sync-<YYYYMMDD-HHMM>.log
#
# Uso:
#   bash ops/skills-sync/sync-skills.sh              # sync real
#   bash ops/skills-sync/sync-skills.sh --dry-run    # preview sem mudar nada
#   bash ops/skills-sync/sync-skills.sh --verbose    # detalha cada arquivo

set -euo pipefail

# PATH defensivo (hpanel browser terminal ás vezes tem PATH curto)
export PATH="/usr/local/sbin:/usr/local/bin:/sbin:/usr/sbin:/bin:/usr/bin:${PATH:-}"

CEREBRO_ROOT="${CEREBRO_ROOT:-/root/cerebro-vital-slim}"
SRC="${CEREBRO_ROOT}/cerebro/empresa/skills"
DST="${WORKSPACE_SKILLS:-/root/.openclaw/workspace/skills}"
LOG_DIR="${CEREBRO_ROOT}/ops/skills-sync/logs"
LOG_FILE="${LOG_DIR}/sync-$(date +%Y%m%d-%H%M%S).log"

DRY_RUN=""
VERBOSE=""
for arg in "$@"; do
  case "$arg" in
    --dry-run|-n) DRY_RUN="--dry-run" ;;
    --verbose|-v) VERBOSE="-v" ;;
    *) echo "opção desconhecida: $arg"; exit 2 ;;
  esac
done

# Validações
if [ ! -d "$SRC" ]; then
  echo "ERRO: origem não existe: $SRC" >&2
  exit 3
fi

if [ ! -d "$DST" ]; then
  echo "AVISO: destino não existe, criando: $DST"
  if [ -z "$DRY_RUN" ]; then
    mkdir -p "$DST"
  fi
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "ERRO: rsync não instalado. Rodar: apt-get install -y rsync" >&2
  exit 4
fi

mkdir -p "$LOG_DIR"

{
  echo "=== SKILL SYNC $(date -Is) ==="
  echo "source:      $SRC"
  echo "destination: $DST"
  echo "dry-run:     ${DRY_RUN:-NO}"
  echo
  echo "=== skills no cérebro ==="
  ls -1 "$SRC" | grep -v "^_" | head -30
  echo
  echo "=== skills atualmente no workspace ==="
  ls -1 "$DST" 2>/dev/null | head -30 || echo "(workspace vazio)"
  echo
  echo "=== rsync ==="
} | tee -a "$LOG_FILE"

# Excluir arquivos/dirs que são metadados do próprio cerebro e não devem ir
# pro workspace
EXCLUDE_FLAGS=(
  --exclude="_index.md"
  --exclude="_templates/"
  --exclude=".git/"
  --exclude=".gitignore"
  --exclude="logs/"
  --exclude="state/"
)

# rsync: -a (archive: perms, times, symlinks), -h (human sizes),
# --itemize-changes (lista o que mudou), sem --delete (preserva runtime files)
rsync -ah --itemize-changes $DRY_RUN $VERBOSE \
  "${EXCLUDE_FLAGS[@]}" \
  "${SRC}/" "${DST}/" 2>&1 | tee -a "$LOG_FILE"

rc=${PIPESTATUS[0]}

{
  echo
  if [ "$rc" -eq 0 ]; then
    if [ -n "$DRY_RUN" ]; then
      echo "=== DRY-RUN OK — nada foi alterado ==="
    else
      echo "=== SYNC OK ==="
    fi
  else
    echo "=== ERRO (rc=$rc) ==="
  fi
  echo "log: $LOG_FILE"
} | tee -a "$LOG_FILE"

exit "$rc"
