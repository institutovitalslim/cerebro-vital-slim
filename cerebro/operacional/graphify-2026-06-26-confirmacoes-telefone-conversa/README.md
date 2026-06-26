# Graphify / RC-25 — Confirmações devem usar o telefone com conversa ativa

- **Data:** 2026-06-26
- **Solicitante:** Tiaro
- **Área:** Operação / Clara / QuarkClinic confirmações
- **Status:** aplicado em código + documentação

## Decisão canônica

Quando houver mais de um telefone no cadastro ou no agendamento, as confirmações de atendimento devem ser enviadas para o telefone em que o paciente já fala com a clínica/Clara no WhatsApp.

A ordem dos telefones no cadastro QuarkClinic é apenas fallback quando nenhum telefone candidato tiver histórico na Clara/Z-API.

## Evidência operacional

Tiaro enviou print de WhatsApp mostrando confirmação enviada para um número que não era o canal habitual de conversa. A orientação foi: “As confirmações de atendimento devem ser sempre enviadas para os telefones que os pacientes já falam conosco na clínica e não no segundo número quando tiver mais de um número”.

## Implementação

Arquivos alterados:

- `/root/cerebro-vital-slim/ops/quarkclinic_confirmations/send_next_morning_confirmations.py`
- `/root/cerebro-vital-slim/skills/quarkclinic-confirmacoes/scripts/send_next_morning_confirmations.py`
- `/root/cerebro-vital-slim/skills/quarkclinic-confirmacoes/SKILL.md`
- `/root/cerebro-vital-slim/skills/quarkclinic-confirmacoes/references/operacao.md`

Nova lógica:

1. Coleta todos os telefones do agendamento e do paciente.
2. Normaliza variantes com e sem nono dígito.
3. Consulta `clara_leads_state.json`.
4. Prioriza telefone com evidência de conversa real (`inbound_count`, `last_inbound_at`, `last_reply_at`, `active`).
5. Usa a ordem do QuarkClinic apenas se nenhum telefone tiver histórico Z-API/Clara.
6. Registra `phoneSelection` no dry-run, log e estado pendente.

## Validação

- `python3 -m py_compile` passou para script operacional e cópia da skill.
- Teste unitário local confirmou que, com dois telefones, escolhe o telefone com histórico Clara/Z-API.
- Dry-run real `same-day-afternoon` executado sem envio WhatsApp: 9 candidatos, 0 skipped, 9/9 com `matched_clara_whatsapp_history`.

## Guardrails

- Dry-run não envia WhatsApp.
- Telefones em relatório para Tiaro devem ser mascarados.
- Envio real continua exigindo `messageId` da Z-API para ser reportado como enviado.
- Resposta do paciente continua sem resposta automática da Clara; apenas atualiza status no QuarkClinic conforme regra existente.
