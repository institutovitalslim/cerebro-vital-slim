# RC-25 — IVS Agent OS Hardening Final

## Entregas
1. Retention/backup
- Script: `scripts/agent_os_retention_backup.py`
- Backup read-only de runs, events, approvals, policies e workflows.
- Prune só com flag explícita `--prune`.

2. Cockpit Vivo
- Script: `scripts/generate_live_agent_os_cockpit.py`
- HTML auto-refresh: `/root/deliverables/cockpit-vivo-ivs-agent-os.html`.

3. Alertas críticos read-only
- Script: `scripts/agent_os_critical_alerts.py`
- Não envia mensagens por si só; só classifica alertas.

4. Workflows adicionados
- `agent-os-retention-backup`
- `agent-os-live-cockpit`
- `agent-os-critical-alerts`

5. Crons criados
- Critical Alerts: `fae296ed-b4a9-4411-bd3a-8a125f1b63cb`, 09:10 America/Bahia.
- Weekly Backup: `43d91783-a1dc-46a0-8fdf-fd9d2d019a00`, domingo 03:30 America/Bahia.

## Validação
- Workflow Registry: 19 workflows / 0 findings.
- Backup: OK.
- Cockpit Vivo: OK.
- Alertas: OK / 0 alertas.
- Workflow Runner: 7 runs concluídas.

## Guardrails
- Sem envio externo automático.
- Sem prune automático.
- Sem ação corretiva automática em produção.
