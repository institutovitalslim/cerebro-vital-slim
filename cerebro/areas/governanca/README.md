# Governança do Cérebro e Playbooks

## Objetivo
Centralizar a governança do cérebro do IVS para reduzir dispersão, deixar clara a fonte de verdade e transformar decisões em operação estável.

## O que é governado aqui
- regras canônicas
- playbooks operacionais
- skills e suas responsabilidades
- backlog e projetos de governança
- rotinas de revisão e auditoria

## Fonte de verdade por camada

### 1. Verdades canônicas
Arquivos que definem fatos, regras e critérios centrais do sistema.
- `cerebro/verdades-operacionais.md`
- `cerebro/verdades-operacionais-clara.md`
- `cerebro/execution-principles.md`
- `cerebro/success-criteria.md`
- `cerebro/skill-design-rubric.md`

### 2. Contexto de negócio e operação
Arquivos que explicam empresa, pessoas, decisões e aprendizados.
- `cerebro/empresa/contexto/`
- `cerebro/areas/*/contexto/`
- `cerebro/learning-ledger.md`

### 3. Playbooks e mapas por área
Arquivos operacionais usados para executar.
- `cerebro/areas/*/MAPA.md`
- `cerebro/areas/*/*.md`
- `cerebro/areas/*/rotinas/`

### 4. Skills
Capacidades executáveis e instruções especializadas.
- `skills/`
- `cerebro/areas/*/skills/`
- `cerebro/empresa/skills/_index.md`

### 5. Projetos e backlog
Registro do que está em andamento, pendente ou concluído.
- `cerebro/empresa/projetos/`
- `cerebro/areas/governanca/projetos/`

### 6. Memória e logs
Aprendizados, histórico e consolidações que alimentam o sistema, mas não substituem a regra canônica.
- `MEMORY.md`
- `memory/`
- `cerebro/logs/clara-learnings/`

## Regra de precedência
Quando houver conflito, seguir esta ordem:
1. `verdades-operacionais*.md`
2. `execution-principles.md` + `success-criteria.md`
3. arquivos de contexto e decisões da área
4. playbooks e MAPA da área
5. skills
6. memória, logs e relatórios históricos

## Regra de atualização obrigatória
Toda decisão nova relevante deve ser desdobrada, quando aplicável, em até 4 camadas:
1. regra canônica
2. playbook/skill
3. backlog/projeto
4. checklist ou rotina operacional

## Resultado esperado
- menos ambiguidade
- menos retrabalho
- backlog mais visível
- execução mais consistente
