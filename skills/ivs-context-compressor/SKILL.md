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

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --input /caminho/arquivo.log \
  --type clara-log \
  --format md
```

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

## Integração opcional com auditoria diária Clara/Z-API

```bash
python3 /root/cerebro-vital-slim/cerebro/areas/tecnologia/skills/ivs-agent-operating-layer/scripts/clara_daily_audit.py \
  --no-save \
  --json \
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
