---
type: policy
status: active
owner: maria
source_of_truth: true
created: 2026-06-13
updated: 2026-06-13
rc25: graphify-2026-06-13-gbrain-aplicacao-operacao-cerebro-agentes
---

# GBrain aplicado à operação IVS

Por decisão de Tiaro, GBrain passa a ser aplicado à operação do IVS, incluindo memória dos agentes e estrutura do cérebro.

## Forma de aplicação
- Estrutura canônica adicionada em `cerebro/gbrain/`.
- Cérebro existente preservado.
- GBrain sidecar continua responsável por índice, grafo e embeddings.
- Graphify/RC-25 continua obrigatório para mudança persistente.

## Resultado esperado
Agentes IVS deixam de depender apenas de memória curta e passam a consultar a camada GBrain antes de responder sobre fatos operacionais, regras, processos e histórico.
