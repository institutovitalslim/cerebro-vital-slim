# RC-25 — IVS Agent OS Command Center e Runbook

## Entregas
1. CLI operacional único
- Script: `scripts/agent_os_cli.py`
- Comandos: `status`, `refresh-all`, `backup`, `alerts`, `test`, `gate`.
- Não executa ação sensível.

2. Runbook operacional
- Script: `scripts/generate_agent_os_runbook.py`
- Saídas: `/root/deliverables/runbook-ivs-agent-os.md` e `.json`.

3. Workflow adicionado
- `agent-os-command-center`

## Validação
- CLI refresh-all: OK.
- CLI test: OK.
- CLI status: OK.
- Workflow Registry: 22 workflows / 0 findings.
- Cockpit Único: OK.
- Workflow Runner: 9 runs concluídas.

## Guardrails
- CLI é safe entrypoint.
- Gate avalia, mas não executa.
- Backup não poda sem flag explícita.
- Runbook reforça: não pausar Clara sem ordem explícita do Tiaro.
