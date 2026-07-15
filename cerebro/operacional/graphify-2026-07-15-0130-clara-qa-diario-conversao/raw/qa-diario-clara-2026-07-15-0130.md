# QA diário Clara — conversão/agendamento — 2026-07-15 01:30 UTC

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
- Taxa aproximada de vitória por lead único: 6.77%
- Taxa aproximada de queda por lead único: 1.13%
- Aprendizado qualitativo disponível: sim, com quatro padrões operacionais sanitizados.

## Leitura de sinais

- Agendamento/vitória: sem sinais na janela current; histórico mantém 30 sinais agregados de vitória.
- Objeção/queda: sem sinais na janela current; histórico mantém 5 quedas agregadas.
- Silêncio: a janela current sem mensagens indica ausência de amostra recente; não autoriza concluir falha de atendimento nem pausar Clara.
- Padrão de conversão observado no histórico: vitórias tendem a ocorrer quando a conversa é objetiva, com proposta direta de horário ou confirmação simples.
- Padrão de risco observado no histórico: explicação precoce sobre consulta, tratamento ou exames antes de fechar data aumenta fricção e pode esfriar o lead.

## Três melhorias práticas seguras

1. **Confirmação de agenda com resposta curta**  
   Para consultas, aplicações ou retornos já marcados, usar uma confirmação enxuta: nome, serviço, dia/hora, local e até três respostas curtas em negrito: *Confirmo*, *Quero remarcar*, *Não vou conseguir*. Sem explicar procedimento no lembrete.

2. **Lead quente recebe horário, não aula**  
   Quando o lead já demonstrou intenção de agendar/remarcar, Clara deve propor diretamente uma data e horário. Explicações sobre tratamento, benefícios, exames ou preparo só entram se o lead perguntar ou depois de aceitar a data.

3. **Triagem de origem antes de conduzir o próximo passo**  
   No primeiro contato, separar mensagem genérica de interesse institucional de conversa sobre treino/personal. Lead genérico deve ser direcionado por serviço de interesse; contexto de treino deve manter a oferta de visita/avaliação de treino, sem migrar automaticamente para consulta médica ou aplicação.

## Risco operacional

- **Risco de atendimento:** baixo pelos dados disponíveis; não há sinal de queda current nem incidente sensível.
- **Risco de observabilidade:** moderado/baixo. A janela current veio zerada, mas o histórico está íntegro e trouxe aprendizado qualitativo. Se o current continuar zerado em ciclos com expediente ativo, revisar pipeline.
- **Intervenção humana indicada:** não para atendimento. Apenas monitoramento técnico no próximo ciclo se o current permanecer sem amostra.
- **Gate Clara:** não pausar Clara sem ordem direta do Tiaro.

## Classificação do aprendizado

- Classificação: **aplicar amanhã** nos fluxos de confirmação e lead quente; **testar 3 dias** na triagem por origem.
- Natureza: aprendizado operacional de conversão, não regra clínica nova.
- Persistência: registro sanitizado via Graphify/RC-25 para rastreabilidade diária.
