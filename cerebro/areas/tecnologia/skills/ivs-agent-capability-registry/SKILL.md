---
name: ivs-agent-capability-registry
description: Inventário e auditoria IVS-first das capacidades dos agentes, skills, workflows e guardrails do OpenClaw.
---

# IVS Agent Capability Registry

Skill inspirada funcionalmente em padrões de Agent OS: cada agente deve ter capacidades declaradas, dono operacional, escopo, ferramentas permitidas, riscos e evidências.

## Uso

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-capability-registry/scripts/capability_registry.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-capability-registry/scripts/capability_registry.py --md-out /root/deliverables/ivs-agent-capability-registry.md
```

## O que verifica

- agentes configurados no OpenClaw;
- skills declaradas por agente;
- skills inexistentes ou sem `SKILL.md`;
- subagentes permitidos;
- workflows registrados no `ivs-agent-operating-layer`;
- guardrails esperados para Maria, Clara, João e Pedro;
- riscos operacionais: paciente/lead, financeiro, publicação externa, envio real e alteração de produção.

## Regras

- Read-only por padrão.
- Não envia WhatsApp, Telegram ou mensagens externas.
- Não altera agentes.
- Mudança canônica exige Maria/Tiaro + RC-25/graphify.
