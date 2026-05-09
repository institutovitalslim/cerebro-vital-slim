# RC-25 — Workflow Runner + Event Store IVS

## Implementação
Criada camada stateful para execução auditável de workflows do IVS Agent Operating Layer.

Arquivos:
- `scripts/workflow_runner.py`
- `scripts/generate_workflow_runs_cockpit.py`
- `workflows/workflow-runner.json`
- diretórios runtime `runs/` e `events/`

## Capacidades
- iniciar run por workflow registrado;
- atualizar estado (`started`, `in_progress`, `blocked`, `completed`, `failed`, `cancelled`);
- registrar evidências e achados;
- gravar eventos JSONL com redaction de telefone;
- gerar cockpit HTML/JSON de runs.

## Validação
- Workflow Registry: 11 workflows / 0 findings.
- Execução real criada e concluída: `ivr-20260509-200150-f87571a2`.
- Cockpit gerado em `/root/deliverables/cockpit-workflow-runs-ivs.html`.

## Guardrails
- Runner não autoriza ação sensível por si só.
- Não envia WhatsApp/Telegram.
- Não pausa/despausa Clara.
- Não altera produção automaticamente.
