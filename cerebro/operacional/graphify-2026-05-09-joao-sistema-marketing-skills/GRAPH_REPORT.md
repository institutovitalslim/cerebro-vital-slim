# João — pacote de skills para Sistema de Marketing IVS

## Contexto
Tiaro solicitou que Maria pegasse no repositório de skills as capacidades de reverse engineering, qualidade de engenharia de software e demais habilidades necessárias para João criar o sistema de marketing da clínica.

## Ações executadas
- Agente João identificado como `agente-reels-intel`.
- Skills pesquisadas no ClawHub e lidas antes de instalação conforme regra de governança.
- Skills instaladas em `/root/.openclaw/workspace/skills/`:
  - `reverse-engineering`
  - `software-architect`
  - `software-engineer`
  - `quality-driven-dev`
  - `quality-gates`
  - `openclaw-marketing-os`
  - `marketing-analytics`
  - `marketing-demand-acquisition`
  - `product-manager-toolkit`
  - `saas-decomposer`
- Skills locais já existentes e também vinculadas ao João:
  - `repo-reverse-ivs`
  - `validacao-qa`
- `/root/.openclaw/openclaw.json` atualizado para incluir essas skills no João.
- João também recebeu permissão de subagentes para `conselho-growth-vital-slim` e `llm-council`, com `requireAgentId=true`.
- Prompt do João recebeu regra operacional específica para atuar como arquiteto do Sistema de Marketing IVS: descoberta, arquitetura, execução, QA, métricas, rollout e consulta aos conselhos quando necessário.
- Sessão do tópico Telegram Marketing/Reels `5782` foi resetada apenas no mapeamento, preservando o arquivo de histórico anterior, para carregar a nova configuração na próxima mensagem.
- Gateway OpenClaw recarregado via SIGUSR1 e healthcheck retornou `ok/live`.

## Governança
- Não copiar código proprietário para produção sem validação de licença, decisão explícita e adaptação IVS-first.
- Separar código/referência analisada de código incorporado em produção.
- João deve usar as novas skills para construir sistema, não apenas peças isoladas.
- Decisões críticas de crescimento, estratégia ou compliance devem acionar Conselho Growth ou LLM Council e voltar como síntese operacional, sem expor bastidores.

## Resultado esperado
João está equipado para especificar e construir o Sistema de Marketing da clínica com:
- reverse engineering de referências e sistemas;
- arquitetura e engenharia de software;
- qualidade, testes e gates;
- marketing operating system com handoffs e receipts;
- funil, aquisição, analytics e priorização de produto;
- decomposição de SaaS/rotinas substituíveis por agentes.
\n## Nota de execução\nGraphify CLI não concluiu automaticamente; relatório operacional RC-25 preservado a partir do raw.
