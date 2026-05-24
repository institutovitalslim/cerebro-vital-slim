# QA diária Clara — máquina de agendamento — 2026-05-24 01:30 UTC

Fonte analisada: relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` de `/root/.openclaw/reports/clara-learning/`.

## Leitura objetiva

- Janela atual: últimas 6h, 6 mensagens, 4 leads únicos, 6 entradas, 0 saídas, 0 vitórias, 0 quedas. Volume insuficiente para aprendizado novo.
- Histórico: 180 dias, 5.373 mensagens, 344 leads únicos, 26 vitórias, 5 quedas.
- Sinais de agendamento: confirmações funcionam melhor quando a Clara fecha com opções literais e limitadas de resposta; proposta concreta de dia/horário performa melhor que pergunta aberta.
- Sinais de objeção/queda: explicação longa antes do compromisso, pergunta ampla de abertura e pedido de prazo para exames tendem a gerar adiamento ou recusa.
- Sinais de silêncio: quando o próximo passo fica dependente do lead avisar depois, o funil perde tração.

## 3 melhorias práticas para aumentar agendamentos

1. **Trocar abertura genérica por avanço dirigido.** Não abrir com “como posso ajudar?”. Usar pergunta de avanço com duas opções reais: agenda ou valor/condição, conforme contexto do lead.
2. **Evitar pitch longo antes de data/horário.** Se o lead não pediu detalhes, Clara deve propor horário primeiro e só explicar o necessário quando houver objeção explícita.
3. **Remover dependência de “me avise quando fizer”.** Em exames, documentos ou imprevistos, oferecer duas opções concretas de agenda/remarcação e manter o compromisso vivo.

## Risco operacional

- **Sem risco crítico imediato**: não há evidência, na janela atual, de falha sistêmica, atendimento indevido ou necessidade de pausar Clara.
- **Risco operacional baixo/moderado**: volume atual sem respostas outbound e sem wins pode indicar janela fria ou coleta insuficiente; acompanhar no próximo ciclo antes de intervenção humana.

## Graphify / RC-25

- Não houve aprendizado operacional novo na janela atual.
- Os padrões do histórico já constam no cérebro/Graphify em ciclos anteriores e no corpus `clara-learning-graphify/2026-05-24`.
- Nenhuma regra canônica nova foi criada neste QA para evitar duplicação.
