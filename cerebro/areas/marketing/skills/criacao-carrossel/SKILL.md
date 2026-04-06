---
name: criacao-carrossel
description: >
  Cria o roteiro completo de um carrossel no Modelo 01 para o Instagram do IVS/Dra. Daniely, seguindo o padrão visual e editorial validado. Trigger: "crie um carrossel sobre [tema]" ou "carrossel Modelo 01".
---

# Criação de Carrossel

## Regras Operacionais
- **Imagens:** sempre usar **NanoBanana2** (`google/gemini-3.1-flash-lite-preview`) para análise, extração de texto e descrição de imagens
- **Avatar Dra. Daniely:** nunca modificar — usar sempre `/root/.openclaw/workspace/deliverables/tmp_modelo01_v4/avatar.png`
- **Script:** `/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py` — Modelo 01

## Quando usar
Sempre que Tiaro pedir um carrossel. Se mencionar "Modelo 01", seguir este playbook com alta fidelidade.

## Input necessário
- Tema ou assunto do carrossel
- Fotos disponíveis (se houver — fotos reais da Dra. Daniely têm prioridade)
- Objetivo do post: Audiência / Tempo de Tela / Desejo / Ação (dos 4 Pilares)

## Estrutura obrigatória (6 slides)

### Slide 1 — Capa
**Template validado por Tiaro (2026-04-06) — script: `/tmp/make_capa_lipedema.py`**

Proporções canônicas (1080×1350px):
- **Foto:** ocupa 742px (55% da altura), largura total 1080px. Fade suave Y=620→742 para preto.
- **Fundo:** pode ser gerado temático (ex: fundo neural dourado) + foto da Dra. sem fundo (rembg) composta em cima
- **Círculo produto/imagem temática:** centro (920, 155), diâmetro 270px, borda dourada 8px
- **Linha dourada divisória:** Y=742, espessura 3px, com gap central para o símbolo V
- **Símbolo V Vital Slim:** `/cerebro/assets/identidade-visual/simbolo-v-negativo-transparente.png` recolorido em dourado (#C5A059), círculo borda dourada, tamanho 52px, centralizado em Y=742
- **Texto:** fonte 88px bold, line-height 108px, começa em Y≈800, margens mínimas (~40px), quase largura total
- **Cores:** branco (#FFFFFF) + dourado (#C5A059) alternando por linha
- **CRM:** "Dra. Daniely Freitas  |  CRM-BA 27588", fonte 26px cinza, centralizado Y=H-38

### Slide 2 — Gancho científico (tweet frame)
**Referência canônica:** `cerebro/assets/carrosseis/REFERENCIA_SLIDE2_TWEET.jpg`

Proporções validadas por Tiaro (2026-04-06):
- Fundo preto total (#000000)
- Avatar circular + "Dra Daniely Freitas ✓" (bold 34px) + "@dradaniely.freitas" (28px cinza) — topo esquerdo, margem 60px
- Texto corrido do tweet: fonte 36px regular branco, margem 60px, line-height 52px — começa em Y≈170
- Imagem do paper/estudo: centralizada, largura 82% do slide, borda fina dourada (2px) com padding 10px, abaixo do texto com gap de 30px
- Referência bibliográfica: fonte 26px cinza centralizada, abaixo da imagem
- Altura do slide: variável (1350–1600px) — expandir se necessário para não cortar conteúdo

### Slides 3, 4 — Pilares de prova
- Foto dominante ocupando todo o fundo
- Overlay escuro na metade inferior
- Título do conceito em branco, muito visível
- Dado principal com número específico + explicação curta
- Referência científica pequena no rodapé
- Contador no topo direito

### Slide 5 — Minha prática
- Fundo claro (quase todo branco) — quebra visual forte
- Pequena foto/avatar da Dra. Daniely no topo esquerdo com nome e perfil
- Título "Minha prática:" em cor de destaque forte
- Bullets grandes, espaçados, muito legíveis
- Muito respiro — este slide não deve parecer carregado

### Slide 6 — Fechamento / CTA
- Foto full-bleed forte e humana
- Texto grande em branco sobre a imagem
- CTA simples e memorável: normalmente "Salve este post."
- Frase final emocional/estratégica abaixo do CTA

## Regras visuais
- Formato vertical 4:5
- Fotos reais com cara editorial/premium — nunca banco de imagens genérico
- Títulos grandes, alto contraste
- Texto em blocos curtos
- Imagem dominante + texto enxuto e potente (nunca 50/50)
- Evitar cards demais, barras laterais ou composições que diminuam a presença humana

## Regras de copy
- Headline curta e forte (escolher hook adequado ao objetivo do post)
- Números específicos quando houver dado científico
- Tom de autoridade sem excesso acadêmico
- Frases memoráveis no fechamento
- Evitar CTA fraco ou genérico

## Lógica editorial
1. Abrir com promessa ampla (hook)
2. Provar com 3 evidências (slides 2–4)
3. Traduzir para prática pessoal (slide 5)
4. Fechar com CTA simples e memorável (slide 6)

## Seleção do hook (ver memory/content/hooks-reels-carrosseis.md)
- Post de Audiência/Tela → Curiosidade Aberta, Dor Direta, Confissão
- Post de Desejo → Autoridade Instantânea, Número+Resultado
- Post de Ação → Promessa Clara, Alerta/Aviso

## Regra de prioridade
- Se Tiaro enviar imagens de referência → elas viram a fonte primária do estilo
- Conflito entre playbook e referência enviada por Tiaro → referência de Tiaro vence
- Se Tiaro mencionar "Modelo 01" → assumir este playbook automaticamente

## Output esperado
Roteiro completo slide a slide com:
- Texto exato de headline, subtítulo, corpo e CTA de cada slide
- Instrução visual para cada slide (foto sugerida, overlay, posicionamento)
- Referências científicas prontas para rodapé (quando aplicável)
