# QA diário Clara — conversão/agendamento — 2026-07-02 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, gerado em 2026-07-02 01:15 UTC, com 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 sinais de vitória/agendamento e 0 sinais de queda/objeção.
- Relatório histórico disponível: últimos 180 dias, arquivo de 2026-06-29 12:38 UTC, com 6187 mensagens, 443 leads únicos, 3275 inbound, 2912 outbound, 30 sinais de vitória/agendamento e 5 sinais de queda/objeção.
- Taxa histórica aproximada: 30 vitórias em 443 leads únicos, cerca de 6,8% de sinal de agendamento sobre conversas únicas; 5 quedas, cerca de 1,1%.
- O campo de aprendizados do relatório current informa `SEM_APRENDIZADOS_NOVOS - sem mensagens no período`.
- O campo de aprendizados do relatório histórico informa `SEM_APRENDIZADOS_NOVOS - falha na extração`.
- Sinal persistente: a limitação de observabilidade já aparecia na QA de 2026-07-01; portanto, a falha deixou de ser pontual e deve ser tratada como bloqueio técnico de QA, sem pausar a Clara.

## Sinais de agendamento, objeção e silêncio
- Agendamento: não houve amostra recente para auditar convite, confirmação ou fechamento de horário. O histórico mantém 30 sinais agregados de vitória, mas sem extração qualitativa confiável.
- Objeção: não há objeção recente classificável; o histórico registra 5 sinais agregados de queda/objeção, sem detalhe acionável.
- Silêncio: o principal sinal operacional do dia é ausência de dados no current e falha de extração no histórico, impedindo distinguir silêncio real de leads versus falha de captura/análise.

## Melhorias práticas para Clara
1. **Transformar intenção mínima em próxima ação de agenda:** quando o lead demonstrar interesse, evitar explicação longa e oferecer dois caminhos objetivos: agendar avaliação ou tirar uma dúvida curta antes de agendar.
2. **Usar oferta fechada de horários sem pressão:** substituir pergunta aberta por duas opções concretas de agenda quando houver prontidão, mantendo linguagem premium e sem prometer resultado.
3. **Follow-up de silêncio com escolha simples:** após ausência de resposta, retomar com uma pergunta de baixa fricção — `quer que eu veja um horário para você ou prefere receber primeiro as informações gerais?` — sem insistência agressiva.

## Aprendizado operacional novo
Aprendizado novo do dia é a persistência do problema de observabilidade: por pelo menos dois ciclos consecutivos de QA diária, o current veio sem mensagens e o histórico manteve falha de extração. Isso não prova falha de atendimento da Clara, mas prova que a gestão está sem amostra confiável para QA conversacional.

## Risco operacional
Há risco operacional técnico que exige intervenção humana/técnica: revisar captura da planilha de conversas, Z-API/bridge, cron de extração e parser de aprendizados. Não há evidência suficiente para intervenção humana em conversas específicas e não há autorização para pausar a Clara.

## Guardrails
Nenhuma melhoria autoriza diagnóstico, prescrição, promessa de resultado, pressão comercial agressiva ou atendimento clínico. O foco é reduzir atrito de agenda, melhorar triagem segura e encaminhar demandas clínicas à equipe certa.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3 como reforço operacional seguro.
- Testar 3 dias: medir taxa de resposta após oferta fechada e follow-up de escolha simples quando o pipeline voltar a capturar conversas.
- Intervenção humana: abrir verificação técnica do pipeline current/historical e parser, pois a falha é persistente.
