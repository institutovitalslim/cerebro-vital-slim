---
name: ivs-agent-communications
description: "MUST USE when any IVS agent needs to send, receive, hand off, notify, or ask another IVS agent something (Ana ↔ João, Maria ↔ Clara, Pedro ↔ Maria, Jarvis ↔ agents). Provides a local governed mailbox with redaction and no patient contact."
metadata:
  version: 1.0.0
  owner: Maria — Instituto Vital Slim
  governance: read_only_external_no_patient_contact
---

# IVS Agent Communications

## Objetivo

Permitir comunicação operacional entre todos os agentes IVS sem depender de mensagem ao Tiaro, sem WhatsApp, sem publicação externa e sem contato com paciente/lead.

Use sempre que precisar falar com outro agente:

- Ana enviar pauta científica para João;
- João pedir validação científica para Ana;
- Clara escalar achado operacional para Maria;
- Pedro pedir contexto financeiro para Maria;
- Jarvis coordenar especialistas;
- qualquer agente registrar handoff para outro.

## Comando canônico

```bash
python3 /root/cerebro-vital-slim/scripts/ivs_agent_message.py send \
  --from ana \
  --to joao \
  --subject "Título curto" \
  --body "Mensagem objetiva" \
  --next-action "O que o destinatário deve fazer" \
  --sensitivity marketing \
  --priority normal \
  --json
```

Também disponível como atalho:

```bash
ivs-agent-message send --from ana --to joao --subject "..." --body "..." --next-action "..." --sensitivity marketing --json
```

## Ler inbox

```bash
ivs-agent-message inbox --agent joao --status open --json
ivs-agent-message inbox --agent ana --status all --limit 20 --json
```

## Marcar status

```bash
ivs-agent-message update --id iam-YYYYMMDD-HHMMSS-xxxx --status ack --json
ivs-agent-message update --id iam-YYYYMMDD-HHMMSS-xxxx --status done --json
ivs-agent-message update --id iam-YYYYMMDD-HHMMSS-xxxx --status blocked --json
```

## Agentes aceitos

Aliases aceitos:

| Agente | Aliases |
|---|---|
| Maria | `maria`, `maria-gerente` |
| Ana | `ana`, `ana-medica-cientifica` |
| João | `joao`, `joão`, `agente-reels-intel` |
| Clara | `clara`, `clara-whatsapp` |
| Pedro | `pedro`, `pedro-controller-ivs` |
| Jarvis | `jarvis`, `jarvis-ivs` |
| Eduardo | `eduardo`, `eduardo-ivs` |
| Conselho Growth | `conselho-growth`, `conselho-growth-vital-slim` |
| LLM Council | `llm-council` |

## Sensibilidades

Use uma das opções:

- `internal`
- `marketing`
- `clinical`
- `lead`
- `patient`
- `financial`
- `tech`
- `compliance`

## Guardrails

- Este barramento **não envia WhatsApp**, **não publica conteúdo**, **não fala com paciente/lead** e **não executa financeiro**.
- Telefones, CPF e e-mails são redigidos automaticamente.
- Para assunto com paciente/lead, envie contexto sanitizado e peça ação ao agente responsável; não inclua PII desnecessária.
- Ação sensível continua exigindo autorização explícita do Tiaro conforme regras do agente.
- Use `evidence` com caminhos/IDs quando precisar, em vez de colar dados sensíveis no corpo.

## Exemplo real: Ana → João

```bash
ivs-agent-message send \
  --from ana \
  --to joao \
  --subject "Pauta científica para Reels — resistência insulínica" \
  --body "Ana validou que o conteúdo deve tratar resistência insulínica como hipótese educativa, sem diagnóstico. Evitar promessa de emagrecimento." \
  --next-action "João transformar em roteiro com linguagem educativa e enviar para compliance antes de publicar." \
  --sensitivity marketing \
  --priority normal \
  --json
```

## Verificação mínima

Depois de enviar, valide se chegou:

```bash
ivs-agent-message inbox --agent joao --status open --json
```

## Pitfall: aviso ao agente ≠ aviso ao Tiaro

Quando Tiaro pedir explicitamente para “informar/avisar o agente”, não basta responder ao Tiaro nem apenas registrar no barramento interno. Faça o canal que o agente realmente vê:

1. **Barramento interno IVS** (`ivs-agent-message`) para handoff rastreável.
2. **Canal visível do agente**, quando existir e for o canal operacional atual.
3. **Watcher de inbox do agente**, quando a mensagem exigir resposta/ação do agente.
4. Reporte ao Tiaro com o ID real da entrega.

### Pitfall crítico: mensagem enviada por bot não vira input do próprio agente

Se Maria usa `hermes send` para postar no chat do agente, isso pode aparecer visualmente no Telegram, mas **não garante que o agente processe**:

- bot não recebe a própria mensagem como inbound;
- bot geralmente não processa mensagem de outro bot;
- DM `telegram:971050173` nos perfis João/Pedro/Jarvis é a DM do Tiaro com aquele bot, não uma fila acionável pela Maria;
- `message_id` de envio prova entrega Telegram, mas não prova que o agente leu, raciocinou ou respondeu.

Regra operacional: para pedir resposta real de outro agente, use `ivs-agent-message` + o watcher `ivs_inbox_watcher.py` do perfil. O watcher lê mensagens novas, aciona o perfil do agente, envia resposta no canal visível quando cadastrado e responde à Maria pelo barramento.
