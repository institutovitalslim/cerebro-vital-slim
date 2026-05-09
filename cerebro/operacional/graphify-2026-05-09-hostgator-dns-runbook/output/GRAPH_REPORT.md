# RC-25 — HostGator DNS Runbook

## Contexto
Tiaro informou que o domínio `institutovitalslim.com.br` está na HostGator.

## Entregas
- Script: `generate_hostgator_dns_runbook.py`.
- Workflow: `hostgator-dns-runbook`.
- Artefatos:
  - `/root/deliverables/hostgator-dns-runbook.json`
  - `/root/deliverables/hostgator-dns-runbook.html`

## Recomendação de registro inicial
- FQDN: `backup.institutovitalslim.com.br`.
- Tipo: `CNAME`, se houver storage/proxy com hostname; `A` apenas se houver IP fixo.
- Target: pendente (`<storage-ou-proxy-privado>`).
- Público: não.

## Guardrails
- DNS não alterado.
- Backup não publicado.
- `www` não deve ser usado para backup.
- Cockpit não deve ser aberto publicamente.
- Credenciais não criadas.

## Validação
- Clara watch: OK.
- Workflow Registry: 54 workflows / 0 findings.
- CI local: 27 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.

## Próximo input obrigatório
Definir o target real do CNAME/A para `backup.institutovitalslim.com.br` ou autorizar abertura assistida do painel HostGator com os dados do destino privado.
