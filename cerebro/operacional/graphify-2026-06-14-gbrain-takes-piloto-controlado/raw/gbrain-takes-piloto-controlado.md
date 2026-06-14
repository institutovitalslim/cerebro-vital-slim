---
type: raw-rc25
status: active
owner: maria
source_of_truth: true
created: 2026-06-14
updated: 2026-06-14
rc25: graphify-2026-06-14-gbrain-takes-piloto-controlado
---
# RC-25 — GBrain IVS piloto controlado de takes

## Decisão
Após autorização operacional de Tiaro, foi executado piloto controlado de `takes` no GBrain IVS.

Resultado: `takes` permanece desligado. O piloto varreu páginas elegíveis e não extraiu claims úteis; portanto, não há ganho operacional imediato que justifique deixar o bootstrap aberto.

## Execução
Configuração temporária aplicada apenas para o piloto:

```bash
gbrain config set takes.bootstrap_enabled true --force
```

Dry-runs:
- `gbrain takes extract --from-pages --dry-run --max-pages 20 --holder ivs-gbrain-pilot`
  - 0 claims / 20 páginas
- `gbrain takes extract --from-pages --dry-run --max-pages 100 --holder ivs-gbrain-pilot`
  - 0 claims / 100 páginas

Piloto real limitado:

```bash
gbrain takes extract --from-pages --yes --max-pages 250 --holder ivs-gbrain-pilot
```

Resultado:
- 0 claims
- 198 páginas escaneadas
- nenhuma regra canônica alterada
- nenhum writeback automático habilitado

Configuração restaurada:

```bash
gbrain config set takes.bootstrap_enabled false --force
```

## Validação pós-piloto
- Doctor-only: OK
- Overall health: 65/100
- Brain score: 70/100
- Embed staleness: OK
- Regressão de agentes: 6/6 OK

## Governança
- `takes` é recurso opt-in e deve continuar exigindo decisão explícita para novo piloto.
- Não usar `takes` como substituto do Graphify/RC-25.
- Não transformar opinião externa ou extração automática em regra canônica.
- Markdown do `cerebro-vital-slim` continua fonte de verdade.
