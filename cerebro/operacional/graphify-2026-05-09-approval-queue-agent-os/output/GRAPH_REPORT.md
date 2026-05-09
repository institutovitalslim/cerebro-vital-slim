# RC-25 — Approval Queue IVS Agent OS

## Entregas
1. Fila read-only de aprovações pendentes
- Script: `scripts/generate_approval_queue.py`
- Artefatos: `approval-queue-ivs-agent-os.json` e `.html`.
- Consolida pendências de Clara Phase 2, Pedro/Omie write e Offsite Backup.

2. Workflow adicionado
- `approval-queue-governance`

3. CI atualizado
- CI local agora inclui `approval_queue`.
- Resultado: 15 checks OK.

## Validação
- Itens na fila: 3.
- Pendentes: 3.
- Executados: 0.
- Workflow Registry: 38 workflows / 0 findings.
- CI local: 15 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.
- Cockpit Único: OK.
- Workflow Runner: 22 runs concluídas.

## Guardrails
- Console não registra aprovação.
- Não ativa Clara enforcement.
- Não chama Omie.
- Não exporta backup.
