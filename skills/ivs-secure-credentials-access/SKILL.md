---
name: ivs-secure-credentials-access
description: "Acesso seguro a credenciais operacionais IVS para agentes Hermes/OpenClaw sem colar segredos em skills, mensagens ou memória. Use para gog/Google Drive/Sheets e demais integrações via env governado."
metadata:
  owner: Maria — Instituto Vital Slim
  version: 1.0.0
  governance: secrets_not_in_skills
---

# IVS Secure Credentials Access

## Regra principal

**Nunca colocar valores de credenciais em skill, prompt, memória, arquivo do cérebro ou mensagem.**

Esta skill documenta o acesso seguro. Os segredos ficam em arquivo de ambiente protegido no host e/ou cofre autorizado. A skill só ensina o caminho operacional.

## Arquivos de ambiente governados

Arquivos locais protegidos usados pelo loader:

```text
/root/.hermes/shared/ivs-runtime.env
/root/.openclaw/.env.runtime
```

Permissão esperada para arquivos com segredo:

```text
600
```

Não imprimir o conteúdo desses arquivos. O loader ignora linhas inválidas e carrega apenas pares `KEY=VALUE`.

## Comando seguro para usar credenciais em shell

```bash
ivs-with-runtime-env <comando>
```

Exemplos:

```bash
ivs-with-runtime-env gog auth status --json
ivs-with-runtime-env gog drive search "mensagens whatsapp" --json
ivs-with-runtime-env ivs-gog-access-check
```

Esse wrapper dá acesso às credenciais operacionais disponíveis no runtime sem copiar valores para skill, memória ou chat.

## Diagnóstico seguro do gog

```bash
ivs-gog-access-check
```

Esse comando retorna JSON sanitizado, sem segredo:

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

## Planilha de mensagens do WhatsApp

Quando Ana ou outro agente precisar acessar a planilha de mensagens do WhatsApp pelo Google Drive/Sheets, primeiro validar:

```bash
ivs-gog-access-check
```

Depois localizar com `gog`, por exemplo:

```bash
ivs-with-runtime-env gog drive search "mensagens whatsapp" --json
```

Se precisar ler Sheets, usar comando `gog sheets ...` conforme `gog sheets --help`.

## Agentes cobertos

O arquivo de ambiente foi plugado via systemd nos gateways dos perfis:

- Maria/default
- Ana
- João
- Clara
- Pedro
- Jarvis
- Eduardo

## Guardrails

- Google/Drive/Sheets: leitura operacional permitida quando for dado interno necessário ao agente.
- Escritas, compartilhamentos, deleções ou mudanças de permissão em Drive/Sheets exigem aprovação explícita.
- Financeiro/Omie write continua exigindo aprovação e gate específico.
- WhatsApp/Z-API real continua governado pela Clara e pelos guards de envio.
- Nunca mover segredo para uma skill. Skill com segredo vira vazamento permanente.

## Se falhar

1. Rodar `ivs-gog-access-check`.
2. Se `gog_keyring_password_env=false`, o gateway do perfil ainda não recebeu o env: reiniciar o serviço do perfil fora do próprio gateway.
3. Se `credentials_exists=false`, revisar `/root/.config/gogcli/credentials.json` sem imprimir valores.
4. Se `auth_status_ok=false`, reautenticar `gog` com conta operacional aprovada.
