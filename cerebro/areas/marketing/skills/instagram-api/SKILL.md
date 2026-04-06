---
name: instagram-api
description: >
  Busca posts, perfis e conteúdo do Instagram via RapidAPI (instagram120.p.rapidapi.com). Usar sempre que precisar acessar post por URL/shortcode, listar posts de um perfil, ou buscar metadados.
---

# Instagram API via RapidAPI

## Credenciais
- **Key:** `cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56`
- **Host:** `instagram120.p.rapidapi.com`
- **Base URL:** `https://instagram120.p.rapidapi.com`

## Perfil do IVS
- **Username:** `institutovitalslim`
- **UserID:** `60410930023`

## Endpoint para buscar post por URL (principal)

```bash
curl --request GET \
  --url 'https://instagram-scraper-stable-api.p.rapidapi.com/get_media_data.php?reel_post_code_or_url=<URL_ENCODED>&type=post' \
  --header 'Content-Type: application/json' \
  --header 'x-rapidapi-host: instagram-scraper-stable-api.p.rapidapi.com' \
  --header 'x-rapidapi-key: cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56'
```
- Funciona com qualquer URL pública do Instagram (post ou reel)
- Retorna caption completa em `edge_media_to_caption.edges[0].node.text`
- Retorna owner em `owner.username`
- API: `instagram-scraper-stable-api.p.rapidapi.com`

## Endpoints disponíveis

### Buscar posts de um perfil
```bash
curl --request POST \
  --url https://instagram120.p.rapidapi.com/api/instagram/posts \
  --header 'Content-Type: application/json' \
  --header 'x-rapidapi-host: instagram120.p.rapidapi.com' \
  --header 'x-rapidapi-key: cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56' \
  --data '{"username":"institutovitalslim","maxId":""}'
```
Retorna até 12 posts. Usar `end_cursor` do `page_info` como `maxId` para paginar.

### Buscar perfil
```bash
curl --request POST \
  --url https://instagram120.p.rapidapi.com/api/instagram/profile \
  --header 'Content-Type: application/json' \
  --header 'x-rapidapi-host: instagram120.p.rapidapi.com' \
  --header 'x-rapidapi-key: cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56' \
  --data '{"username":"institutovitalslim"}'
```

## Script de busca por shortcode

Para encontrar um post específico por shortcode (ex: `DV_HjMKlg5h`), paginar pelos posts do perfil:

```bash
#!/bin/bash
TARGET_CODE="DV_HjMKlg5h"
CURSOR=""
KEY="cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56"

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
    if n.get('code') == '${TARGET_CODE}':
        cap = n.get('caption',{})
        print(cap.get('text','') if isinstance(cap,dict) else str(cap))
" 2>/dev/null)

  [ -n "$FOUND" ] && { echo "FOUND: $FOUND"; break; }

  CURSOR=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
print(d.get('result',{}).get('page_info',{}).get('end_cursor',''))
" 2>/dev/null)

  [ -z "$CURSOR" ] && { echo "Post não encontrado"; break; }
done
```

## Notas operacionais
- A API retorna 12 posts por página
- `DV_` prefix = posts recentes (2026); `C` prefix = posts antigos (2023-2024)
- Endpoint `/api/instagram/post/info` NÃO existe nesta API
- Paginação é necessária para posts mais antigos
