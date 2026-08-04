# QA diário Clara — conversão/agendamento — 2026-08-04 01:30 UTC

## Escopo
QA objetiva da Clara como máquina de agendamento, a partir dos relatórios mais recentes:
- `/root/.openclaw/reports/clara-learning/latest-whatsapp-current.json`
- `/root/.openclaw/reports/clara-learning/latest-whatsapp-historical.json`

Registro sanitizado: não contém PII, telefones nem transcrição sensível.

## Métricas lidas

### Janela current — últimas 6h
- Mensagens: 0
- Leads/conversas únicas: 0
- Inbound/outbound: 0 / 0
- Sinais de agendamento/vitória: 0
- Sinais de queda/objeção: 0
- Resultado: sem amostra recente; não há conversa recente suficiente para inferir falha de abordagem nesta janela.

### Janela histórica — últimos 180 dias
- Mensagens: 6187
- Leads/conversas únicas: 443
- Inbound/outbound: 3275 / 2912
- Sinais de agendamento/vitória: 30
- Sinais de queda/objeção: 5
- Taxa aproximada de vitória por lead único: 6.77%
- Taxa aproximada de queda por lead único: 1.13%

## Sinais operacionais
- Agendamento: confirmações com serviço, dia/horário exatos e opções literais de resposta reduzem fricção e geram respostas objetivas.
- Objeção: abordagem explicativa ou venda da consulta antes de qualificar intenção tende a gerar recuo em lead frio/pesquisando.
- Silêncio/evasão: follow-up aberto sobre exames favorece resposta do tipo “aviso quando fizer”; ancorar prazo concreto melhora a chance de próximo passo.
- Roteamento: demandas distintas no mesmo canal exigem qualificação inicial por serviço antes de detalhar atendimento ou agenda.

## Três melhorias práticas
1. Manter confirmação objetiva com três opções de resposta: `Confirmo`, `Quero remarcar`, `Não vou conseguir`.
2. Em lead frio, trocar explicação longa por pergunta de triagem: identificar se busca emagrecimento/medicina, treino, tricologia ou administrativo antes de vender consulta.
3. Em pendência de exames, evitar pergunta aberta; propor prazo concreto e próximo passo de agenda, sem promessa clínica e sem condicionar indevidamente o atendimento.

## Guardrails
- Não diagnosticar, prescrever ou prometer resultado.
- Não transformar aprendizado de conversa em regra clínica.
- Não expor dados pessoais de pacientes/leads.
- Não pausar Clara sem ordem direta do Tiaro.

## Classificação do aprendizado
- Aplicar amanhã: confirmação com opções literais e triagem inicial por serviço.
- Testar 3 dias: follow-up de exames com prazo concreto e convite para próxima etapa.

## Risco operacional
Baixo para compliance clínico nos dados agregados lidos. Risco de conversão moderado se Clara continuar explicando consulta cedo demais para lead frio ou usando perguntas abertas em pendência de exames. Intervenção humana imediata não indicada. Ponto de atenção: janela current zerada; se repetir em horário ativo por mais ciclos, verificar ingestão/planilha antes de concluir ausência real de mensagens.
