# Topic IDs CANÔNICOS — agente-reels-intel (João)

> **Última atualização: 2026-04-30**
> **Esta é a fonte de verdade. NÃO alterar baseado em memória anterior.**

## Grupo: AI Vital Slim

```
groupId: -1003803476669
```

## Topics onde João responde (Marketing/Reels/Conteúdo)

| Topic ID | Nome atual | Nome anterior | Domínio |
|---|---|---|---|
| **4** | Marketing | Marketing | Estratégia geral de marketing, scripts SPIN, posicionamento |
| **5782** | Marketing 🔥 | Reels | Conteúdo/reels, análise de criadores, roteiros |

> NOTA: O grupo tem **DOIS topics chamados "Marketing"** com IDs diferentes (4 e 5782).
> Topic 5782 foi renomeado de "Reels" para "Marketing" em 2026-04-30.
> Topic_id permanece o mesmo após rename — só o display name muda no Telegram.
> Ambos os topics são domínio do João e ambos estão na rota.

## Topics onde Maria responde (todos os outros)

Qualquer topic que NÃO está na lista acima é responsabilidade da Maria (Gerente Geral) — ex: 271 (Pacientes), 768, 848, 1, 6, 1980, etc.

## DM Telegram

DM com o bot @VitalSlimBot → Maria (default agent).

## Rota canônica

Arquivo: `/root/.openclaw/topic-agent-routing.json`

```json
{
  "version": 1,
  "routes": [
    {"channel": "telegram", "groupId": "-1003803476669:topic:4", "agentId": "agente-reels-intel"},
    {"channel": "telegram", "groupId": "-1003803476669", "topicId": "4", "agentId": "agente-reels-intel"},
    {"channel": "telegram", "groupId": "-1003803476669:topic:5782", "agentId": "agente-reels-intel"},
    {"channel": "telegram", "groupId": "-1003803476669", "topicId": "5782", "agentId": "agente-reels-intel"}
  ]
}
```

Cada topic tem 2 routes (formato composite + canônico) para cobrir variações no `groupResolution.id` do runtime.

## Histórico de erros que esta canonização previne

- 2026-04-29: rota apontava pra topic 5365 (antigo, deprecated)
- 2026-04-30 manhã: rota foi mudada pra topic 768 baseada em memória desatualizada ("Evolução do Openclaw" virou "Reels" por engano no log)
- 2026-04-30 tarde: Maria respondia em topic 4 (Marketing) por falta de rota
- 2026-04-30 noite: Tiaro identificou que existem 2 topics de Marketing (não apenas o renomeado) — rota expandida para cobrir ambos

## Como mudar (futuramente)

Se topics novos forem criados ou nomes mudarem:
1. Identificar topic_id real (ver `t.me/c/3803476669/<TOPIC_ID>` no link do tópico no Telegram)
2. Adicionar 2 routes (composite + canônico) no `/root/.openclaw/topic-agent-routing.json`
3. Atualizar este arquivo (`TOPICS-CANONICOS.md`) com a nova entrada
4. Não precisa restart de gateway (file mtime watch)
