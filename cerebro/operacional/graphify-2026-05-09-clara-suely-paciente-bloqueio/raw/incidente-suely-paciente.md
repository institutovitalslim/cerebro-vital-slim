# Incidente: Clara enviou mensagem para Suely paciente — 2026-05-09

## Contexto
Tiaro reportou que Clara mandou mensagem para Suely, que é paciente. Maria verificou a operação da bridge WhatsApp/Z-API da Clara.

## Causa operacional
O telefone `557191927242` estava em `clara_exclusions.json` como `patient_bridge_known`, mas também havia entrada `active=true` em `clara_leads_state.json` com source `new_contact`. A regra anterior liberava automaticamente `patient_bridge_known` quando existia lead ativo e QuarkClinic não confirmava paciente. Isso abriu risco: paciente real que escreve no WhatsApp pode criar estado ativo de lead e furar o bloqueio.

## Correção aplicada
1. Removida a liberação automática de `patient_bridge_known` baseada apenas em `active=true`.
2. Mantida liberação somente por exceção explícita: `lead_exception*` ou `source=tiaro_lead_exception`.
3. Suely/Sueli adicionadas a bloqueio manual `patient_do_not_reply`:
   - `557191927242` — Suely Estacao Villas Shopping
   - `263084027429080` — Suely Estacao Villas Shopping @lid
   - `5571991927242` — Suely Dalmondez Castro
   - `5538991054179` — Sueli Teixeira de Freitas Oliveira
4. Exceções de lead já validadas por Tiaro foram preservadas como `lead_exception_patient_bridge_known`.

## Validação
Dry-run `/admin/send` retornou bloqueado para Suely/Sueli com `reason=patient_do_not_reply`. Dry-run para lead validado continuou liberado. Nenhum envio real foi feito na validação.

## Regra canônica
Paciente primeiro: `patient_bridge_known` não pode ser liberado automaticamente por estado de lead ativo. Toda liberação contra bloqueio de paciente deve ser exceção explícita e rastreável do Tiaro/equipe autorizada.
