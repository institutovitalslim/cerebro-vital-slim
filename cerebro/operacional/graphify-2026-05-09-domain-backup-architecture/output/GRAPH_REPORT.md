# RC-25 — Domain Backup Architecture

## Pedido
Tiaro autorizou considerar `www.institutovitalslim.com.br` para hospedar em subdomínio ou alternativa melhor.

## Recomendação
- Não usar `www.institutovitalslim.com.br` para hospedar backups.
- Usar subdomínio separado e privado: `backup.institutovitalslim.com.br`.
- Para cockpit protegido, usar outro subdomínio se necessário: `ops.institutovitalslim.com.br`, com token + allowlist/VPN.
- Para status público sanitizado, se desejado: `status.institutovitalslim.com.br`.

## Guardrails
- DNS não alterado.
- Backup não publicado.
- Cockpit não aberto publicamente.
- Credenciais não criadas.

## Inputs pendentes
1. Provedor DNS atual do domínio.
2. Permissão/acesso para criar CNAME/A record.
3. Destino privado real do backup/storage.
4. Política de autenticação: VPN/allowlist/token.
5. Confirmação de que nada será público/indexável.

## Validação
- Clara watch: OK.
- Workflow Registry: 53 workflows / 0 findings.
- CI local: 26 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.
