# RC-25 — IVS Agent OS Drift Detection + Pipeline RC-25

## Entregas
1. Drift Detector
- Script: `scripts/agent_os_drift_detector.py`
- Compara runtime vs cérebro por hash.
- Ignora runtime volátil: runs, events, backups, alerts e approval ledger.
- Resultado final: 0 findings.

2. Artifact Index
- Script: `scripts/generate_agent_os_artifact_index.py`
- Gera índice dos artefatos Agent OS em `/root/deliverables`.

3. Pipeline RC-25
- Script: `scripts/agent_os_rc25_pipeline.py`
- Roda CI, artifact index e drift detector.
- Cria pasta RC de evidência local.
- Não faz push, restart, envio externo ou ação sensível.

4. Workflows adicionados
- `agent-os-drift-detection`
- `agent-os-rc25-pipeline`

## Validação
- Drift final: 0 findings.
- Artifact index: OK.
- RC-25 pipeline: OK.
- Workflow Registry: 26 workflows / 0 findings.
- Cockpit Único: OK.
- Workflow Runner: 11 runs concluídas.

## Guardrails
- Detecção é read-only.
- Pipeline não sincroniza automaticamente.
- Token do cockpit não foi versionado.
