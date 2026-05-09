# Cron Registry — IVS Agent Operating Layer

Atualizado em epoch: `1778355707`

Ativos após limpeza/expansão: **20**
Cancelados na limpeza anterior: **10**

## Crons ativos
- `032fd036-6a69-4088-bae2-8db5a4a31f10` — **monthly-feedback-consolidation** — `cron` `15 3 1 * *` `America/Sao_Paulo` — workflow: `memoria-operacional` — status: `None` erros: `0`
- `3dab666d-ed37-4675-8ddd-94614f5bbe9e` — **biweekly-memory-review** — `cron` `0 4 1,16 * *` `America/Sao_Paulo` — workflow: `memoria-operacional` — status: `None` erros: `0`
- `7f3835ec-e53c-40bb-93cb-13839cb8f953` — **Lembrete diário de oração financeira - tópico Marketing João** — `cron` `0 6 * * *` `America/Sao_Paulo` — workflow: `marketing-os` — status: `None` erros: `0`
- `2ba465d4-3dd0-435b-bb12-1576ed6c0403` — **agenda-diaria-whatsapp** — `cron` `0 6 * * *` `America/Sao_Paulo` — workflow: `agenda-operacional` — status: `None` erros: `0`
- `18833ac7-30c8-4d56-917a-be9665993b78` — **whatsapp-confirmacoes-manha-seguinte** — `cron` `0 16 * * *` `America/Bahia` — workflow: `confirmacoes-quarkclinic` — status: `None` erros: `0`
- `bf264980-0e69-48aa-8c47-46c0caa4f387` — **whatsapp-confirmacoes-tarde-mesmo-dia** — `cron` `30 7 * * *` `America/Bahia` — workflow: `confirmacoes-quarkclinic` — status: `None` erros: `0`
- `54fb064e-175d-490e-bf0e-9c57592d6642` — **manutencao-diaria-cerebro-memoria-clara-0100** — `cron` `0 1 * * *` `UTC` — workflow: `memoria-operacional` — status: `None` erros: `0`
- `30f7e41b-ad7d-4369-815e-294b313b68e4` — **Treino diário da Clara — Conversão Premium WhatsApp** — `cron` `20 7 * * *` `America/Bahia` — workflow: `clara-growth-learning` — status: `None` erros: `0`
- `cac7dc66-577a-426a-8acc-dd5517b26b5f` — **Auditoria diária da Clara — WhatsApp Growth Review** — `cron` `30 21 * * *` `America/Bahia` — workflow: `clara-growth-learning` — status: `None` erros: `0`
- `9beaab69-4c81-4b6b-9b18-31f6f212087b` — **Clara Q&A Diário — Sabatina Conselho Growth** — `cron` `45 21 * * *` `America/Bahia` — workflow: `clara-growth-learning` — status: `None` erros: `0`
- `0161e7ec-7e77-4352-a596-9579d0d9259b` — **Clara Learning — Graphify RC-25 diário** — `cron` `5 22 * * *` `America/Bahia` — workflow: `clara-growth-learning` — status: `None` erros: `0`
- `375d74ed-1fb1-43de-924a-9d8aafc856b4` — **Clara Learning — WhatsApp atual 2/2h** — `cron` `15 8-22/2 * * *` `America/Bahia` — workflow: `clara-growth-learning` — status: `None` erros: `0`
- `cba17d20-3467-4f8c-8f6d-860a4b25a6c0` — **Clara Learning — WhatsApp histórico semanal** — `cron` `30 6 * * 1` `America/Bahia` — workflow: `clara-growth-learning` — status: `None` erros: `0`
- `13141b04-2bdc-44da-9967-350328c33911` — **Clara Agendamento — QA diário de conversão** — `cron` `30 22 * * *` `America/Bahia` — workflow: `clara-growth-learning` — status: `None` erros: `0`
- `535f3616-8621-483d-a895-6f1d57d81222` — **Maria Pulse — Clara máquina de agendamento 2/2h** — `cron` `55 8-22/2 * * *` `America/Bahia` — workflow: `followup-seguro` — status: `None` erros: `0`
- `79822d71-e7f8-410c-bbfe-0a3021eb09fd` — **Clara Strategy Review — semanal agendamento** — `cron` `0 7 * * 1` `America/Bahia` — workflow: `clara-growth-learning` — status: `None` erros: `0`
- `ded8e70d-e351-44d1-9203-58ab672492bd` — **Watchdog Clara — validação operacional do modelo** — `every` `600000ms` `` — workflow: `followup-seguro` — status: `None` erros: `0`
- `dc9e1efc-1639-4b5f-b4a6-04537da33e5e` — **Champion Kit IVS — revisão semanal João + Clara** — `cron` `30 17 * * 5` `America/Bahia` — workflow: `marketing-os` — status: `None` erros: `0`
- `4b645967-fc1a-4967-81bf-b424f2e301cc` — **IVS Agent Operating Layer Audit consolidado diário** — `cron` `45 8 * * *` `America/Bahia` — workflow: `agent-layer-audit` — status: `None` erros: `0`
- `bb73a900-3b75-47e9-bcb9-e43620a758ab` — **IVS Agent Learning Autonomy — diário** — `cron` `10 6 * * *` `America/Bahia` — workflow: `agent-learning-autonomy` — status: `None` erros: `0`

## Crons cancelados
- `6bbea434-eefb-41dc-b8f9-802d35cd03cf` — **Clara/Z-API daily audit** — motivo: substituído pelo audit consolidado do IVS Agent Operating Layer; evita duplicidade de auditoria diária
- `a608fe14-c009-49a7-82b2-b2c8152d9a59` — **Pré-consulta daily audit** — motivo: substituído pelo audit consolidado do IVS Agent Operating Layer; monitor continua disponível sob demanda
- `9e37d4c8-fc40-4413-9c58-e86576ca3e63` — **Marketing OS/João daily audit** — motivo: substituído pelo audit consolidado do IVS Agent Operating Layer; monitor continua disponível sob demanda
- `ce9ea71e-ec78-496e-ab73-4fe2d00319a2` — **cron legado de auditoria/learning Clara** — motivo: redundante com rotina consolidada noturna e registry atual
- `76926327-93e3-456f-a118-ba54b6aa9ee6` — **cron legado silencioso Clara Learning** — motivo: sem entrega operacional independente; substituído por WhatsApp atual + auditoria diária
- `39eae6cc-2d31-4a01-aa9f-c1a3d624dbf7` — **Clara Learning — Instagram manhã** — motivo: slot externo com falhas recorrentes/baixo valor; consolidado na auditoria diária sem cron próprio
- `a4935d7e-2237-45c9-9420-21878d85347f` — **Clara Learning — Instagram tarde** — motivo: slot externo com falhas recorrentes/baixo valor; consolidado na auditoria diária sem cron próprio
- `f086ac46-a2af-4965-91d8-02698fb75d6e` — **Clara Learning — YouTube** — motivo: slot externo com falhas recorrentes; auditoria diária pode consultar quando fizer sentido
- `bbe92ffa-85f3-4840-953d-72ae4abbfab0` — **Clara Learning — X/Twitter** — motivo: slot externo com falhas recorrentes/baixo valor; consolidado na auditoria diária sem cron próprio
- `66eedfbf-8de5-40d4-b537-102e99d3693e` — **Clara Learning — Revisão 21:20** — motivo: redundante com Auditoria diária da Clara 21:30 e Graphify RC-25 22:05

## Política
- Auditorias específicas redundantes devem virar checks sob demanda dentro da skill.
- A rotina consolidada `IVS Agent Operating Layer Audit` fica como auditoria diária principal.
- A rotina `IVS Agent Learning Autonomy` gera briefs diários de evolução para todos os agentes.
- Crons de produção/paciente externos à skill são apenas rastreados, não alterados sem revisão específica.

## IVS Agent OS Daily Audit — cockpit único
- ID: `c677df82-01ce-40fd-b97d-5569586514b6`
- Workflow: `agent-os-daily-audit`
- Schedule: `55 8 * * *` — `America/Bahia`
- Agente: `maria-gerente`
- Modo: read-only
- Entrega: `none`; anunciar Tiaro somente em HIGH/MEDIUM ou mudança operacional relevante.

## IVS Agent OS Critical Alerts — read-only
- ID: `fae296ed-b4a9-4411-bd3a-8a125f1b63cb`
- Workflow: `agent-os-critical-alerts`
- Schedule: `10 9 * * *` — `America/Bahia`
- Entrega: none; anunciar somente se HIGH/MEDIUM.

## IVS Agent OS Weekly Backup — read-only
- ID: `43d91783-a1dc-46a0-8fdf-fd9d2d019a00`
- Workflow: `agent-os-retention-backup`
- Schedule: `30 3 * * 0` — `America/Bahia`
- Modo: backup read-only; sem `--prune`.

## IVS Agent OS Local CI — daily
- ID: `75a256e4-28f0-437c-8c28-dc726d7343cd`
- Workflow: `agent-os-local-ci`
- Schedule: `40 8 * * *` — `America/Bahia`
- Modo: read-only CI; anunciar somente se falhar.
