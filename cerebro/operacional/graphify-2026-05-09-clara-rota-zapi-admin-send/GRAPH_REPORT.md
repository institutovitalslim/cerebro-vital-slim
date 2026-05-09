# GRAPH_REPORT — Clara rota correta WhatsApp/Z-API

## Resultado
Registro RC-25 criado para correção da rota de follow-up real da Clara.

## Nós principais
- Clara WhatsApp
- Bridge Z-API
- Endpoint /admin/send
- Telegram AI Vital Slim
- Follow-up de leads
- Maria Gerente

## Relações
- Clara WhatsApp -> deve usar -> Endpoint /admin/send para envio real WhatsApp
- Endpoint /admin/send -> chama -> Z-API send-text
- Telegram AI Vital Slim -> é canal interno, não rota de envio WhatsApp
- Maria Gerente -> corrigiu -> rota operacional da Clara

## Validação
- Bridge `/healthz`: OK
- `/admin/status`: Clara não pausada
- `/admin/send` dry_run: OK

## Decisão operacional
Follow-ups reais no WhatsApp solicitados em Telegram devem sair pela rota local `http://127.0.0.1:8787/admin/send`; a ferramenta `message`/Telegram não deve ser usada para disparo a leads.
