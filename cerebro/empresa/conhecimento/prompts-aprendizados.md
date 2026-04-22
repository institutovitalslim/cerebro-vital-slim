# Aprendizados de Prompts - Clara

Arquivo append-only onde Clara registra aprendizados sobre prompts que funcionaram
muito bem ou falharam para NanoBanana 2 Pro / Gemini 3 Pro Image.

## Formato de cada entrada:
- **Data**: YYYY-MM-DD
- **Objetivo**: o que queria criar
- **Prompt que funcionou** (ou falhou): trecho-chave
- **Aprendizado**: insight para reuso

---

## Aprendizados documentados

### 2026-04-17 — Template inicial

**Observacao geral**:
- Prompts em ingles renderizam melhor termos tecnicos (lens, lighting, ISO) no NanoBanana 2 Pro
- Descricoes em portugues funcionam bem para elementos culturais/locais (ex: "consultorio brasileiro")
- Mesclar os dois eh aceitavel

**Camera + lente vencedoras para Dra. Daniely**:
- Canon R5 Mark II + 85mm f/1.4 f2.0 = retrato autoridade com bokeh suave ideal
- Evitar 50mm f/1.2 (distorce levemente o rosto em close)

**Iluminacao aprovada para capa de carrossel**:
- "Luz lateral suave de estudio, temperatura quente (3200K), contraste moderado"
- Reproduz o look das fotos reais aprovadas

**Estilo que funciona para capa cientifica**:
- "Editorial contemporaneo, realista, com profundidade de campo curta"
- Evitar "fashion high contrast" (pouco medico)


### 2026-04-20 — Carrossel Intestino (sessao completa de fixes)

Ver documento completo: logs/LICOES_SESSAO_2026-04-20.md

**Fixes aplicados em producao**:
- memory_store: try/except OSError em read_or_text
- make_cover: strip de ? e ! (chr(63) e chr(33))
- /root/make_cover.py: sync com skill obrigatorio
- capture_pubmed: staging /root/chromium_tmp/ (sem dot), profile /root/chromium_prof_<id>/
- capture_pubmed: sintetica com validacao relaxada (so tamanho)
- regen v2: crop adaptativo (sintetica 1200x900 full / real 1200x1800 top 720)
- fetch_instagram: RapidAPI cascata de 2 APIs
- zapi_clara_bridge: _split_message_for_zapi (chunks 3500 com delay)

**Regras de prompt validadas**:
- Capa com 3 pain points + promessa: ANSIEDADE? ACNE? OBESIDADE? UMA CAUSA E MUITOS SINTOMAS
- Destaques dourados nos pain points (nao nas respostas)
- Fundo 3D anatomico LATERALIZADO (nao atras da Dra)
- Blur radius 8 + brightness 0.35-0.55 em fundos Unsplash
- Sempre strip ? ! em destaques do make_cover
