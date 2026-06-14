# GBrain IVS — Camada Canônica Operacional

Esta pasta define como o Instituto Vital Slim aplica o padrão GBrain ao cérebro canônico e à memória dos agentes.

## Status
- GBrain deixa de ser apenas sidecar experimental e passa a ser **camada estrutural operacional** do cérebro.
- O cérebro canônico continua em `/root/cerebro-vital-slim/cerebro`.
- O banco GBrain/PGLite e embeddings continuam fora do worktree, em `/root/.local/share/ivs-gbrain/`, para não misturar runtime com fonte de verdade.

## Regra de convivência
1. **Fonte de verdade:** arquivos markdown do `cerebro-vital-slim`.
2. **Retrieval/índice/graph:** GBrain sidecar.
3. **Mudança canônica:** sempre via Graphify/RC-25.
4. **Escrita direta por GBrain:** proibida até autorização explícita de Tiaro.
5. **Agentes:** consultam GBrain antes de afirmar processo, regra, histórico, pessoa, ferramenta, prazo, valor ou decisão operacional.

## Entradas principais
- `RESOLVER.md` — decisão de onde arquivar/consultar conhecimento.
- `schema.md` — taxonomia estrutural GBrain aplicada ao IVS.
- `agents/memory-bridge.md` — regras para memória dos agentes.
- `policies/operating-policy.md` — governança e limites.
- `sync/playbook.md` — como reindexar o cérebro no GBrain sidecar.

## Comandos operacionais
- Status rápido: `python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py --doctor-only`
- Sincronização completa: `python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py --mode manual`
- Regressão de agentes: `python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_regression.py`
- Consulta direta: `gbrain-ivs search "termo"`
- Página direta: `gbrain-ivs get <slug>`
- Reindexação controlada: ver `sync/playbook.md`

## Critério de operação concluída
- Cron diário ativo.
- Pós-RC-25 definido no playbook.
- `latest-health.md` atualizado com doctor/stats.
- `latest-regression.md` com regressão 100% nos cenários mínimos dos agentes.
- Warnings conhecidos documentados, sem erro bloqueante.
