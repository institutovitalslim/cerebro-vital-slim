# QA diário Clara — conversão/agendamento — 2026-06-14 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 wins, 0 drops.
- Últimas 40 execuções `whatsapp-current` verificadas entre 2026-06-09 23:15 e 2026-06-14 01:15: todas com 0 mensagens e 0 leads únicos.
- Relatório historical disponível: últimos 180 dias, 6187 mensagens, 443 leads, 3275 inbound, 2912 outbound, 30 wins, 5 drops.

## Aprendizado operacional
Quando o current do WhatsApp fica zerado repetidamente por múltiplas execuções, a QA de conversão não deve concluir automaticamente que houve ausência real de demanda. Deve classificar como risco operacional de captura/pipeline e pedir intervenção humana/técnica para validar fonte, planilha, Z-API/bridge e cron.

## Melhorias práticas para Clara
1. Confirmação com respostas literais: ao confirmar consulta, terminar com opções em negrito `Confirmo`, `Quero remarcar`, `Não vou conseguir`.
2. Logística no mesmo bloco: informar horário de chegada e etapa prévia de exames/preparação junto do convite de agenda, reduzindo idas e vindas.
3. Qualificação antes de explicar serviço: antes de detalhar consulta/procedimentos, perguntar se o lead busca atendimento agora ou está pesquisando para decidir mais à frente.

## Guardrail
Nenhuma melhoria autoriza promessa clínica, prescrição, diagnóstico ou pressão comercial agressiva. O foco é clareza, confirmação e redução de atrito de agenda.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3, desde que já alinhadas com guardrails da Clara.
- Intervenção humana: validar pipeline/fonte por sequência anormal de current zerado.
