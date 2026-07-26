# QA diário Clara — conversão/agendamento — 2026-07-26 01:30 UTC

## Escopo
QA objetiva da Clara como máquina de agendamento, a partir dos relatórios sanitizados mais recentes:

- `/root/.openclaw/reports/clara-learning/latest-whatsapp-current.json`
- `/root/.openclaw/reports/clara-learning/latest-whatsapp-historical.json`

Não contém PII, telefones nem transcrição sensível.

## Evidência lida

### Janela current — últimas 6h
- Mensagens analisadas: 0
- Leads/conversas únicas: 0
- Recebidas: 0
- Enviadas: 0
- Sinais de agendamento/vitória: 0
- Sinais de queda/objeção: 0
- Aprendizado reportado: `SEM_APRENDIZADOS_NOVOS - sem mensagens no período`
- Relatório canônico lido: `/root/cerebro-vital-slim/cerebro/logs/clara-whatsapp-learning/20260726-011525-whatsapp-current.md`

### Janela historical — últimos 180 dias
- Mensagens analisadas: 6187
- Leads/conversas únicas: 443
- Recebidas: 3275
- Enviadas: 2912
- Sinais de agendamento/vitória: 30
- Sinais de queda/objeção: 5
- Taxa aproximada de vitória por lead único: 6,77%
- Taxa aproximada de queda por lead único: 1,13%
- Relatório canônico lido: `/root/cerebro-vital-slim/cerebro/logs/clara-whatsapp-learning/20260720-093053-whatsapp-historical.md`

## Leitura de sinais

- **Agendamento/vitória:** sem sinais recentes na janela current; histórico mantém padrão positivo quando a Clara usa confirmação objetiva e/ou oferece horário específico.
- **Objeção/queda:** sem queda recente na janela current; no histórico, explicação longa antes de medir intenção aparece associada a esfriamento de lead em pesquisa.
- **Silêncio:** current zerado significa ausência de amostra recente. Não autoriza concluir falha da Clara nem pausar o atendimento. Se repetir em ciclos de expediente com tráfego ativo, revisar observabilidade/pipeline.
- **Mensagem repetida:** histórico indica que repetição pelo lead sinaliza atraso percebido e deve subir prioridade de resposta.

## Três melhorias práticas seguras

1. **Confirmar agenda com opções fechadas.**  
   Para consultas, aplicações e retornos já marcados, usar confirmação curta com serviço, dia/hora e três respostas exatas: *Confirmo*, *Quero remarcar*, *Não vou conseguir*.

2. **Trocar pergunta aberta por horário concreto.**  
   Quando houver intenção de agendar/remarcar, oferecer 1 ou 2 horários disponíveis. Evitar “qual dia serve?” como primeira condução quando já houver agenda possível.

3. **Medir fase de decisão antes de explicar.**  
   Quando o lead estiver apenas pesquisando, perguntar se quer decidir mais para frente ou agendar ainda nesta semana. Só detalhar consulta/protocolo depois de intenção clara, sem diagnóstico, prescrição ou promessa de resultado.

## Risco operacional

- **Atendimento/compliance:** baixo; não houve amostra recente com violação e as melhorias preservam guardrails clínicos.
- **Conversão:** moderado se houver leads repetindo mensagem sem priorização ou se a Clara explicar demais antes de propor agenda.
- **Observabilidade:** moderado/baixo; current veio zerado. Monitorar próximo ciclo. Se continuar zerado em horário ativo, abrir checagem técnica da fonte WhatsApp/planilha.
- **Intervenção humana imediata:** não indicada para atendimento. Indicada apenas se o pipeline current permanecer zerado com tráfego conhecido.
- **Gate Clara:** não pausar Clara sem ordem direta do Tiaro.

## Classificação do aprendizado

- **Aplicar amanhã:** confirmação objetiva e oferta de horários concretos.
- **Testar 3 dias:** priorização de mensagens repetidas e pergunta de fase de decisão antes da explicação.
- **Persistência:** registro sanitizado via Graphify/RC-25 para rastreabilidade diária. Não há regra clínica nova.
