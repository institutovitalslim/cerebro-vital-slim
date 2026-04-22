# Lições da Sessão 2026-04-20 — Carrossel Intestino (end-to-end)

**Contexto**: Sessão longa de correções na skill `tweet-carrossel` + `prompt-imagens`
+ `memoria-cientifica` + bridge Z-API da Clara, tendo como caso-teste a criação de
carrossel sobre "Eixo Intestino-Saúde Sistêmica" a partir de link do Instagram.

**Resultado final**: carrossel completo de 10 slides JPEG 1080x1350 entregue via Telegram,
com capa (gancho aprovado + destaques dourados + fundo 3D intestino lateral), slide 2
com paper PubMed real (título completo, autores, PMID, DOI) e 8 slides tweet com PMIDs
científicos embasando cada afirmação.

---

## 1. Bugs técnicos encontrados e corrigidos

### 1.1 `memory_store.py` — OSError ao tratar texto longo como path
**Sintoma**: crash quando conteúdo original/research passa como argumento direto
(não arquivo):
```
OSError: [Errno 36] File name too long
```
**Causa raiz**: `Path(v).is_file()` chama `os.stat()` que rejeita paths > 255 chars
com `OSError 36`, em vez de retornar `False`.
**Correção**: envolver em `try/except (OSError, ValueError)` — fallback para usar
`v` como texto direto.

### 1.2 `make_cover.py` — strip não removia `?` e `!` de palavras-destaque
**Sintoma**: headline "ANSIEDADE? ACNE? OBESIDADE?" gerada com todas palavras em
branco (nenhuma dourada), mesmo com `--destaques "ANSIEDADE,ACNE,OBESIDADE"`.
**Causa raiz**: `word.strip().upper().strip('"').strip("'").strip(",").strip(".")`
não removia `?` nem `!`. "ANSIEDADE?" ≠ "ANSIEDADE" no set.
**Correção**: adicionar `.strip(chr(63)).strip(chr(33))` na limpeza. Agora normaliza
`" ' , . ? !`.

### 1.3 `/root/make_cover.py` desatualizado
**Sintoma**: fix aplicado no `.openclaw/workspace/skills/.../make_cover.py` não
surtia efeito.
**Causa raiz**: `compose_cover.py` chamava `/root/make_cover.py` (não o da skill).
Havia 2 cópias divergentes.
**Correção**: sempre sincronizar `cp skill/make_cover.py /root/make_cover.py`
após edição. Idealmente: compose_cover deve usar path relativo à skill.

### 1.4 Chromium snap — AppArmor bloqueando staging
**Sintoma 1**: `chromium --screenshot=/tmp/X.png` → stdout "X bytes written" mas
arquivo **não existe no FS**. Silent failure.
**Sintoma 2**: `chromium --screenshot=/root/.chromium_tmp/X.png` →
`ERROR: Failed to create SingletonLock: Permission denied`.
**Causa raiz**: Chromium do snap tem AppArmor sandbox. Bloqueia:
- `/tmp/` (escrita)
- Qualquer diretório com prefixo `.` em `/root/.X/`
**Correção**:
- Staging em `/root/chromium_tmp/` (sem dot prefix)
- Profile em `/root/chromium_prof_<id>/` (sem dot prefix)
- Mover de staging → destino final após subprocess.run

### 1.5 PubMed — header NIH ausente / sintético rejeitado
**Sintoma**: validação "SEM header NIH azul (0.0%)" em todos 6 user-agents.
Cascata caía no placeholder.
**Causa raiz dupla**:
1. PubMed com rate-limit/detecção anti-bot (429 ou HTML vazio)
2. Sintética gerada por `render_synthetic()` era 87% branca (natural — papel branco
   com texto preto) e era rejeitada pela validação `is_valid_screenshot`.
**Correção**:
- Sintética: validação relaxada (só precisa existir + > 5KB) — é imagem renderizada
  com header NIH garantido, não precisa passar pelas heurísticas de captcha.

### 1.6 Crop fixo cortava título do paper sintético
**Sintoma**: título aparecia "The gut microbiota in anxiety and depression - A sys"
em vez do "...A systematic review" completo.
**Causa raiz**: crop fixo `img.crop((0, 0, 910, 720))` para sintética de 1200×900
cortava os 290px da direita.
**Correção**: crop adaptativo:
- Sintética (h < 1000): mantém largura cheia (`w, min(h, 800)`)
- Real PubMed (h ≥ 1000): crop `(0, 0, w, 720)` com largura cheia

### 1.7 Instagram fetch — bloqueio sem autenticação
**Sintoma**: HTTP fetch direto da URL do post retornava HTML de footer genérico
(lista de idiomas, links "About/Blog/Jobs").
**Correção**: usar RapidAPI (`instagram-scraper-stable-api` ou `instagram120`).
Key em `/root/cerebro-vital-slim/cerebro/areas/marketing/skills/instagram-api/SKILL.md`.
Criado `fetch_instagram.py` com cascata de 2 APIs.

### 1.8 RapidAPI quota mensal esgotada
**Sintoma**: `stable-api` → `"You have exceeded the MONTHLY quota"`.
**Correção**: fallback automático para `instagram120.p.rapidapi.com/api/instagram/posts`
que pagina o perfil @institutovitalslim até achar o shortcode.

### 1.9 Gemini 503 Service Unavailable
**Sintoma**: `ingest_content.py` falhou em research + clinical + summary por
`HTTP Error 503`.
**Correção**: conteúdo crítico pode vir diretamente do Tiaro (texto do post em vez
de URL quando Instagram bloqueia). Script já tem fallback Gemini quando Perplexity
falha, mas Gemini também pode falhar. Pipeline deve graceful-degrade ou pausar.

### 1.10 Z-API truncamento de mensagens longas
**Sintoma**: "Message failed" no WhatsApp quando Clara mandava resposta > 4096 chars.
**Correção**: `_split_message_for_zapi()` em `zapi_clara_bridge.py`. Divide em chunks
de 3500 chars respeitando parágrafos > frases > palavras. Delay de 1.2s entre chunks.

---

## 2. Violações de comportamento da Clara (11 documentadas)

Clara falhou gravemente no 1º e 2º teste de carrossel de intestino:

| # | Violação | Correção aplicada |
|---|----------|-------------------|
| 1 | Chain-of-thought em INGLÊS vazou ao Tiaro | PROIBIÇÃO 1 no CLAUDE.md |
| 2 | Pulou ETAPA 0 (memoria-cientifica) | PROIBIÇÃO 4 no CLAUDE.md |
| 3 | Não usou `ingest_content.py` com URL IG | Integração com `fetch_instagram.py` + SKILL |
| 4 | Mentiu sobre caminho `memory/science/...md` | PROIBIÇÃO 3 (não inventar paths) |
| 5 | Entregou só copy em TEXTO, não gerou JPEGs | PROIBIÇÃO 2 + orquestrador `clara_create_carrossel_from_post.py` |
| 6 | Não usou `capture_pubmed.py` — colou preview auto | PROIBIÇÃO 6 (nunca usar link preview) |
| 7 | Encurtou versão aprofundada sem pedir | PROIBIÇÃO 5 (nunca auto-modificar aprovado) |
| 8 | Aprovação em loop (5 rodadas) | PROIBIÇÃO 5 (fluxo linear 1 aprovação por etapa) |
| 9 | Reutilizava mesma foto (braços cruzados) | `photo_selector.py` + `usage.json` |
| 10 | Preservava pose/roupa/cenário da referência | `PRESERVE_CLAUSE` endurecida — só ROSTO |
| 11 | Gerou imagem da Dra sem foto real | REGRA #1 SKILL prompt-imagens |

---

## 3. Arquitetura final validada

### Pipeline end-to-end (carrossel científico a partir de URL)

```
URL Instagram/Post
    ↓
[fetch_instagram.py] — RapidAPI (stable-api → fallback instagram120)
    ↓
texto do post (caption completa)
    ↓
[memory_search.py] — embeddings Gemini 3072d (score cosseno)
    ├── se score ≥ 0.75: usar pesquisa existente
    └── se < 0.70: [ingest_content.py]
                        ├── Perplexity (deep research)
                        ├── Gemini (fallback + aplicação clínica IVS)
                        ├── resumo TL;DR
                        └── [memory_store.py] — embeddings + master.jsonl
    ↓
APROVAÇÃO do Tiaro (resumo executivo + aplicação clínica prática)
    ↓
[photo_selector.py] — melhor foto da Dra para o tema
    ├── se score < 0.55: [generate_variation.py] via NanoBanana 2 Pro
    └── match direto do acervo
    ↓
[compose_cover_auto.py] (orquestra: rembg → bg contextual → compose → make_cover)
    ├── fundo: Unsplash (processado: blur 8, brightness 0.35-0.55)
    ├── Montserrat Black cap 150, align topo, destaques dourados
    └── saída JPEG 1080×1350
    ↓
[capture_pubmed.py] — 5 estratégias em cascata
    ├── PubMed direto (6 UAs + snap-safe staging)
    ├── Archive.org Wayback
    ├── PMC (eutils)
    ├── Sintético (gera card estilo PubMed com metadados reais)
    └── Placeholder (último recurso)
    ↓
[gen_slides.py / HTML+Chromium] — slides 3-10
    ├── avatar 96px + nome 40px + handle 30px
    ├── texto corpo 44px line-height 1.30
    └── saída JPEG 85 quality
    ↓
VALIDAÇÃO — 10 JPEGs existem, cada > 10KB
    ↓
[send_to_telegram.py] — chat_id -1003803476669, thread_id X
    ↓
LOG em /root/cerebro-vital-slim/cerebro/empresa/conhecimento/logs/
```

### Scripts oficiais (em 2 locais sincronizados)

- `/root/.openclaw/workspace/skills/`
- `/root/cerebro-vital-slim/cerebro/empresa/skills/`

| Skill | Scripts |
|-------|---------|
| `tweet-carrossel` | compose_cover, compose_cover_auto, make_cover, capture_pubmed, catalog_photos, photo_selector, generate_variation, send_to_telegram, gen_slides_full, fetch_instagram, clara_create_carrossel_from_post |
| `prompt-imagens` | build_prompt, generate_image, generate_with_reference, add_overlay, clara_create_image |
| `memoria-cientifica` | ingest_content, memory_store, memory_search |

---

## 4. CLAUDE.md — 7 PROIBIÇÕES ABSOLUTAS

Adicionadas ao sistema prompt da Clara (openclaw + cérebro sync):

1. **Nunca responder/pensar em inglês** (nem chain-of-thought visível)
2. **Nunca entregar carrossel como TEXTO** — sempre JPEGs reais
3. **Nunca inventar caminhos** (memória real: `conhecimento/pesquisas/YYYY-MM-DD_<slug>/`)
4. **Nunca pular ETAPA 0** (memoria-cientifica obrigatória em carrossel)
5. **Nunca pedir aprovação em loop** nem encurtar sem pedir
6. **Nunca usar preview automático do Telegram** como slide 2
7. **Todo paper citado tem resumo prático obrigatório** (título + PMID + DOI +
   achados + aplicação clínica IVS + uso no carrossel)

---

## 5. Boas práticas validadas

### Capa
- Foto da Dra deve ter contexto relacionado ao tema (seletor semântico)
- Fundo: Unsplash → blur radius 8 + brightness 0.35-0.55
- Fundos 3D → **posicionar LATERALMENTE** (não centralizados atrás da Dra)
- `rembg` remove bg chapado (azul, verde) antes de compor
- Gradient escuro (direção contrária) dá profundidade
- Destaques dourados: strip `" ' , . ? !` obrigatório

### Poses (biblioteca de 24)
- NÃO repetir "braços cruzados frontal" em carrosséis consecutivos
- Consultar `usage.json` para diversificação automática
- Ao reinterpretar foto via IA: preservar APENAS rosto (não pose/roupa/cenário)

### PubMed
- Rate-limit + anti-bot do PubMed é realidade frequente
- Sintético com eutils (metadados reais: título, autores, PMID, DOI) é
  alternativa aceitável quando direct falha
- Validação sintética deve ser relaxada (só tamanho)
- Crop adaptativo: sintética 1200×900 full width, real 1200×1800 top 720px

### Chromium snap
- Staging SEMPRE em `/root/chromium_tmp/` (sem dot prefix)
- Profile em `/root/chromium_prof_<id>/`
- Mover staging → destino após cada tentativa

### Instagram
- Fetch direto não funciona (HTML vazio)
- RapidAPI com 2 APIs em cascata é necessário
- Key documentada em `cerebro/areas/marketing/skills/instagram-api/SKILL.md`

### WhatsApp via Z-API
- Mensagens > 4096 chars → split em chunks de 3500 com delay 1.2s
- Preservar limites naturais: `\n\n` > `\n` > `. ! ?` > espaço

---

## 6. Gancho de copy — aprendizado

User rejeitou "QUANDO O INTESTINO NÃO VAI BEM OS SINAIS PODEM APARECER LONGE DELE"
por ser fraco.

Aprovou: **"ANSIEDADE? ACNE? OBESIDADE? UMA CAUSA E MUITOS SINTOMAS"**

Princípios extraídos:
- Pain points concretos (3 sintomas comuns) > abstrações
- Formato pergunta → resposta cria curiosidade
- "UMA CAUSA E MUITOS SINTOMAS" condensa tese em 5 palavras
- Destaques dourados nos **pain points** (não nas respostas) funcionam melhor

---

## 7. Estado final do conhecimento no cérebro

Pesquisas armazenadas em `/root/cerebro-vital-slim/cerebro/empresa/conhecimento/pesquisas/`:
- `2026-04-17_creatina-cognitivo` (PMID 39070254)
- `2026-04-17_deficiencia-global` (PMID 41504160 — magnésio)
- `2026-04-20_eixo-intestino-saude-sistemica` (PMIDs 33271426, 27252163, 36817115)

Embeddings Gemini 3072d em `index/embeddings.jsonl`.
Taxonomia em `index/topics.json`.
Logs em `logs/YYYY-MM-DD.log`.

---

## 8. Próximos passos / débitos técnicos

- [ ] `catalog_photos.py` completou só 8/40 fotos (rate limit Gemini). Rodar de novo.
- [ ] Gemini Image quota se esgota frequentemente. Alternativa: `imagen-4.0-fast`
      (requer plano pago) ou melhor caching.
- [ ] Clara ainda NÃO foi forçada via gateway OpenClaw a executar os scripts.
      Ela AINDA pode usar tools nativas. Próximo passo: restringir toolset do
      agente `main` ou adicionar hook que intercepta pedidos de imagem.
- [ ] `fetch_instagram.py` testado mas não integrado ao `clara_create_carrossel_from_post.py`.
- [ ] PubMed direto sempre retorna captcha hoje. Investigar se proxy residencial
      resolve, ou se sintético é permanente.
