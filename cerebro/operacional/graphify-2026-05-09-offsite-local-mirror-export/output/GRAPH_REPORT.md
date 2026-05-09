# RC-25 — Offsite Local Mirror Export

## Autorização
- Tiaro respondeu “Eu autorizo” no contexto imediato do pedido de exportação para `/root/agent-os-offsite/ivs-agent-os`.
- Approval Ledger: `appr-492641c02baa`.

## Execução
- Modo: `local_mirror`.
- Destino: `/root/agent-os-offsite/ivs-agent-os`.
- Backup origem: `/root/.openclaw/workspace/skills/ivs-agent-operating-layer/backups/agent-os-backup-20260509-220510.tar.gz`.
- Export path: `/root/agent-os-offsite/ivs-agent-os/agent-os-backup-20260509-220510.tar.gz`.
- Exportado: `True`.

## Verificação
- Checksum OK: `True`.
- SHA256: `0e3a701ae67927bf6a8234e894be16028bfb501ea6fb62b4866f000a0fea722e`.
- Tamanho: `32623` bytes.

## Validação global
- Clara watch antes do export: OK.
- Workflow Registry: 44 workflows / 0 findings.
- CI local: 19 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.
- Approval Queue: 1 pendência, 2 executadas.

## Guardrails
- Não foi usado rclone.
- Nenhuma credencial foi criada.
- Exportação ficou restrita a `/root/agent-os-offsite`.
- Próxima pendência sensível: Pedro/Omie write real continua bloqueado sem payload e approval específico.

