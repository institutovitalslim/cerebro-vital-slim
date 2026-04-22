# Memory Compaction Policy

Política de promoção, compactação e limpeza de memória do cérebro.

## Objetivo
Garantir continuidade sem transformar memória em acúmulo caótico.

## Princípio central
Nem tudo que aconteceu merece memória longa.
Memória longa deve guardar apenas o que melhora decisões futuras de forma recorrente.

## Níveis de retenção

### Nível A — Diário
Registrar em `memory/YYYY-MM-DD.md` quando for:
- fato do dia
- tentativa, erro ou correção pontual
- contexto útil de curto prazo
- resultado intermediário
- aprendizado ainda não consolidado

### Nível B — Ledger
Registrar em `cerebro/learning-ledger.md` quando houver:
- incorporação de aprendizado relevante
- criação ou mudança de arquivo canônico
- ajuste estrutural no cérebro
- formalização de nova convenção recorrente

### Nível C — Memória longa
Promover para `MEMORY.md` quando houver:
- skill crítica que precisa ser reencontrada facilmente
- decisão estrutural durável
- regra estratégica recorrente
- índice de fontes importantes
- marco histórico que ajuda orientação futura

### Nível D — Canônico
Promover para arquivo canônico do domínio quando houver:
- regra operacional recorrente
- fato estável do negócio
- IDs, contas, destinos, integrações, contatos, endpoints
- convenção que precisa governar execuções futuras

## Perguntas de decisão
Antes de promover algo para memória longa, perguntar:
1. isso muda decisões futuras de forma recorrente?
2. isso será difícil de reencontrar sem índice?
3. isso é estrutural ou apenas circunstancial?
4. isso pertence a domínio canônico em vez de memória?
5. isso está maduro ou ainda é só observação de uma sessão?

Se a resposta for fraca, manter no diário.

## Regras de compactação do `MEMORY.md`

### Manter
- índices curtos
- ponteiros para arquivos-fonte
- poucas linhas por skill/operação
- marcos estruturais importantes

### Remover ou resumir
- checklists detalhados já documentados em outro lugar
- regras operacionais já consolidadas em arquivo canônico
- exemplos longos
- lições que já viraram arquivo próprio
- duplicações entre memória e canon

## Regra de promoção
Quando um aprendizado nasce no diário e se prova recorrente:
1. identificar o domínio
2. atualizar o arquivo canônico correto, se aplicável
3. registrar a incorporação no ledger
4. atualizar `MEMORY.md` apenas com um índice curto, se fizer sentido

## Regra de não-promoção
Não promover para `MEMORY.md`:
- logs completos de sessão
- tentativas descartadas
- detalhes de debugging efêmeros
- instruções locais já cobertas por skill/script
- fatos que dependem de contexto muito específico e não se repetem

## Revisão periódica
Em revisões de memória:
1. ler memórias diárias recentes
2. identificar o que virou padrão
3. promover apenas o que for durável
4. remover do `MEMORY.md` o que já ficou redundante
5. manter `MEMORY.md` como índice, não arquivo de despejo

## Sinais de memória saudável
- `MEMORY.md` continua curto e navegável
- regras críticas existem em arquivos canônicos, não escondidas no diário
- mudanças estruturais aparecem no ledger
- um agente novo consegue encontrar a fonte certa sem adivinhar

## Sinais de memória doente
- `MEMORY.md` vira manual gigante
- o mesmo aprendizado aparece em 3 ou 4 arquivos sem diferença de papel
- memória diária começa a carregar regras permanentes sem promoção
- decisões importantes ficam só em conversa recente
