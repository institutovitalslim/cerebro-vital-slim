---
name: prompt-imagens
description: >
  OBRIGATORIO acionar para QUALQUER pedido de criacao de imagem (capa, post, ad, foto
  da Dra., etc.). Clara NUNCA gera imagem por conta propria — SEMPRE executa esta skill.
  Cria imagens via NanoBanana 2 Pro com 7 dimensoes + 15 estilos + biblioteca de 24 poses.
  SEMPRE pergunta com/sem referencia. Para imagens da Dra. Daniely: OBRIGATORIAMENTE
  usar generate_with_reference.py com foto REAL do acervo como referencia (nunca sem).
  Valida prompt com Tiaro antes de gerar.
  TRIGGERS (lista completa): "cria uma imagem", "cria imagem", "gera imagem", "gera foto",
  "faz uma foto", "foto da Dra", "imagem da Dra", "imagem para ad", "imagem para post",
  "imagem para carrossel", "capa", "foto para divulgacao", "arte", "crie", "gere",
  "gerar imagem", "criar imagem".
metadata:
  version: 1.1.0
  domain: marketing
  owner: main
---

# Prompt de Imagens — Criacao profissional via NanoBanana 2 Pro

## ⚠️ REGRAS ABSOLUTAS (LER ANTES DE QUALQUER COISA)

### 🚨 REGRA #0: ESTA SKILL EH O UNICO CAMINHO PARA IMAGENS
Clara NUNCA, EM HIPOTESE ALGUMA, gera imagens sem executar esta skill completamente.
NAO usar ferramentas nativas de image generation do gateway, NAO gerar "de cabeca",
NAO pular etapas.

**Se Clara receber pedido de imagem e gerar sem chamar `generate_image.py` ou
`generate_with_reference.py`, isso eh ERRO CRITICO — corrigir imediatamente
executando a skill corretamente.**

### 🚨 REGRA #1: IMAGEM DA DRA. DANIELY — SEMPRE COM REFERENCIA REAL

Se o pedido mencionar "Dra. Daniely", "Daniely", "a doutora", "a medica", Clara
OBRIGATORIAMENTE:

1. **Usa `generate_with_reference.py`** com uma foto REAL do acervo como referencia
   (NUNCA `generate_image.py` sem referencia — perde fisionomia)
2. **Seleciona a foto via `photo_selector.py`** com base no tema, OU manualmente escolhe
   do acervo `/root/.openclaw/workspace/fotos_dra/originais/`
3. **Preserva APENAS o rosto** — pose, roupa, cenario, angulo DEVEM variar conforme prompt
4. **Varia a pose** (consultar biblioteca de 24 poses da skill) — NAO repetir "bracos
   cruzados frontal" em carrosseis consecutivos

**Fotos reais da Dra. disponiveis:**
- `/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 1.png` a `Imagem PNG 29.png`
- `/root/.openclaw/workspace/fotos_dra/dra_seria_frontal.png`
- `/root/.openclaw/workspace/fotos_dra/dra_seria_lateral.png`

Sem referencia → fisionomia sera alterada → INACEITAVEL.

### 🚨 REGRA #2: NUNCA PULAR VALIDACAO COM TIARO

Clara SEMPRE envia o prompt completo ao Tiaro ANTES de gerar. Aguarda aprovacao.
Nao gerar direto — mesmo que o pedido pareca simples.

---

## FLUXO OBRIGATORIO (5 ETAPAS)

### ETAPA 1 — Pergunta inicial (SEMPRE)

Ao receber pedido de criacao de imagem, Clara PRIMEIRO pergunta:

> "Voce quer criar a imagem **SEM referencia** (modelo novo) ou **COM referencia**
>  (baseada em foto que voce vai enviar)?"

### ETAPA 2 — Coleta de contexto

**Se SEM referencia:**
- Tema/contexto da imagem
- Para onde vai (ad, post, carrossel capa, story)
- Estilo desejado (sugerir da lista de 15 estilos — ver secao abaixo)
- Pessoa/sujeito principal (generico ou descricao)

**Se COM referencia:**
- Clara PEDE: "Envie a foto de referencia que deseja usar como base"
- Tiaro envia a foto → Clara salva em `/tmp/` e anota o caminho
- Clara identifica o sujeito da foto
- Tema/cenario desejado para a NOVA imagem
- Para onde vai
- Estilo desejado

### ETAPA 2.5 — ANALISE ESTRATEGICA DE REFERENCIAS (4 PASSOS OBRIGATORIOS)

> "Voce nao precisa criar do zero. Aprenda a combinar referencias com intencao e proposito.
> A IA seguira suas instrucoes. Mostre antes de dizer."

Antes de montar o prompt, Clara executa o **Ciclo de Analise de Referencias**:

#### PASSO 1 — Identifique a intencao
Determinar claramente o tipo de imagem alvo:
- **Comercial** (vende produto/servico — foco em nitidez e aspiracional)
- **Editorial** (conta historia — foco em narrativa e estetica sofisticada)
- **Minimalista** (comunica com poucos elementos — foco em espaco negativo)
- **Documental** (registra realidade — foco em autenticidade)
- **Fine Art** (arte — foco em expressao e significado)
- **Tributo/Homenagem** (celebra pessoa — foco em reverencia)

Clara anota a intencao e usa ela para filtrar referencias e escolher o estilo (dimensao 6).

#### PASSO 2 — Crie um moodboard (3-5 referencias)
Buscar nos 3 sites de inspiracao:

1. **Visual Electric** — https://visualelectric.com/inspo
   Galeria com prompts visiveis. Melhor para estilos contemporaneos/experimentais.

2. **Pinterest BR** — https://br.pinterest.com/
   Buscar por `<tema> + prompt` (ex: "retrato editorial prompt"). Melhor para mood/composicao.

3. **Midjourney Explore** — https://www.midjourney.com/
   Galeria publica com prompts. Melhor para referencia tecnica profissional.

Reunir **3-5 imagens** que capturam a essencia do que deseja criar. Essa selecao
vira o moodboard da pesquisa.

Salvar em `/tmp/moodboard_<slug>/` quando possivel (para referencia futura).

#### PASSO 3 — Observe os detalhes (analise visual)
Para cada referencia do moodboard, Clara analisa:

| Dimensao | O que observar |
|----------|----------------|
| **Iluminacao** | Direcao (lateral, topo, traseira), qualidade (dura/suave), temperatura (quente/fria/neutra) |
| **Paleta de cores** | Tons dominantes, contrastes, paleta restrita (2-3 cores) ou rica |
| **Textura** | Lisa, granulada (filme), brilhante, fosca, realista |
| **Enquadramento** | Close-up, busto, meio-corpo, plano aberto, angulo (baixo/alto/normal) |
| **Narrativa** | Que historia a imagem conta? Que emocao transmite? |

Essas observacoes se traduzem nas dimensoes 4 (cenario), 5 (iluminacao) e 6 (estilo) do prompt.

#### PASSO 4 — Elabore o prompt
Combinar intencao + analise visual nas 7 dimensoes (proxima etapa).

**Regra de ouro**: "Mostre antes de dizer" — referenciar visualmente (fotografos,
filmes, revistas, camaras) eh mais eficaz que adjetivos vagos.

### PIRAMIDE DA CRIACAO (hierarquia de qualidade)

Da base (obrigatorio) ao topo (resultado):

```
                  ┌─────────────────────┐
                  │ CRIACAO EXCEPCIONAL │   ← Imagens que surpreendem
                  ├─────────────────────┤
              ┌───┤  PROMPTS EFICIENTES │   ← Instrucoes claras/detalhadas
              ├───┼─────────────────────┤
          ┌───┤   │   ANALISE VISUAL    │   ← Estudo das referencias
          ├───┼───┼─────────────────────┤
      ┌───┤   │   │  REFERENCIAS INSP.  │   ← Base visual (moodboard)
      └───┴───┴───┴─────────────────────┘
```

Cada camada depende da anterior. **Pular a base = qualidade ruim**. Se Clara tentar
gerar prompt sem moodboard, o resultado sera generico.

### EXEMPLOS PRATICOS DE USO (inspirados em referencias)

| Objetivo | Fonte da referencia | Prompt inspirado (trecho) |
|----------|---------------------|---------------------------|
| Retrato lifestyle | Pinterest Editorial | "natural light portrait, shallow depth of field, soft morning glow, 85mm f1.4, bokeh background" |
| Flat lay criativo | Visual Electric | "flat lay with pastel colors, overhead view, minimalist composition, soft shadows, commercial photography" |
| Produto premium | Galeria Midjourney | "perfume bottle on reflective surface, cinematic lighting, moody contrast, hero product shot, Hasselblad 100mm" |
| Tributo figura publica | Pinterest + Visual Electric | "dramatic portrait, cinematic grading, noir lighting, 35mm film, archival photo reinterpretation" |
| Medicamento/suplemento | Pinterest Commercial | "macro product shot, gradient background, soft rim light, Rx photography, clean commercial" |
| Paciente lifestyle | Pinterest Wellness | "candid documentary, window light, Kinfolk style, 35mm, earthy palette, natural" |

Clara consulta essa tabela para escolher ponto de partida dos prompts.

### FORMULA PARA PROMPTS EFICAZES (4 elementos fundamentais)

> "Para criar prompts que geram resultados extraordinarios, combine estes elementos
> essenciais de forma clara e detalhada. Quanto mais especifico e descritivo for cada
> elemento, melhor sera o resultado final da imagem."

#### 1. SUJEITO — Foco principal
Seja especifico sobre QUEM ou O QUE voce quer representar.
- ❌ Ruim: "gato"
- ✅ Bom: "um gato siames jovem"
- ❌ Ruim: "medica"
- ✅ Bom: "Dra. Daniely Freitas, medica especialista em emagrecimento, 40 anos"

#### 2. APARENCIA — Detalhes fisicos e visuais
Inclua cores, texturas, materiais e caracteristicas distintivas. Especifique o estilo
artistico desejado.
- ❌ Ruim: "blusa bonita"
- ✅ Bom: "blazer de la merino bege, botoes cobertos, alfaiataria estruturada italiana"

#### 3. ACAO — Movimento e interacao
Descreva poses, expressoes e movimentos. Seja especifico sobre a interacao com o
ambiente e outros elementos da cena.
- ❌ Ruim: "ela esta la"
- ✅ Bom: "ela esta parada, levemente virada de lado, olhando para a camera com um
  sorriso sutil, mao direita descansando no bolso do blazer"

#### 4. CENARIO — Ambiente e contexto
Defina o local, hora do dia, condicoes climaticas e elementos que ajudam a contar a
historia.
- ❌ Ruim: "na rua"
- ✅ Bom: "rua movimentada de grande cidade apos chuva, letreiros de neon rosa/azul
  refletindo no asfalto molhado, pedestres desfocados ao fundo, final de tarde 19h"

---

### ELEMENTOS ESSENCIAIS (3 pilares da qualidade tecnica)

Alem das 7 dimensoes basicas, prestar atencao extra em:

#### 📷 ILUMINACAO (dimensao 5)
Define o tom e atmosfera da imagem — cria profundidade e emocao. Uma boa descricao de
iluminacao transforma uma imagem comum em obra extraordinaria.

**Termos-chave (usar com contexto):**
- "iluminacao suave" / "soft lighting" — atmosfera delicada
- "luz dramatica" / "dramatic lighting" — contraste forte, sombras profundas
- "luz natural" / "natural light" — realista, documental
- "golden hour" — dourada, quente (final de tarde)
- "blue hour" — azulada, fria (pos-por do sol)
- "rim light" / "contraluz" — silhueta iluminada nas bordas
- "key light lateral 45deg" — iluminacao classica de estudio
- "overcast sky" — luz difusa, sem sombras marcadas
- "tungsten 3200K" vs "daylight 5500K" — temperatura de cor

#### 🎨 ESTILO (dimensao 6)
Determina a estetica geral — de realismo fotografico a arte conceitual. O estilo
influencia diretamente como a IA interpreta o prompt.

**Especificar:**
- Estilos artisticos (ex: "editorial moderno", "minimalismo japones")
- Periodos historicos (ex: "estetica anos 80 neon", "romantismo vitoriano")
- Tecnicas de renderizacao (ex: "ray tracing", "render fotorrealista", "ilustracao 2D")
- Movimentos (ex: "cyberpunk", "nordic minimalism", "cottagecore")
- Referencia a fotografos/artistas ("no estilo de Irving Penn", "estetica Annie Leibovitz")

#### ✨ QUALIDADE (garante nitidez e detalhes)
Palavras-chave de qualidade sao a diferenca entre mediano e excepcional:

- "alta resolucao" / "high resolution"
- "detalhado" / "highly detailed"
- "4K" / "8K"
- "ultra detalhado" / "ultra detailed"
- "renderizacao fotorrealista" / "photorealistic rendering"
- "hiperdetalhado" / "hyperdetailed"
- "sharp focus" / "foco nitido"
- "masterpiece" / "obra-prima"

**Regra:** incluir 2-3 termos de qualidade ao final da dimensao 6 ou 7. Nao empilhar
dezenas de qualifiers — perde efeito.

---

### TECNICAS DE REFINAMENTO DE PROMPT

#### 1. Use adjetivos especificos (nao vagos)

| Vago (ruim) | Especifico (bom) |
|-------------|------------------|
| bonito | expressao radiante |
| azul | cerulean / cobalto / indigo |
| antigo | vintage dos anos 80 / retro analogico anos 70 |
| grande | imponente / monumental / descomunal |
| foto bonita | close-up frontal com iluminacao lateral suave |
| lugar bacana | laboratorio clinico brutalist com janelas altas |

#### 2. Evite ambiguidades
Seja claro sobre:
- **Angulo da camera** (frontal, 3/4, perfil, contra-plongee, plongee)
- **Distancia** (close-up, medio, plano geral, plano de detalhe)
- **Iluminacao** (direcao + qualidade + temperatura)
- **Posicao do sujeito** (centrado, regra dos tercos, deslocado a direita)

#### 3. Experimente formatos (iteracao)
Se o primeiro resultado nao agradar, Clara sugere:
- Reordenar elementos do prompt (IA da mais peso ao inicio)
- Aumentar/reduzir nivel de detalhe
- Testar versoes com e sem termos tecnicos
- Comparar 2-3 variacoes do mesmo conceito

#### 4. Inclua referencias artisticas
- "no estilo de Van Gogh" / "no estilo de Peter Lindbergh"
- "arte digital minimalista japonesa" / "editorial Vogue dos anos 90"
- "fotografia Magnum" / "revista Kinfolk"
- Citar filmes: "estetica de Blade Runner 2049" / "paleta de Wes Anderson"

#### 5. Defina parametros tecnicos
- Resolucao: "alta resolucao", "8K", "ultra detalhado"
- Proporcao: "4:5 portrait", "16:9 cinematic"
- Qualidade: "renderizacao fotorrealista", "cinematic grade", "clean commercial"

---

### A CHAVE PARA PROMPTS PODEROSOS (4 principios)

1. **Pratica** — experimente diferentes abordagens e refine
2. **Detalhamento** — seja especifico e inclua elementos visuais importantes
3. **Clareza** — evite ambiguidades e termos vagos
4. **Experimentacao** — teste diferentes estilos e tecnicas

---

### CAMERAS DE ALTA QUALIDADE (referencias tecnicas profissionais)

#### 🎥 Canon R5 Mark II
Uma das melhores cameras da atualidade.
- **Fotos**: 45 MP com extrema qualidade e nitidez
- **Video**: 8K ate 60fps
- **Preco referencia**: ~R$ 35.000

**Destaques tecnicos:**
- Sensor CMOS full-frame
- Sistema de AF dual pixel CMOS com 1.053 pontos
- ISO nativo de 100-51.200
- Estabilizacao de imagem de 8 stops

**Ideal para**: fotografia profissional, casamentos, eventos e filmagens comerciais
de alta qualidade.

**Quando usar no prompt:** retratos profissionais, autoridade medica, editorial
de alta producao.

#### 🎥 Sony Alpha A7R V
Outra excelente camera. Fotos de 60 MP com extrema qualidade e grava em 8K. Mesmo
valor medio da Canon.

**Especificacoes principais:**
- Sensor CMOS full-frame de 61 MP
- Processador BIONZ XR
- 759 pontos de AF com deteccao de fase
- Gravacao 8K/24p e 4K/60p

**Ideal para**: fotografia de paisagem, arquitetura e trabalhos que exigem alta resolucao.

**Quando usar no prompt:** cenarios amplos, arquitetura clinica, paisagens, close-ups
de produto ultra-detalhados.

---

### LENTES E ACESSORIOS (profissional)

Lentes com abertura entre **f/1.2 e f/2.8** proporcionam **desfoque suave e agradavel**,
criando profundidade de campo que valoriza o sujeito.

#### Recomendacoes de lentes por uso:

| Lente | Uso principal | Exemplo de prompt |
|-------|--------------|-------------------|
| **50mm f/1.2** | Retrato classico, baixa luz | "Portrait shot with 50mm f/1.2, shallow DOF, creamy bokeh" |
| **85mm f/1.2** | Retrato autoridade, compressao flattering | "Head-and-shoulders portrait, 85mm f/1.2, dreamy bokeh" |
| **24-70mm f/2.8** | Versatil para eventos | "Documentary coverage, 24-70mm f/2.8 zoom range" |
| **70-200mm f/2.8** | Esportes, wildlife, close distante | "Telephoto sports action, 70-200mm f/2.8, frozen motion" |
| **16-35mm f/2.8** | Paisagem, arquitetura, interiores | "Architecture wide shot, 16-35mm f/2.8, leading lines" |
| **100mm f/2.8 Macro** | Close-up de produto, detalhe | "Macro product shot, 100mm f/2.8, extreme detail" |

#### Acessorios essenciais (mencionar no prompt quando relevante):

- **Filtros ND** (densidade neutra): longa exposicao, agua sedosa, nuvens em movimento
- **Polarizadores**: ceus mais saturados, reduz reflexos, verdes mais vivos
- **Flash externo**: rim light, fill light, iluminacao lateral criativa
- **Softbox/beauty dish**: retratos com iluminacao suave e lisonjeira
- **Tripe**: exposicao longa, paisagens, arquitetura precisa

---

### TIPOS DE LENTES POR DISTANCIA FOCAL

Entender distancia focal eh fundamental para escolher a lente correta:

#### 📐 Grande-angular (10-24mm)
- **Efeito**: campo de visao amplo, exagera profundidade
- **Uso**: paisagens, arquitetura, interiores apertados, cenas extensas em unico quadro
- **Prompt**: "wide-angle lens 16-24mm, expansive landscape, depth enhanced"
- **Atencao**: distorce rostos em close — evitar para retratos

#### 📐 Padrao (35-85mm)
- **Efeito**: perspectiva natural (proxima ao olho humano 50mm)
- **Uso**: retratos, fotografia documental, lifestyle
- **Prompt**: "natural perspective, 50mm lens, human-eye view"
- **Sub-ranges**:
  - 35mm: documental, street, ambiente
  - 50mm: retrato classico, rua, lifestyle
  - 85mm: retrato fechado, bokeh pronunciado

#### 📐 Teleobjetiva (100-400mm)
- **Efeito**: aproxima objetos distantes, comprime perspectiva, fundo desfocado extremo
- **Uso**: retratos com fundo desfocado, esportes, wildlife
- **Prompt**: "telephoto 200mm, compressed background, subject isolation, extreme bokeh"
- **Sub-ranges**:
  - 70-135mm: retrato profissional fashion
  - 200mm: esportes, detalhe distante
  - 400mm+: wildlife, fotografia de natureza

---

### ANGULOS DE CAMERA E TIPOS DE TOMADA

A escolha do angulo muda totalmente a mensagem emocional da imagem.

#### 👁 Tomada ao Nivel dos Olhos (eye-level)
- **Efeito**: neutro, realista, criando conexao com o espectador
- **Uso**: retratos, entrevistas, conteudo educacional, autoridade acessivel
- **Exemplo de prompt**:
> "A stunning portrait shot at eye level, captured with a Sony Alpha a7 III and a
> Sony FE 24-105mm f/4 G OSS lens, ultra-detailed, cinematic lighting"

#### ⬆️ Tomada de Baixo Angulo (low-angle / contra-plongee)
- **Efeito**: transmite poder, imponencia, dramaticidade; sujeito parece maior
- **Uso**: herois, autoridade forte, arquitetura monumental, produtos premium
- **Exemplo de prompt**:
> "A heroic warrior standing tall, low-angle shot, taken with a Sony Alpha a7 III
> and a Sony FE 16-35mm f/2.8 GM lens, cinematic shadows, dynamic lighting"

#### ⬇️ Tomada de Alto Angulo (high-angle / plongee)
- **Efeito**: sugere pequenez, vulnerabilidade, controle sobre o sujeito
- **Uso**: cenas emocionais de fragilidade, crianca, pacientes em situacao delicada
- **Prompt**: "high-angle shot from above, subject feels small, contemplative mood"

#### 🦅 Tomada Aerea (aerial / bird's eye view)
- **Efeito**: perspectiva impossivel, reveladora de contexto
- **Uso**: paisagens, revelacao de escala, dinamica de grupo vista de cima
- **Exemplo de prompt**:
> "A breathtaking aerial view of the Grand Canyon at sunset, taken with a DJI
> Phantom 4 Pro, golden hour, epic composition"

#### 📏 Angulos auxiliares (usar conforme necessidade)

| Angulo | Efeito | Uso tipico |
|--------|--------|------------|
| Dutch angle (inclinado) | Tensao, desequilibrio | Cenas de ansiedade, acao intensa |
| Over-the-shoulder | Perspectiva subjetiva | Dialogos, pov |
| Worm's eye view (vertical baixo) | Monumentalidade extrema | Arvores, arranha-ceus |
| Three-quarter (3/4) | Natural e sofisticado | Retrato lifestyle e editorial |
| Profile (perfil) | Elegancia, contorno | Retrato artistico, silhueta |

---

### ILUMINACAO E ATMOSFERA (condicoes naturais)

A condicao climatica altera dramaticamente a atmosfera da imagem:

#### ☀️ Ensolarado (sunny / clear sky)
- **Caracteristicas**: cores vibrantes, contraste forte, sombras definidas
- **Uso**: lifestyle ativo, energia, otimismo, produtos coloridos
- **Prompt**: "bright sunny day, vibrant colors, strong contrast, crisp shadows,
  sunlight from [direcao]"

#### ☁️ Nublado (overcast / cloudy)
- **Caracteristicas**: suaviza sombras, tons frios e atmosfericos, luz difusa natural
- **Uso**: retrato uniforme, lifestyle autentico, documental, fashion
- **Prompt**: "overcast sky, soft diffused light, cool tones, moody atmosphere,
  no harsh shadows"
- **Vantagem**: iluminacao mais flattering para pele (sem sombras duras)

#### 🌃 Noite (night / low light)
- **Caracteristicas**: ambientes escuros, luzes artificiais (neon, tungstenio, LED),
  alto contraste
- **Uso**: cyberpunk, urbano moderno, drama, intimidade, noir
- **Prompt**: "night scene, artificial lighting, neon glow, high contrast, ISO 3200
  for grain atmosphere"

#### 🌅 Golden Hour (hora dourada)
- **Caracteristicas**: luz quente, baixa no ceu (~1h apos nascer / antes do por)
- **Uso**: lifestyle aspiracional, natureza, romantico, aquecido
- **Prompt**: "golden hour, warm amber light, long shadows, backlit subject,
  lens flare suggestion"

#### 🌆 Blue Hour (hora azul)
- **Caracteristicas**: tons azulados profundos, logo apos por-do-sol ou antes de nascer
- **Uso**: urbano melancolico, arquitetura, reflexivo
- **Prompt**: "blue hour, deep cobalt sky, ambient artificial lights starting to glow,
  cinematic quiet mood"

#### 🌧️ Chuvoso (rainy)
- **Caracteristicas**: reflexos, superficies molhadas, atmosfera densa
- **Uso**: street photography, neon refletido, melancolia, Blade Runner
- **Prompt**: "post-rain, wet reflective asphalt, neon reflections, misty atmosphere,
  moody street"

#### 🌫️ Nebuloso (foggy / misty)
- **Caracteristicas**: profundidade reduzida, atmosfera etereal, isolamento
- **Uso**: fine art, natureza, horror sutil, fantasia
- **Prompt**: "foggy landscape, atmospheric depth, low visibility, dreamy ethereal
  mood, diffused ambient light"

---

### HORA DO DIA E ESTILO DE CENA

A hora do dia altera dramaticamente a atmosfera. Escolher a hora eh parte da narrativa
visual do prompt.

#### 1. 🌅 Hora Dourada (Golden Hour)
- **Caracteristicas**: luz quente, tons dourados, sombras suaves e alongadas
- **Horario**: ~1h apos o nascer do sol ou antes do por
- **Prompt**: "golden hour lighting, warm amber tones, long soft shadows, sun low on
  horizon, magic-hour cinematic atmosphere"
- **Uso IVS**: aspiracional, conquista, jornada do paciente, lifestyle premium

#### 2. 🌇 Por do Sol (Sunset)
- **Caracteristicas**: cores vibrantes (laranja/rosa/roxo), silhuetas marcantes,
  contraluz dramatico
- **Prompt**: "sunset sky, vibrant orange and pink gradient, strong silhouette,
  dramatic backlight, rim light on subject"
- **Uso IVS**: reflexao, ponto de virada, transformacao, narrativa emocional

#### 3. 🌃 Noite
- **Caracteristicas**: ambientes escuros, luzes artificiais (neon, tungstenio, LED),
  alto contraste
- **Prompt**: "night scene, artificial neon lighting, deep shadows, high contrast,
  cinematic moody atmosphere"
- **Uso IVS**: conteudo urbano/moderno, cyberpunk, alerta/drama

#### 4. 🌄 Nascer do Sol (Sunrise) [expansao]
- **Caracteristicas**: luz fria suave, bruma baixa, ceu pastel
- **Prompt**: "early sunrise, soft cool light, low mist, pastel sky, peaceful atmosphere"
- **Uso IVS**: recomeco, despertar, rotina saudavel, bem-estar matinal

#### 5. 🌆 Blue Hour (Hora Azul) [expansao]
- **Caracteristicas**: tons azulados profundos, luzes urbanas comecam a brilhar
- **Prompt**: "blue hour, deep cobalt sky, first city lights glowing, transitional mood"
- **Uso IVS**: urbano sofisticado, clinica moderna noturna, arquitetura

#### 6. ☀️ Meio-dia (Midday)
- **Caracteristicas**: sombras duras verticais, contraste extremo, alta luminosidade
- **Prompt**: "midday harsh light, hard vertical shadows, high contrast, bleached highlights"
- **Uso IVS**: pouco usado em retrato (pouco lisonjeiro), bom para produto ou street
- **Atencao**: normalmente evitar para retrato de Dra. (pouco flattering)

---

### ESTILOS E GENEROS FOTOGRAFICOS ESPECIFICOS

Alem dos 15 estilos principais (catalogo acima), estes generos tematicos ampliam as
possibilidades criativas:

#### ✨ Fantasia
- **Elementos**: florestas encantadas, luzes magicas, atmosfera etereal, particulas
  flutuantes (pollen, faiscas), nebulas de luz colorida
- **Prompt**: "enchanted forest, magical glowing light, ethereal atmosphere, floating
  particles, soft bokeh, dreamlike fantasy"
- **Uso IVS**: posts conceituais (transformacao do corpo, jornada interior),
  brainstorm criativo
- **Estilo artistico relacionado**: Fine Art + efeitos magicos

#### 🕷️ Terror / Horror
- **Elementos**: mansoes abandonadas, iluminacao sinistra, sombras contrastantes,
  contraluz, paleta dessaturada com accent vermelho
- **Prompt**: "abandoned mansion, sinister lighting, stark contrasting shadows,
  desaturated palette with blood-red accents, horror atmosphere"
- **Uso IVS**: POUCO adequado para clinica de saude — evitar exceto campanha pontual
  de alerta forte (ex: "os perigos de X")
- **Atencao**: usar apenas se Tiaro pedir explicitamente esse tom

#### 📰 Documentario / Fotojornalismo
- **Elementos**: estilo realista, cenas de rua, protestos, cotidiano cru, sem pose
- **Prompt**: "documentary photojournalism style, real street scene, unposed candid
  moment, raw and authentic, Magnum Photos aesthetic"
- **Uso IVS**: historias reais de pacientes, dia-a-dia na clinica, conteudo autentico
- **Relacionado**: estilo 6 (Documental) + Street Photography (estilo 4)

#### 🎭 Outros generos tematicos

| Genero | Elementos-chave | Uso tipico IVS |
|--------|-----------------|----------------|
| **Sci-Fi / Futurista** | Superficies metalicas, holografia, neon, laboratorios avancados | Tecnologia medica, inovacao |
| **Film Noir** | B&W alto contraste, chuva, fumaca, detetive | Alerta dramatico (pouco uso) |
| **Western / Faroeste** | Poeira, luz dourada, paisagem arida, madeira | Quase nunca (nao se aplica) |
| **Lifestyle Scandinavian** | Minimalismo nordico, luz fria, madeira clara, neutros | Wellness premium, autocuidado |
| **Maximalism** | Cores saturadas, camadas, texturas ricas, opulencia | Raro — evitar pela regra menos-eh-mais |
| **Analog Film** | Grao Kodak/Fuji, leaks de luz, imperfeicoes | Nostalgia, autenticidade |
| **Surrealismo** | Juxtaposicoes impossiveis, ilusoes opticas, oneirismo | Posts conceituais criativos |
| **Abstract** | Sem forma reconhecivel, cores/formas | Background, banners |

Ao usar genero, citar referencia concreta: "estilo documentario tipo National
Geographic" eh melhor que so "documentario".

---

### CICLO DE APERFEICOAMENTO (Proximos Passos)

Criar prompts excepcionais eh um processo iterativo. Clara deve aplicar este ciclo
de 3 etapas em CADA projeto:

#### 1. 🔨 PRATIQUE
- Experimente diferentes combinacoes de **cameras + lentes + angulos**
- Teste variacoes de iluminacao (hora do dia, direcao, qualidade)
- Varie o estilo entre 2-3 candidatos antes de commit
- Nao aceite o primeiro prompt como definitivo — gere 2-3 variacoes e compare

**Na pratica**: ao apresentar ao Tiaro, Clara pode oferecer 2 versoes do prompt
(ex: "Versao A mais editorial, Versao B mais cinematografico — qual prefere?")

#### 2. 🔍 ANALISE
- Compare os **resultados** das variacoes geradas
- Ajuste os prompts com base em:
  - O que funcionou (manter)
  - O que nao funcionou (remover/substituir)
  - O que faltou (adicionar)
- Documente padroes: "prompts com '85mm f/1.2' geram bokeh mais suave que '50mm f/1.4'
  para a Dra."

**Na pratica**: apos gerar imagem, Clara faz mini-analise antes de entregar:
"Observei que X elemento ficou melhor assim, Y poderia ser ajustado se voce quiser"

#### 3. ✨ APERFEICOE
- Refine a tecnica iterativamente
- Manter um **aprendizado acumulado** (adicionar em `/root/cerebro-vital-slim/cerebro/empresa/conhecimento/prompts-aprendizados.md`)
- A cada novo projeto, consultar os aprendizados anteriores

**Aprendizados documentados** devem incluir:
- Combinacoes que funcionaram muito bem (camera+lente+angulo+luz)
- Estilos que renderizaram melhor no NanoBanana 2 Pro
- Termos em ingles vs portugues (geralmente ingles funciona melhor para termos tecnicos)
- Resolucao/proporcao ideais para cada uso

**Mantra**: "refine sua tecnica para obter imagens cada vez mais precisas"

---

### A IMPORTANCIA DAS REFERENCIAS FOTOGRAFICAS

**Por que sao essenciais:**

1. **Detalhamento tecnico** — quanto mais detalhado o prompt, mais proximo do resultado desejado
2. **Uso profissional** — fotografos e artistas usam para conceitos visuais
3. **Reconhecimento de IA** — o modelo reconhece descricoes de **cameras, lentes e angulos**

**Clara DEVE sempre incluir (dimensao 7):**

| Marca | Modelos tipicos |
|-------|-----------------|
| Canon | R5 Mark II, R6 Mark II, 5D Mark IV |
| Sony | A7R V, A1, A7 IV |
| Fujifilm | X-T5, X100VI, GFX 100S |
| Leica | Q3, M11, SL3 |
| Hasselblad | X2D 100C, H6D |
| ARRI | Alexa Mini LF, Alexa 35 |
| Nikon | Z9, Z8, D850 |

**Lentes:**
- Retrato: 85mm f1.4 / 50mm f1.2 / 135mm f1.8
- Lifestyle: 35mm f1.4 / 24-70mm f2.8
- Macro: 100mm f2.8 macro
- Wide: 24mm f1.4
- Cinematica: anamorfica 40mm / 50mm

**Angulos tecnicos:**
- "eye-level" (nivel dos olhos)
- "low angle" (contra-plongee, sujeito parece mais imponente)
- "high angle" (plongee, sujeito parece mais vulneravel)
- "Dutch angle" (inclinado, tensao)
- "bird's eye view" (vertical de cima)
- "worm's eye view" (vertical de baixo)

**Ao usar modelo/lente/angulo**, Clara deixa claro ao Tiaro porque escolheu (ex: "usei
85mm f1.4 porque da bokeh suave ideal para retratos de autoridade").

---

### COMO APRESENTAR AO TIARO

Junto com o prompt montado, Clara inclui SEMPRE nessa ordem:

1. **Intencao identificada** (ex: "Intencao: editorial, tom autoritario")
2. **Analise do contexto** (se houver foto de referencia, o que Clara observou)
3. **Moodboard**: 1-3 links/descricoes das referencias consultadas
4. **Analise visual consolidada**: "Peguei a iluminacao lateral do ref 1,
   a paleta terrosa do ref 2, e o enquadramento do ref 3"
5. **Sugestoes proativas** (da ETAPA 2.7): 3 opcoes para camera, iluminacao, angulo,
   estilo e atmosfera — com recomendacao marcada e justificativa
6. **Prompt completo** (baseado na combinacao recomendada) nas 7 dimensoes
7. **Pergunta de validacao dupla**:
   - "Posso gerar com este prompt?"
   - "OU quer mudar alguma das sugestoes (camera/luz/angulo/estilo)?"

### BIBLIOTECA DE POSES / ACOES PARA A DRA. DANIELY

**IMPORTANTE**: ao gerar COM REFERENCIA, Clara deve VARIAR a pose. Preservar APENAS o
rosto, NUNCA a pose da foto de referencia. Usar uma das poses abaixo conforme o tema.

#### Poses de AUTORIDADE (consultas, capas cientificas)

1. **Em pe, bracos cruzados, olhar frontal** (CLASSICO — usar com moderacao, evitar
   repetir em carrosseis consecutivos)
2. **Sentada atras da mesa, maos cruzadas sobre ela** — autoridade acessivel
3. **Em pe, maos nos bolsos do blazer, leve sorriso** — confianca moderna
4. **Apontando para uma tela/monitor com grafico** — autoridade didatica
5. **Segurando prontuario aberto, olhando para camera** — autoridade clinica
6. **Sentada, pernas cruzadas, apoio de queixo nas maos unidas** — reflexiva

#### Poses de ACOLHIMENTO (posts sobre pacientes, historias humanas)

7. **Conversando com paciente (foco na Dra., paciente de costas)** — acolhimento
8. **Mao no ombro do paciente em gesto reconfortante** — empatia
9. **Sorriso genuino, leve inclinacao de cabeca** — receptividade
10. **Apoiada em balcao, expressao descontraida** — proximidade
11. **Apontando para tablet/folha mostrando resultado** — explicacao pedagogica

#### Poses de MOVIMENTO/AÇÃO (lifestyle, ads dinamicos)

12. **Caminhando pelo corredor do consultorio** — dinamismo profissional
13. **Entrando no consultorio, abrindo porta** — acolhida
14. **Segurando medicamento/suplemento, examinando com curiosidade** — analise
15. **Escrevendo prescricao, foco nas maos + rosto em semi-perfil** — trabalho
16. **Operando microscopio/equipamento** — cientificidade

#### Poses de PRODUTO/SUPLEMENTO (ads, apresentacao)

17. **Segurando o produto em primeiro plano, rosto como fundo desfocado** — foco produto
18. **Apontando para o produto na prateleira** — recomendacao
19. **Entregando o produto ao paciente, sorriso confiante** — prescricao
20. **Segurando caneta injetora (retatrutide/ozempic)** — medicacao especifica

#### Poses para TRIBUTO/REFLEXIVA (posts conceituais, datas comemorativas)

21. **Perfil lateral, olhar para janela** — reflexao
22. **Cruzada de bracos mas virada de lado, olhando a distancia** — contemplacao
23. **Caminhando ao por do sol no consultorio (janela dourada)** — jornada
24. **Retrato fechado, foco apenas no rosto em iluminacao cinema** — drama

#### Como sugerir ao Tiaro:

Ao propor opcoes de pose (dentro da ETAPA 2.7), Clara cita 3 alternativas VARIADAS:

```
🧍 POSE (evitei repetir as ultimas ja usadas — ver usage.json):
  A) [pose 5] Segurando prontuario aberto, olhar frontal → autoridade clinica
     (RECOMENDADO para tema cientifico sobre [X])
  B) [pose 12] Caminhando pelo corredor → dinamismo profissional
  C) [pose 14] Segurando medicamento, examinando → analise critica
```

**Regras:**
- Consultar `usage.json` do photo_selector para nao repetir poses usadas recentemente
- Se Tiaro pediu "imagem diferente da ultima", OBRIGATORIAMENTE mudar a pose
- Evitar pose 1 (bracos cruzados frontal) quando ja foi usada em carrosseis recentes

---

### ETAPA 2.7 — SUGESTOES PROATIVAS (OBRIGATORIA)

Apos analisar a referencia/contexto (se houver) e o tema, ANTES de montar o prompt,
Clara DEVE propor ativamente sugestoes tecnicas ao Tiaro com **3 opcoes** para cada
dimensao critica e suas **justificativas**.

**NAO apenas perguntar "o que voce quer"**. Clara eh especialista — ela analisa o
contexto e recomenda, explicando o porque.

#### Quando com REFERENCIA de foto:
Clara observa a foto enviada e analisa:
1. **Qualidade tecnica original** (iluminacao, angulo, enquadramento, qualidade do rosto)
2. **Limitacoes do arquivo** (resolucao, cortes, angulo ruim para o uso proposto)
3. **Potencial de preservacao** (a foto tem o mood certo? precisa retoque?)
4. **Gaps entre foto atual e objetivo** (ex: foto clara demais para capa noturna)

Com base nisso, propoe ajustes/variacoes.

#### Template de apresentacao de sugestoes:

```
Analisei o contexto [+ a foto de referencia] e tenho as seguintes sugestoes
para criar a melhor imagem possivel:

📷 CAMERA (escolha uma):
  A) Canon R5 Mark II + 85mm f/1.4 → look editorial autoritario (RECOMENDADO
     para capa de autoridade medica)
  B) Sony A7R V + 50mm f/1.2 → look lifestyle mais natural
  C) Hasselblad X2D + 80mm f/1.9 → look fashion premium (alto impacto)

💡 ILUMINACAO (escolha uma):
  A) Luz lateral suave 3200K + rim light dourado → autoridade calorosa (RECOMENDADO
     para tema medico acolhedor)
  B) Soft box frontal grande + fill discreto → editorial clean limpo
  C) Chiaroscuro dramatico 45 graus → impacto visual forte (para titulos fortes)

📐 ANGULO:
  A) Eye-level frontal → conexao direta com espectador (RECOMENDADO para tema
     [X] pois gera confianca)
  B) Low-angle 15deg → autoridade, imponencia (bom para alerta/decisao)
  C) 3/4 lateral → elegancia editorial

🎨 ESTILO:
  A) Editorial contemporaneo → credibilidade medica (RECOMENDADO)
  B) Cinematografico → impacto emocional
  C) Fine Art → reflexivo/poetico

🌅 HORA/ATMOSFERA (se cenario externo):
  A) Golden hour → aspiracional, quente
  B) Overcast difuso → profissional neutro (RECOMENDADO para medico)
  C) Blue hour → moderno sofisticado

Minha recomendacao combinada: [A+A+A+A+B] porque [justificativa contextual].

Voce quer seguir minha recomendacao, escolher outra combinacao, ou quer que eu
proponha variacoes para um elemento especifico?
```

#### Com REFERENCIA, tambem sugerir:

- **Melhorias da foto original**: "a foto esta com shadow forte no lado direito do
  rosto — posso compensar com fill light artificial no prompt"
- **Adaptacao para uso pretendido**: "a foto eh horizontal mas a capa eh 4:5, entao
  vou sugerir reenquadramento que preserve rosto centralizado"
- **Contexto faltante**: "a foto original tem fundo preto simples — para combinar
  com o tema [X], sugiro gerar cenario [Y] como substituicao"
- **Preservacao vs reinterpretacao**: "pela foto, vejo que rosto eh o ativo principal —
  recomendo Caminho A (add_overlay) para preservar 100%. Se quiser reinterpretacao
  artistica do cenario, Caminho B."

#### Quando SEM referencia:

Clara propoe sugestoes apenas com base no **tema + uso pretendido**:

```
Para o tema [X] em [uso pretendido], sugiro:

📷 CAMERA: [A/B/C com justificativa]
💡 ILUMINACAO: [A/B/C]
📐 ANGULO: [A/B/C]
🎨 ESTILO: [A/B/C]
🌅 ATMOSFERA: [A/B/C]

Minha recomendacao combinada: [...] porque [...]
```

#### Princípios para boas sugestoes:

1. **Sempre 3 opcoes** (nao 2, nao 5) — o cerebro escolhe melhor entre 3
2. **UMA das 3 marcada como RECOMENDADO** — Clara toma posicao, nao eh neutra
3. **Justificativa curta** (1 linha) ligando escolha ao contexto/objetivo
4. **Jargao tecnico + traducao de efeito** (ex: "85mm f/1.4 → bokeh suave ideal
   para autoridade")
5. **Combinacao sugerida no final** — Clara monta a melhor combinacao e explica
6. **Liberdade do Tiaro** — pergunta se ele quer seguir, mudar ou explorar variacoes

---

### ETAPA 3 — Construcao do prompt (7 DIMENSOES)

Clara constroi o prompt EXATAMENTE nessa estrutura, cada dimensao em um paragrafo:

```
1. SUJEITO: [elemento principal - quem/o que eh]

2. APARENCIA: [caracteristicas fisicas detalhadas - cabelo, pele, roupa, acessorios]

3. ACAO: [movimento ou postura - o que esta fazendo]

4. CENARIO: [ambiente e contexto - onde acontece, com detalhes tangiveis]

5. ILUMINACAO: [qualidade + direcao + temperatura da luz]

6. ESTILO: [estetica visual - escolher da lista de 15 estilos]

7. CAMERA/LENTE: [especificacoes tecnicas fotograficas]
```

**REGRAS DE CONSTRUCAO:**
- Detalhes especificos, nao adjetivos vagos
- Iluminacao DEVE indicar direcao + qualidade + temperatura (ex: "luz lateral suave,
  dourada de final de tarde, ~3200K, contraste moderado")
- Cenario deve criar atmosfera com elementos tangiveis (ex: "chao molhado refletindo
  neons rosa/azul") NAO "lugar bonito"
- Estilo deve referenciar tradicao visual concreta (ex: "editorial tipo Vogue",
  "Kodak Portra 400", "filmes A24")

**QUANDO COM REFERENCIA — CLAUSULA OBRIGATORIA:**

No final do prompt, incluir:

> "PRESERVACAO DE IDENTIDADE (OBRIGATORIO): Preserve 100% o rosto, estrutura facial,
>  tracos, cor e corte de cabelo, cor dos olhos e aparencia geral da pessoa na imagem
>  de referencia anexa. Ela deve ser CLARAMENTE reconhecivel como a mesma pessoa.
>  Modifique apenas cenario, iluminacao, vestimenta (se pedido) e pose."

**SOBRE FIGURAS PUBLICAS / TRIBUTOS / HOMENAGENS (importante!):**

Clara NAO deve recusar quando Tiaro envia foto de pessoa publica (atleta, artista,
personalidade historica) pedindo peca com texto/frase inspiracional. Esse eh um uso
LEGITIMO de design editorial/tributo, comum em marketing e redes sociais.

**DOIS CAMINHOS - escolher conforme o pedido:**

### Caminho A — MANTER FISIONOMIA 100% REAL (overlay sobre foto original)

**Quando usar:**
- Tiaro pede explicitamente "mantenha a fisionomia real", "mesma foto", "preserve o rosto"
- Tributo/homenagem a figura publica historica (Ayrton Senna, Chico Xavier, etc.)
- Card motivacional com foto real de paciente/pessoa
- Qualquer cenario onde a pessoa da foto deve ficar INTACTA

**Como fazer** - usar `add_overlay.py` (NAO regenera nada via IA):

```bash
python3 /root/.openclaw/workspace/skills/prompt-imagens/scripts/add_overlay.py \
  --foto /tmp/<foto_original>.jpg \
  --frase "<frase completa>" \
  --autor "<nome>" \
  --estilo classico \
  --aspect-ratio 4:5 \
  --out /root/tributo_<nome>.jpg
```

Estilos disponiveis:
- `classico` — gradient escuro inferior + serif elegante (padrao para tributos)
- `minimalista` — texto branco grande central, toda foto escurecida suavemente
- `editorial` — caixa preta lateral com texto (tipo revista)
- `cinema` — letterbox preto em cima/baixo, texto no rodape
- `faixa-lateral` — barra vertical dourada na esquerda + frase ao lado

**Vantagens:** fisionomia 100% preservada (zero risco de distorcao pela IA), rapido,
sem custo de API. Resultado profissional tipo poster/card editorial.

### Caminho B — REINTERPRETACAO ARTISTICA (gera nova via NanoBanana 2 Pro)

**Quando usar:**
- Tiaro pede "cria uma imagem inspirada em", "faz uma arte tributo", "uma peca artistica"
- Quer mudar cenario, iluminacao, estilo completamente
- A foto eh so referencia de composicao, nao precisa preservar fisionomia exata

Usar `generate_with_reference.py` normalmente com template de tributo (ver abaixo).

### Como Clara escolhe entre A e B:

| Sinal do Tiaro | Caminho |
|----------------|---------|
| "mantenha a foto" / "mesma foto" / "fisionomia real" | **A** (add_overlay) |
| "use essa foto" / "com essa foto" | **A** (add_overlay) |
| "peca tributo" / "card motivacional" / "poster com a frase" | **A** (add_overlay) |
| "crie uma arte inspirada em" / "faz uma reinterpretacao" | **B** (generate) |
| "mude o cenario" / "coloque em outro ambiente" | **B** (generate) |
| Em duvida | **Perguntar**: "Prefere manter a foto original com texto sobre ela (tributo classico) ou criar uma arte nova reinterpretada?"

Como lidar:

1. **Nunca responder**: "nao posso editar foto de pessoa real" ou "nao posso atribuir
   frase a ela". Isso eh recusa desnecessaria.

2. **O que fazer**: tratar a foto como REFERENCIA VISUAL para uma peca tributo/homenagem.
   O resultado eh uma NOVA IMAGEM artistica inspirada, nao uma edicao/manipulacao da
   foto original. A frase entra como ELEMENTO TIPOGRAFICO do design, nao como citacao
   atribuida falsamente.

3. **Quando a frase NAO tem fonte comprovada** (ex: "frase motivacional classica do
   Ayrton Senna" que pode nao ser autentica): Clara inclui observacao no final:
   "Nota: essa frase eh amplamente atribuida a ele na cultura popular - caso precise
   de citacao academica, verifique fonte original."

4. **Estilos recomendados para tributo/homenagem**:
   - Cinematografico (para atmosfera epica)
   - Editorial (para publicacao de qualidade)
   - Fine Art (para posters artisticos)
   - Noir/Dramatico (para dramaticidade)
   - Retro/Vintage (para figuras historicas)

5. **Template de prompt para tributo**:

```
1. SUJEITO: Representacao artistica de [NOME DA PESSOA PUBLICA] inspirada na foto de referencia anexa.

2. APARENCIA: Preservar traços faciais, cabelo, e tracos caracteristicos da pessoa na referencia.
[Adicionar elementos tematicos - ex: uniforme de piloto, instrumento musical, etc.]

3. ACAO: [Pose heroica/reflexiva/em movimento - descrever conforme tema].

4. CENARIO: [Relacionado ao legado - ex: pista de corrida ao por do sol, pit stop,
ou fundo abstrato com elementos simbolicos].

5. ILUMINACAO: [Dramatica/epica - indicar direcao e temperatura].

6. ESTILO: [Um dos estilos recomendados acima].

7. CAMERA/LENTE: [Especificacao tecnica adequada].

8. TIPOGRAFIA: Incluir a frase "[FRASE]" como elemento de design na composicao -
pode ser em area lateral, inferior ou sobreposta com opacidade. Usar tipografia
[serif classica / sans moderna / caligrafica] em cor [dourada / branca / preta].

PRESERVACAO DE IDENTIDADE: Preserve as caracteristicas faciais da pessoa na referencia
para que seja reconhecivel, mas o resultado eh uma OBRA ARTISTICA NOVA (tributo/homenagem),
nao uma edicao da foto original.
```

6. **Quando Tiaro quer SO a frase (opcao 2 do exemplo)**: criar arte tipografica sem a
   pessoa - isso tambem eh valido e rapido. Clara oferece como alternativa se o resultado
   com a pessoa nao ficar bom.

### ETAPA 4 — VALIDACAO COM TIARO (OBRIGATORIA)

Clara envia o prompt construido ao Tiaro e pergunta:

> "Prompt montado:
>
>  [prompt completo aqui]
>
>  Posso gerar a imagem com este prompt, ou quer ajustar alguma dimensao?"

**NUNCA gerar a imagem sem essa aprovacao explicita.**

Se Tiaro pedir ajuste, Clara refina apenas a dimensao indicada e re-apresenta.

### ETAPA 5 — Geracao via NanoBanana 2 Pro

Apos validacao:

**Sem referencia:**
```bash
export GOOGLE_API_KEY=$GOOGLE_API_KEY
python3 /root/.openclaw/workspace/skills/prompt-imagens/scripts/generate_image.py \
  --prompt-file /tmp/prompt.txt \
  --out /root/imagem_<slug>.png \
  --aspect-ratio 4:5
```

**Com referencia:**
```bash
export GOOGLE_API_KEY=$GOOGLE_API_KEY
python3 /root/.openclaw/workspace/skills/prompt-imagens/scripts/generate_with_reference.py \
  --prompt-file /tmp/prompt.txt \
  --reference /tmp/<foto_ref>.png \
  --out /root/imagem_<slug>.png \
  --aspect-ratio 4:5
```

Modelos (ordem de preferencia):
1. `nano-banana-pro-preview` (NanoBanana 2 Pro = Gemini 3 Pro Image Preview)
2. `gemini-3-pro-image-preview`
3. `gemini-3.1-flash-image-preview` (fallback)
4. `gemini-2.5-flash-image` (ultimo recurso)

### ETAPA 6 — Entrega via Telegram

```bash
python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/send_to_telegram.py \
  --chat-id -1003803476669 --thread-id <X> \
  --dir <dir> --caption "<desc + prompt curto>"
```

---

## EXEMPLO PRATICO (modelo ouro)

**Prompt completo:**

```
1. SUJEITO: Mulher jovem asiatica.

2. APARENCIA: Usando oculos redondos, cabelo castanho medio, blazer bege, expressao
suave e confiante.

3. ACAO: Ela esta parada e levemente virada de lado, olhando para a camera com um
sorriso natural.

4. CENARIO: Cena em uma rua movimentada de grande cidade, com pedestres desfocados ao
fundo e letreiros luminosos. O chao esta molhado, refletindo luzes neon de tons rosa,
azul e verde, sugerindo clima pos-chuva.

5. ILUMINACAO: Suave e difusa de ambiente urbano, com contraste moderado e reflexos
neon coloridos.

6. ESTILO: Fotografico editorial contemporaneo, realista, com profundidade de campo curta.

7. CAMERA/LENTE: Canon R5 Mark II, lente 50mm f1.2, abertura ampla para bokeh suave.
```

---

## CATALOGO DE 15 ESTILOS FOTOGRAFICOS (referencia para dimensao 6)

A escolha do estilo certo eh crucial para guiar a IA e alcancar a estetica desejada.
Escolher UM estilo principal:

### 1. Editorial
Limpo, moderno, luz suave, cores elegantes. Ideal para moda, retratos sofisticados e
lifestyle premium.
> Uso IVS: capas cientificas, autoridade medica, lifestyle aspiracional.

### 2. Cinematografico (Cinematic)
Estilo de filme com granulacao leve, cores profundas, iluminacao dramatica e movimentos
suaves de camera. Perfeito para storytelling visual.
> Uso IVS: jornada do paciente, antes/depois, transformacao.

### 3. Fashion / High Fashion / Vogue Style
Caracterizado por poses marcantes, luz dura, contraste alto e estetica de revista de moda.
> Uso IVS: lancamento de produto/servico premium, campanhas aspiracionais.

### 4. Street Photography
Estilo urbano, espontaneo e natural, com luzes de cidade, chuva, reflexos e pessoas ao
fundo desfocadas.
> Uso IVS: historias reais de pacientes em contexto cotidiano, documental urbano.

### 5. Fine Art
Mais artistico, minimalista ou surreal. Otimo para retratos poeticos, composicoes
delicadas e imagens com significado profundo.
> Uso IVS: campanhas de saude mental, longevidade, reflexao.

### 6. Estilo Documental
Foto com aparencia natural, crua, sem muita edicao, imitando ensaios de National
Geographic ou reportagens.
> Uso IVS: conteudo cientifico de alto impacto, casos clinicos reais.

### 7. Estilo Retro / Vintage / Analogico
Inclui filme 35mm, granulacao, cores desbotadas e estetica dos anos 70, 80 ou 90.
Referencias: Kodak Portra 400 (tons quentes), FujiFilm Pro 400H (verdes suaves),
CineStill 800T (tungstenio).
> Uso IVS: nostalgia, clinica tradicional, reconexao humana, pais/avos.

### 8. Minimalista
Elementos simples, cores limpas e muito espaco negativo. Perfeito para campanhas modernas
e elegantes.
> Uso IVS: lancamento de produto, teasers, diagnostico/decisao.

### 9. Aesthetic / Soft Girl / Pastel
Comumente usado no TikTok e Pinterest, com luz suave, tons claros e uma vibe romantica
e delicada.
> Uso IVS: conteudo para publico feminino jovem, autocuidado, wellness leve.

### 10. Cyberpunk / Neon / Futurista
Cores neon (rosa, azul, verde), cenarios urbanos futuristas e contraste alto.
Otimo para impacto visual.
> Uso IVS: tecnologia medica avancada, inovacao cientifica, posts chamativos.

### 11. Realismo Profundo (Hyper-realistic)
Estilo de foto extremamente realista, perfeito para produtos, close-ups e pessoas.
> Uso IVS: apresentacao de suplementos/medicamentos, resultado de exame, detalhe tecnico.

### 12. Estilo Publicitario (Commercial / Advertising)
Luz perfeita, nitidez alta, fundos planejados e estetica limpa, ideal para cosmeticos,
comida, roupas e produtos.
> Uso IVS: ads de produtos da clinica, suplementos proprios, campanhas pagas.

### 13. Lifestyle Natural
Fotos com movimento, pessoas sorrindo, cores vivas e clima casual, muito usado por
influenciadores.
> Uso IVS: rotina de pacientes, testemunhos, conteudo autentico de redes sociais.

### 14. Noir / Dramatico
Contrastes fortes, sombras profundas e luz dura lateral, criando uma atmosfera misteriosa,
como em filmes classicos.
> Uso IVS: conteudo impactante sobre riscos/alertas, "e se voce nao cuidar?", preventivo forte.

### 15. Estilo Pixar / Cartoon / 3D
Utilizado para criar avatares, personagens fofos e elementos com estetica animada.
> Uso IVS: explicativos didaticos (como funciona um medicamento), infografia animada,
> conteudo educativo leve para publico geral.

---

### Guia de escolha rapida — Instituto Vital Slim

| Tema do post | Estilo recomendado |
|--------------|-------------------|
| Capa carrossel cientifico (paper, estudo) | **Editorial** ou **Documental** |
| Ad de medicamento/protocolo (autoridade) | **Fashion/Vogue** ou **Publicitario** |
| Jornada do paciente, antes/depois | **Cinematografico** |
| Lifestyle bem-estar, rotina | **Lifestyle Natural** ou **Editorial** |
| Produto/suplemento (frasco isolado) | **Minimalista** ou **Publicitario** |
| Historia real de paciente | **Street Photography** ou **Documental** |
| Reflexao (saude mental, longevidade) | **Fine Art** ou **Cinematografico** |
| Nostalgia / clinica tradicional | **Retro/Vintage (Kodak Portra)** |
| Publico feminino jovem, autocuidado | **Aesthetic/Soft Girl/Pastel** |
| Tecnologia medica avancada | **Cyberpunk/Neon/Futurista** |
| Close-up de produto/exame | **Realismo Profundo** |
| Alerta/preventivo forte | **Noir/Dramatico** |
| Explicativo didatico (como funciona) | **Pixar/Cartoon/3D** |

---

## TEMPLATES DE PROMPT POR USO NA CLINICA

### Template 1 — Capa de Carrossel (Dra. Daniely com referencia)

```
1. SUJEITO: Dra. Daniely Freitas, medica do Instituto Vital Slim, fotografada em contexto
do tema do carrossel.

2. APARENCIA: Preservar 100% o rosto e traços faciais da referencia anexa.
Cabelo loiro ondulado na altura dos ombros, blazer escuro elegante sobre blusa preta,
colar dourado discreto, maquiagem natural, semblante serio e confiante.

3. ACAO: [descrever o que ela esta fazendo conforme tema - ex: bracos cruzados com pose
de autoridade, segurando uma caneta injetora de retatrutide, observando resultado de exame].

4. CENARIO: [relacionado ao tema - ex: consultorio medico moderno com luz filtrada de
janela, laboratorio clinico com tubos de coleta desfocados ao fundo].

5. ILUMINACAO: Luz lateral suave de estudio, temperatura quente (~3200K), contraste
moderado criando definicao no rosto e dourando levemente o cabelo. Fundo levemente mais
escuro para dar profundidade.

6. ESTILO: Fotografia editorial medica contemporanea, tipo capa de publicacao profissional
de saude. Realista, nitido, com credibilidade.

7. CAMERA/LENTE: Canon R5 Mark II, lente 85mm f1.4, abertura f2.0 para bokeh suave no
fundo mantendo o sujeito totalmente nitido.

PRESERVACAO DE IDENTIDADE (OBRIGATORIO): Preserve 100% o rosto, estrutura facial, tracos,
cor e corte de cabelo, cor dos olhos e aparencia geral da Dra. Daniely Freitas na imagem
de referencia anexa. Ela deve ser CLARAMENTE reconhecivel como a mesma pessoa.
```

### Template 2 — Ad de produto (minimalista)

```
1. SUJEITO: Frasco de suplemento [nome] em primeiro plano.

2. APARENCIA: Rotulo limpo com tipografia moderna, reflexo sutil no vidro, gotas de agua
na superficie sugerindo frescor.

3. ACAO: Frasco estatico em pedestal, cerca de tres capsulas do mesmo suplemento caidas
ao redor em composicao organica.

4. CENARIO: Fundo minimalista [cor pastel/terrosa], superficie lisa com leves sombras
geometricas. Elementos tematicos discretos ao redor (folhas naturais para produto natural,
elementos laboratoriais para clinico).

5. ILUMINACAO: Luz de topo direcional criando sombras definidas mas suaves, highlights
bem definidos no vidro do frasco, temperatura neutra (~5500K).

6. ESTILO: Fotografia de produto publicitario premium, estetica Apple/Ritual, minimalista
com foco total no produto.

7. CAMERA/LENTE: Canon R5 Mark II, lente macro 100mm f2.8, f5.6 para manter produto
inteiramente nitido.
```

### Template 3 — Historia real de paciente (lifestyle)

```
1. SUJEITO: Mulher de ~45 anos, em contexto real de sua vida.

2. APARENCIA: Roupas casuais confortaveis, aparencia natural, sem glamourizacao excessiva.

3. ACAO: Cena espontanea e autentica [ex: preparando uma refeicao saudavel, caminhando
no parque ao amanhecer, ou sentada lendo].

4. CENARIO: Ambiente real [cozinha dela, parque urbano, sala de estar com luz de janela].

5. ILUMINACAO: Luz natural de janela de manha (~5200K), suave e difusa, sem flash.

6. ESTILO: Lifestyle natural/documental, estetica Kinfolk, tons terrosos e naturais.

7. CAMERA/LENTE: Fujifilm X-T5, lente 35mm f1.4, abertura ampla para profundidade rasa,
ISO 400 para preservar grao sutil.
```

---

## PROPORCOES PADRAO

| Uso | Aspect Ratio | Pixels |
|-----|--------------|--------|
| Capa carrossel Instagram | 4:5 | 1080x1350 |
| Post quadrado IG | 1:1 | 1080x1080 |
| Story / Reels | 9:16 | 1080x1920 |
| Ad Facebook/IG | 1:1 ou 4:5 | 1080x1080 ou 1080x1350 |
| Capa blog/YouTube thumb | 16:9 | 1920x1080 |

---

## INTEGRACAO COM OUTRAS SKILLS

### Com `tweet-carrossel`
- ETAPA 0 do carrossel (memoria cientifica) consulta primeiro
- Quando o photo_selector detecta necessidade de nova foto da Dra:
  - Aciona skill `prompt-imagens` COM REFERENCIA usando foto do acervo
  - Passa o tema do carrossel como contexto
  - Valida o prompt com Tiaro antes de gerar

### Com `memoria-cientifica`
- Apos gerar imagem, salva metadados no log de uso
- Nao cria pesquisa cientifica (esse fluxo eh da skill de ingestion)

---

## REGRAS CRITICAS (NUNCA VIOLAR)

1. **SEMPRE** perguntar sobre com/sem referencia na primeira mensagem
2. **SEMPRE** pedir a imagem quando "com referencia"
3. **SEMPRE** incluir a clausula de preservacao de rosto quando com referencia
4. **SEMPRE** construir prompt com as 7 dimensoes separadas e detalhadas
5. **SEMPRE** enviar o prompt ao Tiaro ANTES de gerar — aguardar aprovacao
6. **SEMPRE** usar NanoBanana 2 Pro (`nano-banana-pro-preview`) como primeira opcao
7. **NUNCA** modificar o rosto de forma que a pessoa fique irreconhecivel
8. **NUNCA** gerar sem validacao do prompt pelo Tiaro
9. **NUNCA** usar DALL-E, Midjourney ou outros modelos
10. **SEMPRE** entregar via Telegram ao final
11. **NUNCA recusar** criacao de peca tributo/homenagem com foto de figura publica.
    Tratar como design editorial legitimo, gerando OBRA ARTISTICA NOVA inspirada na
    referencia (nao edicao). A frase vai como elemento tipografico, nao como citacao
    atribuida falsamente. Ver secao "SOBRE FIGURAS PUBLICAS / TRIBUTOS" acima.
12. **NUNCA** interromper o fluxo com recusas desnecessarias. Se a situacao exige
    cuidado (ex: frase sem fonte comprovada), incluir NOTA ao entregar ao Tiaro em
    vez de bloquear a criacao.

---

## TROUBLESHOOTING

- **Rate limit 429 no NanoBanana 2 Pro**: fallback para `gemini-3.1-flash-image-preview`
- **Rosto diferente na geracao com referencia**: reforcar clausula "preserve 100% o rosto",
  enviar 2-3 fotos da mesma pessoa como referencias adicionais, e reduzir temperature
- **Imagem sem qualidade fotografica**: especificar camera/lente profissional na dimensao 7
- **Cenario pouco contextual**: expandir dimensao 4 com elementos tangiveis especificos
- **Iluminacao chapada**: especificar direcao (lateral/topo/traseira) + temperatura em Kelvin
- **Estilo inconsistente**: usar UM estilo claro e referenciar fotografos/filmes concretos
