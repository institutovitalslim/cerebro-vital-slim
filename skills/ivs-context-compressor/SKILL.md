---
name: ivs-context-compressor
description: Compressão segura IVS-first de logs, outputs de tools, resultados GBrain e auditorias, com redaction de PII/secrets, preservação do original por SHA256 e recuperação governada.
---

# IVS Context Compressor

## Quando usar

Use quando Maria/Tiaro/João/Ana/Pedro precisarem analisar contexto grande antes de entregar a um agente ou relatório:

- logs da Clara/Z-API;
- auditorias de “recebidas sem envio”;
- logs de cron e falhas `assistant turn failed`;
- resultados extensos do GBrain;
- outputs longos de scripts;
- blocos JSON/webhook grandes;
- relatórios técnicos que podem conter PII/secrets.

## Regra de governança

O compressor **não substitui fonte canônica**. Ele gera uma visão compacta/redigida e preserva o original localmente com SHA256 para recuperação.

Para incidentes críticos, sempre confira o original preservado antes de concluir.

## Comando principal

Arquivo:

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --input /caminho/arquivo.log \
  --type clara-log \
  --format md
```

Pipe/stdin:

```bash
algum_comando_que_gera_log | python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --stdin \
  --stdin-name saida-comando.log \
  --type cron-log \
  --format json
```

Wrapper curto versionado:

```bash
algum_comando_que_gera_log | /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc cron-log saida-comando.log --format json
```

Alias operacional instalado no PATH do servidor:

```bash
algum_comando_que_gera_log | ivscc cron-log saida-comando.log --format json
```

Instalação do alias:

```bash
ln -sfn /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc /usr/local/bin/ivscc
```

Receitas operacionais: `tools/ivs-context-compressor/recipes.md`.

Tipos aceitos:

- `clara-log`
- `zapi-webhook`
- `cron-log`
- `gbrain-results`
- `generic`

## Recuperar original

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --recover <sha256_completo>
```

## Retenção/limpeza segura

Dry-run por padrão — não apaga nada:

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --cleanup \
  --cleanup-retention-days 30
```

Aplicar limpeza exige flag explícito:

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --cleanup \
  --apply-cleanup \
  --cleanup-retention-days 30
```

Segurança: só remove arquivos antigos em `reports/` e `evidence/`, com sufixos conhecidos (`.json`, `.md`, `.txt`, `.log`, `.meta.json`), preservando `.gitignore`.

## Saídas padrão

- Relatórios JSON/Markdown: `/root/cerebro-vital-slim/ops/context-compressor/reports/`
- Originais preservados: `/root/cerebro-vital-slim/ops/context-compressor/evidence/`

## O que preserva no resumo

- timestamps;
- `messageId`, `message_id`, `idMensagem`;
- `trace_id`, `request_id`, `run_id`;
- status codes;
- linhas com erro/falha/timeout;
- eventos `NO_REPLY`, `zapi-fail`, `zapi-commit`, QuarkClinic, webhook, cron.

## O que redige por padrão

- `mcp_token` em URL;
- bearer tokens;
- api keys/tokens/secrets/password/senha;
- e-mails;
- CPF;
- telefones brasileiros;
- tokens/instâncias Z-API óbvios.

## Integrações opcionais read-only

### Métricas de redução

Cada execução inclui no JSON/Markdown:

- `estimated_tokens_original`
- `estimated_tokens_redacted`
- `estimated_tokens_compressed_context`
- `estimated_token_reduction_pct`
- `compression_effect`: `reduced`, `expanded` ou `neutral`

A estimativa usa aproximação local de 4 caracteres por token. Em entradas pequenas, o resumo pode ficar maior que o original; isso aparece como `compression_effect=expanded`.

### Auditoria diária Clara/Z-API

```bash
python3 /root/cerebro-vital-slim/cerebro/areas/tecnologia/skills/ivs-agent-operating-layer/scripts/clara_daily_audit.py \
  --no-save \
  --json \
  --compress-context
```

### Auditoria de crons Agent OS

```bash
python3 /root/cerebro-vital-slim/cerebro/areas/tecnologia/skills/ivs-agent-operating-layer/scripts/agent_os_cron_auditor.py \
  --json \
  --compress-context
```

### Health do GBrain

```bash
python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py \
  --doctor-only \
  --mode doctor-only \
  --compress-context
```

- Campo novo no JSON: `compressed_context`.
- Modo seguro: pós-processador read-only; falha do compressor não falha a auditoria.
- Não envia WhatsApp, não pausa/despausa Clara, não altera estado quando combinado com `--no-save`.

## Teste obrigatório após alteração

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/tests/test_ivs_context_compressor.py
python3 -m py_compile \
  /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  /root/cerebro-vital-slim/tools/ivs-context-compressor/tests/test_ivs_context_compressor.py
```

## Origem

Criado após reverse governado do Headroom (`headroomlabs-ai/headroom`) via `repo-reverse-ivs`. O Headroom foi usado como inspiração funcional; esta implementação é própria do IVS.
