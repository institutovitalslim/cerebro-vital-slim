# GBrain IVS — Health Report

Gerado em: `2026-06-14T16:15:34.474847+00:00`
Modo: `post-rc25`
Arquivos espelhados: **5134**

## Estatísticas
- Pages: **4958**
- Chunks: **7589**
- Embedded: **7589**
- Links: **3632**
- Tags: **28**
- Timeline: **0**

## Saúde
- Overall health: **65/100**
- Brain score: **70/100**
- Embed staleness: **OK**

## Warnings
- `content_sanity_audit_recent` — 218 events (hard=0 [hard_block=0 reject=0 quarantine=0] soft=15 [soft_block=0 flag=15] warn=203), sources: default=218. (Local audit only — multi-host operators set GBRAIN_AUDIT_DIR.)
- `flagged_pages` — 1 page(s) flagged (markup-heavy or oversize) — still searchable, agent warned on retrieval. Review with 'gbrain quarantine list --include-flagged'.
- `jsonb_integrity` — Could not check JSONB integrity
- `pgvector` — Could not check pgvector extension
- `resolver_health` — 4 issue(s): 0 error(s), 4 warning(s)
- `skill_conformance` — Could not parse manifest.json
- `takes_count` — 0 takes (takes.bootstrap_enabled is false; opt in to enable)

## Comandos
- **OK** `bun run src/cli.ts import /root/.local/share/ivs-gbrain/import/ivs-brain --no-embed` (25.71s)
- **OK** `bun run src/cli.ts extract --stale --catch-up` (2.12s)
- **OK** `bun run src/cli.ts embed --stale` (2.62s)
- **OK** `bun run src/cli.ts doctor` (4.63s)
- **OK** `bun run src/cli.ts stats` (1.09s)

## Regra operacional
- Fonte de verdade continua sendo o markdown do `cerebro-vital-slim`.
- GBrain é retrieval/grafo/embeddings/resolver.
- Escrita persistente continua via Graphify/RC-25.
