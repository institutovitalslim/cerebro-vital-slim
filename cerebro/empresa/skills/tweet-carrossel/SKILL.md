---
name: tweet-carrossel
description: >
  Gera carrosseis completos para o Instagram no formato tweet (estilo X/Twitter).
  Fluxo: primeiro criar a COPY (texto), depois de aprovada, gerar as IMAGENS.
  Capa via compose_cover.py com foto REAL da Dra. Slides via gen_slides.py.
  Slide do paper SEMPRE validado via capture_pubmed.py. Entrega SEMPRE via Telegram.
  Use quando: "carrossel", "criar carrossel", "formato tweet", "slides instagram",
  "carrossel cientifico", "montar carrossel", "criar slides".
metadata:
  version: 4.0.0
  domain: marketing
  owner: main
---

# Tweet Carrossel v4 - Geracao Completa de Carrosseis Instagram

## 🚨 ORQUESTRADOR UNICO — Use isto quando Tiaro enviar URL/link

Quando Tiaro enviar URL de post/artigo cientifico pedindo carrossel, Clara DEVE
rodar UM unico comando que faz toda a cadeia:

```bash
python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/clara_create_carrossel_from_post.py \
  --url "<URL>" \
  --topic "<topico>" \
  --slug "<slug>" \
  --thread-id 4
```

Faz automaticamente:
1. memory_search (verifica se ja pesquisou o tema)
2. ingest_content (se novo: Perplexity + aplicacao clinica + armazena)
3. Apresenta resumo ao Tiaro e pausa
4. Apos --approve: gera copy + capa + slide 2 PubMed + slides tweet
5. Valida JPEGs existem
6. send_to_telegram entrega os 10 slides

NAO inventar fluxo proprio. NAO entregar copy em texto. UM comando, carrossel
completo.

---

## FLUXO DE TRABALHO OBRIGATORIO (4 ETAPAS)

### ETAPA 0 - PRE-REQUISITO: MEMORIA CIENTIFICA (OBRIGATORIA)

**ANTES de qualquer copy**, Clara DEVE rodar a skill `memoria-cientifica`:

1. Buscar na memoria existente:
```bash
python3 /root/cerebro-vital-slim/cerebro/empresa/skills/memoria-cientifica/scripts/memory_search.py   --query "<TEMA_DO_CARROSSEL>" --top-k 3
```

2. **Se encontrou resultado com score >= 0.70**: usar o `clinical.md` e `research.md` da
   pesquisa como FONTE CIENTIFICA da copy. Clara NAO inventa informacao.

3. **Se nao encontrou OU score < 0.70**: rodar ingestao primeiro:
```bash
python3 /root/cerebro-vital-slim/cerebro/empresa/skills/memoria-cientifica/scripts/ingest_content.py   --url "<URL_RECEBIDA>" --topic "<TOPICO>"
```
   Apresentar ao Tiaro o resumo + aplicacao clinica, aguardar aprovacao, e SO ENTAO
   prosseguir para ETAPA 1 (copy).

**NUNCA criar carrossel sem embasamento cientifico da memoria.**

---
## FLUXO DE TRABALHO OBRIGATORIO (COM ETAPA 0 OBRIGATORIA)

### ETAPA 1 - COPY (texto)
1. Usuario envia tema, paper cientifico ou arquivo de referencia
2. Clara cria um RASCUNHO da copy de todos os slides
3. Clara aciona a skill llm-council (conselho) para avaliar e refinar a copy
4. Clara incorpora o feedback do conselho e gera a COPY FINAL
5. Clara apresenta a copy final para aprovacao do usuario
6. Usuario aprova ou pede ajustes
7. SO APOS APROVACAO da copy, seguir para etapa 2

### ETAPA 2 - IMAGENS
1. Clara gera a capa via `compose_cover.py` (NUNCA gera foto da Dra. via IA)
2. Clara captura o PubMed via `capture_pubmed.py` (NUNCA confia em captura sem validar)
3. Clara gera slide 2 (paper) via HTML + Chromium
4. Clara gera slides 3+ via gen_slides.py (saida JPEG, < 200KB por slide)

### ETAPA 3 - ENTREGA VIA TELEGRAM (OBRIGATORIA)

Apos gerar todos os slides, SEMPRE enviar via Telegram usando send_to_telegram.py:

```bash
export TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/send_to_telegram.py \
  --chat-id -1003803476669 \
  --thread-id <THREAD_DO_USUARIO> \
  --dir <DIRETORIO_DOS_SLIDES> \
  --caption "<TITULO_DO_CARROSSEL>"
```

**NUNCA** apenas salvar arquivos na VPS e dizer "feito" — o usuario precisa receber os JPEGs pelo Telegram.

---

## ESTRUTURA DO CARROSSEL

| Slide | Tipo | Metodo de geracao |
|-------|------|-------------------|
| 1 | Capa (foto real Dra. + headline) | compose_cover.py (rembg + fundo + make_cover) |
| 2 | Paper cientifico (texto tweet + PubMed) | capture_pubmed.py + HTML + Chromium |
| 3-N | Tweet format (texto puro) | Python/Pillow (gen_slides.py / HTML templates) |

---

## SLIDE 1 - CAPA

**Fundo: PRETO #000000** — A capa mantém fundo preto com foto da Dra. e headline em branco/dourado.
**Slides 2+ (tweet): fundo BRANCO #FFFFFF** com texto preto.

### Pipeline OBRIGATORIO: compose_cover.py

```bash
export GOOGLE_API_KEY=$GOOGLE_API_KEY
python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/compose_cover.py \
  --foto <FOTO_DRA> \
  --tema "<DESCRICAO_FUNDO>" \
  --circulo <IMAGEM_CIRCULO> \
  --headline "<LINHA1|LINHA2|LINHA3>" \
  --destaques "<PALAVRA1,PALAVRA2,PALAVRA3>" \
  --out /root/capa_<TEMA>.jpg
```

### Pipeline faz tudo automaticamente:
1. Remove fundo da foto da Dra. com rembg + suavizacao de bordas (sem halo)
2. Gera fundo contextual via Gemini OU usa --skip-bg <path> para fundo manual
3. Compoe Dra. cintura-para-cima sobre o fundo contextual
4. Gera capa final JPEG com make_cover.py (Montserrat Black, simbolo V, destaques dourados)

### REGRAS CRITICAS DA CAPA (NUNCA QUEBRAR)

### REGRA DE MANUTENCAO DA FOTO EM ALTERACOES (IMPORTANTE)

**Quando o usuario pede ALTERACAO em conteudo ja criado** (ajustar acentos, trocar destaques,
corrigir headline, refinar texto, etc.): **MANTER a mesma foto da versao anterior**. Nao rodar
seletor novamente — a foto original ja foi validada como adequada ao tema.

Use `compose_cover.py` direto com `--foto "<caminho_foto_anterior>"` em vez de
`compose_cover_auto.py`. Nao marcar como usada novamente.

**Apenas rodar seletor nova foto quando:**
- For um NOVO carrossel/post sobre outro tema
- Usuario pedir EXPLICITAMENTE "troca a foto" ou "usa outra foto"

Exemplos:
- "corrija os acentos" -> **manter foto**
- "ajusta destaques" -> **manter foto**
- "troca a foto" -> **rodar seletor** (respeitando penalidade de uso)
- "novo carrossel sobre X" -> **rodar seletor**

---

### SELECAO DA FOTO DA DRA (OBRIGATORIA - sem pular)

Clara NUNCA escolhe a foto manualmente nem reutiliza a mesma. SEMPRE roda o seletor inteligente:

```bash
python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/photo_selector.py   --theme "<TEMA_DO_CARROSSEL>" --top-k 5
```

O seletor:
1. Usa embeddings Gemini para matchear tema vs descricoes das fotos catalogadas
2. Penaliza fotos usadas nos ultimos 30 dias (diversificacao automatica)
3. Retorna ranking com score final (semantico x penalidade de uso)

**Se `needs_generation = false`** (score semantico >= 0.55):
- Usa a foto vencedora como `--foto` no `compose_cover.py`
- APOS gerar a capa com sucesso, marca como usada:
  ```bash
  photo_selector.py --mark-used "<nome_arquivo>" --with-theme "<tema>"
  ```

**Se `needs_generation = true`** (score < 0.55, nenhuma foto adequada):
- Clara gera uma VARIACAO via NanoBanana 2 usando a foto mais proxima como base:
  ```bash
  python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/generate_variation.py     --base "<foto_base_do_top1>"     --variation "<descricao_do_cenario_ideal_para_o_tema>"     --out "/root/dra_variation_<tema>.png"
  ```
- A variacao preserva identidade facial (rosto, cabelo) mas altera cenario/iluminacao/roupas
- Incluir no prompt a instrucao canônica de consistencia facial estrita:
  `Enable strict facial consistency mode. Prioritize the facial features from the provided reference image for all subsequent generations. Maintain the subject's identity accurately while only adapting the pose, lighting, and background. Do not alter the core facial structure.`
- Variacao criada fica disponivel para futuro uso (adicionada ao catalogo via nova rodada de catalog_photos.py)

**Regras gerais da foto:**
- Acervo em `/root/.openclaw/workspace/fotos_dra/originais/` (40+ fotos catalogadas)
- Catalogo com descricoes em `/root/.openclaw/workspace/fotos_dra/catalog.json`
- Registro de uso em `/root/.openclaw/workspace/fotos_dra/usage.json`
- NUNCA jaleco - sempre blazer escuro elegante
- NUNCA sorriso exagerado (exceto temas que pedem acolhimento, ex: maternidade)
- NUNCA corpo inteiro - cintura para cima
- Diversificacao automatica: sistema evita reuso da mesma foto em carrosseis proximos

**Regras do fundo:**
- NUNCA fundo que pareça loja de bebidas
- Fundo contextual via Unsplash: buscar, escurecer (brightness 0.35-0.40), blur (radius 8)
- Se Gemini quota excedida: buscar imagem no Unsplash e usar --skip-bg
- Tema deve ser CLARAMENTE relacionado ao assunto (ex: magnesio=tubos de sangue; creatina=potes de suplementos CREATINE+PROTEIN+PRE-WORKOUT)
- Testar: se fundo nao tem relacao obvia com tema, trocar

**Regras da headline:**
- Fonte Montserrat Black (instalada em /usr/local/share/fonts/)
- Cores: branco + dourado #9F8844
- Cap max 150px, mas o script calcula automaticamente para caber na safe area
- Line-height 1.05 (tight)
- Alinhamento: TOPO da area de texto (NAO centrado) para eliminar espaco vazio
- TEXT_AREA_START: 0.58 (logo apos linha dourada) — **elevado para safe area do feed**
- PHOTO_HEIGHT_RATIO: 0.54 — **reduzido para dar mais espaco ao texto**
- LINE_Y_RATIO: 0.56 — **acompanha TEXT_AREA_START**
- **Safe area para feed (1:1):** O Instagram corta ~135px do topo e da base da capa 4:5. A headline deve caber inteiramente dentro da area segura central. O script `make_cover.py` calcula o tamanho da fonte automaticamente para garantir isso.

**Regras de destaques:**
- Palavras em dourado separadas por virgula
- Todas as palavras-chave devem estar na mesma cor (dourado)
- Ex: headline "SEU MAGNESIO ESTA NORMAL MAS SEU CORPO DISCORDA" -> destaques "MAGNESIO,NORMAL,CORPO,DISCORDA"

### Saida:
- SEMPRE JPEG quality=85 (limite 20MB do Claude)
- Tamanho tipico: ~110-130KB

---

## SLIDE 2 - PAPER CIENTIFICO

### CAPTURA DO PUBMED - VALIDACAO OBRIGATORIA

**NUNCA** aceitar screenshot do PubMed sem validar. Usar SEMPRE:

```bash
python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/capture_pubmed.py \
  --pmid <PMID> \
  --out /root/pubmed_<PMID>.png
```

**O script tem CASCATA de 5 estrategias - NUNCA FALHA:**
1. PubMed direto com 6 user-agents (Safari Mac, Chrome Win/Linux, Firefox, iPhone, Googlebot) + incognito + anti-bot flags + perfil limpo por tentativa
2. Fallback: Archive.org Wayback Machine
3. Fallback: PubMed Central (PMC) se disponivel
4. Fallback: gera imagem sintetica com metadados reais via eutils API (cor NIH, titulo, autores, PMID, DOI)
5. Ultimo recurso: placeholder com link

**Validacao automatica:**
- Arquivo > 50KB
- Header contem pixels azul NIH (RGB 32,84,147) >= 15%
- Pagina nao eh > 85% branca (detecta captcha)

**A CLARA DEVE CONTINUAR ATE CONSEGUIR**. O script NUNCA para - roda ate ter uma imagem valida do paper, seja do PubMed, PMC, Archive ou sintetica.

### Formato do slide 2:
- Fundo branco #FFFFFF
- Avatar + nome + handle no topo (mesmo padrao dos slides tweet)
- Texto em cor unica #000000
- Screenshot do PubMed centralizado no espaco abaixo do texto
- Screenshot deve incluir: header NIH azul, PubMed logo, titulo completo, autores, PMID, DOI
- Imagem respeita margens laterais, com border-radius

### Checklist visual do slide 2 ANTES de entregar:
- [ ] Header azul "NIH National Library of Medicine" visivel
- [ ] Logo PubMed visivel
- [ ] Titulo do paper completo
- [ ] Autores listados
- [ ] PMID e DOI aparecem
- [ ] NAO ha texto "403 Forbidden" na imagem
- [ ] NAO ha captcha "Select all images" visivel

---

## SLIDES 3+ - FORMATO TWEET

### Avatar OBRIGATORIO: arquivo "Foto Perfil Daniely.png"
- Local: `C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Banco de imagens\Dany\Ensaio Fotografico\Fotos\Foto Perfil Daniely.png`
- VPS: `/root/avatar_hq.png` (= /root/avatar_hq_original.png)
- Especificacoes: 320x320 PNG, fundo transparente, frame dourado circular, Dra centralizada dentro
- Base64 em: /root/avatar_hq_b64.txt

### CSS do header (avatar + nome + handle):

```css
.header { display: flex; align-items: center; gap: 28px; margin-bottom: 50px; flex-shrink: 0; }
.avatar { width: 96px; height: 96px; border-radius: 50%; overflow: hidden; flex-shrink: 0; }
.avatar img { width: 100%; height: 100%; object-fit: cover; display: block; }
.user-info { display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.name-row { display: flex; align-items: center; line-height: 1.15; }
.name { font-weight: 700; font-size: 58px; color: #000000; line-height: 1.15; }
.verified { 
  display: inline-block; width: 38px; height: 38px; 
  background: #1d9bf0; border-radius: 50%; 
  text-align: center; line-height: 38px; font-size: 20px;
  color: #fff; margin-left: 12px; font-weight: 700; 
}
.handle { color: #71767b; font-size: 41px; line-height: 1.15; }
```

**CRITICAL:** Avatar = 96px (altura que casa com nome+handle ~90px, evita desalinhamento visual)

### CSS do corpo do texto:

```css
body { padding: 60px 64px; display: flex; flex-direction: column; }
.centered { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.content { flex-shrink: 0; }
p { font-size: 60px; line-height: 1.28; color: #000000; margin-bottom: 36px; font-weight: 400; }
```

### ESPECIFICACOES FINAIS DOS SLIDES

| Elemento | Valor |
|----------|-------|
| Tamanho | 1080 x 1350 px (4:5) |
| Fundo | branco #FFFFFF |
| Padding | 60px 64px |
| Avatar | 96px circular |
| Nome | bold, preto #000000, 58px, line-height 1.15 |
| Selo verificado | circulo azul #1D9BF0, ~46px |
| Handle | regular, cinza #71767B, 41px, line-height 1.15 |
| Gap avatar-texto | 28px |
| Texto corpo | regular, preto #000000, 60px, line-height 1.28 |
| Gap entre paragrafos | 36px margin-bottom |
| Cor do texto | UMA COR SO (#000000) - sem bold, sem destaques |
| Saida | JPEG quality=85, ~50-120KB por slide |

### ESTRUTURA DE CONTEUDO (10 SLIDES — Viral Content Strategy)

Cada carrossel deve contar uma historia, nao apenas transmitir informacao. Usar gaps de curiosidade, gatilhos emocionais e open loops para manter o leitor deslizando.

**Slide 1 – HOOK (Pattern Interrupt):**
- Headline ousada, controversa ou que desperta curiosidade
- Fazer o leitor pensar: "Espera... o que?"
- Usar tensao, surpresa ou afirmacao forte
- Maximo 5-10 palavras

**Slide 2 – REHOOK (Open Loop):**
- Aumentar a intriga sem dar a resposta
- Preparar o resultado, construir gap de curiosidade
- Fazer com que PRECISEM do proximo slide

**Slide 3 – RELATABLE PAIN / INICIO DA HISTORIA:**
- Comecar uma historia curta ou situacao identificavel
- "A maioria das pessoas pensa que..."
- "Eu costumava..."
- "Todo mundo faz isso errado..."

**Slides 4-7 – VALOR (Historia + Insights):**
- Entregar o conteudo principal atraves de um fluxo narrativo
- Quebrar expectativas
- Revelar insights passo a passo
- Cada slide = 1 ideia-chave
- Frases curtas e impactantes
- Misturar storytelling + valor acionavel

**Slide 8 – TURNING POINT (Momento AHA):**
- Revelar o insight-chave ou mudanca de perspectiva
- Deve parecer uma realizacao
- Este e o momento "salvavel"

**Slide 9 – ACTIONABLE TAKEAWAY:**
- Dar passos claros e praticos
- Facil de aplicar imediatamente

**Slide 10 – CTA (Engagement Trigger):**
- Call-to-action direto no texto
- Ex: "Comenta 'QUERO' que eu te envio"
- Ex: "Me segue para mais"
- Ex: "Salva isso antes que suma"

### REGRAS DE ESCRITA

1. Texto CONVERSACIONAL, nao tecnico
2. Frases CURTAS e impactantes
3. CADA slide termina com frase de gancho para o proximo
4. UM conceito por slide
5. Apos ponto, SEMPRE letra maiuscula
6. Escrever como se estivesse falando com uma pessoa so
7. Cada linha deve criar momentum

### GATILHOS PSICOLOGICOS A USAR

- Gap de curiosidade (curiosity gap)
- Pattern interrupt (quebrar padroes)
- Tom de prova social (social proof tone)
- Medo de perder algo (FOMO)
- Ideias contrarianas
- Recompensas rapidas (quick wins)
---

## PERFIL CONFIGURADO

### Dra. Daniely Freitas
- Nome: Dra. Daniely Freitas
- Handle: @dradaniely.freitas
- Verificado: sim (selo azul)
- CRM: BA 27588
- Visual na capa: blazer escuro, blusa preta, colar dourado, semblante serio
- Avatar: "Foto Perfil Daniely.png" (fundo transparente, frame dourado)
- Cor da marca: dourado #9F8844

### Fotos de referencia
- Fotos serias da Dra: `C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Banco de imagens\Dany\Ensaio Fotografico\Fotos\IA\`
- VPS fotos: `/root/.openclaw/workspace/fotos_dra/`
- Avatar oficial: `Foto Perfil Daniely.png`
- Logo/simbolo V: `C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Logo\`

---

## CAPAS JA APROVADAS (referencias exatas)

### Magnesio
- Headline: SEU MAGNESIO ESTA "NORMAL" MAS SEU CORPO DISCORDA.
- Destaques dourados: MAGNESIO, NORMAL, CORPO, DISCORDA
- Foto: dra_seria_frontal.png
- Fundo: tubos de sangue laboratoriais (Unsplash: blood test tubes rack laboratory)
- Circulo: capsulas douradas de magnesio

### Creatina
- Headline: UM DOS SUPLEMENTOS MAIS SUBESTIMADOS PARA O CEREBRO
- Destaques dourados: SUPLEMENTOS, SUBESTIMADOS, CEREBRO
- Foto: dra_seria_lateral.png
- Fundo: loja de suplementos escura (Unsplash: "three containers of protein powder" - CREATINE+PROTEIN+PRE-WORKOUT jars + shaker)
- BG cacheado em: /root/bg_creatina_approved.png
- Circulo: po de creatina

---

## SCRIPTS OFICIAIS (em /root/.openclaw/workspace/skills/tweet-carrossel/scripts/)

| Script | Funcao |
|--------|--------|
| `compose_cover.py` | Pipeline completo da capa (rembg + fundo + make_cover) |
| `make_cover.py` | Gerador de capa (Montserrat Black, simbolo V, JPEG) |
| `capture_pubmed.py` | Captura PubMed com cascata de 5 estrategias |
| `send_to_telegram.py` | Envia slides para o Telegram (grupo AI Vital Slim) |
| `gen_slides.py` | Gerador de slides tweet (HTML + Chromium -> JPEG) |

---

## CHECKLIST DE QUALIDADE (OBRIGATORIO antes de entregar)

### Copy (etapa 1)
- [ ] Headline da capa e de IMPACTO (scroll-stop)
- [ ] Texto conversacional, nao tecnico
- [ ] Frases curtas
- [ ] Gancho no final de cada slide
- [ ] Um conceito por slide
- [ ] Apos ponto, letra maiuscula


### Imagens (etapa 2)
- [ ] Proporcao 4:5 (1080x1350) em TODOS os slides
- [ ] Capa: foto REAL da Dra. (NAO gerada por IA)
- [ ] Capa: Dra. com semblante serio, blazer escuro, braços cruzados, cintura pra cima
- [ ] Capa: fundo contextual CLARAMENTE relacionado ao tema (nao generico, nao "loja de bebidas")
- [ ] Capa: headline em Montserrat Black, texto grande (max 150px, min 80px)
- [ ] Capa: texto alinhado ao TOPO da area (sem espaco vazio entre linha dourada e texto)
- [ ] Capa: TODAS as palavras-chave em dourado na mesma cor
- [ ] Slide 2: screenshot PubMed validado (header NIH azul, titulo, autores, PMID, DOI)
- [ ] Slide 2: SEM captcha "Select all images" ou "403 Forbidden"
- [ ] Slides tweet: avatar 96px (alinhado com nome 48px + handle 34px)
- [ ] Slides tweet: texto de cor unica #000000, 60px
- [ ] Slides tweet: avatar = "Foto Perfil Daniely.png" (com frame dourado, fundo transparente)
- [ ] Todos os slides: JPEG quality=85, < 200KB

### Entrega (etapa 3)
- [ ] Enviou via Telegram (NAO apenas salvou na VPS)
- [ ] Usou send_to_telegram.py com caption descritiva
- [ ] Chat_id -1003803476669, thread_id conforme tema

---

## TROUBLESHOOTING

- **Capa com rosto diferente da Dra.**: usar APENAS fotos reais em /root/.openclaw/workspace/fotos_dra/ (NUNCA gerar via IA)
- **Capa com fundo errado (loja de bebidas, etc.)**: trocar busca Unsplash para termos mais especificos (ex: "blood test tubes rack laboratory" em vez de "laboratory")
- **Capa com texto pequeno/espaço vazio**: verificar make_cover.py tem cap 150, TEXT_AREA_START=0.62, alinhamento TOPO
- **Capa com destaques em cores diferentes**: conferir TODAS as palavras-chave estao no `--destaques` separadas por virgula
- **Slide 2 com 403 Forbidden**: capture_pubmed.py deve ter validacao NIH blue >= 15% (impede falso-positivo)
- **Slide 2 com captcha**: capture_pubmed.py deve usar --incognito + perfil limpo por tentativa
- **Avatar desalinhado com nome**: avatar = 96px (match text block height ~90px)
- **Avatar com fundo branco visivel**: usar "Foto Perfil Daniely.png" (fundo transparente), NAO dra_avatar_real.png (tem padding)
- **Request too large (20MB)**: todas as imagens DEVEM ser JPEG quality=85 (slides e capa)
- **Clara entregou arquivos na VPS mas nao no Telegram**: SEMPRE rodar send_to_telegram.py depois de gerar
- **API key Gemini invalida/quota**: capture_pubmed.py tem cascata que nao depende de Gemini

---

## HISTORICO DE VERSOES

- **v4.0.0** (2026-04-17): Avatar "Foto Perfil Daniely.png" + fontes grandes + pipeline completo + Telegram obrigatorio
- **v3.0.0** (2026-04-14): compose_cover.py + capture_pubmed.py validando
- **v2.0.0** (2026-04-09): HTML templates para slides
- **v1.0.0**: Geracao basica via Pillow


## BUSCA DE POSTS DO INSTAGRAM (quando Tiaro envia URL)

Quando Tiaro enviar URL do Instagram pedindo carrossel, Clara DEVE usar o
fetch_instagram.py para extrair a caption REAL (Instagram nao e extraivel via
simple HTTP fetch):

```bash
python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/fetch_instagram.py   --url "<URL_INSTAGRAM>"   --out /tmp/post_caption.txt
```

O script usa RapidAPI (key salva em /root/cerebro-vital-slim/cerebro/areas/marketing/skills/instagram-api/SKILL.md):
- Primeira tentativa: instagram-scraper-stable-api (rapido, por URL)
- Fallback: instagram120 (pagina posts do perfil @institutovitalslim)

Apos obter a caption, Clara usa ela como input para ingest_content.py:

```bash
python3 /root/cerebro-vital-slim/cerebro/empresa/skills/memoria-cientifica/scripts/ingest_content.py   --file /tmp/post_caption.txt --topic "<topico>" --slug "<slug>"
```

