# Atendimento — Contexto

> Conteúdo derivado de fatos canônicos: `cerebro/CLAUDE.md` (Protocolo de Dúvida, Atendimento a LEADS no WhatsApp), `cerebro/empresa/contexto/people.md`, `cerebro/leads-argumentos-venda-ligacoes.md`, `areas/atendimento/skills/`.

## Como funciona

**Atendimento da clínica** acontece em três camadas, com handoff explícito:

1. **Clara (digital, primeira linha) — WhatsApp via Z-API**
   - Toda mensagem de paciente/lead chega primeiro nela
   - **Antes de responder qualquer coisa:** consulta a planilha Apps Script de histórico (URL em `cerebro/CLAUDE.md`) pelo número do telefone — para retomar do ponto exato onde a última interação parou, sem repetir perguntas
   - Responde diretamente o que está dentro do escopo público da clínica (informações já documentadas, cumprimentos, dúvidas básicas)
   - Em qualquer dúvida sobre preço, especialidade médica, horário, procedimento clínico, convênio, parceria, evento → **aciona o Protocolo de Dúvida**: acusa recebimento ao lead ("Olá! Obrigada pelo contato 😊 Só um momento, já te retorno"), consulta o Tiaro via Telegram, aguarda orientação, responde com o conteúdo confirmado, salva na memória pra não perguntar de novo
   - Para áudios recebidos: transcreve via Whisper, gera resposta da Clara, e responde **em áudio** via ElevenLabs TTS (voice ID `EXAVITQu4vr4xnSDxMaL`)

2. **Liane Rodrigues (humana, concierge) — presencial e telefone**
   - **Enfermeira e Concierge de Pacientes** (ver `cerebro/empresa/contexto/people.md`)
   - Cuida da experiência e do acolhimento presencial (paciente que chega na clínica)
   - Recebe agendamentos confirmados e prepara recepção
   - WhatsApp interno: `5571991574827`

3. **Tiaro / Dra. Daniely (sócios, decisão)**
   - Tiaro é o canal de escalação default da Clara para dúvidas operacionais
   - Dra. Daniely é o canal de escalação para dúvidas clínicas/médicas
   - Ambos via Telegram (preferencial) ou WhatsApp (fallback)

**Princípios duros de atendimento (de `cerebro/CLAUDE.md`):**
- **NUNCA** dizer "não consegui recuperar o que ficou pendente" / "reenvie sua última mensagem" — trata cada mensagem como válida e completa
- **NUNCA** mencionar erros técnicos ou problemas de sessão ao lead/paciente
- **NUNCA** deixar lead sem resposta
- **SEMPRE** cumprimentar de volta quando o lead cumprimenta
- **SEMPRE** responder em português brasileiro

## Ferramentas

- **WhatsApp via Z-API** — canal único de entrada de paciente (`localhost:8787`)
- **ElevenLabs TTS** — respostas em áudio quando o paciente envia áudio
- **Whisper (OpenAI)** — transcrição de áudio recebido
- **Planilha Apps Script (Google Sheets)** — histórico canônico de conversas por número (URL em `cerebro/CLAUDE.md` seção "Rotina obrigatória")
- **QuarkClinic** — confirmação de agendamento, info da agenda
- **Telegram** — canal interno de escalação Clara → Tiaro / Dra
- **Skills da área** (`areas/atendimento/skills/`):
  - `responder-cliente` — segue tom e padrão da clínica
  - `escalar-duvida` — escala dúvida que não sabe responder pro responsável (Tiaro)
  - `consulta-base-conhecimento` — busca antes de responder
  - `registro-duvida-pendente` — registra dúvida não resolvida pra acompanhamento
  - `relatorio-suporte` — resumo diário de volume, perguntas frequentes, escalações, taxa de resolução
  > ⚠️ **Pendência:** o `_index.md` desta área menciona "workspace da Amora" e "Bruno" — nomes que não pertencem ao IVS, provavelmente leftover do template OpenClaw. Precisa revisão.

## Principais desafios

1. **Cobertura 24/7 sem perder qualidade** — paciente decide quando decide (final de semana, noite, feriado). Clara responde sempre, mas escalação humana fora do horário comercial ainda é gargalo.
2. **Compliance médico (CFM/CRM-BA)** — antes/depois, promessas de resultado e depoimentos têm restrições. Toda resposta envolvendo informação clínica precisa estar dentro do que está documentado/aprovado — na dúvida, escalar.
3. **Não cair em sessão perdida com lead recorrente** — risco recorrente: tratar nova mensagem de lead conhecido como contato novo, perdendo histórico. Por isso a consulta à planilha de histórico é **obrigatória antes de qualquer resposta**.
4. **Loop fechado entre atendimento e vendas** — informações que aparecem no atendimento (objeção real, dor não verbalizada, padrão de hesitação) precisam alimentar o processo de vendas. Hoje esse loop depende de relatos manuais.

_Atualizado: 2026-04-23_
