# RC-25 — IVS Agent OS Production Activation Plan

## Entregas
1. Plano faseado de ativação
- Arquivo: `activation/production-activation-plan.json`
- 5 fases: baseline, Clara shadow, Clara enforcement, Pedro/Omie guarded write, cockpit supervisionado.

2. Validador read-only
- Script: `scripts/agent_os_activation_plan.py`
- Valida plano, CI, toggle da Clara não ativado automaticamente, cockpit service e offsite no-export.
- Recomendação atual: `ready_for_phase_0_and_phase_1_shadow_only`.

3. CI atualizado
- CI local agora inclui `production_activation_plan`.
- Resultado: 11 checks OK.

4. Workflow adicionado
- `agent-os-production-activation-plan`

## Validação
- Production activation validation: OK.
- Workflow Registry: 34 workflows / 0 findings.
- CI local: 11 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.
- Cockpit Único: OK.
- Workflow Runner: 18 runs concluídas.

## Guardrails
- Não ativa `CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=1` automaticamente.
- Pedro/Omie write exige Approval Ledger e revisão de credenciais.
- Offsite export exige destino explícito e aprovação.
- Cockpit permanece local/protegido.
