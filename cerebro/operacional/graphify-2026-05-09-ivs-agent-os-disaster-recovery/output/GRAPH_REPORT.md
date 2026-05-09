# RC-25 — IVS Agent OS Disaster Recovery

## Entregas
1. Backup Verify
- Script: `scripts/agent_os_backup_verify.py`
- Verifica arquivo tar.gz, diretórios obrigatórios e path traversal.
- Read-only.

2. Restore Planner
- Script: `scripts/agent_os_restore_planner.py`
- Gera plano de restauração dry-run.
- `--apply` é bloqueado por design e exige novo processo/approval/janela de manutenção.

3. Workflow adicionado
- `agent-os-disaster-recovery`

4. Cron semanal
- ID: `9efa98c4-1d2a-4c97-95d3-9c07da4133f3`
- Horário: domingo 03:45 America/Bahia.
- Entrega: none; anunciar somente se falhar.

## Validação
- Backup verify: OK.
- Restore plan dry-run: OK.
- Workflow Registry: 27 workflows / 0 findings.
- CI local: OK.
- Cockpit Único: OK.
- Workflow Runner: 12 runs concluídas.

## Guardrails
- Sem restauração automática.
- Sem sobrescrita de runtime.
- Sem prune automático.
- Backups e token não foram versionados no cérebro.
