# RC-25 — Acesso seguro de credenciais operacionais para agentes IVS

Data: 2026-06-24
Responsável: Maria

## Decisão

Tiaro determinou que os agentes IVS tenham acesso operacional às credenciais necessárias, começando pelo caso crítico da Ana: acesso ao Google Drive/Sheets via `gog` para localizar/ler a planilha de mensagens do WhatsApp.

## Regra de segurança

Credenciais **não** devem ser colocadas em skills, prompts, memória, mensagens ou arquivos canônicos. Skills podem documentar o procedimento, mas nunca conter o valor de tokens, senhas, refresh tokens ou segredos.

## Implementação

Foi criada a skill:

```text
ivs-secure-credentials-access
```

Foi criado o wrapper:

```bash
/usr/local/bin/ivs-with-runtime-env
/root/cerebro-vital-slim/scripts/ivs_with_runtime_env.py
```

Função: carregar pares `KEY=VALUE` de arquivos protegidos locais e executar o comando solicitado sem imprimir segredos.

Foi criado o diagnóstico sanitizado:

```bash
/usr/local/bin/ivs-gog-access-check
/root/cerebro-vital-slim/scripts/ivs_gog_access_check.py
```

## Arquivos protegidos usados pelo loader

```text
/root/.hermes/shared/ivs-runtime.env
/root/.openclaw/.env.runtime
```

O arquivo compartilhado local foi configurado com permissão `600`. Não deve ser commitado e não deve ter conteúdo impresso.

## Systemd

Os gateways Hermes receberam drop-in local com:

```text
EnvironmentFile=/root/.hermes/shared/ivs-runtime.env
```

Perfis cobertos:

- default/Maria
- Ana
- João
- Clara
- Pedro
- Jarvis
- Eduardo

Observação: gateways já rodando precisam reiniciar fora do próprio gateway para herdar env diretamente. Enquanto isso, o wrapper `ivs-with-runtime-env` funciona imediatamente para comandos de terminal.

## Validação

Validação simulando perfil Ana:

```bash
HERMES_HOME=/root/.hermes/profiles/ana ivs-with-runtime-env ivs-gog-access-check
```

Resultado sanitizado:

```json
{
  "ok": true,
  "gog_binary": true,
  "gog_keyring_password_env": true,
  "gog_account_env": true,
  "auth_status_ok": true,
  "credentials_exists": true
}
```

Busca Drive via Ana validada:

```bash
HERMES_HOME=/root/.hermes/profiles/ana ivs-with-runtime-env gog drive search "mensagens whatsapp" --json
```

Retorno: `search_ok true`.

## Uso operacional

```bash
ivs-with-runtime-env gog auth status --json
ivs-with-runtime-env gog drive search "mensagens whatsapp" --json
ivs-with-runtime-env ivs-gog-access-check
```

## Guardrails

- Leitura operacional permitida para dados internos necessários ao escopo do agente.
- Escrita, compartilhamento, deleção ou mudança de permissão em Drive/Sheets exige aprovação explícita.
- Omie write, Z-API real e publicação externa continuam nos gates específicos.
- Nunca copiar credenciais para skill.
