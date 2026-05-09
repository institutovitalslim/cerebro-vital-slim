# Cron — IVS Pré-consulta Safety Audit diário

- Job ID: `a608fe14-c009-49a7-82b2-b2c8152d9a59`
- Agente: `maria-gerente`
- Sessão: `agent:maria-gerente:telegram:default:direct:971050173`
- Schedule: `25 8 * * *`
- Timezone: `America/Bahia`

Executa:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/preconsulta_daily_audit.py --json
```

Reportar Tiaro somente se severidade ALTA/MÉDIA ou mudança relevante.
Nunca contatar paciente, nunca pedir novo preenchimento, nunca alterar produção nesta rotina.
