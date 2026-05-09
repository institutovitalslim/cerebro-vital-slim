# Cron — IVS Marketing OS João Audit diário

- Job ID: `9e37d4c8-fc40-4413-9c58-e86576ca3e63`
- Agente: `maria-gerente`
- Sessão: `agent:maria-gerente:telegram:default:direct:971050173`
- Schedule: `35 8 * * *`
- Timezone: `America/Bahia`

Executa:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/marketing_os_daily_audit.py --json
```

Reportar Tiaro somente se severidade ALTA/MÉDIA ou mudança relevante.
Não publicar em canais externos, não alterar produção e não executar tarefas no lugar do João.
