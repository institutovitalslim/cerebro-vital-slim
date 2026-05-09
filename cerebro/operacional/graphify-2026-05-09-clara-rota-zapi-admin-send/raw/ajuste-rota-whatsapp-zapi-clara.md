# Ajuste operacional — Clara rota WhatsApp/Z-API admin/send

Data: 2026-05-09
Responsável: Maria Gerente
Solicitante: Tiaro

## Problema
Clara tentou executar follow-up solicitado no Telegram usando o canal disponível da sessão Telegram. O envio falhou porque a ação real deveria sair pelo WhatsApp/Z-API, não pelo Telegram.

## Correção aplicada
- Bridge local `zapi_clara_bridge.py` recebeu endpoint interno `POST /admin/send`.
- Endpoint usa `send_zapi_text(phone, message)` para disparo real via Z-API.
- Endpoint aceita `dry_run: true` para teste sem disparo.
- Endpoint respeita exclusões de paciente/fornecedor/teste e retorna `blocked: true` com motivo, salvo uso explícito de `force`.
- Prompt do agente `clara-whatsapp` em `/root/.openclaw/openclaw.json` recebeu instrução prioritária: envio real WhatsApp deve usar `curl http://127.0.0.1:8787/admin/send`, nunca `message.send` Telegram.
- Gateway OpenClaw recarregado via `SIGUSR1`.
- Bridge Z-API reiniciado e validado em `/healthz`.

## Teste técnico
`POST /admin/send` com `dry_run: true` para telefone fictício retornou `ok: true`, confirmando rota operacional sem disparar mensagem real.

## Regra operacional canônica
Quando Tiaro ou Maria pedir follow-up real no WhatsApp, Clara deve:
1. Normalizar telefone.
2. Enviar pela rota local Z-API `/admin/send`.
3. Conferir JSON de retorno.
4. Reportar enviados e bloqueados com motivo.
5. Não alegar ausência de canal WhatsApp sem antes testar a rota local.
