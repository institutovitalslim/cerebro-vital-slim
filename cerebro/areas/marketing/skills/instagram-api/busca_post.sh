#!/bin/bash
# Busca post do IVS pelo shortcode via RapidAPI
# Uso: ./busca_post.sh DV_HjMKlg5h

TARGET_CODE="${1:-}"
KEY="cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56"
CURSOR=""

if [ -z "$TARGET_CODE" ]; then
  echo "Uso: $0 <shortcode>"
  exit 1
fi

echo "Buscando post: $TARGET_CODE"

PAGE=1
while true; do
  RESULT=$(curl -s --max-time 30 \
    --request POST \
    --url https://instagram120.p.rapidapi.com/api/instagram/posts \
    --header 'Content-Type: application/json' \
    --header "x-rapidapi-host: instagram120.p.rapidapi.com" \
    --header "x-rapidapi-key: $KEY" \
    --data "{\"username\":\"institutovitalslim\",\"maxId\":\"$CURSOR\"}")

  FOUND=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
for e in d.get('result',{}).get('edges',[]):
    n = e['node']
    if n.get('code') == '$TARGET_CODE':
        cap = n.get('caption',{})
        text = cap.get('text','') if isinstance(cap,dict) else str(cap)
        print(text)
" 2>/dev/null)

  if [ -n "$FOUND" ]; then
    echo "=== POST ENCONTRADO (página $PAGE) ==="
    echo "$FOUND"
    exit 0
  fi

  CURSOR=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
pi = d.get('result',{}).get('page_info',{})
if pi.get('has_next_page'):
    print(pi.get('end_cursor',''))
" 2>/dev/null)

  if [ -z "$CURSOR" ]; then
    echo "Post não encontrado após $PAGE páginas"
    exit 1
  fi

  PAGE=$((PAGE + 1))
  echo "Página $PAGE..."
done
