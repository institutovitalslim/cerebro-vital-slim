# QA diário Clara — conversão/agendamento — 2026-06-16 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 wins, 0 drops.
- Últimas execuções `whatsapp-current` seguem zeradas; não foi encontrado `whatsapp-current` não zerado depois de 2026-06-01 23:16 UTC na amostra local de relatórios JSON.
- Relatório historical disponível: últimos 180 dias, 6187 mensagens, 443 leads, 3275 inbound, 2912 outbound, 30 wins, 5 drops.
- Aprendizados históricos ativos: confirmações com opções fechadas; proposta direta de horário antes de explicações; evitar perguntas abertas genéricas; ancoragem rápida para links/saudações vazias.

## Leitura operacional
A Clara, como máquina de agendamento, deve reduzir atrito e conduzir o lead para horário concreto quando houver sinal de intenção. A ausência contínua de mensagens no `current` impede QA real de conversas recentes e deve ser tratada como risco de fonte/pipeline, não como prova de ausência real de demanda.

## Melhorias práticas para Clara
1. Para lead com intenção ou pedido de informação, oferecer duas janelas concretas de agenda antes de explicar detalhes do serviço: `Temos [dia] às [horário] ou [dia] às [horário]. Qual fica melhor para você?`.
2. Para confirmação de atendimento, manter mensagem fechada com nome, procedimento, data, horário e três respostas literais: `Confirmo`, `Quero remarcar`, `Não vou conseguir`.
3. Para abertura vazia, link de Instagram ou pedido genérico de informação, responder com ancoragem curta e avanço de agenda, sem `Como posso te ajudar?` e sem explicação longa inicial.

## Risco operacional
Há risco operacional que exige intervenção humana/técnica: validar por que o `whatsapp-current` está zerado de forma persistente. Checar planilha/fonte de conversas, Z-API/bridge, permissões, cron e janela de coleta. Não pausar a Clara sem ordem explícita do Tiaro.

## Guardrail
Nenhuma melhoria autoriza promessa clínica, diagnóstico, prescrição, pressão comercial agressiva ou atendimento direto fora do domínio da Clara. O foco é clareza, condução para agenda e redução de atrito.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3, dentro dos guardrails existentes da Clara.
- Intervenção humana: validação técnica do pipeline `whatsapp-current` por sequência persistente de relatórios zerados.
- Novo aprendizado canônico: sem mudança estrutural nova; reforço/evidência operacional do risco já registrado em 2026-06-14.
