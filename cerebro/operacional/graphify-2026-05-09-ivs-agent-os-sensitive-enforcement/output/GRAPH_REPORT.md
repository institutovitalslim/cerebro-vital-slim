# RC-25 — IVS Agent OS Sensitive Enforcement + Testes

## Implementação
1. Suíte automatizada de regressão
- Arquivo: `ivs-agent-operating-layer/tests/test_agent_os_regression.py`
- Resultado: 9 testes OK.

2. Sensitive Action Guard
- Arquivo: `ivs-agent-operating-layer/scripts/sensitive_action_guard.py`
- Falha fechado para ações sensíveis sem aprovação válida.

3. Clara/Z-API optional Action Gate
- `/admin/send` agora possui avaliação opcional via `CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=1`.
- Default permanece desligado para não quebrar produção.
- Dry-run validado após restart do bridge.

4. Pedro/Omie Guard
- Arquivo: `pedro-controller-ivs/scripts/pedro_omie_action_guard.py`
- Bloqueia escrita Omie sem aprovação válida.

5. Workflow adicionado
- `sensitive-action-enforcement`

## Validação
- Testes: 9/9 OK.
- Workflow Registry: 16 workflows / 0 findings.
- Cockpit Único: OK.
- Z-API Bridge: health OK após restart.
- Workflow Runner: 6 runs concluídas.

## Guardrails
- Nenhum envio real foi feito nos testes.
- Clara continua respeitando exclusões/patient safety.
- Enforcement forte de Clara fica opt-in por variável de ambiente.
- Pedro não escreve no Omie; apenas avalia gate.
