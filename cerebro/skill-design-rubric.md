# Rubrica de Design de Skills

Use esta rubrica antes de criar, expandir ou refatorar uma skill.

## 1. Precisa mesmo ser uma skill?
Criar skill nova só quando houver pelo menos um destes casos:
- fluxo recorrente com múltiplas etapas
- regras canônicas próprias
- risco alto de erro sem procedimento fixo
- utilidade repetida ao longo do tempo

Se for ajuste pontual, prefira:
- atualizar skill existente
- criar script dentro do domínio certo
- registrar regra no arquivo canônico

## 2. Escopo mínimo
A skill deve resolver um problema real e delimitado.
- evitar escopo aberto demais
- evitar "skill framework" sem uso concreto
- evitar abstrações para um único caso

## 3. Entrada, saída e verificação
Toda skill deve deixar claro:
- entrada esperada
- passos obrigatórios
- saída esperada
- como verificar sucesso
- qual evidência mínima deve aparecer no fechamento, conforme `cerebro/evidence-output-standard.md`

## 4. Fonte de verdade
A skill precisa apontar para:
- arquivo canônico do domínio
- scripts oficiais
- credenciais/localização quando relevante
- restrições operacionais críticas

## 5. Anti-duplicação
Antes de criar ou expandir:
- já existe skill parecida?
- já existe script canônico?
- a regra pertence ao cérebro, e não à skill?
- estou duplicando instrução universal em vez de referenciar?

## 6. Anti-overengineering
Evitar:
- opções demais sem necessidade real
- múltiplos caminhos equivalentes sem motivo
- linguagem vaga sobre quando usar
- longas instruções para casos simples

## 7. Regra de qualidade
Uma boa skill deve ser:
- específica
- acionável
- verificável
- curta o bastante para navegar
- forte o bastante para evitar erro recorrente
