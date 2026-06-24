# RC-25 — Barramento de comunicação interagentes IVS

Data: 2026-06-24
Responsável: Maria

## Decisão

Tiaro determinou que todos os agentes IVS devem conseguir se comunicar entre si. Foi criado um barramento local governado de mensagens interagentes para Maria, Ana, João, Clara, Pedro, Jarvis, Eduardo, Conselho Growth e LLM Council.

## Implementação canônica

Script:

```bash
/root/cerebro-vital-slim/scripts/ivs_agent_message.py
/usr/local/bin/ivs-agent-message
```

Skill distribuída:

```text
ivs-agent-communications
```

Instalada nos perfis Hermes:

- default/Maria
- ana
- joao
- clara
- pedro
- jarvis
- eduardo

## Uso principal

Enviar mensagem:

```bash
ivs-agent-message send \
  --from ana \
  --to joao \
  --subject "Assunto" \
  --body "Mensagem" \
  --next-action "Próxima ação" \
  --sensitivity marketing \
  --json
```

Ler inbox:

```bash
ivs-agent-message inbox --agent joao --status open --json
```

Atualizar status:

```bash
ivs-agent-message update --id <message_id> --status ack --json
ivs-agent-message update --id <message_id> --status done --json
```

## Governança

- Não envia WhatsApp.
- Não publica externamente.
- Não fala com paciente/lead.
- Não executa financeiro.
- Telefones, CPF e e-mails são redigidos automaticamente.
- Ação sensível continua exigindo autorização explícita do Tiaro.
- O barramento registra eventos locais em JSONL.

## Armazenamento

Banco local:

```text
/root/.openclaw/workspace/ops/ivs_agent_layer/inter_agent_messages.db
```

Eventos:

```text
/root/.openclaw/workspace/ops/ivs_agent_layer/inter_agent_messages.jsonl
```

## Validação realizada

Teste Ana → João:

```text
from = ana-medica-cientifica
to = agente-reels-intel
status = open
inbox João = mensagem visível
```

Teste de redaction:

```text
71999999999 → [telefone-redigido]
teste@example.com → [email-redigido]
```

## Observação operacional

O barramento resolve o problema da Ana não conseguir enviar mensagem ao João por depender de canal Telegram/DM. A partir de agora, comunicação entre agentes é local, auditável, redigida e independente de tópico do Telegram.
