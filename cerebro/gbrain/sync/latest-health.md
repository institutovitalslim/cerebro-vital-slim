# GBrain IVS — Health Report

Gerado em: `2026-08-02T13:58:45.110110+00:00`
Modo: `post-rc25`
Arquivos espelhados: **12164**

## Estatísticas
- Pages: **4739**
- Chunks: **11607**
- Embedded: **11607**
- Links: **3796**
- Tags: **19**
- Timeline: **9**

## Saúde
- Overall health: **35/100**
- Brain score: **75/100**
- Embed staleness: **OK**

## Warnings
- `content_sanity_audit_recent` — 540 events (hard=0 [hard_block=0 reject=0 quarantine=0] soft=0 [soft_block=0 flag=0] warn=540), sources: default=540. (Local audit only — multi-host operators set GBRAIN_AUDIT_DIR.)
- `conversation_format_coverage` — 6/6 conversation pages (100.0%) match NO built-in pattern. Breakdown: _no_match=6. Investigate: gbrain conversation-parser scan <slug> | Enable LLM fallback (opt-in): gbrain config set conversation_parser.llm_fallback_enabled true
- `jsonb_integrity` — Could not check JSONB integrity
- `pgvector` — Could not check pgvector extension
- `takes_count` — 0 takes (takes.bootstrap_enabled is false; opt in to enable)

## Comandos
- **OK** `bun run src/cli.ts import /root/.local/share/ivs-gbrain/import/ivs-brain --no-embed` (32.34s)
- **OK** `bun run src/cli.ts extract --stale --catch-up` (0.99s)
- **OK** `bun run src/cli.ts embed --stale` (1.79s)
- **FALHA** `bun run src/cli.ts doctor` (3.3s)
- **OK** `bun run src/cli.ts stats` (0.99s)

## Regra operacional
- Fonte de verdade continua sendo o markdown do `cerebro-vital-slim`.
- GBrain é retrieval/grafo/embeddings/resolver.
- Escrita persistente continua via Graphify/RC-25.
