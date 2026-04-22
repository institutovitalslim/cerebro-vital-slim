# CONTEXT_CANON.md

Mapa canônico de onde buscar a verdade por domínio operacional.

## 1. Execução
- Regra principal: `OPERATING_RULES.md`
- Checklist geral: `EXECUTION_CHECKLIST.md`
- Comportamento do workspace: `AGENTS.md`
- Arquitetura do cérebro: `cerebro/BRAIN_ARCHITECTURE.md`
- Política de compactação de memória: `cerebro/memory-compaction-policy.md`

## 2. Bridge / Clara / WhatsApp
- Regras de follow-up: `/root/.openclaw/workspace/ops/zapi_bridge/FOLLOWUP_CHECKLIST.md`
- Exclusões: `/root/.openclaw/workspace/ops/zapi_bridge/clara_exclusions.json`
- Overrides/controle: `/root/.openclaw/workspace/ops/zapi_bridge/clara_control_state.json`
- Modelo/config da bridge: `/root/.openclaw/workspace/ops/zapi_bridge/zapi_bridge.env`
- Script principal: `/root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge.py`

## 3. LLMs em produção
- Regras: `OPERATING_RULES.md`
- Auditoria: `/root/.openclaw/workspace/ops/llm-audit/`
- Relatório atual: `/root/.openclaw/workspace/ops/llm-audit/latest_report_v3.json`

## 4. Skills críticas
### tweet-carrossel
- Fonte de verdade: `MEMORY.md` + skill canônica no diretório da skill

### omie-boletos
- Fonte de verdade: `MEMORY.md`
- Script: `/root/.openclaw/workspace/skills/omie-boletos/scripts/omie_boletos.py`

### agenda-diaria-whatsapp
- Fonte de verdade: `MEMORY.md`
- Skill: `/root/.openclaw/workspace/skills/agenda-diaria-whatsapp/`

## 5. Conhecimento único entre tópicos
Em grupos com múltiplos tópicos, todos os tópicos devem operar sobre um **conhecimento único e transversal**.
Nenhuma integração, decisão, regra ou fluxo canônico deve ficar “preso” ao tópico em que apareceu primeiro.
O tópico é a interface da conversa; a verdade operacional deve permanecer na memória e no cérebro canônicos.

## 6. Regra de precedência
Quando houver conflito, usar nesta ordem:
1. instrução direta do usuário
2. regras de segurança e sistema
3. arquivo operacional do fluxo
4. checklist operacional específico
5. arquivo canônico do domínio
6. `OPERATING_RULES.md`
7. `CONTEXT_CANON.md`
8. `cerebro/execution-principles.md`
9. `cerebro/success-criteria.md`
10. `AGENTS.md`
11. memória longa (`MEMORY.md`)
12. memória diária (`memory/YYYY-MM-DD.md`)
13. contexto recente de conversa
