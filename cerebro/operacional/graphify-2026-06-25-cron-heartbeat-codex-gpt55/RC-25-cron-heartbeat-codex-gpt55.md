# RC-25 — Crons e heartbeats IVS devem rodar em Codex GPT-5.5

- **Data:** 2026-06-25
- **Decisor:** Tiaro
- **Executora:** Maria
- **Escopo:** Hermes cron jobs, heartbeats, keep-alives, monitores recorrentes e rotinas agendadas dos agentes IVS

## Decisão

Todo cron ou heartbeat que precise de LLM deve rodar em:

```yaml
provider: openai-codex
model: gpt-5.5
```

Crons/heartbeats simples, determinísticos ou de watchdog devem preferencialmente rodar como:

```yaml
no_agent: true
script: <script>
```

Nesse caso, não há chamada LLM e portanto não há custo OpenRouter/Opus.

## Regra prática

1. **Permitido e preferível:** `no_agent=true` para checks determinísticos, syncs, healthchecks e watchdogs.
2. **Permitido quando precisa raciocínio:** LLM cron/heartbeat fixado em `openai-codex/gpt-5.5`.
3. **Proibido:** cron/heartbeat herdando modelo do perfil quando o perfil usa Opus/OpenRouter.
4. **Proibido:** keep-alive, heartbeat, polling ou rotina de baixo valor operacional usando Opus 4.8.
5. **Exceção:** nenhuma exceção automática. Se algum cron médico-científico precisar de Opus, deve virar tarefa manual/sob demanda da Ana, não heartbeat/cron recorrente.

## Medidas aplicadas

- Inventário dos crons Hermes dos perfis `default`, `ana`, `clara`, `joao`, `pedro`, `jarvis`.
- Crons ativos atuais no perfil `default` são `no_agent`:
  - `99c6856042d6` — IVS sync QuarkClinic pacientes para histórico Clara;
  - `98911e9a5c36` — Ana OpenRouter cost watchdog;
  - `1dd756d835fb` — IVS cron heartbeat model guard.
- Cron ENDOGIN no perfil Ana permanece pausado:
  - `95d31ff0692c` — ENDOGIN keep-alive sessão.
- Esse cron ENDOGIN foi fixado defensivamente em:
  - `provider=openai-codex`
  - `model=gpt-5.5`
  Mesmo pausado, se alguém reativar, não volta pelo Opus do perfil Ana.
- Criado script guard:
  - `/root/.hermes/scripts/ivs_cron_model_guard.py`
- Criado cron guard script-only:
  - `1dd756d835fb` — IVS cron heartbeat model guard — `every 1h`.

## Critério de aceite

O guard deve ficar silencioso quando todos os jobs estiverem conformes. Se aparecer qualquer job LLM sem `openai-codex/gpt-5.5`, ele envia alerta para Maria/Tiaro.

## Observação

Esta regra complementa a governança de custo da Ana: Opus 4.8 continua permitido para revisão médica final sob demanda, mas não para rotinas agendadas, keep-alive, heartbeat ou cron.
