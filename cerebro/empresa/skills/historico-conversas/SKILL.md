---
name: historico-conversas
description: >
  Consulta o historico completo de conversas de um lead/paciente na planilha central do Instituto Vital Slim ANTES de iniciar qualquer atendimento no WhatsApp. Essa skill deve ser acionada OBRIGATORIAMENTE antes de Clara responder qualquer lead, para evitar respostas genericas e preservar o contexto historico.
  Use quando: receber mensagem nova de lead no WhatsApp, antes de responder qualquer contato, quando precisar saber o historico de um paciente, quando precisar verificar se é lead novo ou recorrente.
metadata:
  version: 1.0.0
  domain: atendimento
  owner: main
---

# Historico de Conversas — Skill de Consulta Pre-Atendimento

## Objetivo

Garantir que a Clara SEMPRE consulte o historico de conversas de um lead/paciente ANTES de responder qualquer mensagem no WhatsApp. Isso evita:
- Respostas genericas para leads conhecidos
- Perguntas repetidas que ja foram respondidas
- Perda de contexto de negociacoes em andamento
- Tratamento inadequado de pacientes ativos

## Fonte de dados

**Google Sheets central:**
- **ID**: `1QXvRhElCx1t7mxMAwGkcvh5V7YyKLjP9zozSGH7LHnM`
- **Conta de acesso**: `medicalemagrecimento@gmail.com`
- **Link**: https://docs.google.com/spreadsheets/d/1QXvRhElCx1t7mxMAwGkcvh5V7YyKLjP9zozSGH7LHnM/

**Abas (sheets) da planilha:**
- `Folha1` — raw log de todas as mensagens (RAW_SHEET_NAME)
- `pacientes` — lista de pacientes ativos (PATIENTS_SHEET_NAME)
- `contexto_paciente` — contexto estruturado por paciente (CONTEXT_SHEET_NAME)

**Apps Script que alimenta a planilha:**
- URL: https://script.google.com/macros/s/AKfycbxmLLmzLtjnmQwBNxPTaCwNEBtbcez3qvz78C5X2dxV1w5CK4R6j-Ky-1CXtvfU-3Hy7Q/exec
- Editor: https://script.google.com/u/3/home/projects/1p7SoEdHMUUKvPeKMHDlrhKOdl9mrhEDOgu-huXf0TW5pqgXXQMDj59PI/edit

## Protocolo Obrigatorio (antes de cada resposta)

### Passo 1 — Identificar o telefone do lead
Extrair o numero do telefone da mensagem recebida.

### Passo 2 — Consultar a planilha
Rodar o script de consulta:
```bash
python3 /root/.openclaw/workspace/skills/historico-conversas/scripts/consultar_historico.py --telefone NUMERO
```

Retorna:
- Se é lead novo ou recorrente
- Historico completo de mensagens daquele numero
- Se ja consta em `pacientes` (paciente ativo)
- Contexto estruturado da aba `contexto_paciente` (se houver)
- Quantas interacoes ja aconteceram
- Estagio do funil (interesse, qualificacao, agendado, paciente ativo)

### Passo 3 — Interpretar o contexto
Com base no retorno:

| Situacao | Como agir |
|----------|-----------|
| Lead novo (sem historico) | Primeira interacao: acolher, apresentar-se, perguntar como pode ajudar |
| Lead recorrente | Retomar do ponto onde parou, NAO fazer perguntas ja respondidas |
| Paciente ativo | Bloqueado pela logica do bridge — NAO responder (Clara so atende leads) |
| Contexto estruturado disponivel | Usar as informacoes para personalizar a resposta |

### Passo 4 — Responder com contexto
So entao gerar a resposta para o lead, partindo do contexto correto.

### Passo 5 — Se nao conseguir acessar a planilha
1. **NAO inventar historico**
2. **NAO fingir que viu mensagens anteriores**
3. **Notificar o Tiaro imediatamente** via Telegram ou WhatsApp (5571986968887)
4. **Responder como primeira interacao acolhedora**, sem citar historico que voce nao viu

## Script de Consulta

Caminho: `/root/.openclaw/workspace/skills/historico-conversas/scripts/consultar_historico.py`

### Uso

```bash
# Consultar por telefone
python3 consultar_historico.py --telefone 557192501702

# Consultar com formato completo
python3 consultar_historico.py --telefone 5571986968887 --json

# Verificar apenas se é paciente ativo
python3 consultar_historico.py --telefone 557192501702 --apenas-status
```

### Credenciais necessarias

- `GOG_KEYRING_PASSWORD` — via 1Password item `gog-keyring-pass`
- Conta Google: `medicalemagrecimento@gmail.com` com scopes de Sheets autorizados

## Regras Criticas

1. **OBRIGATORIO consultar antes de CADA resposta** a lead novo
2. **Nunca responder sem consultar** — mesmo que a consulta demore
3. **Nunca inventar contexto** — se o script falhar, notificar Tiaro
4. **Preservar o historico** — nao apagar nem modificar registros
5. **Privacidade** — nao compartilhar dados de pacientes em respostas a terceiros

## Troubleshooting

- **403 permission denied**: reautorizar gog com scopes de Sheets: `gog auth login -a medicalemagrecimento@gmail.com --services drive,sheets --force-consent`
- **Planilha vazia ou erro**: verificar se o Apps Script fanout esta funcionando (endpoint na bridge Z-API)
- **Telefone nao encontrado**: normal para leads totalmente novos — tratar como primeira interacao
- **Multiplos formatos de telefone**: a planilha pode ter variacoes (com/sem DDI, com/sem DDD). O script normaliza automaticamente.

## Integracao com outras skills

- **tweet-carrossel**: nao usa esta skill
- **omie-api / omie-boletos**: nao usa esta skill  
- **agenda-diaria-whatsapp**: nao usa esta skill (envia para destinatarios fixos)
- **llm-council**: pode ser acionado APOS consulta do historico se precisar avaliar resposta complexa

Esta skill é **especifica para atendimento de leads** no WhatsApp via bridge Z-API.
