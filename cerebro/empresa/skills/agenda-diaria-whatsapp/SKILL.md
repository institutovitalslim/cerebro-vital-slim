---
name: agenda-diaria-whatsapp
description: >
  Envia a agenda diária de atendimentos do Instituto Vital Slim por WhatsApp via Z-API.
  Consulta agendamentos no QuarkClinic, formata por turno e dispara para os destinatários.
  Use quando: "agenda do dia", "enviar agenda", "agenda diária", "agenda whatsapp",
  "manda a agenda", "disparar agenda", "agenda de atendimentos", "agenda de hoje".
  Cron configurado: todos os dias às 06:00 (America/Sao_Paulo).
metadata:
  version: 1.0.0
  domain: operacional
  owner: main
---

# Agenda Diária WhatsApp — Skill de Envio Automático

## O que é

Consulta a agenda de atendimentos do dia no QuarkClinic e envia por WhatsApp via Z-API para a equipe da clínica.

## Cron Configurado

| Campo | Valor |
|-------|-------|
| **Nome** | agenda-diaria-whatsapp |
| **Horário** | 06:00 (America/Sao_Paulo) |
| **Frequência** | Todos os dias |
| **ID** | 2ba465d4-3dd0-435b-bb12-1576ed6c0403 |

## Destinatários

| Nome | Número | Função |
|------|--------|--------|
| Tiaro | 5571986968887 | Sócio-administrador |
| Dra. Daniely | 5571996962059 | Médica responsável |
| Liane | 5571991574827 | Enfermagem |

## Protocolo de Execução

### Passo 1 — Consultar agenda do dia no QuarkClinic

```bash
python3 /root/.openclaw/workspace/skills/quarkclinic-api/scripts/quarkclinic_api.py GET /v1/agendamentos --query data_agendamento_inicio=DD-MM-AAAA --query data_agendamento_fim=DD-MM-AAAA
```

Caminho alternativo (se o primeiro não existir):
```bash
python3 /root/.openclaw/workspace/snapshot/openclaw-home/workspace/skills/quarkclinic-api/scripts/quarkclinic_api.py GET /v1/agendamentos --query data_agendamento_inicio=DD-MM-AAAA --query data_agendamento_fim=DD-MM-AAAA
```

> Substituir DD-MM-AAAA pela data de hoje.

### Passo 2 — Formatar a mensagem

Separar por turno:
- **Manhã** (antes das 12h)
- **Tarde** (12h às 18h)
- **Noite** (após 18h)

Cada linha:
```
HH:MM — Nome do Paciente — Procedimento — Convênio
```

Ao final, incluir resumo:
```
Resumo:
- Manhã: X atendimento(s)
- Tarde: X atendimento(s)
- Noite: X atendimento(s)
- Total do dia: X atendimento(s)
```

Iniciar com: "Bom dia! Agenda de atendimentos de hoje:"
Se não houver atendimentos: "Bom dia! Não há atendimentos agendados para hoje."

### Passo 3 — Enviar via Z-API

Para **CADA** destinatário, executar via exec:

```bash
curl -s -X POST "https://api.z-api.io/instances/3CF367BB00EB205F87468A74AFBCE7F1/token/C26CFC41175FD987513C3202/send-text" \
  -H "Content-Type: application/json" \
  -H "Client-Token: F277815dcf4e94be7bc2861e8ae9fc369S" \
  -d '{"phone": "NUMERO", "message": "TEXTO_DA_AGENDA"}'
```

## Regras

1. **SOMENTE usar curl via exec** para enviar pelo Z-API. NÃO usar o canal whatsapp do OpenClaw.
2. **Escapar aspas e caracteres especiais** no JSON do curl.
3. **Confirmar envio** verificando se o retorno do curl contém "messageId".
4. **Não enviar mensagem vazia** — sempre verificar se o texto foi gerado antes de disparar.
5. **Um curl por destinatário** — enviar individualmente, não em grupo.

## Z-API — Dados da Instância

| Campo | Valor |
|-------|-------|
| **Instance ID** | 3CF367BB00EB205F87468A74AFBCE7F1 |
| **Token** | C26CFC41175FD987513C3202 |
| **Client Token** | F277815dcf4e94be7bc2861e8ae9fc369S |
| **Número conectado** | 7138388708 |
| **Base URL** | https://api.z-api.io/instances/3CF367BB00EB205F87468A74AFBCE7F1/token/C26CFC41175FD987513C3202 |

## Execução manual

```bash
# Rodar via cron do OpenClaw
openclaw cron run 2ba465d4-3dd0-435b-bb12-1576ed6c0403

# Ou via agente
openclaw agent --agent main --session-id agenda-manual -m "Envie a agenda de hoje por WhatsApp seguindo a skill agenda-diaria-whatsapp"
```

## Troubleshooting

- **"Outbound not configured for channel: whatsapp"**: ignorar — é erro do anúncio no Telegram, não do envio. O envio via Z-API funciona independentemente.
- **Mensagem não chega**: verificar se o número está correto (formato 55DDNNNNNNNNN). Testar com curl direto.
- **Script QuarkClinic não encontrado**: usar o caminho alternativo em `/root/.openclaw/workspace/snapshot/`.
- **Z-API desconectada**: verificar status em `curl -s 'https://api.z-api.io/instances/.../status'`. Se desconectado, escanear QR code novamente.
- **Erro de encoding**: caracteres especiais no nome do paciente podem quebrar o JSON do curl. Usar aspas duplas e escapar com backslash.

## Empresa

- **Instituto Vital Slim**
- **CNPJ**: 40.289.526/0001-58
- **Sistema de agenda**: QuarkClinic (api.quark.tec.br)
