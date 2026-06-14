# Playbook — Sincronização GBrain IVS

## Objetivo
Manter o sidecar GBrain alinhado ao cérebro canônico sem transformar o banco GBrain em fonte de verdade.

## Comandos seguros

### Sincronização completa

```bash
python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py --mode manual
```

O script:
- espelha o cérebro canônico para `/root/.local/share/ivs-gbrain/import/ivs-brain`;
- roda `import --no-embed`, `extract --stale --catch-up`, `embed --stale`, `doctor` e `stats`;
- grava relatório runtime em `/root/.local/share/ivs-gbrain/reports/`;
- atualiza o resumo canônico em `cerebro/gbrain/sync/latest-health.md`.

### Validação rápida sem reimportar

```bash
python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py --doctor-only
```

### Regressão de uso pelos agentes

```bash
python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_regression.py
```

Valida se o GBrain encontra informação suficiente para os reflexos mínimos de Maria, Clara, João, operações, marketing, apresentação e financeiro.

## Quando rodar
- Após RC-25 estrutural.
- Após alteração grande em agentes/skills.
- Após reorganização de área do cérebro.
- Diariamente via cron operacional.

## Cron operacional

Linha oficial:

```cron
40 10 * * * /usr/bin/python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py --mode cron >> /root/.local/share/ivs-gbrain/reports/cron.log 2>&1
```

Horário: 10:40 UTC / 07:40 Bahia.

## Pós-RC-25 obrigatório

Depois de qualquer RC-25 relevante:

```bash
python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py --mode post-rc25
python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_regression.py
```

Critério mínimo:
- `embed_staleness`: OK;
- regressão: 100%;
- sem erro bloqueante no doctor;
- warnings documentados em `latest-health.md`.

## Proibido
- Rodar writeback automático no cérebro canônico.
- Salvar segredos.
- Reestruturar pastas em massa sem backup e RC-25.
