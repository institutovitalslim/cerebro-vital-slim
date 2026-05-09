# RC-25 — IVS Agent OS Protected Cockpit Service

## Entregas
1. Service Manager do Cockpit Protegido
- Script: `scripts/agent_os_cockpit_service.py`
- Ações: `status`, `start`, `stop`, `restart`.
- Mantém bind em `127.0.0.1:8791`.
- Não imprime token.

2. Servidor iniciado e validado
- Status: ativo em localhost.
- HTTP sem token: 403.
- HTTP com token local: 200.

3. CI atualizado
- CI local agora inclui `cockpit_service_status`.
- Resultado: 9 checks OK.

4. Workflow adicionado
- `agent-os-protected-cockpit-service`

## Validação
- Workflow Registry: 32 workflows / 0 findings.
- CI local: 9 checks OK.
- Readiness: READY 100/100.
- Cockpit Único: OK.
- Workflow Runner: 16 runs concluídas.

## Guardrails
- Sem bind público.
- Sem token versionado no cérebro/RC.
- Sem listagem de diretórios.
- Sem exposição fora de `/root/deliverables` allowlistado.
