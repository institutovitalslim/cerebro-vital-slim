# RC-25 — Clara Phase 2 Watch Pós-Ativação

## Entregas
- Script: `scripts/clara_phase2_watch.py`
- Modo: read-only, sem pausa, sem alteração de env e sem envio WhatsApp.
- Checkpoints temporários agendados: +15min, +30min, +60min, +120min.

## Status inicial
- Health/toggle/status: OK.
- Janela recente de logs: sem HIGH.
- Action Gate blocks recentes: esperados por validação.
- Mensagens externas no watch: 0.

## Guardrails
- Não pausar Clara.
- Não desbloquear paciente.
- Não enviar WhatsApp.
- Qualquer HIGH/MEDIUM relevante deve ser reportado imediatamente a Tiaro.
