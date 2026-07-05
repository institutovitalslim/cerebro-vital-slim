# QA diário Clara — conversão/agendamento — 2026-07-05 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, gerado em 2026-07-05 01:15 UTC, com 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 sinais de vitória/agendamento e 0 sinais de queda/objeção.
- Relatório histórico disponível: últimos 180 dias, arquivo de 2026-06-29 12:38 UTC, com 6187 mensagens, 443 leads únicos, 3275 inbound, 2912 outbound, 30 sinais de vitória/agendamento e 5 sinais de queda/objeção.
- Taxa histórica aproximada: 30 vitórias em 443 leads únicos, cerca de 6,8% de sinal de agendamento sobre conversas únicas; 5 quedas, cerca de 1,1%.
- O campo de aprendizados do relatório current informa `SEM_APRENDIZADOS_NOVOS - sem mensagens no período`.
- O campo de aprendizados do relatório histórico informa `SEM_APRENDIZADOS_NOVOS - falha na extração`.
- Sinal persistente: a combinação de current sem amostra e histórico sem extração qualitativa segue presente após os registros anteriores de 2026-07-01, 2026-07-02 e 2026-07-03. O histórico também está sem atualização desde 2026-06-29.

## Sinais de agendamento, objeção e silêncio
- Agendamento: não houve amostra recente para auditar convite, confirmação ou fechamento de horário. O histórico mantém 30 sinais agregados de vitória, mas sem extração qualitativa confiável.
- Objeção: não há objeção recente classificável; o histórico registra 5 sinais agregados de queda/objeção, sem detalhe acionável.
- Silêncio: o principal sinal operacional é ausência de dados atuais. Não é seguro concluir ausência real de demanda; pode ser silêncio real, período sem mensagens ou falha de captura/análise.

## Melhorias práticas para Clara
1. **Microfechamento antes de explicar demais:** quando houver interesse mínimo, conduzir para o próximo passo de agenda com baixa fricção: perguntar se pode verificar os melhores horários para avaliação inicial antes de alongar explicações.
2. **Resposta de objeção com dupla rota segura:** diante de preço, dúvida ampla ou “vou pensar”, oferecer dois caminhos sem promessa clínica: informação geral objetiva ou avaliação para entender o caso com a equipe.
3. **Follow-up binário de silêncio:** quando o lead parar, retomar com alternativa simples: receber informações gerais ou verificar horário para avaliação. Evitar pressão, urgência artificial ou promessa de resultado.

## Aprendizado operacional novo
A persistência do current zerado somada ao histórico desatualizado desde 2026-06-29 e com falha de extração impede QA qualitativa confiável da Clara por vários ciclos. O aprendizado operacional é tratar o pipeline de observabilidade como item de manutenção técnica recorrente até normalizar: sem dados recentes, a gestão deve classificar recomendações de conversão como reforços seguros, não como conclusão sobre performance real.

## Risco operacional
Há risco operacional técnico que exige intervenção humana/técnica: revisar captura da planilha de conversas, Z-API/bridge, cron de extração, atualização do histórico e parser de aprendizados. Não há evidência suficiente para intervenção humana em conversas específicas e não há autorização para pausar a Clara.

## Guardrails
Nenhuma melhoria autoriza diagnóstico, prescrição, promessa de resultado, pressão comercial agressiva ou atendimento clínico. O foco é reduzir atrito de agenda, melhorar triagem segura e encaminhar demandas clínicas à equipe certa.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3 como reforço operacional seguro.
- Testar 3 dias: medir taxa de resposta após microcompromisso, rota dupla e follow-up binário quando o pipeline voltar a capturar conversas.
- Intervenção humana: abrir verificação técnica do pipeline current/historical e parser, pois a falha é persistente e o histórico está desatualizado.
