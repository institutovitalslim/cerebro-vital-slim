# Auditoria diária consolidada — IVS Agent Operating Layer

- Gerado em: 09/05/2026 19:30 UTC
- Severidade consolidada: **ALTA**
- Modo: read-only; sem contato com paciente; sem publicação externa; sem alteração de produção.

## Indicadores
- Achados totais: 4
- HIGH: 1
- MEDIUM: 2
- LOW: 1

## Áreas
- Clara/Z-API: MEDIUM — Bridge OK · exclusões —
- Pré-consulta: HIGH — App OK · submissões 1 · drafts 0
- Marketing OS / João: MEDIUM — Backlog 7 · HTMLs 2 · regras ausentes 0

## Mudanças desde a última execução
- Primeira execução: baseline consolidado criado.

## Achados
- clara · MEDIUM · active_leads_blocked_as_patient_like · count=—
- preconsulta · HIGH · submission_without_markdown · count=1
- marketing_os · MEDIUM · joao_session_risk_markers · count=1
- marketing_os · LOW · marketing_backlog_active · count=7

## Regra mantida
- Monitores consolidam evidência. Ações de estado continuam exigindo autorização explícita quando houver risco operacional.
