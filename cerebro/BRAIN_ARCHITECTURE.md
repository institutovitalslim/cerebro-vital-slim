# Brain Architecture

Mapa estrutural do cérebro: o que cada camada guarda, em que ordem consultar, e onde registrar mudanças.

## Objetivo
Evitar duas falhas recorrentes:
- procurar a verdade no arquivo errado;
- duplicar regra em múltiplos lugares até perder coerência.

## Camadas do cérebro

### 1. Camada de comportamento geral
Arquivos que definem como agir de forma ampla.

- `AGENTS.md` → boot do workspace, postura geral, memória, heartbeats, comportamento social
- `SOUL.md` → identidade, tom e princípios de personalidade
- `OPERATING_RULES.md` → regras operacionais universais
- `PREFLIGHT.md` → pré-checagem para tarefas críticas
- `CONTEXT_CANON.md` → mapa de onde buscar a verdade por domínio
- `cerebro/execution-principles.md` → princípios universais de execução
- `cerebro/success-criteria.md` → definição objetiva de concluído por domínio

### 2. Camada canônica por domínio
Arquivos que guardam fatos operacionais reais e estáveis por área.

Exemplos:
- `cerebro/verdades-operacionais.md`
- `cerebro/github.md`
- `cerebro/quarkclinic.md`
- `cerebro/omie.md`
- `cerebro/whatsapp-zapi.md`
- `cerebro/time-clinica.md`

Regra: aqui entram fatos, IDs, contas, integrações, decisões operacionais e convenções reais do negócio.

### 3. Camada de skill / fluxo
Arquivos e scripts que explicam como executar um fluxo específico.

Exemplos:
- `SKILL.md` da skill correspondente
- scripts oficiais da skill
- checklists operacionais específicos
- artefatos executáveis do fluxo

Regra: a skill deve explicar gatilho, escopo, sequência, limites e verificação. Ela não deve virar depósito de regra universal já coberta pela camada geral.

### 4. Camada de memória
Arquivos que preservam continuidade e contexto.

- `MEMORY.md` → índice de memória longa, enxuto e curado
- `memory/YYYY-MM-DD.md` → memória diária, factual e incremental
- `cerebro/learning-ledger.md` → registro de mudanças e aprendizados incorporados

Regra: memória não substitui fonte canônica de domínio. Memória aponta, resume e preserva contexto.

## Ordem de leitura prática

### Tarefa simples e não operacional
1. `AGENTS.md`
2. `SOUL.md`
3. `USER.md`
4. memória recente do dia

### Tarefa operacional recorrente
1. `OPERATING_RULES.md`
2. `CONTEXT_CANON.md`
3. `PREFLIGHT.md`
4. arquivo canônico do domínio
5. skill/checklist específico
6. `cerebro/success-criteria.md` se houver chance de declarar conclusão

### Tarefa estrutural no cérebro
1. `OPERATING_RULES.md`
2. `cerebro/execution-principles.md`
3. `cerebro/skill-design-rubric.md`
4. `cerebro/LEARNING_PROTOCOL.md`
5. `cerebro/learning-ledger.md`

## Ordem de precedência
Quando houver conflito, usar nesta ordem:
1. instrução direta do usuário
2. regras de segurança e sistema
3. arquivo operacional/checklist específico do fluxo
4. arquivo canônico do domínio
5. `OPERATING_RULES.md`
6. `CONTEXT_CANON.md`
7. `cerebro/execution-principles.md`
8. `cerebro/success-criteria.md`
9. `AGENTS.md`
10. `MEMORY.md`
11. `memory/YYYY-MM-DD.md`
12. contexto recente de conversa

## O que vai para cada lugar

### Vai para `MEMORY.md`
- índice de skills críticas
- ponteiros para fontes canônicas
- decisões estruturais duráveis
- marcos importantes da evolução do cérebro

### Não vai para `MEMORY.md`
- passo a passo detalhado de fluxo operacional
- listas extensas de regras já canônicas em outro arquivo
- logs de sessão completos
- detalhes efêmeros que pertencem só ao diário

### Vai para memória diária
- fatos do dia
- erros e correções contextuais
- decisões ainda não curadas
- resultados intermediários

### Vai para arquivo canônico do domínio
- fatos estáveis do negócio
- IDs, contas, integrações, endpoints, destinos
- convenções recorrentes
- regras específicas daquele domínio

### Vai para skill
- gatilho de uso
- sequência de execução
- limites da skill
- verificação final do fluxo
- referências executáveis e scripts oficiais

## Regra anti-duplicação
Antes de escrever uma nova regra, perguntar:
1. isso já existe em camada universal?
2. isso é de domínio ou só desta skill?
3. isso precisa virar memória longa ou só ledger?
4. isso é fato estável ou detalhe temporário?

Se a resposta não estiver clara, não duplicar ainda. Primeiro escolher a camada certa.

## Critério de boa arquitetura
A arquitetura está saudável quando:
- cada regra tem um lugar óbvio
- o índice aponta para a fonte certa
- `MEMORY.md` continua curto
- skills ficam menores e mais focadas
- o agente consegue explicar por que consultou cada arquivo
