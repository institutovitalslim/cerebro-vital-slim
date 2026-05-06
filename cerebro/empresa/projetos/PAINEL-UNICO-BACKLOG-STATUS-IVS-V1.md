# Painel Único de Backlog e Status - IVS (V1 Preenchida)

## Objetivo
Dar leitura executiva rápida do que está aberto, fechado, monitorado e onde está a fonte de verdade de cada frente.

---

## 1. Abertos reais

### A1. Redução de dispersão entre camadas
- **Frente:** Governança / Operações
- **Problema resumido:** parte dos aprendizados ainda nasce em relatório ou memória antes de ganhar porta única definitiva
- **Próximo passo:** continuar promovendo recorrências reais para índices, playbooks, checklists e projetos
- **Status:** monitoramento contínuo
- **Fonte de verdade:** `cerebro/empresa/projetos/pendencias.md`

### A2. Disciplina operacional dos scripts de recuperação
- **Frente:** Atendimento
- **Problema resumido:** os scripts e mensagens foram fortalecidos, mas ainda precisam virar uso operacional consistentemente aplicado
- **Próximo passo:** manter uso recorrente e revisar aderência no atendimento real
- **Status:** monitoramento contínuo
- **Fonte de verdade:** `cerebro/areas/atendimento/checklist-atendimento-clara.md`

### A4. Notion — governança de uso e canonização dos bunkers
- **Frente:** Operações / Inteligência
- **Problema resumido:** a leitura do Notion foi validada, mas ainda falta consolidar a governança oficial de quais páginas/bunkers o João deve consultar por padrão e como tratar duplicidades
- **Próximo passo:** manter mapa oficial dos bunkers, registrar IDs canônicos e decidir se páginas variantes devem ser mantidas ou arquivadas
- **Status:** monitoramento contínuo após validação real
- **Fonte de verdade:** `cerebro/areas/marketing/agentes/agente-reels-intel/JOAO-FONTES-E-FERRAMENTAS.md`

### A5. Entrega de HTML no Telegram sem workaround inadequado
- **Frente:** Operações / Entregáveis
- **Problema resumido:** materiais extensos e apresentações HTML precisam chegar como anexo `.html` visível e abrível no tópico correto; ZIP e colagem de código HTML não são aceitos como entrega principal.
- **Próximo passo:** corrigir rota/conector de envio de HTML no tópico correto e validar entrega real.
- **Status:** aberto operacional
- **Fonte de verdade:** `memory/2026-05-04.md` + `cerebro/empresa/projetos/pendencias.md`

### A6. 21st.dev / MCP magic21st ainda não homologado
- **Frente:** Tecnologia / Skills
- **Problema resumido:** ferramenta segue sem API key válida e sem teste real do MCP, portanto não pode ser tratada como recurso canônico.
- **Próximo passo:** obter credencial válida, testar em sandbox e só então decidir homologação.
- **Status:** aberto/bloqueado por credencial e teste real
- **Fonte de verdade:** `memory/2026-05-04.md`

### A7. Hyperframes/HeyGen — piloto controlado antes de adoção
- **Frente:** Marketing / Vídeo programático
- **Problema resumido:** Hyperframes parece útil para Reels programáticos, overlays e templates, mas ainda é versão 0.x, depende de Node/FFmpeg/render headless e não substitui editor/avatar/plataforma final.
- **Próximo passo:** executar piloto em sandbox com 1 Reel vertical 1080x1920 de 15s, sem dados de paciente, medindo qualidade, tempo, ajuste, peso e reaproveitamento.
- **Status:** aprovado apenas para teste em sandbox
- **Fonte de verdade:** `memory/2026-05-05.md`


### A8. Apresentação V2.3 do paciente Erick
- **Frente:** Empresa / Apresentações / Conversão médica
- **Problema resumido:** a V2.2 melhorou, mas ficou prolixa e redundante; precisa perder 25% a 35% do texto sem perder exames, questionário, SPIN e condução médica.
- **Próximo passo:** implementar cortes cirúrgicos recomendados pelo Conselho Growth e validar fluidez para uso pela médica.
- **Status:** aberto operacional
- **Fonte de verdade:** `memory/2026-05-05.md` + `skills/geracao-apresentacao-paciente/SKILL.md`

### A9. Clara — aprendizado externo com governança
- **Frente:** Atendimento / Inteligência operacional
- **Problema resumido:** RC-27/RC-28/RC-29 e crons silenciosos foram criados; o risco agora é aprendizado externo virar regra fixa sem validação ou ruído anti-compliance.
- **Próximo passo:** monitorar relatórios em `/root/.openclaw/reports/clara-learning/` e só promover aprendizados com classificação e validação.
- **Status:** monitoramento contínuo após consolidação
- **Fonte de verdade:** `memory/2026-05-05.md` + skill `clara-learning-orchestrator`

---

## 2. Fechados reais

### F1. Painel único de backlog e status
- **Resultado:** painel criado, preenchido e canonizado como porta executiva principal de governança
- **Status:** fechado
- **Fonte:** `cerebro/empresa/projetos/PAINEL-UNICO-BACKLOG-STATUS-IVS-V1.md`

### F2. Correção intertópicos da manutenção diária
- **Resultado:** a rotina de manutenção foi formalmente corrigida para não falhar por causa do tópico atual
- **Status:** fechado
- **Fonte:** `cerebro/manutencao/ROTINA-DIARIA-0100.md`

### F3. Validação real do João no tópico 5782
- **Resultado:** João validado em produção no tópico correto de Reels
- **Status:** fechado
- **Fonte:** `cerebro/telegram-topics.md`

### F4. Handoff/manual takeover da Clara
- **Resultado:** regra promovida, código endurecido, validação controlada executada e bridge re-pausada por segurança
- **Status:** fechado
- **Fonte:** `cerebro/areas/atendimento/checklist-atendimento-clara.md` + documentação da bridge

### F5. Fluxo único de produção de vídeo
- **Resultado:** o fluxo saiu de rascunho e virou referência canônica de operação
- **Status:** fechado na camada estrutural
- **Fonte:** `cerebro/areas/marketing/fluxo-unico-producao-video-ivs.md`

### F6. Ativo operacional de bioimpedância da Clara
- **Resultado:** vídeo salvo em caminho estável e incorporado ao playbook/checklist
- **Status:** fechado
- **Fonte:** `cerebro/areas/atendimento/checklist-atendimento-clara.md`

### F7. Logo oficial no template de apresentação
- **Resultado:** o template base da skill de apresentação foi atualizado para usar os ativos oficiais já presentes no brand kit do IVS
- **Status:** fechado
- **Fonte:** `skills/geracao-apresentacao-paciente/assets/template-apresentacao.html`

---

### F8. Correção de rótulo do tópico do João (Reels → Marketing)
- **Resultado:** tópico operacional do João confirmado como Marketing `5782`, rótulo semântico corrigido e gateway reiniciado
- **Status:** fechado
- **Fonte:** `cerebro/telegram-topics.md` + `cerebro/telegram-topic-agent-routing.json`

### F9. Confirmação canônica do tópico "Pacientes"
- **Resultado:** `topic_id` do tópico **Pacientes** confirmado como `271` e mapa canônico atualizado
- **Status:** fechado
- **Fonte:** `cerebro/telegram-topics.md`

### F10. Modelo de subagentes sob demanda do João
- **Resultado:** Tiaro aprovou biblioteca interna de especialidades acionadas sob demanda, em vez de 12 agentes fixos; regra foi promovida para cérebro, graphify e runtime do agente.
- **Status:** fechado como decisão operacional; uso por especialidade segue monitorado para futura promoção
- **Fonte:** `cerebro/areas/marketing/agentes/agente-reels-intel/JOAO-SUBAGENTES-SOB-DEMANDA.md`

### F11. Prompt-master incorporado seletivamente
- **Resultado:** referência pública foi aproveitada como estrutura de engenharia de prompt para ferramentas web e prompt visual, sem adoção crua como skill oficial.
- **Status:** fechado como incorporação seletiva
- **Fonte:** `cerebro/areas/marketing/agentes/agente-reels-intel/JOAO-PROMPTS-PARA-FERRAMENTAS-WEB.md`

## 3. Monitoramentos contínuos

### M1. Novos pedidos recorrentes do Tiaro
- manter expansão do índice conforme a linguagem real de pedido aparecer
- fonte: `cerebro/operacional/INDEX-PEDIDOS-RECORRENTES.md`

### M2. Nomes técnicos de skill vs linguagem do Tiaro
- revisar se os nomes internos continuam aderentes à linguagem operacional real
- fonte: `cerebro/operacional/ITENS-AMBIGUOS-A-AUDITAR.md`

### M3. Relatórios HTML virando conhecimento recuperável
- evitar que relatório importante fique só em `relatorios/`
- fonte: `relatorios/` + `pendencias.md`

### M4. Bridge da Clara sem regressão
- monitorar deduplicação, cooldown, circuit breaker e ownership humano após mudanças futuras
- fonte: `cerebro/operacional/ITENS-AMBIGUOS-A-AUDITAR.md`

### M5. Fluxo de vídeo mantendo aderência prática
- garantir que a operação real continue obedecendo o fluxo único e checklist curto
- fonte: `cerebro/areas/marketing/fluxo-unico-producao-video-ivs.md`

### M6. Avaliação de ferramentas externas sem promoção indevida
- separar referência, piloto em sandbox, homologação e skill oficial
- fonte: `cerebro/operacional/ITENS-AMBIGUOS-A-AUDITAR.md`

### M7. Subagentes sob demanda do João
- monitorar volume e ganho operacional por especialidade antes de qualquer agente fixo
- fonte: `cerebro/areas/marketing/agentes/agente-reels-intel/JOAO-SUBAGENTES-SOB-DEMANDA.md`

### M8. Conselho Growth virando briefing executável
- evitar que parecer estratégico aprovado fique apenas em relatório; quando aprovado, virar especificação, checklist ou pendência explícita
- fonte: `cerebro/operacional/INDEX-PEDIDOS-RECORRENTES.md` + `skills/geracao-apresentacao-paciente/SKILL.md`

### M9. Aprendizado externo da Clara com filtro RC-29
- checar se crons de Instagram/YouTube/X geram aplicação operacional sem copiar conteúdo externo e sem virar regra automática
- fonte: `memory/2026-05-05.md` + relatórios `clara-learning`

---

## 4. Fontes canônicas por frente

### Atendimento
- porta principal: `cerebro/areas/atendimento/checklist-atendimento-clara.md`

### Marketing
- porta principal: `cerebro/areas/marketing/fluxo-unico-producao-video-ivs.md`

### Governança / Backlog
- porta principal: `cerebro/empresa/projetos/pendencias.md`

### Recuperabilidade operacional
- porta principal: `cerebro/operacional/INDEX-PEDIDOS-RECORRENTES.md`

### Avaliação de ferramentas / skills / MCPs
- porta principal: `cerebro/operacional/ITENS-AMBIGUOS-A-AUDITAR.md`

### Ambiguidades e risco de ruído
- porta principal: `cerebro/operacional/ITENS-AMBIGUOS-A-AUDITAR.md`

### Tópicos Telegram e memória transversal
- porta principal: `cerebro/telegram-topics.md`

---

## 5. Risco de dispersão

### R1. Relatório sem promoção
- risco: aprendizado importante ficar só em HTML
- contenção: revisar relatórios e promover recorrências

### R2. Memória diária sem porta única
- risco: decisão real existir, mas ficar difícil de recuperar
- contenção: promover para checklist, playbook, índice ou projeto

### R3. Item já fechado reaparecer como aberto
- risco: retrabalho por contexto incompleto
- contenção: manter bloco de fechados reais atualizado

### R4. Tópico especializado ser confundido com isolamento de conhecimento
- risco: falha de continuidade entre áreas
- contenção: reforçar a regra intertópicos e manutenção transversal

---

## 6. Leitura executiva de hoje
- os abertos factuais críticos foram fechados
- a leitura do Notion pelo João foi validada em produção
- o ponto remanescente é governança de uso dos bunkers e tratamento de duplicidades/variantes
- o restante é majoritariamente governança contínua e disciplina operacional
