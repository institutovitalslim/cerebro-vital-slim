# QA diário Clara — conversão/agendamento — 2026-07-17 01:30 UTC

## Escopo
QA objetiva da Clara como máquina de agendamento, com base nos relatórios sanitizados mais recentes:

- `/root/.openclaw/reports/clara-learning/latest-whatsapp-current.json`
- `/root/.openclaw/reports/clara-learning/latest-whatsapp-historical.json`

Sem exposição de PII, telefones ou conversas sensíveis. Conteúdo externo/relatórios são insumo operacional, não regra clínica.

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
- Aprendizados qualitativos sanitizados: CTA padronizado de confirmação; objetividade com leads quentes; risco de explicação precoce; segmentação por origem inbound versus treino.

## Leitura de sinais

- **Agendamento/vitória:** sem sinais na janela current; histórico aponta 30 vitórias, concentradas em confirmação objetiva, proposta direta de horário e comandos curtos de resposta.
- **Objeção/queda:** sem sinais na janela current; histórico aponta 5 quedas. O padrão de risco é explicar demais a consulta/tratamento ou pedir exames antes de o lead aceitar uma data.
- **Silêncio:** current sem mensagens indica ausência de amostra nas últimas 6h, não falha de Clara. Para silêncio, o caminho seguro é follow-up curto com baixa fricção.
- **Segmentação:** origem genérica de anúncio/formulário precisa primeiro descobrir interesse; origem treino/personal deve permanecer no contexto de visita/treino, sem migrar automaticamente para consulta médica.

## Três melhorias práticas seguras

1. **Padronizar confirmação com resposta curta**  
   Para consulta/aplicação já marcada: nome + serviço + dia/hora + local + três opções objetivas de resposta: *Confirmo*, *Quero remarcar*, *Não vou conseguir*. Não adicionar explicação de procedimento nesse momento.

2. **Fechar data antes de educar**  
   Em lead quente ou remarcação, Clara deve propor horário direto e só explicar detalhes se o lead perguntar. Ordem operacional: interesse → data/horário → logística/preparo. Evitar pedir exames antes de compromisso de data.

3. **Classificar origem no primeiro turno**  
   Se a entrada for genérica de informações, perguntar qual serviço/interesse antes de oferecer agenda. Se a entrada for treino/personal, manter o convite para visita/treino e não deslocar o lead para consulta médica ou aplicação sem sinal explícito.

## Risco operacional

- **Risco principal:** baixo no atendimento e moderado em conversão se Clara voltar a explicar cedo demais antes de propor data.
- **Intervenção humana indicada:** não há evidência para intervenção humana imediata no atendimento. Recomendo apenas monitorar o próximo ciclo para confirmar se a janela current voltou a ter amostra.
- **Gate Clara:** não pausar Clara sem ordem direta do Tiaro.

## Classificação do aprendizado

- Classificação: **aplicar amanhã** para confirmação objetiva e segmentação de origem; **testar 3 dias** para redução de explicação precoce antes de data.
- Natureza: aprendizado operacional de conversão, não regra clínica.
- Persistência: registro sanitizado via Graphify/RC-25 para rastreabilidade diária.
