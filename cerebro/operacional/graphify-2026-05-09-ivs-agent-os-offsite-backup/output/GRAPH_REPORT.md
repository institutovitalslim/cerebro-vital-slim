# RC-25 — IVS Agent OS Offsite Backup Readiness

## Entregas
1. Offsite Backup Adapter
- Script: `scripts/agent_os_offsite_backup.py`
- Modo padrão: readiness/no-export.
- Gera backup local, verifica integridade e prepara plano de exportação.
- Export real exige `--apply`, destino explícito e approval via Action Gate.

2. Modos preparados
- `readiness`: valida sem exportar.
- `local_mirror`: permitido apenas em `/root/agent-os-offsite` com approval.
- `rclone`: gera plano, mas apply real fica bloqueado até revisão manual do operador.

3. CI atualizado
- CI local agora inclui `offsite_backup_readiness`.
- Resultado: 10 checks OK.

4. Workflow adicionado
- `agent-os-offsite-backup-readiness`

## Validação
- Offsite readiness: OK.
- Backup local verificado: OK.
- Nenhum dado foi enviado para fora.
- Workflow Registry: 33 workflows / 0 findings.
- CI local: 10 checks OK.
- Readiness: READY 100/100.
- Cockpit Único: OK.
- Workflow Runner: 17 runs concluídas.

## Guardrails
- Sem export externo automático.
- Sem credenciais no código/artefatos.
- Export exige aprovação explícita e destino configurado.
