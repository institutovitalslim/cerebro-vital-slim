---
name: ivs-agent-operating-layer
description: Camada operacional IVS-first inspirada em Agent OS: Hands, workflows, safety monitor e auditoria para Clara, João e Maria.
---

# IVS Agent Operating Layer

Camada prática para transformar padrões de Agent OS em rotinas seguras do Instituto Vital Slim, sem migrar o OpenClaw nem copiar código externo.

## Princípios

1. **IVS-first**: Clara, João, Maria, Pedro e conselhos seguem donos, escopo e guardrails do IVS.
2. **Paciente protegido por design**: paciente, `do_not_reply` e `patient_bridge_known` bloqueiam automações de WhatsApp salvo exceção explícita autorizada.
3. **Workflow auditável**: toda rotina crítica deve ter entrada, responsável, decisão, saída, logs e critério de aceite.
4. **Dry-run antes de produção**: testes de WhatsApp e follow-up nunca enviam mensagem real sem autorização explícita.
5. **Graphify/RC-25 para mudança estrutural**: toda regra/camada permanente deve ser registrada no cérebro.

## Hands IVS prioritárias

### Hand Clara Safety Monitor
Audita Z-API/Clara sem enviar mensagens. Verifica pausa global, overrides humanos, colisões entre leads e exclusões, exceções explícitas, entradas `patient_do_not_reply`, `patient_bridge_known` e saúde do bridge.

### Hand Follow-up Seguro
Pipeline de follow-up ativo: validar lead → checar exclusões → montar mensagem → dry-run → aprovação/execução controlada.

### Hand Marketing OS
Rotinas do João: pesquisa, campanha, criativos, QA, métricas, aprendizado e cockpit.

### Hand Pré-consulta
Monitora submissões, drafts, falhas, pacientes sem formulário e inconsistências de dados.

## Comando inicial

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/clara_safety_monitor.py --json
```

Por padrão, o monitor é somente leitura e não pausa/despausa Clara.

## Workflow: Follow-up Seguro

Preflight para qualquer envio ativo fora do atendimento receptivo:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/followup_safety_check.py \
  --phone 55DDDNUMERO \
  --message 'mensagem aprovada' \
  --local-only
```

- O padrão é `dry_run`/validação local.
- Envio real exige `--real --i-understand-real-whatsapp-send` e autorização explícita.
- Se houver exclusão sem exceção explícita, bloqueia.

## Cockpit Clara/Z-API

Gera um HTML read-only com indicadores operacionais:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_clara_cockpit.py \
  --out /root/deliverables/cockpit-clara-zapi-ivs.html \
  --json-out /root/deliverables/cockpit-clara-zapi-ivs.json
```

Indicadores: saúde do bridge, pausa global, leads ativos, exclusões, do_not_reply, patient_bridge_known, overrides e colisões para revisão.

## Auditoria diária automática

Script:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/clara_daily_audit.py --json
```

Função:
- executa o `Clara Safety Monitor`;
- cria snapshot de baseline em `clara_safety_audit_state.json`;
- detecta deltas de bridge, pausa, overrides, exclusões e colisões;
- gera relatório Markdown em `/root/deliverables/clara-daily-audit-latest.md`;
- mantém operação read-only.

Cron OpenClaw configurado:
- Nome: `IVS Clara/Z-API Safety Audit diário`
- Job ID: `6bbea434-eefb-41dc-b8f9-802d35cd03cf`
- Horário: todos os dias às 08:15, timezone `America/Bahia`
- Regra de comunicação: reportar Tiaro somente em severidade MÉDIA/ALTA ou mudança operacional relevante.

## Pré-consulta Safety Monitor

Monitora o app de pré-consulta sem contato com paciente e sem alteração de produção.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/preconsulta_safety_monitor.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_preconsulta_cockpit.py \
  --out /root/deliverables/cockpit-preconsulta-ivs.html \
  --json-out /root/deliverables/cockpit-preconsulta-ivs.json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/preconsulta_daily_audit.py --json
```

Verifica:
- disponibilidade HTTP do app;
- JSONs válidos;
- submissões;
- drafts e drafts antigos;
- submissões sem markdown no cérebro;
- registros incompletos;
- fila fallback Telegram.

Cron OpenClaw:
- Nome: `IVS Pré-consulta Safety Audit diário`
- Job ID: `a608fe14-c009-49a7-82b2-b2c8152d9a59`
- Horário: todos os dias às 08:25, timezone `America/Bahia`.

## Marketing OS Monitor — João

Monitora a operação de marketing e continuidade do João sem publicar em canais externos e sem alterar produção.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/marketing_os_monitor.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_marketing_os_cockpit.py \
  --out /root/deliverables/cockpit-marketing-os-joao-ivs.html \
  --json-out /root/deliverables/cockpit-marketing-os-joao-ivs.json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/marketing_os_daily_audit.py --json
```

Verifica:
- backlog marketing no painel único;
- entregáveis HTML recentes de marketing/João;
- presença no outbound permitido para anexo Telegram;
- regras canônicas do João;
- marcadores de risco em sessões recentes do João;
- documentos de marketing atualizados nos últimos 7 dias.

Cron OpenClaw:
- Nome: `IVS Marketing OS João Audit diário`
- Job ID: `9e37d4c8-fc40-4413-9c58-e86576ca3e63`
- Horário: todos os dias às 08:35, timezone `America/Bahia`.

## Cockpit Geral — IVS Agent Operating Layer

Consolida Clara/Z-API, Pré-consulta e Marketing OS/João em visão executiva read-only.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/ivs_agent_layer_monitor.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_ivs_agent_layer_cockpit.py \
  --out /root/deliverables/cockpit-geral-ivs-agent-operating-layer.html \
  --json-out /root/deliverables/cockpit-geral-ivs-agent-operating-layer.json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/ivs_agent_layer_daily_audit.py --json
```

Cron OpenClaw:
- Nome: `IVS Agent Operating Layer Audit consolidado diário`
- Job ID: `4b645967-fc1a-4967-81bf-b424f2e301cc`
- Horário: todos os dias às 08:45, timezone `America/Bahia`.

Regras:
- não contatar pacientes;
- não publicar externamente;
- não pausar/despausar Clara;
- não alterar produção;
- reportar Tiaro apenas em ALTA/MÉDIA ou mudança relevante.

## Workflow Registry

Camada formal de workflows operacionais do IVS Agent Operating Layer.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/workflow_registry.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_workflow_registry_cockpit.py \
  --out /root/deliverables/workflow-registry-ivs-agent-operating-layer.html \
  --json-out /root/deliverables/workflow-registry-ivs-agent-operating-layer.json
```

Workflows atuais:
- `followup-seguro`
- `preconsulta-safety`
- `marketing-os`
- `agent-layer-audit`

## Regra operacional — sequências de atividades do Tiaro

Quando Tiaro informar uma sequência de atividades, lista, lote ou checklist, Maria deve usar esta skill como camada padrão de orquestração.

Procedimento:
1. transformar a sequência em plano curto;
2. mapear cada etapa para um workflow do registry;
3. executar primeiro checks read-only;
4. separar ações seguras de ações sensíveis;
5. pedir autorização explícita para envio real, pausa/despausa, alteração de produção, contato com paciente/lead ou mudança canônica;
6. reportar workflow usado, evidência, bloqueios e próximo passo.

Workflow canônico para esse caso: `sequencia-operacional`.

## Cron Governance

A skill mantém um inventário dos crons ativos e dos crons cancelados por perda de sentido operacional.

Arquivos:
- `/root/.openclaw/workspace/skills/ivs-agent-operating-layer/crons/CRON-REGISTRY.md`
- `/root/.openclaw/workspace/skills/ivs-agent-operating-layer/crons/active-crons.json`
- `/root/.openclaw/workspace/skills/ivs-agent-operating-layer/crons/removed-crons.json`

Regra:
- auditorias específicas substituídas pelo `IVS Agent Operating Layer Audit` viram checks sob demanda;
- crons externos de paciente/produção são rastreados, não removidos sem revisão específica;
- crons com falha recorrente e baixo valor operacional são removidos quando já houver cobertura consolidada.

Workflow canônico: `cron-governance`.

## Autonomia Evolutiva dos Agentes

Tiaro determinou que Maria, Clara, João, Pedro e os agentes do conselho devem evoluir de forma autônoma com aprendizado de pesquisas, perfis públicos de Instagram/X e canais do YouTube.

Workflow canônico: `agent-learning-autonomy`.

Arquivos:
- `/root/.openclaw/workspace/skills/ivs-agent-operating-layer/learning/agent-learning-registry.json`
- `/root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_learning_autonomy.py`
- relatórios em `/root/.openclaw/reports/ivs-agent-learning/`

Cron diário:
- `bb73a900-3b75-47e9-bcb9-e43620a758ab`
- 06:10 America/Bahia
- gera briefs de aprendizado por agente, sem anunciar se estiver OK.

Governança:
- aprendizado externo vira hipótese, não regra automática;
- classificação obrigatória: aplicar amanhã, testar 3 dias, descartar ou propor RC-25;
- regra fixa/memória estrutural exige Maria/Tiaro e graphify/RC-25;
- nunca copiar literalmente, prometer resultado ou transformar conteúdo externo em decisão clínica/financeira/jurídica.

## Skills OpenFang-inspired adicionadas

A partir da análise do OpenFang como referência de Agent Operating System, foram adicionadas três skills IVS-first, sem copiar código externo:

### IVS Agent Capability Registry

Inventário read-only de agentes, skills, subagentes, workflows e riscos.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-capability-registry/scripts/capability_registry.py --json
```

Workflow canônico: `capability-governance`.

### IVS Agent Handoff Guard

Gera pacotes seguros de transferência entre Maria, Clara, João, Pedro e conselhos.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-handoff-guard/scripts/handoff_packet.py \
  --from maria-gerente --to clara-whatsapp \
  --subject "Assunto" \
  --context "Contexto" \
  --next-action "Próxima ação" \
  --sensitivity lead
```

Workflow canônico: `handoff-operacional`.

### IVS Agent Observability Events

Normaliza logs e eventos de Z-API, workflows e entregáveis em feed redigido/read-only.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-observability-events/scripts/agent_events.py --json
```

Workflow canônico: `observability-events`.

## Workflow Runner + Event Store

Camada de execução rastreável para workflows operacionais. Não executa ações sensíveis; registra estado, evidência, bloqueios e eventos redigidos.

```bash
# iniciar execução
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/workflow_runner.py start \
  --workflow handoff-operacional \
  --subject "Retomada de lead" \
  --context "Lead respondeu ao follow-up" \
  --sensitivity lead

# atualizar estado
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/workflow_runner.py update \
  --run-id RUN_ID \
  --state completed \
  --message "Handoff validado"

# listar runs/eventos
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/workflow_runner.py show
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/workflow_runner.py events

# cockpit
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_workflow_runs_cockpit.py \
  --out /root/deliverables/cockpit-workflow-runs-ivs.html \
  --json-out /root/deliverables/cockpit-workflow-runs-ivs.json
```

Estados aceitos: `started`, `in_progress`, `blocked`, `completed`, `failed`, `cancelled`.

## Agent Permission Matrix + Policy Gate

Matriz objetiva de permissões por agente e ação: `read_only`, `dry_run`, `write_with_approval` ou `forbidden`.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/permission_gate.py \
  --agent clara-whatsapp \
  --action followup_whatsapp \
  --sensitivity lead
```

Arquivos:
- `/root/.openclaw/workspace/skills/ivs-agent-operating-layer/policies/agent-permission-matrix.json`
- `/root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/permission_gate.py`
- workflow: `permission-governance`

Regra: o policy gate avalia, mas não executa a ação. Ações `write_with_approval` continuam exigindo autorização explícita e evidência.

## Cockpit Único IVS Agent OS

Visão executiva consolidada de capacidades, workflows, runs, eventos e matriz de permissões.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_agent_os_cockpit.py \
  --out /root/deliverables/cockpit-unico-ivs-agent-os.html \
  --json-out /root/deliverables/cockpit-unico-ivs-agent-os.json
```

Regra: read-only. O cockpit não envia mensagens, não altera produção e não substitui autorização explícita para ações sensíveis.

## Auditoria Diária IVS Agent OS

Executa o cockpit único, compara com baseline anterior e gera relatório diário read-only.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_daily_audit.py --json
```

Saídas:
- `/root/deliverables/cockpit-unico-ivs-agent-os.html`
- `/root/deliverables/cockpit-unico-ivs-agent-os.json`
- `/root/deliverables/agent-os-daily-audit-latest.md`

Workflow: `agent-os-daily-audit`.

## Action Gate + Approval Ledger

Camada final de governança para ações sensíveis. Registra aprovação explícita e avalia a ação combinando Permission Gate + Approval Ledger. Não executa a ação.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/approval_ledger.py add \
  --agent maria-gerente --action pause_clara \
  --approved-by Tiaro --evidence "ordem explícita" --scope "manutenção" --ttl-minutes 60

python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/action_gate.py \
  --agent maria-gerente --action pause_clara --sensitivity pause_clara --approval-id APPROVAL_ID
```

Workflow: `action-gate-approval`.

## Sensitive Action Enforcement

Guard reutilizável para scripts que possam acionar ações sensíveis. Ele consulta o Action Gate e falha fechado quando a política exige aprovação.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/sensitive_action_guard.py \
  --agent pedro-controller-ivs --action omie_write --sensitivity financial --mode enforce
```

Workflow: `sensitive-action-enforcement`.

## Hardening Final: backup, cockpit vivo e alertas

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_retention_backup.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_live_agent_os_cockpit.py
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_critical_alerts.py --json
```

Workflows: `agent-os-retention-backup`, `agent-os-live-cockpit`, `agent-os-critical-alerts`.

## Analytics e Approval Console

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_agent_os_trends.py
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_approval_console.py
```

Workflows: `agent-os-trends`, `approval-console`.

## Command Center CLI

Entrada única segura para rotinas do Agent OS:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py status
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py refresh-all
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py test
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py backup
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py gate --agent pedro-controller-ivs --action omie_write --sensitivity financial
```

Workflow: `agent-os-command-center`.

## Cockpit interno protegido e CI local

Servidor local protegido por token, bind padrão em `127.0.0.1`:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cockpit_server.py --print-token
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cockpit_server.py
```

CI local:

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_ci.py --json
```

Workflows: `agent-os-protected-cockpit-server`, `agent-os-local-ci`.

## Drift Detection e Pipeline RC-25

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_drift_detector.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/generate_agent_os_artifact_index.py
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_rc25_pipeline.py --json
```

Workflows: `agent-os-drift-detection`, `agent-os-rc25-pipeline`.

## Disaster Recovery

Verificação de backup e plano de restore dry-run. Não restaura automaticamente.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_backup_verify.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_restore_planner.py --json
```

Workflow: `agent-os-disaster-recovery`.

## Security Compliance

Scanner read-only de secrets e manifest de integridade.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_secrets_scanner.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_integrity_manifest.py
```

Workflow: `agent-os-security-compliance`.

## Readiness Scorecard e Release Bundle

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_readiness_scorecard.py --json
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_release_bundle.py --json
```

Workflows: `agent-os-readiness-scorecard`, `agent-os-release-bundle`.

## Cron Governance Final

Auditoria read-only dos crons reais do Gateway contra o registry operacional do Agent OS.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cron_auditor.py --json
```

Workflow: `agent-os-cron-governance-final`.

## Serviço do Cockpit Protegido

Gerenciador local do servidor protegido do cockpit. Não imprime token e mantém bind em `127.0.0.1`.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cockpit_service.py status
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cockpit_service.py start
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cockpit_service.py restart
```

Workflow: `agent-os-protected-cockpit-service`.

## Offsite Backup Readiness

Prepara exportação externa de backup sem enviar dados por padrão. Export real exige `--apply`, destino explícito e aprovação.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_offsite_backup.py --json
```

Workflow: `agent-os-offsite-backup-readiness`.

## Production Activation Plan

Plano faseado para ativar produção/enforcement do IVS Agent OS. Por padrão é read-only: valida readiness e recomenda a fase segura. Não ativa toggles sensíveis.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_activation_plan.py --json
```

Workflow: `agent-os-production-activation-plan`.

## Clara Action Gate Shadow — Phase 1

Validação read-only/dry-run antes de qualquer enforcement da Clara. Não envia WhatsApp real e não altera `CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE`.

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/clara_action_gate_shadow.py --json
```

Workflow: `clara-action-gate-shadow`.
