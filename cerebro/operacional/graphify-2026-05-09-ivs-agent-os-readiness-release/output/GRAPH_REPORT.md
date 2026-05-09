# RC-25 — IVS Agent OS Readiness Scorecard + Release Bundle

## Entregas
1. Readiness Scorecard
- Script: `scripts/agent_os_readiness_scorecard.py`
- Critérios: CI, Workflow Registry, Drift, Secrets, Backup, Restore dry-run, Alertas e Cockpit protegido.
- Resultado: READY, 100/100.

2. Release Bundle
- Script: `scripts/agent_os_release_bundle.py`
- Gera bundle sanitizado em `/root/deliverables/releases/`.
- Exclui server/token, backups e secrets.
- Gera SHA-256.

3. Workflows adicionados
- `agent-os-readiness-scorecard`
- `agent-os-release-bundle`

## Validação
- Scorecard: READY 100/100.
- Release bundle: OK, 183 arquivos.
- Workflow Registry: 30 workflows / 0 findings.
- CI local: 7 checks OK.
- Cockpit Único: OK.
- Workflow Runner: 14 runs concluídas.

## Guardrails
- Bundle não é publicado externamente.
- Token/backups/releases não são versionados no cérebro.
- Scorecard é read-only.
