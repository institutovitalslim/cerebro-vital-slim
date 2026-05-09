# GRAPH_REPORT — Pré-consulta / rascunho automático

Data: 2026-05-09

## Resumo
Incidente Erick: paciente relatou novo preenchimento, mas não apareceu no sistema. Logs confirmaram acesso ao formulário sem `POST /api/submit`; o backend não recebeu submissão final.

## Correção
- Persistência local no navegador.
- Novo endpoint `/api/draft`.
- Autosave de rascunho durante preenchimento.
- Rascunhos aparecem no painel `/pacientes` como `[RASCUNHO]`.

## Validação
Build e restart PM2 realizados. Teste técnico de `/api/draft` OK; arquivo de teste removido.
