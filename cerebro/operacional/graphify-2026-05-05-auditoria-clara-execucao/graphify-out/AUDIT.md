# AUDIT — Execução 2026-05-05 · Clara / Maria / Conselho Growth

## Corpus auditado via graphify
- Memória diária `memory/2026-05-05.md`.
- Regras operacionais `OPERATING_RULES.md`.
- Excertos redigidos do runtime da Clara contendo RC-26, RC-27, RC-28 e RC-29.
- Skills criadas/alteradas: `conselho-growth-vital-slim`, `rapidapi-social-learning`, `youtube-learning-ivs`, `clara-learning-orchestrator`, `agenda-diaria-whatsapp`.
- Scripts relacionados: RapidAPI, YouTube, orquestrador de aprendizado, Picsart, ElevenLabs e Z-API agenda.
- Crons relevantes da Clara/Maria.

## Achados

### 1. Memória incompleta sobre RC-28 e RC-29
A memória diária registrava RC-26 e RC-27, mas ainda não registrava adequadamente:
- RC-28 — Aprendizado com YouTube;
- RC-29 — Governança do Aprendizado Externo;
- criação da skill `clara-learning-orchestrator`;
- crons silenciosos 07:10, 10:30, 12:40, 17:40 e 21:20.

**Correção:** memória diária deve receber consolidação canônica desta auditoria.

### 2. Cron antigo `agenda-diaria-whatsapp` tinha falha operacional
O cron estava com `delivery: last`, gerando erro: `Delivering to Telegram requires target <chatId>`.

**Correção aplicada:** payload do cron atualizado para usar `delivery.mode=none`, porque o envio real é via Z-API e não precisa anúncio Telegram.

### 3. Credenciais Z-API estavam expostas em prompt/skill/cron/sessões
Foram encontrados tokens da Z-API em documentação operacional e registros de agente.

**Correções aplicadas:**
- Criado `/root/.openclaw/secure/zapi.env` com permissão `600`.
- Ajustado `/root/.openclaw/workspace/ops/zapi_bridge/zapi_bridge.env` para permissão `600`.
- Criado script seguro `/root/.openclaw/workspace/skills/agenda-diaria-whatsapp/scripts/send_agenda.py`.
- Atualizada skill `agenda-diaria-whatsapp` para não documentar tokens.
- Atualizado cron `agenda-diaria-whatsapp` para chamar o script canônico.
- Redigidos tokens Z-API em memórias/sessões/documentos não-env.

### 4. Picsart MCP token
O token Picsart já estava tratado como sensível, mas havia ocorrências em sessões/logs históricos.

**Correção aplicada:** redigidas ocorrências não-env. O wrapper `picsart.py` mantém sanitização de saída.

### 5. Configuração Clara
Runtime da Clara contém exatamente uma ocorrência de cada bloco:
- RC-26;
- RC-27;
- RC-28;
- RC-29.

Sem duplicação detectada nos blocos de regra.

## Status pós-correção
- Scripts Python relevantes compilam sem erro.
- Z-API saiu de prompt/cron operacional e passou para script seguro.
- Aprendizado da Clara agora tem coleta, filtro, registro e revisão.
- Memória precisa ser atualizada com este resumo para fechar RC-25.
