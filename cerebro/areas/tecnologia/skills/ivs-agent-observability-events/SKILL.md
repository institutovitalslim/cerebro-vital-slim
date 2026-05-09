---
name: ivs-agent-observability-events
description: Normaliza eventos operacionais de agentes IVS, Z-API, workflows e entregáveis em um feed/cockpit read-only com redaction.
---

# IVS Agent Observability Events

Skill de observabilidade inspirada em Agent OS: transforma logs dispersos em eventos operacionais seguros.

## Uso

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-observability-events/scripts/agent_events.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-observability-events/scripts/agent_events.py --md-out /root/deliverables/ivs-agent-events.md
```

## Fontes

- sessões recentes de agentes;
- log Clara/Z-API;
- workflow registry;
- entregáveis recentes;
- cron registry.

## Regras

- Read-only.
- Redige telefones e trechos longos.
- Não envia mensagens.
- Não substitui análise clínica/financeira.
