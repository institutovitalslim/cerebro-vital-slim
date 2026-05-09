# RC-25 — Offsite Local Mirror Approval Preflight

## Entregas
- Preflight de local mirror gerado para `/root/agent-os-offsite/ivs-agent-os`.
- Approval packet gerado sem exportar.
- Workflow: `offsite-local-mirror-approval-preflight`.

## Status
- Clara watch atual: OK.
- Backup readiness local: OK.
- Exportação executada: não.
- Approval registrado: não.
- Frase exigida para executar: `Autorizo exportar o backup Agent OS para /root/agent-os-offsite/ivs-agent-os agora`.

## Guardrails
- Não exportar sem approval_id.
- Não escrever fora de `/root/agent-os-offsite`.
- Não criar credencial.
- Não usar rclone nesta etapa.
