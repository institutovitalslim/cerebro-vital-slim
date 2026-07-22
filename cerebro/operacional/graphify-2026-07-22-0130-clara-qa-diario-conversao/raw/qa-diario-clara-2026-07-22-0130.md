# QA diário Clara — conversão/agendamento — 2026-07-22 01:30 UTC

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
- Resultado: sem amostra recente; não há conversa recente suficiente para inferir falha operacional.

### Janela histórica — últimos 180 dias
- Mensagens: 6187
- Leads/conversas únicas: 443
- Inbound/outbound: 3275 / 2912
- Sinais de agendamento/vitória: 30
- Sinais de queda/objeção: 5
- Taxa aproximada de vitória por lead único: 6.77%
- Taxa aproximada de queda por lead único: 1.13%

## Sinais operacionais
- Agendamento: confirmação com identificação do atendimento, horário claro e opções curtas reduz fricção; oferta de 1 ou 2 horários específicos performa melhor que pergunta aberta.
- Objeção: explicação longa sobre consulta/protocolo antes de medir intenção tende a esfriar leads em pesquisa.
- Silêncio/risco de perda de temperatura: mensagens repetidas pelo lead indicam atraso percebido e devem virar fila prioritária de resposta.

## Três melhorias práticas
1. Padronizar confirmação com três respostas curtas: `Confirmo`, `Quero remarcar`, `Não vou conseguir`.
2. Para lead com intenção, oferecer 1 ou 2 horários concretos antes de entrar em explicações do programa; se o lead estiver pesquisando, perguntar fase de decisão antes de detalhar.
3. Criar gatilho operacional de prioridade quando houver mensagem repetida do mesmo lead: reconhecer atraso percebido, responder de forma objetiva e levar para o próximo passo de agenda.

## Guardrails
- Não diagnosticar, prescrever ou prometer resultado.
- Não pedir exames como condição antes de propor agenda, salvo fluxo validado pela equipe.
- Não pausar Clara sem ordem direta do Tiaro.

## Classificação do aprendizado
- Aplicar amanhã: confirmação objetiva e oferta de horários concretos.
- Testar 3 dias: gatilho de prioridade para mensagens repetidas.

## Risco operacional
Baixo para atendimento clínico/compliance. Moderado para conversão se houver mensagens repetidas sem priorização ou explicação longa antes da agenda. Intervenção humana imediata não indicada; apenas monitoramento do próximo ciclo current e revisão se a janela continuar zerada por mais ciclos em horário ativo.
