# Pendências

## Pendências centrais
- manter vivo e evoluir o painel único de backlog e status

## Consolidado em 03/05/2026 (rotina de manutenção)

### Pendências encerradas ou arquivadas desde 30/04/2026:
- **Handoff/manual takeover da Clara** → arquivado. Entrou para camada operacional contínua de monitoramento no checklist.
- **Tópico Reels 768 vs 5782** → arquivado. João validado no tópico Marketing 5782.
- **`topic_id` do tópico "Pacientes"** → encerrado. Confirmado canonicamente como `271` em 03/05/2026.

### Pendências de governança ativas:
- alimentar continuamente `cerebro/operacional/INDEX-PEDIDOS-RECORRENTES.md` com novos pedidos reais do Tiaro
- auditar demandas antigas que podem ter ficado abertas por erro de tópico, interrupção ou troca de contexto
- transformar backlog esquecido em portas únicas ou pendências explícitas
- revisar periodicamente relatórios HTML e promover itens recorrentes para camada operacional
- garantir que a rotina `cerebro/manutencao/ROTINA-DIARIA-0100.md` siga transversal entre tópicos e não falhe por presença de agente especializado em tópico específico

## Consolidado em 05/05/2026 (rotina de manutenção)

### Pendências encerradas ou promovidas desde 04/05/2026:
- **Modelo de subagentes sob demanda do João** → promovido para regra operacional do agente, com arquivo canônico próprio e critério de futura promoção para agente fixo.
- **Prompt-master** → incorporado seletivamente como referência de engenharia de prompt para ferramentas web, sem adoção crua do repositório como skill oficial.

### Pendências operacionais ativas:
- **Entrega de HTML no Telegram**: corrigir rota/conector para garantir envio do `.html` como anexo visível e abrível no tópico correto; ZIP segue proibido como workaround e código HTML não deve ser colado como entrega principal.
- **21st.dev / MCP magic21st**: permanece não homologado até existir API key válida e teste real.
- **Hyperframes/HeyGen**: aprovado apenas para piloto em sandbox; próximo passo é gerar 1 Reel vertical 1080x1920 de 15s, sem dados de paciente, com identidade IVS, e avaliar qualidade, tempo de render, ajuste pelo João, peso e reaproveitamento como template.

### Pendências de monitoramento adicionadas:
- diferenciar explicitamente **referência**, **piloto em sandbox**, **homologação** e **skill oficial** em avaliações de ferramentas externas;
- tratar URLs com token/parâmetro sensível como segredo potencial e recomendar rotação quando aplicável;
- monitorar uso real das especialidades do João antes de qualquer promoção para agente fixo.

## Consolidado em 06/05/2026 (rotina de manutenção)

### Correções de memória/recuperabilidade executadas:
- `memory/2026-05-05.md` estava com blocos duplicados da consolidação do dia; a memória foi deduplicada, preservando os registros únicos. Backup local criado em `memory/2026-05-05.md.bak-dedupe-20260506-0100`.
- Novos pedidos recorrentes promovidos: passar peça pelo Conselho Growth; gerar especificação HTML para Claude Code; enxugar apresentação prolixa.

### Pendências operacionais ativas adicionadas:
- **Apresentação V2.3 do paciente Erick**: aplicar cortes recomendados pelo Conselho Growth na V2.2, reduzindo 25% a 35% do texto, removendo redundâncias e preservando exame/questionário, SPIN enxuto, objeções e CTA ético.
- **Clara — aprendizado externo RC-27/RC-28/RC-29**: monitorar se os crons silenciosos estão gerando relatórios úteis sem promover automaticamente aprendizados externos para regra fixa.

### Pendências de monitoramento reforçadas:
- toda URL com token/parâmetro sensível recebida em chat deve ser tratada como segredo potencial, sem reutilização, exposição em relatório ou transcrição operacional;
- decisões do Conselho Growth devem virar briefing executável ou porta canônica quando forem aprovadas, para não ficarem apenas em HTML/relatório.
