# Cron — IVS Clara/Z-API Safety Audit diário

- Job ID: `6bbea434-eefb-41dc-b8f9-802d35cd03cf`
- Agente: `maria-gerente`
- Sessão: `agent:maria-gerente:telegram:default:direct:971050173`
- Schedule: `15 8 * * *`
- Timezone: `America/Bahia`
- Modo: systemEvent na sessão principal.

## Instrução operacional

Executar diariamente:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/clara_daily_audit.py --json
```

Reportar Tiaro somente se:
- severidade ALTA;
- severidade MÉDIA;
- mudança operacional relevante diferente de “Sem mudanças relevantes desde a última execução”.

Nunca enviar WhatsApp, nunca pausar/despausar Clara nesta rotina.
