# QA diário Clara — conversão/agendamento — 2026-07-01 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, gerado em 2026-07-01 01:15 UTC, com 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 sinais de vitória/agendamento e 0 sinais de queda/objeção.
- Relatório histórico disponível: últimos 180 dias, arquivo de 2026-06-29 12:38 UTC, com 6187 mensagens, 443 leads únicos, 3275 inbound, 2912 outbound, 30 sinais de vitória/agendamento e 5 sinais de queda/objeção.
- Taxa histórica aproximada: 30 vitórias em 443 leads únicos, cerca de 6,8% de sinal de agendamento sobre conversas únicas; 5 quedas, cerca de 1,1%.
- O campo de aprendizados do relatório current informa `SEM_APRENDIZADOS_NOVOS - sem mensagens no período`.
- O campo de aprendizados do relatório histórico informa `SEM_APRENDIZADOS_NOVOS - falha na extração`.

## Sinais de agendamento, objeção e silêncio
- Agendamento: a amostra recente não permite auditar conversa real; o histórico segue indicando que a Clara precisa transformar intenção em horário concreto e confirmação objetiva.
- Objeção: sem extração conversacional nova, não há objeção específica recente para classificar; manter foco em evitar venda direta antes de qualificar prontidão e dor real.
- Silêncio: o maior sinal operacional do dia é observabilidade, não comportamento do lead: current zerado e histórico com falha de extração impedem leitura confiável do período recente.

## Melhorias práticas para Clara
1. **Pergunta de prontidão antes de explicar demais:** quando o lead pedir informações genéricas, perguntar se busca atendimento agora ou se está pesquisando para decidir, antes de enviar explicações longas.
2. **Oferta de agenda com duas opções fechadas:** quando houver mínima intenção, substituir pergunta aberta por duas opções objetivas de horário/dia, mantendo tom premium e sem pressão.
3. **Confirmação com resposta literal:** ao encaminhar confirmação, usar opções padronizadas `Confirmo`, `Quero remarcar` ou `Não vou conseguir`, para reduzir silêncio e facilitar triagem.

## Aprendizado operacional novo
Aprendizado novo do dia é de observabilidade: o pipeline atual não entregou amostra conversacional recente e o histórico retornou falha de extração. Portanto, a QA deve classificar qualquer recomendação conversacional como reforço de regra canônica, não como conclusão nova baseada no período.

## Risco operacional
Há risco operacional técnico que exige intervenção humana/técnica, mas não pausa da Clara: sem amostra current e com extração histórica falha, a gestão perde capacidade de QA diária real. Validar captura da planilha de conversas, Z-API/bridge, cron de extração e parser de aprendizados. Sem ordem direta do Tiaro, Clara não deve ser pausada.

## Guardrails
Nenhuma melhoria autoriza diagnóstico, prescrição, promessa de resultado, pressão comercial agressiva ou atendimento clínico. O foco é reduzir atrito de agenda, melhorar triagem segura e encaminhar demandas clínicas à equipe certa.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3 como reforço operacional seguro.
- Testar 3 dias: medir taxa de resposta após oferta fechada de horários e confirmação literal quando o pipeline voltar a capturar mensagens.
- Intervenção humana: validar pipeline current/historical do WhatsApp e parser de aprendizados.
