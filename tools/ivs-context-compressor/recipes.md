# Receitas operacionais — IVS Context Compressor

Estas receitas padronizam uso curto do compressor em pipes e comandos recorrentes de debug/log.

## Wrapper curto

Caminho:

```bash
/root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc
```

Formato geral:

```bash
comando_que_gera_saida | /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc <type> <nome-da-evidencia.log> --format json
```

Tipos:

- `clara-log`
- `zapi-webhook`
- `cron-log`
- `gbrain-results`
- `generic`

## Clara/Z-API — últimas linhas do runtime

```bash
tail -n 500 /root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge_runtime.log 2>&1 | \
  /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc clara-log clara-runtime-tail.log --format md
```

## Clara/Z-API — buscar falhas comuns sem expor bruto no chat

```bash
grep -E 'NO_REPLY|zapi-fail|quarkclinic_check_failed|Traceback|ERROR|timeout' \
  /root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge_runtime.log 2>&1 | \
  /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc clara-log clara-falhas-filtradas.log --format json
```

Observação: use `grep` aqui apenas em terminal operacional. Na conversa com ferramentas Hermes, prefira `search_files` para busca em arquivos.

## Cron/Agent OS

```bash
python3 /root/cerebro-vital-slim/cerebro/areas/tecnologia/skills/ivs-agent-operating-layer/scripts/agent_os_cron_auditor.py --json 2>&1 | \
  /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc cron-log agent-os-cron-audit.log --format json
```

## GBrain doctor/health

```bash
python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py --doctor-only --mode doctor-only 2>&1 | \
  /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc gbrain-results gbrain-doctor.log --format json
```

## Qualquer comando longo

```bash
comando_longo 2>&1 | \
  /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc generic comando-longo.log --format md
```

## Recuperar original preservado

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py --recover <sha256_completo>
```

## Governança

- O resumo não substitui a fonte original.
- O original fica preservado por SHA256 em `ops/context-compressor/evidence/`.
- Relatórios/evidências gerados ficam fora do Git por `.gitignore`.
- Para incidente crítico, recuperar e revisar o original antes de concluir.
