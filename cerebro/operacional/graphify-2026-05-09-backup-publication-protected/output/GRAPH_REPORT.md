# RC-25 — Publicação protegida do backup Agent OS

## Autorização
Tiaro autorizou seguir e publicar o backup.

## Execução segura
O backup não foi publicado aberto. Foi publicada somente uma cópia criptografada e protegida por autenticação HTTP Basic.

## URL
- Backup criptografado: `https://backup.institutovitalslim.com.br/agent-os/agent-os-backup-20260509-220510.tar.gz.enc`
- Checksum: `https://backup.institutovitalslim.com.br/agent-os/agent-os-backup-20260509-220510.tar.gz.enc.sha256`

## Proteções
- Raiz `/` continua 403.
- Sem autenticação, arquivo retorna 401.
- Com autenticação, arquivo retorna 200.
- Arquivo é criptografado com `openssl enc -aes-256-cbc -salt -pbkdf2 -iter 310000`.
- Backup bruto `.tar.gz` não foi exposto.
- Credenciais e passphrase não foram gravadas no cérebro/RC.
- Arquivo de segredo local: `/root/secrets/ivs-backup-publication-latest.json`.

## Verificação
- `unauth_code`: 401.
- `auth_code`: 200.
- `checksum_auth_code`: 200.
- `root_code`: 403.
- `checksum_ok`: true.
