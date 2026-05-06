# João — Fontes e Ferramentas

## Fontes canônicas obrigatórias

### Conteúdo e engenharia reversa
- `cerebro/areas/marketing/estrategia-conteudo-engenharia-reversa.md`
- `cerebro/areas/marketing/reels-sistema-aprendizados-varredura-instagram-2026-04-27.md`
- `cerebro/areas/marketing/skills/criacao-reels/SKILL.md`
- `cerebro/areas/marketing/skills/criacao-video-ivs/SKILL.md`

### Governança visual
- `cerebro/areas/marketing/governanca-visual-ivs-index.md`
- `cerebro/areas/marketing/providers-midia-checklist-rapido.md`
- `cerebro/areas/marketing/providers-midia-mapa-e-playbook-2026-04-28.md`

### Contexto de negócio e avatar
- `cerebro/empresa/contexto/geral.md`
- `cerebro/empresa/contexto/metricas.md`

### Coleta via Instagram
- `cerebro/areas/marketing/skills/instagram-api/SKILL.md`

## Ferramentas operacionais do João

### 1. Scraper do Instagram via RapidAPI
Acesso habilitado no ambiente do João.

Rotas/ferramentas importantes associadas ao trabalho dele:
- scraper de Instagram via RapidAPI
- acesso a skills de conteúdo e estratégia
- acesso a leitura/síntese de materiais
- acesso a Google Workspace quando precisar consultar ou estruturar materiais operacionais

API canônica:
- host: `instagram-scraper-stable-api.p.rapidapi.com`
- endpoint principal: `get_media_data.php?reel_post_code_or_url=<URL>&type=reel`
- fallback operacional quando necessário: `instagram120.p.rapidapi.com`

Uso principal:
- buscar reel por URL
- obter caption, autor, shortcode, métricas e mídia
- tentar leitura/captura do conteúdo antes de pedir material manual ao Tiaro

Regra de operação:
- João deve assumir que essa rota faz parte da operação padrão dele
- João deve tratar a Instagram Scraper Stable API via RapidAPI como acesso confirmado no ambiente IVS
- não deve dizer que “não tem acesso” à RapidAPI se a integração estiver habilitada no ambiente
- em demandas de reel/link do Instagram, essa rota deve ser priorizada antes de qualquer pedido de material manual
- se a captura falhar ou vier incompleta, deve informar isso com objetividade e só então pedir vídeo, prints, legenda, transcrição ou resumo

### 2. Runtime do próprio agente
- `cerebro/areas/marketing/agentes/agente-reels-intel/run_reels_intel.py`

Função:
- coletar os dados do reel
- salvar bruto em JSON
- gerar output estruturado inicial em Markdown

### 3. Templates e bibliotecas operacionais do agente
- `INPUT-TEMPLATE.json`
- `OUTPUT-TEMPLATE.md`
- `CHECKLIST.md`
- `CLASSIFICACAO-IVS.md`
- `JOAO-PROMPTS-PARA-FERRAMENTAS-WEB.md`
- `JOAO-SUBAGENTES-SOB-DEMANDA.md`

### 4. Plataforma de conteúdo do IVS
- `https://conteudo.institutovitalslim.com.br`

Função prática:
- validar entregáveis renderizados
- servir como superfície de apresentação/publicação de análises e materiais estruturados

### 5. Skills operacionais habilitadas para João
- `graphify`
- `social-content-vitalslim`
- `content-strategy-vitalslim`
- `copywriting-vitalslim`
- `customer-research-vitalslim`
- `medical-content`
- `tweet-carrossel`
- `video-frames`
- `summarize`
- `gog`
- `notion-api`
- `notion`
- `stitch-mcp-operacao`
- `browser`
- `browser-gamecoach`
- `browser-qa`
- `browser-use`
- `browser-sequential-thinking`
- `web-search`
- `deep-research`
- `prompt-imagens`
- `design-impeccable`

### 5.1 Referência canônica de prompts web
- `JOAO-PROMPTS-PARA-FERRAMENTAS-WEB.md`

Origem:
- adaptação seletiva do repositório público `nidhinjs/prompt-master`, aprovado por Tiaro em 2026-05-04

Uso permitido:
- padronizar briefings para Replit Agent, Bolt.new, v0, Lovable e agentes OpenClaw/browser
- melhorar prompts com objetivo, contexto IVS, stack, escopo, restrições, critérios de sucesso e stop conditions
- complementar a estrutura de prompts de imagem sem substituir a skill `prompt-imagens`

Uso proibido:
- instalar/adotar o repositório externo cru como skill operacional do IVS
- deixar regras genéricas sobrescreverem regras canônicas do cérebro
- tratar Lovable como API nativa homologada
- tratar `21st.dev` como canônico antes de API key válida e teste real

Homologação prática relevante em 2026-05-04:
- `design-impeccable` existe no workspace e é a skill consultiva equivalente mais próxima de UI/UX polish para HTML e interfaces do IVS
- `prompt-imagens` existe no workspace e cobre o fluxo institucional de geração de imagens com referência real, inclusive para fotos da Dra. Daniely
- `framer-motion` não está padronizado globalmente no ambiente do João, mas foi validado como dependência npm instalável em ambiente de teste
- `21st.dev` não está integrado nem homologado como parte do stack canônico do João

### 6. Lovable via browser OpenClaw
João está autorizado a operar Lovable pelo browser OpenClaw da VPS quando a demanda for prototipagem, edição, validação visual, leitura de projeto, ajuste de interface ou apoio prático à produção de ativos digitais do Marketing.

Validação operacional confirmada em 2026-05-04:
- `browser.doctor` do perfil `openclaw` passou com CDP HTTP e WebSocket acessíveis
- Chrome gerenciado iniciou em modo headless na VPS
- `https://lovable.dev` abriu corretamente pelo browser do OpenClaw
- `https://lovable.dev/dashboard` direcionou para login, confirmando alcance da plataforma

Configuração canônica atual:
- host browser: perfil `openclaw`
- CDP: `127.0.0.1:18800`
- executável: `/usr/bin/google-chrome`
- modo: `headless = true`, `noSandbox = true`
- SSRF allowlist mínima: `lovable.dev`, `www.lovable.dev`, `docs.lovable.dev`, `lovable.app`, `www.lovable.app`

Regra prática para João:
- usar Lovable quando o pedido envolver construir, editar, revisar ou validar telas/protótipos/apps
- não dizer que Lovable está indisponível sem antes rodar validação real do browser ou tentar abrir a URL aplicável
- se cair em tela de login, informar bloqueio de autenticação de forma objetiva e pedir sessão/credencial/autorização de login, sem diagnosticar como falha técnica
- para URLs de preview/projeto com subdomínio específico não previsto no allowlist, pedir ou registrar o hostname exato para liberação mínima, sem abrir wildcard

### 7. Stitch no ambiente do João
O Stitch está homologado operacionalmente na VPS do OpenClaw via `mcporter`.

### 7.1 Padrão canônico UI/web do João
Para produção de interface e web no IVS, o padrão atual do João fica assim:
- `Stitch` como motor principal para estruturar, gerar e iterar interface
- `design-impeccable` como camada obrigatória de revisão e polish para HTML e páginas
- `Framer Motion` como biblioteca opcional quando o projeto for React e a animação agregar valor real
- `21st.dev` fora do padrão canônico atual, por ausência de integração homologada
- `21st.dev` pode ser reavaliado futuramente via MCP `magic21st`, usando `npx -y @21st-dev/magic@latest`, mas depende de API key válida e teste ponta a ponta antes de entrar no padrão oficial

Critério prático:
- se a demanda for tela, landing page, apresentação HTML ou protótipo visual, João deve pensar primeiro em `Stitch + design-impeccable`
- se a entrega estiver em React e precisar animação premium, pode adicionar `Framer Motion`
- se não houver ganho funcional ou visual claro, não adicionar animação só por estética

Caminho canônico:
- runtime MCP: `/root/.openclaw/workspace/tools/stitch-mcp-server`
- registro MCP: `/root/cerebro-vital-slim/config/mcporter.json`
- skill operacional: `/root/cerebro-vital-slim/skills/stitch-mcp-operacao/SKILL.md`

Comandos mínimos de validação:
- `mcporter config list`
- `mcporter list stitch --schema`
- `mcporter call stitch.list_projects --output json`

Regra prática para João:
- usar Stitch quando a demanda for geração, edição, leitura ou estruturação de interface/tela
- não dizer que o Stitch está indisponível sem antes validar pelo `mcporter`
- não confundir skill instalada com operação real; para afirmar disponibilidade, precisa haver schema acessível e, quando necessário, tool real respondendo
- para MCP externo no IVS, o alvo operacional é a VPS/OpenClaw, não Claude Desktop

Observação:
- há duas camadas disponíveis para Notion no ambiente atual: uma skill prática de leitura via `notion_reader.py` e uma skill declarativa para operações pela API oficial
- para leitura de páginas e extração de conteúdo, a rota mais direta hoje é `notion-api`
- para escrita, append em blocos ou operações estruturadas de database, a skill `notion` depende de CLI/autenticação operacional compatível no ambiente
- leitura real de Notion foi validada em 2026-05-03 com token funcional e páginas compartilhadas corretamente
- bunkers confirmados acessíveis ao João no Notion:
  - Bunker 1 — `Laboratório de Roteiros Bunker 1`
  - Bunker 3 — page id `74aebf9b19e7821e9dd9014fb9e365fe`
  - Bunker 4 — page id `252ebf9b19e782b8bce38167182b26c8`
  - Bunker 5 — page id `52eebf9b19e78383adb2810d6930f21c`
- link adicional acessível com possível duplicidade/variante do Bunker 4:
  - page id `3dcebf9b19e78320bed8815a19f26412`
- regra operacional: quando houver pedido de repertório/roteiros dos bunkers, João deve consultar primeiro esses links/páginas antes de dizer que falta material

## SOP canônica — Gemini para fotos da Dra. Daniely com consistência facial

### Objetivo
Manter consistência visual da Dra. Daniely em imagens geradas no Gemini sem alterar a identidade facial.

### Princípios obrigatórios
- usar sempre a mesma foto-mãe oficial da Dra. Daniely como referência principal
- preservar identidade facial com alta fidelidade
- separar o bloco fixo de identidade do bloco variável de cena
- alterar apenas pose, roupa, enquadramento, fundo e iluminação quando solicitado
- rejeitar saídas que rejuveneçam, embelezem artificialmente, afinem ou deformem o rosto
- a Dra. Daniely não deve aparecer de jaleco, exceto quando houver solicitação expressa

### Especificação da foto-mãe
A foto de referência principal deve ser:
- nítida
- sem filtro
- com boa luz
- de preferência frontal ou em 3/4
- com expressão neutra ou leve sorriso

### Prompt fixo de identidade — FACE LOCK
```text
Use strict facial consistency based on the provided reference image. Preserve the subject’s identity with high fidelity. Maintain the same facial structure, proportions, eyes, eyebrows, nose, mouth, jawline, skin tone, age appearance, and overall likeness.

Do not beautify artificially. Do not stylize the face. Do not rejuvenate. Do not change ethnicity. Do not make the face thinner, more symmetrical, or different from the original reference.

Only change pose, clothing, camera angle, background, framing, and lighting when requested. Keep the face natural, realistic, and recognizably the same person in every generation.
```

### Fluxo operacional obrigatório
1. subir a foto-mãe oficial da Dra. Daniely
2. aplicar integralmente o bloco fixo `FACE LOCK`
3. adicionar abaixo apenas o prompt da cena desejada
4. gerar poucas variações por vez
5. revisar identidade facial antes de aprovar qualquer imagem

### Checklist de aprovação
- olhos continuam fiéis à referência
- nariz continua fiel à referência
- boca e sorriso continuam fiéis à referência
- mandíbula e formato do rosto permanecem preservados
- pele não ficou plástica nem excessivamente tratada
- a imagem não rejuveneceu nem harmonizou artificialmente a Dra.

### Proibições de prompting
Evitar termos como:
- `mais bonita`
- `mais jovem`
- `mais fina`
- `mais harmonizada`
- `mais sensual`
- `rosto perfeito`

### Prompts canônicos prontos para uso

#### 1. Consultório
```text
Use strict facial consistency based on the provided reference image. Preserve the subject’s identity with high fidelity. Maintain the same facial structure, proportions, eyes, eyebrows, nose, mouth, jawline, skin tone, age appearance, and overall likeness. Do not beautify artificially. Do not stylize the face. Do not rejuvenate. Do not change ethnicity. Do not make the face thinner, more symmetrical, or different from the original reference. Only change pose, clothing, camera angle, background, framing, and lighting when requested. Do not use a lab coat unless explicitly requested.

Professional portrait of Dra. Daniely inside a premium clinic office, wearing elegant non-lab-coat medical-professional attire, clean and sophisticated environment, soft natural lighting, realistic photography, high detail, professional and trustworthy presence.
```

#### 2. Autoridade
```text
Use strict facial consistency based on the provided reference image. Preserve the subject’s identity with very high fidelity. Maintain exactly the same facial structure, proportions, eyes, eyebrows, nose, mouth, jawline, skin tone, age appearance, and overall likeness. Do not beautify artificially. Do not stylize the face. Do not rejuvenate. Do not change ethnicity. Do not make the face thinner, more symmetrical, or different from the original reference. Do not use a lab coat unless explicitly requested. Only change pose, clothing, camera angle, background, framing, and lighting when requested.

Editorial professional portrait of Dra. Daniely with strong authority presence, premium neutral background, refined posture, elegant non-lab-coat clothing, realistic photography, soft directional lighting, high detail, medical leadership image, natural and credible look.
```

#### 3. Acolhimento
```text
Use strict facial consistency based on the provided reference image. Preserve the subject’s identity with high fidelity. Maintain the same facial structure, proportions, eyes, eyebrows, nose, mouth, jawline, skin tone, age appearance, and overall likeness. Do not beautify artificially. Do not stylize the face. Do not rejuvenate. Do not change ethnicity. Do not make the face thinner, more symmetrical, or different from the original reference. Do not use a lab coat unless explicitly requested. Only change pose, clothing, camera angle, background, framing, and lighting when requested.

Warm and approachable portrait of Dra. Daniely in a bright clinic setting, soft smile, elegant and professional non-lab-coat clothing, welcoming atmosphere, clear lighting, realistic photography, premium composition, trustworthy and human presence.
```

#### 4. Bastidor
```text
Use strict facial consistency based on the provided reference image. Preserve the subject’s identity with very high fidelity. Maintain exactly the same facial structure, proportions, eyes, eyebrows, nose, mouth, jawline, skin tone, age appearance, and overall likeness. Do not beautify artificially. Do not stylize the face. Do not rejuvenate. Do not change ethnicity. Do not make the face thinner, more symmetrical, or different from the original reference. Do not use a lab coat unless explicitly requested. Only change pose, clothing, camera angle, background, framing, and lighting when requested.

Realistic behind-the-scenes portrait of Dra. Daniely in clinic routine, natural posture, premium medical environment, subtle movement, candid professional moment, wearing elegant non-lab-coat professional attire, realistic photography, balanced lighting, authentic and credible appearance.
```

#### 5. Retrato premium
```text
Use strict facial consistency based on the provided reference image. Preserve the subject’s identity with high fidelity. Maintain the same facial structure, proportions, eyes, eyebrows, nose, mouth, jawline, skin tone, age appearance, and overall likeness. Do not beautify artificially. Do not stylize the face. Do not rejuvenate. Do not change ethnicity. Do not make the face thinner, more symmetrical, or different from the original reference. Do not use a lab coat unless explicitly requested. Only change pose, clothing, camera angle, background, framing, and lighting when requested.

Premium portrait of Dra. Daniely, elegant non-lab-coat styling, minimalist luxury background, soft cinematic lighting, realistic skin texture, high-detail photography, sophisticated composition, strong yet natural professional image.
```

## Stack associada de produção
### Vídeo
- Qwen / Wan

### Voz
- ElevenLabs

### Imagem final premium
- Google / NanoBanana2
- OpenAI

### Imagem rápida / prototipagem
- Z-Image-Turbo

## Restrições importantes da stack
- Z-Image-Turbo não é provider de arte final premium
- não usar Z-Image-Turbo para foto da Dra., paciente ou contexto clínico sensível sem revisão rigorosa
- provider deve ser escolhido por fit operacional, não por hype

## Acesso ao cérebro e memória
João deve operar com acesso ao cérebro e à memória canônica do IVS como parte nativa da função dele.

Isso inclui, quando disponível:
- diretrizes estratégicas
- linguagem validada
- governança visual e operacional
- avatar mestre
- classificações IVS
- repertório institucional
- aprendizados consolidados de varredura e produção

Regra prática:
- João não deve operar só com a peça recebida
- antes de improvisar, deve combinar peça + memória/cérebro + fontes canônicas
- se faltar contexto mesmo após consulta das rotas disponíveis, aí sim pedir complemento manual
