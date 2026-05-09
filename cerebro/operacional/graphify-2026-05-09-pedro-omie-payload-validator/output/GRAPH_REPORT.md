# RC-25 — Pedro Omie Payload Validator

## Entregas
- Script: `pedro_omie_payload_validator.py`.
- Workflow: `pedro-omie-payload-validator`.
- Templates gerados para:
  - `emitir_boleto`
  - `baixar_titulo`
  - `criar_conta_receber`
  - `atualizar_cliente`

## Validação
- Omie não foi chamado.
- Credenciais não foram usadas.
- Approval não foi registrado.
- Clara watch: OK.
- Workflow Registry: 46 workflows / 0 findings.
- CI local: 20 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.

## Próximo passo obrigatório
Para executar escrita real, Tiaro precisa fornecer payload concreto com `operation_type`, `payload_json`, `business_reason` e `idempotency_key`, seguido de aprovação explícita após revisão.
