#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="ivs-pgvector-gbrain-benchmark"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME COMPOSE_PROFILES
COMPOSE=(docker compose --file "$ROOT/compose.yaml" --project-name "$PROJECT")

PASSWORD_VALUE="$(python3 -c 'import secrets; print(secrets.token_hex(24))')"
export IVS_BENCH_DB_PASSWORD="$PASSWORD_VALUE"
export IVS_BENCH_PGVECTOR_DSN='postgresql://ivs_benchmark@127.0.0.1:55432/ivs_benchmark?application_name=ivs_pgvector_benchmark'
export PGPASSFILE="$ROOT/.pgpass.benchmark.$$"
printf '127.0.0.1:55432:ivs_benchmark:ivs_benchmark:%s\n' "$PASSWORD_VALUE" > "$PGPASSFILE"
chmod 600 "$PGPASSFILE"
unset PASSWORD_VALUE

cleanup() {
  "${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true
  rm -f "$PGPASSFILE"
}
trap cleanup EXIT

"${COMPOSE[@]}" up -d --wait
cd "$ROOT"
uv run pytest -q
