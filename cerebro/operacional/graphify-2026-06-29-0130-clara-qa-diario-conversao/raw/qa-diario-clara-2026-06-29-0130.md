# QA diário Clara — conversão/agendamento — 2026-06-29 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, gerado em 2026-06-29 01:15 UTC, com 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 wins e 0 drops.
- Relatório histórico disponível: últimos 180 dias, 6187 mensagens, 443 leads únicos, 3275 inbound, 2912 outbound, 30 sinais de vitória/agendamento e 5 sinais de queda/objeção.
- Sinais de agendamento no histórico: confirmações estruturadas com atendimento, data, horário e opções fechadas de resposta geram confirmação objetiva.
- Sinais de objeção no histórico: abordagem de venda direta em leads frios, pergunta aberta genérica ou explicação longa antes de qualificar interesse tendem a gerar recusa do tipo “por enquanto não”.
- Sinais de silêncio/observabilidade: o current veio novamente zerado, então a QA não consegue medir performance recente real; usa apenas padrões históricos.

## Aprendizado operacional novo
Não houve aprendizado conversacional novo no período current, porque a fonte trouxe zero mensagens. O aprendizado incremental é operacional: a captura recente do WhatsApp continua sem amostra útil e deve permanecer como pendência de observabilidade até validação técnica do pipeline.

## Melhorias práticas para Clara
1. **Qualificar antes de vender para lead frio:** em entradas genéricas de anúncio ou pedido de informações, abrir com escolha de área de interesse — emagrecimento, aplicações, tricologia ou nutrição — antes de propor consulta ou explicar pacote.
2. **Converter intenção mínima em agenda concreta:** quando a pessoa indicar área de interesse ou pedir continuidade, oferecer um horário específico e uma alternativa curta, sem alongar explicações clínicas. Exemplo operacional: “Tenho uma vaga amanhã às 14h ou quinta às 10h. Qual fica melhor para você?”
3. **Fechar confirmação com opções padronizadas:** após agendamento ou aplicação marcada, confirmar atendimento, dia e horário e pedir resposta literal entre `Confirmo`, `Quero remarcar` ou `Não vou conseguir`, para reduzir silêncio e facilitar triagem.

## Risco operacional
Há risco operacional de observabilidade que exige intervenção humana/técnica, mas não pausa da Clara: o relatório current está zerado e impede QA recente confiável. Ação recomendada: validar captura WhatsApp, planilha, Z-API/bridge e cron. Sem ordem direta do Tiaro, Clara não deve ser pausada.

## Guardrails
Nenhuma melhoria autoriza diagnóstico, prescrição, promessa de resultado, pressão comercial agressiva ou atendimento clínico. O foco é reduzir atrito de agenda, melhorar triagem comercial segura e encaminhar demandas administrativas ou clínicas para a equipe correta.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3 como hipótese operacional segura.
- Testar 3 dias: medir resposta à qualificação inicial, oferta de horário concreto e confirmação fechada quando o current voltar a capturar dados.
- Intervenção humana: validar pipeline current do WhatsApp como pendência técnica recorrente.
