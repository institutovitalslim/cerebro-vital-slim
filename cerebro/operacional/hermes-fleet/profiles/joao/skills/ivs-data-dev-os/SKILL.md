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

- `references/content-engine-weekly-sprint.md`: Sprint Semanal, família de conteúdo e briefing herdado.
- `references/content-engine-performance-learning.md`: Fase 3 do Content Engine OS — publicação vinculada ao criativo, importação governada de métricas, dashboard por variável e retroalimentação do próximo sprint.
- `references/vital-slim-tracker-patient-portal-replit-lessons.md`: lições de produto/arquitetura e execução Replit para sistemas com ambiente profissional + portal paciente mobile, incluindo o pitfall de não presumir Plan mode antes de mandar comando direto de Build.
- `references/replit-patient-portal-dev-lessons.md`: lições operacionais para apps Replit com painel profissional + portal paciente mobile, comandos diretos de Build, validação de escrita real e separação de origem dos dados.
- `references/replit-patient-portal-qa-confirm-flow.md`: receita de QA real para fluxos mobile de registro em etapas (`Tipo → Itens/foto → Conferir → Salvar`), incluindo bug de botão sem `onClick` no Button real, uso de logs temporários e critério de aceite via preview/browser.
- `references/replit-patient-portal-soft-delete-p1-p2-lessons.md`: lições P1/P2 do portal paciente mobile — feedback pós-salvamento, editar/remover/repetir refeição, câmera/preview local, soft delete com `deletedAt`, filtros em todos os consumidores e visão profissional de pacientes sem registro hoje.
- `references/replit-patient-portal-p1-mobile-ux-lessons.md`: lições P1 do portal paciente mobile — feedback pós-salvamento, repetir sem salvar direto, editar/remover refeição recente, foto local sem upload, favoritos com feedback, validação real no preview e comandos Replit atômicos.
- `references/replit-patient-portal-p3-onboarding-reminder-lessons.md`: lições P3 do portal paciente mobile — onboarding por paciente, lembrete local de refeição pendente, validação de handler real do CTA, cache bust/HMR no Replit e QA com backup/restauração de `localStorage`.
- `references/replit-patient-portal-p4-team-adherence-lessons.md`: lições P4/P4.1 do portal paciente/profissional — cockpit read-only de aderência da equipe, cálculo por dias distintos, data local sem UTC, fila por severidade hoje/48h/3d/7d, filtros `deletedAt/status` e validação real com soft delete temporário.
- `references/replit-patient-portal-p4-adherence-lessons.md`: lições P4 do portal profissional — cockpit de aderência semanal, pacientes sem registro por período, filtros `!deletedAt/status !== deleted`, proibição de notificação/lançamento pelo profissional e QA com simulação/restauração de `localStorage`.
- `references/replit-login-gated-build-validation.md`: padrão para quando o Replit aguarda validação de login/rota protegida no browser; testar preview real com credenciais demo, checar console/guardrails e devolver evidência ao Replit para continuar o build.
- `references/replit-mobile-click-handler-debugging.md`: lições para depurar CTAs mobile no preview Replit quando o DOM aparece mas o clique não dispara; cobre markers de bundle, Vite overlays, Plan/Build flipping, shadcn/form pitfalls, bottom nav interceptando clique e validação ponta a ponta de registro de refeição.
- `references/replit-patient-portal-build-mode-click-debugging.md`: lições para Replit alternando Plan/Build durante QA de portal paciente, botões mobile que visualmente clicam mas não mudam estado, Vite overlays, marcadores de bundle e CTAs fixos acima do nav.
- `references/replit-professional-login-consent-qa-lessons.md`: lições para QA de área profissional protegida por LGPD/login demo em Replit, incluindo consentimento que renderiza mas não dispara, markers DOM, `preventDefault/stopPropagation` em iframe/React e validação de `/dashboard`, `/refeicoes`, `/evolucao` e `/relatorio`.
- `references/replit-plan-build-flapping-browser-qa.md`: lições para quando o Replit alterna entre Plan/Build durante correções; usar prompts cirúrgicos, marcador DOM temporário, QA real por cadeia de handlers e tratar Plan mode recorrente como bloqueio operacional antes de declarar conclusão.
- `references/replit-patient-portal-build-mode-qa-lessons.md`: lições de Build/Plan mode no Replit, QA real no browser, handlers de botões/formulários em portal paciente e workaround de adicionar alimento direto pelo clique na linha quando a detail view fica frágil.
- `references/replit-patient-portal-build-mode-qa-loop.md`: loop prático para apps Replit com portal paciente, aceite LGPD/localStorage, botões críticos sem handler, cache/HMR stale e Replit alternando Plan/Build enquanto espera evidência de browser.
- `references/replit-patient-professional-portal-qa-lessons.md`: checklist final para apps Replit com portal paciente + área profissional, cobrindo smoke HTTP, consentimentos LGPD separados, login demo, persistência entre papéis, markers DOM temporários e pitfalls de botões em iframe/nav fixo.
- `references/replit-patient-portal-whatsapp-access-button.md`: padrão para botão profissional “Enviar acesso por WhatsApp” após cadastro do paciente, com `wa.me` pré-preenchido, revisão humana obrigatória, mensagem segura e QA real do link/código.
- `references/replit-patient-portal-p15-final-qa-lessons.md`: checklist P15 de aceite final para MVP/demo de portal paciente + área profissional, incluindo cadastro com accessCode, WhatsApp com/fallback sem telefone, registrar/salvar/editar/remover/repetir refeição, base alimentar anti-duplicação, rotas, console e padrão de relatório “MVP fechado vs produção pendente”.
- `references/replit-patient-portal-p15-mvp-qa-lessons.md`: checklist P15 para fechar MVP Replit com painel profissional + portal paciente — smoke, cadastro com `accessCode`, WhatsApp com/fallback sem telefone, registrar/editar/remover/repetir refeição, base alimentar sem duplicidade, rotas profissionais e distinção entre MVP funcional aprovado vs acabamento de logs temporários.
- `references/replit-patient-portal-p15-final-qa-lessons.md`: gate final P15 para fechar MVP em apps Replit com área profissional + portal paciente; cobre smoke, LGPD/login, cadastro novo com `accessCode`, WhatsApp com/fallback sem telefone, CTA Registrar, base alimentar sem duplicação, editar/remover/repetir e console.
- `references/replit-patient-portal-anti-refresh-debugging.md`: padrão para diagnosticar e corrigir sensação de refresh/reload em apps Replit com portal paciente, separando erro real de HMR de polling/redirect de autenticação, com validação por estabilidade de 20–30s no browser.
- `references/replit-patient-access-code-localstorage-seed.md`: padrão para diagnosticar código de paciente recém-criado que falha em outro navegador/dispositivo quando o MVP usa `localStorage`; cobre repro, seed compartilhado, bump de versão e validação do portal.
- `references/replit-food-database-expansion-anti-dup-qa.md`: padrão para expandir bases alimentares em apps Replit sem duplicar registros, com auditoria por ID/nome/sinônimos, validação de warnings React de chave duplicada e evidência browser para destravar o Replit quando ele aguarda validação.t-access-code-localstorage-seed.md`: padrão para diagnosticar código de paciente recém-criado que falha em outro navegador/dispositivo quando o MVP usa `localStorage`; cobre repro, seed compartilhado, bump de versão e validação do portal.
- `references/replit-food-database-expansion-anti-dup-qa.md`: padrão para expandir bases alimentares em apps Replit sem duplicar registros, com auditoria por ID/nome/sinônimos, validação de warnings React de chave duplicada e evidência browser para destravar o Replit quando ele aguarda validação.
- `references/replit-food-base-qa-lessons.md`: QA final para base alimentar ampliada no portal paciente Replit, incluindo busca por sinônimos brasileiros, fluxo registrar→conferir→salvar, validação do link WhatsApp e pitfall de IDs/keys duplicadas em alimentos.
- `references/replit-patient-portal-barcode-scanner-qa.md`: padrão para implementar e validar consulta de alimentos por código de barras no portal paciente, com câmera/scanner como caminho principal, digitação manual como fallback, base local de produtos e QA contra bottom nav interceptando o CTA.
- `references/replit-patient-portal-barcode-scanner-lessons.md`: padrão para adicionar consulta por código de barras no portal paciente Replit com câmera/scanner como caminho principal, fallback manual, base local demo, fluxo produto encontrado→rascunho→conferir→salvar e pitfall de CTA coberto pela navegação inferior.
- `references/replit-patient-portal-cross-browser-barcode-camera.md`: lição específica para scanner por câmera em iPhone/Safari e navegadores sem `BarcodeDetector` nativo; usar `getUserMedia` + polyfill cross-browser, evitar no-support prematuro, e validar fallback manual/CTA.
- `references/replit-barcode-bottom-nav-interception.md`: QA específico para scanner/barcode em portal paciente quando cards/CTAs renderizados são interceptados pela bottom nav; usar `elementFromPoint` no centro do botão, corrigir padding/spacer/safe-area e só concluir quando o clique não navegar para a aba inferior errada.

## Content Engine OS — checkpoints de fase

Quando Tiaro pedir para "seguir para a próxima fase" do Content Engine OS, não basta implementar uma tela isolada: feche o ciclo operacional com contrato de API, UI, smoke, validação real, **publicação no subdomínio do sistema**, commit e push. GitHub é obrigatório para versionamento, mas **não conta como publicação da entrega**; a entrega só está concluída quando estiver acessível e validada no subdomínio operacional, por exemplo `https://conteudo.institutovitalslim.com.br/<rota>`.

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
13. Em Replit QA, `browser_click` com sucesso não prova handler funcionando. Se o DOM/storage/rota não mudam, reportar como “clique recebido, estado não mudou” e corrigir handler/layout. Em mobile preview, botões no fim do conteúdo podem ficar sob nav fixo/iframe; mova CTAs críticos para área fixa acima do nav com z-index alto, ou use uma ação já comprovada no list row para o MVP.
14. HTTP 200 não prova build saudável: Vite overlay também pode responder 200. Se o preview mostrar `[plugin:vite:*]` ou erro JSX, capturar arquivo/linha exatos e corrigir compilação antes de continuar QA funcional.
13. Em Replit MCP, `phase: updating` não prova que um patch foi aplicado. Se o preview ainda mostra o bug ou o marcador de versão não aparece, perguntar read-only ao Replit se voltou para Plan mode antes de continuar. Quando o Agent alternar para Plan mode, pedir ao Tiaro para acionar Build e reenviar comando cirúrgico com um único critério de aceite.
14. Em fluxos paciente por etapas, valide a cadeia inteira de handlers: login/consentimento → seleção → busca → adicionar → conferir → salvar → reflexo na home/relatório. Se um botão renderiza mas não muda estado, trate o preview como fonte de verdade e peça patch mínimo do handler real.
15. Quando um botão em detail view falha mas o clique no item da lista funciona, simplifique o MVP: faça o clique do item adicionar diretamente com porção padrão e deixe ajuste de porção como etapa secundária. Isso evita forms aninhados, Button custom e event bubbling no caminho crítico.
16. Em área profissional protegida por consentimento, validar com storage limpo e rota protegida real (`/relatorio`) antes de declarar sucesso. Se o botão de aceite renderiza mas não troca estado, evitar `preventDefault`/`stopPropagation` em `pointerdown/mousedown` e IIFE com `let fired`; use botão nativo com `onClick` simples, grave a chave LGPD e troque para o formulário por estado React. Ver `references/replit-professional-login-consent-qa-lessons.md`.
17. Em apps com portal paciente + área profissional, quando o time precisar enviar acesso ao portal por WhatsApp, implemente como handoff manual: botão/link `Enviar acesso por WhatsApp` no card/lista/detalhe do paciente, `wa.me` com texto pré-preenchido via `encodeURIComponent`, `data-testid="send-access-whatsapp"`, e nunca envio automático. Validar no DOM que o link contém nome, `/paciente/login`, `accessCode` e Instituto Vital Slim; testar paciente recém-criado e limpar QA depois. Ver `references/replit-patient-portal-whatsapp-access-button.md`.
18. Quando Tiaro pedir P15 ou fechamento de MVP em Replit, tratar como gate de aceite, não como resumo. Rode smoke de rotas, QA profissional, cadastro de paciente novo, WhatsApp com telefone e fallback sem telefone, login paciente, registro/conferir/salvar, base alimentar sem duplicação, dashboard/telas e console. Não declarar MVP fechado se novo paciente não gera `accessCode`/card de acesso, se CTA principal não navega, ou se `Editar`/`Remover`/`Repetir` renderizam mas não alteram estado. Ver `references/replit-patient-portal-p15-final-qa-lessons.md`.
19. Em MVP Replit com portal paciente, validar códigos recém-criados em **navegador limpo ou storage zerado**, não só no mesmo browser do painel profissional. Se o código existe no painel mas falha no portal limpo, o root cause provável é `localStorage` isolado por navegador/dispositivo; corrigir com camada compartilhada de pacientes/códigos ou seed demo comum. Ver `references/replit-patient-portal-cross-browser-access-codes.md`.
18. Em bases alimentares/listagens buscáveis em Replit, ampliar dados com anti-duplicação explícita: auditar `id`, nome normalizado, `nomePopular` e sinônimos antes de adicionar; enriquecer item existente quando houver equivalência; manter IDs únicos e validar no browser a busca do termo problemático com console limpo. Se o Replit ficar “aguardando você”, fazer a validação real e devolver evidência objetiva para ele continuar. Ver `references/replit-food-database-expansion-anti-dup-qa.md`.
18. Ao ampliar base alimentar em portal paciente, validar no browser real com busca por termos e sinônimos brasileiros (`aipim`, `mandioca`, `macaxeira`, `frango`, `ovo`) e depois conferir o console. Warnings React de key duplicada em alimento (`Encountered two children with the same key`) são pendência de QA: corrigir IDs/keys únicos antes de declarar conclusão. Ver `references/replit-food-base-qa-lessons.md`. 
19. Em fluxo de código de barras no portal paciente, câmera/scanner deve ser o caminho principal e digitação manual o fallback obrigatório. Produto encontrado vira sugestão revisável e deve convergir para o mesmo draft da busca manual; nunca salvar automaticamente. Em preview mobile, validar se **todo card/CTA relevante** (`produto demo`, resultado manual, `Adicionar à refeição`, `Conferir`, `Salvar`) está fisicamente clicável com `document.elementFromPoint` no centro do botão — bottom nav fixa pode interceptar o clique e navegar para `Progresso`. Se `elementFromPoint` retornar link da nav, corrigir layout/padding/spacer/safe-area antes de mexer mais no handler. Ver `references/replit-patient-portal-barcode-scanner-qa.md` e `references/replit-barcode-bottom-nav-interception.md`.
19. Em fluxo de código de barras no portal paciente, câmera/scanner deve ser o caminho principal e digitação manual o fallback obrigatório. Produto encontrado não salva sozinho: precisa adicionar ao rascunho, mostrar `Conferir refeição` e só então salvar. Em mobile/Replit, validar se o CTA `Adicionar à refeição` não está fisicamente sob a bottom nav usando `document.elementFromPoint` no centro do botão; se estiver, mover o CTA para cima/sticky e adicionar padding inferior. Ver `references/replit-patient-portal-barcode-scanner-lessons.md`.
20. Para scanner por câmera cross-browser, não tratar ausência de `window.BarcodeDetector` nativo como falta de suporte. Se `getUserMedia` existe, tentar câmera com polyfill/biblioteca compatível; só mostrar no-support quando câmera APIs forem realmente indisponíveis. Em Replit/Vite/pnpm, cuidado com `@zxing/browser` + peer deps de `@zxing/library`, que pode gerar root em branco/`Invalid hook call`; para MVP, preferir polyfill auto-contido como `barcode-detector/polyfill`. Ver `references/replit-patient-portal-cross-browser-barcode-camera.md`.
13. Em Replit MCP, `phase: updating` não prova que um patch foi aplicado. Se o preview ainda mostra o bug ou o marcador de versão não aparece, perguntar read-only ao Replit se voltou para Plan mode antes de continuar. Quando o Agent alternar para Plan mode, pedir ao Tiaro para acionar Build e reenviar comando cirúrgico com um único critério de aceite.
14. Em portais mobile com fluxo multi-etapas, se um botão em detail view/custom Button/form não dispara mesmo após patch, simplificar o caminho feliz: mover a ação primária para um clique já comprovado no preview (ex.: clicar na linha do alimento adiciona direto com porção padrão) e deixar ajustes finos como etapa posterior. Não insistir em múltiplas camadas de `preventDefault`/`stopPropagation` sem evidência de avanço.
13. Em portais paciente Replit com aceite LGPD/localStorage, separar o diagnóstico por transição: se o bypass manual de `localStorage` libera o login e o pós-login funciona, o bug está no handler do consentimento/botão, não no fluxo inteiro. Reporte essa evidência estreita ao Replit.
14. Quando um botão crítico renderiza mas não muda estado (`Adicionar à refeição`, `Conferir`, `Salvar`), suspeitar de custom Button perdendo handler, `type` incorreto, submit interceptado ou `<form>` aninhado. Validar no browser real e pedir patch mínimo com botão nativo/handler explícito antes de declarar bloqueio maior.
15. Se o Replit responder que edits foram aplicados mas o preview continua igual, fazer hard-refresh/cache bust e checar storage/DOM novamente. Se persistir, confirmar Plan/Build mode e pedir execução em Build mode com critério de aceite; não concluir baseado no autorrelato do Agent.

## Verification Checklist

- [ ] `validate --json` retorna ok.
- [ ] Todo agente tem dono, tools permitidas, sensitivity e output schema.
- [ ] Toda ferramenta tem permission_mode e risk_level.
- [ ] Toda fonte tem owner, sensitivity e redaction_policy.
- [ ] Bench v0 roda sem dados reais.
- [ ] Dashboard HTML foi gerado.
- [ ] Nenhum secret, telefone, nome de paciente ou token aparece no output.
