# GBrain IVS — Health Report

Gerado em: `2026-06-14T11:17:37.492681+00:00`
Modo: `post-rc25`
Arquivos espelhados: **5096**

## Estatísticas
- Pages: **4933**
- Chunks: **7551**
- Embedded: **7551**
- Links: **3632**
- Tags: **28**
- Timeline: **0**

## Saúde
- Overall health: **60/100**
- Brain score: **70/100**
- Embed staleness: **OK**

## Warnings
- `content_sanity_audit_recent` — 98 events (hard=0 [hard_block=0 reject=0 quarantine=0] soft=7 [soft_block=0 flag=7] warn=91), sources: default=98. (Local audit only — multi-host operators set GBRAIN_AUDIT_DIR.)
- `flagged_pages` — 1 page(s) flagged (markup-heavy or oversize) — still searchable, agent warned on retrieval. Review with 'gbrain quarantine list --include-flagged'.
- `jsonb_integrity` — Could not check JSONB integrity
- `pack_upgrade_available` — Active pack: gbrain-base@1.0.0+7bd490ab. Successor available: gbrain-base-v2@1.0.0+b9bebaa4. Preview: `gbrain onboard --check --explain`
- `pgvector` — Could not check pgvector extension
- `resolver_health` — 4 issue(s): 0 error(s), 4 warning(s)
- `skill_conformance` — Could not parse manifest.json
- `takes_count` — 0 takes (takes.bootstrap_enabled is false; opt in to enable)

## Comandos
- **OK** `bun run src/cli.ts import /root/.local/share/ivs-gbrain/import/ivs-brain --no-embed` (22.3s)
- **OK** `bun run src/cli.ts extract --stale --catch-up` (1.84s)
- **OK** `bun run src/cli.ts embed --stale` (1.84s)
- **OK** `bun run src/cli.ts doctor` (4.0s)
- **OK** `bun run src/cli.ts stats` (1.85s)

## Regra operacional
- Fonte de verdade continua sendo o markdown do `cerebro-vital-slim`.
- GBrain é retrieval/grafo/embeddings/resolver.
- Escrita persistente continua via Graphify/RC-25.
