# QA diário Clara — conversão/agendamento — 2026-06-20 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, gerado em 2026-06-20 01:16 UTC, com 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 wins e 0 drops.
- Relatório histórico disponível: últimos 180 dias, 6187 mensagens, 443 leads únicos, 3275 inbound, 2912 outbound, 30 sinais de vitória/agendamento e 5 sinais de queda/objeção.
- Sinais de agendamento no histórico: confirmação objetiva com opções fechadas; proposta direta de horário; aceitação mais frequente quando a agenda aparece antes de explicações longas.
- Sinais de objeção/queda no histórico: perguntas abertas, explicações longas antes da proposta de agenda e entradas sem contexto que ficam sem ancoragem rápida.
- Sinal de silêncio/observabilidade: o current permanece zerado, mantendo bloqueio de leitura recente; a QA de hoje não consegue inferir performance atual da Clara, apenas reforçar padrões históricos.

## Aprendizado operacional novo
Não houve aprendizado conversacional novo no período current, porque a fonte trouxe zero mensagens. O aprendizado operacional incremental é de observabilidade: a persistência do current zerado precisa permanecer como risco ativo até validação técnica da captura WhatsApp/planilha/Z-API/bridge/cron.

## Melhorias práticas para Clara
1. **Oferta direta com horário específico:** quando houver intenção mínima, propor data/horário concreto antes de explicar detalhes do serviço. Exemplo operacional: “Temos uma vaga amanhã às 14h00. Posso reservar para você?”
2. **Ancoragem rápida para lead sem contexto:** para “oi”, link de Instagram ou pedido genérico de informações, responder com origem provável e duas opções de agenda, sem abrir com “como posso ajudar?”.
3. **Confirmação fechada pós-agendamento:** confirmar nome, atendimento, dia e horário, pedindo resposta literal entre `Confirmo`, `Quero remarcar` ou `Não vou conseguir`, para reduzir silêncio e facilitar triagem.

## Risco operacional
Há risco operacional que exige intervenção humana/técnica, mas não pausa da Clara: o relatório current segue zerado e impede QA recente confiável. Ação recomendada: validar captura WhatsApp, planilha, Z-API/bridge e cron. Sem ordem direta do Tiaro, Clara não deve ser pausada.

## Guardrails
Nenhuma melhoria autoriza diagnóstico, prescrição, promessa de resultado, pressão comercial agressiva ou atendimento clínico. O foco é reduzir atrito de agenda e melhorar triagem comercial segura.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3 como hipótese operacional segura.
- Testar 3 dias: medir taxa de resposta a oferta direta e confirmação fechada quando o current voltar a capturar dados.
- Intervenção humana: manter validação técnica do pipeline current como pendência operacional.
