# QA diário Clara — conversão/agendamento — 2026-08-08 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, gerado em 2026-08-08 01:15 UTC, com 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 sinais de vitória/agendamento e 0 sinais de queda/objeção.
- Relatório histórico disponível: últimos 180 dias, arquivo de 2026-08-03 10:23 UTC, com 6187 mensagens, 443 leads únicos, 3275 inbound, 2912 outbound, 30 sinais de vitória/agendamento e 5 sinais de queda/objeção.
- **Congelamento de dados confirmado**: os contadores históricos são idênticos aos da QA de 2026-07-02 (6187 mensagens, 443 leads, 30 vitórias, 5 quedas). Isso comprova que a pipeline de ingestão de conversas do WhatsApp está parada há pelo menos 36 dias.
- Taxa histórica aproximada: 30 vitórias em 443 leads únicos, cerca de 6,8% de sinal de agendamento; 5 quedas, cerca de 1,1%.
- O campo de aprendizados do relatório current informa `SEM_APRENDIZADOS_NOVOS - sem mensagens no período`.
- O relatório histórico contém 4 aprendizados qualitativos consolidados (confirmação com opções, abordagem fria, follow-up de exames, qualificação de serviço).

## Sinais de agendamento, objeção e silêncio
- Agendamento: sem amostra recente no current; histórico mantém 30 sinais de vitória, todos de confirmação de agendamento já existente (não de fechamento de novo lead).
- Objeção: sem objeção recente classificável; histórico registra 5 quedas, todas com causa raiz identificada: oferta de explicação técnica antes do compromisso de agenda.
- Silêncio: o sinal dominante é a ausência completa de dados de conversa nas últimas 6h (horário noturno, esperado) e o congelamento dos dados históricos (não esperado, indica falha técnica).

## Melhorias práticas para Clara
1. **Recuperar pipeline de dados antes de qualquer novo aprendizado conversacional**: a Clara não pode melhorar o que não consegue enxergar. A prioridade zero é restabelecer a captura de conversas do WhatsApp para o motor de aprendizado.
2. **Ancorar follow-up de leads não convertidos com oferta fechada e prazo curto**: com ~413 leads não convertidos no pipeline, a Clara precisa de um script de reativação que ofereça duas opções de horário concretas (ex.: "terça 14h ou quarta 10h") em vez de perguntar "quando você pode".
3. **Criar qualificação de serviço no primeiro toque para evitar desperdício de closer**: o histórico mostra demandas de tricologia, treino, aplicação e administrativo chegando no mesmo canal. Um menu de 3 opções na saudação inicial (`emagrecimento/medicina`, `treino`, `tricologia`) reduziria o tempo de triagem.

## Aprendizado operacional novo
- **Congelamento de pipeline confirmado**: os dados históricos não se alteram há 36+ dias. Isso não é falha pontual; é um bloqueio técnico persistente de observabilidade que impede QA conversacional efetiva.
- **Causa raiz dos drops é conhecida e 100% evitável**: 3 dos 5 drops (60%) vieram da mesma ação — oferecer explicar a consulta antes de propor horário. A correção é simples e de alto impacto.
- **Taxa de conversão de 6,8% é baseline, não teto**: com 413 leads não convertidos e pipeline de reativação inexistente, há espaço mensurável para aumento de agendamentos sem violar guardrails.

## Risco operacional
- **CRÍTICO**: Pipeline de ingestão de conversas do WhatsApp parada há 36+ dias. A gestão está operando sem amostra confiável de conversas. Isso exige intervenção técnica imediata no Z-API, bridge, planilha de conversas e parser de aprendizados.
- **MÉDIO**: 413 leads não convertidos no pipeline histórico sem estratégia de reativação estruturada. Isso é receita potencial deixada na mesa.
- **BAIXO**: Os 5 drops históricos são poucos, mas com causa raiz única e corrigível. Não há padrão de violação de guardrails clínicos.

## Guardrails
Nenhuma melhoria autoriza diagnóstico, prescrição, promessa de resultado, pressão comercial agressiva ou atendimento clínico. O foco é reduzir atrito de agenda, melhorar triagem segura e encaminhar demandas clínicas à equipe certa.

## Classificação
- **Intervenção humana técnica imediata**: abrir ticket de infraestrutura para restabelecer captura de conversas WhatsApp → planilha → relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json`.
- **Aplicar amanhã**: correção do script da Clara para nunca oferecer "explicar a consulta" antes de propor horário concreto.
- **Testar 3 dias**: quando a pipeline voltar, medir taxa de resposta ao novo script de reativação com oferta fechada de horários.
