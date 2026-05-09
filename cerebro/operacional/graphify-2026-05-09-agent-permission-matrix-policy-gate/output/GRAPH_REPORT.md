# RC-25 — Agent Permission Matrix + Policy Gate IVS

## Implementação
Criada matriz objetiva de permissões por agente/ação e um policy gate read-only para avaliar antes de ações sensíveis.

Arquivos:
- `policies/agent-permission-matrix.json`
- `scripts/permission_gate.py`
- `workflows/permission-governance.json`

## Níveis
- `read_only`: consulta/auditoria/relatório.
- `dry_run`: simulação sem envio/escrita externa.
- `write_with_approval`: exige autorização explícita e evidência.
- `forbidden`: bloqueado, exige handoff/decisão humana.

## Validação
Casos testados:
- Clara follow-up WhatsApp lead sem aprovação → bloqueia exigindo aprovação.
- Clara diagnóstico clínico → forbidden.
- Maria pausar Clara sem aprovação → bloqueia exigindo aprovação.
- Maria pausar Clara com evidência de ordem explícita → permitido no nível `write_with_approval`.
- Pedro escrita Omie sem aprovação → bloqueia exigindo aprovação.
- João publicação externa sem aprovação → bloqueia exigindo aprovação.

Workflow Registry: 12 workflows / 0 findings.

## Guardrails
O policy gate avalia e bloqueia, mas não executa ações. Ele não substitui autorização do Tiaro/Maria nem RC-25/graphify para mudança canônica.
