# RC-25 — backup.institutovitalslim.com.br em uso seguro

## Pedido
Tiaro informou que `backup.intitutovitalslim.com.br` estava no ar e pediu para usar.

## Correção validada
- Host informado com erro de digitação (`intitutovitalslim`) não resolve.
- Host correto validado: `backup.institutovitalslim.com.br`.
- DNS A: `187.77.58.193`.

## Execução
- Criado vhost nginx reservado para `backup.institutovitalslim.com.br`.
- Certificado Let's Encrypt emitido e instalado.
- HTTPS ativo.
- Endpoint público mínimo: `/__backup_alive` retorna `200 ok`.
- Raiz `/` retorna `403 Forbidden`.

## Guardrails
- Nenhum backup publicado.
- Nenhum diretório de backup exposto.
- Nenhum cockpit exposto.
- Nenhuma credencial criada ou versionada.
- Header `X-Robots-Tag: noindex, nofollow, noarchive` aplicado.

## Verificação
- `https://backup.institutovitalslim.com.br/__backup_alive` → 200.
- `https://backup.institutovitalslim.com.br/` → 403.
- TLS CN: `backup.institutovitalslim.com.br`.
