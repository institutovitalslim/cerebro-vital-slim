# Infraestrutura - Sistemas e Integracoes

## Stack tecnico (RC-20)

### WhatsApp - canal de leads e pacientes
- **API**: Z-API (zapi.io)
- **Bridge**: `zapi-clara-bridge.service` na VPS 187.77.58.193
- **Codigo**: `/root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge.py`
- **Porta**: 127.0.0.1:8787
- **Webhook**: `/webhook/<TOKEN>` recebe eventos do Z-API
- **Outbound**: chamada direta a API Z-API quando Clara responde

### Telegram - canal interno com equipe
- **Gateway**: openclaw-gateway (systemd user service)
- **Grupo principal**: -1003803476669 ("AI Vital Slim")
- **Topicos**: Pacientes (questionarios), Gestao de Estoque, Evolucao Pessoal e Profissional
- **Membros**: Tiaro, Liane, Dra. Daniely, Clara (bot)

⚠️ **Isolamento entre canais**: NAO ha bridge entre WhatsApp e Telegram. Conversa de paciente nunca vaza pro Telegram.

## Sistemas integrados

### QuarkClinic (fonte de verdade RC-21)
- **URL**: https://api.quark.tec.br/clinic/ext (auth via QUARKCLINIC_AUTH_TOKEN)
- **Funcao**: prontuario eletronico + CRM da clinica
- **Uso da Clara**: classificar contato (Lead vs Paciente)
- **Criterio**: 0 atendimentos = Lead / 1+ atendimentos = Paciente

### Sistema proprio de pre-consulta (RC-22)
- **URL**: https://preconsulta.institutovitalslim.com.br
- **Funcao**: questionarios pre-consulta
- **Fluxo**: paciente preenche → automatico para Telegram topico Pacientes
- **Substitui**: Google Forms antigos que ainda circulam em scripts da Liane

### InfinityPay (CloudWalk) - gateway pagamento
- **Status**: SEM API disponivel
- **Modelo**: Tiaro/Liane emite link manualmente
- **Default**: pre-consulta R$ 300 cartao 2x sem juros
- **Fluxo Clara**: handoff por WhatsApp via RC-16

### Memed - receita digital
- **URL**: https://assistant.memed.com.br
- **Formato**: link com codigo de 4 digitos para abrir/baixar PDF assinado
- **Quem envia**: equipe humana (Liane/Tiaro)
- **Clara**: orienta paciente sobre como abrir o link se perguntar

### Galileu Online - bioimpedancia
- **URL**: https://galileuonline.com.br
- **Funcao**: relatorio do exame de bioimpedancia
- **Quem envia link**: equipe humana
- **Formato**: link com hash ID do paciente

### Banco Inter
- **Funcao**: emissao de boletos para pacientes em programa
- **Visivel**: Clara/equipe envia PDFs de boleto ("Boleto_PXXX-XXX_R$XXX_VencDD-MM-YYYY.pdf")

### Omie - ERP
- **Funcao**: financeiro/contabil da clinica
- **Visivel**: Liane comenta "baixa no sistema da Omie" quando paciente pergunta status pagamento

## Endpoints administrativos do bridge

### GET /admin/status
Consulta estado da pausa.

### POST /admin/pause
Acoes: pause / pause_indefinite / unpause / status

Detalhes em `operacoes/endpoints-bridge.md`.

## Variaveis de ambiente (zapi_clara_bridge)

```
BRIDGE_HOST                 # 0.0.0.0 default
BRIDGE_PORT                 # 8787
OPENCLAW_GATEWAY_URL        # http://127.0.0.1:18789/v1/responses
OPENCLAW_GATEWAY_TOKEN      # token do agente
OPENCLAW_AGENT_REF          # openclaw/main
OPENCLAW_MODEL_OVERRIDE     # openai/gpt-5.4
QUARKCLINIC_AUTH_TOKEN      # auth para classificar paciente
QUARKCLINIC_BASE_URL        # https://api.quark.tec.br/clinic/ext
ZAPI_INSTANCE_ID            # instancia Z-API
ZAPI_TOKEN                  # token Z-API
ZAPI_CLIENT_TOKEN           # client token Z-API
ZAPI_BASE_URL               # construido com instance + token
ZAPI_SEND_TEXT_PATH         # /send-text
APPS_SCRIPT_FANOUT_URL      # webhook para Google Apps Script
WEBHOOK_PATH_TOKEN          # token na URL do webhook
BRIDGE_SHARED_SECRET        # X-Bridge-Secret para admin endpoints
CLARA_NOTIFY_PHONE          # 5571986968887 (Tiaro)
CLARA_CONTROL_FILE          # /root/.openclaw/workspace/ops/zapi_bridge/clara_control_state.json
CLARA_LEADS_FILE            # /root/.openclaw/workspace/ops/zapi_bridge/clara_leads_state.json
CLARA_SYSTEM_PROMPT_FILE    # /root/.openclaw/workspace/ops/zapi_bridge/clara_system_prompt.md
CLARA_ACTIVATION_PHRASE     # "Gostaria de saber mais informacoes sobre o Instituto Vital Slim"
DEDUP_TTL_SECONDS           # 600 (10 min)
HTTP_TIMEOUT_SECONDS        # 90
```

## Modelo de IA

- **OpenAI GPT-5.4** (via OpenClaw gateway)
- Override: `OPENCLAW_MODEL_OVERRIDE=openai/gpt-5.4`
- Memoria semantica: aguardando integracao OpenAI (atualmente acessa via memory_search por keyword/topic)

## Cache e dedup

- `SEEN`: OrderedDict em memoria com TTL 600s para deduplicar mensagens (evita responder mesma message_id 2x se Z-API reenviar webhook)

## Fluxo de uma mensagem entrante (resumo)

```
1. Paciente envia mensagem WhatsApp
2. Z-API entrega webhook → http://VPS:8787/webhook/<TOKEN>
3. Bridge recebe → fanout para Apps Script (analytics)
4. Bridge filtra: from_me? group_message? sem texto? duplicado?
5. Bridge resgata estado:
   - should_pause_clara() → check global pause + TTL
   - is_existing_patient() → consulta QuarkClinic
   - should_respond_to_lead() → check leads_state
6. Se OK: chama OpenClaw gateway com prompt + texto
7. Recebe resposta → envia via Z-API API
8. Loga sucesso/falha
```

## Source of truth

MEMORIA_CONSOLIDADA secao 10. RC-20.
