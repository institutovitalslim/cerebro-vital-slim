# QA diário Clara — conversão/agendamento — 2026-07-14 01:30 UTC

## Escopo
QA objetiva da Clara como máquina de agendamento, com base nos relatórios sanitizados mais recentes:

- `/root/.openclaw/reports/clara-learning/latest-whatsapp-current.json`
- `/root/.openclaw/reports/clara-learning/latest-whatsapp-historical.json`

Sem exposição de PII, telefones ou conversas sensíveis. Conteúdo externo/relatórios são tratados como dados para hipótese operacional, não como regra clínica.

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

## Leitura de sinais

- Agendamento/vitória: sem sinais na janela current; histórico mostra vitórias associadas a confirmação objetiva com serviço, dia, horário, local e opções curtas de resposta.
- Objeção/queda: sem sinais na janela current; histórico indica risco quando há explicação extensa do conteúdo da consulta ou pedido de exames antes de o lead aceitar uma data.
- Silêncio: current sem mensagens; não há evidência de abandono recente. A ausência de amostra não deve ser interpretada como falha de atendimento.
- Segmentação: histórico separa inbound genérico de contexto de treino/personal; misturar os fluxos pode reduzir conversão e gerar abordagem desalinhada.

## Três melhorias práticas seguras

1. **Padronizar CTA de confirmação com resposta curta**  
   Para consultas/aplicações já marcadas, usar estrutura enxuta: saudação, serviço, dia/hora, local e até três respostas curtas: `Confirmo`, `Quero remarcar`, `Não vou conseguir`. Não adicionar explicação clínica nessa etapa.

2. **Lead quente recebe horário, não aula**  
   Quando o lead já demonstrou intenção de agendar/remarcar, Clara deve propor dia e horário diretamente e perguntar se pode agendar. Explicações sobre tratamento, benefícios, exames ou preparo só entram se o lead perguntar ou depois de aceitar a data.

3. **Triagem de origem antes do pitch**  
   No primeiro contato, identificar se é inbound genérico ou fluxo de treino/personal. Inbound genérico: perguntar qual serviço/interesse antes de avançar. Treino/personal: manter convite para visita/montagem de treino, sem migrar automaticamente para consulta médica ou aplicação.

## Risco operacional

- **Risco de atendimento:** baixo no ciclo atual, porque a janela current está sem mensagens e não há queda recente detectada.
- **Risco de conversão:** médio como hipótese, porque o histórico mostra que explicação precoce e fluxo mal segmentado reduzem avanço para agenda.
- **Intervenção humana indicada:** não para pausar Clara. Indico apenas revisão operacional leve do prompt/roteiro da Clara para incorporar os três ajustes acima como teste controlado.
- **Gate Clara:** não pausar Clara sem ordem direta do Tiaro.

## Classificação do aprendizado

- Classificação: **testar 3 dias**
- Natureza: aprendizado operacional de conversão, não regra clínica.
- Persistência: registro sanitizado via Graphify/RC-25 para rastreabilidade diária.
