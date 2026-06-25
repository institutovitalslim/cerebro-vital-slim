# Relatório executivo — IVS Context Compressor

Data: 2026-06-25
Origem: reverse governado do repositório `headroomlabs-ai/headroom` via `repo-reverse-ivs`.

## Entrega

Foi criada a primeira versão funcional do **IVS Context Compressor**, uma camada local para reduzir ruído de logs/outputs antes de entregar contexto aos agentes, preservando o original por SHA256.

## Artefatos criados

- Ferramenta principal: `tools/ivs-context-compressor/ivs_context_compressor.py`
- Testes: `tools/ivs-context-compressor/tests/test_ivs_context_compressor.py`
- README operacional: `tools/ivs-context-compressor/README.md`
- Exemplo sanitizado: `tools/ivs-context-compressor/examples/clara_sample.log`
- Skill canônica no cérebro: `skills/ivs-context-compressor/SKILL.md`
- Skill Hermes criada: `openclaw-imports/ivs-context-compressor`

## Capacidades v0

- Entrada por arquivo (`--input`) ou pipe/stdin (`--stdin --stdin-name`).
- Métricas estimadas de redução de contexto/tokens:
  - `estimated_tokens_original`;
  - `estimated_tokens_redacted`;
  - `estimated_tokens_compressed_context`;
  - `estimated_token_reduction_pct`;
  - `compression_effect`.
- Redaction de PII/secrets:
  - `mcp_token` em URL;
  - bearer token;
  - api key/token/secret/password/senha;
  - e-mail;
  - telefone BR com DDD;
  - CPF;
  - tokens/instâncias Z-API óbvios.
- Preservação do original em `/root/cerebro-vital-slim/ops/context-compressor/evidence/`.
- Hash SHA256 do original.
- Extração de linhas críticas por tipo operacional:
  - `clara-log`;
  - `zapi-webhook`;
  - `cron-log`;
  - `gbrain-results`;
  - `generic`.
- Geração de relatório JSON e Markdown.
- Recuperação do original por SHA256.

## Validação real executada

Comando de teste:

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/tests/test_ivs_context_compressor.py
python3 -m py_compile \
  /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  /root/cerebro-vital-slim/tools/ivs-context-compressor/tests/test_ivs_context_compressor.py
```

Resultado: `ok`

Smoke real com exemplo Clara:

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --input /root/cerebro-vital-slim/tools/ivs-context-compressor/examples/clara_sample.log \
  --type clara-log \
  --format json
```

Resultado resumido:

```json
{
  "ok": true,
  "sha256": "36145672db8b8b3b485f4b578850686fd8f099bc5ecf87b4ed37cfa71be4a692",
  "critical_line_count": 5,
  "redactions": {
    "api_key": 1,
    "email": 1,
    "phone_br": 1,
    "cpf": 1
  },
  "message_ids": ["MSG123456789", "MSG987654321"]
}
```
## Novo uso por pipe/stdin

Agora qualquer comando pode mandar saída direto para o compressor:

```bash
algum_comando_que_gera_log | python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --stdin \
  --stdin-name saida-comando.log \
  --type cron-log \
  --format json
```

Ou com o wrapper curto versionado:

```bash
algum_comando_que_gera_log | /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc cron-log saida-comando.log --format json
```

Alias operacional instalado no PATH do servidor:

```bash
algum_comando_que_gera_log | ivscc cron-log saida-comando.log --format json
```

Verificação da instalação:

```text
/usr/local/bin/ivscc -> /root/cerebro-vital-slim/tools/ivs-context-compressor/ivscc
```

Receitas operacionais documentadas em `tools/ivs-context-compressor/recipes.md`.

Resultado resumido do smoke real com wrapper:

```json
{
  "ok": true,
  "input_path": "stdin",
  "input_name": "wrapper-smoke.log",
  "error_like_count": 1,
  "redactions": {"phone_br": 1},
  "compression_effect": "expanded"
}
```

Observação: `expanded` é esperado em inputs muito pequenos porque o resumo/evidência mínima pode ser maior que a linha original; em logs grandes, a métrica tende a mostrar redução.

Recuperação validada:

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --recover 36145672db8b8b3b485f4b578850686fd8f099bc5ecf87b4ed37cfa71be4a692
```

Resultado: original localizado em `/root/cerebro-vital-slim/ops/context-compressor/evidence/36145672db8b8b3b485f4b578850686fd8f099bc5ecf87b4ed37cfa71be4a692.log`.

## Decisão operacional

A v0 já pode ser usada em modo **local/read-only** para:

1. auditorias da Clara/Z-API;
2. logs de cron;
3. outputs longos do GBrain;
4. relatórios técnicos internos.

## Retenção/limpeza segura

Criada rotina de limpeza com dry-run por padrão:

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --cleanup \
  --cleanup-retention-days 30
```

Aplicação real exige confirmação explícita:

```bash
python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py \
  --cleanup \
  --apply-cleanup \
  --cleanup-retention-days 30
```

Smoke real em produção, sem apagar nada:

```json
{
  "ok": true,
  "mode": "dry-run",
  "retention_days": 30,
  "candidate_count": 0,
  "candidate_bytes": 0,
  "deleted_count": 0,
  "safety": "dry-run by default; deletion requires --apply-cleanup"
}
```

Segurança: a rotina só considera arquivos antigos dentro de `reports/` e `evidence/`, com sufixos conhecidos (`.json`, `.md`, `.txt`, `.log`, `.meta.json`), e preserva `.gitignore`.

## Integração opcional já aplicada

As auditorias abaixo receberam o flag opcional `--compress-context`.

### Clara/Z-API

```bash
python3 /root/cerebro-vital-slim/cerebro/areas/tecnologia/skills/ivs-agent-operating-layer/scripts/clara_daily_audit.py \
  --no-save \
  --json \
  --compress-context
```

Resultado real do smoke:

```json
{
  "ok": true,
  "severity": "MÉDIA",
  "compressed_context": {
    "ok": true,
    "critical_line_count": 12,
    "redactions": {"phone_br": 21}
  }
}
```

### Crons Agent OS

```bash
python3 /root/cerebro-vital-slim/cerebro/areas/tecnologia/skills/ivs-agent-operating-layer/scripts/agent_os_cron_auditor.py \
  --json \
  --compress-context
```

Resultado real do smoke:

```json
{
  "ok": true,
  "compressed_context": {
    "ok": true,
    "critical_line_count": 2,
    "redactions": {}
  }
}
```

### Health do GBrain

```bash
python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py \
  --doctor-only \
  --mode doctor-only \
  --compress-context
```

Resultado real do smoke:

```json
{
  "ok": false,
  "mode": "doctor-only",
  "compressed_context": {
    "ok": true,
    "critical_line_count": 6,
    "redactions": {}
  }
}
```

Observação: no smoke do GBrain, `ok:false` veio do health atual do GBrain/doctor, não do compressor; o compressor executou com `ok:true` e preservou evidência.

Governança mantida: o compressor é pós-processador de observabilidade; falha nele não derruba a auditoria, não envia WhatsApp, não pausa/despausa Clara e não entra no caminho crítico do atendimento.

Ainda não deve ser colocada como proxy ou dependência crítica no caminho da Clara.

## Próximos incrementos recomendados

1. Criar fixtures reais anonimizados de Z-API e cron.
2. Adicionar métrica de redução percentual de caracteres/tokens.
3. Adicionar modo `--stdin` para uso em pipes.
4. Adicionar política de retenção/limpeza para originais preservados.
