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

Arquivo:

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --input /caminho/para/log.txt \
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

Wrapper curto:

```bash
algum_comando_que_gera_log | /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc cron-log saida-comando.log --format json
```

Receitas operacionais: `tools/ivs-context-compressor/recipes.md`.

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

## Métricas de redução

Cada JSON/Markdown inclui estimativas locais, sem dependência de tokenizer externo:

- `estimated_tokens_original`
- `estimated_tokens_redacted`
- `estimated_tokens_compressed_context`
- `estimated_token_reduction_pct`
- `compression_effect`: `reduced`, `expanded` ou `neutral`

A estimativa usa aproximação conservadora de 4 caracteres por token. Em entradas muito pequenas, o resumo pode ficar maior que o original; nesses casos `compression_effect=expanded`.

## Integrações opcionais read-only

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

O campo `compressed_context` no JSON retorna SHA256, caminhos do Markdown/JSON comprimidos e evidência original preservada. Falha no compressor não derruba a auditoria; ele é observabilidade, não dependência de produção.

## Teste

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/tests/test_ivs_context_compressor.py
```

## Limitações

- Não faz diagnóstico clínico nem interpretação médica.
- Não deve ser usado para ocultar problema operacional; sempre recuperar original em incidentes críticos.
- A anonimização é heurística; dados altamente sensíveis devem ser revisados antes de circular em relatório amplo.
