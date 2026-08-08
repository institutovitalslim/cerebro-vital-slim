# Graphify RC-25 — QA diário Clara — 2026-08-08

## Status
Registro sanitizado criado. Corpus pequeno de QA diária; extração semântica automática não gerou grafo completo, então o registro operacional foi estruturado manualmente em formato Graphify/RC-25.

## Nós operacionais
- Clara WhatsApp
- QA diária de conversão/agendamento
- Observabilidade WhatsApp current/historical
- Congelamento de pipeline de dados (36+ dias)
- Guardrails clínicos
- Taxa de conversão baseline 6,8%
- Causa raiz dos drops: explicação técnica antes do compromisso

## Relações
- Clara WhatsApp exige QA de agendamento sem PII.
- Current zerado e histórico congelado há 36+ dias indicam risco técnico crítico de observabilidade.
- O risco exige intervenção técnica humana imediata no pipeline de captura/análise, sem pausar a Clara sem ordem direta do Tiaro.
- Melhorias recomendadas reforçam regras seguras de conversão e não criam regra clínica nova.
- Correção da causa raiz dos drops (oferta de explicação antes do horário) é de alto impacto e baixo risco.
