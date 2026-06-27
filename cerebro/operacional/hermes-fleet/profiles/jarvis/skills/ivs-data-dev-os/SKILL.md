---
name: ivs-data-dev-os
description: "Use when Tiaro/Maria want to design, build, evaluate, or govern IVS software and data-intelligence systems with a multi-agent pipeline: discovery, architecture, data contracts, implementation, QA, security, release, observability, and executive reporting."
version: 1.0.0
author: Maria — Instituto Vital Slim
license: Proprietary-IVS
metadata:
  hermes:
    tags: [ivs, data-intelligence, software-development, multi-agent, governance, lgpd]
    related_skills: [ivs-agent-operating-layer, repo-reverse-ivs, quality-driven-dev, security-compliance]
---

# IVS Data Dev OS

## Overview

IVS Data Dev OS é a camada operacional para criar sistemas internos do Instituto Vital Slim com uma cadeia multiagente mais governada e mais útil que um coding agent genérico. A inspiração arquitetural vem do reverse de Codebuff/Freebuff, mas a implementação é IVS-first: dados sensíveis protegidos, agentes por etapa, registry de ferramentas, contratos de dados, avaliação contínua, rastreabilidade, LGPD e entrega executiva em HTML.

A regra central: **não existe agente decorativo**. Cada agente precisa reduzir risco, aumentar qualidade ou acelerar uma etapa mensurável.

## When to Use

Use quando o pedido envolver:
- criar sistema interno, dashboard, cockpit, relatório automatizado ou pipeline de dados;
- transformar demanda do Tiaro em arquitetura técnica;
- organizar agentes diferentes com skills/ferramentas específicas por etapa;
- cruzar fontes IVS como QuarkClinic, Z-API, Omie, Ads, Drive, pré-consulta ou cérebro;
- criar benchmark/evals para medir qualidade de agentes ou relatórios;
- definir segurança, LGPD, redaction, approval gates e observabilidade antes de build;
- mapear ferramentas externas de conteúdo/SaaS e transformar seus padrões em módulos soberanos dentro do Content Engine OS.

Não use para atendimento direto a paciente/lead, decisão clínica, escrita real sem aprovação, ou cópia direta de código externo para produção.

## North Star

Toda entrega deve sair com problema/métrica claros, fontes e contratos definidos, agentes e ferramentas com permissões explícitas, pipeline read-only/dry-run primeiro, bench, trace sanitizado e relatório executivo.

## Regra operacional IVS — desenvolvimento por padrão

Tiaro determinou que **todo desenvolvimento solicitado a qualquer agente IVS** deve usar esta skill (`ivs-data-dev-os`) como padrão operacional antes de qualquer skill complementar. Isso vale para sistemas internos, dashboards, pipelines, integrações, automações, APIs, correções técnicas, evolução de agentes e melhorias de produto/infraestrutura. Carregue esta skill primeiro, depois complemente com skills específicas como `quality-driven-dev`, `security-compliance`, `ivs-agent-operating-layer`, `repo-reverse-ivs`, ou skills de marketing/design conforme o caso.

## Pipeline Multiagente Padrão

| Etapa | Agente | Função | Saída obrigatória |
|---|---|---|---|
| 1 | Product Analyst IVS | traduz demanda em problema, usuário, métrica e escopo | problem brief |
| 2 | Solution Architect IVS | define arquitetura, serviços, integrações e tradeoffs | architecture plan |
| 3 | Data Architect IVS | define fontes, schemas, lineage e qualidade | data contract |
| 4 | Security/LGPD Guard IVS | classifica sensibilidade, PII, secrets e permissões | risk gate |
| 5 | Builder IVS | implementa scripts, APIs, dashboards ou automações | diff/artefato |
| 6 | QA/Bench Engineer IVS | cria testes, bench e valida regressões | test report |
| 7 | Release Engineer IVS | prepara deploy/rollback/cron/observabilidade | release packet |
| 8 | Executive Narrator IVS | transforma resultado em decisão executiva | HTML/briefing |

## Regras de Governança

- `lead`, `patient`, `clinical` e `financial` exigem redaction por padrão.
- Relatórios gerais não exibem nome, telefone, token, e-mail privado ou dado clínico identificável.
- Dados reais entram apenas por fonte governada e em modo read-only inicialmente.
- WhatsApp/Z-API, QuarkClinic e Omie em escrita real exigem autorização explícita e gates canônicos IVS.
- Cada ferramenta deve declarar permission_mode, sensitivity_allowed, risco, logs e evidências.
- Em sistemas com múltiplos atores, defina antes do build **quem cria cada dado**. Exemplo IVS: profissional pode cadastrar paciente/metas e acompanhar/revisar; refeição/foto diária deve nascer no módulo do paciente, não no painel profissional, salvo fluxo explicitamente marcado como simulação/revisão.
- Em protótipos de paciente, separar `professional dashboard` e `patient portal` com sessão/role explícita, `tenantId`, `patientId`, origem do dado e avisos de demo/LGPD.

## Referências complementares

- `references/content-engine-editorial-ingest.md`: Sprint Semanal, família de conteúdo e briefing herdado.
- `references/content-engine-web-pain-desire-ingest.md`: ingestão governada de perguntas/dúvidas públicas da web como dores e desejos do avatar mestre no Content Engine OS (`story_themes`, `themes`, `manual_themes`, `opportunities`, `content_pattern_library`).
- `references/content-engine-performance-learning.md`: Fase 3 do Content Engine OS — publicação vinculada ao criativo, importação governada de métricas, dashboard por variável e retroalimentação do próximo sprint.

- `references/replit-patient-portal-dev-lessons.md`: lições operacionais para apps Replit com painel profissional + portal paciente mobile, comandos diretos de Build, validação de escrita real e separação de origem dos dados.
- `references/replit-patient-portal-qa-confirm-flow.md`: receita de QA real para fluxos mobile de registro em etapas (`Tipo → Itens/foto → Conferir → Salvar`), incluindo bug de botão sem `onClick` no Button real, uso de logs temporários e critério de aceite via preview/browser.
- `references/replit-patient-portal-soft-delete-p1-p2-lessons.md`: lições P1/P2 do portal paciente mobile — feedback pós-salvamento, editar/remover/repetir refeição, câmera/preview local, soft delete com `deletedAt`, filtros em todos os consumidores e visão profissional de pacientes sem registro hoje.
- `references/replit-patient-portal-p1-mobile-ux-lessons.md`: lições P1 do portal paciente mobile — feedback pós-salvamento, repetir sem salvar direto, editar/remover refeição recente, foto local sem upload, favoritos com feedback, validação real no preview e comandos Replit atômicos.
- `references/replit-patient-portal-p3-onboarding-reminder-lessons.md`: lições P3 do portal paciente mobile — onboarding por paciente, lembrete local de refeição pendente, validação de handler real do CTA, cache bust/HMR no Replit e QA com backup/restauração de `localStorage`.
- `references/replit-patient-portal-p4-team-adherence-lessons.md`: lições P4/P4.1 do portal paciente/profissional — cockpit read-only de aderência da equipe, cálculo por dias distintos, data local sem UTC, fila por severidade hoje/48h/3d/7d, filtros `deletedAt/status` e validação real com soft delete temporário.
- `references/replit-patient-portal-p4-adherence-lessons.md`: lições P4 do portal profissional — cockpit de aderência semanal, pacientes sem registro por período, filtros `!deletedAt/status !== deleted`, proibição de notificação/lançamento pelo profissional e QA com simulação/restauração de `localStorage`.
- `references/replit-login-gated-build-validation.md`: padrão para quando o Replit aguarda validação de login/rota protegida no browser; testar preview real com credenciais demo, checar console/guardrails e devolver evidência ao Replit para continuar o build.

## Content Engine OS — checkpoints de fase

Quando Tiaro pedir para "seguir para a próxima fase" do Content Engine OS, não basta implementar uma tela isolada: feche o ciclo operacional com contrato de API, UI, smoke, validação real, **publicação no subdomínio do sistema**, commit e push. GitHub é obrigatório para versionamento, mas **não conta como publicação da entrega**; a entrega só está concluída quando estiver acessível e validada no subdomínio operacional, por exemplo `https://conteudo.institutovitalslim.com.br/<rota>`.

### Blog científico IVS em VPS com aprovação médica

Quando Tiaro pedir blog científico/médico, biblioteca pública de autoridade, conteúdo assinado pela Dra. Daniely ou publicação em subdomínio como `blog.institutovitalslim.com.br`, use o padrão em `references/medical-blog-vps-approval-workflow.md`. Regra central: se um post leva assinatura da Dra. Daniely, a aprovação médica precisa ser um gate técnico com `approved_by`, `approved_at`, hash da versão aprovada e audit log; qualquer alteração após aprovação invalida a publicação até nova aprovação.

- Fase 1: `Sprint → Produção → Banco de Criativos → Aprovar → Calendário → Publicado → Métrica → BI`.
- Fase 2: loop de aprendizado a partir das peças medidas.
- Fase 3: aprendizado real por performance — precisa registrar publicação, importar métricas governadas, ranquear variáveis vencedoras (`format`, `hook`, `objection`, `cta`, `visual`, `pillar`, `origin_tag`) e retroalimentar o Sprint Semanal.
- Fase 4: radar externo e engenharia reversa — precisa ingerir sinais públicos por fonte governada/RapidAPI ou payload manual, manter ingestão idempotente por `tenant_id + source_network + external_id`, gerar `reverse_engineering`, consolidar `content_pattern_library`, criar oportunidades `external_learning`, expor `/radar-externo`, validar contrato `fase_4_external_reverse_engineering` e preservar governança read-only. Detalhes: `references/content-engine-phase4-external-learning.md`.
- Fase 5: científico/compliance premium — precisa criar gate pré-publicação para claims clínicos: serviço central de assessment, tabela `compliance_assessments`, seed/registry em `scientific_sources`, endpoints `/compliance/overview`, `/compliance/review-text`, `/compliance/creatives/{id}/assess`, UI `/compliance`, integração com aprovação/calendário e bloqueio de publicação quando `risk_level=high`. Validar contrato `fase_5_scientific_compliance`, build web, smoke e teste real de texto com promessa/diagnóstico/prescrição. Detalhes: `references/content-engine-phase5-scientific-compliance.md`.

Pitfall: depois de `docker restart`, o web pode retornar 502 temporário enquanto o Next recompila/sobe. Aguarde readiness e rode o smoke novamente antes de concluir falha.

## Comandos

```bash
python3 /root/.hermes/skills/ivs-data-dev-os/scripts/ivs_data_dev_os.py validate --json
python3 /root/.hermes/skills/ivs-data-dev-os/scripts/ivs_data_dev_os.py registry --json
python3 /root/.hermes/skills/ivs-data-dev-os/scripts/ivs_data_dev_os.py dashboard --out /root/deliverables/ivs-data-dev-os-dashboard.html --json-out /root/deliverables/ivs-data-dev-os-dashboard.json --json
python3 /root/.hermes/skills/ivs-data-dev-os/scripts/ivs_data_dev_os.py bench --out /root/deliverables/ivs-data-dev-os-bench.json --json
python3 /root/.hermes/skills/ivs-data-dev-os/scripts/ivs_data_dev_os.py scaffold --project-name cockpit-leads-ads --out-dir /root/.openclaw/workspace/projects/cockpit-leads-ads --json
```

## Workflow de execução

1. **Frame** — defina problema, dono, métrica, prazo e decisão que o sistema informará. Completo quando há `problem_brief` com métrica de sucesso.
2. **Mapeie fontes** — consulte `data-source-registry.json` e marque sensibilidade. Completo quando cada fonte tem dono, modo, acesso e redaction.
3. **Monte agentes** — selecione agentes no registry. Completo quando cada agente tem ferramentas e output schema.
4. **Gate de segurança** — avalie se é read-only, dry-run ou write_with_approval. Completo quando ações sensíveis estão bloqueadas ou têm approval explícito.
5. **Build pequeno** — implemente o menor fluxo testável com dados sintéticos/sanitizados. Completo quando o artefato roda localmente.
6. **Bench** — rode tarefas de avaliação e registre score. Completo quando há scorecard e falhas priorizadas.
7. **Entrega executiva** — gere HTML/briefing com fonte, confiança, decisão sugerida e próximos passos.

### Autonomia depois de “pode seguir”

Quando Tiaro autorizar continuidade com “pode seguir”, “siga até o final” ou equivalente em desenvolvimento de app/sistema, não pedir confirmação em microetapas reversíveis. Continue executando, validando e corrigindo até entregar artefato funcional ou até encontrar bloqueio técnico real já verificado com tentativa alternativa. Só interrompa para pedir decisão quando houver risco alto/irreversível, gasto, escrita externa sensível ou ambiguidade que mude o produto.

## Receita: Stories Engine / Stories 10x no Content Engine OS

Quando projetar ou melhorar módulos de stories dentro do Content Engine OS, use a referência `references/stories10x-content-engine-mapping.md`. Ela resume o funcionamento do AppBumper/Stories 10x e a versão IVS-first recomendada: sequências, stories, temas, produtos, CTAs, debriefing, tracking e integração Clara/Z-API.

Para implementação concreta no Content Engine OS, siga também `references/stories-engine-ivs-implementation.md`: spec antes de código, migration idempotente, endpoints de themes/products/handoff, UI `/stories-engine`, smoke dedicado e validação pública. Para fases avançadas de tracking, export, analytics, contrato Clara por `origin_tag` e relatório semanal, use `references/stories-engine-phase2-phase3.md`.

Regra: não faça apenas clone visual. O diferencial IVS é fechar o ciclo `story → CTA → WhatsApp/Clara → lead/agendamento → debrief/aprendizado` com compliance healthcare. O handoff para Clara deve ser governado, sem envio automático, com UTM/tag/texto pré-preenchido e orientação SPIN para não pular direto para agendamento.

## Receita: Content Engine OS — redesign operacional

Quando Tiaro/Maria pedirem para analisar, corrigir, refazer ou elevar o Content Engine OS, use `references/content-engine-os-redesign.md`. O alvo é um cockpit operacional de autoridade, não um conjunto de páginas soltas. A estrutura deve guiar o usuário por: `sinal → tese → família de conteúdo → aprovação → publicação → BI → próxima rodada`.

Ative somente os agentes do pipeline desta skill (`Product Analyst IVS`, `Solution Architect IVS`, `Data Architect IVS`, `Security/LGPD Guard IVS`, `Builder IVS`, `QA/Bench Engineer IVS`, `Release Engineer IVS`, `Executive Narrator IVS`) antes de recorrer a habilidades complementares. O padrão de produto é: próxima ação clara em até 10 segundos, criação por família de conteúdo, aprovação explícita, BI acionável e zero PII.

Quando a melhoria envolver produção por formato, BI social, métricas de seguidores/interações ou busca ativa governada, use também `references/content-engine-production-social-selling.md`. A produção deve separar Carrosséis, Estáticos e Reels, mantendo Stories no Stories Engine; o Social Selling deve priorizar interatores públicos para abordagem manual, sem DM automática, disparo em massa, diagnóstico ou promessa.

Quando a correção envolver `/producao/carrosseis`, fila de peças recentes ou revisão de slides, use `references/content-engine-carousel-review-fixes.md`. Pitfalls obrigatórios: módulos travados por formato também precisam filtrar a listagem; correções de carrossel devem ser acumulativas por slide; “solicitar melhoria” deve regerar de fato, limpar renders antigos e não exibir assets stale enquanto `asset_url` estiver nulo.

Quando a evolução envolver transformar o Content Engine OS em uma máquina semanal de posicionamento, use `references/content-engine-weekly-sprint.md`. Padrão: `/sprint-semanal`, `weekly-command` API, tese/pilar antes de peça, família com Reels + Carrossel + Stories + Estático, hook selector para Reels, briefing herdado por querystring nos módulos de produção, rodapé/disclaimer obrigatório em toda legenda aplicado no prompt e no backend, e governança `plan_only` sem publicação/DM automática.

Quando Tiaro/Maria enviarem DOCX/XLSX/TXT para alimentar o Content Engine OS com hooks, temas, roteiros, régua de mídia ou stories, use `references/content-engine-editorial-ingest.md`. Padrão: extrair com `python-docx`/`openpyxl`, criar script idempotente com `origin` do lote, gravar em `viral_scripts`, `themes`, `story_themes` e/ou `narrative_devices`, validar por endpoints públicos e manter tudo como repertório editorial interno sem publicação, DM, Z-API, QuarkClinic ou Omie. Para detalhes práticos do lote 2026-06-23 — validação do Weekly Command, pitfalls de `psycopg LIKE` e correção de `.next` stale — consulte `references/content-engine-editorial-ingest-20260623-lessons.md`.

Quando Tiaro pedir que perguntas/dúvidas públicas encontradas na web entrem como dores e desejos do avatar mestre, use `references/content-engine-web-pain-desire-ingest.md`. Padrão: manter dados agregados e públicos, criar origem idempotente, gravar em `story_themes`, `themes`, `manual_themes`, `opportunities` e `content_pattern_library`, validar smoke e API pública correta (`https://conteudo.institutovitalslim.com.br/api/...`, não apenas `127.0.0.1` quando o smoke usa domínio público).

## Receita: Content Engine OS quebrado

Quando testar/corrigir o sistema de conteúdo (`/root/cerebro-vital-slim/sistemas/content-engine-os`):

1. Reproduza com loop curto: `python3 scripts/content_engine_smoke.py --json`.
2. Verifique build web: `cd apps/web && npm run build`.
3. Verifique Python: `python3 -m compileall apps/api render_worker scripts -q`.
4. Verifique API pública por `/api/*` e renders por `/renders/*`; Nginx precisa rotear `/renders/` para a FastAPI (`127.0.0.1:8010/renders/`).
5. Verifique `content-render.service`; Higgsfield no worker deve ser opt-in (`HF_ENABLE=1`), nunca bloqueante por padrão.
6. Depois de build local em volume montado, reinicie `content-engine-web` para evitar `.next` inconsistente no Next dev server.

Conclusão mínima: smoke `ok:true`, criativo teste `renderizado`, PNG público `200 image/png`, web `/criar` `200`, commit + push.

## Referências complementares

- `references/content-engine-weekly-sprint.md` — sprint semanal de posicionamento, hook selector, briefing herdado e governança de legenda.
- `references/content-engine-phase1-editorial-flow.md` — contrato e validação da Fase 1 operacional: aprovar criativo → calendário → publicado → métrica → BI.
- `references/content-engine-phase2-learning-loop.md` — contrato e validação da Fase 2: métricas registradas → ranking de vencedores → recomendações → próxima tese do Sprint Semanal.
- `references/higgsfield-cli-content-os-map.md` — roteamento Higgsfield CLI para Content Engine OS, com fonte canônica no cérebro.

## Common Pitfalls

1. Criar muitos agentes cedo demais; comece com nucleares.
2. Confundir relatório bonito com inteligência; toda conclusão precisa de fonte, confiança e ação.
3. Vazar PII em log; use hash, contagem, reason code e evidência sanitizada.
4. Pular bench; sem avaliação, o sistema é frágil.
5. Escrever produção antes de ler bem; primeiro read-only, depois dry-run, depois approval.
6. Ao mapear SaaS externo autenticado, não alterar dados nem publicar; observe, documente entidades/fluxos e transforme em design IVS-first sem copiar conteúdo proprietário literalmente.
7. Em projetos Replit, não presumir que o Agent está preso em Plan mode só porque ele pede Build mode ou parece aguardando. Primeiro mande um comando direto de execução/construção; só classifique como bloqueio real depois de tentar o comando direto e validar o status.
8. Quando o Replit alternar Build/Plan e os lotes grandes falharem, reduza para comandos **mínimos e atômicos**: um arquivo por vez, uma edição bem delimitada, sem pedir checkpoint no meio. Validar cada escrita com `ask_question` curto antes de avançar para o próximo arquivo. Se comandos técnicos por arquivo continuarem sem escrever, reformule como **pedido natural de produto** com guardrails e critérios de aceite; em Replit MCP isso pode destravar melhor que insistir em “edite arquivo X”.
9. Em sistemas de acompanhamento com paciente + equipe, não misturar papéis: se o paciente é quem coleta/lança dados no mobile, o ambiente profissional deve acompanhar/revisar/gerar acesso — não virar tela de lançamento em nome do paciente, salvo fluxo explicitamente marcado como simulação/revisão.
10. Em QA de Replit, não confiar apenas no autorrelato do Agent. Se o preview/browser mostrar que um botão não avançou, uma rota não abriu ou uma etapa não renderizou, tratar a evidência visual como fonte de verdade e mandar correção mínima direcionada.
11. Em fluxos mobile por etapas, validar o **handler real do botão** no DOM/preview, não só o texto visual. Se o label mudou mas o clique não avança, patchar o `onClick` no Button que renderiza o texto real, adicionar log temporário rastreável e exigir evidência: etapa de confirmação visível, salvamento, redirecionamento e reflexo no painel profissional.
12. Quando o Replit disser ou o usuário informar que a construção está aguardando teste de login pelo browser, não tentar destravar apenas com novo prompt. Abrir o preview, testar `/login` com credenciais demo fornecidas pelo app/usuário, validar pós-login, console e rota-chave da fase, e só então enviar ao Replit a evidência objetiva para continuar o Build.

## Verification Checklist

- [ ] `validate --json` retorna ok.
- [ ] Todo agente tem dono, tools permitidas, sensitivity e output schema.
- [ ] Toda ferramenta tem permission_mode e risk_level.
- [ ] Toda fonte tem owner, sensitivity e redaction_policy.
- [ ] Bench v0 roda sem dados reais.
- [ ] Dashboard HTML foi gerado.
- [ ] Nenhum secret, telefone, nome de paciente ou token aparece no output.
