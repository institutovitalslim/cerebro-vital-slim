# QA diário Clara — conversão/agendamento — 2026-07-23 01:30 UTC

## Escopo
QA objetiva da Clara como máquina de agendamento, a partir dos relatórios sanitizados mais recentes:
- `/root/.openclaw/reports/clara-learning/latest-whatsapp-current.json`
- `/root/.openclaw/reports/clara-learning/latest-whatsapp-historical.json`

Não contém PII, telefones nem transcrição sensível.

## Métricas lidas

### Janela current — últimas 6h
- Mensagens: 0
- Leads/conversas únicas: 0
- Inbound/outbound: 0 / 0
- Sinais de agendamento/vitória: 0
- Sinais de queda/objeção: 0
- Aprendizado reportado: sem mensagens no período.
- Resultado: sem amostra recente; não há base para concluir falha operacional da Clara.

### Janela histórica — últimos 180 dias
- Mensagens: 6187
- Leads/conversas únicas: 443
- Inbound/outbound: 3275 / 2912
- Sinais de agendamento/vitória: 30
- Sinais de queda/objeção: 5
- Taxa aproximada de vitória por lead único: 6,77%
- Taxa aproximada de queda por lead único: 1,13%

## Sinais operacionais
- Agendamento: confirmações objetivas, com serviço, data/horário e opções curtas de resposta, reduzem fricção e aumentam confirmação.
- Objeção: explicação detalhada de protocolo, consulta ou tratamento antes de entender fase de decisão pode esfriar leads em pesquisa.
- Silêncio: mensagens repetidas pelo mesmo lead indicam atraso percebido e risco de perda de temperatura; devem virar fila prioritária.
- Observabilidade: current zerado no período noturno não indica incidente isoladamente; revisar pipeline apenas se repetir em ciclos com expediente ativo.

## Três melhorias práticas
1. Manter confirmação de agenda em formato curto: serviço, dia/horário, local e três opções de resposta — `Confirmo`, `Quero remarcar`, `Não vou conseguir`.
2. Para lead quente, propor 1 ou 2 horários concretos antes de qualquer explicação longa; para lead em pesquisa, perguntar fase de decisão antes de detalhar.
3. Criar prioridade operacional para mensagem repetida: reconhecer o atraso percebido e conduzir imediatamente para próximo passo de agenda.

## Guardrails
- Não diagnosticar, prescrever ou prometer resultado.
- Não transformar aprendizado operacional em regra clínica.
- Não pedir exames como barreira antes de propor agenda, salvo fluxo validado pela equipe.
- Não pausar Clara sem ordem direta do Tiaro.

## Classificação do aprendizado
- Aprendizado novo nesta rodada: não identificado.
- Reforço operacional: aplicar amanhã confirmação objetiva e oferta de horários concretos; manter teste de 3 dias para prioridade de mensagens repetidas.

## Risco operacional
Baixo para atendimento/compliance. Moderado/baixo para conversão se houver mensagens repetidas sem priorização ou explicação longa antes da agenda. Intervenção humana imediata não indicada. Monitorar se a janela current continuar zerada em ciclos com expediente ativo.
