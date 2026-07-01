#!/usr/bin/env bash
set -euo pipefail
cd /root/cerebro-vital-slim
out=$(/usr/bin/python3 scripts/hostinger_snapshot_backup.py 2>&1) || {
  code=$?
  printf '🔴 Snapshot Hostinger FALHOU | exit=%s | %s\n' "$code" "$(printf '%s' "$out" | tr '\n' ' ' | cut -c1-900)"
  exit "$code"
}
SNAPSHOT_JSON="$out" python3 - <<'PY'
import json, os, sys
raw = os.environ.get('SNAPSHOT_JSON', '')
data = json.loads(raw)
status = data.get('status')
created = data.get('snapshot_created_at') or '-'
expires = data.get('snapshot_expires_at') or '-'
log = data.get('log') or '-'
failed = data.get('failed_checks') or []
if status == 'success' and not failed:
    print(f'✅ Snapshot Hostinger OK | VPS={data.get("vm_id")} | criado={created} | expira={expires} | log={log}')
else:
    print(f'🔴 Snapshot Hostinger FALHA | VPS={data.get("vm_id")} | status={status} | falhas={failed} | log={log}')
    sys.exit(1)
PY
