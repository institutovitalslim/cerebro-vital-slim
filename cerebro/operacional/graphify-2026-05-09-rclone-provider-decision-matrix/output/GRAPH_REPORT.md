# RC-25 — Rclone Provider Decision Matrix

## Entregas
- Script: `generate_rclone_provider_decision_matrix.py`.
- Workflow: `rclone-provider-decision-matrix`.
- Artefatos:
  - `/root/deliverables/rclone-provider-decision-matrix.json`
  - `/root/deliverables/rclone-provider-decision-matrix.html`

## Recomendação operacional
- Provider recomendado: `s3_compatible`.
- Tipo rclone: `s3`.
- Destino lógico: `remote:ivs-agent-os-backups`.
- Retenção: `7 daily + 4 weekly + 6 monthly`.

## Opções listadas
- `s3_compatible`
- `backblaze_b2`
- `sftp`
- `google_drive`
- `webdav`

## Validação
- Remote criado: não.
- Credencial criada: não.
- Backup externo exportado: não.
- Clara watch: OK.
- Workflow Registry: 52 workflows / 0 findings.
- CI local: 25 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.

## Próximo input obrigatório
Tiaro precisa escolher provedor/conta. Recomendação: S3 compatível com credenciais configuradas fora do cérebro.
