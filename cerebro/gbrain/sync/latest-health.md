# GBrain IVS — Health Report

Gerado em: `2026-07-04T10:36:27.060961+00:00`
Modo: `manual`
Arquivos espelhados: **9586**

## Estatísticas
- Pages: **3743**
- Chunks: **9495**
- Embedded: **9495**
- Links: **3796**
- Tags: **19**
- Timeline: **9**

## Saúde
- Overall health: **35/100**
- Brain score: **83/100**
- Embed staleness: **OK**

## Warnings
- `content_sanity_audit_recent` — 328 events (hard=0 [hard_block=0 reject=0 quarantine=0] soft=0 [soft_block=0 flag=0] warn=328), sources: default=328. (Local audit only — multi-host operators set GBRAIN_AUDIT_DIR.)
- `conversation_format_coverage` — 6/6 conversation pages (100.0%) match NO built-in pattern. Breakdown: _no_match=6. Investigate: gbrain conversation-parser scan <slug> | Enable LLM fallback (opt-in): gbrain config set conversation_parser.llm_fallback_enabled true
- `jsonb_integrity` — Could not check JSONB integrity
- `pgvector` — Could not check pgvector extension
- `takes_count` — 0 takes (takes.bootstrap_enabled is false; opt in to enable)

## Comandos
- **OK** `bun run src/cli.ts import /root/.local/share/ivs-gbrain/import/ivs-brain --no-embed` (31.13s)
- **OK** `bun run src/cli.ts extract --stale --catch-up` (1.48s)
- **OK** `bun run src/cli.ts embed --stale` (4.33s)
- **FALHA** `bun run src/cli.ts doctor` (3.8s)
- **OK** `bun run src/cli.ts stats` (0.93s)

## Regra operacional
- Fonte de verdade continua sendo o markdown do `cerebro-vital-slim`.
- GBrain é retrieval/grafo/embeddings/resolver.
- Escrita persistente continua via Graphify/RC-25.
