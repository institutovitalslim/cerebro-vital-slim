# Teste Canônico — WhatsApp / Z-API

## Cenário
Usuário pede envio, follow-up ou ação operacional via WhatsApp.

## Entrada típica
- destinatário ou conversa-alvo
- contexto real da conversa
- intenção da mensagem

## Ação esperada
- validar o contexto correto da bridge
- consultar exclusões e estado real da conversa quando aplicável
- não responder genericamente
- enviar só pelo caminho operacional correto

## Evidência mínima de sucesso
- retorno real de envio (`messageId`, log ou status); ou
- bloqueio explícito por ambiguidade/contexto; ou
- rascunho claramente marcado como não enviado

## Parar e pedir confirmação quando
- houver ambiguidade entre lead e paciente
- faltar contexto suficiente da conversa
- o canal real de envio não estiver disponível
- existir risco de resposta comercial errada
