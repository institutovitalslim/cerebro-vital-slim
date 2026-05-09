# RC-25 — Novas skills IVS-first baseadas na análise OpenFang

## Decisão
Tiaro autorizou seguir com implementação das novas skills baseadas na análise do agente/Agent OS. A referência OpenFang foi usada como inspiração funcional, sem cópia de código.

## Skills criadas
1. `ivs-agent-capability-registry`
   - Inventaria agentes, skills, subagentes, workflows e riscos.
   - Script: `scripts/capability_registry.py`.
   - Modo: read-only.

2. `ivs-agent-handoff-guard`
   - Gera pacotes seguros de handoff entre Maria, Clara, João, Pedro e conselhos.
   - Script: `scripts/handoff_packet.py`.
   - Modo: no-delivery; não envia mensagens.

3. `ivs-agent-observability-events`
   - Normaliza eventos/logs em feed operacional com redaction.
   - Script: `scripts/agent_events.py`.
   - Modo: read-only.

## Workflows adicionados
- `capability-governance`
- `handoff-operacional`
- `observability-events`

Workflow Registry validado: 10 workflows, 0 findings.

## Integração em agentes
- Maria, João, Pedro, Conselho Growth e LLM Council receberam as três novas skills.
- Clara recebeu apenas `ivs-agent-handoff-guard`, para manter escopo enxuto e seguro no atendimento externo.

## Evidência de validação
- `capability_registry.py`: executado com sucesso; 6 agentes, 10 workflows, 3 achados LOW de documentação/skills legadas.
- `handoff_packet.py`: executado com sucesso, pacote seguro para lead.
- `agent_events.py`: executado com sucesso; eventos redigidos, sem HIGH.
- `workflow_registry.py`: OK, 10 workflows, 0 findings.

## Guardrails
- Todas as skills são read-only/no-delivery por padrão.
- Nenhuma envia WhatsApp ou Telegram.
- Nenhuma altera produção automaticamente.
- Mudança canônica continua exigindo Maria/Tiaro + RC-25/graphify.
