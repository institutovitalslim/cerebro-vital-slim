---
name: tweet-carrossel
description: >
  Gera carrosseis completos para o Instagram no formato tweet (estilo X/Twitter).
  Inclui: capa (NanoBanana 2 + Pillow), slide 2 com paper cientifico, e slides 3+ em formato tweet via script Python.
  Use quando: "carrossel", "criar carrossel", "formato tweet", "carrossel preto", "slides instagram",
  "carrossel cientifico", "montar carrossel", "criar slides".
  SEMPRE usar NanoBanana 2 (google/gemini-3.1-flash-lite-preview) para gerar imagens.
metadata:
  version: 2.0.0
  domain: marketing
  owner: main
---

# Tweet Carrossel - Geracao Completa de Carrosseis Instagram

## Estrutura Obrigatoria do Carrossel

| Slide | Tipo | Como gerar | Modelo |
|-------|------|-----------|--------|
| 1 | **Capa** - foto da Dra. + headline impactante | Abordagem hibrida: NanoBanana 2 (foto) + Pillow (texto) | google/gemini-3.1-flash-lite-preview |
| 2 | **Paper cientifico** - texto tweet + screenshot PubMed | Script Python (Chromium headless - screenshot HTML) | - |
| 3+ | **Tweet format** - texto puro centralizado | Script Python (make_tweet_slides.py) | - |

## REGRA FUNDAMENTAL: Geracao de Imagens

**SEMPRE usar o NanoBanana 2** (google/gemini-3.1-flash-lite-preview) para qualquer geracao de imagem.
**NUNCA usar GPT/DALL-E** para gerar imagens dos carrosseis.
**NUNCA usar o modelo principal** (GPT-5.4 ou Claude) para gerar imagens.

A API key do Gemini esta em:
- auth-profiles.json: profile google:manual
- 1Password: item "Gemini API Key" no vault "openclaw"

---

## SLIDE 1 - CAPA

### Padrao visual obrigatorio

- **Proporcao**: 4:5 (1080x1350)
- **Foto da Dra. Daniely**: semblante SERIO, bracos cruzados, blazer escuro (NUNCA jaleco)
- **Fundo**: laboratorio/clinica com frascos, iluminacao quente
- **Capsulas douradas**: no canto superior direito, em circulo com borda gold
- **Linha divisoria**: dourada, horizontal, com simbolo V da marca no centro
- **Texto**: Montserrat Black, duas cores (branco + dourado #9F8844)
- **Headline**: frase de IMPACTO que causa scroll-stop (NAO explicativa)
- **Rodape**: "Dra. Daniely Freitas | CRM-BA 27588"

### Abordagem hibrida (2 passos)

**Passo 1 - Gerar foto via NanoBanana 2:**

Prompt base para a foto:
"Professional editorial portrait of a Brazilian female doctor, 43 years old, blonde wavy shoulder-length hair, round face, brown eyes, serious determined expression, closed lips, wearing dark navy blazer over black blouse, gold pendant necklace, arms crossed, waist-up framing, modern laboratory background with glass bottles and warm lighting, golden supplement capsules in top-right corner circle, premium editorial medical photography, 4:5 aspect ratio, photorealistic"

Enviar junto 3-6 fotos de referencia da Dra. Daniely de:
/root/.openclaw/workspace/fotos_dra/

**Passo 2 - Adicionar texto via Pillow:**
- Montserrat Black para headline
- Branco (#FFFFFF) para texto principal
- Dourado (#9F8844) para palavras de destaque
- Linha dourada + V como divisor entre foto e texto

### Regras da headline
- Frase de IMPACTO, nao explicativa
- Gerar curiosidade (scroll-stop)
- Exemplo BOM: "SEU MAGNESIO ESTA 'NORMAL' MAS SEU CORPO DISCORDA."
- Exemplo RUIM: "Magnesio serico representa apenas 1% do magnesio total"
- Regra: "se comecar com explicacao, perde retencao. Se comecar com percepcao de valor, ganha atencao."

---

## SLIDE 2 - PAPER CIENTIFICO (quando houver pesquisa)

### Padrao visual

- **Formato**: tweet (avatar + nome + handle + texto)
- **Fundo**: preto #000
- **Texto**: cor unica #c8c8c8, mesmo tamanho do nome do perfil (~28-32px)
- **Imagem do paper**: screenshot do PubMed (capa do artigo com titulo)
- **Imagem respeita margens** laterais do slide, com border-radius 10px
- **Imagem centralizada** no espaco disponivel abaixo do texto

### Como gerar

Renderizar via HTML + Chromium headless na VPS:
chromium --headless --disable-gpu --no-sandbox --screenshot=slide2.png --window-size=1080,1350 file:///root/slide2.html

### Regras do screenshot PubMed
- Incluir: header NIH + PubMed logo + barra de busca + referencia do journal + titulo completo do paper
- Screenshot via Chromium headless da URL do PubMed do artigo
- Redimensionar para 1080px de largura
- Usar user-agent de Safari/Mac para evitar bloqueio
- Acessar a URL direta do artigo (ex: https://pubmed.ncbi.nlm.nih.gov/PMID/)

---

## SLIDES 3+ - FORMATO TWEET

### Padrao visual obrigatorio

- **Tamanho**: 1080x1350 (4:5)
- **Fundo**: preto #000000
- **Texto**: cor UNICA #c8c8c8, MESMO tamanho, SEM bold, SEM destaques coloridos
- **Fonte**: mesmo tamanho do nome do perfil (~28-34px)
- **Avatar**: foto de perfil real da Dra. (circular, ~56-72px)
- **Nome**: "Dra. Daniely Freitas" + selo verificado azul
- **Handle**: @dradaniely.freitas em cinza
- **Margens laterais**: 64px

### Regra de posicionamento

| Cenario | Posicionamento |
|---------|---------------|
| Texto curto SEM imagem | Centralizar verticalmente TODO o bloco (header + texto) |
| Texto + imagem do paper | Texto no topo, imagem centralizada no espaco restante |
| **NUNCA** | Texto colado no topo com area preta vazia embaixo |

### Regras de conteudo

1. **Texto conversacional**, NAO tecnico
2. **Frases curtas** e impactantes (fator "uau, eu nao sabia disso")
3. **Cada slide termina com frase de gancho** para reter no proximo
4. **Um conceito por slide** - nao sobrecarregar
5. **Apos ponto, letra maiuscula**
6. **Ultimo slide**: CTA com botao dourado (#d4a84b para #b8922e gradient)

### Exemplos de ganchos
- "E nao e so isso..."
- "Mas o que isso causa no seu corpo? ->"
- "E se existisse um jeito de investigar isso de verdade? ->"
- "Resultado nao e sorte. E precisao clinica. ->"

### Script de geracao

python3 scripts/make_tweet_slides.py --config slides.json --avatar avatar.png --out ./output --name "Dra Daniely Freitas" --handle "@dradaniely.freitas"

---

## Perfil Configurado

### Dra. Daniely Freitas
- **Nome**: Dra. Daniely Freitas
- **Handle**: @dradaniely.freitas
- **Verificado**: sim (selo azul)
- **CRM**: BA 27588
- **Idade**: 43 anos
- **Visual**: blazer escuro, blusa preta, colar dourado, cabelo loiro ondulado
- **NUNCA**: jaleco, sorriso exagerado
- **Avatar**: foto de perfil do Instagram (blazer branco + blusa preta)
- **Cor da marca**: dourado #9F8844

### Fotos de referencia
- VPS: /root/.openclaw/workspace/fotos_dra/
- Local: C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Banco de imagens\Dany\
- Logo: C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Logo\

---

## Checklist de Qualidade (OBRIGATORIO antes de entregar)

- [ ] Proporcao 4:5 (1080x1350) em TODOS os slides
- [ ] Capa: Dra. com semblante serio, blazer escuro, fundo contextual
- [ ] Capa: headline de impacto (scroll-stop), nao explicativa
- [ ] Capa: imagem gerada pelo NanoBanana 2 (NAO GPT/DALL-E)
- [ ] Slide 2: screenshot PubMed com titulo completo do paper (se houver pesquisa)
- [ ] Slides tweet: texto de cor unica, mesmo tamanho, centralizado
- [ ] Slides tweet: gancho no final de cada slide
- [ ] Slides tweet: texto curto sem imagem = centralizado verticalmente
- [ ] CTA no ultimo slide com botao dourado
- [ ] Nenhum slide com texto colado no topo e area vazia embaixo
- [ ] Fontes corretas (Montserrat na capa, DejaVu nos tweets)
- [ ] Margens respeitadas (64px laterais)

## Troubleshooting

- **Imagem inconsistente na capa**: garantir que esta usando NanoBanana 2 (google/gemini-3.1-flash-lite-preview), nao GPT. Verificar auth-profiles.json.
- **Rosto diferente da Dra.**: enviar 3-6 fotos de referencia junto com o prompt ao NanoBanana 2.
- **Texto cortado**: verificar margens laterais (64px) e tamanho da fonte.
- **PubMed bloqueando**: usar user-agent de Safari e acessar a URL direta do artigo.
- **Espaco vazio**: centralizar texto OU adicionar imagem do paper para preencher.
- **API key Gemini invalida**: verificar em 1Password item "Gemini API Key" e atualizar auth-profiles.json.
