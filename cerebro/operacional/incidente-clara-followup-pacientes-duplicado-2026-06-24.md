# Incidente — Clara follow-up em lote enviou mensagens a pacientes e duplicadas

Data: 2026-06-24
Responsável: Maria
Severidade: ALTA

## Resumo

Após autorização de envio real de follow-ups em lote, a execução do script `run_safe_lead_followups_now.py` enviou mensagens para contatos classificados pelo histórico como `paciente_ativo`, incluindo mensagens sem contexto suficiente e duplicadas.

## Evidências sanitizadas

Relatório operacional:

```text
/root/cerebro-vital-slim/cerebro/operacional/clara-followups/2026-06-24/safe_followups_execute.json
```

Resumo do relatório:

```text
sent_count: 20
evaluated_count: 22
raw_candidate_count: 33
historico_classificacao: paciente_ativo em 21 resultados
patient_like_sent: 20
```

Captura enviada por Tiaro mostrou conversa marcada como paciente, com mensagem operacional anterior da equipe e duas mensagens genéricas de follow-up enviadas em seguida.

## Causa raiz

1. O script consultava `historico_status()` e recebia `classificacao=paciente_ativo`, mas não usava esse resultado como bloqueio.
2. O `/admin/send` permitia bypass de `patient_bridge_known` quando a checagem QuarkClinic não confirmava paciente, criando falso negativo.
3. Mensagens com `kind=frio` eram permitidas em lote mesmo sem contexto validado.
4. A execução em lote não tinha trava de duplicidade/contexto forte o suficiente para contato paciente-like.

## Contenção aplicada

- Não havia processo ativo de follow-up após o incidente.
- Aprovações de lote foram expiradas/revogadas:
  - `appr-bc9feec411cf`
  - `appr-f46dad05dfaa`
- Bridge Clara permanece ativo e não pausado, para não interromper atendimento receptivo.
- `/admin/send` foi alterado para bloquear `patient_bridge_known`/`bridge_contexto_paciente` em modo fail-closed.
- Script de follow-up foi alterado para:
  - bloquear `historico_status.is_paciente_ativo=true`;
  - bloquear `classificacao=paciente_ativo`;
  - bloquear mensagens sem contexto (`context_validated=false`) em lote.

## Estado após contenção

```text
zapi-clara-bridge.service: active
hermes-gateway-clara.service: active
/admin/status: paused=false
```

## Regras operacionais pós-incidente

1. Follow-up em lote da Clara não pode enviar para `paciente_ativo`, mesmo que QuarkClinic retorne falso negativo.
2. `patient_bridge_known` deve ser bloqueio fail-closed em `/admin/send`.
3. Mensagem fria genérica sem contexto não pode ser enviada em lote.
4. Qualquer novo lote exige dry-run com auditoria explícita de:
   - contagem por `historico_classificacao`;
   - zero `paciente_ativo` elegível;
   - zero `kind=frio` enviado;
   - zero duplicidade por telefone/chat.

## Pendências

- Gerar lista sanitizada dos contatos impactados para revisão humana.
- Definir com Tiaro se haverá mensagem corretiva humana para pacientes impactados.
- Adicionar teste automatizado de regressão para impedir novo bypass.
