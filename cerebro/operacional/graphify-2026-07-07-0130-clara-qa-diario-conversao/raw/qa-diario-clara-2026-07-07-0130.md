# QA diário Clara — conversão/agendamento — 2026-07-07 01:30 UTC

## Escopo
QA objetiva da Clara como máquina de agendamento, com base nos relatórios sanitizados mais recentes:

- `/root/.openclaw/reports/clara-learning/latest-whatsapp-current.json`
- `/root/.openclaw/reports/clara-learning/latest-whatsapp-historical.json`

Sem exposição de PII, telefones ou conversas sensíveis.

## Evidência lida

### Janela current — últimas 6h
- Mensagens analisadas: 0
- Leads/conversas únicas: 0
- Recebidas: 0
- Enviadas: 0
- Sinais de agendamento/vitória: 0
- Sinais de queda/objeção: 0
- Aprendizado reportado: `SEM_APRENDIZADOS_NOVOS - sem mensagens no período`

### Janela historical — últimos 180 dias
- Mensagens analisadas: 6187
- Leads/conversas únicas: 443
- Recebidas: 3275
- Enviadas: 2912
- Sinais de agendamento/vitória: 30
- Sinais de queda/objeção: 5
- Taxa aproximada de vitória por lead único: 6,77%
- Taxa aproximada de queda por lead único: 1,13%
- Aprendizado reportado: `SEM_APRENDIZADOS_NOVOS - falha na extração`

## Leitura de sinais

- Agendamento/vitória: sem sinais na janela current; histórico mantém 30 sinais agregados.
- Objeção/queda: sem sinais na janela current; histórico mantém 5 quedas agregadas.
- Silêncio: a janela current sem mensagens indica ausência de amostra operacional recente, não prova falha de atendimento.
- Observabilidade: a extração qualitativa histórica falhou; portanto, não há base segura para afirmar padrões específicos de objeção, timing ou linguagem a partir do relatório de hoje.

## Três melhorias práticas seguras

1. **Convite de agenda mais objetivo após sinal de interesse**  
   Quando o lead demonstrar intenção ou encaixe, a Clara deve reduzir rodeio e oferecer duas opções simples de avanço: avaliação inicial ou melhor horário para contato. Sem prometer resultado clínico.

2. **Resposta-pivô para objeção sem debate clínico**  
   Ao aparecer objeção de preço, medo, tempo ou dúvida sobre tratamento, acolher em uma frase, reforçar que a avaliação individual é o lugar certo para entender o caso e retomar o próximo passo de agenda. Não diagnosticar, prescrever ou garantir desfecho.

3. **Follow-up curto para silêncio**  
   Se o lead não responde após uma pergunta operacional, usar um lembrete breve, premium e com baixa fricção: confirmar se deseja ajuda para encontrar o melhor horário ou se prefere receber orientação de próximos passos. Evitar sequência longa ou pressão.

## Risco operacional

- **Risco principal:** técnico/observabilidade. A janela current não trouxe amostra e o histórico segue com falha de extração qualitativa; isso limita a QA de conversão.
- **Intervenção humana indicada:** sim, mas técnica/leve — revisar pipeline de extração qualitativa do learning report se a falha persistir no próximo ciclo.
- **Intervenção em atendimento:** não indicada pelos dados atuais.
- **Gate Clara:** não pausar Clara sem ordem direta do Tiaro.

## Classificação do aprendizado

- Classificação: **testar 3 dias**
- Natureza: reforço operacional seguro, não regra clínica nova.
- Persistência: registro sanitizado via Graphify/RC-25 para rastreabilidade diária.
