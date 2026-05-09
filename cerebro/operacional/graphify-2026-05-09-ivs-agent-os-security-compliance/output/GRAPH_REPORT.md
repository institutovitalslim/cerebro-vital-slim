# RC-25 — IVS Agent OS Security Compliance

## Entregas
1. Secrets Scanner
- Script: `scripts/agent_os_secrets_scanner.py`
- Scanner read-only com mascaramento de previews.
- Token que havia em deliverable local foi redigido; token real permanece apenas no arquivo 0600 do servidor local.
- Resultado final: 0 findings.

2. Integrity Manifest
- Script: `scripts/agent_os_integrity_manifest.py`
- Gera SHA-256 dos arquivos relevantes e root hash.

3. CI atualizado
- CI local agora inclui secrets scan e integrity manifest.
- Resultado: 7 checks OK.

4. Workflow e cron
- Workflow: `agent-os-security-compliance`
- Cron: `8f514c54-0c58-49a6-b07d-df5a0cdbd276`, 08:50 America/Bahia.

## Validação
- Secrets scan: 0 findings.
- Integrity manifest: OK.
- Workflow Registry: 28 workflows / 0 findings.
- CI local: 7 checks OK.
- Cockpit Único: OK.
- Workflow Runner: 13 runs concluídas.

## Guardrails
- Não imprime secret completo.
- Não envia token por mensagem.
- Não corrige produção automaticamente.
- Token e backups não são versionados no cérebro.
