# Content Radar v1 — manifesto de rollout reversível

Preparado em: `2026-07-31T10:46:22Z`

Estado inicial obrigatório: `CONTENT_RADAR_V1_ENABLED=false`

Destino: `/root/cerebro-vital-slim/sistemas/content-engine-os`

Origem: `/root/.config/superpowers/worktrees/cerebro-vital-slim/feature-content-radar-v1/sistemas/content-engine-os`

## Escopo fechado

Promover somente os 21 caminhos de `docs/content-radar-v1-rollout-files.txt`. Não copiar o worktree inteiro: origem e destino contêm alterações não relacionadas.

| SHA-256 da origem | Caminho |
|---|---|
| `4c25ef858578da2293d5bc6f1d6bb8a634e1d68983c8c10fce9e74c63de29ca7` | `apps/api/app/config.py` |
| `937fccfa0d0465c4396238464f3164e8e8e3bde80bdfa1002b202d414dd3fd45` | `apps/api/app/content_radar.py` |
| `0556d577e4d8c08d3080d071e5b1a48d137bf5a7110117f0bd2495e3a1804e34` | `apps/api/app/content_radar_schemas.py` |
| `125f476ac53d2cbabaf960030858a20123f074850bca9c64bd10abdc524fd53e` | `apps/api/app/radar_provenance.py` |
| `7df0c8f357fe3a47863fca2b73e644ac986be8bd56cc5ec20a78f30aa31dcc20` | `apps/api/app/routers/external_learning.py` |
| `3d841c55ef9ce92759dd2d14d7048a9191e85ea68a2e8c7d27b29d5cbd25c4f7` | `apps/api/app/routers/ideias.py` |
| `af05aad532b4af64447f4712b43489d9a4a192282c32a5f5205ed12011daad7f` | `apps/api/app/routers/orchestrate.py` |
| `353521facc43934eb4738b8bc8cc60b63584f88a33fb7e7c05855cfe8a530159` | `apps/api/app/routers/stories.py` |
| `50ea6cdba3cf29bed003dea0e1dc2fdbd1ea5fce39dfe7f8d31b8107c12ef63b` | `apps/web/app/components/galeria.tsx` |
| `24c62a017fb7865eff26f2979164d34a01d54be5273a6fa5d3a60dd702a7f610` | `apps/web/app/radar-externo/loading.tsx` |
| `0f346445b2c83996e44689dc25378f7272817b4d67bbab3532f1700229b04ab5` | `apps/web/app/radar-externo/page.tsx` |
| `95533acf84da4d397eb5d8c52a90c363b538d13e171c685e15aa7b573d29053e` | `apps/web/app/stories-engine/page.tsx` |
| `70896d2d7b02a3e55a052b0aa89b5a0dc87473f108c9be908cbfb84eff91694f` | `apps/web/app/styles.css` |
| `a60ad57ea5cee0e0e7584865c569193456cbfb01acf734caf13c6ce7ad7ea539` | `db/init/022_content_radar_v1.sql` |
| `5d40988a43a116d1ee8d66cef9fc5ab979b22110289341ad92ea20c630f753f5` | `db/init/023_content_radar_v1_hardening.sql` |
| `76bc486dd473148512382160ee27cc75200597924ed2fb53c985b9d9e17afd19` | `db/init/024_radar_creative_provenance.sql` |
| `233161d8b34eabc67acee84bb71107c108821c3d90dcb336156b2ae5445eac30` | `scripts/apply_migrations.py` |
| `dc723eaca0a39381b18f2e596daf82cf6b92b570867aa06fa98f3f4aee771195` | `scripts/content_radar_runtime_smoke.py` |
| `fae2109f73d6bb9fb4fb87c9bbec9ec593206c28dfa06fb6b7387bdb61b3a153` | `scripts/instagram_profile_external_collect_ingest.py` |
| `1b8d535a4ef7371b1b3844db0275a187622b07f22cb6774653c655d689bcfd5b` | `scripts/phase4_external_ingest.py` |
| `3195d04163e1d08e4539a79c179558793da87cd8d2cbda9b3760d63de7c88d07` | `docs/content-radar-v1-backend-rollback.md` |

Qualquer diferença de hash da origem ou do destino após o backup invalida a promoção.

## Evidência pré-rollout

- Backend completo: `136 passed`.
- `compileall`, `tsc --noEmit --incremental false` e `next build`: aprovados.
- Migrations `022 -> 023 -> 024` aplicadas em clone real de PostgreSQL 16 e reaplicadas como `already_applied`.
- Clone preservou 271 itens legados e criou 271 snapshots de auditoria.
- Integração real no clone: 13 checks aprovados para auth, RBAC, tenant, replay idempotente, conflito 409, ledger, governança de fonte, fila de ideias e revogação de usuário.
- Correção adicional validada: excluir fonte sincroniza `source_kind=excluded` + `active=false`; restaurar sincroniza `active=true`.
- Nenhuma publicação, DM, gasto, escrita clínica ou coleta recorrente faz parte deste rollout.

## Sequência governada

1. Confirmar flag ausente/false sem imprimir segredos.
2. Criar backup versionado dos arquivos existentes e manifesto com hash/modo/existência.
3. Gerar dump consistente e validar catálogo com `pg_restore -l` dentro do container PostgreSQL.
4. Revalidar hashes de origem e destino contra o snapshot.
5. Copiar somente a allowlist.
6. Aplicar `022`, `023` e `024` pelo runner com ledger/checksum; reaplicar para provar idempotência.
7. Reiniciar API e web mantendo flag desligada.
8. Executar health, smoke autenticado `--expect off`, logs e contagens do banco.
9. Ativação da flag é uma etapa separada e não pertence a este item de rollout.

## Critérios de aceite flag-off

- API e web saudáveis.
- Overview sem sessão = 401.
- Overview com owner = 200, `feature_enabled=false` e contrato observado.
- Tenant divergente = 404 quando existir segundo tenant.
- Ingestão/mutação bloqueadas com flag desligada.
- Fila legada continua funcional e não inclui Radar.
- CSS do Radar está servido e página responde sem 5xx.
- Migrations 022/023/024 registradas com checksums esperados.
- 271 itens legados preservados; audit correspondente disponível.

## Rollback

1. Manter/forçar `CONTENT_RADAR_V1_ENABLED=false`.
2. Restaurar somente arquivos cujo hash ainda seja o artefato implantado.
3. Remover somente arquivos marcados como inexistentes antes do rollout.
4. Reiniciar API/web e executar smoke legado/off conforme o binário restaurado.
5. Não apagar schema aditivo nem ledgers; preservar dump, audit e logs.
