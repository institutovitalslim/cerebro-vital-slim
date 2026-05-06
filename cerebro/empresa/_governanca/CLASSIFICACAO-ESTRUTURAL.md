# Classificação Estrutural — `cerebro/empresa/`

## Objetivo
Deixar explícito o que é material canônico, operacional, experimental/teste e histórico/log dentro de `cerebro/empresa/`.

## Camadas

### 1. Canônico
Arquivos que definem contexto, regras, frameworks, mapas e padrões que devem ser usados como referência principal.

Entram aqui, por padrão:
- `contexto/`
- `skills/GOVERNANCA-SKILLS.md`
- `skills/DEPENDENCIAS-SKILLS.md`
- `skills/TEMPLATE-SKILL-IVS.md`
- `skills/_index.md`
- `vendas/lead-qualificacao-framework.md`
- `MAPA.md`

### 2. Operacional
Arquivos usados para execução recorrente, produção, entrega ou operação ativa.

Entram aqui, por padrão:
- skills ativas
- playbooks em uso
- análises de conteúdo reaproveitadas operacionalmente
- projetos e pendências em andamento

### 3. Experimental / teste
Arquivos de teste, protótipo, validação, exploração ou material ainda não promovido a operação/canônico.

Entram aqui, por padrão:
- testes de pré-consulta
- experimentos de prompts
- protótipos e rasgos de processo ainda não consolidados

### 4. Histórico / log
Arquivos de histórico, evidência, rastreio, log de execução e materiais que não governam mais a operação atual.

Entram aqui, por padrão:
- `conhecimento/logs/`
- logs técnicos de skills
- snapshots e relatórios preservados apenas para consulta histórica

## Regra prática
Se houver dúvida sobre onde um arquivo deve ser consultado primeiro:
1. canônico
2. operacional
3. experimental/teste
4. histórico/log
