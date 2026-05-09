# GRAPH_REPORT — OpenFang como referência para IVS Agent Operating Layer

## Resumo

Tiaro aprovou seguir usando a arquitetura do OpenFang como referência prática. Foi implementada a primeira melhoria IVS-first: a skill `ivs-agent-operating-layer`, com o módulo `Clara Safety Monitor`.

## Nós principais

- OpenFang / Agent OS: referência arquitetural, não dependência de produção.
- IVS Agent Operating Layer: camada própria sobre OpenClaw.
- Clara Safety Monitor: primeira Hand operacional.
- Z-API Bridge: fonte auditada.
- Exclusões Clara: bloqueios de paciente e do_not_reply.
- Leads State: base de leads ativos.
- Workflow Follow-up Seguro: próximo módulo.

## Relações

- `OpenFang` INSPIRA `IVS Agent Operating Layer`.
- `IVS Agent Operating Layer` CONTÉM `Clara Safety Monitor`.
- `Clara Safety Monitor` LÊ `clara_exclusions.json`.
- `Clara Safety Monitor` LÊ `clara_leads_state.json`.
- `Clara Safety Monitor` LÊ `clara_control_state.json`.
- `Clara Safety Monitor` CONSULTA `http://127.0.0.1:8787/healthz`.
- `Clara Safety Monitor` NÃO_ENVIA `WhatsApp`.
- `Clara Safety Monitor` NÃO_PAUSA `Clara`.
- `patient_do_not_reply` BLOQUEIA `follow-up ativo`.
- `patient_bridge_known` BLOQUEIA `follow-up ativo` salvo exceção explícita.
- `lead_exception*` / `tiaro_lead_exception` PODE_LIBERAR `lead específico` mediante revisão.

## Auditoria de primeira execução

- Bridge health: OK.
- Pausa global: false.
- Exclusões totais: 396.
- `patient_do_not_reply`: 6.
- `patient_bridge_known`: 390.
- Leads ativos: 25.
- Colisões active lead + bloqueio paciente-like: 25.

## Decisão operacional

Manter a abordagem conservadora: colisões não são liberadas automaticamente. O monitor aponta o problema para revisão; quem decide exceção é Tiaro/Maria conforme contexto.

## Checklist RC-25

- [x] Código criado fora de produção crítica.
- [x] Modo somente leitura.
- [x] Sem envio WhatsApp.
- [x] Sem pausa/despausa Clara.
- [x] Cópia canônica registrada no cérebro.
- [x] Primeiro relatório gerado.

## Incremento — Workflow Follow-up Seguro

Foi adicionado o script `followup_safety_check.py` como preflight operacional para envio ativo de WhatsApp:

- valida telefone/mensagem;
- consulta exclusões locais;
- consulta estado de lead;
- bloqueia paciente/do_not_reply por padrão;
- permite modo `local-only` para auditoria sem HTTP;
- modo real exige dupla confirmação explícita por flag;
- pode chamar `/admin/send` em dry-run para validação server-side.

Teste inicial executado com telefone fictício em `--local-only`, sem envio; o teste confirmou bloqueio conservador por `patient_bridge_known` quando há exclusão.

## Incremento — Cockpit Clara/Z-API

Foi adicionado o gerador `generate_clara_cockpit.py`, que produz HTML read-only com os principais indicadores da Clara/Z-API:

- saúde do bridge;
- pausa global;
- leads ativos;
- exclusões totais;
- `patient_do_not_reply`;
- `patient_bridge_known`;
- overrides manuais ativos;
- colisões lead ativo + bloqueio paciente-like;
- amostras para revisão operacional.

Arquivo gerado: `/root/deliverables/cockpit-clara-zapi-ivs.html`.

## Incremento — Auditoria diária automática

Foi adicionado `clara_daily_audit.py` para executar auditoria read-only com baseline/delta.

Primeira execução:
- severidade: BAIXA;
- baseline criado;
- bridge saudável;
- Clara não pausada;
- colisões lead + paciente-like: 25;
- overrides manuais ativos: 3.

Cron configurado no OpenClaw:
- Job ID: `6bbea434-eefb-41dc-b8f9-802d35cd03cf`;
- todos os dias às 08:15 BRT (`America/Bahia`);
- reportar Tiaro somente em exceções relevantes;
- rotina não envia WhatsApp e não altera estado da Clara.

## Incremento — Pré-consulta Safety Monitor

Foi criado o módulo read-only de segurança da pré-consulta:

- `preconsulta_safety_monitor.py`: audita app, JSONs, drafts, markdowns, fallback Telegram e inconsistências;
- `generate_preconsulta_cockpit.py`: gera cockpit HTML;
- `preconsulta_daily_audit.py`: cria baseline/delta e relatório Markdown diário.

Primeira execução:
- app HTTP disponível;
- JSONs: 1;
- submissões: 1;
- drafts: 0;
- achado ALTA: 1 submissão sem markdown correspondente (`Tiaro Fernandes Neves`, submissão de 2026-04-24). Este achado exige investigação antes de afirmar que dados existem ou pedir novo preenchimento em casos futuros.

Cron configurado:
- Job ID: `a608fe14-c009-49a7-82b2-b2c8152d9a59`;
- todos os dias às 08:25 BRT;
- rotina não contata paciente e não altera produção.

## Incremento — Marketing OS Monitor João

Foi criado o módulo read-only de monitoramento do Marketing OS/João:

- `marketing_os_monitor.py`: audita backlog marketing, entregáveis HTML, outbound Telegram, regras canônicas e sinais de sessão;
- `generate_marketing_os_cockpit.py`: gera cockpit HTML premium;
- `marketing_os_daily_audit.py`: cria baseline/delta e relatório Markdown diário.

Primeira execução ajustada:
- backlog marketing ativo: 7 itens;
- HTMLs recentes de marketing: 2;
- HTMLs de marketing fora do outbound: 0;
- regras canônicas ausentes: 0;
- achados: backlog marketing ativo e marcadores de risco em sessões recentes do João.

Cron configurado:
- Job ID: `9e37d4c8-fc40-4413-9c58-e86576ca3e63`;
- todos os dias às 08:35 BRT;
- rotina não publica, não altera produção e não executa tarefas no lugar do João.

## Incremento — Cockpit Geral IVS Agent Operating Layer

Foi criado o módulo consolidado read-only:

- `ivs_agent_layer_monitor.py`: executa e normaliza Clara/Z-API, Pré-consulta e Marketing OS/João;
- `generate_ivs_agent_layer_cockpit.py`: gera cockpit executivo HTML consolidado;
- `ivs_agent_layer_daily_audit.py`: cria baseline/delta consolidado e relatório Markdown diário.

Primeira execução consolidada:
- severidade geral: ALTA;
- Clara/Z-API: MÉDIA por leads ativos bloqueados como paciente-like;
- Pré-consulta: ALTA por submissão sem markdown correspondente;
- Marketing OS/João: MÉDIA por marcador de sessão e backlog ativo.

Cron configurado:
- Job ID: `4b645967-fc1a-4967-81bf-b424f2e301cc`;
- todos os dias às 08:45 BRT;
- rotina não contata pacientes, não publica externamente e não altera produção.

## Incremento — Workflow Registry

Foi criada a camada formal de workflows do IVS Agent Operating Layer.

Workflows registrados:
- `followup-seguro`: follow-up Clara/Z-API com preflight e bloqueios de paciente;
- `preconsulta-safety`: segurança de submissões, drafts e markdowns;
- `marketing-os`: continuidade operacional do João e entregáveis de marketing;
- `agent-layer-audit`: consolidação executiva dos monitores.

Arquivos:
- `workflows/*.json`;
- `workflow_registry.py`;
- `generate_workflow_registry_cockpit.py`.

Validação inicial:
- workflows registrados: 4;
- findings de validação: 0;
- status: válido.

## Regra — Sequências de atividades do Tiaro

Tiaro determinou que, quando enviar uma sequência de atividades, Maria deve usar as novas skills/workflows do IVS Agent Operating Layer como camada padrão de execução.

Implementação:
- criado workflow `sequencia-operacional`;
- atualizado `SKILL.md` com a regra operacional;
- registry validado com 5 workflows e 0 findings.

Regra prática:
- transformar sequência em plano;
- mapear cada item para workflow;
- executar checks read-only primeiro;
- pedir autorização explícita para ações sensíveis;
- reportar evidência, bloqueios e próximos passos.

## Governança de Crons

Tiaro pediu revisão dos crons ativos e cancelamento dos que perderam sentido.

Resultado:
- crons ativos após limpeza: 19;
- crons cancelados: 10;
- novo workflow registrado: `cron-governance`;
- registry validado: 6 workflows, 0 findings.

Crons cancelados por redundância/baixo valor/falha recorrente:
- auditorias específicas Clara/Z-API, Pré-consulta e Marketing OS, substituídas pelo audit consolidado;
- slots externos de Clara Learning Instagram manhã/tarde, YouTube e X/Twitter, com falhas recorrentes e baixa utilidade independente;
- revisão 21:20 redundante com auditoria 21:30 e Graphify 22:05;
- crons legados silenciosos sem função operacional independente.

Arquivos:
- `crons/CRON-REGISTRY.md`;
- `crons/active-crons.json`;
- `crons/removed-crons.json`.

## Autonomia Evolutiva dos Agentes

Tiaro determinou que todos os agentes — Maria, Clara, João, Pedro e agentes do conselho — devem ser autônomos em relação à própria evolução baseada em aprendizado de pesquisas, perfis públicos de Instagram/X e canais do YouTube.

Implementação:
- criado workflow `agent-learning-autonomy`;
- criado registry `/learning/agent-learning-registry.json` com fontes, objetivos e uso por agente;
- criado script `agent_learning_autonomy.py` para gerar briefs diários por agente;
- skills `ivs-agent-operating-layer`, `rapidapi-social-learning` e `youtube-learning-ivs` vinculadas a Maria, Clara, João, Pedro, Conselho Growth e LLM Council;
- prompts dos agentes receberam bloco de governança de autonomia evolutiva;
- gateway recarregado via SIGUSR1;
- criado cron diário `bb73a900-3b75-47e9-bcb9-e43620a758ab` às 06:10 America/Bahia para gerar briefs sem ruído quando OK.

Governança:
- aprendizado externo vira hipótese operacional, não regra automática;
- classificação obrigatória: aplicar amanhã, testar 3 dias, descartar ou propor RC-25;
- nenhuma regra clínica, financeira, jurídica ou canônica muda sem Maria/Tiaro e graphify/RC-25;
- conteúdo externo não deve ser copiado literalmente nem exposto a pacientes/leads como bastidor.

Validação:
- registry de workflows: 7 workflows, 0 findings;
- primeiro brief gerado para 6 agentes.
