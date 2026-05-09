# RC-25 — IVS Agent OS Cockpit Protegido + CI Local

## Entregas
1. Servidor interno protegido
- Script: `scripts/agent_os_cockpit_server.py`
- Bind padrão: `127.0.0.1:8791`
- Token obrigatório por query/header.
- Serve somente arquivos allowlistados de `/root/deliverables`.
- Token armazenado localmente em `server/cockpit-token.txt` com permissão 0600 e não versionado no cérebro.

2. CI local
- Script: `scripts/agent_os_ci.py`
- Checks: workflow registry, regressão, cockpit generation, CLI status, guard smoke.
- Resultado: CI verde.

3. Workflows adicionados
- `agent-os-protected-cockpit-server`
- `agent-os-local-ci`

4. Cron CI diário
- ID: `75a256e4-28f0-437c-8c28-dc726d7343cd`
- Horário: 08:40 America/Bahia
- Entrega: none; anunciar somente se falhar.

## Validação
- Workflow Registry: 24 workflows / 0 findings.
- Cockpit Único: OK.
- Workflow Runner: 10 runs concluídas.
- CI local: OK.

## Guardrails
- Sem bind público.
- Sem token no RC/cérebro.
- Sem listagem de diretório.
- Sem execução de ação sensível.
