# Itens Ambíguos a Auditar

## Itens auditados e corrigidos em 30/04/2026

### 1. Pedidos recorrentes ainda não formalizados
**Risco:** baixa recuperabilidade por linguagem natural.
**Correção:** índice de pedidos recorrentes foi expandido com apresentações, Instagram, vídeo, objeções, boletos, histórico, memória da Clara e backlog aberto.

### 2. Backlog que existia em relatório mas não em pendência explícita
**Risco:** demanda some entre tópicos.
**Correção:** `cerebro/empresa/projetos/pendencias.md` ganhou seção específica de governança e recuperabilidade.

### 3. Conhecimento operacional sem porta única clara
**Risco:** a Clara sabe, mas não encontra.
**Correção:** `PORTAS-UNICAS-DE-EXECUCAO.md` foi reforçado com Omie, histórico e apresentações.

### 4. Papel do operacional como backlog recuperável
**Risco:** a camada operacional ficar só como índice, sem função real de resgate.
**Correção:** `cerebro/operacional/README.md` passou a explicitar essa função.

## Itens resolvidos (arquivados em 03/05/2026)

### 5. Handoff/manual takeover da Clara — resolvido em 01/05/2026 → arquivado em 03/05/2026
**Risco original:** a bridge reativar a Clara no meio de atendimento humano sem trava real.
**Status final:** **resolvido e arquivado**. O aprendizado foi promovido para checklist/playbook, o código da bridge foi endurecido, a validação real controlada confirmou bloqueio por ownership humano. Monitoramento contínuo transferido para `cerebro/areas/atendimento/checklist-atendimento-clara.md`.

### 6. Tópico Reels validado pós-correção — resolvido em 01/05/2026 → arquivado em 03/05/2026
**Risco original:** confusão entre 768 e 5782 no roteamento do João.
**Status final:** **resolvido e arquivado**. Tiaro validou em 2026-05-01 que o João está respondendo corretamente no tópico real `5782` (tópico Marketing). Documentação canônica corrigida em `cerebro/telegram-topics.md` e `cerebro/telegram-topic-agent-routing.json`. O rótulo "Reels" foi corrigido para "Marketing" no roteamento.

## Itens vivos para manutenção contínua
- novos pedidos recorrentes ainda não observados
- possíveis nomes técnicos de skill que ainda não batem 100% com a linguagem do Tiaro
- futuros relatórios HTML que precisem ser promovidos a pendência ou porta operacional
- bridge da Clara: manter monitoramento contínuo de deduplicação, cooldown, circuit breaker e ownership humano para evitar regressão após futuras mudanças

## Item adicionado em 03/05/2026

### 7. Notion — governança de bunkers e duplicidades após validação de acesso
**Risco original:** o João até consegue ler o Notion, mas sem governança oficial de quais bunkers consultar por padrão e como tratar páginas variantes/duplicadas a operação pode voltar a dispersar.
**Status atual:** **vivo/monitoramento contínuo**. A leitura real já foi validada com token funcional e páginas compartilhadas; o ponto aberto passou a ser governança de uso, mapa oficial dos bunkers e tratamento de duplicidades.
**Próximo passo:** manter lista canônica dos bunkers/páginas prioritárias no arquivo operacional do João e decidir se variantes devem ser mantidas ou arquivadas.
**Fonte:** `cerebro/areas/marketing/agentes/agente-reels-intel/JOAO-FONTES-E-FERRAMENTAS.md`

## Itens adicionados em 05/05/2026

### 8. Avaliação de ferramentas externas — diferença entre teste, homologação e adoção
**Risco original:** pedido do tipo "olha essa ferramenta/repo/skill" virar instalação ou adoção canônica sem validação, ou um teste em sandbox ser confundido com aprovação operacional.
**Status atual:** **vivo/monitoramento contínuo**. O padrão foi reforçado após avaliações de prompt-master, 21st.dev e Hyperframes/HeyGen: ferramenta externa pode ser útil como referência ou piloto sem virar skill oficial.
**Próximo passo:** em toda avaliação, registrar veredito, riscos, requisitos, status de homologação e menor piloto seguro.
**Fonte:** `cerebro/operacional/INDEX-PEDIDOS-RECORRENTES.md`

### 9. Tokens/segredos em URLs recebidas pelo chat
**Risco original:** links com parâmetros sensíveis, como `mcp_token`, serem copiados para relatório, memória ou comandos e exporem credenciais.
**Status atual:** **vivo/monitoramento contínuo**. Token recebido deve ser tratado como segredo potencial: não reutilizar, não expor e recomendar rotação quando parecer vinculado a ambiente real.
**Próximo passo:** manter higiene de segredo em avaliações técnicas, principalmente MCPs, Replit, Notion, Lovable, HeyGen e ferramentas de automação.
**Fonte:** memória de 2026-05-05 sobre avaliação Hyperframes/HeyGen.

### 10. Subagentes sob demanda do João vs agentes fixos
**Risco original:** transformar repertório de especialidades em 12 agentes fixos antes de haver demanda real suficiente, aumentando complexidade e manutenção.
**Status atual:** **resolvido como regra operacional, com monitoramento de promoção**. João usa biblioteca interna sob demanda; especialidade só vira agente fixo após 5+ demandas reais e aprovação do Tiaro.
**Próximo passo:** observar uso real por especialidade e registrar evidência antes de qualquer promoção.
**Fonte:** `cerebro/areas/marketing/agentes/agente-reels-intel/JOAO-SUBAGENTES-SOB-DEMANDA.md`

### 11. Conselho Growth — parecer aprovado precisa virar especificação/pendência
**Risco original:** conselho produzir diagnóstico ótimo, mas a execução ficar dispersa em HTML/relatório sem porta operacional.
**Status atual:** **vivo/monitoramento contínuo**. Em 05/05, a avaliação da apresentação V2.2 do Erick gerou cortes cirúrgicos para V2.3; isso deve ficar em pendência até implementação/validação.
**Próximo passo:** quando Tiaro aprovar parecer do Conselho Growth, transformar em briefing executável, checklist ou item de backlog.
**Fonte:** `memory/2026-05-05.md` e `cerebro/operacional/INDEX-PEDIDOS-RECORRENTES.md`.

### 12. Aprendizado externo da Clara — cron útil vs regra canônica
**Risco original:** conteúdos de Instagram/YouTube/X virarem regra fixa ou linguagem copiada sem validação.
**Status atual:** **vivo/monitoramento contínuo**. RC-27/RC-28/RC-29 definem aprendizado externo como insumo, com filtro anti-guru e classificação antes de promoção.
**Próximo passo:** revisar relatórios do orquestrador e promover apenas aprendizados validados por Maria/Tiaro/RC-25 quando necessário.
**Fonte:** `memory/2026-05-05.md` e skill `clara-learning-orchestrator`.
