# Pausa de Emergencia - Clara

Mecanismo para Tiaro pausar Clara rapidamente quando ela responde errado, com TTL automatico (anti-esquecimento).

## Contexto historico

Em 8 de abril de 2026, Tiaro setou `paused: true` manualmente porque Clara estava respondendo errado a pacientes. A pausa nunca foi removida, ficando ativa por **20 dias** (descoberto em 28/04). Solucao: implementar TTL automatico.

## Endpoints HTTP do bridge

Bridge: `zapi-clara-bridge.service` na VPS `187.77.58.193`
Porta: `127.0.0.1:8787`
Auth: header `X-Bridge-Secret` (se configurado)

### GET /admin/status
Retorna estado atual da pausa:

```json
{
  "ok": true,
  "paused": true,
  "paused_at": 1777406133,
  "paused_until": 1777407933,
  "remaining_seconds": 1800,
  "paused_reason": "respondendo errado",
  "paused_by": "Tiaro"
}
```

### POST /admin/pause

#### action: pause (com TTL)
```json
{
  "action": "pause",
  "duration_minutes": 120,    // default 2h
  "reason": "Clara respondendo errado",
  "by": "Tiaro"
}
```
Retorna:
```json
{
  "ok": true,
  "action": "paused",
  "paused_until": 1777500000,
  "duration_minutes": 120,
  "reason": "...",
  "by": "Tiaro"
}
```

#### action: pause_indefinite
```json
{
  "action": "pause_indefinite",
  "reason": "manutencao",
  "by": "Tiaro"
}
```

#### action: unpause
```json
{
  "action": "unpause"
}
```

#### action: status (mesma coisa que GET /admin/status)
```json
{
  "action": "status"
}
```

## Comportamento

| Tipo | TTL | Auto-libera | Lembrete |
|------|-----|-------------|----------|
| `pause` | duration_minutes (default 2h) | SIM, na proxima request apos paused_until | nao precisa |
| `pause_indefinite` | nao tem | NAO - aguarda comando manual | a cada 3h, Clara lembra Tiaro via Telegram |

## Auto-release

Implementado em `should_pause_clara()` no bridge:
1. Se `paused: true` e `paused_until` ja passou -> auto-despausa
2. Salva estado novo (paused=false)
3. Loga evento "global_pause auto_released (TTL expired)"
4. Continua processando mensagem normalmente

## Comandos via Telegram (Tiaro fala com Clara)

Estes sao os comandos que Tiaro vai usar na pratica. A Clara precisa interpretar e chamar o endpoint:

| Comando Tiaro | Acao Clara |
|---------------|------------|
| "Clara, pausa por 2h - motivo X" | POST /admin/pause `{action: "pause", duration_minutes: 120, reason: "X", by: "Tiaro"}` |
| "Clara, pausa por 30 minutos" | POST `{action: "pause", duration_minutes: 30, by: "Tiaro"}` |
| "Clara, pausa indefinido - motivo X" | POST `{action: "pause_indefinite", reason: "X", by: "Tiaro"}` |
| "Clara, pode voltar" | POST `{action: "unpause"}` |
| "Clara, status" | GET /admin/status |

## Lembrete a cada 3h (pausa indefinida)

Cron ou scheduler dedicado dispara a cada 3h:
1. Se `paused: true` e `paused_until` is null (indefinida)
2. Calcula tempo desde `paused_at`
3. Envia Telegram para Tiaro: "Continuo pausada desde [hora]. Manter ou despausar?"

(A implementar como skill auxiliar, nao parte do bridge)

## Quem pode pausar/despausar

- Tiaro (5571986968887, user_id Telegram 971050173)
- [TBD: Liane tambem? Confirmar user_id Telegram]

## Estado atual

```bash
# Consultar status
curl -s http://127.0.0.1:8787/admin/status

# Pausar 1h
curl -X POST -H "Content-Type: application/json" \
  -d '{"action":"pause","duration_minutes":60,"reason":"teste","by":"Tiaro"}' \
  http://127.0.0.1:8787/admin/pause

# Despausar
curl -X POST -H "Content-Type: application/json" \
  -d '{"action":"unpause"}' \
  http://127.0.0.1:8787/admin/pause
```

## Implementacao

Codigo: `/root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge.py`

Funcoes adicionadas (28/04/2026):
- `default_control_state()` - novos campos: paused_at, paused_until, paused_reason, paused_by
- `save_control_state()` - helper para persistir estado
- `should_pause_clara()` - checagem de TTL e auto-release
- `handle_admin_pause()` - dispatcher das acoes
- Handler.do_GET / do_POST - novos paths /admin/status e /admin/pause

Backup pre-mudanca: `zapi_clara_bridge.py.bak-pre-pause-ttl-20260428-XXXXXX`
