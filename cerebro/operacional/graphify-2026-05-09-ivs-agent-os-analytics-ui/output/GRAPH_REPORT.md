# RC-25 — IVS Agent OS Analytics + Approval Console

## Entregas
1. Dashboard de tendências
- Script: `scripts/generate_agent_os_trends.py`
- Saídas: `/root/deliverables/agent-os-trends.html` e `.json`
- Agrega runs, eventos e aprovações.

2. Approval Console estático
- Script: `scripts/generate_approval_console.py`
- Saídas: `/root/deliverables/approval-console-ivs-agent-os.html` e `.json`
- Read-only; orienta comando seguro, mas não cria aprovação nem executa ação.

3. Workflows adicionados
- `agent-os-trends`
- `approval-console`

## Validação
- Workflow Registry: 21 workflows / 0 findings.
- Cockpit Único: OK.
- Workflow Runner: 8 runs concluídas.

## Guardrails
- Sem execução de ação sensível.
- Sem UI ativa que altere estado.
- Sem exposição de tokens.
