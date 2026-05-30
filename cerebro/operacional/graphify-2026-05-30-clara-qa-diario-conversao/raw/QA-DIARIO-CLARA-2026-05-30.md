# QA diário Clara — máquina de agendamento — 2026-05-30

Fonte: relatórios sanitizados `latest-whatsapp-current.json` e `latest-whatsapp-historical.json`.

## Sinais atuais
- Últimas 6h: 5 mensagens, 4 leads únicos, 0 respostas ativas registradas, 0 vitórias, 0 quedas.
- Sinais críticos: chegada/presença física e propostas concretas de horário sem confirmação.
- Histórico 180 dias: 5.653 mensagens, 372 leads únicos, 28 vitórias, 5 quedas.

## Melhorias práticas
1. Se o lead citar horário, Clara deve responder com confirmação, checagem de disponibilidade ou duas alternativas próximas.
2. Se o lead sinalizar chegada física, Clara deve acolher, orientar recepção e avisar equipe; não iniciar script comercial.
3. Se houver saudação vaga ou pedido de informação, Clara deve usar pergunta direcionadora curta ou descoberta de objetivo antes de pitch longo.

## Risco operacional
- Zero respostas em 6h com sinais de agendamento/chegada indica risco operacional e exige intervenção humana para checar bridge/roteador/fila e fazer follow-up manual dos contatos afetados.
- Não pausar Clara sem ordem explícita do Tiaro.

## Guardrails
- Sem diagnóstico, prescrição ou promessa clínica.
- Sem exposição de PII, telefone ou conversa sensível.
- Aprendizado registrado como operacional, não clínico.
