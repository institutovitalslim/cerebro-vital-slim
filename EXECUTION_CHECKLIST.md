# EXECUTION_CHECKLIST.md

Checklist geral para tarefas longas, críticas ou multi-etapas.

## Regra-mãe
Se o usuário disser "pode seguir", "siga", "corrija", "instale", "faça", ou equivalente, a tarefa entra em modo **EXECUÇÃO ATÉ CONCLUSÃO**.

## Antes de começar
1. Definir objetivo exato
2. Definir critério de conclusão
3. Identificar se há risco, dependência externa ou necessidade de aprovação
4. Escolher a trilha operacional mais direta

## Durante a execução
- Não interromper com update de intenção vazio
- Não voltar só para dizer que vai verificar/pesquisar/diagnosticar
- Continuar até concluir, ou até encontrar um bloqueio real
- Se a tarefa for longa, só voltar com valor real, não com filler

## Estados válidos de retorno
- CONCLUÍDO
- BLOQUEADO (com causa concreta)
- PRECISO DE DECISÃO (com pergunta objetiva)
- PARADO POR SEGURANÇA

## O que conta como bloqueio real
- credencial ausente
- permissão negada
- dependência externa fora do host
- risco/destrutividade exigindo confirmação
- erro técnico que impede seguir sem mudar estratégia

## O que NÃO conta como retorno válido
- "vou verificar"
- "vou pesquisar"
- "vou diagnosticar"
- "já vou ver"
- "estou olhando"

## Fechamento obrigatório
Ao concluir, informar:
1. o que foi feito
2. o que mudou
3. o que ficou pendente (se houver)
4. próximo passo recomendado (se útil)

Em tarefas executivas, operacionais ou verificáveis, usar também o padrão:
- Ação executada
- Evidência
- IDs / Arquivos
- Pendências

Fonte canônica: `cerebro/evidence-output-standard.md`
