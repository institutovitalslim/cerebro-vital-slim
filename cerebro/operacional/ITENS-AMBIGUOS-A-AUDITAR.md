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

### 7. Notion — João com ferramenta instalada, mas sem credencial habilitada
**Risco original:** Tiaro solicita que João acesse Notion, mas o token/permissão não está configurado.
**Status atual:** **vivo/dependente de credencial**. A skill `notion_reader.py` existe. O bloqueio é ausência de `NOTION_TOKEN` e eventual permissão/página compartilhada.
**Próximo passo:** (a) Tiaro gerar token de integração Notion; (b) compartilhar página/database com a integração; (c) validar leitura em tópico de Operações ou Marketing.
**Fonte:** `memory/2026-05-02.md`

### 8. Tópico "Pacientes" — topic_id ainda não confirmado
**Risco original:** tópico existe conceitualmente, mas não está mapeado numericamente.
**Status atual:** **vivo/pendente de Tiaro**. Mapeado no painel como A4.
**Fonte:** `cerebro/empresa/projetos/pendencias.md`
