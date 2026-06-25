# IVS Context Compressor

Camada local de compressão segura de contexto para agentes operacionais IVS.

## Origem

Criado após reverse engineering governado do repositório público `headroomlabs-ai/headroom` via skill `repo-reverse-ivs`.

O Headroom serviu como referência funcional para o padrão:

`conteúdo bruto → classificação → compressão/redaction → preservação do original → recuperação por hash`

Esta implementação é IVS-first e não copia código do repositório externo.

## Objetivo

Reduzir custo, ruído e tamanho de contexto em:

- logs da Clara/Z-API;
- auditorias de recebidas sem envio;
- logs de cron;
- outputs longos de scripts;
- resultados extensos do GBrain;
- relatórios técnicos internos.

## Regra de governança

O compressor **não substitui fonte canônica**. Ele cria uma visão compacta e redigida para leitura operacional, preservando o original em diretório restrito com SHA256.

## Uso rápido

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --input /caminho/para/log.txt \
  --type clara-log \
  --format md
```

Tipos aceitos:

- `clara-log`
- `zapi-webhook`
- `cron-log`
- `gbrain-results`
- `generic`

## Recuperar original preservado

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --recover <sha256_completo>
```

## Saídas

Relatórios:

`/root/cerebro-vital-slim/ops/context-compressor/reports/`

Evidências originais:

`/root/cerebro-vital-slim/ops/context-compressor/evidence/`

Cada execução gera:

- JSON estruturado;
- Markdown operacional;
- original preservado;
- metadados com SHA256, origem e timestamp.

## PII e secrets

Redige por padrão:

- `mcp_token` em URL;
- bearer tokens;
- api keys/tokens/secrets/password/senha;
- e-mails;
- CPF;
- telefones brasileiros;
- tokens/instâncias Z-API óbvios.

## Evidências preservadas no resumo

Extrai e preserva quando encontrados:

- timestamps;
- `messageId` / `message_id`;
- `trace_id` / `request_id`;
- status codes;
- linhas com erro/falha/timeout;
- eventos Z-API relevantes;
- eventos QuarkClinic/Clara relevantes;
- falhas de cron/agente.

## Teste

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/tests/test_ivs_context_compressor.py
```

## Limitações

- Não faz diagnóstico clínico nem interpretação médica.
- Não deve ser usado para ocultar problema operacional; sempre recuperar original em incidentes críticos.
- A anonimização é heurística; dados altamente sensíveis devem ser revisados antes de circular em relatório amplo.
