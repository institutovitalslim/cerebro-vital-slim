# Cron — IVS Agent Operating Layer Audit consolidado diário

- Job ID: `4b645967-fc1a-4967-81bf-b424f2e301cc`
- Agente: `maria-gerente`
- Sessão: `agent:maria-gerente:telegram:default:direct:971050173`
- Schedule: `45 8 * * *`
- Timezone: `America/Bahia`

Executa:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/ivs_agent_layer_daily_audit.py --json
```

Reportar Tiaro somente se severidade ALTA/MÉDIA ou mudança relevante.
Não contatar paciente, não publicar externamente, não pausar/despausar Clara e não alterar produção.
