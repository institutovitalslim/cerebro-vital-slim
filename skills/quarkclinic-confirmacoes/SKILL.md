---
name: quarkclinic-confirmacoes
description: Enviar confirmações de consulta por WhatsApp para pacientes agendados, registrar pendências por telefone/agendamento e processar respostas para confirmar, cancelar ou remarcar no Quarkclinic. Use quando o usuário pedir confirmação de pacientes, automação diária de confirmações, ou atualização do status de agendamentos a partir de respostas no WhatsApp.
user-invocable: true
---

# Quarkclinic Confirmações

Use esta skill para operar o fluxo de confirmação de pacientes entre **Quarkclinic + Z-API + bridge**.

## Quando usar
- confirmar pacientes do dia seguinte
- disparar confirmações em lote
- validar ou operar o cron diário de confirmações
- processar resposta de paciente e atualizar o Quarkclinic
- depurar o fluxo de confirmação/cancelamento/remarcação

## Arquivos da skill
- Script de envio: `scripts/send_next_morning_confirmations.py`
- Script de resposta: `scripts/process_reply.py`
- Referência operacional: `references/operacao.md`
- Estado pendente: `/root/cerebro-vital-slim/ops/quarkclinic_confirmations/state/pending_confirmations.json`
- Logs: `/root/cerebro-vital-slim/ops/quarkclinic_confirmations/logs/`
- Bridge: `/root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge.py`

## Regras operacionais
1. Nunca afirmar envio sem `messageId` real da Z-API.
2. Nunca afirmar confirmação/cancelamento no Quarkclinic sem retorno real do endpoint PATCH.
3. Para respostas ambíguas do paciente, não atualizar status automaticamente.
4. “Preciso remarcar” não é cancelamento automático, é estado `needs_reschedule`.
5. O fluxo diário é apenas para pacientes da **manhã seguinte**.

## Execução padrão
### Enviar confirmações da manhã seguinte
```bash
python3 /root/cerebro-vital-slim/ops/quarkclinic_confirmations/send_next_morning_confirmations.py --mode next-morning
```

### Enviar confirmações da tarde do mesmo dia
```bash
python3 /root/cerebro-vital-slim/ops/quarkclinic_confirmations/send_next_morning_confirmations.py --mode same-day-afternoon
```

### Processar uma resposta manualmente
```bash
python3 /root/cerebro-vital-slim/ops/quarkclinic_confirmations/process_reply.py 5571999999999 "Confirmo"
```

## Lógica esperada
- Buscar agendamentos conforme o modo escolhido no Quarkclinic
- Filtrar atendimentos antes de 12:00 para manhã seguinte
- Filtrar atendimentos a partir de 12:00 para tarde do mesmo dia
- Enviar WhatsApp com opções curtas de resposta
- Salvar vínculo `telefone -> agendamentoId`
- Quando houver resposta:
  - `confirmo` → confirmar no Quarkclinic
  - `não vou` / `cancelar` → cancelar no Quarkclinic
  - `remarcar` → marcar `needs_reschedule` e responder pedindo melhor período

## Cron atual
Existe um cron diário às 16:00 (`America/Bahia`) para esse fluxo. Antes de alterar, verifique o job ativo e preserve o horário a menos que o usuário peça mudança.

## Diagnóstico rápido
Se algo falhar, leia `references/operacao.md` e verifique nesta ordem:
1. Z-API retornou `messageId`
2. `pending_confirmations.json` foi atualizado
3. bridge está ativa
4. resposta do paciente chegou ao webhook
5. PATCH do Quarkclinic respondeu com sucesso

## Resultado esperado
Sempre retornar em um destes estados:
- concluído
- bloqueio real objetivo
- decisão concreta do usuário necessária
