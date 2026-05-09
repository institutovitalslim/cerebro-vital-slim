# GRAPH_REPORT — Clara acesso a conselhos

Data: 2026-05-09

## Resumo
Por solicitação de Tiaro, Clara recebeu acesso operacional às skills `conselho-growth-vital-slim` e `llm-council`.

## Governança
Uso restrito a contexto interno autorizado. Não acionar em conversa externa de lead/paciente. Não expor bastidores. Mudança permanente de regra depende de Maria/Tiaro e RC-25/graphify.

## Validação
Configuração validada e gateway recarregado; healthcheck OK.

## Correção técnica adicional — 2026-05-09 14:40 UTC

Após validação em sessão real, foi identificado que a autorização operacional de skills não bastava para chamadas via `sessions_spawn`: faltava liberar os agentIds na allowlist de subagentes.

Ajustes adicionais em `/root/.openclaw/openclaw.json`:
- Criados agentes técnicos:
  - `conselho-growth-vital-slim`
  - `llm-council`
- `clara-whatsapp.subagents.allowAgents` passou a incluir:
  - `conselho-growth-vital-slim`
  - `llm-council`
- `tools.agentToAgent.allow` também passou a incluir os dois conselhos.
- Gateway recarregado e healthcheck OK.

Observação: sessões já abertas podem manter allowlist em cache até nova rodada/contexto; a configuração canônica agora está correta para novas execuções.
