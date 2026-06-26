# Operação

## Componentes
- `scripts/send_next_morning_confirmations.py`: dispara confirmações reais por WhatsApp, com `--mode next-morning` ou `--mode same-day-afternoon`.
- `scripts/process_reply.py`: classifica resposta e atualiza o Quarkclinic, sem responder automaticamente o paciente no WhatsApp.
- Estado operacional principal: `/root/cerebro-vital-slim/ops/quarkclinic_confirmations/state/pending_confirmations.json` (cumulativo entre os disparos ativos, sem sobrescrever o turno anterior)
- Logs: `/root/cerebro-vital-slim/ops/quarkclinic_confirmations/logs/`
- Bridge Z-API: `/root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge.py`

## Endpoint Quarkclinic usados
- `GET /v1/agendamentos`
- `PATCH /v1/agendamentos/{id}/confirmar`
- `PATCH /v1/agendamentos/{id}/cancelar`

## Regras de classificação
- confirmação: `confirmo`, `ok`, `sim`, `estarei`
- cancelamento: `não vou`, `cancelar`, `não consigo`
- remarcação: `remarcar`, `reagendar`, `outro horário`
- ambíguo: não atualizar automaticamente
- variações de telefone entre Quarkclinic e webhook devem ser toleradas, inclusive com ou sem o 9 adicional no celular

## Regra de escolha do telefone de confirmação
- Se o paciente/agendamento tiver mais de um telefone, a confirmação deve ir para o número em que o paciente já conversa com a clínica/Clara no WhatsApp.
- A fonte para essa decisão é o histórico local da Clara/Z-API (`clara_leads_state.json`), usando evidências como `inbound_count`, `last_inbound_at`, `last_reply_at` e `active`.
- A ordem dos telefones no Quarkclinic só é fallback quando nenhum candidato tem histórico na Clara/Z-API.
- O sistema deve tolerar variantes com e sem nono dígito ao comparar números.
- O dry-run registra `phoneSelection.reason`; o estado pendente registra `phoneSelection` junto com o envio real.

## Cron ativo
- Nome: `whatsapp-confirmacoes-manha-seguinte` → `0 16 * * *`
- Nome: `whatsapp-confirmacoes-tarde-mesmo-dia` → `30 7 * * *`
- Fuso: `America/Bahia`

## Checklist de validação
1. a data e hora do texto conferem com a agenda real do Quarkclinic para aquele disparo
2. o procedimento citado no texto bate com o procedimento real do agendamento
3. envio retornou `messageId`
4. paciente entrou em `pending_confirmations.json`
5. reply caiu no webhook
6. `process_reply.py` encontrou telefone pendente
7. PATCH do Quarkclinic executou com sucesso
