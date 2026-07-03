# QA diário Clara — conversão/agendamento — 2026-07-03 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, gerado em 2026-07-03 01:15 UTC, com 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 sinais de vitória/agendamento e 0 sinais de queda/objeção.
- Relatório histórico disponível: últimos 180 dias, arquivo de 2026-06-29 12:38 UTC, com 6187 mensagens, 443 leads únicos, 3275 inbound, 2912 outbound, 30 sinais de vitória/agendamento e 5 sinais de queda/objeção.
- Taxa histórica aproximada: 30 vitórias em 443 leads únicos, cerca de 6,8% de sinal de agendamento sobre conversas únicas; 5 quedas, cerca de 1,1%.
- O campo de aprendizados do relatório current informa `SEM_APRENDIZADOS_NOVOS - sem mensagens no período`.
- O campo de aprendizados do relatório histórico informa `SEM_APRENDIZADOS_NOVOS - falha na extração`.
- Sinal persistente: a limitação de observabilidade já apareceu nas QAs de 2026-07-01 e 2026-07-02; portanto, este é pelo menos o terceiro ciclo consecutivo em que a QA não tem amostra qualitativa confiável.

## Sinais de agendamento, objeção e silêncio
- Agendamento: não houve amostra recente para auditar convite, confirmação ou fechamento de horário. O histórico mantém 30 sinais agregados de vitória, mas sem extração qualitativa confiável.
- Objeção: não há objeção recente classificável; o histórico registra 5 sinais agregados de queda/objeção, sem detalhe acionável.
- Silêncio: o principal sinal operacional do dia é ausência de dados no current e falha de extração no histórico, impedindo distinguir silêncio real de leads versus falha de captura/análise.

## Melhorias práticas para Clara
1. **Fechamento com microcompromisso:** quando houver interesse mínimo, conduzir para uma decisão pequena e segura: `posso ver os melhores horários para uma avaliação inicial?` antes de abrir explicações longas.
2. **Objeção tratada com escolha controlada:** quando o lead pedir preço, detalhes ou “vou pensar”, responder sem promessa clínica e oferecer dois caminhos: receber informação geral objetiva ou já reservar avaliação para entender o caso com a equipe.
3. **Follow-up de silêncio com alternativa binária:** após ausência de resposta, retomar com baixa fricção: `prefere que eu te envie as informações gerais ou que eu veja um horário para avaliação?` — sem insistência agressiva.

## Aprendizado operacional novo
A persistência por pelo menos três ciclos da combinação `current sem mensagens` + `histórico com falha na extração` eleva o problema de observabilidade de alerta recorrente para bloqueio técnico de QA. Isso não prova falha da Clara no atendimento, mas prova que a gestão não consegue validar conversão, objeções e silêncio com segurança pelos relatórios atuais.

## Risco operacional
Há risco operacional técnico que exige intervenção humana/técnica: revisar captura da planilha de conversas, Z-API/bridge, cron de extração, atualização do histórico e parser de aprendizados. Não há evidência suficiente para intervenção humana em conversas específicas e não há autorização para pausar a Clara.

## Guardrails
Nenhuma melhoria autoriza diagnóstico, prescrição, promessa de resultado, pressão comercial agressiva ou atendimento clínico. O foco é reduzir atrito de agenda, melhorar triagem segura e encaminhar demandas clínicas à equipe certa.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3 como reforço operacional seguro.
- Testar 3 dias: medir taxa de resposta após microcompromisso, oferta controlada e follow-up binário quando o pipeline voltar a capturar conversas.
- Intervenção humana: abrir verificação técnica do pipeline current/historical e parser, pois a falha é persistente por pelo menos três ciclos.
