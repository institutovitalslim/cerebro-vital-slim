---
type: raw-rc25
status: active
owner: maria
source_of_truth: true
created: 2026-06-14
updated: 2026-06-14
rc25: graphify-2026-06-14-gbrain-base-v2-takes-decisao
---
# RC-25 — GBrain IVS upgrade base-v2 e decisão sobre takes

## Decisão
Após autorização operacional de Tiaro, o GBrain IVS foi migrado de `gbrain-base` para `gbrain-base-v2` via handler protegido `unify-types`.

`takes` permanece desligado neste ciclo. Motivo: é recurso opt-in de classificação/derivação adicional; antes de ativar, precisa de piloto controlado e critério de rollback. A camada canônica segue sem writeback automático.

## Execução técnica
Comando aplicado:

```bash
gbrain jobs submit unify-types --allow-protected --follow --params '{"target_pack":"gbrain-base-v2"}'
```

Resultado:
- Active pack antes: `gbrain-base@1.0.0+7bd490ab`
- Active pack depois: `gbrain-base-v2@1.0.0+b9bebaa4`
- Distinct page types antes: 8
- Distinct page types depois: 3
- Retyped explicit: 10 páginas
- Retyped catch-all: 18 páginas
- Page-to-link: 0
- Page-to-alias: 0
- Warnings do handler: 0

## Validação pós-upgrade
Executado post-RC25 sync + doctor + stats + regressão.

Resultado validado:
- Pages: 4958
- Chunks: 7589
- Embedded: 7589
- Links: 3632
- Embed staleness: OK
- Regressão de agentes: 6/6 OK
- Overall health: 65/100
- Brain score: 70/100
- `pack_upgrade_available`: OK / current

## Warnings remanescentes aceitos
- `content_sanity_audit_recent`
- `flagged_pages` — 1 página markup-heavy pesquisável
- `jsonb_integrity` — limitação local de check
- `pgvector` — limitação local de check
- `resolver_health` — 4 warnings, 0 erros
- `skill_conformance` — manifest externo não parseado
- `takes_count` — esperado, pois takes segue desligado

## Governança
- Markdown do `cerebro-vital-slim` continua fonte de verdade.
- GBrain continua sendo camada de retrieval/grafo/embeddings/resolver.
- Escrita persistente continua via Graphify/RC-25.
- Nenhum segredo/token foi registrado.
- Nenhum writeback automático foi habilitado.
