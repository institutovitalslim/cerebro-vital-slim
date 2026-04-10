# CONTEXT_CANON.md

Mapa canônico de onde buscar a verdade por domínio operacional.

## 1. Execução
- Regra principal: `OPERATING_RULES.md`
- Checklist geral: `EXECUTION_CHECKLIST.md`
- Comportamento do workspace: `AGENTS.md`

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

## 5. Regra de precedência
Quando houver conflito, usar nesta ordem:
1. arquivo operacional do fluxo
2. checklist operacional específico
3. `OPERATING_RULES.md`
4. `AGENTS.md`
5. memória longa (`MEMORY.md`)
6. memória diária (`memory/YYYY-MM-DD.md`)
7. contexto recente de conversa
