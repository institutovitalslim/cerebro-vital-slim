# RC-25 — IVS Agent OS Action Gate Final

## Implementação final estendida
Tiaro pediu seguir até o final. Foram adicionadas as camadas finais de governança prática:

1. Approval Ledger
- Script: `scripts/approval_ledger.py`
- Registra aprovação explícita com TTL, evidência, escopo e aprovador.
- Não executa ações.

2. Action Gate
- Script: `scripts/action_gate.py`
- Combina Permission Gate + Approval Ledger.
- Resultado final: allow/block político, mas sem execução.

3. Handoff Dispatcher Seguro
- Script: `ivs-agent-handoff-guard/scripts/handoff_dispatcher.py`
- Gera pacote de handoff e só considera destinos internos.
- Padrão dry-run/no-delivery.

4. Workflow adicionado
- `action-gate-approval`

## Validação
- Workflow Registry: 15 workflows / 0 findings.
- Action Gate validado para `pause_clara` com aprovação registrada: `ALLOW_BY_POLICY_BUT_NO_EXECUTION`.
- Handoff Dispatcher validado para João: `dry_run_no_delivery`.
- Cockpit Único: OK.
- Workflow Runner: 5 runs concluídas.

## Guardrails
- Nenhuma ação sensível é executada por essas camadas.
- Approval Ledger não substitui ordem explícita.
- Action Gate não envia mensagens, não pausa Clara, não escreve no Omie e não publica conteúdo.
- Dispatcher não envia para paciente/lead.
