# RC-25 — Clara Phase 2 Enforcement Activation

## Autorização
Tiaro autorizou a liberação da Clara Phase 2 no contexto imediato da recomendação operacional: ativar `CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=1`.

## Entregas
1. Approval Ledger
- Approval registrado para `clara-whatsapp / followup_whatsapp`.
- Artefato: `clara-phase2-approval.json`.

2. Toggle ativado
- `CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=1` aplicado em `zapi_bridge.env`.
- Z-API bridge reiniciado.
- `/healthz`: OK.

3. Correção crítica aplicada
- Durante validação, foi detectado que o Action Gate aceitava approval amplo quando `/admin/send` omitia `approval_id`.
- Antes da correção, uma validação sintética para `5599999999999` foi aceita pela Z-API (`messageId=6F159B0F41197D1EABCD`).
- Patch aplicado imediatamente: `/admin/send` agora exige `approval_id` explícito quando enforcement está ativo.
- `action_gate.py` também passou a exigir `approval_id` explícito para considerar approval.

4. Workflow adicionado
- `clara-enforcement-phase2-activation`

5. CI atualizado
- CI local agora inclui `clara_enforcement_phase2_status`.
- Resultado: 17 checks OK.

## Validação final
- Bridge healthz: OK.
- Toggle carregado no processo: OK.
- Patch strict approval_id presente: OK.
- `/admin/send` sem `approval_id`: bloqueado 403.
- Paciente Suely `patient_do_not_reply`: bloqueado.
- Action Gate com `approval_id`: avaliação libera, sem executar por si.
- Mensagens externas após patch strict: 0.
- Workflow Registry: 40 workflows / 0 findings.
- CI local: 17 checks OK.
- Readiness: READY 100/100.
- Drift: 0 findings.
- Approval Queue: 2 pendências, 1 executada.
- Workflow Runner: 24 runs concluídas.

## Guardrails
- Clara não foi pausada.
- Nenhum paciente foi desbloqueado.
- Envios reais administrativos agora exigem `approval_id` explícito.
- Rollback: setar `CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=0` e reiniciar o bridge.
