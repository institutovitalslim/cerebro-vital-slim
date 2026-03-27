# Canais — Mapeamento Tópicos Telegram ↔ Áreas

> Grupo: Mkt - Imersão OpenClaw nos Negócios

| Tópico | ID | Área |
|--------|----|------|
| General | 1 | Geral — conversas livres |
| 📢 Marketing | 8 | Marketing — campanhas, tráfego, conteúdo |

## Como usar

- **Relatórios de campanha** → 📢 Marketing (topic_id: 8)
- **Alertas de ROAS** → 📢 Marketing (topic_id: 8)
- **Crons** sempre entregam no tópico da área, nunca no General

## Configuração de Crons com Tópicos

Ao criar um cron que envia relatório para o Telegram, especificar o `topic_id`:

```json
{
  "name": "relatorio-campanha-semanal",
  "schedule": "0 11 * * 1",
  "topicId": "8"
}
```

---

*Atualizado: março 2026*
