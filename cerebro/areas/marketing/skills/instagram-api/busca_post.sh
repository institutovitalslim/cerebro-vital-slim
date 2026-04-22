#!/bin/bash
# Busca post/reel do Instagram por shortcode ou URL
# Default: Instagram Scraper Stable API (direct fetch)
# Fallback: instagram120 (paginacao pelo perfil IVS) se a Stable falhar
#
# Uso: ./busca_post.sh <shortcode_ou_url>
# Exemplo:
#   ./busca_post.sh DV_HjMKlg5h
#   ./busca_post.sh https://www.instagram.com/p/DV_HjMKlg5h/
#   ./busca_post.sh https://www.instagram.com/reel/DV_HjMKlg5h/

set -euo pipefail

INPUT="${1:-}"
KEY="cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56"
STABLE_HOST="instagram-scraper-stable-api.p.rapidapi.com"
LEGACY_HOST="instagram120.p.rapidapi.com"
FALLBACK_USERNAME="institutovitalslim"

if [ -z "$INPUT" ]; then
  echo "Uso: $0 <shortcode_ou_url>" >&2
  exit 1
fi

# Extrai shortcode se for URL. Se ja for shortcode puro, mantem.
SHORTCODE=$(echo "$INPUT" | python3 -c '
import sys, re
s = sys.stdin.read().strip()
m = re.search(r"/(?:p|reel|tv)/([A-Za-z0-9_-]+)", s)
if m:
    print(m.group(1))
elif re.match(r"^[A-Za-z0-9_-]+$", s):
    print(s)
else:
    sys.exit(1)
')

if [ -z "$SHORTCODE" ]; then
  echo "Input invalido. Passe um shortcode ou URL do Instagram." >&2
  exit 1
fi

echo "[info] shortcode=$SHORTCODE" >&2

# --- PRIMARIO: Stable API ---
try_stable() {
  local TYPE="$1"
  curl -sS --max-time 20     "https://${STABLE_HOST}/get_media_data.php?reel_post_code_or_url=${SHORTCODE}&type=${TYPE}"     -H "x-rapidapi-host: ${STABLE_HOST}"     -H "x-rapidapi-key: ${KEY}"
}

echo "[stable] type=post" >&2
RES=$(try_stable post)
if echo "$RES" | python3 -c 'import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get("shortcode") else 1)' 2>/dev/null; then
  echo "$RES"
  exit 0
fi

echo "[stable] type=reel (fallback)" >&2
RES=$(try_stable reel)
if echo "$RES" | python3 -c 'import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get("shortcode") else 1)' 2>/dev/null; then
  echo "$RES"
  exit 0
fi

# --- FALLBACK: instagram120 pagina pelo perfil ---
echo "[fallback] instagram120 paginando perfil $FALLBACK_USERNAME" >&2
CURSOR=""
PAGE=1
while true; do
  RES=$(curl -sS --max-time 30     --request POST     --url "https://${LEGACY_HOST}/api/instagram/posts"     --header 'Content-Type: application/json'     --header "x-rapidapi-host: ${LEGACY_HOST}"     --header "x-rapidapi-key: ${KEY}"     --data "{\"username\":\"${FALLBACK_USERNAME}\",\"maxId\":\"${CURSOR}\"}")

  FOUND=$(echo "$RES" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
for e in d.get('result',{}).get('edges',[]):
    n = e['node']
    if n.get('code') == '$SHORTCODE':
        print(json.dumps(n))
" 2>/dev/null || true)

  if [ -n "$FOUND" ]; then
    echo "$FOUND"
    exit 0
  fi

  CURSOR=$(echo "$RES" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
pi = d.get('result',{}).get('page_info',{})
if pi.get('has_next_page'):
    print(pi.get('end_cursor',''))
" 2>/dev/null || true)

  if [ -z "$CURSOR" ]; then
    echo "Post nao encontrado em $PAGE paginas do perfil $FALLBACK_USERNAME." >&2
    echo "Se o post nao for do IVS, ajuste FALLBACK_USERNAME no script." >&2
    exit 1
  fi
  PAGE=$((PAGE + 1))
  echo "[fallback] pagina $PAGE..." >&2
done
