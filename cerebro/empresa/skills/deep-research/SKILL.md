---
name: deep-research-protocol
description: >
  Protocolo estruturado de pesquisa profunda com múltiplas fontes, síntese e relatório
  acionável em HTML. Use quando o Tiaro pedir pesquisa detalhada, análise de mercado, investigação
  de tema ou benchmarking. Acionar quando: "pesquisa sobre", "deep research", "investiga",
  "analisa o mercado de", "benchmark", "quero entender melhor", "pesquisa profunda",
  "me dá um overview de", "análise de concorrentes". Para pesquisas complexas (>30min),
  spawnar como sub-agent.
metadata:
  author: amora-cos (adaptado para IVS)
  version: 1.1.0
  domain: shared
  owner: main
---

# Deep Research Protocol — Skill de Pesquisa Profunda

## O que é

Protocolo estruturado para pesquisa profunda. Combina múltiplas fontes, sintetiza findings, e entrega relatório acionável **em formato HTML**.

## Formato de Saída Padrão: HTML

**IMPORTANTE**: O output padrão é sempre HTML. Salvar como `.html` e enviar ao usuário.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>[Tema] — Deep Research</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.7; }
  h1 { border-bottom: 3px solid #d4a84b; padding-bottom: 12px; }
  h2 { color: #2c3e50; margin-top: 32px; border-left: 4px solid #d4a84b; padding-left: 12px; }
  h3 { color: #34495e; }
  .tldr { background: #f8f9fa; border-left: 4px solid #d4a84b; padding: 16px 20px; margin: 20px 0; border-radius: 4px; }
  .finding { background: #fff; border: 1px solid #e0e0e0; padding: 16px; margin: 12px 0; border-radius: 8px; }
  .finding-source { color: #666; font-size: 0.85em; }
  .recommendation { background: #e8f5e9; border-left: 4px solid #2e7d32; padding: 16px 20px; margin: 20px 0; border-radius: 4px; }
  .meta { color: #888; font-size: 0.9em; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; }
  th, td { border: 1px solid #ddd; padding: 10px 14px; text-align: left; }
  th { background: #f5f5f5; font-weight: 600; }
  a { color: #1a73e8; }
  .tag { display: inline-block; background: #e3f2fd; color: #1565c0; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 4px; }
  .tag.opinion { background: #fff3e0; color: #e65100; }
  .tag.signal { background: #f3e5f5; color: #7b1fa2; }
</style>
</head>
<body>
<!-- Conteúdo do relatório aqui -->
</body>
</html>
```

## Protocolo de Pesquisa

### 1. Enquadramento (2 min)
- Qual a pergunta exata?
- Qual decisão essa pesquisa vai informar?
- Qual nível de profundidade? (Quick scan vs Deep dive)

### 2. Coleta Multi-fonte

**Fontes primárias (usar nesta ordem):**
1. `web_search` — busca geral (Brave)
2. `web_fetch` — extrair conteúdo de URLs relevantes
3. **Perplexity** — busca com AI-powered answers e citações
   ```bash
   export OP_SERVICE_ACCOUNT_TOKEN=$(grep OP_SERVICE_ACCOUNT_TOKEN /root/.openclaw/.op.service-account.env | cut -d= -f2-)
   PERPLEXITY_API_KEY=$(op item get "Perplexity API" --vault "openclaw" --field credential --reveal 2>/dev/null)
   node /root/.openclaw/workspace/skills/perplexity/scripts/search.mjs "query"
   ```
4. Knowledge Base — memória do OpenClaw (`memory_search`)

**Fontes especializadas:**
- **PubMed** (https://pubmed.ncbi.nlm.nih.gov/) — fonte obrigatória para qualquer pesquisa científica. Sempre consultar primeiro.
- **Google Scholar** (https://scholar.google.com/) — complementar ao PubMed
- **PMC** (https://www.ncbi.nlm.nih.gov/pmc/) — artigos com texto completo gratuito
- Reddit/HackerNews — opinião de comunidade técnica
- Twitter/X — sinais em tempo real
- YouTube — análises longas e tutoriais
- GitHub — repos e projetos open source

### 3. Síntese

Para cada fonte, classificar com tags:
- <span class="tag">Fato</span> — o que é confirmável
- <span class="tag opinion">Opinião</span> — o que é interpretação
- <span class="tag signal">Sinal</span> — o que sugere tendência

### 4. Relatório HTML

**Estrutura padrão do HTML:**

```
<h1>[Tema] — Deep Research</h1>
<p class="meta">Data: DD/MM/YYYY | Nível: [Quick/Standard/Deep] | Fontes: N</p>

<div class="tldr">
  <h2>TL;DR</h2>
  <ul>3-5 bullets principais</ul>
</div>

<h2>Contexto</h2>
<p>Por que estamos pesquisando isso</p>

<h2>Findings</h2>
<div class="finding">
  <h3>Subtema 1</h3>
  <p>Finding + análise</p>
  <p class="finding-source">Fonte: <a href="url">título</a></p>
</div>

<h2>Análise</h2>
<p>Cruzamento dos findings, padrões identificados</p>

<div class="recommendation">
  <h2>Recomendação</h2>
  <p>O que fazer com essa informação</p>
</div>

<h2>Fontes</h2>
<ol>Lista de URLs consultadas com títulos</ol>
```

### 5. Salvamento
- Salvar HTML em `/root/.openclaw/workspace/research/YYYY-MM-DD-[slug].html`
- Salvar cópia em memória: `memory/research/YYYY-MM-DD-[slug].md` (versão resumida)
- Se relevante pra Knowledge Base → ingestar

### 6. Entrega
- Enviar o arquivo HTML ao usuário (via Telegram como documento ou link)
- Para visualização local, o HTML é auto-contido (CSS inline, sem dependências externas)

## Níveis de Profundidade

| Nível | Tempo | Fontes | Output |
|-------|-------|--------|--------|
| Quick scan | 5-10 min | 3-5 URLs | HTML 1 página |
| Standard | 15-30 min | 8-12 URLs | HTML 2-3 páginas |
| Deep dive | 30-60 min | 15-20+ URLs | HTML 4-6 páginas |

## Quando spawnar sub-agent

Se a pesquisa é deep dive (>30min) ou Tiaro quer continuar trabalhando enquanto pesquisa roda:
- Spawnar via `sessions_spawn` com task detalhada
- Sub-agent entrega relatório HTML quando pronto
- Clara faz review e envia pro Tiaro

## Vieses a evitar

- **Confirmation bias** — buscar contra-argumentos ativamente
- **Recency bias** — verificar se tendências são reais ou hype
- **Survivorship bias** — buscar casos de fracasso, não só sucesso
- **Authority bias** — expert disse ≠ é verdade

## Contexto IVS (Instituto Vital Slim)

Para pesquisas no domínio médico/saúde:
- **REGRA OBRIGATÓRIA**: sempre consultar PubMed (https://pubmed.ncbi.nlm.nih.gov/) como fonte primária para qualquer pesquisa científica
- Priorizar revisões sistemáticas e meta-análises
- Complementar com Google Scholar e PMC para artigos com texto completo
- Usar NotebookLM para análise de papers
- Compliance CFM/CRM-BA: não fazer afirmações que violem regras do conselho
- Focar em evidências de nível A e B
- Sempre citar DOI e PMID quando disponível
