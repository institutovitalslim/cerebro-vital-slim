#!/usr/bin/env bash
set -euo pipefail

api_port="${HOOK_API_PORT:-18082}"
web_port="${HOOK_WEB_PORT:-13000}"
api_base="${HOOK_API_BASE_URL:-http://127.0.0.1:${api_port}}"
web_base="${HOOK_WEB_BASE_URL:-http://127.0.0.1:${web_port}}"
response_file="$(mktemp)"
trap 'rm -f "$response_file"' EXIT

wait_for_url() {
  local name="$1"
  local url="$2"
  local attempts="${3:-30}"
  local delay="${4:-2}"
  local attempt
  for ((attempt = 1; attempt <= attempts; attempt++)); do
    if curl --fail --silent --show-error --max-time 4 "$url" >/dev/null 2>&1; then
      printf 'OK: %s saudável (%s)\n' "$name" "$url"
      return 0
    fi
    sleep "$delay"
  done
  printf 'ERRO: %s não ficou saudável após %s tentativas (%s)\n' "$name" "$attempts" "$url" >&2
  return 1
}

command -v curl >/dev/null || { printf 'ERRO: curl não encontrado\n' >&2; exit 1; }
command -v python3 >/dev/null || { printf 'ERRO: python3 não encontrado\n' >&2; exit 1; }

wait_for_url backend "${api_base}/health"
wait_for_url web "${web_base}/"
wait_for_url "proxy web → backend" "${web_base}/api/backend/health"

curl --fail --silent --show-error --max-time 15 \
  -H 'Content-Type: application/json' \
  --data '{"topic":"qualidade do sono","channel":"reel","objective":"retention","audience":"mulheres acima de 40","library":"universal","count":5,"use_ai":false}' \
  "${api_base}/v1/hooks/generate" >"$response_file"

python3 - "$response_file" <<'PY'
import json
import re
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
hooks = payload.get("hooks")
assert isinstance(hooks, list) and len(hooks) == 5, "a resposta deve conter exatamente 5 hooks"
placeholder = re.compile(r"\{[^{}]+\}")
for index, hook in enumerate(hooks):
    text = hook.get("text")
    explanation = hook.get("explanation")
    assert isinstance(text, str) and text.strip(), f"hook {index} sem texto"
    assert isinstance(explanation, str) and explanation.strip(), f"hook {index} sem explicação"
    assert not placeholder.search(text), f"hook {index} contém placeholder no texto"
    assert not placeholder.search(explanation), f"hook {index} contém placeholder na explicação"
    scores = hook.get("scores")
    assert isinstance(scores, dict) and scores, f"hook {index} sem scores"
    assert all(isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0 for value in scores.values()), f"hook {index} contém score não positivo"
print("OK: POST gerou exatamente 5 hooks, todos com scores > 0 e sem placeholders")
PY
