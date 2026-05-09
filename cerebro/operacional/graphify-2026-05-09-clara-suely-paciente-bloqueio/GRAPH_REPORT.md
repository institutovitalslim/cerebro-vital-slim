# GRAPH_REPORT — Clara / Suely paciente bloqueio

Data: 2026-05-09

## Resumo
Incidente corrigido: Clara havia enviado mensagem para Suely, paciente. A causa foi liberação automática de `patient_bridge_known` quando o contato também aparecia como lead ativo (`new_contact`).

## Decisão operacional
A partir desta correção, `patient_bridge_known` não é mais liberado automaticamente por `active=true`. Somente exceções explícitas (`lead_exception*` ou `source=tiaro_lead_exception`) podem liberar um número previamente marcado como paciente.

## Telefones bloqueados manualmente
- `557191927242` — Suely Estacao Villas Shopping
- `263084027429080` — Suely Estacao Villas Shopping @lid
- `5571991927242` — Suely Dalmondez Castro
- `5538991054179` — Sueli Teixeira de Freitas Oliveira

## Validação
- `/admin/send dry_run` para Suely/Sueli: bloqueado com `patient_do_not_reply`.
- Lead validado em exceção: liberado em `dry_run`.
- Nenhum envio real foi feito durante a validação.
