#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "[bootstrap] .env criado a partir de .env.example"
fi

echo "[bootstrap] Subindo stack base..."
docker compose up -d

echo "[bootstrap] Stack solicitada. Verifique com: docker compose ps"
