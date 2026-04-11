# Cross-Topic Promotion Rules

## Objetivo
Transformar decisões importantes feitas em qualquer tópico do Telegram em memória canônica reutilizável.

## O que deve ser promovido automaticamente
Promover para o cérebro canônico sempre que aparecer:
- regra operacional nova
- definição de repo, canal, integração ou ferramenta oficial
- contato importante do time
- agenda/ID/endpoints recorrentes
- significado especial definido por Tiaro (ex.: convenções internas)
- correção relevante de algo que já estava errado
- aprendizado de erro que possa se repetir

## Destino por tipo de conteúdo
- GitHub → `cerebro/github.md`
- Quarkclinic → `cerebro/quarkclinic.md` ou `cerebro/quarkclinic-operacao.md`
- WhatsApp/Z-API → `cerebro/whatsapp-zapi.md`
- Time da clínica → `cerebro/time-clinica.md`
- Verdade estrutural → `cerebro/verdades-operacionais.md`
- Aprendizado de processo → `cerebro/LEARNING_PROTOCOL.md` / `cerebro/learning-ledger.md`
- Contexto intertópicos → `cerebro/telegram-topics.md` / `cerebro/cross-topic-memory.md`

## Fluxo obrigatório
1. Surgiu aprendizado relevante em qualquer tópico.
2. Classificar domínio e nível.
3. Atualizar o arquivo canônico correspondente.
4. Atualizar `cerebro/OPERATIONS_INDEX.md` se necessário.
5. Registrar no `cerebro/learning-ledger.md`.
6. Se estrutural, fazer commit no cérebro.

## Regra de ouro
O tópico de origem não é o destino final da memória. O destino final é sempre a estrutura canônica por domínio.
