# AUDIT_REPORT — Auditoria Clara 2026-05-04

**Realizada via**: graphify cluster + análise manual de cobertura
**Sources analisadas**: 33 arquivos (30 skill files + prompt v3.1 + memoria consolidada + topics canônicos)
**Versão graphify base**: graph.json de 2026-04-29 (122 nodes, 33 communities) — re-clusterizado

## Inventário pré-auditoria

| Fonte | Localização | Files antes | Files depois |
|---|---|---|---|
| Skill OpenClaw | `/root/.openclaw/workspace/skills/clara-concierge-whatsapp/` | 30 | 30 |
| Cérebro Git | `cerebro/empresa/conhecimento/operacional/clara-concierge-whatsapp/` | 7 | 38 (sync 30 skill files + prompt v3.1) |
| Prompt Production | `/root/.openclaw/workspace/ops/zapi_bridge/clara_system_prompt.md` | v3.1 (25KB) | v3.1 (25KB) |

## Cobertura RC-01 a RC-33 (após sincronização + fix)

### ✅ Cobertura completa (skill + prompt + memoria):
RC-01, RC-02, RC-06, RC-07, RC-08, RC-09, RC-11, RC-12, RC-13, RC-14, RC-16, RC-17, RC-19, RC-22, RC-23, RC-24

### ✅ Adicionadas hoje ao REGRAS_CANONICAS.md (skill):
RC-25 a RC-33 (graphify, brush-off, close, releia histórico, anti-template, acolhimento, progressiva, memória, agenda Dra.)

### ⚠️ Gaps remanescentes:
- **REGRAS_CANONICAS.md (skill)**: nenhum
- **PROMPT v3.1 (produção)**: [3, 4, 5, 10, 15, 18, 20, 21]
  - RCs 3, 4, 5, 10, 15, 18, 20, 21 não estão no prompt
  - Análise: estes são RCs **operacionais** (equipe, infra, pipeline, catálogo) que podem não precisar estar no prompt do agente. Validar individualmente.
- **MEMORIA_CONSOLIDADA**: [25]

## God nodes no graph (top 5 nodes mais conectados)

(Conforme graphify-2026-04-29/GRAPH_REPORT.md, mantidos no re-cluster):
1. RC-12 (Lead vs Paciente) — bridge entre múltiplas communities
2. RC-16 (Handoff financeiro) — conexão com Tiaro/Liane/Z-API
3. SPIN flow — central pra conversão
4. RC-19 (Escalação) — segurança/compliance
5. PITCH_OFICIAL — conexão com personas e closing

## Ações aplicadas nesta auditoria

1. ✅ Sincronização: 30 skill files copiados pra `cerebro/.../clara-concierge-whatsapp/skill/`
2. ✅ Prompt v3.1 production salvo em `clara_system_prompt_v3.1_APLICADO_<ts>.md`
3. ✅ MEMORIA_CONSOLIDADA atualizada com RCs 26-33 + renomeada pra `MEMORIA_CONSOLIDADA_2026-05-04.md`
4. ✅ REGRAS_CANONICAS.md atualizado com RCs 25-33
5. ✅ graphify cluster-only re-rodado: 122 nodes / 33 communities (mantido a partir do graph anterior)
6. ✅ AUDIT_REPORT.md (este arquivo) gerado

## Próximos passos sugeridos

1. **Validar** se RCs operacionais (3, 4, 5, 10, 15, 18, 20, 21) precisam aparecer no prompt
2. **Roadmap RC-34+**: novas regras nascem das observações de produção
3. **Re-graphify completo (com LLM)** quando adicionar 5+ arquivos novos — para re-detectar cross-document surprises
