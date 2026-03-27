# Rotina: Heartbeat (Verificação Periódica)

## O que faz
Verificação automática de saúde do sistema. Checa pendências, prazos, projetos parados, crons com erro e memória não consolidada.

## Frequência
A cada 1h (configurado no OpenClaw: `heartbeat.every: "1h"`)

## Checklist executado

1. **Pendências** — Se item em `empresa/gestao/pendencias.md` > 3 dias sem resposta → alertar Felipe
2. **Prazos** — Se projeto com deadline em < 7 dias → alertar com plano de ação
3. **Projetos parados** — Se projeto sem atualização > 7 dias → alertar
4. **Crons com erro** — Se `consecutiveErrors >= 2` → alertar IMEDIATAMENTE
5. **Memória** — Se notas diárias > 3 dias sem consolidar → consolidar no repo

## Entrega
- **Tudo OK:** silencioso (`HEARTBEAT_OK`)
- **Algo precisa de atenção:** alerta no tópico da área correspondente
  - Pendência de vendas → 💰 Vendas (topic_id: 4)
  - Cron de marketing com erro → 📢 Marketing (topic_id: 3)
  - Problema de operações → ⚙️ Operações (topic_id: 6)

## Configuração no OpenClaw

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "1h"
      }
    }
  }
}
```

O heartbeat lê o arquivo `agentes/assistente/HEARTBEAT.md` a cada execução.

---

*Atualizado: março 2026*
