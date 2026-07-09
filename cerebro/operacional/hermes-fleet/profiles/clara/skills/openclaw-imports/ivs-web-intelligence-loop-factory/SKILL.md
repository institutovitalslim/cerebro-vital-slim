---
name: ivs-web-intelligence-loop-factory
description: Use when an IVS agent needs to turn public web pages, competitor pages, social references, SEO/AEO gaps, content ideas, finance/revenue signals, repo/skill patterns, or handoff drift into a governed operational loop with evidence and human gates.
---

# IVS Web Intelligence Loop Factory

## Overview
Transforma pesquisa pública em loop operacional IVS: objetivo + URLs públicas -> relatório + estado do loop + evidência + próximos testes + gates.

Base: `ivs-crawl4ai-sandbox`, `ivs-loop-factory`, `ivs-agent-capability-registry`, `ivs-video-intake` e `rapidapi-social-learning` quando a fonte for mídia social.

## Quando usar

| Loop | Uso IVS |
|---|---|
| `revenue` | leads parados, follow-up perdido, Clara sem resposta, pré-consulta travada |
| `content` | referências públicas -> hooks, ângulos, variações para João |
| `seo-aeo` | site/blog/concorrentes -> intent, gaps, updates, rank, AI answer visibility |
| `outbound` | pesquisa de parceiros/listas públicas; drafts apenas até aprovação |
| `finance` | gasto duplicado, assinatura inútil, renovação, vazamento de margem |
| `repo-skill` | detectar processos que devem virar skill, auditar skills/scripts |
| `continuation` | manter contexto entre agentes/crons, reduzir drift e falsa conclusão |

Não use para login, paciente, lead individual, PII, paywall, DRM, proxy, stealth, publicação externa, envio de mensagem ou escrita em sistemas sensíveis.

## Comando rápido

```bash
python3 scripts/run_web_intelligence_loop.py \
  --loop-type seo-aeo \
  --goal "auditar oportunidade SEO/AEO IVS" \
  --target https://blog.institutovitalslim.com.br/ \
  --out /tmp/ivs-web-loop
```

## Critério de aceite
Antes de reportar `DONE`: `report.md`, `loop-state.json` e, quando houver web, `crawl/summary.json`; relatório com gates; nenhuma ação externa tomada.

## Human gates
Parar antes de envio externo, publicação, alteração de site/anúncio/orçamento/credencial/permissão, escrita em Omie/QuarkClinic/financeiro, ingestão canônica no cérebro/GBrain, uso de login/cookies/paywall/PII.

## Output esperado

```text
Status:
Loop:
Stop reason:
Evidence:
Applications:
Human gates:
Next action:
```
