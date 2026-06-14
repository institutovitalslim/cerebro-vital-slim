---
type: raw-rc25
status: active
owner: maria
source_of_truth: true
created: 2026-06-14
updated: 2026-06-14
rc25: graphify-2026-06-14-gbrain-fechamento-operacional
---
# RC-25 — GBrain fechamento operacional IVS

## Decisão
GBrain passa de estrutura aplicada para operação mínima concluída no IVS, preservando o cérebro markdown como fonte de verdade e Graphify/RC-25 como caminho de escrita persistente.

## Evidências técnicas
- Script de sync/health criado: `/root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py`.
- Script de regressão criado: `/root/cerebro-vital-slim/scripts/gbrain_ivs_regression.py`.
- Cron diário ativo: `40 10 * * * /usr/bin/python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py --mode cron`.
- Health latest: `/root/cerebro-vital-slim/cerebro/gbrain/sync/latest-health.md`.
- Regressão latest: `/root/cerebro-vital-slim/cerebro/gbrain/sync/latest-regression.md`.

## Resultado validado em 2026-06-14
- Pages: 4933
- Chunks: 7551
- Embedded: 7551
- Links: 3632
- Embed staleness: OK
- Regressão de agentes: 6/6 OK
- Overall health: 60/100
- Brain score: 70/100

## Regressão mínima aprovada
- Governança GBrain / Graphify RC-25
- Resolver por área operacional
- Clara confirmação objetiva
- Marketing João / Reels
- Apresentação paciente V10
- Financeiro Omie

## Warnings aceitos como não bloqueantes
- `content_sanity_audit_recent`
- `flagged_pages` — 1 página markup-heavy pesquisável
- `jsonb_integrity` — limitação de check local
- `pgvector` — limitação de check local
- `resolver_health` — warnings sem erro
- `skill_conformance` — manifest externo não parseado
- `takes_count` — takes desativado por decisão operacional até Tiaro autorizar
- `pack_upgrade_available` — upgrade para gbrain-base-v2 fica como próximo ciclo

## Governança
- GBrain é camada de retrieval/grafo/embeddings/resolver.
- Markdown do `cerebro-vital-slim` continua fonte de verdade.
- Nenhum writeback automático para o canônico foi habilitado.
- Segredos/tokens continuam proibidos.
