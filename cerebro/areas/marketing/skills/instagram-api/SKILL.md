---
name: instagram-api
description: >
  Busca posts, reels, perfis e conteudo do Instagram. API PADRAO: instagram-scraper-stable-api
  (mais rapida, pega direto por shortcode ou URL). Fallback: instagram120 (para listar posts de
  um perfil com paginacao, funcao que a Stable API nao cobre). Usar sempre que precisar acessar
  post por URL/shortcode, listar posts de um perfil, ou buscar metadados.
---

# Instagram API

## API PADRAO - Instagram Scraper Stable API

Use esta como primeira opcao sempre que precisar buscar dados de post ou reel.

- **Host:** `instagram-scraper-stable-api.p.rapidapi.com`
- **Base URL:** `https://instagram-scraper-stable-api.p.rapidapi.com`
- **Key (compartilhada):** `cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56`

### Motivos para ser o padrao
- acessa post direto por shortcode ou URL completa (sem paginar perfil)
- retorna caption completa, owner, display_url, dimensions em 1 chamada
- latencia < 2s tipica
- funciona para posts publicos e reels

### Endpoint principal: buscar post/reel por shortcode ou URL
```bash
# Por shortcode
curl -sS --max-time 20   "https://instagram-scraper-stable-api.p.rapidapi.com/get_media_data.php?reel_post_code_or_url=DV_HjMKlg5h&type=post"   -H 'x-rapidapi-host: instagram-scraper-stable-api.p.rapidapi.com'   -H 'x-rapidapi-key: cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56'

# Por URL completa (URL-encoded)
curl -sS --max-time 20   "https://instagram-scraper-stable-api.p.rapidapi.com/get_media_data.php?reel_post_code_or_url=https%3A%2F%2Fwww.instagram.com%2Fp%2FDV_HjMKlg5h%2F&type=post"   -H 'x-rapidapi-host: instagram-scraper-stable-api.p.rapidapi.com'   -H 'x-rapidapi-key: cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56'

# Para reel, usar type=reel
```

### Parametros
- `reel_post_code_or_url` (obrigatorio): shortcode puro (ex: `DV_HjMKlg5h`) ou URL completa URL-encoded
- `type` (obrigatorio): `post` ou `reel`

### Campos uteis no retorno
- `shortcode` - shortcode do post
- `owner.username` - perfil dono do post
- `edge_media_to_caption.edges[0].node.text` - caption completa
- `display_url` - URL da imagem principal
- `dimensions` - largura/altura
- `is_video` - boolean

### Erros comuns
- `{"error":"media_code should not be a url..."}` - voce passou URL sem encode. URL-encode antes.
- `{"error":"post/reel data not found..."}` - shortcode invalido, post removido ou privado. Se type=post falhar, tentar type=reel.

---

## Fallback - instagram120 (usar so quando necessario)

Use esta API apenas quando:
- precisar **listar** posts de um perfil com paginacao (Stable API nao tem esse endpoint)
- precisar **buscar perfil** por username (Stable API nao tem esse endpoint)
- Stable API retornar erro e precisar procurar o post paginando o perfil

### Credenciais
- **Host:** `instagram120.p.rapidapi.com`
- **Base URL:** `https://instagram120.p.rapidapi.com`
- **Key:** `cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56` (mesma)

### Perfil do IVS
- **Username:** `institutovitalslim`
- **UserID:** `60410930023`

### Listar posts de um perfil (paginacao)
```bash
curl -sS --request POST   --url https://instagram120.p.rapidapi.com/api/instagram/posts   --header 'Content-Type: application/json'   --header 'x-rapidapi-host: instagram120.p.rapidapi.com'   --header 'x-rapidapi-key: cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56'   --data '{"username":"institutovitalslim","maxId":""}'
```
Retorna ate 12 posts. Usar `page_info.end_cursor` como `maxId` para paginar.

### Buscar perfil
```bash
curl -sS --request POST   --url https://instagram120.p.rapidapi.com/api/instagram/profile   --header 'Content-Type: application/json'   --header 'x-rapidapi-host: instagram120.p.rapidapi.com'   --header 'x-rapidapi-key: cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56'   --data '{"username":"institutovitalslim"}'
```

---

## Scripts prontos

### `busca_post.sh <shortcode_ou_url>`
Script padrao. Tenta a Stable API primeiro (por shortcode ou URL); se falhar com "not found", tenta como reel; so depois cai no instagram120 paginando pelo perfil IVS. Uso:

```bash
./busca_post.sh DV_HjMKlg5h
./busca_post.sh https://www.instagram.com/p/DV_HjMKlg5h/
./busca_post.sh https://www.instagram.com/reel/DV_HjMKlg5h/
```

---

## Regras operacionais

- **Sempre que a task for "buscar info no Instagram", comece pela Stable API.** So use instagram120 quando Stable nao cobrir o caso (listagem, perfil, busca em perfil especifico).
- A key eh compartilhada entre ambas as APIs (ambas hospedadas na RapidAPI).
- Stable API aceita tanto shortcode puro quanto URL completa (URL-encoded).
- `DV_` prefix = posts recentes (2026); `C` prefix = posts antigos (2023-2024).
- Endpoint `/api/instagram/post/info` nao existe na instagram120 - so funciona via paginacao de posts do perfil.
- Paginacao na instagram120 eh necessaria para posts antigos quando buscando por shortcode via fallback.

## Notas de mudanca

- **2026-04-22:** Stable API promovida a padrao (antes era usada so em casos especificos). Fundamento: latencia menor, endpoint direto por shortcode/URL, menos chamadas. instagram120 fica como fallback para listagem/perfil.
