# QA diário Clara — conversão/agendamento — 2026-06-19 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, gerado em 2026-06-19 01:15 UTC, com 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 wins e 0 drops.
- Sequência operacional observada: relatórios `whatsapp-current` seguem zerados de forma recorrente desde pelo menos 2026-06-14, inclusive em dias e horários comerciais.
- Relatório histórico mais recente: últimos 180 dias, 6187 mensagens, 443 leads, 3275 inbound, 2912 outbound, 30 sinais de agendamento/vitória e 5 sinais de queda/objeção.
- O histórico mostra que vitórias se concentram em confirmação objetiva, oferta direta de horário e redução de explicações antes da proposta de agenda.
- As quedas/objeções aparecem associadas a abordagem consultiva aberta, explicação longa antes de agenda e lead sem contexto que não recebe ancoragem rápida.

## Aprendizado operacional novo
A recorrência de `whatsapp-current` zerado por vários dias transforma o sinal de 2026-06-14 de alerta pontual em bloqueio operacional de observabilidade: a QA diária não consegue medir conversão recente da Clara nem detectar objeções/silêncios atuais enquanto a fonte current permanecer zerada. Deve haver validação humana/técnica da captura WhatsApp, planilha, Z-API/bridge e cron antes de usar o current para decisões de performance.

## Melhorias práticas para Clara
1. **Oferta direta com horário específico antes da explicação:** para lead com intenção mínima, abrir com uma opção concreta de agenda e pergunta de fechamento simples. Evitar explicar a consulta antes de propor horário, preservando a possibilidade de explicar se o lead pedir.
2. **Ancoragem rápida para entrada sem contexto:** quando vier apenas saudação, link de rede social ou pedido genérico de informação, responder com contexto curto de origem e duas opções de agenda. Não usar pergunta aberta tipo “como posso ajudar?” como primeiro movimento.
3. **Confirmação fechada e rastreável:** após marcar, confirmar nome, serviço/atendimento, dia e horário, pedindo resposta literal entre `Confirmo`, `Quero remarcar` ou `Não vou conseguir`, para reduzir silêncio e facilitar triagem operacional.

## Risco operacional
Há risco operacional que exige intervenção humana/técnica, mas não pausa da Clara: o current zerado persistente impede QA recente confiável e pode indicar falha de captura/pipeline. Ação recomendada: validar fonte de dados, bridge/Z-API, planilha e agendamento do cron. Sem ordem direta do Tiaro, Clara não deve ser pausada.

## Guardrail
Nenhuma melhoria autoriza diagnóstico, prescrição, promessa de resultado, pressão comercial agressiva ou atendimento clínico. O foco é clareza, timing de agenda, redução de atrito e melhor triagem de intenção.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3 como hipótese operacional segura.
- Testar 3 dias: medir resposta a oferta direta de horário e confirmações fechadas quando o pipeline current voltar a capturar dados.
- Intervenção humana: validar pipeline current por persistência de zero em múltiplas execuções.
