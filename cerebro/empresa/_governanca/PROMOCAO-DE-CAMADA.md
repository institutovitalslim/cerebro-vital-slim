# Promoção de camada — `cerebro/empresa/`

## Objetivo
Definir como um arquivo sai de experimental/teste ou operacional e vira referência mais forte.

## Regras de promoção
### Experimental → Operacional
Promover quando:
- o teste já foi usado com sucesso
- o formato mostrou utilidade recorrente
- existe clareza de uso prático

### Operacional → Canônico
Promover quando:
- o padrão já virou regra estável
- mais de uma frente depende dele
- ele precisa governar decisões futuras

### Qualquer camada → Histórico
Mover para leitura histórica quando:
- deixou de governar a operação atual
- serve mais para rastreio do que para decisão ativa

## Regra prática
Toda promoção relevante deve atualizar:
- `MAPA.md`
- índice estrutural
- skill/playbook/contexto correspondente
