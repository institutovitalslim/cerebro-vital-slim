# WhatsApp / Z-API

## Regra canônica
- A comunicação operacional por WhatsApp deve usar a **bridge da Z-API** já criada.
- Não assumir que um job ou resposta iniciada em contexto Telegram conseguirá enviar WhatsApp automaticamente.
- Sempre validar o caminho de entrega real antes de prometer que uma automação WhatsApp está funcionando.

## Uso
- Para automações diárias e mensagens operacionais da clínica, priorizar a bridge da Z-API.
- Se houver bloqueio de cross-channel, tratar isso como limitação real do contexto atual e migrar o fluxo para o caminho correto da bridge.

## Regra de honestidade
- Nunca afirmar que o WhatsApp foi enviado se não houver confirmação real do disparo.
