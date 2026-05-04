# Sessão 2026-04-29 — Clara v2 + Maria + Roteamento OpenClaw

## Contexto inicial
Clara WhatsApp pausada há 20+ dias por confundir paciente com Tiaro. Tinha sido feito o trabalho de mapeamento (graphify), prompt v2 escrito (~500 linhas, 33 communities, 122 nodes), enviado para Telegram topic 768 aguardando aprovação.

## Decisões e mudanças aplicadas

### 1. Aplicação do prompt v2 da Clara em produção
- Backup do prompt antigo (`clara_system_prompt.md.bak-2026-04-29`)
- Substituição por v2 (16.082 bytes, 24+1 RCs canônicas)
- Bridge ZAPI lê o prompt a cada request — não precisa restart

### 2. Reorganização de papéis
- **Clara WhatsApp** (clara-whatsapp): Concierge Comercial — APENAS WhatsApp via bridge ZAPI. Atende leads/pacientes externos. Foco: agendamento de consulta.
- **Maria Telegram** (maria-gerente): Gerente Geral. Default agent. Responde no DM do bot e em todos os tópicos do grupo "AI Vital Slim" exceto o tópico Reels.
- **João Reels** (agente-reels-intel): Especialista em reels. Restrito ao tópico Reels (topic_id=5782) do grupo Telegram.

### 3. Configuração OpenClaw
Arquivo: `/root/.openclaw/openclaw.json`
- agents.list = [maria-gerente (default:true), agente-reels-intel, clara-whatsapp]
- Removido model override per-agent → usa default chain (gpt-5.5 primary, kimi fallback)

### 4. Topic routing
Arquivo: `/root/.openclaw/topic-agent-routing.json`
```json
{
  "version": 1,
  "routes": [
    {"channel": "telegram", "groupId": "-1003803476669:topic:5782", "agentId": "agente-reels-intel"},
    {"channel": "telegram", "groupId": "-1003803476669", "topicId": "5782", "agentId": "agente-reels-intel"}
  ]
}
```
Formato composite (`groupId:topic:N`) é o que o gateway computa em `groupResolution.id`.

### 5. Bridge ZAPI Clara — patches
Arquivo: `/root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge.py`
- Header `x-openclaw-agent-id: clara-whatsapp` adicionado
- env: `OPENCLAW_SESSION_PREFIX=agent:clara-whatsapp:zapi` (formato canônico exigido por parseAgentSessionKey)
- env: `OPENCLAW_AGENT_REF=openclaw/clara-whatsapp`
- env: `OPENCLAW_MODEL_OVERRIDE=openai-codex/gpt-5.5`

### 6. Runtime OpenClaw — 3 patches críticos
Arquivo: `/usr/lib/node_modules/openclaw/dist/get-reply-bONH39Y6.js` e `session-key-L2XsSJT_.js`

**Patch 1 — `canRouteTopicAgent` honra default agent não-main:**
```js
const _ocDefaultAgents = listAgentEntries(cfg);
const _ocDefaultAgentId = normalizeAgentId(((_ocDefaultAgents.find((a) => a?.default) ?? _ocDefaultAgents[0])?.id?.trim()) || "main");
const canRouteTopicAgent = !requestedSessionKey
  || requestedSessionAgent?.agentId === "main"
  || requestedSessionAgent?.agentId === _ocDefaultAgentId;
```
Sem isso, sessões bound ao default (Maria) bypassavam topic routing.

**Patch 2 — `toAgentStoreSessionKey` usa target agent, não source:**
```js
// ANTES (bug):
if (parsed) return `agent:${parsed.agentId}:${parsed.rest}`;
// DEPOIS:
if (parsed) return `agent:${normalizeAgentId(params.agentId)}:${parsed.rest}`;
```
Sem isso, migração de session key não acontecia (mantinha agentId antigo).

**Patch 3 — `getReplyFromConfig` honra topic routing:**
```js
let agentId = resolveSessionAgentId(...);
const _outerCanRoute = !agentSessionKey || requestedAgent?.agentId === "main" || requestedAgent?.agentId === defaultId;
if (_outerCanRoute) {
  const _outerRouted = await resolveTopicAgentIdFromInbound({cfg, ctx, groupResolution});
  if (_outerRouted) agentId = _outerRouted;
}
```
Sem isso, prompt/model eram carregados ANTES da migração da sessão.

## Validação end-to-end

| Cenário | Agente esperado | Resultado |
|---|---|---|
| Tópico Reels (5782) | João | ✅ |
| DM Telegram | Maria | ✅ |
| Outros tópicos do grupo | Maria | ✅ |
| WhatsApp via bridge — Persona Paula (cética) | Clara v2 | ✅ |
| WhatsApp — Persona Roberto (Mounjaro) | Clara v2 | ✅ |
| WhatsApp — Persona Carla (lead quente) | Clara v2 | ✅ |
| WhatsApp — Persona Luiza (fria "quanto custa") | Clara v2 | ✅ |
| WhatsApp — ataque de prompt injection | Clara v2 | ✅ defletido |
| WhatsApp — "Oi Clara é Tiaro" | Clara v2 | ✅ |

## Conselho LLM (Karpathy 5-advisors + peer review + chairman)

**Onde concordou:**
- Os 6 testes não validam prontidão real (personas sintéticas)
- Infra antes de prompt (systemd, logs, healthcheck)
- 25 RCs são cicatrizes, não design

**Blind spots iniciais (depois corrigidos pelo Tiaro):**
- LGPD/CFM 2.314 NÃO se aplica — Clara é apenas concierge comercial, não faz triagem clínica
- Riscos clínicos não se aplicam pelo escopo restrito

## Despause
Estado: `paused: false` ativo em produção.

## Próximos passos sugeridos
- [ ] Systemd para zapi_clara_bridge (atualmente processo Python solto)
- [ ] Healthcheck + UptimeRobot
- [ ] Stop-loss explícito (volume controlado primeiros dias)
- [ ] Comandos Telegram para Maria pausar/despausar Clara
- [ ] Cron de 3h pra lembrar Tiaro de pausa indefinida
