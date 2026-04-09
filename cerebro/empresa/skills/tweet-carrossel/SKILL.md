---
name: tweet-carrossel
description: >
  Gera carrosseis completos para o Instagram no formato tweet (estilo X/Twitter).
  Fluxo: primeiro criar a COPY (texto), depois de aprovada, gerar as IMAGENS.
  SEMPRE usar NanoBanana 2 para gerar fotos. Slides tweet via Python/Pillow ou HTML+Chromium.
  Use quando: "carrossel", "criar carrossel", "formato tweet", "carrossel preto",
  "slides instagram", "carrossel cientifico", "montar carrossel", "criar slides".
metadata:
  version: 3.0.0
  domain: marketing
  owner: main
---

# Tweet Carrossel v3 - Geracao Completa de Carrosseis Instagram

## FLUXO DE TRABALHO OBRIGATORIO (2 ETAPAS)

### ETAPA 1 - COPY (texto)
1. Usuario envia tema, paper cientifico ou arquivo de referencia
2. Clara cria a copy de TODOS os slides seguindo a estrutura AIDA/retenção
3. Clara apresenta a copy para aprovacao do usuario
4. Usuario aprova ou pede ajustes
5. SO APOS APROVACAO da copy, seguir para etapa 2

### ETAPA 2 - IMAGENS
1. Clara gera a capa via NanoBanana 2 + Pillow
2. Clara gera o slide 2 (paper) via HTML + Chromium
3. Clara gera slides 3+ via script Python (make_tweet_slides.py)
4. Clara entrega todas as imagens

**NUNCA gerar imagens antes da copy ser aprovada.**

---

## ESTRUTURA DO CARROSSEL

| Slide | Tipo | Metodo de geracao |
|-------|------|-------------------|
| 1 | Capa (foto Dra. + headline) | NanoBanana 2 (foto) + Pillow (texto) |
| 2 | Paper cientifico (texto tweet + PubMed) | HTML + Chromium headless |
| 3-N | Tweet format (texto puro ou texto + imagem) | Python/Pillow (make_tweet_slides.py) |

---

## REGRA CRITICA: GERACAO DE IMAGENS

- **SEMPRE** usar NanoBanana 2 (google/gemini-3.1-flash-lite-preview)
- **NUNCA** usar GPT, DALL-E ou qualquer outro modelo para gerar imagens
- API key Gemini em auth-profiles.json (profile google:manual) e 1Password

---

## SLIDE 1 - CAPA

### Especificacoes visuais EXATAS (ver imagem de referencia aprovada)

- Proporcao: 4:5 (1080x1350)
- METADE SUPERIOR (~60%): foto da Dra. Daniely
  - Semblante SERIO, bracos cruzados
  - Blazer escuro (NUNCA jaleco, NUNCA sorrindo)
  - Fundo de laboratorio/clinica com frascos e iluminacao quente
  - Capsulas douradas em circulo no canto superior direito
- DIVISOR: linha dourada horizontal fina + simbolo V da marca no centro
- METADE INFERIOR (~40%): headline
  - Fonte: Montserrat Black
  - Cores: branco + dourado #9F8844
  - Texto centralizado
  - Palavras-chave em dourado (ex: MAGNESIO, NORMAL, DISCORDA)
- RODAPE: "Dra. Daniely Freitas | CRM-BA 27588" (pequeno, discreto)

### Regras da headline
- Frase de IMPACTO (scroll-stop), NUNCA explicativa
- Regra: "se comecar com explicacao, perde retencao"
- BOM: "SEU MAGNESIO ESTA 'NORMAL' MAS SEU CORPO DISCORDA."
- BOM: "ESSA E A BEBIDA MAIS PREJUDICIAL QUE EXISTE."
- RUIM: "O magnesio serico representa apenas 1% do total"

---

## SLIDE 2 - PAPER CIENTIFICO

### Formato tweet + screenshot PubMed
- Fundo preto #000
- Avatar + nome + handle no topo (mesmo padrao dos slides tweet)
- Texto em cor unica #c8c8c8
- Screenshot do PubMed centralizado no espaco abaixo do texto
- Screenshot deve incluir: header NIH, PubMed logo, titulo completo do paper
- Imagem respeita margens laterais, com border-radius

---

## SLIDES 3+ - FORMATO TWEET

### DOIS TIPOS DE SLIDE TWEET:

#### TIPO A - Tweet com foto/imagem
Referencia: slides 1/15 e 4/15 do modelo Tallis Gomes

Layout:
```
+----------------------------------+
|                                  |
| (avatar) Nome Verificado         |  <- topo
|          @handle                 |
|                                  |
| Texto do slide em branco.        |
| Fonte ~38px, espacamento         |
| generoso entre paragrafos.       |
|                                  |
| Gancho para o proximo ->         |
|                                  |
| +------------------------------+|
| |                              ||  <- foto(s) na parte inferior
| |    IMAGEM / SCREENSHOT       ||     colada nas laterais
| |    border-radius 12px        ||     ~40-45% da altura do slide
| |                              ||
| +------------------------------+|
|                                  |
+----------------------------------+
```

Regras:
- Texto no TOPO com avatar
- Imagem(s) na parte INFERIOR
- Imagem ocupa toda a largura (respeitando margens laterais 48px)
- Se 2 imagens lado a lado: gap de 8px entre elas
- Border-radius: 12px nas imagens
- Texto e imagem distribuidos proporcionalmente (sem area vazia grande)

#### TIPO B - Tweet sem foto (texto puro)
Referencia: slide 3/15 do modelo Tallis Gomes

Layout:
```
+----------------------------------+
|                                  |
|                                  |
|                                  |  <- respiro superior
|                                  |
| (avatar) Nome Verificado         |
|          @handle                 |  <- CENTRALIZADO
|                                  |     VERTICALMENTE
| Texto do slide em branco.        |
| Fonte ~38px, espacamento         |
| generoso entre paragrafos.       |
|                                  |
|                                  |
|                                  |  <- respiro inferior
|                                  |
+----------------------------------+
```

Regras:
- TODO o bloco (avatar + texto) centralizado VERTICALMENTE
- Respiro equilibrado em cima e embaixo
- **NUNCA** texto colado no topo com area preta vazia embaixo

### ESPECIFICACOES TECNICAS DOS SLIDES TWEET

| Elemento | Valor |
|----------|-------|
| Tamanho | 1080 x 1350 px (4:5) |
| Fundo | preto #000000 |
| Margens laterais | 48-64 px |
| Avatar | 72px circular |
| Nome | bold, branco, ~32px |
| Selo verificado | circulo azul #1D9BF0 com checkmark branco, 24px |
| Handle | regular, cinza #71767B, ~20px |
| Gap avatar-texto | 32px |
| Texto corpo | regular, branco #c8c8c8, ~38px, line-height 1.45x |
| Gap entre paragrafos | ~40px (linha em branco visual) |
| Cor do texto | UMA COR SO (#c8c8c8) - sem bold, sem destaques, sem dourado |
| Imagens | border-radius 12px, respeitam margens laterais |

### REGRAS DE CONTEUDO

1. Texto CONVERSACIONAL, nao tecnico
2. Frases CURTAS e impactantes
3. CADA slide termina com frase de gancho para o proximo
4. UM conceito por slide
5. Apos ponto, SEMPRE letra maiuscula
6. Ultimo slide: CTA com botao dourado (gradient #d4a84b -> #b8922e)

### EXEMPLOS DE GANCHOS
- "E nao e so isso..."
- "Mas o que isso causa no seu corpo? ->"
- "E se existisse um jeito de investigar isso de verdade? ->"
- "Resultado nao e sorte. E precisao clinica. ->"
- "Quer saber o que realmente funciona? ->"

---

## PERFIL CONFIGURADO

### Dra. Daniely Freitas
- Nome: Dra. Daniely Freitas
- Handle: @dradaniely.freitas
- Verificado: sim (selo azul)
- CRM: BA 27588
- Idade: 43 anos
- Visual na capa: blazer escuro, blusa preta, colar dourado, cabelo loiro ondulado
- NUNCA: jaleco, sorriso exagerado
- Avatar: foto de perfil do Instagram (blazer branco + blusa preta)
- Cor da marca: dourado #9F8844

### Fotos de referencia
- VPS: /root/.openclaw/workspace/fotos_dra/
- Local: C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Banco de imagens\Dany\
- Logo: C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Logo\

---

## SCRIPT DE GERACAO

```bash
python3 scripts/make_tweet_slides.py \
  --config slides.json \
  --avatar avatar.png \
  --out ./output \
  --name "Dra Daniely Freitas" \
  --handle "@dradaniely.freitas"
```

---

## CHECKLIST DE QUALIDADE (OBRIGATORIO antes de entregar)

### Copy (etapa 1)
- [ ] Headline da capa e de IMPACTO (scroll-stop)
- [ ] Texto conversacional, nao tecnico
- [ ] Frases curtas
- [ ] Gancho no final de cada slide
- [ ] Um conceito por slide
- [ ] Apos ponto, letra maiuscula
- [ ] CTA no ultimo slide

### Imagens (etapa 2)
- [ ] Proporcao 4:5 (1080x1350) em TODOS os slides
- [ ] Capa: foto gerada pelo NanoBanana 2 (NAO GPT/DALL-E)
- [ ] Capa: Dra. com semblante serio, blazer escuro, fundo contextual
- [ ] Capa: headline de impacto em Montserrat Black (branco + dourado)
- [ ] Slide 2: screenshot PubMed com titulo completo (se houver pesquisa)
- [ ] Slides tweet: texto de cor unica #c8c8c8, mesmo tamanho, sem destaques
- [ ] Slides tweet sem foto: bloco centralizado verticalmente
- [ ] Slides tweet com foto: texto no topo, foto na parte inferior
- [ ] Nenhum slide com texto colado no topo e area vazia embaixo
- [ ] Margens laterais respeitadas (48-64px)
- [ ] Imagens com border-radius 12px

## TROUBLESHOOTING

- Imagem inconsistente na capa: verificar se usa NanoBanana 2 em auth-profiles.json
- Rosto diferente da Dra.: enviar 3-6 fotos de referencia junto com o prompt
- Texto cortado: verificar margens e tamanho da fonte
- PubMed bloqueando: user-agent Safari, URL direta do artigo
- Espaco vazio: centralizar (tipo B) ou adicionar imagem (tipo A)
- API key Gemini invalida: verificar 1Password item "Gemini API Key"
