---
name: validacao-qa
description: >
  Bateria de testes para validar pipeline de carrossel da Clara. Roda 5 grupos de
  validacao (arquivos oficiais, scripts unitarios, integracao, end-to-end, CLAUDE.md).
  Ultima execucao: 2026-04-20 com 78/78 passing + E2E completo (10 slides entregues).
metadata:
  version: 1.0.0
  domain: qa
---

# Validacao QA — Pipeline de Carrossel

## Quando rodar
- Apos qualquer mudanca em scripts da skill tweet-carrossel, prompt-imagens ou memoria-cientifica
- Antes de colocar a Clara para gerar carrossel em producao
- Toda sessao de debugging deve terminar com a suite

## Comandos

### Suite completa (78 testes + E2E)
\`\`\`bash
export GOOGLE_API_KEY=\$GOOGLE_API_KEY
export TELEGRAM_BOT_TOKEN=\$TELEGRAM_BOT_TOKEN
python3 /root/.openclaw/workspace/skills/validacao-qa/scripts/validation_tests.py --send-telegram
\`\`\`

### So os testes rapidos (sem E2E)
\`\`\`bash
python3 /root/.openclaw/workspace/skills/validacao-qa/scripts/validation_tests.py --quick
\`\`\`

### E2E real (gera carrossel completo sobre tema novo e envia no Telegram)
\`\`\`bash
python3 /root/.openclaw/workspace/skills/validacao-qa/scripts/e2e_real_test.py
\`\`\`

## Cobertura

### Grupo 1 — Arquivos (49 checks)
- SKILL.md dos 3 skills em 2 locais (6)
- 26 scripts oficiais em 2 locais
- CLAUDE.md com 7 PROIBICOES (2)
- /root/make_cover.py sincronizado (2)
- Acervo fotos Dra + avatar + logs (5)

### Grupo 2 — Unidades (6 checks)
- make_cover strip ? e !
- memory_search encontra creatina
- memory_search lista topicos
- photo_selector retorna match
- capture_pubmed gera imagem
- build_prompt 7 dimensoes

### Grupo 3 — Integracao (2 checks)
- memory_store armazena
- memory_search encontra logo apos

### Grupo 4 — End-to-end (4 checks)
- compose_cover JPEG
- dimensoes 1080x1350
- envio Telegram
- capture_pubmed com arquivo real

### Grupo 5 — CLAUDE.md forcing functions (14 checks)
- PROIBICOES 1-7 presentes
- Regras-chave explicitas (ingles, texto vs JPEG, ETAPA 0, etc)

### E2E Real (adicional — e2e_real_test.py)
- 8 passos simulando cenario real da Clara
- Carrossel completo sobre tema novo ("Creatina mulher 40+")
- Entrega 10 JPEGs via Telegram

## Historico

### 2026-04-20 18:05 — 78/78 passing + E2E completo
- 49 checks de arquivos: OK
- 6 testes unitarios: OK
- 2 integracoes: OK
- 4 E2E: OK
- 14 CLAUDE.md: OK
- Carrossel real: 10 slides entregues, 8/8 steps

## Relatorios
JSON detalhado salvo em:
\`/root/cerebro-vital-slim/cerebro/empresa/conhecimento/logs/validation_YYYY-MM-DD_HHMMSS.json\`
