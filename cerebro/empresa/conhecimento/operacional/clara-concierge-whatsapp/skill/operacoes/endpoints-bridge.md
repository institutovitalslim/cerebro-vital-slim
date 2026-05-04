# Endpoints HTTP do Bridge

Documentacao tecnica dos endpoints expostos pelo `zapi-clara-bridge.service`.

**Servidor**: 127.0.0.1:8787 na VPS 187.77.58.193
**Auth**: header `X-Bridge-Secret: <BRIDGE_SHARED_SECRET>` (se definido)

## Endpoints publicos

### GET /healthz
Health check. Sem autenticacao.

```bash
curl http://127.0.0.1:8787/healthz
# {"ok": true, "service": "zapi-clara-bridge"}
```

### GET /health
Alias de /healthz.

## Endpoints administrativos

### GET /admin/status
Consulta estado atual da pausa.

```bash
curl -H "X-Bridge-Secret: $SECRET" http://127.0.0.1:8787/admin/status
```

Resposta:
```json
{
  "ok": true,
  "paused": true,
  "paused_at": 1777406133,
  "paused_until": 1777407933,
  "remaining_seconds": 1234,
  "paused_reason": "Clara respondendo errado",
  "paused_by": "Tiaro"
}
```

Quando nao pausada:
```json
{
  "ok": true,
  "paused": false,
  "paused_at": null,
  "paused_until": null,
  "remaining_seconds": null,
  "paused_reason": null,
  "paused_by": null
}
```

### POST /admin/pause
Acoes de controle de pausa.

#### Action: pause (com TTL automatico)
```bash
curl -X POST -H "X-Bridge-Secret: $SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "pause",
    "duration_minutes": 120,
    "reason": "Clara respondendo errado",
    "by": "Tiaro"
  }' \
  http://127.0.0.1:8787/admin/pause
```

Parametros:
- `action`: "pause" (obrigatorio)
- `duration_minutes`: minutos (default 120 = 2h)
- `reason`: string (opcional)
- `by`: nome de quem pausou (opcional)

Resposta:
```json
{
  "ok": true,
  "action": "paused",
  "paused_until": 1777407933,
  "duration_minutes": 120,
  "reason": "Clara respondendo errado",
  "by": "Tiaro"
}
```

Comportamento:
- Pausa Clara IMEDIATAMENTE
- Auto-libera quando `paused_until` expira (na proxima request)
- Logs: `admin pause duration=Xmin by='Tiaro' reason='...'`

#### Action: pause_indefinite
```bash
curl -X POST -H "X-Bridge-Secret: $SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "pause_indefinite",
    "reason": "manutencao",
    "by": "Tiaro"
  }' \
  http://127.0.0.1:8787/admin/pause
```

Comportamento:
- Pausa Clara ate ser despausada manualmente
- NAO tem TTL
- Recomendacao: cron a cada 3h lembrar Tiaro via Telegram (a implementar)

#### Action: unpause
```bash
curl -X POST -H "X-Bridge-Secret: $SECRET" \
  -H "Content-Type: application/json" \
  -d '{"action": "unpause"}' \
  http://127.0.0.1:8787/admin/pause
```

Comportamento:
- Despausa Clara imediatamente
- Reseta todos os campos de pausa
- Logs: `admin unpause (was_paused=True/False)`

#### Action: status
Mesma coisa que GET /admin/status, mas via POST.
```bash
curl -X POST -H "X-Bridge-Secret: $SECRET" \
  -H "Content-Type: application/json" \
  -d '{"action": "status"}' \
  http://127.0.0.1:8787/admin/pause
```

## Webhook (uso interno do Z-API)

### POST /webhook/<TOKEN>
Recebe eventos do Z-API. Token configurado em `WEBHOOK_PATH_TOKEN`.

NAO chamar manualmente. So o Z-API deve postar aqui.

Comportamento:
- Fanout para Apps Script (analytics)
- Filtra: from_me / group_message / nao-texto / duplicado
- Se OK: chama `should_pause_clara()` -> `is_existing_patient()` -> `should_respond_to_lead()` -> `call_clara()` -> `send_zapi_text()`

## Codigos de resposta

| Codigo | Significado |
|--------|-------------|
| 200 | OK |
| 400 | invalid json / invalid action |
| 403 | forbidden (X-Bridge-Secret invalido) |
| 404 | not found (path invalido) |

## Errors recentes vistos em logs

### BrokenPipeError
Cliente fecha conexao antes de Clara responder. Inofensivo - Clara processou OK, so nao conseguiu fechar HTTP. Nao afeta o paciente.

## Observacoes operacionais

- TTL e checado a cada request entrante. Se ninguem mandar mensagem, paused fica ativo ate proxima request (e nao precisa - ninguem precisa de Clara nesse tempo).
- Pausa indefinida deve ter cron de lembrete a cada 3h (a implementar).
- Logs em journalctl --user -u zapi-clara-bridge.

## Como Clara aciona via comando Telegram

(Integracao via OpenClaw gateway - a implementar)

| Comando do Tiaro | Clara executa |
|------------------|---------------|
| "Clara, pausa por 2h - motivo X" | POST /admin/pause `{"action":"pause","duration_minutes":120,"reason":"X","by":"Tiaro"}` |
| "Clara, pausa indefinido - motivo X" | POST /admin/pause `{"action":"pause_indefinite","reason":"X","by":"Tiaro"}` |
| "Clara, pode voltar" | POST /admin/pause `{"action":"unpause"}` |
| "Clara, status" | GET /admin/status |

## Source of truth

operacoes/pausa-emergencia.md + codigo zapi_clara_bridge.py.
