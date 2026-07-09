---
name: ivs-crawl4ai-sandbox
description: Use when an IVS agent needs to extract, audit, summarize, or benchmark public web pages with governed Crawl4AI/scraping, especially competitor pages, IVS blog/site, SEO, public tool docs, or content research without login, PII, leads, patients, proxy, stealth, or bypass.
---

# IVS Crawl4AI Sandbox

## Objetivo
Usar o piloto local governado de Crawl4AI para transformar páginas públicas em Markdown/JSON/HTML, com guardrails IVS.

## Quando usar
Use para pesquisa pública de concorrentes, auditoria de blog/site IVS, documentação pública de ferramentas, benchmark SEO/local e briefings a partir de páginas públicas.

Não use para login, paywall, portal, área admin, WhatsApp, checkout, paciente, lead, prontuário, CRM, PII, scraping autenticado, proxy, stealth, bypass anti-bot ou DRM.

## Comando canônico

```bash
cd /opt/ivs/ivs-crawl4ai-sandbox
uv run python -m ivs_crawl4ai_sandbox.runner --out runs/$(date +%Y%m%d-%H%M%S)
```

Com URLs específicas:

```bash
cd /opt/ivs/ivs-crawl4ai-sandbox
uv run python -m ivs_crawl4ai_sandbox.runner \
  --target https://institutovitalslim.com.br/ \
  --target https://blog.institutovitalslim.com.br/ \
  --out runs/$(date +%Y%m%d-%H%M%S)
```

## Critério de aceite
Antes de reportar DONE: testes passam; `summary.json` e `summary.html` existem; cada página tem `.md`, `.json`, `.html`; relatório explicita engine/fallback; alvo bloqueado não vira sucesso.

## Evidência real do piloto inicial

```text
/opt/ivs/ivs-crawl4ai-sandbox/RELATORIO-PILOTO-20260709.md
/opt/ivs/ivs-crawl4ai-sandbox/runs/20260709-061826-crawl4ai/summary.json
/opt/ivs/ivs-crawl4ai-sandbox/runs/20260709-061826-crawl4ai/summary.html
```

Resultado: 5 testes passaram; 3 páginas públicas extraídas com engine crawl4ai; sem API pública exposta.

## Governança
- Execução local/loopback por padrão.
- Não agendar cron recorrente sem Maria/Tiaro.
- Não publicar nem enviar mensagem externa.
- Não escrever no cérebro/GBrain automaticamente; consolidar regra permanente via Graphify/RC-25.
- Sanitizar tokens/query strings antes de qualquer relatório.

## Erros comuns

| Erro | Correção |
|---|---|
| Usar URL com token | sanitize primeiro; nunca registrar token |
| Scrapar portal/login | bloquear; pedir gate explícito se for operação interna governada |
| Chamar fallback de sucesso total | reportar engine e fallback claramente |
| Colocar resultado direto no cérebro | gerar relatório local e submeter para validação |
| Rodar em massa | começar com poucos alvos e allowlist |
