# RC-25 — Cockpit Único IVS Agent OS

## Implementação
Criado cockpit unificado para consolidar Agent OS IVS:
- agentes/capabilities;
- workflow registry;
- workflow runs;
- observability events;
- permission matrix.

Arquivo principal:
- `scripts/generate_agent_os_cockpit.py`

Workflow adicionado:
- `agent-os-cockpit`

## Saídas
- `/root/deliverables/cockpit-unico-ivs-agent-os.html`
- `/root/deliverables/cockpit-unico-ivs-agent-os.json`

## Validação
- Workflow Registry: 13 workflows / 0 findings.
- Cockpit gerado com status `LOW`, ok=true.
- Status LOW vem de 3 achados baixos no Capability Registry relacionados a skills legadas sem `SKILL.md` detectável.
- Sem HIGH/MEDIUM e sem erro de coleta.

## Guardrails
- Read-only.
- Não envia mensagens.
- Não altera produção.
- Não pausa/despausa Clara.
- Não substitui autorização explícita.
