# RC-25 — Activation Dossier IVS Agent OS

## Entregas
1. Dossier executivo read-only
- Script: `scripts/generate_activation_dossier.py`
- Artefatos: `activation-dossier-ivs-agent-os.json` e `.html`.
- Consolida readiness, aprovações pendentes, riscos e recomendações.

2. Workflow adicionado
- `activation-dossier-governance`

3. CI atualizado
- CI local agora inclui `activation_dossier`.
- Resultado: 16 checks OK.

## Validação
- Readiness: READY 100/100.
- Aprovações pendentes: 3.
- Ações sensíveis executadas: 0.
- Drift findings: 0.
- Workflow Registry: 39 workflows / 0 findings.
- CI local: 16 checks OK.
- Cockpit Único: OK.
- Workflow Runner: 23 runs concluídas.

## Guardrails
- Dossier não aprova.
- Dossier não executa.
- Dossier não altera toggle.
- Dossier não chama sistema externo.
