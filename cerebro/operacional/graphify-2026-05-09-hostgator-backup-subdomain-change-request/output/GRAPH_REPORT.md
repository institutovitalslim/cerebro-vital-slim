# RC-25 — HostGator Backup Subdomain Change Request

## Autorização
Tiaro autorizou criar `backup.institutovitalslim.com.br`.

## Estado atual
- Consulta DNS atual: sem A/CNAME para `backup.institutovitalslim.com.br`.
- DNS provider informado: HostGator.

## Change request preparado
Registro recomendado:
- Tipo: `CNAME`
- Nome: `backup`
- FQDN: `backup.institutovitalslim.com.br`
- Target: pendente (`<storage-ou-proxy-privado>`)
- TTL: `300` ou automático
- Público/indexável: não

Alternativa se houver IP fixo:
- Tipo: `A`
- Nome: `backup`
- Target: `<IP-fixo-do-proxy-privado>`

## Execução
- DNS alterado: não.
- Motivo: falta target real e acesso HostGator nesta sessão.

## Guardrails
- Não apontar para `www`.
- Não publicar backup em diretório público.
- Não abrir cockpit sem auth.
- Não gravar credenciais no cérebro.

## Validação
- Workflow Registry: 55 workflows / 0 findings.
- CI local: 27 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.
