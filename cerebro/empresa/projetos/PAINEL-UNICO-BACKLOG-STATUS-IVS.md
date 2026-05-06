# Painel Único de Backlog e Status — IVS

## Objetivo
Criar uma porta central de governança para reduzir dispersão entre memória, skill, playbook, projeto, relatórios HTML e backlog recuperável.

## Função do painel
Este painel não substitui os arquivos de domínio.
Ele funciona como **camada mestra de leitura executiva e triagem operacional**.

Ele deve responder rapidamente a 5 perguntas:
1. o que está realmente aberto?
2. o que foi fechado e não deve voltar como pendência?
3. qual é a fonte de verdade de cada frente?
4. qual é o próximo passo objetivo de cada frente?
5. onde existe risco de esquecimento, dispersão ou ambiguidade?

## Fontes de verdade que alimentam o painel

### 1. Pendências executivas
- `cerebro/empresa/projetos/pendencias.md`
- papel: lista curta das pendências centrais e de governança

### 2. Backlog recuperável e recorrências
- `cerebro/operacional/INDEX-PEDIDOS-RECORRENTES.md`
- `cerebro/operacional/ITENS-AMBIGUOS-A-AUDITAR.md`
- papel: recuperar pedidos reais do Tiaro e itens com risco de se perder entre tópicos

### 3. Estado de fluxos canônicos
- fluxos, checklists e playbooks por área
- exemplos:
  - `cerebro/areas/marketing/fluxo-unico-producao-video-ivs.md`
  - `cerebro/areas/atendimento/checklist-atendimento-clara.md`
  - `cerebro/areas/marketing/checklist-curto-producao-video-ivs.md`

### 4. Relatórios HTML relevantes
- diretório: `relatorios/`
- papel: fonte de síntese executiva, auditoria e consolidação histórica
- regra: relatório importante não pode ficar só como artefato passivo; precisa virar pendência, porta única, playbook ou confirmação de fechamento

### 5. Memória recente
- `memory/`
- papel: resgatar decisões novas ainda não totalmente promovidas

## Estrutura recomendada do painel

## Bloco A — Abertos reais
Lista curta, sem ruído.
Cada item deve ter:
- frente
- problema resumido
- próximo passo
- status
- fonte de verdade

## Bloco B — Fechados reais
Itens que já foram resolvidos e não devem reaparecer como pendência aberta.
Serve para evitar reabertura por erro de contexto.

## Bloco C — Monitoramentos contínuos
Itens que não estão “em aberto crítico”, mas exigem vigilância operacional contínua.
Exemplos:
- novos pedidos recorrentes
- aderência entre nomes técnicos de skill e linguagem do Tiaro
- revisão periódica de relatórios HTML
- regressão de bridge/handoff da Clara

## Bloco D — Fontes canônicas por frente
Mapa curto por área:
- Atendimento
- Marketing
- Operações
- Governança
- Financeiro
- Integrações/sistemas

Cada frente deve apontar para sua porta principal.

## Bloco E — Risco de dispersão
Lista curta dos itens com maior risco de:
- sumir entre tópicos
- ficar só em relatório
- existir só em memória diária
- ficar ambíguo entre playbook e projeto

## Regra operacional do painel
1. o painel deve ser curto e executivo
2. o painel não replica conteúdo longo; ele aponta para a fonte correta
3. item fechado sai do bloco de abertos e entra em fechados reais
4. item ambíguo precisa ir para a camada correta: pendência, monitoramento ou fechado
5. sempre que houver consolidação estrutural relevante, promover via graphify antes da atualização canônica

## Cadência de atualização
- atualização rápida: sempre que houver fechamento ou abertura estrutural relevante
- revisão curta: junto da rotina `ROTINA-DIARIA-0100.md`
- revisão ampliada: quando houver acúmulo de relatórios HTML ou múltiplas frentes abertas ao mesmo tempo

## Primeira versão recomendada
A versão 1 do painel deve começar com 4 seções práticas:
1. Abertos reais
2. Fechados reais
3. Monitoramentos contínuos
4. Fontes de verdade por frente

## Ganho esperado
- menos redescoberta
- menos backlog escondido
- menos ambiguidade entre o que está aberto vs já resolvido
- resposta executiva mais rápida para Tiaro
- continuidade melhor entre tópicos do Telegram
