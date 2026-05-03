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

### A4. Confirmação do tópico numérico de "Pacientes"
- **Frente:** Telegram / Atendimento
- **Problema resumido:** o tópico "Pacientes" já existe conceitualmente, mas o `topic_id` numérico ainda não está confirmado no mapa canônico
- **Próximo passo:** confirmar o `topic_id` e mapear a área canônica correspondente
- **Status:** aberto de mapeamento — atualizado em 2026-05-03
- **Fonte de verdade:** `cerebro/telegram-topics.md`

### A5. Notion — credencial de API não habilitada para João
- **Frente:** Operações / Inteligência
- **Problema resumido:** João tem ferramenta de leitura Notion instalada (`notion_reader.py`), mas sem token/permissão operacional configurada
- **Próximo passo:** Tiaro gerar token de integração Notion, compartilhar página/database, validar leitura
- **Status:** aberto — aguardando credencial
- **Fonte de verdade:** `memory/2026-05-02.md`

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
- o bloco crítico mais sensível foi fechado
- o principal aberto estrutural agora é a consolidação do próprio painel único como porta mestra
- o restante é majoritariamente governança contínua e disciplina operacional
