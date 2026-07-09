#!/usr/bin/env bash
set -euo pipefail
cd /opt/ivs/ivs-crawl4ai-sandbox
OUT="${1:-runs/$(date +%Y%m%d-%H%M%S)}"
shift || true
uv run pytest -q >/tmp/ivs_crawl4ai_skill_pytest.log
uv run python -m ivs_crawl4ai_sandbox.runner --out "$OUT" "$@"
printf 'OUT=%s
' "/opt/ivs/ivs-crawl4ai-sandbox/$OUT"
printf 'SUMMARY_JSON=%s
' "/opt/ivs/ivs-crawl4ai-sandbox/$OUT/summary.json"
printf 'SUMMARY_HTML=%s
' "/opt/ivs/ivs-crawl4ai-sandbox/$OUT/summary.html"
