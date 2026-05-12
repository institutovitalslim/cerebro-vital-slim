# Graphify RC-25 — QA diário Clara como máquina de agendamento — 2026-05-12

## Escopo
Registro canônico e sanitizado do QA diário da Clara no WhatsApp, com foco em conversão para agendamento, objeções, silêncio e guardrails clínicos. Não contém PII, telefones ou conversas sensíveis.

## Base analisada
- Current: últimas 6 horas; 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 vitórias, 0 quedas. Resultado: sem aprendizados novos por ausência de volume.
- Historical: últimos 180 dias; 5149 mensagens, 326 leads únicos, 2239 inbound, 2910 outbound, 23 vitórias, 5 quedas.

## Sinais operacionais
- Agendamento/confirmação: confirmações com opções de resposta rápida produziram adesão direta.
- Objeção: explicações genéricas, pergunta ampla antes da qualificação e documentos soltos aumentaram escape ou adiamento.
- Silêncio: no recorte atual não houve mensagens; sem sinal de falha ativa pelo relatório, mas a ausência de volume limita QA em tempo real.

## Aprendizados operacionais novos ou reforçados

### 1. Confirmação com três respostas literais
Ao confirmar consulta, procedimento ou horário, Clara deve fechar com três opções literais e destacadas: *Confirmo*, *Quero remarcar* e *Não vou conseguir*. Classificação: aplicar amanhã.

### 2. Lead sem intenção clara precisa de bifurcação objetiva
Quando o lead ainda não disser claramente que quer agendar, Clara não deve abrir com explicação genérica nem "como posso ajudar". Deve perguntar: "Você gostaria de agendar uma avaliação ou prefere saber os valores primeiro?" Classificação: aplicar amanhã.

### 3. Demanda de treino deve ir para avaliação física antes de consulta médica
Quando aparecerem termos como treino, visita, montar treino ou personalizado, Clara deve responder com localização e horários disponíveis para avaliação física, sem desviar para consulta médica antes de entender a demanda. Classificação: testar 3 dias.

### 4. Exames e documentos precisam de data vinculada ao próximo passo
Clara não deve perguntar genericamente quando o lead fará exames nem enviar PDF/documento sem condução. Deve propor data e horário específico vinculando entrega dos exames ao atendimento, sem prescrever nem interpretar exames. Classificação: testar 3 dias.

## Guardrails
- Não diagnosticar, não prescrever, não interpretar exames e não prometer resultado.
- Não expor PII, telefones ou conversas sensíveis.
- Não pausar Clara sem ordem explícita de Tiaro.
- Conteúdo vira melhoria operacional de conversão, não regra clínica.
