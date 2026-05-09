# RC-25 — Automação de publicação protegida do backup Agent OS

## Autorização
Tiaro disse "Pode seguir" após publicação protegida inicial.

## Implementação
- Script: `publish_protected_agent_os_backup.py`.
- Workflow: `protected-backup-publication-automation`.
- Cron local: `/etc/cron.d/ivs-agent-os-protected-backup`.
- Agendamento: diário às 05:10 UTC / 02:10 BRT.
- Retenção publicada: últimos 7 backups criptografados.

## Endpoint
- Latest gerado: `https://backup.institutovitalslim.com.br/agent-os/agent-os-backup-20260509-232838.tar.gz.enc`.
- Manifest autenticado: `https://backup.institutovitalslim.com.br/agent-os/manifest.json`.

## Guardrails
- Backup bruto `.tar.gz` não é publicado.
- Somente `.enc` e `.sha256` são servidos.
- HTTP Basic obrigatório.
- Passphrase e senha não são versionadas nem copiadas para o cérebro.
- Segredo permanece em `/root/secrets/ivs-backup-publication-latest.json`.
- Raiz do subdomínio continua 403.

## Validação
- Sem auth: 401.
- Com auth: 200.
- Checksum: OK.
- Manifest com auth: 200.
- Workflow Registry: 56 workflows / 0 findings.
- CI local: 28 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.
