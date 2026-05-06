# OpenClaw cron jobs relevantes — auditoria 2026-05-06

Coletado via `cron list` em 2026-05-06.

## Jobs criados/validados hoje

- `375d74ed-1fb1-43de-924a-9d8aafc856b4` — **Clara Learning — WhatsApp atual 2/2h**
  - Enabled: true
  - Schedule: `15 8-22/2 * * *`, TZ `America/Bahia`
  - Execução prevista: `python3 /root/.openclaw/workspace/ops/zapi_bridge/whatsapp_clara_learning.py --mode current --hours 6`
  - Delivery: none

- `cba17d20-3467-4f8c-8f6d-860a4b25a6c0` — **Clara Learning — WhatsApp histórico semanal**
  - Enabled: true
  - Schedule: `30 6 * * 1`, TZ `America/Bahia`
  - Execução prevista: `python3 /root/.openclaw/workspace/ops/zapi_bridge/whatsapp_clara_learning.py --mode historical --days 180`
  - Delivery: none

- `0161e7ec-7e77-4352-a596-9579d0d9259b` — **Clara Learning — Graphify RC-25 diário**
  - Enabled: true
  - Schedule: `5 22 * * *`, TZ `America/Bahia`
  - Execução prevista: `python3 /root/.openclaw/workspace/skills/clara-learning-orchestrator/scripts/graphify_clara_learning.py`
  - Delivery: Telegram Tiaro

- `9beaab69-4c81-4b6b-9b18-31f6f212087b` — **Clara Q&A Diário — Sabatina Conselho Growth**
  - Enabled: true
  - Schedule: `45 21 * * *`, TZ `America/Bahia`
  - Usa `latest-*.json` e rolling buffer antes da sabatina.

## Jobs já existentes relacionados

- `bbe92ffa-85f3-4840-953d-72ae4abbfab0` — Clara Learning — X/Twitter — `40 12 * * *`
- `f086ac46-a2af-4965-91d8-02698fb75d6e` — Clara Learning — YouTube — `30 10 * * *`
- `39eae6cc-2d31-4a01-aa9f-c1a3d624dbf7` — Clara Learning — Instagram manhã — `10 7 * * *`
- `a4935d7e-2237-45c9-9420-21878d85347f` — Clara Learning — Instagram tarde — `40 17 * * *`
- `66eedfbf-8de5-40d4-b537-102e99d3693e` — Clara Learning — Revisão 21:20 — `20 21 * * *`

Observação operacional: alguns jobs externos tiveram erro de resposta do agente, mas os scripts foram executados/validados manualmente durante a implementação. A cobertura de WhatsApp e Graphify está com jobs novos ativos.
